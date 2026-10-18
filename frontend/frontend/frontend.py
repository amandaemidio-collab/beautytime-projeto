"""BeautyTime identity and public-company pages."""

import re
from typing import Any
from urllib.parse import unquote, urlencode

import reflex as rx

from frontend.api_client import request_json
from frontend.api_config import api_url

IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PAGE_STYLE = {
    "min_height": "100vh",
    "background_color": "#f7f5f2",
    "padding": {"initial": "24px 16px", "md": "48px 24px"},
}
CARD_STYLE = {
    "width": "100%",
    "max_width": "480px",
    "padding": {"initial": "24px 20px", "md": "32px"},
    "border": "1px solid #e9e3dc",
    "border_radius": "20px",
    "background_color": "white",
    "box_shadow": "0 12px 36px rgba(47, 38, 31, 0.08)",
}


def _api_error(status: int, data: dict[str, object]) -> str:
    """Translate common Xano errors into concise Portuguese messages."""
    message = str(data.get("message", "")).lower()
    if status == 0:
        return str(data.get("message", "Não foi possível conectar à API."))
    if status == 429:
        return "Muitas tentativas em pouco tempo. Aguarde e tente novamente."
    if "identifier is already in use" in message:
        return "Este identificador já está em uso."
    if "already in use" in message:
        return "Este e-mail já está em uso."
    if "public identifier must" in message:
        return "Use de 3 a 40 caracteres: letras minúsculas, números e hífens simples."
    if "invalid credentials" in message:
        return "E-mail ou senha inválidos para este tipo de acesso."
    if status in (400, 422):
        return "Confira os dados informados e tente novamente."
    return f"Não foi possível concluir a solicitação (HTTP {status})."


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
        rx.text(label, size="2", weight="medium", color="#3f3833"),
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
                rx.heading("BeautyTime", size="6", color="#7c3f55"),
                href="/",
                underline="none",
            ),
            rx.box(
                rx.vstack(
                    rx.heading(title, size="7", color="#282321"),
                    rx.text(description, color="#706761"),
                    rx.form(
                        rx.vstack(
                            *fields,
                            rx.text(State.message, color="#a83232", size="2"),
                            rx.button(
                                submit_label,
                                type="submit",
                                width="100%",
                                size="3",
                                background_color="#7c3f55",
                                color="white",
                                _hover={"background_color": "#653247"},
                            ),
                            align="stretch",
                            spacing="4",
                            width="100%",
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
            max_width="480px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


class State(rx.State):
    """Frontend state; credentials and the Xano token remain backend-only."""

    _auth_token: str = ""

    message: str = ""
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
            self.message = (
                "Use de 3 a 40 caracteres: letras minúsculas, números "
                "e hífens simples, sem hífen no início ou no fim."
            )
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
        self.public_company_name = ""
        self.public_company_identifier = ""
        self.public_company_found = False
        self.public_company_message = ""
        if (
            not 3 <= len(identifier) <= 40
            or not IDENTIFIER_PATTERN.fullmatch(identifier)
        ):
            self.public_company_message = "Empresa não encontrada."
            return

        query = urlencode({"public_identifier": identifier})
        status, data = request_json(
            "GET",
            f"{api_url('members_accounts', 'company/public')}?{query}",
        )
        if status == 404:
            self.public_company_message = "Empresa não encontrada."
            return
        if status != 200:
            self.public_company_message = _api_error(status, data)
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
            rx.heading("BeautyTime", size="8", color="#7c3f55"),
            rx.text(
                "Identidade e empresa em um só lugar.",
                color="#706761",
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
                color="#706761",
                size="2",
                text_align="center",
            ),
            align="center",
            spacing="6",
            width="100%",
            max_width="860px",
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
            rx.heading(title, size="5", color="#282321"),
            rx.text(description, color="#706761"),
            rx.link(
                rx.button(
                    "Entrar",
                    width="100%",
                    background_color="#7c3f55",
                    color="white",
                    _hover={"background_color": "#653247"},
                ),
                href=login_route,
                width="100%",
            ),
            rx.link("Criar conta", href=signup_route, color="#7c3f55"),
            align="stretch",
            spacing="4",
            width="100%",
        ),
        flex="1",
        padding="24px",
        border="1px solid #e9e3dc",
        border_radius="20px",
        background_color="white",
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
        rx.link("Já tem conta? Entrar", href="/clientes/login", color="#7c3f55"),
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
        rx.link("Ainda não tem conta? Cadastre-se", href="/clientes/cadastro", color="#7c3f55"),
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
            _field(
                "Identificador público",
                "public_identifier",
                placeholder="meu-salao",
                min_length=3,
                max_length=40,
                pattern="[a-z0-9]+(-[a-z0-9]+)*",
            ),
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
            color="#7c3f55",
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
            color="#7c3f55",
        ),
    )


def welcome_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("BeautyTime", size="6", color="#7c3f55"),
            rx.box(
                rx.vstack(
                    rx.heading("Boas-vindas", size="7", color="#282321"),
                    rx.text(State.message, color="#a83232"),
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
                                color="#706761",
                            ),
                            rx.cond(
                                State.company_identifier != "",
                                rx.link(
                                    f"/agendar/{State.company_identifier}",
                                    href=f"/agendar/{State.company_identifier}",
                                    color="#7c3f55",
                                ),
                                rx.text(
                                    "O painel e os agendamentos estarão disponíveis em uma próxima etapa.",
                                    color="#706761",
                                ),
                            ),
                            rx.button(
                                "Sair",
                                on_click=State.logout,
                                variant="outline",
                                width="100%",
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
            max_width="480px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


def public_company_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.link(
                rx.heading("BeautyTime", size="6", color="#7c3f55"),
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
                                color="#282321",
                            ),
                            rx.text(
                                f"/agendar/{State.public_company_identifier}",
                                color="#706761",
                            ),
                            rx.text(
                                "Esta é a página pública da empresa. "
                                "Os agendamentos estarão disponíveis em uma próxima etapa.",
                                color="#706761",
                            ),
                            align="stretch",
                            spacing="4",
                        ),
                        rx.vstack(
                            rx.heading("Empresa", size="7", color="#282321"),
                            rx.text(
                                State.public_company_message,
                                color="#706761",
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
            max_width="480px",
        ),
        display="flex",
        justify_content="center",
        style=PAGE_STYLE,
    )


app = rx.App()
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
