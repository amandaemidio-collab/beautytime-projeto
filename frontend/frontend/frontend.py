"""BeautyTime booking, account, and public-company pages."""

import json
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import unquote, urlencode

import reflex as rx

from frontend.api_client import request_json, request_json_list
from frontend.api_config import api_url
from frontend.theme import (
    COLORS,
    FORM_FIELD_STYLE,
    FONT_FAMILY,
    FONT_STYLESHEET,
    GLOBAL_STYLES,
    SHADOWS,
    TILE_STYLE,
)

IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
TIME_PATTERN = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d\Z")
SAO_PAULO = timezone(timedelta(hours=-3), "America/Sao_Paulo")
WEEKDAY_SHORT = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
WEEKDAY_OPTIONS = [
    ("1", "Segunda-feira"),
    ("2", "Terça-feira"),
    ("3", "Quarta-feira"),
    ("4", "Quinta-feira"),
    ("5", "Sexta-feira"),
    ("6", "Sábado"),
    ("7", "Domingo"),
]


def _duration_label(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    if not hours:
        return f"{minutes} min"
    if not remainder:
        return f"{hours}h"
    return f"{hours}h {remainder}min"


def _price_label(price_cents: int) -> str:
    return f"R$ {price_cents // 100},{price_cents % 100:02d}"


def _minute_label(minutes: int) -> str:
    if minutes == 1440:
        return "24:00"
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _parse_time(value: str) -> int | None:
    if value == "24:00":
        return 1440
    if not TIME_PATTERN.fullmatch(value):
        return None
    hours, minutes = (int(part) for part in value.split(":"))
    return hours * 60 + minutes


def _local_datetime(value: object) -> datetime:
    if isinstance(value, bool):
        raise ValueError("Timestamp inválido.")
    if isinstance(value, (int, float)):
        timestamp = value / 1000 if abs(value) >= 100_000_000_000 else value
        return datetime.fromtimestamp(timestamp, tz=SAO_PAULO)
    if not isinstance(value, str) or not value:
        raise ValueError("Timestamp inválido.")
    try:
        timestamp = float(value)
    except ValueError:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=SAO_PAULO)
        return parsed.astimezone(SAO_PAULO)
    timestamp = timestamp / 1000 if abs(timestamp) >= 100_000_000_000 else timestamp
    return datetime.fromtimestamp(timestamp, tz=SAO_PAULO)


def _local_datetime_label(value: object) -> str:
    return _local_datetime(value).strftime("%d/%m/%Y às %H:%M")


DURATION_OPTIONS = [
    (str(minutes), _duration_label(minutes)) for minutes in range(15, 481, 15)
]
PAGE_STYLE = {
    "min_height": "100vh",
    "background_color": COLORS["background"],
    "font_family": FONT_FAMILY,
    "padding": rx.breakpoints(initial="28px 16px", md="56px 24px"),
    "overflow_x": "hidden",
}
CARD_STYLE = {
    "width": "100%",
    "max_width": "520px",
    "padding": rx.breakpoints(initial="28px 20px", md="40px"),
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "24px",
    "background_color": COLORS["surface"],
    "box_shadow": SHADOWS["card"],
}
HELPER_TEXT = "Exemplo: salao-da-ana"
IDENTIFIER_FORMAT_ERROR = (
    "Use de 3 a 40 caracteres: letras minúsculas, números e hífen, "
    "sem começar ou terminar com hífen."
)
BOOKING_WINDOW_DAYS = 30
LATE_CANCELLATION_SECONDS = 8 * 3600
CANCELLATION_POLICY = (
    "Cancelamento gratuito com 8 horas ou mais de antecedência. Com menos de "
    "8 horas, o cancelamento fica marcado como tardio, com taxa apenas "
    "informativa de R$ 5,00. Nenhum pagamento é processado pelo BeautyTime."
)


def _api_error(status: int, data: dict[str, object]) -> str:
    """Translate common Xano errors into concise Portuguese messages."""
    message = str(data.get("message", "")).lower()
    if status == 0:
        return str(data.get("message", "Não foi possível conectar à API."))
    if status == 429:
        return "Muitas tentativas em pouco tempo. Aguarde e tente novamente."
    if "already in use" in message:
        return "Este e-mail já está em uso."
    if "invalid credentials" in message:
        return "E-mail ou senha inválidos para este tipo de acesso."
    if status in (400, 422):
        return "Confira os dados informados e tente novamente."
    return f"Não foi possível concluir a solicitação (HTTP {status})."


def _identifier_error(data: dict[str, object]) -> str | None:
    """Return a field-specific message when Xano rejects a public identifier."""
    message = str(data.get("message", "")).lower()
    if "public identifier" not in message and "identifier" not in message:
        return None
    if "already in use" in message:
        return "Este endereço já está em uso. Escolha outro."
    return IDENTIFIER_FORMAT_ERROR


