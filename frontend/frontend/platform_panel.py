"""Private Reflex pages for platform administrators."""

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import reflex as rx

from frontend.api_client import request_json, request_json_list
from frontend.api_config import api_url
from frontend.formatting import price_label
from frontend.theme import (
    BADGE_STYLES,
    BUTTON_STYLES,
    CARD_DEFAULT_PADDING,
    COLORS,
    FORM_FIELD_STYLE,
    FONT_FAMILY,
    MAX_WIDTHS,
    METRIC_CARD_STYLE,
    MENU_STYLE,
    PAGE_STYLE,
    PAGE_SECTION_GAP,
    PANEL_STYLE,
    SHADOWS,
    brand,
    empty_state,
    error_callout,
    field_label,
    loading_state,
    status_badge,
)

SAO_PAULO = timezone(timedelta(hours=-3), "America/Sao_Paulo")


def _api_message(status: int, data: dict[str, object] | list[object]) -> str:
    if isinstance(data, dict):
        message = str(data.get("message", "")).lower()
        if "invalid credentials" in message:
            return "E-mail ou senha inválidos para o acesso à plataforma."
        if status == 0:
            return str(data.get("message", "Não foi possível conectar à API."))
    if status == 404:
        return "Salão não encontrado."
    return f"Não foi possível concluir a solicitação (HTTP {status})."


