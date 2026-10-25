"""BeautyTime booking, account, and public-company pages."""

import re
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
)

IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def _duration_label(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    if not hours:
        return f"{minutes} min"
    if not remainder:
        return f"{hours}h"
    return f"{hours}h {remainder}min"


def _price_label(price_cents: int) -> str:
    return f"R$ {price_cents // 100},{price_cents % 100:02d}"


DURATION_OPTIONS = [
    (str(minutes), _duration_label(minutes)) for minutes in range(15, 481, 15)
]
PAGE_STYLE = {
    "min_height": "100vh",
    "background_color": COLORS["background"],
    "font_family": FONT_FAMILY,
    "padding": {"initial": "28px 16px", "md": "56px 24px"},
}
CARD_STYLE = {
    "width": "100%",
    "max_width": "520px",
    "padding": {"initial": "28px 20px", "md": "40px"},
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
            aria_described_by="public-identifier-help public-identifier-error",
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

    @rx.event
    def clear_message(self):
        self.message = ""
        self.identifier_error = ""

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
        return rx.redirect("/boas-vindas")

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
        return rx.redirect("/boas-vindas")

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
        return rx.redirect("/admin/servicos")

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
        return rx.redirect("/admin/servicos")

    @rx.event
    def load_welcome(self):
        if not self._auth_token:
            self.user_role = ""
            self.user_name = ""
            self.message = "Entre na sua conta para ver esta página."
            return
        if not self._load_identity(self.user_role):
            self._auth_token = ""

    @rx.event
    def logout(self):
        self._auth_token = ""
        self.user_name = ""
        self.user_role = ""
        self.company_name = ""
        self.company_identifier = ""
        self.service_items = []
        self.message = ""
        return rx.redirect("/")

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

    @rx.event
    def load_public_company(self):
        path = str(self.router.url.path).rstrip("/")
        identifier = unquote(path.rsplit("/", 1)[-1]).strip()
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
                    "name": item["name"],
                    "duration_display": _duration_label(duration),
                    "price_display": _price_label(price_cents),
                }
            )


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
        rx.link("Já tem conta? Entrar", href="/clientes/login", color=COLORS["accent"]),
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
        rx.link("Ainda não tem conta? Cadastre-se", href="/clientes/cadastro", color=COLORS["accent"]),
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


def welcome_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _brand(),
            rx.box(
                rx.vstack(
                    rx.heading("Boas-vindas", size="7", color=COLORS["text"]),
                    rx.text(State.message, color=COLORS["error"], role="alert"),
                    rx.cond(
                        State.user_role != "",
                        rx.vstack(
                            rx.text(f"Olá, {State.user_name}.", size="4"),
                            rx.text(
                                rx.cond(
                                    State.user_role == "admin",
                                    "Sua conta administradora está conectada.",
                                    "Sua conta de cliente está conectada.",
                                ),
                                color=COLORS["muted"],
                            ),
                            rx.cond(
                                State.company_identifier != "",
                                rx.link(
                                    f"/agendar/{State.company_identifier}",
                                    href=f"/agendar/{State.company_identifier}",
                                    color=COLORS["accent"],
                                ),
                                rx.text(
                                    "Os recursos de agendamento e gestão estarão disponíveis em breve.",
                                    color=COLORS["muted"],
                                ),
                            ),
                            rx.button(
                                "Sair",
                                on_click=State.logout,
                                variant="outline",
                                width="100%",
                                height="52px",
                                color=COLORS["accent"],
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.link("Entrar como cliente", href="/clientes/login"),
                            rx.link(
                                "Entrar como administradora",
                                href="/admin/login",
                            ),
                            align="stretch",
                            spacing="3",
                            width="100%",
                        ),
                    ),
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
            aria_described_by=error_id,
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


def admin_services_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                _brand(),
                rx.button(
                    "Sair",
                    on_click=State.logout,
                    variant="outline",
                    height="44px",
                    color=COLORS["accent"],
                    border_color=COLORS["border"],
                ),
                justify="between",
                align="center",
                width="100%",
                wrap="wrap",
                spacing="3",
            ),
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
                    service["duration_display"],
                    color=COLORS["muted"],
                    size="2",
                ),
                align="start",
                spacing="2",
                flex="1",
            ),
            rx.text(
                service["price_display"],
                color=COLORS["text"],
                weight="bold",
                size="4",
                white_space="nowrap",
            ),
            direction={"initial": "column", "sm": "row"},
            align={"initial": "start", "sm": "center"},
            justify="between",
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding={"initial": "16px", "sm": "20px"},
        border=f"1px solid {COLORS['border']}",
        border_radius="16px",
        background_color=COLORS["surface"],
        box_shadow=SHADOWS["tile"],
    )


def public_company_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.link(
                _brand(),
                href="/",
                underline="none",
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
                            ),
                            rx.text(
                                f"/agendar/{State.public_company_identifier}",
                                color=COLORS["muted"],
                            ),
                            rx.text(
                                "Agende seu horário em poucos toques. "
                                "A disponibilidade de agendamentos estará disponível em breve.",
                                color=COLORS["muted"],
                            ),
                            rx.divider(color=COLORS["border"]),
                            rx.heading(
                                "Serviços",
                                size="5",
                                color=COLORS["text"],
                            ),
                            rx.cond(
                                State.public_services_loading,
                                rx.text(
                                    "Carregando serviços...",
                                    color=COLORS["muted"],
                                ),
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
                style=CARD_STYLE,
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
    on_load=State.clear_message,
)
app.add_page(
    client_login_page,
    route="/clientes/login",
    title="Entrar como cliente",
    on_load=State.clear_message,
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
    admin_services_page,
    route="/admin/servicos",
    title="Serviços da empresa",
    on_load=State.load_admin_services,
)
app.add_page(
    welcome_page,
    route="/boas-vindas",
    title="Boas-vindas",
    on_load=State.load_welcome,
)
app.add_page(
    public_company_page,
    route="/agendar/[identificador]",
    title="Página pública da empresa",
    on_load=State.load_public_company,
)