def _field(
    label: str,
    name: str,
    input_type: str = "text",
    placeholder: str = "",
    required: bool = True,
    **input_props: object,
) -> rx.Component:
    """Create a labeled form field without copying its value into app state."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color=COLORS["text"]),
        rx.input(
            name=name,
            type=input_type,
            placeholder=placeholder,
            required=required,
            width="100%",
            size="3",
            **input_props,
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _identifier_field() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Endereço público da empresa",
            size="2",
            weight="medium",
            color=COLORS["text"],
        ),
        rx.input(
            name="public_identifier",
            type="text",
            placeholder=HELPER_TEXT.split(": ", maxsplit=1)[-1],
            required=True,
            min_length=3,
            max_length=40,
            pattern="[a-z0-9]+(-[a-z0-9]+)*",
            width="100%",
            size="3",
            style=FORM_FIELD_STYLE,
            aria_invalid=State.identifier_error != "",
            aria_describedby="public-identifier-help public-identifier-error",
        ),
        rx.text(
            HELPER_TEXT,
            id="public-identifier-help",
            size="2",
            color=COLORS["muted"],
        ),
        rx.text(
            State.identifier_error,
            id="public-identifier-error",
            role="alert",
            size="2",
            color=COLORS["error"],
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _form_page(
    title: str,
    description: str,
    submit_label: str,
    fields: list[rx.Component],
    handler: rx.EventHandler,
    footer: rx.Component,
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.link(
                _brand(),
                href="/",
                underline="none",
            ),
            rx.box(
                rx.vstack(
                    rx.heading(title, size="8", color=COLORS["text"], weight="bold"),
                    rx.text(description, color=COLORS["muted"], line_height="1.6"),
                    rx.form(
                        rx.vstack(
                            *fields,
                            rx.text(
                                State.message,
                                color=COLORS["error"],
                                size="2",
                                role="alert",
                            ),
                            rx.button(
                                submit_label,
                                type="submit",
                                width="100%",
                                size="3",
                                style=FORM_FIELD_STYLE,
                                height="52px",
                                background_color=COLORS["accent"],
                                color=COLORS["surface"],
                                _hover={"background_color": COLORS["accent_hover"]},
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
                            font_family=FONT_FAMILY,
                        ),
                        on_submit=handler,
                        reset_on_submit=False,
                        width="100%",
                    ),
                    footer,
                    align="stretch",
                    spacing="4",
                    width="100%",
                ),
                style=CARD_STYLE,
            ),
            align="center",
            spacing="6",
            width="100%",
            max_width="520px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _brand() -> rx.Component:
    return rx.heading(
        "BeautyTime",
        size="6",
        weight="bold",
        color=COLORS["accent"],
        letter_spacing="-0.04em",
    )


class State(rx.State):
    """Frontend state; credentials and the Xano token remain backend-only."""

    _auth_token: str = ""

    message: str = ""
    identifier_error: str = ""
    user_name: str = ""
    user_role: str = ""
    company_name: str = ""
    company_identifier: str = ""
    dashboard_loading: bool = False
    dashboard_error: str = ""
    public_link: str = ""
    clipboard_notice: str = ""
    public_company_name: str = ""
    public_company_identifier: str = ""
    public_company_message: str = ""
    public_company_found: bool = False
    public_service_items: list[dict[str, Any]] = []
    public_services_loading: bool = False
    public_services_error: str = ""
    service_items: list[dict[str, Any]] = []
    services_loading: bool = False
    services_error: str = ""
    services_notice: str = ""
    editing_service_id: int = 0
    service_name: str = ""
    service_duration: str = ""
    service_price: str = ""
    service_name_error: str = ""
    service_duration_error: str = ""
    service_price_error: str = ""
    professionals_loading: bool = False
    professionals_error: str = ""
    professionals_notice: str = ""
    professional_items: list[dict[str, Any]] = []
    professional_service_options: list[dict[str, Any]] = []
    editing_professional_id: int = 0
    professional_name: str = ""
    professional_name_error: str = ""
    professional_service_ids: list[str] = []
    professional_original_service_ids: list[str] = []
    hours_loading: bool = False
    hours_error: str = ""
    hours_notice: str = ""
    hours_professional_options: list[dict[str, str]] = []
    selected_hours_professional_id: str = ""
    hour_items: list[dict[str, Any]] = []
    editing_hour_id: int = 0
    hours_day: str = "1"
    hours_start: str = "09:00"
    hours_end: str = "18:00"
    agenda_loading: bool = False
    agenda_error: str = ""
    agenda_date: str = ""
    agenda_professional_options: list[dict[str, str]] = []
    agenda_professional_id: str = "all"
    agenda_items: list[dict[str, Any]] = []
    booking_message: str = ""
    booking_identifier: str = ""
    booking_service_id: int = 0
    booking_service_name: str = ""
    booking_service_duration: str = ""
    booking_service_price: str = ""
    booking_professional_options: list[dict[str, str]] = []
    booking_professionals_loading: bool = False
    booking_professionals_error: str = ""
    booking_professional_id: str = ""
    booking_date: str = ""
    booking_date_min: str = ""
    booking_date_max: str = ""
    booking_days: list[dict[str, Any]] = []
    booking_days_loading: bool = False
    booking_days_error: str = ""
    booking_slots: list[dict[str, Any]] = []
    booking_slots_loading: bool = False
    booking_slots_error: str = ""
    booking_slot_start: int = 0
    booking_slot_label: str = ""
    booking_submitting: bool = False
    booking_resume: bool = False
    booking_confirmed: bool = False
    booking_confirmation: dict[str, str] = {}
    client_appointments_loading: bool = False
    client_appointments_error: str = ""
    client_notice: str = ""
    client_upcoming: list[dict[str, Any]] = []
    client_past: list[dict[str, Any]] = []
    cancel_dialog_open: bool = False
    cancel_target_id: int = 0
    cancel_target_label: str = ""
    cancel_target_late: bool = False
    cancel_submitting: bool = False
    cancel_error: str = ""
    salons: list[dict[str, str]] = []
    salons_loading: bool = False
    salons_error: str = ""

    @rx.var
    def client_signed_in(self) -> bool:
        return self.user_role == "client"

    @rx.var
    def booking_professional_label(self) -> str:
        for option in self.booking_professional_options:
            if option["id"] == self.booking_professional_id:
                return option["name"]
        return ""

    @rx.event
    def clear_message(self):
        self.message = ""
        self.identifier_error = ""
        self.clipboard_notice = ""

    def _set_session_from_identity(
        self,
        identity: dict[str, object],
        token: str,
        expected_role: str,
        fallback_name: str = "",
    ) -> bool:
        role = str(identity.get("role", ""))
        account_id = identity.get("account_id")
        if role != expected_role:
            self.message = "A conta não corresponde ao fluxo de acesso escolhido."
            return False
        if role == "client" and account_id not in (None, 0, "0", ""):
            self.message = "A conta de cliente possui um vínculo de empresa inválido."
            return False
        if role == "admin" and account_id in (None, 0, "0", ""):
            self.message = "A conta administradora não possui uma empresa associada."
            return False

        self._auth_token = token
        self.user_name = str(identity.get("name") or fallback_name)
        self.user_role = role
        self.message = ""
        return True

    def _accept_signup(
        self,
        data: dict[str, object],
        expected_role: str,
        fallback_name: str,
    ) -> bool:
        token = str(data.get("authToken", ""))
        actual_role = str(data.get("user_type", ""))
        if not token or actual_role != expected_role:
            self.message = "A API não confirmou a criação da conta esperada."
            return False

        self._auth_token = token
        self.user_name = fallback_name
        self.user_role = expected_role
        self.message = ""
        return True

    def _load_identity(self, expected_role: str) -> bool:
        status, identity = request_json(
            "GET",
            api_url("authentication", "auth/me"),
            token=self._auth_token,
        )
        if status != 200:
            self._auth_token = ""
            self.user_role = ""
            self.user_name = ""
            self.message = _api_error(status, identity)
            return False
        return self._set_session_from_identity(
            identity,
            self._auth_token,
            expected_role,
        )

    @rx.event
    def client_signup(self, form_data: dict[str, Any]):
        name = form_data.get("name", "").strip()
        email = form_data.get("email", "").strip()
        phone = form_data.get("phone", "").strip()
        password = form_data.get("password", "")
        if not name or not email or not phone or not password:
            self.message = "Preencha todos os campos."
            return

        status, data = request_json(
            "POST",
            api_url("authentication", "auth/signup"),
            {
                "name": name,
                "email": email,
                "phone": phone,
                "password": password,
            },
        )
        if status not in (200, 201):
            self.message = _api_error(status, data)
            return
        if not self._accept_signup(data, "client", name):
            return
        return rx.redirect(self._client_destination())

    @rx.event
    def client_login(self, form_data: dict[str, Any]):
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.message = "Informe seu e-mail e sua senha."
            return

        status, data = request_json(
            "POST",
            api_url("authentication", "auth/login"),
            {"email": email, "password": password},
        )
        if status != 200:
            self.message = _api_error(status, data)
            return
        token = str(data.get("authToken", ""))
        if not token:
            self.message = "A API não retornou uma sessão válida."
            return
        self._auth_token = token
        if not self._load_identity("client"):
            return
        return rx.redirect(self._client_destination())

    def _client_destination(self) -> str:
        """Return to the pending booking flow or to the client area."""
        if (
            self.booking_resume
            and IDENTIFIER_PATTERN.fullmatch(self.booking_identifier)
            and self.booking_service_id
        ):
            return f"/agendar/{self.booking_identifier}"
        self.booking_resume = False
        return "/meus-agendamentos"

    @rx.event
    def load_client_auth_page(self):
        """Keep the booking continuation only when the flow sent the client here."""
        self.clear_message()
        query = self.router.url.query_parameters
        if query.get("retomar") != "agendamento":
            self.booking_resume = False

    @rx.event
    def admin_signup(self, form_data: dict[str, Any]):
        self.message = ""
        self.identifier_error = ""
        name = form_data.get("name", "").strip()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        company_name = form_data.get("company_name", "").strip()
        identifier = form_data.get("public_identifier", "").strip()
        if not name or not email or not password or not company_name or not identifier:
            self.message = "Preencha todos os campos obrigatórios."
            return
        if not 3 <= len(identifier) <= 40 or not IDENTIFIER_PATTERN.fullmatch(
            identifier
        ):
            self.identifier_error = IDENTIFIER_FORMAT_ERROR
            return

        payload: dict[str, object] = {
            "name": name,
            "email": email,
            "phone": form_data.get("phone", "").strip(),
            "password": password,
            "company_name": company_name,
            "public_identifier": identifier,
            "description": form_data.get("description", "").strip(),
            "location": form_data.get("location", "").strip(),
        }
        status, data = request_json(
            "POST",
            api_url("authentication", "auth/admin/signup"),
            payload,
        )
        if status not in (200, 201):
            self.identifier_error = _identifier_error(data) or ""
            if not self.identifier_error:
                self.message = _api_error(status, data)
            return
        if not self._accept_signup(data, "admin", name):
            return

        company = data.get("company")
        if isinstance(company, dict):
            self.company_name = str(company.get("name", company_name))
            self.company_identifier = str(
                company.get("public_identifier", identifier)
            )
        else:
            self.company_name = company_name
            self.company_identifier = identifier
        return rx.redirect("/admin")

    @rx.event
    def admin_login(self, form_data: dict[str, Any]):
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.message = "Informe seu e-mail e sua senha."
            return

        status, data = request_json(
            "POST",
            api_url("authentication", "auth/admin/login"),
            {"email": email, "password": password},
        )
        if status != 200:
            self.message = _api_error(status, data)
            return
        token = str(data.get("authToken", ""))
        if not token:
            self.message = "A API não retornou uma sessão válida."
            return
        self._auth_token = token
        if not self._load_identity("admin"):
            return
        return rx.redirect("/admin")

    @rx.event
    def logout(self):
        self._auth_token = ""
        self.user_name = ""
        self.user_role = ""
        self.company_name = ""
        self.company_identifier = ""
        self.public_link = ""
        self.professional_items = []
        self.professional_service_options = []
        self.service_items = []
        self.hour_items = []
        self.agenda_items = []
        self.hours_professional_options = []
        self.agenda_professional_options = []
        self.client_upcoming = []
        self.client_past = []
        self.client_notice = ""
        self._reset_booking("")
        self.message = ""
        return rx.redirect("/")

    @rx.event
    def load_admin_dashboard(self):
        self.dashboard_loading = True
        self.dashboard_error = ""
        self.clipboard_notice = ""
        if not self._auth_token or not self._load_identity("admin"):
            self.dashboard_loading = False
            return rx.redirect("/admin/login")
        if not self._refresh_admin_catalog():
            self.dashboard_loading = False
            self.dashboard_error = self.services_error
            return
        self.dashboard_loading = False
        return rx.call_script(
            "window.location.origin + '/agendar/' + "
            f"encodeURIComponent({json.dumps(self.company_identifier)})",
            callback=State.set_public_link,
        )

    @rx.event
    def set_public_link(self, link: str):
        self.public_link = link

    @rx.event
    def copy_public_link(self):
        self.clipboard_notice = ""
        if not self.public_link:
            self.clipboard_notice = (
                "O link público ainda não está disponível para cópia."
            )
            return
        return rx.call_script(
            "navigator.clipboard.writeText("
            f"{json.dumps(self.public_link)}"
            ").then(() => true).catch(() => false)",
            callback=State.handle_clipboard_result,
        )

    @rx.event
    def handle_clipboard_result(self, copied: bool):
        self.clipboard_notice = (
            "Link copiado."
            if copied
            else "Não foi possível copiar. Selecione e copie o link exibido."
        )

    def _refresh_admin_catalog(self) -> bool:
        status, data = request_json(
            "GET",
            api_url("catalogo", "admin/services"),
            token=self._auth_token,
        )
        if status != 200:
            self.services_error = _api_error(status, data)
            self.service_items = []
            return False

        company = data.get("company")
        services = data.get("services")
        if not isinstance(company, dict) or not isinstance(services, list):
            self.services_error = "A API retornou dados inválidos para o catálogo."
            self.service_items = []
            return False

        self.company_name = str(company.get("name", ""))
        self.company_identifier = str(company.get("public_identifier", ""))
        self.service_items = []
        for item in services:
            if not isinstance(item, dict):
                continue
            duration = int(item["duration_minutes"])
            price_cents = int(item["price_cents"])
            self.service_items.append(
                {
                    **item,
                    "duration_display": _duration_label(duration),
                    "price_display": _price_label(price_cents),
                }
            )
        self.services_error = ""
        return True

    @rx.event
    def load_admin_services(self):
        self.services_loading = True
        self.services_error = ""
        self.services_notice = ""
        if not self._auth_token:
            self.service_items = []
            self.services_loading = False
            return rx.redirect("/admin/login")
        if not self._load_identity("admin"):
            self.service_items = []
            self.services_loading = False
            return rx.redirect("/admin/login")

        self._refresh_admin_catalog()
        self.services_loading = False

    @rx.event
    def begin_service_edit(
        self,
        service_id: int,
        name: str,
        duration_minutes: int,
        price_cents: int,
    ):
        self.editing_service_id = service_id
        self.service_name = name
        self.service_duration = str(duration_minutes)
        self.service_price = (
            f"{price_cents // 100}.{price_cents % 100:02d}"
        )
        self.services_notice = ""
        self.service_name_error = ""
        self.service_duration_error = ""
        self.service_price_error = ""

    @rx.event
    def cancel_service_edit(self):
        self.editing_service_id = 0
        self.service_name = ""
        self.service_duration = ""
        self.service_price = ""
        self.service_name_error = ""
        self.service_duration_error = ""
        self.service_price_error = ""
        self.services_notice = ""

    @rx.event
    def set_service_name(self, value: str):
        self.service_name = value

    @rx.event
    def set_service_duration(self, value: str):
        self.service_duration = value

    @rx.event
    def set_service_price(self, value: str):
        self.service_price = value

    @rx.event
    def submit_service(self, form_data: dict[str, Any]):
        self.services_notice = ""
        self.services_error = ""
        self.service_name = str(form_data.get("service_name", "")).strip()
        self.service_duration = str(form_data.get("service_duration", "")).strip()
        self.service_price = str(form_data.get("service_price", "")).strip()
        self.service_name_error = ""
        self.service_duration_error = ""
        self.service_price_error = ""

        name = self.service_name
        if not 2 <= len(name) <= 80:
            self.service_name_error = "Use um nome de 2 a 80 caracteres."

        try:
            duration = Decimal(self.service_duration)
            if (
                not duration.is_finite()
                or duration != duration.to_integral_value()
                or duration < 15
                or duration > 480
                or duration % 15 != 0
            ):
                self.service_duration_error = (
                    "Informe um número inteiro múltiplo de 15, entre 15 e 480."
                )
        except InvalidOperation:
            self.service_duration_error = (
                "Informe um número inteiro múltiplo de 15, entre 15 e 480."
            )

        price_text = self.service_price.replace(",", ".")
        try:
            price = Decimal(price_text)
            if (
                not price.is_finite()
                or price < 0
                or price > Decimal("99999.99")
                or price != price.quantize(Decimal("0.01"))
            ):
                self.service_price_error = (
                    "Informe um preço entre R$ 0,00 e R$ 99.999,99."
                )
        except InvalidOperation:
            self.service_price_error = (
                "Informe um preço entre R$ 0,00 e R$ 99.999,99."
            )

        if (
            self.service_name_error
            or self.service_duration_error
            or self.service_price_error
        ):
            return

        payload = {
            "name": name,
            "duration_minutes": int(duration),
            "price_cents": int(price * 100),
        }
        if self.editing_service_id:
            method = "PATCH"
            path = f"admin/services/{self.editing_service_id}"
        else:
            method = "POST"
            path = "admin/services"

        status, data = request_json(
            method,
            api_url("catalogo", path),
            payload,
            token=self._auth_token,
        )
        if status not in (200, 201):
            error = str(data.get("message", ""))
            if error == "service_name_taken":
                self.service_name_error = "Este nome já está em uso nesta empresa."
            elif error == "service_name_invalid":
                self.service_name_error = "Use um nome de 2 a 80 caracteres."
            elif error == "service_duration_invalid":
                self.service_duration_error = (
                    "Informe um número inteiro múltiplo de 15, entre 15 e 480."
                )
            elif error == "service_price_invalid":
                self.service_price_error = (
                    "Informe um preço entre R$ 0,00 e R$ 99.999,99."
                )
            else:
                self.services_error = _api_error(status, data)
            return

        self.services_notice = (
            "Serviço atualizado com sucesso."
            if method == "PATCH"
            else "Serviço cadastrado com sucesso."
        )
        self.editing_service_id = 0
        self.service_name = ""
        self.service_duration = ""
        self.service_price = ""
        self._refresh_admin_catalog()

    @rx.event
    def toggle_service_status(self, service_id: int):
        service = next(
            (
                item
                for item in self.service_items
                if item.get("id") == service_id
            ),
            None,
        )
        if service is None:
            self.services_error = "O serviço não está mais disponível na lista."
            return

        status, data = request_json(
            "PATCH",
            api_url("catalogo", f"admin/services/{service_id}/status"),
            {"is_active": not bool(service.get("is_active"))},
            token=self._auth_token,
        )
        if status != 200:
            self.services_error = _api_error(status, data)
            return

        self.services_notice = (
            "Serviço ativado."
            if data.get("is_active")
            else "Serviço desativado."
        )
        self._refresh_admin_catalog()

    def _refresh_professional_catalog(self) -> bool:
        status, data = request_json(
            "GET",
            api_url("catalogo", "admin/professionals"),
            token=self._auth_token,
        )
        if status != 200:
            self.professionals_error = _api_error(status, data)
            self.professional_items = []
            self.professional_service_options = []
            return False

        professionals = data.get("professionals")
        services = data.get("services")
        associations = data.get("service_associations")
        if not all(
            isinstance(value, list)
            for value in (professionals, services, associations)
        ):
            self.professionals_error = (
                "A API retornou dados inválidos para os profissionais."
            )
            self.professional_items = []
            self.professional_service_options = []
            return False

        self.professional_service_options = []
        for service in services:
            if (
                not isinstance(service, dict)
                or not isinstance(service.get("id"), int)
                or isinstance(service.get("id"), bool)
                or not isinstance(service.get("name"), str)
            ):
                self.professionals_error = (
                    "A API retornou um serviço inválido para seleção."
                )
                self.professional_service_options = []
                return False
            self.professional_service_options.append(
                {"id": str(service["id"]), "name": service["name"]}
            )

        associations_by_professional: dict[int, list[dict[str, Any]]] = {}
        for association in associations:
            if (
                not isinstance(association, dict)
                or not isinstance(association.get("professional_id"), int)
                or not isinstance(association.get("service_id"), int)
                or not isinstance(association.get("service_name"), str)
                or not isinstance(association.get("service_is_active"), bool)
            ):
                self.professionals_error = (
                    "A API retornou uma associação de serviço inválida."
                )
                self.professional_items = []
                return False
            associations_by_professional.setdefault(
                association["professional_id"], []
            ).append(association)

        self.professional_items = []
        for professional in professionals:
            if (
                not isinstance(professional, dict)
                or not isinstance(professional.get("id"), int)
                or not isinstance(professional.get("name"), str)
                or not isinstance(professional.get("is_active"), bool)
            ):
                self.professionals_error = (
                    "A API retornou um profissional inválido."
                )
                self.professional_items = []
                return False

            linked_services = associations_by_professional.get(
                professional["id"], []
            )
            service_names = [
                f"{item['service_name']}{'' if item['service_is_active'] else ' (inativo)'}"
                for item in linked_services
            ]
            self.professional_items.append(
                {
                    "id": professional["id"],
                    "name": professional["name"],
                    "is_active": professional["is_active"],
                    "service_ids": [
                        str(item["service_id"])
                        for item in linked_services
                        if item["service_is_active"]
                    ],
                    "services_label": ", ".join(service_names)
                    or "Nenhum serviço associado.",
                }
            )

        self.professionals_error = ""
        return True

    @rx.event
    def load_admin_professionals(self):
        self._reset_professional_form()
        self.professionals_loading = True
        self.professionals_error = ""
        self.professionals_notice = ""
        if not self._auth_token or not self._load_identity("admin"):
            self.professional_items = []
            self.professional_service_options = []
            self.professionals_loading = False
            return rx.redirect("/admin/login")

        if not self._refresh_admin_catalog():
            self.professional_items = []
            self.professional_service_options = []
            self.professionals_error = self.services_error
            self.professionals_loading = False
            return

        self._refresh_professional_catalog()
        self.professionals_loading = False

    @rx.event
    def load_admin_hours(self):
        self.hours_loading = True
        self.hours_error = ""
        self.hours_notice = ""
        if not self._auth_token or not self._load_identity("admin"):
            self.hours_professional_options = []
            self.hour_items = []
            self.hours_loading = False
            return rx.redirect("/admin/login")
        if not self._refresh_admin_catalog():
            self.hours_error = self.services_error
            self.hours_loading = False
            return
        if not self._refresh_professional_catalog():
            self.hours_error = self.professionals_error
            self.hours_loading = False
            return

        self.hours_professional_options = [
            {"id": str(item["id"]), "name": item["name"]}
            for item in self.professional_items
            if item["is_active"]
        ]
        if not self.hours_professional_options:
            self.selected_hours_professional_id = ""
            self.hour_items = []
            self.hours_loading = False
            return

        professional_ids = {
            item["id"] for item in self.hours_professional_options
        }
        if self.selected_hours_professional_id not in professional_ids:
            self.selected_hours_professional_id = (
                self.hours_professional_options[0]["id"]
            )
        self.hours_loading = False
        return State.load_professional_hours(
            int(self.selected_hours_professional_id)
        )

    @rx.event
    def set_hours_professional(self, professional_id: str):
        if not any(
            item["id"] == professional_id
            for item in self.hours_professional_options
        ):
            self.hours_error = "Selecione um profissional ativo da empresa."
            return
        self.selected_hours_professional_id = professional_id
        self.editing_hour_id = 0
        self.hours_notice = ""
        self.hours_day = "1"
        self.hours_start = "09:00"
        self.hours_end = "18:00"
        return State.load_professional_hours(int(professional_id))

    @rx.event
    def load_professional_hours(self, professional_id: int):
        self.hours_loading = True
        self.hours_error = ""
        status, data = request_json_list(
            "GET",
            api_url(
                "agenda",
                f"admin/professionals/{professional_id}/hours",
            ),
            token=self._auth_token,
        )
        self.hours_loading = False
        if status != 200:
            self.hour_items = []
            self.hours_error = _api_error(status, data)
            return
        if not isinstance(data, list):
            self.hour_items = []
            self.hours_error = "A API retornou horários em formato inválido."
            return

        items: list[dict[str, Any]] = []
        weekday_labels = dict(WEEKDAY_OPTIONS)
        for item in data:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), int)
                or isinstance(item.get("id"), bool)
                or not isinstance(item.get("day_of_week"), int)
                or isinstance(item.get("day_of_week"), bool)
                or not isinstance(item.get("start_minute"), int)
                or isinstance(item.get("start_minute"), bool)
                or not isinstance(item.get("end_minute"), int)
                or isinstance(item.get("end_minute"), bool)
                or str(item["day_of_week"]) not in weekday_labels
            ):
                self.hour_items = []
                self.hours_error = (
                    "A API retornou um período de atendimento inválido."
                )
                return
            items.append(
                {
                    **item,
                    "day_name": weekday_labels[str(item["day_of_week"])],
                    "start_label": _minute_label(item["start_minute"]),
                    "end_label": _minute_label(item["end_minute"]),
                }
            )
        self.hour_items = sorted(
            items,
            key=lambda item: (
                item["day_of_week"],
                item["start_minute"],
            ),
        )

    @rx.event
    def begin_hour_edit(
        self,
        hour_id: int,
        day_of_week: int,
        start_minute: int,
        end_minute: int,
    ):
        if not any(item["id"] == hour_id for item in self.hour_items):
            self.hours_error = "O período não está mais disponível na lista."
            return
        self.editing_hour_id = hour_id
        self.hours_day = str(day_of_week)
        self.hours_start = _minute_label(start_minute)
        self.hours_end = _minute_label(end_minute)
        self.hours_error = ""
        self.hours_notice = ""

    @rx.event
    def cancel_hour_edit(self):
        self.editing_hour_id = 0
        self.hours_day = "1"
        self.hours_start = "09:00"
        self.hours_end = "18:00"
        self.hours_error = ""
        self.hours_notice = ""

    @rx.event
    def set_hours_day(self, value: str):
        self.hours_day = value

    @rx.event
    def set_hours_start(self, value: str):
        self.hours_start = value

    @rx.event
    def set_hours_end(self, value: str):
        self.hours_end = value

    @rx.event
    def submit_hour(self, form_data: dict[str, Any]):
        self.hours_error = ""
        self.hours_notice = ""
        day = str(form_data.get("day_of_week", self.hours_day))
        start_text = str(form_data.get("start_time", self.hours_start)).strip()
        end_text = str(form_data.get("end_time", self.hours_end)).strip()
        start_minute = _parse_time(start_text)
        end_minute = _parse_time(end_text)
        if day not in dict(WEEKDAY_OPTIONS):
            self.hours_error = "Selecione um dia da semana válido."
            return
        if (
            start_minute is None
            or end_minute is None
            or start_minute >= 1440
            or start_minute >= end_minute
        ):
            self.hours_error = (
                "Informe horários válidos e um término posterior ao início."
            )
            return
        if not self.selected_hours_professional_id:
            self.hours_error = "Selecione um profissional ativo."
            return

        payload = {
            "day_of_week": int(day),
            "start_minute": start_minute,
            "end_minute": end_minute,
        }
        if self.editing_hour_id:
            method = "PATCH"
            path = (
                f"admin/professionals/{self.selected_hours_professional_id}"
                f"/hours/{self.editing_hour_id}"
            )
        else:
            method = "POST"
            path = (
                f"admin/professionals/{self.selected_hours_professional_id}"
                "/hours"
            )
        status, data = request_json(
            method,
            api_url("agenda", path),
            payload,
            token=self._auth_token,
        )
        if status not in (200, 201):
            self.hours_error = _api_error(status, data)
            return

        self.hours_notice = (
            "Período atualizado com sucesso."
            if method == "PATCH"
            else "Período cadastrado com sucesso."
        )
        self.editing_hour_id = 0
        self.hours_day = "1"
        self.hours_start = "09:00"
        self.hours_end = "18:00"
        return State.load_professional_hours(
            int(self.selected_hours_professional_id)
        )

    @rx.event
    def remove_hour(self, hour_id: int):
        if not any(item["id"] == hour_id for item in self.hour_items):
            self.hours_error = "O período não está mais disponível na lista."
            return
        status, data = request_json(
            "DELETE",
            api_url(
                "agenda",
                f"admin/professionals/{self.selected_hours_professional_id}"
                f"/hours/{hour_id}",
            ),
            token=self._auth_token,
        )
        if status != 200:
            self.hours_error = _api_error(status, data)
            return
        self.hours_notice = "Período removido."
        if self.editing_hour_id == hour_id:
            self.cancel_hour_edit()
        return State.load_professional_hours(
            int(self.selected_hours_professional_id)
        )

    @rx.event
    def load_admin_agenda(self):
        self.agenda_loading = True
        self.agenda_error = ""
        if not self._auth_token or not self._load_identity("admin"):
            self.agenda_items = []
            self.agenda_professional_options = []
            self.agenda_loading = False
            return rx.redirect("/admin/login")
        if not self._refresh_admin_catalog():
            self.agenda_error = self.services_error
            self.agenda_loading = False
            return
        if not self._refresh_professional_catalog():
            self.agenda_error = self.professionals_error
            self.agenda_loading = False
            return

        self.agenda_professional_options = [
            {"id": "all", "name": "Todos os profissionais"}
        ] + [
            {
                "id": str(item["id"]),
                "name": (
                    item["name"]
                    if item["is_active"]
                    else f"{item['name']} (inativo)"
                ),
            }
            for item in self.professional_items
        ]
        if not self.agenda_date:
            self.agenda_date = datetime.now(SAO_PAULO).date().isoformat()
        self.agenda_loading = False
        return State.refresh_admin_agenda()

    @rx.event
    def set_agenda_date(self, value: str):
        self.agenda_date = value
        return State.refresh_admin_agenda()

    @rx.event
    def set_agenda_professional(self, value: str):
        self.agenda_professional_id = value
        return State.refresh_admin_agenda()

    @rx.event
    def refresh_admin_agenda(self):
        self.agenda_loading = True
        self.agenda_error = ""
        self.agenda_items = []
        if not self._auth_token or not self._load_identity("admin"):
            self.agenda_loading = False
            return rx.redirect("/admin/login")
        try:
            selected_date = date.fromisoformat(self.agenda_date)
        except ValueError:
            self.agenda_loading = False
            self.agenda_error = "Selecione uma data válida."
            return
        query: dict[str, str] = {
            "appointment_date": selected_date.isoformat()
        }
        if self.agenda_professional_id != "all":
            if not self.agenda_professional_id.isdigit():
                self.agenda_loading = False
                self.agenda_error = "Selecione um profissional válido."
                return
            query["professional_id"] = self.agenda_professional_id
        status, data = request_json_list(
            "GET",
            f"{api_url('agenda', 'admin/appointments')}?{urlencode(query)}",
            token=self._auth_token,
        )
        self.agenda_loading = False
        if status != 200:
            self.agenda_error = _api_error(status, data)
            return
        if not isinstance(data, list):
            self.agenda_error = "A API retornou a agenda em formato inválido."
            return

        items: list[dict[str, Any]] = []
        for item in data:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), int)
                or isinstance(item.get("id"), bool)
                or not isinstance(item.get("client_name"), str)
                or not isinstance(item.get("professional_name"), str)
                or not isinstance(item.get("service_name"), str)
                or not isinstance(item.get("status"), str)
                or not isinstance(item.get("is_late_cancellation"), bool)
            ):
                self.agenda_error = (
                    "A API retornou um agendamento em formato inválido."
                )
                return
            try:
                start_label = _local_datetime_label(item.get("starts_at"))
                end_label = _local_datetime_label(item.get("ends_at"))
            except (TypeError, ValueError, OverflowError):
                self.agenda_error = (
                    "A API retornou um horário de agendamento inválido."
                )
                return
            items.append(
                {
                    **item,
                    "start_label": start_label,
                    "end_label": end_label,
                    "status_label": (
                        "Agendado"
                        if item["status"] == "agendado"
                        else "Cancelado"
                    ),
                }
            )
        self.agenda_items = items

    @rx.event
    def begin_professional_edit(self, professional_id: int):
        professional = next(
            (
                item
                for item in self.professional_items
                if item["id"] == professional_id
            ),
            None,
        )
        if professional is None:
            self.professionals_error = (
                "O profissional não está mais disponível na lista."
            )
            return

        self.editing_professional_id = professional_id
        self.professional_name = professional["name"]
        self.professional_name_error = ""
        self.professional_service_ids = list(professional["service_ids"])
        self.professional_service_ids = sorted(self.professional_service_ids)
        self.professional_original_service_ids = sorted(
        professional["service_ids"]
        )
        self.professionals_error = ""
        self.professionals_notice = ""

    def _reset_professional_form(self):
        self.editing_professional_id = 0
        self.professional_name = ""
        self.professional_name_error = ""
        self.professional_service_ids = []
        self.professional_original_service_ids = []

    @rx.event
    def cancel_professional_edit(self):
        self._reset_professional_form()
        self.professionals_error = ""
        self.professionals_notice = ""

    @rx.event
    def set_professional_name(self, value: str):
        self.professional_name = value

    @rx.event
    def set_professional_service_ids(self, service_ids: list[str]):
        self.professional_service_ids = sorted(set(service_ids))

    @rx.event
    def toggle_professional_service_selection(
        self,
        service_id: str,
        checked: bool,
    ):
        selected = set(self.professional_service_ids)
        if checked:
            selected.add(service_id)
        else:
            selected.discard(service_id)
        self.professional_service_ids = sorted(selected)

    @rx.event
    def submit_professional(self, form_data: dict[str, Any]):
        self.professionals_error = ""
        self.professionals_notice = ""
        self.professional_name = str(
            form_data.get("professional_name", self.professional_name)
        ).strip()
        self.professional_name_error = ""

        if not self.professional_name:
            self.professional_name_error = "Informe o nome do profissional."
            return

        selected_service_ids = sorted(set(self.professional_service_ids))
        if self.editing_professional_id:
            services_changed = (
                selected_service_ids != self.professional_original_service_ids
            )
        else:
            services_changed = True

        if services_changed and not selected_service_ids:
            self.professionals_error = (
                "Selecione pelo menos um serviço ativo da sua empresa."
            )
            return
        if not self.editing_professional_id and not self.professional_service_options:
            self.professionals_error = (
                "Cadastre um serviço ativo antes de criar um profissional."
            )
            return

        try:
            service_ids = [int(service_id) for service_id in selected_service_ids]
        except ValueError:
            self.professionals_error = (
                "A seleção de serviços contém um identificador inválido."
            )
            return

        if self.editing_professional_id:
            payload: dict[str, object] = {"name": self.professional_name}
            if services_changed:
                payload["service_ids"] = service_ids
            method = "PATCH"
            path = (
                "admin/professionals/"
                f"{self.editing_professional_id}"
            )
        else:
            payload = {
                "name": self.professional_name,
                "service_ids": service_ids,
            }
            method = "POST"
            path = "admin/professionals"

        status, data = request_json(
            method,
            api_url("catalogo", path),
            payload,
            token=self._auth_token,
        )
        if status not in (200, 201):
            error = str(data.get("message", ""))
            if error == "professional_name_required":
                self.professional_name_error = (
                    "Informe o nome do profissional."
                )
            elif error in (
                "professional_requires_service",
                "professional_service_invalid",
                "professional_service_duplicate",
            ):
                self.professionals_error = (
                    "Selecione somente serviços ativos da sua empresa."
                )
            else:
                self.professionals_error = _api_error(status, data)
            return

        self._reset_professional_form()
        self.professionals_notice = (
            "Profissional atualizado com sucesso."
            if method == "PATCH"
            else "Profissional cadastrado com sucesso."
        )
        self._refresh_professional_catalog()

    @rx.event
    def toggle_professional_status(self, professional_id: int):
        professional = next(
            (
                item
                for item in self.professional_items
                if item["id"] == professional_id
            ),
            None,
        )
        if professional is None:
            self.professionals_error = (
                "O profissional não está mais disponível na lista."
            )
            return

        status, data = request_json(
            "PATCH",
            api_url(
                "catalogo",
                f"admin/professionals/{professional_id}/status",
            ),
            {"is_active": not professional["is_active"]},
            token=self._auth_token,
        )
        if status != 200:
            self.professionals_error = _api_error(status, data)
            return

        self.professionals_notice = (
            "Profissional reativado."
            if data.get("is_active")
            else "Profissional desativado."
        )
        self._refresh_professional_catalog()

    @rx.event
    def load_public_company(self):
        path = str(self.router.url.path).rstrip("/")
        identifier = unquote(path.rsplit("/", 1)[-1]).strip()
        resuming = (
            identifier == self.booking_identifier
            and self.booking_service_id != 0
            and not self.booking_confirmed
        )
        if not resuming:
            self._reset_booking(identifier)
        self.booking_resume = False
        today = datetime.now(SAO_PAULO).date()
        self.booking_date_min = today.isoformat()
        self.booking_date_max = (
            today + timedelta(days=BOOKING_WINDOW_DAYS)
        ).isoformat()
        self.message = ""
        self.identifier_error = ""
        self.public_company_name = ""
        self.public_company_identifier = ""
        self.public_company_found = False
        self.public_company_message = ""
        self.public_service_items = []
        self.public_services_loading = False
        self.public_services_error = ""
        if (
            not 3 <= len(identifier) <= 40
            or not IDENTIFIER_PATTERN.fullmatch(identifier)
        ):
            self.public_company_message = "Empresa não encontrada"
            return

        query = urlencode({"public_identifier": identifier})
        status, data = request_json(
            "GET",
            f"{api_url('members_accounts', 'company/public')}?{query}",
        )
        if status == 404:
            self.public_company_message = "Empresa não encontrada"
            return
        if status != 200:
            self.public_company_message = (
                "Não foi possível carregar os dados públicos da empresa."
            )
            return

        self.public_company_name = str(data.get("name", ""))
        self.public_company_identifier = str(data.get("public_identifier", ""))
        self.public_company_found = bool(
            self.public_company_name and self.public_company_identifier
        )
        if not self.public_company_found:
            self.public_company_message = "Não foi possível carregar os dados públicos."
            return

        self.public_services_loading = True
        return State.load_public_services(identifier)

    @rx.event
    def load_public_services(self, identifier: str):
        query = urlencode({"public_identifier": identifier})
        status, data = request_json_list(
            "GET",
            f"{api_url('catalogo', 'public/services')}?{query}",
        )
        self.public_services_loading = False
        if status != 200:
            self.public_services_error = (
                "Não foi possível carregar os serviços desta empresa."
            )
            return
        if not isinstance(data, list):
            self.public_services_error = (
                "Não foi possível carregar os serviços desta empresa."
            )
            return

        for item in data:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), int)
                or isinstance(item.get("id"), bool)
                or not isinstance(item.get("name"), str)
                or not isinstance(item.get("duration_minutes"), int)
                or isinstance(item.get("duration_minutes"), bool)
                or not isinstance(item.get("price_cents"), int)
                or isinstance(item.get("price_cents"), bool)
            ):
                self.public_service_items = []
                self.public_services_error = (
                    "Não foi possível carregar os serviços desta empresa."
                )
                return
            duration = item["duration_minutes"]
            price_cents = item["price_cents"]
            self.public_service_items.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "duration_display": _duration_label(duration),
                    "price_display": _price_label(price_cents),
                }
            )
        if self.booking_service_id:
            return State.resume_booking

    @rx.event
    def start_fresh_booking(self, identifier: str):
        """Open a salon's booking page with no choices carried over."""
        if not IDENTIFIER_PATTERN.fullmatch(identifier):
            return
        self._reset_booking(identifier)
        return rx.redirect(f"/agendar/{identifier}")

    def _reset_booking(self, identifier: str):
        self.booking_identifier = identifier
        self.booking_message = ""
        self.booking_confirmed = False
        self.booking_confirmation = {}
        self.booking_submitting = False
        self._clear_booking_service()

    def _clear_booking_service(self):
        self.booking_service_id = 0
        self.booking_service_name = ""
        self.booking_service_duration = ""
        self.booking_service_price = ""
        self.booking_professional_options = []
        self.booking_professionals_loading = False
        self.booking_professionals_error = ""
        self.booking_professional_id = ""
        self.booking_days = []
        self.booking_days_loading = False
        self.booking_days_error = ""
        self._clear_booking_date()

    def _clear_booking_date(self):
        self.booking_date = ""
        self.booking_slots = []
        self.booking_slots_loading = False
        self.booking_slots_error = ""
        self._clear_booking_slot()

    def _clear_booking_slot(self):
        self.booking_slot_start = 0
        self.booking_slot_label = ""

    def _load_booking_professionals(self) -> bool:
        self.booking_professionals_loading = False
        self.booking_professionals_error = ""
        self.booking_professional_options = []
        status, data = request_json_list(
            "GET",
            api_url(
                "agenda",
                f"public/{self.booking_identifier}/services/"
                f"{self.booking_service_id}/professionals",
            ),
        )
        if status != 200 or not isinstance(data, list):
            self.booking_professionals_error = (
                "Não foi possível carregar os profissionais deste serviço."
                if status != 404
                else "Este serviço não está mais disponível."
            )
            return False
        options = [{"id": "any", "name": "Sem preferência"}]
        for item in data:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("id"), int)
                or isinstance(item.get("id"), bool)
                or not isinstance(item.get("name"), str)
            ):
                self.booking_professionals_error = (
                    "Não foi possível carregar os profissionais deste serviço."
                )
                return False
            options.append({"id": str(item["id"]), "name": item["name"]})
        if len(options) == 1:
            self.booking_professionals_error = (
                "Nenhum profissional realiza este serviço no momento."
            )
            return False
        self.booking_professional_options = options
        return True

    def _load_booking_days(self) -> bool:
        """Mark which days of the booking window have at least one free start."""
        self.booking_days_loading = False
        self.booking_days_error = ""
        self.booking_days = []
        query: dict[str, str] = {"service_id": str(self.booking_service_id)}
        if self.booking_professional_id != "any":
            query["professional_id"] = self.booking_professional_id
        status, data = request_json_list(
            "GET",
            api_url("agenda", f"public/{self.booking_identifier}/available_days")
            + f"?{urlencode(query)}",
        )
        if status != 200 or not isinstance(data, list):
            self.booking_days_error = (
                _api_error(status, data)
                if status == 429
                else "Não foi possível carregar os dias disponíveis."
            )
            return False
        available = {item for item in data if isinstance(item, str)}
        first_day = date.fromisoformat(self.booking_date_min)
        days: list[dict[str, Any]] = []
        for offset in range(BOOKING_WINDOW_DAYS + 1):
            day = first_day + timedelta(days=offset)
            days.append(
                {
                    "date": day.isoformat(),
                    "weekday": WEEKDAY_SHORT[day.isoweekday() - 1],
                    "label": day.strftime("%d/%m"),
                    "available": day.isoformat() in available,
                }
            )
        self.booking_days = days
        return True

    def _booking_day_available(self, value: str) -> bool:
        return any(
            day["date"] == value and day["available"] for day in self.booking_days
        )

    def _load_booking_slots(self):
        self.booking_slots_loading = False
        self.booking_slots_error = ""
        self.booking_slots = []
        query: dict[str, str] = {
            "service_id": str(self.booking_service_id),
            "appointment_date": self.booking_date,
        }
        if self.booking_professional_id != "any":
            query["professional_id"] = self.booking_professional_id
        status, data = request_json_list(
            "GET",
            api_url("agenda", f"public/{self.booking_identifier}/availability")
            + f"?{urlencode(query)}",
        )
        if status != 200 or not isinstance(data, list):
            self.booking_slots_error = (
                _api_error(status, data)
                if status == 429
                else "Não foi possível carregar os horários deste dia."
            )
            return
        starts: dict[int, str] = {}
        for item in data:
            try:
                start = _local_datetime(item.get("starts_at"))
            except (AttributeError, TypeError, ValueError, OverflowError):
                self.booking_slots_error = (
                    "A API retornou um horário em formato inválido."
                )
                return
            starts[int(start.timestamp() * 1000)] = start.strftime("%H:%M")
        self.booking_slots = [
            {"starts_at": value, "label": label}
            for value, label in sorted(starts.items())
        ]

    @rx.event
    def resume_booking(self):
        """Revalidate choices kept across login or signup."""
        service = next(
            (
                item
                for item in self.public_service_items
                if item["id"] == self.booking_service_id
            ),
            None,
        )
        if service is None:
            self._clear_booking_service()
            self.booking_message = "O serviço escolhido não está mais disponível."
            return
        selected_professional = self.booking_professional_id
        selected_slot = self.booking_slot_start
        if not self._load_booking_professionals():
            return
        option_ids = [option["id"] for option in self.booking_professional_options]
        if selected_professional not in option_ids:
            self.booking_professional_id = ""
            self._clear_booking_date()
            if selected_professional:
                self.booking_message = (
                    "O profissional escolhido não está mais disponível."
                )
            return
        if not self._load_booking_days():
            return
        if not self.booking_date:
            return
        if not self._booking_day_available(self.booking_date):
            self._clear_booking_date()
            self.booking_message = (
                "O dia escolhido não tem mais horários livres. Escolha outro."
            )
            return
        self._load_booking_slots()
        if selected_slot and not any(
            slot["starts_at"] == selected_slot for slot in self.booking_slots
        ):
            self._clear_booking_slot()
            self.booking_message = (
                "O horário escolhido não está mais disponível. Escolha outro."
            )

    @rx.event
    def select_booking_service(self, service_id: int):
        service = next(
            (item for item in self.public_service_items if item["id"] == service_id),
            None,
        )
        if service is None:
            return
        self.booking_message = ""
        self.booking_confirmed = False
        self.booking_confirmation = {}
        self._clear_booking_service()
        self.booking_service_id = service_id
        self.booking_service_name = service["name"]
        self.booking_service_duration = service["duration_display"]
        self.booking_service_price = service["price_display"]
        self.booking_professionals_loading = True
        yield
        self._load_booking_professionals()

    @rx.event
    def select_booking_professional(self, professional_id: str):
        if professional_id not in [
            option["id"] for option in self.booking_professional_options
        ]:
            return
        self.booking_message = ""
        self.booking_professional_id = professional_id
        self._clear_booking_slot()
        self.booking_days_loading = True
        yield
        if not self._load_booking_days():
            self._clear_booking_date()
            return
        if not self._booking_day_available(self.booking_date):
            self._clear_booking_date()
            return
        self._load_booking_slots()

    @rx.event
    def set_booking_date(self, value: str):
        self.booking_message = ""
        self._clear_booking_date()
        try:
            selected = date.fromisoformat(value)
        except ValueError:
            return
        if not (
            date.fromisoformat(self.booking_date_min)
            <= selected
            <= date.fromisoformat(self.booking_date_max)
        ):
            self.booking_slots_error = (
                "Escolha um dia entre hoje e os próximos 30 dias."
            )
            return
        if not self._booking_day_available(selected.isoformat()):
            self.booking_slots_error = "Este dia não tem horários livres."
            return
        self.booking_date = selected.isoformat()
        self.booking_slots_loading = True
        yield
        self._load_booking_slots()

    @rx.event
    def select_booking_slot(self, starts_at: int, label: str):
        self.booking_message = ""
        self.booking_slot_start = starts_at
        self.booking_slot_label = label

    @rx.event
    def start_booking_auth(self, target: str):
        """Send the client to login or signup and come back to this flow."""
        if target not in ("login", "cadastro") or not self.booking_slot_start:
            return
        self.booking_resume = True
        return rx.redirect(f"/clientes/{target}?retomar=agendamento")

    @rx.event
    def confirm_booking(self):
        if (
            not self.booking_service_id
            or not self.booking_professional_id
            or not self.booking_slot_start
        ):
            self.booking_message = "Escolha serviço, profissional, dia e horário."
            return
        if not self._auth_token or self.user_role != "client":
            self.booking_message = "Entre ou crie sua conta de cliente para confirmar."
            return
        self.booking_submitting = True
        self.booking_message = ""
        yield
        payload: dict[str, object] = {
            "identifier": self.booking_identifier,
            "service_id": self.booking_service_id,
            "professional_id": (
                None
                if self.booking_professional_id == "any"
                else int(self.booking_professional_id)
            ),
            "starts_at": self.booking_slot_start,
        }
        status, data = request_json(
            "POST",
            api_url("agenda", "client/appointments"),
            payload,
            token=self._auth_token,
        )
        self.booking_submitting = False
        if status in (401, 403):
            self._auth_token = ""
            self.user_role = ""
            self.user_name = ""
            self.booking_message = (
                "Sua sessão de cliente não é válida. Entre novamente para confirmar."
            )
            return
        if status not in (200, 201):
            self.booking_message = (
                _api_error(status, data)
                if status in (0, 429)
                else "A reserva não foi concluída: o horário pode ter ficado "
                "indisponível. Escolha outro horário."
            )
            self._clear_booking_slot()
            if status != 0:
                self._load_booking_slots()
            return
        try:
            start = _local_datetime(data.get("starts_at"))
            duration = int(data["service_duration_minutes"])
            price = int(data["service_price_cents"])
        except (KeyError, TypeError, ValueError, OverflowError):
            self.booking_message = (
                "A reserva foi registrada, mas não foi possível exibir o resumo. "
                "Confira em Meus agendamentos."
            )
            return
        professional_name = next(
            (
                option["name"]
                for option in self.booking_professional_options
                if option["id"] == str(data.get("professional_id"))
            ),
            "",
        )
        self.booking_confirmation = {
            "company_name": str(data.get("company_name") or self.public_company_name),
            "service_name": str(data.get("service_name", "")),
            "professional_name": professional_name,
            "start_label": start.strftime("%d/%m/%Y às %H:%M"),
            "duration_display": _duration_label(duration),
            "price_display": _price_label(price),
        }
        self.booking_confirmed = True

    @rx.event
    def new_booking(self):
        self._reset_booking(self.booking_identifier)

    @rx.event
    def load_client_appointments(self):
        self.client_appointments_loading = True
        self.client_appointments_error = ""
        self.cancel_dialog_open = False
        if not self._auth_token or not self._load_identity("client"):
            self.client_upcoming = []
            self.client_past = []
            self.client_appointments_loading = False
            return rx.redirect("/clientes/login")
        yield
        self._refresh_client_appointments()

    @rx.event
    def load_salons(self):
        """Load the public list of salons that accept bookings."""
        self.salons = []
        self.salons_error = ""
        self.salons_loading = True
        yield
        self.salons_loading = False
        status, data = request_json_list(
            "GET", api_url("members_accounts", "companies/public")
        )
        if status != 200 or not isinstance(data, list):
            self.salons_error = (
                _api_error(status, data)
                if status == 429
                else "Não foi possível carregar os salões. Recarregue a página "
                "para tentar novamente."
            )
            return
        salons: list[dict[str, str]] = []
        for item in data:
            name = item.get("name") if isinstance(item, dict) else None
            identifier = (
                item.get("public_identifier") if isinstance(item, dict) else None
            )
            if (
                not isinstance(name, str)
                or not name.strip()
                or not isinstance(identifier, str)
                or not IDENTIFIER_PATTERN.fullmatch(identifier)
            ):
                self.salons_error = (
                    "A lista de salões veio em formato inválido. Recarregue a "
                    "página para tentar novamente."
                )
                return
            salons.append({"name": name.strip(), "identifier": identifier})
        self.salons = salons

    def _refresh_client_appointments(self):
        self.client_appointments_loading = False
        status, data = request_json_list(
            "GET",
            api_url("agenda", "client/appointments"),
            token=self._auth_token,
        )
        if status in (401, 403):
            self._auth_token = ""
            self.user_role = ""
            self.client_appointments_error = "Sua sessão expirou. Entre novamente."
            return
        if status != 200 or not isinstance(data, list):
            self.client_appointments_error = (
                "Não foi possível carregar seus agendamentos."
            )
            return
        now = datetime.now(SAO_PAULO)
        upcoming: list[dict[str, Any]] = []
        past: list[dict[str, Any]] = []
        for item in data:
            try:
                if not isinstance(item, dict) or isinstance(item.get("id"), bool):
                    raise ValueError
                start = _local_datetime(item.get("starts_at"))
                appointment = {
                    "id": int(item["id"]),
                    "company_name": str(item["company_name"]),
                    "public_identifier": str(item.get("public_identifier") or ""),
                    "professional_name": str(item["professional_name"]),
                    "service_name": str(item["service_name"]),
                    "duration_display": _duration_label(
                        int(item["service_duration_minutes"])
                    ),
                    "price_display": _price_label(int(item["service_price_cents"])),
                    "start_label": start.strftime("%d/%m/%Y às %H:%M"),
                    "starts_at": int(start.timestamp() * 1000),
                    "status": str(item["status"]),
                    "is_late_cancellation": bool(item.get("is_late_cancellation")),
                }
            except (KeyError, TypeError, ValueError, OverflowError):
                self.client_appointments_error = (
                    "A API retornou um agendamento em formato inválido."
                )
                return
            appointment["status_label"] = (
                "Agendado" if appointment["status"] == "agendado" else "Cancelado"
            )
            appointment["can_cancel"] = (
                appointment["status"] == "agendado" and start > now
            )
            (upcoming if start > now else past).append(appointment)
        upcoming.sort(key=lambda appointment: appointment["starts_at"])
        past.sort(key=lambda appointment: appointment["starts_at"], reverse=True)
        self.client_upcoming = upcoming
        self.client_past = past

    @rx.event
    def open_cancel_dialog(self, appointment_id: int):
        appointment = next(
            (
                item
                for item in self.client_upcoming
                if item["id"] == appointment_id and item["can_cancel"]
            ),
            None,
        )
        if appointment is None:
            return
        seconds_left = (
            appointment["starts_at"] / 1000 - datetime.now(SAO_PAULO).timestamp()
        )
        self.client_notice = ""
        self.cancel_error = ""
        self.cancel_target_id = appointment_id
        self.cancel_target_label = (
            f"{appointment['service_name']} em {appointment['start_label']}"
        )
        self.cancel_target_late = seconds_left < LATE_CANCELLATION_SECONDS
        self.cancel_dialog_open = True

    @rx.event
    def set_cancel_dialog_open(self, is_open: bool):
        if self.cancel_submitting:
            return
        self.cancel_dialog_open = is_open
        if not is_open:
            self.cancel_target_id = 0
            self.cancel_error = ""

    @rx.event
    def confirm_cancel(self):
        if not self.cancel_target_id:
            return
        self.cancel_submitting = True
        self.cancel_error = ""
        yield
        status, data = request_json(
            "PATCH",
            api_url(
                "agenda",
                f"client/appointments/{self.cancel_target_id}/cancel",
            ),
            {"confirm_late_cancellation": self.cancel_target_late},
            token=self._auth_token,
        )
        self.cancel_submitting = False
        message = str(data.get("message", ""))
        if status == 200:
            self.cancel_dialog_open = False
            self.cancel_target_id = 0
            self.client_notice = (
                "Agendamento cancelado. O cancelamento foi registrado como tardio."
                if data.get("is_late_cancellation")
                else "Agendamento cancelado sem taxa."
            )
            self._refresh_client_appointments()
            return
        if "late_cancellation_confirmation_required" in message:
            self.cancel_target_late = True
            self.cancel_error = (
                "Agora faltam menos de 8 horas para o início. Confirme novamente "
                "ciente da taxa informativa."
            )
            return
        if "appointment_cannot_be_cancelled" in message or status == 404:
            self.cancel_dialog_open = False
            self.cancel_target_id = 0
            self.client_notice = "Este agendamento não pode mais ser cancelado."
            self._refresh_client_appointments()
            return
        self.cancel_error = _api_error(status, data)