def _field(
    label: str,
    name: str,
    *,
    input_type: str = "text",
    placeholder: str = "",
    required: bool = True,
    default_value: Any = None,
) -> rx.Component:
    return rx.vstack(
        field_label(label),
        rx.input(
            name=name,
            type=input_type,
            placeholder=placeholder,
            required=required,
            default_value=default_value,
            width="100%",
            size="3",
            style=FORM_FIELD_STYLE,
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _datetime_label(value: object) -> str:
    try:
        if isinstance(value, (int, float)):
            timestamp = value / 1000 if abs(value) >= 100_000_000_000 else value
            return datetime.fromtimestamp(timestamp, SAO_PAULO).strftime(
                "%d/%m às %H:%M"
            )
        if isinstance(value, str):
            try:
                timestamp = float(value)
            except ValueError:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=SAO_PAULO)
                return parsed.astimezone(SAO_PAULO).strftime("%d/%m às %H:%M")
            timestamp = (
                timestamp / 1000 if abs(timestamp) >= 100_000_000_000 else timestamp
            )
            return datetime.fromtimestamp(timestamp, SAO_PAULO).strftime(
                "%d/%m às %H:%M"
            )
    except (OverflowError, OSError, TypeError, ValueError):
        return "Horário indisponível"
    return "Horário indisponível"


class PlatformState(rx.State):
    """Session, API access, and editing state for the platform-only area."""

    _auth_token: str = ""
    user_name: str = ""
    login_error: str = ""
    login_loading: bool = False

    search: str = ""
    service_filter: str = ""
    accounts: list[dict[str, Any]] = []
    accounts_loading: bool = False
    accounts_error: str = ""

    account_id: int = 0
    account: dict[str, Any] = {}
    services: list[dict[str, Any]] = []
    professionals: list[dict[str, Any]] = []
    dashboard: dict[str, Any] = {}
    top_services: list[dict[str, Any]] = []
    upcoming_today: list[dict[str, Any]] = []
    detail_loading: bool = False
    detail_error: str = ""
    active_tab: str = "account"
    notice: str = ""
    edit_error: str = ""

    account_editing: bool = False
    service_editing_id: int = 0
    service_editing_active: bool = False
    professional_editing_id: int = 0
    professional_editing_active: bool = False

    def _clear_session(self):
        self._auth_token = ""
        self.user_name = ""
        self.accounts = []
        self.account = {}
        self.services = []
        self.professionals = []
        self.dashboard = {}
        self.top_services = []
        self.upcoming_today = []

    def _has_platform_identity(self) -> bool:
        if not self._auth_token:
            return False
        status, identity = request_json(
            "GET",
            api_url("authentication", "auth/me"),
            token=self._auth_token,
        )
        account_id = identity.get("account_id")
        valid_account_id = account_id in (None, 0, "0", "")
        if status != 200 or identity.get("role") != "platform_admin" or not valid_account_id:
            self._clear_session()
            return False
        self.user_name = str(identity.get("name") or "")
        return True

    def _require_platform_identity(self) -> bool:
        if self._has_platform_identity():
            return True
        self.login_error = "Entre com uma conta administradora da plataforma."
        return False

    def _api_auth_failed(self, status: int) -> bool:
        if status not in (401, 403):
            return False
        self._clear_session()
        self.login_error = "Sua sessão expirou ou não tem acesso à plataforma."
        return True

    @rx.event
    def load_login(self):
        self.login_error = ""
        self.login_loading = False
        if self._auth_token and self._has_platform_identity():
            return rx.redirect("/platform")

    @rx.event
    def login(self, form_data: dict[str, Any]):
        email = str(form_data.get("email", "")).strip()
        password = str(form_data.get("password", ""))
        self.login_error = ""
        if not email or not password:
            self.login_error = "Informe seu e-mail e sua senha."
            return

        self.login_loading = True
        status, data = request_json(
            "POST",
            api_url("authentication", "auth/platform/login"),
            {"email": email, "password": password},
        )
        self.login_loading = False
        if status != 200:
            self.login_error = _api_message(status, data)
            return

        token = str(data.get("authToken", ""))
        if not token:
            self.login_error = "A API não retornou uma sessão válida."
            return
        self._auth_token = token
        if not self._has_platform_identity():
            self._clear_session()
            self.login_error = "Esta conta não tem acesso ao painel da plataforma."
            return
        return rx.redirect("/platform")

    @rx.event
    def logout(self):
        self._clear_session()
        self.login_error = ""
        return rx.redirect("/platform/login")

    def _fetch_accounts(self) -> bool:
        query = urlencode(
            {
                key: value
                for key, value in (
                    ("search", self.search.strip()),
                    ("service", self.service_filter.strip()),
                )
                if value
            }
        )
        url = api_url("platform", "platform/accounts")
        if query:
            url = f"{url}?{query}"
        status, data = request_json_list(
            "GET",
            url,
            token=self._auth_token,
        )
        if self._api_auth_failed(status):
            self.accounts = []
            self.accounts_error = self.login_error
            return False
        if status != 200 or not isinstance(data, list):
            self.accounts = []
            self.accounts_error = _api_message(status, data)
            return False
        self.accounts = [item for item in data if isinstance(item, dict)]
        self.accounts_error = ""
        return True

    @rx.event
    def load_home(self):
        self.accounts = []
        self.accounts_error = ""
        self.accounts_loading = True
        if not self._require_platform_identity():
            self.accounts_loading = False
            return rx.redirect("/platform/login")
        self._fetch_accounts()
        self.accounts_loading = False
        if not self._auth_token:
            return rx.redirect("/platform/login")

    @rx.event
    def search_accounts(self, form_data: dict[str, Any]):
        if not self._require_platform_identity():
            return rx.redirect("/platform/login")
        self.search = str(form_data.get("search", "")).strip()
        self.service_filter = str(form_data.get("service", "")).strip()
        self.accounts_loading = True
        self._fetch_accounts()
        self.accounts_loading = False
        if not self._auth_token:
            return rx.redirect("/platform/login")

    @rx.event
    def load_salon(self):
        self.account = {}
        self.services = []
        self.professionals = []
        self.dashboard = {}
        self.top_services = []
        self.upcoming_today = []
        self.detail_error = ""
        self.notice = ""
        self.edit_error = ""
        self.detail_loading = True
        if not self._require_platform_identity():
            self.detail_loading = False
            return rx.redirect("/platform/login")

        path = str(self.router.url.path).rstrip("/")
        try:
            account_id = int(path.rsplit("/", 1)[-1])
        except ValueError:
            self.detail_error = "Identificador do salão inválido."
            self.detail_loading = False
            return
        if account_id <= 0:
            self.detail_error = "Identificador do salão inválido."
            self.detail_loading = False
            return
        self.account_id = account_id

        status, details = request_json(
            "GET",
            api_url("platform", f"platform/accounts/{account_id}"),
            token=self._auth_token,
        )
        if self._api_auth_failed(status):
            self.detail_error = self.login_error
            self.detail_loading = False
            return rx.redirect("/platform/login")
        services = details.get("services")
        professionals = details.get("professionals")
        account = details.get("account")
        if (
            status != 200
            or not isinstance(account, dict)
            or not isinstance(services, list)
            or not isinstance(professionals, list)
        ):
            self.detail_error = _api_message(status, details)
            self.detail_loading = False
            return

        self.account = account
        self.services = []
        for item in services:
            if not isinstance(item, dict):
                continue
            try:
                price_cents = int(item.get("price_cents", 0))
            except (TypeError, ValueError):
                price_cents = 0
            self.services.append(
                {**item, "price_display": price_label(price_cents)}
            )
        self.professionals = [
            item for item in professionals if isinstance(item, dict)
        ]

        status, dashboard = request_json(
            "GET",
            api_url("platform", f"platform/accounts/{account_id}/dashboard"),
            token=self._auth_token,
        )
        if self._api_auth_failed(status):
            self.detail_error = self.login_error
            self.detail_loading = False
            return rx.redirect("/platform/login")
        if status != 200:
            self.detail_error = _api_message(status, dashboard)
            self.detail_loading = False
            return
        dashboard["revenue_display"] = price_label(
            int(dashboard.get("estimated_revenue_cents", 0))
        )
        try:
            cancellation_percent = float(dashboard.get("cancellation_rate", 0)) * 100
        except (TypeError, ValueError):
            cancellation_percent = 0
        dashboard["cancellation_display"] = (
            f"{cancellation_percent:.1f}".rstrip("0").rstrip(".") + "%"
        )
        top_services = dashboard.get("top_services")
        dashboard["top_services"] = (
            top_services if isinstance(top_services, list) else []
        )
        upcoming = dashboard.get("upcoming_today")
        dashboard["upcoming_today"] = [
            {**item, "time_display": _datetime_label(item.get("starts_at"))}
            for item in upcoming
            if isinstance(item, dict)
        ] if isinstance(upcoming, list) else []
        self.top_services = [
            item for item in dashboard["top_services"] if isinstance(item, dict)
        ]
        self.upcoming_today = dashboard["upcoming_today"]
        self.dashboard = dashboard
        self.active_tab = "account"
        self.detail_loading = False

    @rx.event
    def select_tab(self, tab: str):
        if tab in ("account", "services", "professionals"):
            self.active_tab = tab

    @rx.event
    def begin_account_edit(self):
        self.account_editing = True
        self.notice = ""
        self.edit_error = ""

    @rx.event
    def cancel_edit(self):
        self.account_editing = False
        self.service_editing_id = 0
        self.professional_editing_id = 0
        self.notice = ""
        self.edit_error = ""

    @rx.event
    def save_account(self, form_data: dict[str, Any]):
        if not self._require_platform_identity():
            return rx.redirect("/platform/login")
        name = str(form_data.get("name", "")).strip()
        if not name:
            self.edit_error = "O nome do salão não pode ficar vazio."
            return
        payload = {
            "name": name,
            "description": str(form_data.get("description", "")).strip(),
            "location": str(form_data.get("location", "")).strip(),
        }
        status, data = request_json(
            "PATCH",
            api_url("platform", f"platform/accounts/{self.account_id}"),
            payload,
            self._auth_token,
        )
        if self._api_auth_failed(status):
            return rx.redirect("/platform/login")
        if status != 200:
            self.edit_error = _api_message(status, data)
            return
        self.account = {**self.account, **data}
        self.account_editing = False
        self.edit_error = ""
        self.notice = "Dados do salão atualizados."

    @rx.event
    def begin_service_edit(
        self,
        service_id: int,
        is_active: bool,
    ):
        self.service_editing_id = service_id
        self.service_editing_active = is_active
        self.professional_editing_id = 0
        self.account_editing = False
        self.edit_error = ""
        self.notice = ""

    @rx.event
    def set_service_active(self, is_active: bool):
        self.service_editing_active = is_active

    @rx.event
    def save_service(self, form_data: dict[str, Any]):
        if not self._require_platform_identity():
            return rx.redirect("/platform/login")
        try:
            duration = int(form_data.get("duration_minutes", ""))
            price_cents = int(form_data.get("price_cents", ""))
        except (TypeError, ValueError):
            self.edit_error = "Informe duração e preço usando números inteiros."
            return
        payload = {
            "name": str(form_data.get("name", "")).strip(),
            "duration_minutes": duration,
            "price_cents": price_cents,
            "is_active": self.service_editing_active,
        }
        status, data = request_json(
            "PATCH",
            api_url("platform", f"platform/services/{self.service_editing_id}"),
            payload,
            self._auth_token,
        )
        if self._api_auth_failed(status):
            return rx.redirect("/platform/login")
        if status != 200:
            self.edit_error = _api_message(status, data)
            return
        try:
            price_display = price_label(int(data.get("price_cents", 0)))
        except (TypeError, ValueError):
            price_display = price_label(0)
        self.services = [
            {**item, **data, "price_display": price_display}
            if item.get("id") == self.service_editing_id
            else item
            for item in self.services
        ]
        self.service_editing_id = 0
        self.edit_error = ""
        self.notice = "Serviço atualizado."

    @rx.event
    def begin_professional_edit(
        self,
        professional_id: int,
        is_active: bool,
    ):
        self.professional_editing_id = professional_id
        self.professional_editing_active = is_active
        self.service_editing_id = 0
        self.account_editing = False
        self.edit_error = ""
        self.notice = ""

    @rx.event
    def set_professional_active(self, is_active: bool):
        self.professional_editing_active = is_active

    @rx.event
    def save_professional(self, form_data: dict[str, Any]):
        if not self._require_platform_identity():
            return rx.redirect("/platform/login")
        payload = {
            "name": str(form_data.get("name", "")).strip(),
            "is_active": self.professional_editing_active,
        }
        status, data = request_json(
            "PATCH",
            api_url(
                "platform",
                f"platform/professionals/{self.professional_editing_id}",
            ),
            payload,
            self._auth_token,
        )
        if self._api_auth_failed(status):
            return rx.redirect("/platform/login")
        if status != 200:
            self.edit_error = _api_message(status, data)
            return
        self.professionals = [
            {**item, **data}
            if item.get("id") == self.professional_editing_id
            else item
            for item in self.professionals
        ]
        self.professional_editing_id = 0
        self.edit_error = ""
        self.notice = "Profissional atualizado."


def _header() -> rx.Component:
    active = PlatformState.router.url.path != "/platform/login"
    logo = rx.link(
        rx.hstack(
            brand(),
            rx.text(
                "· Plataforma",
                font_family=FONT_FAMILY,
                font_size="14px",
                color=COLORS["muted"],
            ),
            align="baseline",
            spacing="2",
        ),
        href="/platform",
        underline="none",
    )
    menu_link = rx.link(
        "Salões",
        href="/platform",
        color=rx.cond(active, COLORS["primary_foreground"], COLORS["muted"]),
        font_size="14px",
        font_weight="600",
        background_color=rx.cond(active, COLORS["accent"], "transparent"),
        padding="8px 16px",
        border_radius="999px",
        min_height="40px",
        display="flex",
        align_items="center",
        white_space="nowrap",
        aria_current=rx.cond(active, "page", "false"),
    )
    return rx.vstack(
        rx.flex(
            logo,
            rx.button(
                "Sair",
                on_click=PlatformState.logout,
                style=BUTTON_STYLES["ghost"],
                min_height="40px",
            ),
            align="center",
            justify="between",
            width="100%",
        ),
        rx.flex(
            menu_link,
            rx.text(PlatformState.user_name, color=COLORS["muted"]),
            align="center",
            justify="between",
            width="100%",
            style=MENU_STYLE,
        ),
        align="stretch",
        spacing="3",
        width="100%",
    )


def platform_login_page() -> rx.Component:
    return rx.box(
        rx.form(
            rx.vstack(
                rx.heading(
                    "Acesso da plataforma",
                    size="6",
                    color=COLORS["text"],
                ),
                rx.text(
                    "Entre com a conta administradora da plataforma.",
                    color=COLORS["muted"],
                ),
                _field("E-mail", "email", input_type="email"),
                _field("Senha", "password", input_type="password"),
                rx.cond(
                    PlatformState.login_error != "",
                    error_callout(PlatformState.login_error),
                    rx.fragment(),
                ),
                rx.button(
                    rx.cond(PlatformState.login_loading, "Entrando...", "Entrar"),
                    type="submit",
                    disabled=PlatformState.login_loading,
                    width="100%",
                    height="48px",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            on_submit=PlatformState.login,
            reset_on_submit=False,
            width="100%",
            max_width=MAX_WIDTHS["platform_login"],
            padding=CARD_DEFAULT_PADDING,
            border=f"1px solid {COLORS['border']}",
            border_radius="28px",
            background_color=COLORS["surface"],
            box_shadow=SHADOWS["card"],
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _account_card(account: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.link(
        rx.vstack(
            rx.flex(
                rx.heading(account["name"], size="4", color=COLORS["text"]),
                rx.text(
                    account["location"],
                    color=COLORS["muted"],
                    size="2",
                ),
                direction={"initial": "column", "sm": "row"},
                justify="between",
                align={"initial": "start", "sm": "center"},
                width="100%",
                spacing="2",
            ),
            rx.flex(
                rx.badge(
                    f"Serviços: {account['service_count']}",
                    style=BADGE_STYLES["outline"],
                ),
                rx.badge(
                    f"Profissionais: {account['professional_count']}",
                    style=BADGE_STYLES["outline"],
                ),
                rx.badge(
                    f"Agendamentos: {account['appointment_count']}",
                    style=BADGE_STYLES["outline"],
                ),
                wrap="wrap",
                spacing="2",
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        href=f"/platform/saloes/{account['id']}",
        underline="none",
        style=PANEL_STYLE,
        width="100%",
    )


def platform_home_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _header(),
            rx.heading("Salões", size="7", color=COLORS["text"]),
            rx.form(
                rx.grid(
                    _field(
                        "Buscar por nome",
                        "search",
                        placeholder="Nome do salão",
                        default_value=PlatformState.search,
                        required=False,
                    ),
                    _field(
                        "Filtrar por serviço ativo",
                        "service",
                        placeholder="Nome do serviço",
                        default_value=PlatformState.service_filter,
                        required=False,
                    ),
                    columns={"initial": "1", "md": "2"},
                    spacing="4",
                    width="100%",
                ),
                rx.button(
                    "Buscar",
                    type="submit",
                    height="48px",
                    style=BUTTON_STYLES["primary"],
                ),
                on_submit=PlatformState.search_accounts,
                reset_on_submit=False,
                style=PANEL_STYLE,
            ),
            rx.cond(
                PlatformState.accounts_loading,
                loading_state("Carregando salões..."),
                rx.fragment(),
            ),
            rx.cond(
                PlatformState.accounts_error != "",
                rx.text(
                    PlatformState.accounts_error,
                    color=COLORS["error"],
                    role="alert",
                ),
                rx.fragment(),
            ),
            rx.cond(
                PlatformState.accounts.length() > 0,
                rx.grid(
                    rx.foreach(PlatformState.accounts, _account_card),
                    columns={"initial": "1", "md": "2"},
                    spacing="4",
                    width="100%",
                ),
                rx.cond(
                    PlatformState.accounts_loading
                    | (PlatformState.accounts_error != ""),
                    rx.fragment(),
                    empty_state(
                        "Nenhum salão corresponde aos filtros.",
                        "Revise os termos ou tente uma busca diferente.",
                    ),
                ),
            ),
            align="stretch",
            spacing=PAGE_SECTION_GAP,
            width="100%",
            max_width=MAX_WIDTHS["platform"],
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def _metric_card(title: str, value: rx.Var[Any]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                title,
                color=COLORS["muted"],
                font_size="11px",
                font_weight="700",
                letter_spacing="0.16em",
                text_transform="uppercase",
            ),
            rx.heading(
                value,
                size="5",
                font_size="38px",
                font_weight="600",
                line_height="1",
                color=COLORS["accent"],
            ),
            align="start",
            spacing="3",
        ),
        style=METRIC_CARD_STYLE,
    )


def _account_editor() -> rx.Component:
    return rx.form(
        rx.vstack(
            _field("Nome", "name", default_value=PlatformState.account["name"]),
            _field(
                "Descrição",
                "description",
                required=False,
                default_value=PlatformState.account["description"],
            ),
            _field(
                "Localização",
                "location",
                required=False,
                default_value=PlatformState.account["location"],
            ),
            rx.flex(
                rx.button(
                    "Salvar",
                    type="submit",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                ),
                rx.button(
                    "Cancelar",
                    type="button",
                    on_click=PlatformState.cancel_edit,
                    style=BUTTON_STYLES["secondary"],
                ),
                spacing="3",
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        on_submit=PlatformState.save_account,
        reset_on_submit=False,
    )


def _account_tab() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.heading("Dados do salão", size="5"),
            rx.button(
                "Editar",
                on_click=PlatformState.begin_account_edit,
                style=BUTTON_STYLES["secondary"],
            ),
            justify="between",
            align="center",
        ),
        rx.cond(
            PlatformState.account_editing,
            _account_editor(),
            rx.vstack(
                rx.text(f"Nome: {PlatformState.account['name']}"),
                rx.text(
                    f"Descrição: {PlatformState.account['description']}",
                    color=COLORS["muted"],
                ),
                rx.text(f"Localização: {PlatformState.account['location']}"),
                rx.text(
                    f"Identificador público: "
                    f"{PlatformState.account['public_identifier']}",
                    color=COLORS["muted"],
                ),
                align="stretch",
                spacing="2",
                width="100%",
            ),
        ),
        align="stretch",
        spacing="4",
        style=PANEL_STYLE,
    )


def _service_editor(service: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.form(
        rx.vstack(
            _field("Nome", "name", default_value=service["name"]),
            rx.grid(
                _field(
                    "Duração (minutos)",
                    "duration_minutes",
                    input_type="number",
                    default_value=service["duration_minutes"],
                ),
                _field(
                    "Preço (centavos)",
                    "price_cents",
                    input_type="number",
                    default_value=service["price_cents"],
                ),
                columns={"initial": "1", "sm": "2"},
                spacing="3",
                width="100%",
            ),
            rx.checkbox(
                "Serviço ativo",
                checked=PlatformState.service_editing_active,
                on_change=PlatformState.set_service_active,
            ),
            rx.flex(
                rx.button(
                    "Salvar",
                    type="submit",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                ),
                rx.button(
                    "Cancelar",
                    type="button",
                    on_click=PlatformState.cancel_edit,
                    style=BUTTON_STYLES["secondary"],
                ),
                spacing="3",
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        on_submit=PlatformState.save_service,
        reset_on_submit=False,
    )


def _service_card(service: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.heading(service["name"], size="4", color=COLORS["text"]),
                status_badge(
                    rx.cond(service["is_active"], "Ativo", "Inativo"),
                    service["is_active"],
                    neutral_when_inactive=True,
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.text(
                f"Duração: {service['duration_minutes']} min",
                color=COLORS["muted"],
            ),
            rx.text(
                f"Preço: {service['price_display']}",
                weight="bold",
                color=COLORS["text"],
            ),
            rx.cond(
                PlatformState.service_editing_id == service["id"],
                _service_editor(service),
                rx.button(
                    "Editar",
                    on_click=PlatformState.begin_service_edit(
                        service["id"], service["is_active"]
                    ),
                    style=BUTTON_STYLES["secondary"],
                ),
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        style=PANEL_STYLE,
    )


def _services_tab() -> rx.Component:
    return rx.vstack(
        rx.heading("Serviços", size="5"),
        rx.cond(
            PlatformState.services.length() > 0,
            rx.grid(
                rx.foreach(PlatformState.services, _service_card),
                columns={"initial": "1", "md": "2"},
                spacing="4",
                width="100%",
            ),
            empty_state(
                "Este salão ainda não tem serviços.",
                "Cadastre os serviços pelo painel do salão.",
            ),
        ),
        align="stretch",
        spacing="4",
        style=PANEL_STYLE,
    )


def _professional_editor(
    professional: rx.Var[dict[str, Any]],
) -> rx.Component:
    return rx.form(
        rx.vstack(
            _field("Nome", "name", default_value=professional["name"]),
            rx.checkbox(
                "Profissional ativo",
                checked=PlatformState.professional_editing_active,
                on_change=PlatformState.set_professional_active,
            ),
            rx.flex(
                rx.button(
                    "Salvar",
                    type="submit",
                    background_color=COLORS["accent"],
                    color=COLORS["surface"],
                ),
                rx.button(
                    "Cancelar",
                    type="button",
                    on_click=PlatformState.cancel_edit,
                    style=BUTTON_STYLES["secondary"],
                ),
                spacing="3",
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        on_submit=PlatformState.save_professional,
        reset_on_submit=False,
    )


def _professional_card(professional: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.heading(professional["name"], size="4", color=COLORS["text"]),
                status_badge(
                    rx.cond(professional["is_active"], "Ativo", "Inativo"),
                    professional["is_active"],
                    neutral_when_inactive=True,
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.cond(
                PlatformState.professional_editing_id == professional["id"],
                _professional_editor(professional),
                rx.button(
                    "Editar",
                    on_click=PlatformState.begin_professional_edit(
                        professional["id"], professional["is_active"]
                    ),
                    style=BUTTON_STYLES["secondary"],
                ),
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        style=PANEL_STYLE,
    )


def _professionals_tab() -> rx.Component:
    return rx.vstack(
        rx.heading("Profissionais", size="5"),
        rx.cond(
            PlatformState.professionals.length() > 0,
            rx.grid(
                rx.foreach(PlatformState.professionals, _professional_card),
                columns={"initial": "1", "md": "2"},
                spacing="4",
                width="100%",
            ),
            empty_state(
                "Este salão ainda não tem profissionais.",
                "Cadastre os profissionais pelo painel do salão.",
            ),
        ),
        align="stretch",
        spacing="4",
        style=PANEL_STYLE,
    )


def _tab_button(label: str, tab: str) -> rx.Component:
    active = PlatformState.active_tab == tab
    return rx.button(
        label,
        on_click=PlatformState.select_tab(tab),
        background_color=rx.cond(active, COLORS["accent"], COLORS["secondary"]),
        color=rx.cond(
            active,
            COLORS["primary_foreground"],
            COLORS["accent"],
        ),
        border_radius="999px",
        min_height="40px",
        padding_x="16px",
    )


def _dashboard_summary() -> rx.Component:
    return rx.grid(
        _metric_card("Agendamentos hoje", PlatformState.dashboard["appointments_today"]),
        _metric_card(
            "Agendamentos na semana",
            PlatformState.dashboard["appointments_week"],
        ),
        _metric_card("Faturamento estimado", PlatformState.dashboard["revenue_display"]),
        _metric_card(
            "Taxa de cancelamento",
            PlatformState.dashboard["cancellation_display"],
        ),
        columns={"initial": "1", "sm": "2", "lg": "4"},
        spacing="4",
        width="100%",
    )


def _dashboard_details() -> rx.Component:
    return rx.grid(
        rx.box(
            rx.vstack(
                rx.heading("Serviços mais agendados na semana", size="4"),
                rx.cond(
                    PlatformState.top_services.length() > 0,
                    rx.foreach(
                        PlatformState.top_services,
                        lambda service: rx.flex(
                            rx.text(service["service_name"]),
                            rx.text(
                                rx.cond(
                                    service["appointment_count"] == 1,
                                    f"{service['appointment_count']} agendamento",
                                    f"{service['appointment_count']} agendamentos",
                                ),
                                color=COLORS["muted"],
                            ),
                            justify="between",
                            width="100%",
                        ),
                    ),
                    rx.text("Sem agendamentos nesta semana.", color=COLORS["muted"]),
                ),
                align="stretch",
                spacing="3",
            ),
            style=PANEL_STYLE,
        ),
        rx.box(
            rx.vstack(
                rx.heading("Próximos horários de hoje", size="4"),
                rx.cond(
                    PlatformState.upcoming_today.length() > 0,
                    rx.foreach(
                        PlatformState.upcoming_today,
                        lambda appointment: rx.box(
                            rx.text(appointment["time_display"], weight="bold"),
                            rx.text(appointment["service_name"]),
                            rx.text(
                                appointment["professional_name"],
                                color=COLORS["muted"],
                            ),
                            padding_y="2",
                            border_bottom=f"1px solid {COLORS['border']}",
                        ),
                    ),
                    rx.text("Não há próximos horários hoje.", color=COLORS["muted"]),
                ),
                align="stretch",
                spacing="3",
            ),
            style=PANEL_STYLE,
        ),
        columns={"initial": "1", "md": "2"},
        spacing="3",
        width="100%",
    )


def platform_salon_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            _header(),
            rx.cond(
                PlatformState.detail_loading,
                loading_state("Carregando dados do salão..."),
                rx.fragment(),
            ),
            rx.cond(
                PlatformState.detail_error != "",
                rx.box(
                    rx.heading("Não foi possível abrir o salão", size="5"),
                    rx.text(PlatformState.detail_error, color=COLORS["error"]),
                    rx.link("Voltar para salões", href="/platform"),
                    style=PANEL_STYLE,
                ),
                rx.fragment(),
            ),
            rx.cond(
                PlatformState.account.length() > 0,
                rx.vstack(
                    rx.heading(PlatformState.account["name"], size="7"),
                    _dashboard_summary(),
                    _dashboard_details(),
                    rx.cond(
                        PlatformState.notice != "",
                        rx.text(
                            PlatformState.notice,
                            color=COLORS["success"],
                            role="status",
                            aria_live="polite",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        PlatformState.edit_error != "",
                        rx.text(
                            PlatformState.edit_error,
                            color=COLORS["error"],
                            role="alert",
                        ),
                        rx.fragment(),
                    ),
                    rx.flex(
                        _tab_button("Dados do salão", "account"),
                        _tab_button("Serviços", "services"),
                        _tab_button("Profissionais", "professionals"),
                        wrap="wrap",
                        spacing="2",
                        width="100%",
                    ),
                    rx.cond(
                        PlatformState.active_tab == "account",
                        _account_tab(),
                        rx.cond(
                            PlatformState.active_tab == "services",
                            _services_tab(),
                            _professionals_tab(),
                        ),
                    ),
                    align="stretch",
                    spacing=PAGE_SECTION_GAP,
                    width="100%",
                ),
                rx.fragment(),
            ),
            align="stretch",
            spacing=PAGE_SECTION_GAP,
            width="100%",
            max_width=MAX_WIDTHS["platform"],
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )
