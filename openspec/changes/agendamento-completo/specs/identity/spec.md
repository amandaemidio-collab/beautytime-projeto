# Spec Delta

## MODIFIED Requirements

### Requirement: Cliente e administrador entram pelo fluxo correspondente
O sistema SHALL autenticar clientes e administradores com e-mail e senha e SHALL disponibilizar, após autenticação bem-sucedida, a identidade e o tipo da conta sem expor a senha ou seu hash. Após login ou cadastro, a interface SHALL encaminhar cada tipo de conta ao destino correspondente.

#### Scenario: Login válido
- **WHEN** uma conta envia e-mail e senha corretos pelo fluxo correspondente ao seu tipo
- **THEN** o sistema autentica a conta e retorna uma sessão utilizável com sua identidade e tipo

#### Scenario: Boas-vindas após login
- **WHEN** uma cliente ou administradora conclui o login com sucesso
- **THEN** a administradora é encaminhada ao painel inicial `/admin` e a cliente à área `/meus-agendamentos`

#### Scenario: Destino após cadastro
- **WHEN** uma cliente ou administradora conclui o cadastro com sucesso
- **THEN** a administradora é encaminhada ao painel inicial `/admin` e a cliente à área `/meus-agendamentos`

#### Scenario: Credenciais inválidas
- **WHEN** uma conta envia e-mail inexistente, senha incorreta ou credenciais de tipo incompatível
- **THEN** o sistema rejeita a autenticação sem emitir uma sessão válida