def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            _brand(),
            rx.text(
                "Agende seu horário em poucos toques.",
                color=COLORS["muted"],
                size="4",
                text_align="center",
            ),
            rx.flex(
                _entry_card(
                    "Sou cliente",
                    "Acesse sua conta global ou crie uma nova.",
                    "/clientes/login",
                    "/clientes/cadastro",
                ),
                _entry_card(
                    "Sou administradora",
                    "Entre na sua empresa ou cadastre uma nova.",
                    "/admin/login",
                    "/admin/cadastro",
                ),
                direction={"initial": "column", "md": "row"},
                align="stretch",
                spacing="4",
                width="100%",
            ),
            rx.text(
                "Já tem o link de uma empresa? Acesse /agendar/identificador.",
                color=COLORS["muted"],
                size="2",
                text_align="center",
            ),
            align="center",
            spacing="6",
            width="100%",
            max_width="900px",
            padding={"initial": "28px 20px", "md": "40px"},
            border=f"1px solid {COLORS['border']}",
            border_radius="24px",
            background_color=COLORS["surface"],
            box_shadow=SHADOWS["card"],
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _entry_card(
    title: str,
    description: str,
    login_route: str,
    signup_route: str,
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(title, size="5", color=COLORS["text"]),
            rx.text(description, color=COLORS["muted"], line_height="1.6"),
            rx.link(
                rx.button(
                    "Entrar",
                    width="100%",
                    height="52px",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                    _hover={"background_color": COLORS["accent_hover"]},
                ),
                href=login_route,
                width="100%",
            ),
            rx.link("Criar conta", href=signup_route, color=COLORS["accent"]),
            align="stretch",
            spacing="4",
            width="100%",
        ),
        flex="1",
        padding={"initial": "22px", "md": "28px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )


def client_signup_page() -> rx.Component:
    return _form_page(
        "Criar conta de cliente",
        "Sua conta é global e não fica vinculada a uma empresa.",
        "Criar conta",
        [
            _field("Nome", "name", placeholder="Seu nome"),
            _field("E-mail", "email", input_type="email", placeholder="voce@exemplo.com"),
            _field("Telefone", "phone", input_type="tel", placeholder="(00) 00000-0000"),
            _field(
                "Senha",
                "password",
                input_type="password",
                placeholder="Mínimo de 8 caracteres",
                min_length=8,
            ),
        ],
        State.client_signup,
        rx.link(
            "Já tem conta? Entrar",
            href=rx.cond(
                State.booking_resume,
                "/clientes/login?retomar=agendamento",
                "/clientes/login",
            ),
            color=COLORS["accent"],
        ),
    )


def client_login_page() -> rx.Component:
    return _form_page(
        "Entrar como cliente",
        "Use a mesma conta em todas as empresas da plataforma.",
        "Entrar",
        [
            _field("E-mail", "email", input_type="email", placeholder="voce@exemplo.com"),
            _field(
                "Senha",
                "password",
                input_type="password",
                placeholder="Sua senha",
            ),
        ],
        State.client_login,
        rx.link(
            "Ainda não tem conta? Cadastre-se",
            href=rx.cond(
                State.booking_resume,
                "/clientes/cadastro?retomar=agendamento",
                "/clientes/cadastro",
            ),
            color=COLORS["accent"],
        ),
    )


def admin_signup_page() -> rx.Component:
    return _form_page(
        "Cadastrar empresa",
        "Crie sua conta administradora junto com a empresa.",
        "Criar empresa e conta",
        [
            _field("Seu nome", "name", placeholder="Nome da administradora"),
            _field("E-mail", "email", input_type="email", placeholder="voce@exemplo.com"),
            _field(
                "Senha",
                "password",
                input_type="password",
                placeholder="Mínimo de 8 caracteres",
                min_length=8,
            ),
            _field("Telefone (opcional)", "phone", input_type="tel", required=False),
            _field("Nome da empresa", "company_name", placeholder="Nome do salão"),
            _identifier_field(),
            _field(
                "Descrição (opcional)",
                "description",
                required=False,
                placeholder="Conte um pouco sobre a empresa",
            ),
            _field("Localização (opcional)", "location", required=False),
        ],
        State.admin_signup,
        rx.link(
            "Já tem conta administradora? Entrar",
            href="/admin/login",
            color=COLORS["accent"],
        ),
    )


def admin_login_page() -> rx.Component:
    return _form_page(
        "Entrar como administradora",
        "Acesse a conta vinculada à sua empresa.",
        "Entrar",
        [
            _field("E-mail", "email", input_type="email", placeholder="voce@exemplo.com"),
            _field(
                "Senha",
                "password",
                input_type="password",
                placeholder="Sua senha",
            ),
        ],
        State.admin_login,
        rx.link(
            "Ainda não tem empresa? Cadastre-se",
            href="/admin/cadastro",
            color=COLORS["accent"],
        ),
    )


def _panel(*children: rx.Component, **props: object) -> rx.Component:
    """White bordered panel used by the client and booking pages."""
    return rx.box(
        rx.vstack(*children, align="stretch", spacing="3", width="100%"),
        width="100%",
        padding=rx.breakpoints(initial="18px", sm="22px"),
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
        **props,
    )


def _empty_box(text: str) -> rx.Component:
    return rx.box(
        rx.text(text, color=COLORS["muted"]),
        width="100%",
        padding="22px",
        border=f"1px dashed {COLORS['border']}",
        border_radius="16px",
    )


def _policy_callout() -> rx.Component:
    return rx.callout(
        CANCELLATION_POLICY,
        icon="info",
        color_scheme="gray",
        width="100%",
    )


def _client_appointment_card(appointment: rx.Var[dict[str, Any]]) -> rx.Component:
    return _panel(
        rx.flex(
            rx.vstack(
                rx.heading(
                    appointment["service_name"],
                    size="4",
                    color=COLORS["text"],
                    overflow_wrap="anywhere",
                ),
                rx.text(
                    appointment["start_label"],
                    color=COLORS["text"],
                    weight="bold",
                ),
                align="start",
                spacing="2",
                flex="1",
                min_width="0",
            ),
            rx.badge(
                appointment["status_label"],
                color_scheme=rx.cond(
                    appointment["status"] == "agendado", "green", "gray"
                ),
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "start", "sm": "center"},
            justify="between",
            spacing="3",
            width="100%",
        ),
        rx.text(
            f"{appointment['company_name']} · {appointment['professional_name']}",
            color=COLORS["muted"],
            overflow_wrap="anywhere",
        ),
        rx.text(
            f"{appointment['duration_display']} · {appointment['price_display']}",
            color=COLORS["muted"],
        ),
        rx.cond(
            appointment["is_late_cancellation"],
            rx.callout(
                "Cancelamento tardio: taxa informativa de R$ 5,00.",
                icon="info",
                color_scheme="ruby",
                width="100%",
            ),
            rx.fragment(),
        ),
        rx.flex(
            rx.cond(
                appointment["public_identifier"] != "",
                rx.button(
                    "Agendar de novo",
                    on_click=State.start_fresh_booking(
                        appointment["public_identifier"]
                    ),
                    variant="outline",
                    color=COLORS["accent"],
                    width={"initial": "100%", "sm": "auto"},
                    height="44px",
                    aria_label=f"Agendar de novo em {appointment['company_name']}",
                ),
                rx.fragment(),
            ),
            rx.cond(
                appointment["can_cancel"],
                rx.button(
                    "Cancelar agendamento",
                    on_click=State.open_cancel_dialog(appointment["id"]),
                    variant="outline",
                    color_scheme="ruby",
                    width={"initial": "100%", "sm": "auto"},
                    height="44px",
                ),
                rx.fragment(),
            ),
            direction={"initial": "column", "sm": "row"},
            spacing="3",
            width="100%",
        ),
    )


def _client_appointment_list(
    title: str,
    items: rx.Var[list[dict[str, Any]]],
    empty_text: str,
) -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="5", color=COLORS["text"]),
        rx.cond(
            items.length() == 0,
            _empty_box(empty_text),
            rx.vstack(
                rx.foreach(items, _client_appointment_card),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        align="stretch",
        spacing="3",
        width="100%",
    )


def _cancel_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(
                rx.cond(
                    State.cancel_target_late,
                    "Cancelamento tardio",
                    "Cancelar agendamento",
                )
            ),
            rx.alert_dialog.description(
                rx.text(State.cancel_target_label, weight="medium"),
            ),
            rx.vstack(
                rx.cond(
                    State.cancel_target_late,
                    rx.callout(
                        "Faltam menos de 8 horas para o início. O cancelamento "
                        "será marcado como tardio, com taxa apenas informativa "
                        "de R$ 5,00. Nenhum pagamento é processado.",
                        icon="triangle_alert",
                        color_scheme="ruby",
                        width="100%",
                    ),
                    rx.text(
                        "O cancelamento é gratuito porque faltam 8 horas ou "
                        "mais para o início.",
                        color=COLORS["muted"],
                    ),
                ),
                rx.text(State.cancel_error, color=COLORS["error"], role="alert"),
                align="stretch",
                spacing="3",
                margin_top="12px",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Manter agendamento",
                        variant="soft",
                        color_scheme="gray",
                        disabled=State.cancel_submitting,
                    ),
                ),
                rx.button(
                    rx.cond(
                        State.cancel_target_late,
                        "Confirmar cancelamento tardio",
                        "Confirmar cancelamento",
                    ),
                    on_click=State.confirm_cancel,
                    loading=State.cancel_submitting,
                    color_scheme="ruby",
                ),
                direction={"initial": "column-reverse", "sm": "row"},
                justify="end",
                spacing="3",
                margin_top="16px",
            ),
            max_width="460px",
        ),
        open=State.cancel_dialog_open,
        on_open_change=State.set_cancel_dialog_open,
    )


def client_appointments_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.link(_brand(), href="/", underline="none"),
                rx.button(
                    "Sair",
                    on_click=State.logout,
                    variant="outline",
                    color=COLORS["accent"],
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            _panel(
                rx.heading(
                    "Meus agendamentos",
                    size={"initial": "6", "sm": "7"},
                    color=COLORS["text"],
                ),
                rx.cond(
                    State.user_name != "",
                    rx.text(f"Olá, {State.user_name}.", color=COLORS["muted"]),
                    rx.fragment(),
                ),
                rx.link(
                    rx.button(
                        "Novo agendamento",
                        width="100%",
                        height="48px",
                        background_color=COLORS["accent"],
                        color=COLORS["surface"],
                    ),
                    href="/saloes",
                    width={"initial": "100%", "sm": "auto"},
                ),
                _policy_callout(),
            ),
            rx.cond(
                State.client_notice != "",
                rx.callout(
                    State.client_notice,
                    icon="info",
                    color_scheme="green",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.client_appointments_loading,
                rx.text("Carregando agendamentos...", color=COLORS["muted"]),
                rx.cond(
                    State.client_appointments_error != "",
                    rx.text(
                        State.client_appointments_error,
                        role="alert",
                        color=COLORS["error"],
                    ),
                    rx.vstack(
                        _client_appointment_list(
                            "Próximos",
                            State.client_upcoming,
                            "Você não tem agendamentos futuros. Use “Novo "
                            "agendamento” para encontrar um salão.",
                        ),
                        _client_appointment_list(
                            "Passados",
                            State.client_past,
                            "Nenhum agendamento passado.",
                        ),
                        align="stretch",
                        spacing="5",
                        width="100%",
                    ),
                ),
            ),
            _cancel_dialog(),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="720px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _salon_card(salon: rx.Var[dict[str, str]]) -> rx.Component:
    return _panel(
        rx.flex(
            rx.heading(
                salon["name"],
                size="4",
                color=COLORS["text"],
                overflow_wrap="anywhere",
                flex="1",
                min_width="0",
            ),
            rx.button(
                "Agendar",
                on_click=State.start_fresh_booking(salon["identifier"]),
                width={"initial": "100%", "sm": "auto"},
                height="44px",
                background_color=COLORS["accent"],
                color=COLORS["surface"],
                aria_label=f"Agendar em {salon['name']}",
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "stretch", "sm": "center"},
            justify="between",
            spacing="3",
            width="100%",
        ),
    )


def salons_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.link(_brand(), href="/", underline="none"),
                rx.cond(
                    State.client_signed_in,
                    rx.link("Meus agendamentos", href="/meus-agendamentos"),
                    rx.fragment(),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            _panel(
                rx.heading(
                    "Encontrar salões",
                    size={"initial": "6", "sm": "7"},
                    color=COLORS["text"],
                ),
                rx.text(
                    "Escolha um salão para ver os serviços e agendar seu horário.",
                    color=COLORS["muted"],
                ),
            ),
            rx.cond(
                State.salons_loading,
                rx.text("Carregando salões...", color=COLORS["muted"]),
                rx.cond(
                    State.salons_error != "",
                    rx.text(
                        State.salons_error,
                        role="alert",
                        color=COLORS["error"],
                    ),
                    rx.cond(
                        State.salons.length() == 0,
                        _empty_box(
                            "Ainda não há salões disponíveis para agendamento."
                        ),
                        rx.vstack(
                            rx.foreach(State.salons, _salon_card),
                            align="stretch",
                            spacing="3",
                            width="100%",
                        ),
                    ),
                ),
            ),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="720px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _service_form_field(
    label: str,
    name: str,
    value: rx.Var[str],
    on_change: rx.EventHandler,
    error: rx.Var[str],
    **input_props: object,
) -> rx.Component:
    error_id = f"{name}-error"
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color=COLORS["text"]),
        rx.input(
            name=name,
            value=value,
            on_change=on_change,
            width="100%",
            size="3",
            style=FORM_FIELD_STYLE,
            aria_invalid=error != "",
            aria_describedby=error_id,
            **input_props,
        ),
        rx.text(
            error,
            id=error_id,
            role="alert",
            size="2",
            color=COLORS["error"],
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _service_duration_field(
    value: rx.Var[str],
    on_change: rx.EventHandler,
    error: rx.Var[str],
) -> rx.Component:
    return rx.vstack(
        rx.text(
            "Duração",
            size="2",
            weight="medium",
            color=COLORS["text"],
        ),
        rx.select.root(
            rx.select.trigger(
                placeholder="Selecione a duração",
                width="100%",
                style=FORM_FIELD_STYLE,
            ),
            rx.select.content(
                rx.select.group(
                    *[
                        rx.select.item(label, value=minutes)
                        for minutes, label in DURATION_OPTIONS
                    ]
                )
            ),
            name="service_duration",
            value=value,
            on_change=on_change,
            size="3",
            width="100%",
        ),
        rx.text(
            error,
            role="alert",
            size="2",
            color=COLORS["error"],
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _service_card(service: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.flex(
                    rx.heading(
                        service["name"],
                        size="4",
                        color=COLORS["text"],
                        min_width=0,
                        overflow_wrap="anywhere",
                    ),
                    rx.badge(
                        rx.cond(service["is_active"], "Ativo", "Inativo"),
                        color_scheme=rx.cond(
                            service["is_active"], "green", "gray"
                        ),
                    ),
                    align="center",
                    wrap="wrap",
                    spacing="3",
                ),
                rx.text(
                    service["duration_display"],
                    color=COLORS["muted"],
                    size="2",
                ),
                rx.text(
                    service["price_display"],
                    color=COLORS["text"],
                    weight="bold",
                    size="4",
                ),
                align="start",
                spacing="2",
                flex="1",
            ),
            rx.flex(
                rx.button(
                    "Editar",
                    on_click=State.begin_service_edit(
                        service["id"],
                        service["name"],
                        service["duration_minutes"],
                        service["price_cents"],
                    ),
                    variant="outline",
                    height="44px",
                    color=COLORS["accent"],
                    border_color=COLORS["border"],
                    _hover={"background_color": COLORS["background"]},
                ),
                rx.button(
                    rx.cond(service["is_active"], "Desativar", "Reativar"),
                    on_click=State.toggle_service_status(service["id"]),
                    height="44px",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                    _hover={"background_color": COLORS["accent_hover"]},
                ),
                direction={"initial": "column", "sm": "row"},
                spacing="2",
                width={"initial": "100%", "sm": "auto"},
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "stretch", "sm": "center"},
            spacing="4",
            width="100%",
        ),
        width="100%",
        padding={"initial": "18px", "sm": "22px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )


def _admin_header() -> rx.Component:
    return rx.flex(
        _brand(),
        rx.flex(
            rx.link(
                "Painel",
                href="/admin",
                color=COLORS["accent"],
                font_weight="medium",
            ),
            rx.link(
                "Serviços",
                href="/admin/servicos",
                color=COLORS["accent"],
                font_weight="medium",
            ),
            rx.link(
                "Profissionais",
                href="/admin/profissionais",
                color=COLORS["accent"],
                font_weight="medium",
            ),
            rx.link(
                "Horários",
                href="/admin/horarios",
                color=COLORS["accent"],
                font_weight="medium",
            ),
            rx.link(
                "Agenda",
                href="/admin/agenda",
                color=COLORS["accent"],
                font_weight="medium",
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "stretch", "sm": "center"},
            wrap="wrap",
            spacing="4",
            width={"initial": "100%", "sm": "auto"},
        ),
        rx.button(
            "Sair",
            on_click=State.logout,
            variant="outline",
            height="44px",
            color=COLORS["accent"],
            border_color=COLORS["border"],
            width={"initial": "100%", "sm": "auto"},
        ),
        direction={"initial": "column", "sm": "row"},
        align={"initial": "stretch", "sm": "center"},
        justify="between",
        width="100%",
        spacing="4",
    )


def _hour_card(hour: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.heading(
                    hour["day_name"],
                    size="4",
                    color=COLORS["text"],
                ),
                rx.text(
                    f"{hour['start_label']} – {hour['end_label']}",
                    color=COLORS["muted"],
                ),
                align="start",
                spacing="2",
                flex="1",
            ),
            rx.flex(
                rx.button(
                    "Editar",
                    on_click=State.begin_hour_edit(
                        hour["id"],
                        hour["day_of_week"],
                        hour["start_minute"],
                        hour["end_minute"],
                    ),
                    variant="outline",
                    height="44px",
                    color=COLORS["accent"],
                    border_color=COLORS["border"],
                    width={"initial": "100%", "sm": "auto"},
                ),
                rx.button(
                    "Remover",
                    on_click=State.remove_hour(hour["id"]),
                    variant="outline",
                    height="44px",
                    color=COLORS["error"],
                    border_color=COLORS["border"],
                    width={"initial": "100%", "sm": "auto"},
                ),
                direction={"initial": "column", "sm": "row"},
                spacing="2",
                width={"initial": "100%", "sm": "auto"},
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "stretch", "sm": "center"},
            spacing="4",
            width="100%",
        ),
        width="100%",
        padding={"initial": "18px", "sm": "22px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )


def _agenda_card(appointment: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.heading(
                        appointment["service_name"],
                        size="4",
                        color=COLORS["text"],
                        min_width="0",
                        overflow_wrap="anywhere",
                    ),
                    rx.text(
                        appointment["start_label"],
                        color=COLORS["text"],
                        weight="bold",
                    ),
                    align="start",
                    spacing="2",
                    flex="1",
                    min_width="0",
                ),
                rx.badge(
                    appointment["status_label"],
                    color_scheme=rx.cond(
                        appointment["status"] == "agendado",
                        "green",
                        "gray",
                    ),
                ),
                direction={"initial": "column", "sm": "row"},
                align={"initial": "start", "sm": "center"},
                justify="between",
                spacing="3",
                width="100%",
            ),
            rx.text(
                f"Cliente: {appointment['client_name']}",
                color=COLORS["text"],
                overflow_wrap="anywhere",
            ),
            rx.text(
                f"Profissional: {appointment['professional_name']}",
                color=COLORS["muted"],
                overflow_wrap="anywhere",
            ),
            rx.text(
                f"Término: {appointment['end_label']}",
                color=COLORS["muted"],
            ),
            rx.cond(
                appointment["is_late_cancellation"],
                rx.callout(
                    "Cancelamento tardio",
                    icon="info",
                    color_scheme="ruby",
                    width="100%",
                ),
                rx.box(),
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding={"initial": "18px", "sm": "22px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )


def admin_hours_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _admin_header(),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Horários de atendimento",
                        size={"initial": "6", "sm": "7"},
                        color=COLORS["text"],
                    ),
                    rx.text(State.company_name, color=COLORS["muted"]),
                    rx.vstack(
                        rx.text(
                            "Profissional",
                            size="2",
                            weight="medium",
                            color=COLORS["text"],
                        ),
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecione um profissional",
                                width="100%",
                            ),
                            rx.select.content(
                                rx.foreach(
                                    State.hours_professional_options,
                                    lambda professional: rx.select.item(
                                        professional["name"],
                                        value=professional["id"],
                                    ),
                                )
                            ),
                            value=State.selected_hours_professional_id,
                            on_change=State.set_hours_professional,
                            size="3",
                            width="100%",
                        ),
                        align="stretch",
                        spacing="2",
                        width="100%",
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["tile"],
            ),
            rx.box(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            State.editing_hour_id > 0,
                            "Editar período",
                            "Cadastrar período",
                        ),
                        size="5",
                        color=COLORS["text"],
                    ),
                    rx.form(
                        rx.vstack(
                            rx.vstack(
                                rx.text(
                                    "Dia da semana",
                                    size="2",
                                    weight="medium",
                                    color=COLORS["text"],
                                ),
                                rx.select.root(
                                    rx.select.trigger(width="100%"),
                                    rx.select.content(
                                        rx.select.group(
                                            *[
                                                rx.select.item(
                                                    label,
                                                    value=value,
                                                )
                                                for value, label in WEEKDAY_OPTIONS
                                            ]
                                        )
                                    ),
                                    name="day_of_week",
                                    value=State.hours_day,
                                    on_change=State.set_hours_day,
                                    size="3",
                                    width="100%",
                                ),
                                align="stretch",
                                spacing="2",
                                width="100%",
                            ),
                            rx.flex(
                                rx.vstack(
                                    rx.text(
                                        "Início",
                                        size="2",
                                        weight="medium",
                                        color=COLORS["text"],
                                    ),
                                    rx.input(
                                        name="start_time",
                                        type="text",
                                        value=State.hours_start,
                                        on_change=State.set_hours_start,
                                        placeholder="09:00",
                                        pattern="(?:[01][0-9]|2[0-3]):[0-5][0-9]",
                                        required=True,
                                        width="100%",
                                        size="3",
                                    ),
                                    align="stretch",
                                    spacing="2",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "Término",
                                        size="2",
                                        weight="medium",
                                        color=COLORS["text"],
                                    ),
                                    rx.input(
                                        name="end_time",
                                        type="text",
                                        value=State.hours_end,
                                        on_change=State.set_hours_end,
                                        placeholder="18:00",
                                        pattern="(?:[01][0-9]|2[0-3]):[0-5][0-9]|24:00",
                                        required=True,
                                        width="100%",
                                        size="3",
                                    ),
                                    align="stretch",
                                    spacing="2",
                                    width="100%",
                                ),
                                direction={"initial": "column", "sm": "row"},
                                spacing="4",
                                width="100%",
                            ),
                            rx.text(
                                "Use o formato HH:MM. Para encerrar à meia-noite, use 24:00.",
                                size="2",
                                color=COLORS["muted"],
                            ),
                            rx.text(
                                State.hours_error,
                                role="alert",
                                color=COLORS["error"],
                                size="2",
                            ),
                            rx.text(
                                State.hours_notice,
                                role="status",
                                color=COLORS["accent"],
                                size="2",
                            ),
                            rx.flex(
                                rx.button(
                                    rx.cond(
                                        State.editing_hour_id > 0,
                                        "Salvar alterações",
                                        "Cadastrar período",
                                    ),
                                    type="submit",
                                    height="52px",
                                    width={"initial": "100%", "sm": "auto"},
                                    disabled=(
                                        State.selected_hours_professional_id
                                        == ""
                                    ),
                                    background_color=COLORS["accent"],
                                    color=COLORS["surface"],
                                    _hover={
                                        "background_color": COLORS[
                                            "accent_hover"
                                        ]
                                    },
                                ),
                                rx.cond(
                                    State.editing_hour_id > 0,
                                    rx.button(
                                        "Cancelar edição",
                                        type="button",
                                        on_click=State.cancel_hour_edit,
                                        variant="outline",
                                        height="52px",
                                        width={"initial": "100%", "sm": "auto"},
                                        color=COLORS["accent"],
                                        border_color=COLORS["border"],
                                    ),
                                    rx.box(),
                                ),
                                direction={"initial": "column", "sm": "row"},
                                spacing="3",
                                width="100%",
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
                        ),
                        id="hours-form",
                        on_submit=State.submit_hour,
                        reset_on_submit=False,
                        width="100%",
                    ),
                    align="stretch",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["card"],
            ),
            rx.vstack(
                rx.heading("Períodos semanais", size="5", color=COLORS["text"]),
                rx.cond(
                    State.hours_loading,
                    rx.text(
                        "Carregando horários...",
                        color=COLORS["muted"],
                    ),
                    rx.cond(
                        State.hours_error != "",
                        rx.text(
                            State.hours_error,
                            role="alert",
                            color=COLORS["error"],
                        ),
                        rx.cond(
                            State.hours_professional_options.length() == 0,
                            rx.text(
                                "Cadastre e ative um profissional antes de configurar horários.",
                                color=COLORS["muted"],
                            ),
                            rx.cond(
                                State.hour_items.length() == 0,
                                rx.box(
                                    rx.text(
                                        "Este profissional ainda não tem períodos de atendimento.",
                                        color=COLORS["muted"],
                                    ),
                                    width="100%",
                                    padding="22px",
                                    border=f"1px dashed {COLORS['border']}",
                                    border_radius="16px",
                                ),
                                rx.vstack(
                                    rx.foreach(State.hour_items, _hour_card),
                                    align="stretch",
                                    spacing="3",
                                    width="100%",
                                ),
                            ),
                        ),
                    ),
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="820px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def admin_agenda_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _admin_header(),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Agenda do salão",
                        size={"initial": "6", "sm": "7"},
                        color=COLORS["text"],
                    ),
                    rx.text(State.company_name, color=COLORS["muted"]),
                    rx.flex(
                        rx.vstack(
                            rx.text(
                                "Dia",
                                size="2",
                                weight="medium",
                                color=COLORS["text"],
                            ),
                            rx.input(
                                type="date",
                                value=State.agenda_date,
                                on_change=State.set_agenda_date,
                                width="100%",
                                size="3",
                            ),
                            align="stretch",
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text(
                                "Profissional",
                                size="2",
                                weight="medium",
                                color=COLORS["text"],
                            ),
                            rx.select.root(
                                rx.select.trigger(
                                    placeholder="Todos os profissionais",
                                    width="100%",
                                ),
                                rx.select.content(
                                    rx.foreach(
                                        State.agenda_professional_options,
                                        lambda professional: rx.select.item(
                                            professional["name"],
                                            value=professional["id"],
                                        ),
                                    )
                                ),
                                value=State.agenda_professional_id,
                                on_change=State.set_agenda_professional,
                                size="3",
                                width="100%",
                            ),
                            align="stretch",
                            spacing="2",
                            width="100%",
                        ),
                        direction={"initial": "column", "sm": "row"},
                        spacing="4",
                        width="100%",
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["tile"],
            ),
            rx.vstack(
                rx.cond(
                    State.agenda_loading,
                    rx.text("Carregando agenda...", color=COLORS["muted"]),
                    rx.cond(
                        State.agenda_error != "",
                        rx.text(
                            State.agenda_error,
                            role="alert",
                            color=COLORS["error"],
                        ),
                        rx.cond(
                            State.agenda_items.length() == 0,
                            rx.box(
                                rx.text(
                                    "Não há reservas para este dia e filtro.",
                                    color=COLORS["muted"],
                                ),
                                width="100%",
                                padding="22px",
                                border=f"1px dashed {COLORS['border']}",
                                border_radius="16px",
                            ),
                            rx.vstack(
                                rx.foreach(State.agenda_items, _agenda_card),
                                align="stretch",
                                spacing="3",
                                width="100%",
                            ),
                        ),
                    ),
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="820px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _admin_area_card(
    title: str,
    description: str,
    href: str = "",
) -> rx.Component:
    content = rx.vstack(
        rx.heading(title, size="4", color=COLORS["text"]),
        rx.text(description, color=COLORS["muted"], line_height="1.6"),
        align="start",
        spacing="2",
        width="100%",
    )
    card = rx.box(
        content,
        width="100%",
        min_height="112px",
        padding={"initial": "18px", "sm": "22px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )
    if href:
        return rx.link(card, href=href, width="100%", underline="none")
    return card


def admin_dashboard_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _admin_header(),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Painel administrativo",
                        size={"initial": "6", "sm": "7"},
                        color=COLORS["text"],
                    ),
                    rx.text(State.company_name, color=COLORS["muted"]),
                    align="stretch",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["tile"],
            ),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Link público do salão",
                        size="5",
                        color=COLORS["text"],
                    ),
                    rx.cond(
                        State.public_link != "",
                        rx.link(
                            State.public_link,
                            href=State.public_link,
                            color=COLORS["accent"],
                            word_break="break-all",
                        ),
                        rx.text(
                            "Preparando o link público...",
                            color=COLORS["muted"],
                        ),
                    ),
                    rx.button(
                        "Copiar link",
                        on_click=State.copy_public_link,
                        disabled=State.public_link == "",
                        height="48px",
                        width={"initial": "100%", "sm": "auto"},
                        background_color=COLORS["accent"],
                        color=COLORS["surface"],
                        _hover={"background_color": COLORS["accent_hover"]},
                    ),
                    rx.text(
                        State.clipboard_notice,
                        role="status",
                        color=COLORS["muted"],
                        size="2",
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["tile"],
            ),
            rx.cond(
                State.dashboard_loading,
                rx.text("Carregando painel...", color=COLORS["muted"]),
                rx.text(
                    State.dashboard_error,
                    role="alert",
                    color=COLORS["error"],
                ),
            ),
            rx.grid(
                _admin_area_card(
                    "Serviços",
                    "Cadastre e mantenha o catálogo da empresa.",
                    "/admin/servicos",
                ),
                _admin_area_card(
                    "Profissionais",
                    "Gerencie a equipe e os serviços realizados.",
                    "/admin/profissionais",
                ),
                _admin_area_card(
                    "Horários",
                    "Configure os períodos semanais de cada profissional.",
                    "/admin/horarios",
                ),
                _admin_area_card(
                    "Agenda",
                    "Consulte os agendamentos por dia e profissional.",
                    "/admin/agenda",
                ),
                columns={"initial": "1", "sm": "2"},
                spacing="4",
                width="100%",
            ),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="820px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _professional_card(
    professional: rx.Var[dict[str, Any]],
) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.flex(
                    rx.heading(
                        professional["name"],
                        size="4",
                        color=COLORS["text"],
                        min_width=0,
                        overflow_wrap="anywhere",
                    ),
                    rx.badge(
                        rx.cond(
                            professional["is_active"],
                            "Ativo",
                            "Inativo",
                        ),
                        color_scheme=rx.cond(
                            professional["is_active"], "green", "gray"
                        ),
                    ),
                    align="center",
                    wrap="wrap",
                    spacing="3",
                ),
                rx.text(
                    professional["services_label"],
                    color=COLORS["muted"],
                    size="2",
                    overflow_wrap="anywhere",
                ),
                align="start",
                spacing="2",
                flex="1",
                min_width="0",
            ),
            rx.flex(
                rx.button(
                    "Editar",
                    on_click=State.begin_professional_edit(
                        professional["id"]
                    ),
                    variant="outline",
                    height="44px",
                    color=COLORS["accent"],
                    border_color=COLORS["border"],
                    width={"initial": "100%", "sm": "auto"},
                ),
                rx.button(
                    rx.cond(
                        professional["is_active"],
                        "Desativar",
                        "Reativar",
                    ),
                    on_click=State.toggle_professional_status(
                        professional["id"]
                    ),
                    height="44px",
                    color=COLORS["surface"],
                    background_color=COLORS["accent"],
                    _hover={"background_color": COLORS["accent_hover"]},
                    width={"initial": "100%", "sm": "auto"},
                ),
                direction={"initial": "column", "sm": "row"},
                spacing="2",
                width={"initial": "100%", "sm": "auto"},
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "stretch", "sm": "center"},
            spacing="4",
            width="100%",
            min_width="0",
        ),
        width="100%",
        min_width="0",
        padding={"initial": "18px", "sm": "22px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="18px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )


def admin_professionals_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _admin_header(),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Profissionais da empresa",
                        size={"initial": "6", "sm": "7"},
                        color=COLORS["text"],
                    ),
                    rx.text(State.company_name, color=COLORS["muted"]),
                    align="stretch",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["tile"],
            ),
            rx.box(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            State.editing_professional_id > 0,
                            "Editar profissional",
                            "Cadastrar profissional",
                        ),
                        size="5",
                        color=COLORS["text"],
                    ),
                    rx.cond(
                        (State.professional_service_options.length() == 0)
                        & (State.editing_professional_id == 0),
                        rx.callout(
                            "Cadastre um serviço ativo antes de criar um profissional.",
                            icon="info",
                            color_scheme="ruby",
                        ),
                        rx.box(),
                    ),
                    rx.form(
                        rx.vstack(
                            rx.vstack(
                                rx.text(
                                    "Nome",
                                    size="2",
                                    weight="medium",
                                    color=COLORS["text"],
                                ),
                                rx.input(
                                    name="professional_name",
                                    value=State.professional_name,
                                    on_change=State.set_professional_name,
                                    required=True,
                                    width="100%",
                                    size="3",
                                    style=FORM_FIELD_STYLE,
                                    placeholder="Nome do profissional",
                                    aria_invalid=(
                                        State.professional_name_error != ""
                                    ),
                                    aria_describedby=(
                                        "professional-name-error"
                                    ),
                                ),
                                rx.text(
                                    State.professional_name_error,
                                    id="professional-name-error",
                                    role="alert",
                                    size="2",
                                    color=COLORS["error"],
                                ),
                                align="stretch",
                                spacing="2",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Serviços que realiza",
                                    size="2",
                                    weight="medium",
                                    color=COLORS["text"],
                                ),
                                rx.cond(
                                    State.professional_service_options.length()
                                    > 0,
                                    rx.vstack(
                                        rx.foreach(
                                            State.professional_service_options,
                                            lambda service: rx.checkbox(
                                                service["name"],
                                                value=service["id"],
                                                name="service_ids",
                                                checked=State.professional_service_ids.contains(
                                                    service["id"]
                                                ),
                                                on_change=State.toggle_professional_service_selection(
                                                    service["id"]
                                                ),
                                                color_scheme="ruby",
                                            ),
                                        ),
                                        align="stretch",
                                        spacing="3",
                                        width="100%",
                                    ),
                                    rx.text(
                                        "Não há serviços ativos para selecionar.",
                                        color=COLORS["muted"],
                                        size="2",
                                    ),
                                ),
                                align="stretch",
                                spacing="3",
                                width="100%",
                            ),
                            rx.text(
                                State.professionals_error,
                                role="alert",
                                color=COLORS["error"],
                                size="2",
                            ),
                            rx.text(
                                State.professionals_notice,
                                role="status",
                                color=COLORS["accent"],
                                size="2",
                            ),
                            rx.flex(
                                rx.button(
                                    rx.cond(
                                        State.editing_professional_id > 0,
                                        "Salvar alterações",
                                        "Cadastrar profissional",
                                    ),
                                    type="submit",
                                    height="52px",
                                    width={"initial": "100%", "sm": "auto"},
                                    disabled=(
                                        (State.professional_service_options.length()
                                        == 0)
                                        & (State.editing_professional_id == 0)
                                    ),
                                    background_color=COLORS["accent"],
                                    color=COLORS["surface"],
                                    _hover={
                                        "background_color": COLORS[
                                            "accent_hover"
                                        ]
                                    },
                                ),
                                rx.cond(
                                    State.editing_professional_id > 0,
                                    rx.button(
                                        "Cancelar edição",
                                        type="button",
                                        on_click=State.cancel_professional_edit,
                                        variant="outline",
                                        height="52px",
                                        width={"initial": "100%", "sm": "auto"},
                                        color=COLORS["accent"],
                                        border_color=COLORS["border"],
                                    ),
                                    rx.box(),
                                ),
                                direction={"initial": "column", "sm": "row"},
                                spacing="3",
                                width="100%",
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
                        ),
                        id="professional-form",
                        on_submit=State.submit_professional,
                        reset_on_submit=False,
                        width="100%",
                    ),
                    align="stretch",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                min_width="0",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["card"],
            ),
            rx.vstack(
                rx.heading(
                    "Equipe",
                    size="5",
                    color=COLORS["text"],
                ),
                rx.cond(
                    State.professionals_loading,
                    rx.text(
                        "Carregando profissionais...",
                        color=COLORS["muted"],
                    ),
                    rx.cond(
                        State.professionals_error != "",
                        rx.text(
                            State.professionals_error,
                            role="alert",
                            color=COLORS["error"],
                        ),
                        rx.cond(
                            State.professional_items.length() == 0,
                            rx.box(
                                rx.vstack(
                                    rx.text(
                                        "Sua empresa ainda não tem profissionais cadastrados.",
                                        color=COLORS["muted"],
                                    ),
                                    rx.link(
                                        rx.button(
                                            "Cadastrar o primeiro profissional",
                                            height="48px",
                                            width="100%",
                                            background_color=COLORS["accent"],
                                            color=COLORS["surface"],
                                        ),
                                        href="#professional-form",
                                        width="100%",
                                    ),
                                    align="stretch",
                                    spacing="3",
                                    width="100%",
                                ),
                                width="100%",
                                padding="22px",
                                border=f"1px dashed {COLORS['border']}",
                                border_radius="16px",
                            ),
                            rx.vstack(
                                rx.foreach(
                                    State.professional_items,
                                    _professional_card,
                                ),
                                align="stretch",
                                spacing="3",
                                width="100%",
                            ),
                        ),
                    ),
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="820px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def admin_services_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _admin_header(),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Serviços da empresa",
                        size={"initial": "6", "sm": "7"},
                        color=COLORS["text"],
                    ),
                    rx.text(State.company_name, color=COLORS["muted"]),
                    rx.link(
                        rx.text(
                            f"/agendar/{State.company_identifier}",
                            word_break="break-all",
                        ),
                        href=f"/agendar/{State.company_identifier}",
                        color=COLORS["accent"],
                    ),
                    align="stretch",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["tile"],
            ),
            rx.box(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            State.editing_service_id > 0,
                            "Editar serviço",
                            "Cadastrar serviço",
                        ),
                        size="5",
                        color=COLORS["text"],
                    ),
                    rx.form(
                        rx.vstack(
                            _service_form_field(
                                "Nome",
                                "service_name",
                                State.service_name,
                                State.set_service_name,
                                State.service_name_error,
                                type="text",
                                min_length=2,
                                max_length=80,
                                placeholder="Ex.: Corte feminino",
                            ),
                            _service_duration_field(
                                State.service_duration,
                                State.set_service_duration,
                                State.service_duration_error,
                            ),
                            _service_form_field(
                                "Preço (R$)",
                                "service_price",
                                State.service_price,
                                State.set_service_price,
                                State.service_price_error,
                                type="number",
                                min=0,
                                max="99999.99",
                                step="0.01",
                                placeholder="Ex.: 75,00",
                            ),
                            rx.text(
                                State.services_error,
                                role="alert",
                                color=COLORS["error"],
                                size="2",
                            ),
                            rx.text(
                                State.services_notice,
                                role="status",
                                color=COLORS["accent"],
                                size="2",
                            ),
                            rx.flex(
                                rx.button(
                                    rx.cond(
                                        State.editing_service_id > 0,
                                        "Salvar alterações",
                                        "Cadastrar serviço",
                                    ),
                                    type="submit",
                                    height="52px",
                                    width={"initial": "100%", "sm": "auto"},
                                    background_color=COLORS["accent"],
                                    color=COLORS["surface"],
                                    _hover={
                                        "background_color": COLORS["accent_hover"]
                                    },
                                ),
                                rx.cond(
                                    State.editing_service_id > 0,
                                    rx.button(
                                        "Cancelar edição",
                                        type="button",
                                        on_click=State.cancel_service_edit,
                                        variant="outline",
                                        height="52px",
                                        width={"initial": "100%", "sm": "auto"},
                                        color=COLORS["accent"],
                                        border_color=COLORS["border"],
                                    ),
                                    rx.box(),
                                ),
                                direction={"initial": "column", "sm": "row"},
                                spacing="3",
                                width="100%",
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
                        ),
                        id="service-form",
                        on_submit=State.submit_service,
                        reset_on_submit=False,
                        width="100%",
                    ),
                    align="stretch",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                padding={"initial": "20px", "sm": "26px"},
                border=f"1px solid {COLORS['border']}",
                border_radius="20px",
                background_color=COLORS["surface"],
                box_shadow=SHADOWS["card"],
            ),
            rx.vstack(
                rx.heading("Catálogo", size="5", color=COLORS["text"]),
                rx.cond(
                    State.services_loading,
                    rx.text("Carregando serviços...", color=COLORS["muted"]),
                    rx.cond(
                        State.services_error != "",
                        rx.text(
                            State.services_error,
                            role="alert",
                            color=COLORS["error"],
                        ),
                        rx.cond(
                            State.service_items.length() == 0,
                            rx.box(
                                rx.vstack(
                                    rx.text(
                                        "Sua empresa ainda não tem serviços cadastrados.",
                                        color=COLORS["muted"],
                                    ),
                                    rx.link(
                                        rx.button(
                                            "Cadastrar o primeiro serviço",
                                            height="48px",
                                            background_color=COLORS["accent"],
                                            color=COLORS["surface"],
                                        ),
                                        href="#service-form",
                                        width="100%",
                                    ),
                                    align="stretch",
                                    spacing="3",
                                    width="100%",
                                ),
                                width="100%",
                                padding="22px",
                                border=f"1px dashed {COLORS['border']}",
                                border_radius="16px",
                            ),
                            rx.vstack(
                                rx.foreach(State.service_items, _service_card),
                                align="stretch",
                                spacing="3",
                                width="100%",
                            ),
                        ),
                    ),
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="820px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _public_service_card(service: rx.Var[dict[str, Any]]) -> rx.Component:
    selected = State.booking_service_id == service["id"]
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.heading(
                    service["name"],
                    size="4",
                    color=COLORS["text"],
                    min_width=0,
                    overflow_wrap="anywhere",
                ),
                rx.text(
                    f"{service['duration_display']} · {service['price_display']}",
                    color=COLORS["muted"],
                    size="2",
                ),
                align="start",
                spacing="2",
                flex="1",
                min_width="0",
            ),
            rx.button(
                rx.cond(selected, "Selecionado", "Escolher"),
                on_click=State.select_booking_service(service["id"]),
                variant=rx.cond(selected, "solid", "outline"),
                color_scheme="ruby",
                width={"initial": "100%", "sm": "auto"},
                height="44px",
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "stretch", "sm": "center"},
            justify="between",
            spacing="3",
            width="100%",
        ),
        border=rx.cond(
            selected,
            f"2px solid {COLORS['accent']}",
            f"1px solid {COLORS['border']}",
        ),
        style=TILE_STYLE,
    )


