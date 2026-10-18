"""BeautyTime booking, account, and public-company pages."""

import re
from typing import Any
from urllib.parse import unquote, urlencode

import reflex as rx

from frontend.api_client import request_json
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
        return rx.redirect("/boas-vindas")

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
        return rx.redirect("/boas-vindas")

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
        self.message = ""
        return rx.redirect("/")

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
                            align="stretch",
                            spacing="4",
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
            max_width="520px",
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
