# Spec Delta

## MODIFIED Requirements

### Requirement: Cliente e administrador entram pelo fluxo correspondente
O sistema SHALL autenticar clientes e administradores com e-mail e senha e SHALL disponibilizar, após autenticação bem-sucedida, a identidade e o tipo da conta sem expor a senha ou seu hash.

#### Scenario: Login válido
- **WHEN** uma conta envia e-mail e senha corretos pelo fluxo correspondente ao seu tipo
- **THEN** o sistema autentica a conta e retorna uma sessão utilizável com sua identidade e tipo

#### Scenario: Boas-vindas após login
- **WHEN** uma cliente conclui o login ou cadastro com sucesso
- **THEN** a interface a leva a uma página simples de boas-vindas, sem funcionalidades de agendamento

#### Scenario: Administradora entra na área de serviços
- **WHEN** uma administradora conclui o login ou cadastro com sucesso
- **THEN** a interface a leva à área administrativa de serviços da própria empresa

#### Scenario: Credenciais inválidas
- **WHEN** uma conta envia e-mail inexistente, senha incorreta ou credenciais de tipo incompatível
- **THEN** o sistema rejeita a autenticação sem emitir uma sessão válida