def _booking_step(number: str, title: str, *children: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.divider(color=COLORS["border"]),
        rx.heading(f"{number}. {title}", size="5", color=COLORS["text"]),
        *children,
        align="stretch",
        spacing="3",
        width="100%",
    )


def _choice_button(
    label: rx.Var[str],
    selected: rx.Var[bool],
    on_click: Any,
) -> rx.Component:
    return rx.button(
        label,
        on_click=on_click,
        variant=rx.cond(selected, "solid", "outline"),
        color_scheme="ruby",
        height="44px",
        min_width="88px",
    )


def _booking_professional_step() -> rx.Component:
    return _booking_step(
        "2",
        "Profissional",
        rx.cond(
            State.booking_professionals_loading,
            rx.text("Carregando profissionais...", color=COLORS["muted"]),
            rx.cond(
                State.booking_professionals_error != "",
                rx.text(
                    State.booking_professionals_error,
                    role="alert",
                    color=COLORS["error"],
                ),
                rx.flex(
                    rx.foreach(
                        State.booking_professional_options,
                        lambda option: _choice_button(
                            option["name"],
                            State.booking_professional_id == option["id"],
                            State.select_booking_professional(option["id"]),
                        ),
                    ),
                    wrap="wrap",
                    spacing="2",
                    width="100%",
                ),
            ),
        ),
    )


def _booking_day_button(day: rx.Var[dict[str, Any]]) -> rx.Component:
    selected = State.booking_date == day["date"]
    return rx.button(
        rx.vstack(
            rx.text(day["weekday"], size="1"),
            rx.text(day["label"], size="2", weight="bold"),
            spacing="0",
            align="center",
        ),
        on_click=State.set_booking_date(day["date"]),
        disabled=~day["available"].to(bool),
        variant=rx.cond(selected, "solid", "outline"),
        color_scheme=rx.cond(day["available"].to(bool), "ruby", "gray"),
        text_decoration=rx.cond(day["available"].to(bool), "none", "line-through"),
        aria_label=rx.cond(
            day["available"].to(bool),
            f"{day['weekday']} {day['label']}",
            f"{day['weekday']} {day['label']} indisponível",
        ),
        height="56px",
        width="100%",
    )


def _booking_day_step() -> rx.Component:
    return _booking_step(
        "3",
        "Dia e horário",
        rx.text(
            "Escolha um dia entre hoje e os próximos 30 dias. Dias riscados "
            "não têm horários livres.",
            color=COLORS["muted"],
            size="2",
        ),
        rx.cond(
            State.booking_days_loading,
            rx.text("Carregando dias disponíveis...", color=COLORS["muted"]),
            rx.cond(
                State.booking_days_error != "",
                rx.text(
                    State.booking_days_error,
                    role="alert",
                    color=COLORS["error"],
                ),
                rx.grid(
                    rx.foreach(State.booking_days, _booking_day_button),
                    columns={"initial": "4", "sm": "7"},
                    spacing="2",
                    width="100%",
                ),
            ),
        ),
        rx.cond(
            State.booking_slots_loading,
            rx.text("Carregando horários...", color=COLORS["muted"]),
            rx.cond(
                State.booking_slots_error != "",
                rx.text(
                    State.booking_slots_error,
                    role="alert",
                    color=COLORS["error"],
                ),
                rx.cond(
                    State.booking_date == "",
                    rx.fragment(),
                    rx.cond(
                        State.booking_slots.length() == 0,
                        _empty_box(
                            "Dia indisponível: não há horários livres. "
                            "Escolha outro dia."
                        ),
                        rx.flex(
                            rx.foreach(
                                State.booking_slots,
                                lambda slot: _choice_button(
                                    slot["label"],
                                    State.booking_slot_start == slot["starts_at"],
                                    State.select_booking_slot(
                                        slot["starts_at"], slot["label"]
                                    ),
                                ),
                            ),
                            wrap="wrap",
                            spacing="2",
                            width="100%",
                        ),
                    ),
                ),
            ),
        ),
    )


def _booking_summary_step() -> rx.Component:
    return _booking_step(
        "4",
        "Confirmação",
        _panel(
            rx.text(
                f"{State.booking_service_name} · {State.booking_service_duration}"
                f" · {State.booking_service_price}",
                weight="bold",
                color=COLORS["text"],
                overflow_wrap="anywhere",
            ),
            rx.text(
                f"Profissional: {State.booking_professional_label}",
                color=COLORS["muted"],
            ),
            rx.text(
                f"Dia {State.booking_date} às {State.booking_slot_label}",
                color=COLORS["muted"],
            ),
        ),
        _policy_callout(),
        rx.cond(
            State.client_signed_in,
            rx.button(
                "Confirmar agendamento",
                on_click=State.confirm_booking,
                loading=State.booking_submitting,
                width="100%",
                height="52px",
                background_color=COLORS["accent"],
                color=COLORS["surface"],
                _hover={"background_color": COLORS["accent_hover"]},
            ),
            rx.vstack(
                rx.text(
                    "Entre ou crie sua conta de cliente para confirmar. Suas "
                    "escolhas serão mantidas.",
                    color=COLORS["muted"],
                ),
                rx.flex(
                    rx.button(
                        "Entrar para confirmar",
                        on_click=State.start_booking_auth("login"),
                        flex="1",
                        height="52px",
                        background_color=COLORS["accent"],
                        color=COLORS["surface"],
                        _hover={"background_color": COLORS["accent_hover"]},
                    ),
                    rx.button(
                        "Criar conta",
                        on_click=State.start_booking_auth("cadastro"),
                        flex="1",
                        height="52px",
                        variant="outline",
                        color=COLORS["accent"],
                    ),
                    direction={"initial": "column", "sm": "row"},
                    spacing="3",
                    width="100%",
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
    )


def _booking_confirmation() -> rx.Component:
    confirmation = State.booking_confirmation
    return rx.vstack(
        rx.callout(
            "Agendamento confirmado!",
            icon="info",
            color_scheme="green",
            width="100%",
        ),
        _panel(
            rx.heading(
                confirmation["service_name"],
                size="5",
                color=COLORS["text"],
                overflow_wrap="anywhere",
            ),
            rx.text(confirmation["start_label"], weight="bold"),
            rx.text(
                f"Empresa: {confirmation['company_name']}",
                color=COLORS["muted"],
            ),
            rx.text(
                f"Profissional: {confirmation['professional_name']}",
                color=COLORS["muted"],
            ),
            rx.text(
                f"Duração: {confirmation['duration_display']} · "
                f"Preço: {confirmation['price_display']}",
                color=COLORS["muted"],
            ),
        ),
        _policy_callout(),
        rx.flex(
            rx.link(
                rx.button(
                    "Ver meus agendamentos",
                    width="100%",
                    height="52px",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                ),
                href="/meus-agendamentos",
                flex="1",
            ),
            rx.button(
                "Fazer outro agendamento",
                on_click=State.new_booking,
                flex="1",
                height="52px",
                variant="outline",
                color=COLORS["accent"],
            ),
            direction={"initial": "column", "sm": "row"},
            spacing="3",
            width="100%",
        ),
        align="stretch",
        spacing="4",
        width="100%",
    )


def _booking_flow() -> rx.Component:
    return rx.vstack(
        rx.heading("1. Serviço", size="5", color=COLORS["text"]),
        rx.cond(
            State.public_services_loading,
            rx.text("Carregando serviços...", color=COLORS["muted"]),
            rx.cond(
                State.public_services_error != "",
                rx.text(
                    State.public_services_error,
                    role="alert",
                    color=COLORS["error"],
                ),
                rx.cond(
                    State.public_service_items.length() == 0,
                    rx.text(
                        "Esta empresa ainda não tem serviços disponíveis.",
                        color=COLORS["muted"],
                    ),
                    rx.vstack(
                        rx.foreach(
                            State.public_service_items,
                            _public_service_card,
                        ),
                        align="stretch",
                        spacing="3",
                        width="100%",
                    ),
                ),
            ),
        ),
        rx.cond(
            State.booking_service_id != 0,
            _booking_professional_step(),
            rx.fragment(),
        ),
        rx.cond(
            State.booking_professional_id != "",
            _booking_day_step(),
            rx.fragment(),
        ),
        rx.cond(
            State.booking_slot_start != 0,
            _booking_summary_step(),
            rx.fragment(),
        ),
        rx.cond(
            State.booking_message != "",
            rx.callout(
                State.booking_message,
                icon="triangle_alert",
                color_scheme="ruby",
                role="alert",
                width="100%",
            ),
            rx.fragment(),
        ),
        align="stretch",
        spacing="4",
        width="100%",
    )


def public_company_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.link(_brand(), href="/", underline="none"),
                rx.cond(
                    State.client_signed_in,
                    rx.link("Meus agendamentos", href="/meus-agendamentos"),
                    rx.fragment(),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.cond(
                        State.public_company_found,
                        rx.vstack(
                            rx.heading(
                                State.public_company_name,
                                size="7",
                                color=COLORS["text"],
                                overflow_wrap="anywhere",
                            ),
                            rx.text(
                                "Escolha o serviço, o profissional, o dia e o "
                                "horário para fazer seu agendamento.",
                                color=COLORS["muted"],
                            ),
                            rx.cond(
                                State.booking_confirmed,
                                _booking_confirmation(),
                                _booking_flow(),
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.heading("Empresa", size="7", color=COLORS["text"]),
                            rx.text(
                                State.public_company_message,
                                color=COLORS["muted"],
                            ),
                            align="stretch",
                            spacing="4",
                        ),
                    ),
                    align="stretch",
                    width="100%",
                ),
                style={**CARD_STYLE, "max_width": "720px"},
            ),
            align="center",
            spacing="6",
            width="100%",
            max_width="720px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


app = rx.App(
    stylesheets=[FONT_STYLESHEET],
    style=GLOBAL_STYLES,
)
app.add_page(index, route="/", title="BeautyTime")
app.add_page(
    client_signup_page,
    route="/clientes/cadastro",
    title="Criar conta de cliente",
    on_load=State.load_client_auth_page,
)
app.add_page(
    client_login_page,
    route="/clientes/login",
    title="Entrar como cliente",
    on_load=State.load_client_auth_page,
)
app.add_page(
    admin_signup_page,
    route="/admin/cadastro",
    title="Cadastrar empresa",
    on_load=State.clear_message,
)
app.add_page(
    admin_login_page,
    route="/admin/login",
    title="Entrar como administradora",
    on_load=State.clear_message,
)
app.add_page(
    admin_dashboard_page,
    route="/admin",
    title="Painel administrativo",
    on_load=State.load_admin_dashboard,
)
app.add_page(
    admin_services_page,
    route="/admin/servicos",
    title="Serviços da empresa",
    on_load=State.load_admin_services,
)
app.add_page(
    admin_professionals_page,
    route="/admin/profissionais",
    title="Profissionais da empresa",
    on_load=State.load_admin_professionals,
)
app.add_page(
    admin_hours_page,
    route="/admin/horarios",
    title="Horários de atendimento",
    on_load=State.load_admin_hours,
)
app.add_page(
    admin_agenda_page,
    route="/admin/agenda",
    title="Agenda do salão",
    on_load=State.load_admin_agenda,
)
app.add_page(
    client_appointments_page,
    route="/meus-agendamentos",
    title="Meus agendamentos",
    on_load=State.load_client_appointments,
)
app.add_page(
    salons_page,
    route="/saloes",
    title="Encontrar salões",
    on_load=State.load_salons,
)
app.add_page(
    client_appointments_page,
    route="/boas-vindas",
    title="Meus agendamentos",
    on_load=rx.redirect("/meus-agendamentos"),
)
app.add_page(
    public_company_page,
    route="/agendar/[identificador]",
    title="Página pública da empresa",
    on_load=State.load_public_company,
)
