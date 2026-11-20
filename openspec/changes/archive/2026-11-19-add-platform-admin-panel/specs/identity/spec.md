# Spec Delta

## MODIFIED Requirements

### Requirement: Contas de cliente são globais à plataforma
O sistema SHALL permitir que uma cliente mantenha uma conta única, identificada por e-mail e utilizável em todas as empresas da plataforma; contas de cliente e de administrador da plataforma nunca terão empresa associada. O vínculo com uma empresa SHALL existir somente para contas de administrador de salão e será obrigatório para elas.

#### Scenario: Cadastro de cliente
- **WHEN** uma pessoa envia nome, e-mail, telefone e senha para criar uma conta de cliente com e-mail ainda não cadastrado
- **THEN** o sistema cria uma conta do tipo cliente sem associação a empresa

#### Scenario: E-mail já cadastrado
- **WHEN** uma pessoa tenta criar uma conta de cliente com um e-mail já utilizado por qualquer tipo de conta
- **THEN** o sistema rejeita o cadastro e não cria nem altera uma conta

#### Scenario: Cliente tenta se associar a uma empresa
- **WHEN** uma conta de cliente tenta criar ou obter um vínculo com uma empresa
- **THEN** o sistema rejeita a operação e mantém a conta sem empresa associada

#### Scenario: Administrador da plataforma não possui salão
- **WHEN** uma conta tem o tipo `platform_admin`
- **THEN** a conta permanece sem associação a empresa

### Requirement: Conta de usuário tem um único tipo
O sistema SHALL identificar cada conta como cliente, administrador de salão ou administrador da plataforma, sem permitir que a mesma conta exerça dois tipos ou troque de tipo por meio de cadastro ou login.

#### Scenario: Cadastro com e-mail usado pelo outro tipo
- **WHEN** uma pessoa tenta cadastrar uma conta de cliente ou administrador de salão com e-mail já associado a outra conta
- **THEN** o sistema rejeita o cadastro e preserva o tipo e os vínculos existentes da conta

#### Scenario: Credenciais válidas para o tipo incorreto
- **WHEN** uma pessoa tenta entrar pelo fluxo de cliente com credenciais de administrador, ou pelo fluxo de administrador de salão com credenciais de cliente
- **THEN** o sistema não autentica a conta nesse fluxo e não altera seu tipo

#### Scenario: Administrador da plataforma não usa cadastro público
- **WHEN** uma pessoa tenta criar uma conta `platform_admin` pelos fluxos públicos de cliente ou administrador de salão
- **THEN** o sistema rejeita a tentativa e não cria uma conta de administrador da plataforma

## ADDED Requirements

### Requirement: Administrador da plataforma autentica e consulta identidade no fluxo próprio
O sistema SHALL autenticar `platform_admin` por um fluxo separado e SHALL retornar a identidade da sessão sem exigir associação a uma empresa.

#### Scenario: Login válido da plataforma
- **WHEN** uma conta `platform_admin` sem `account_id` informa e-mail e senha corretos no fluxo de login da plataforma
- **THEN** o sistema emite uma sessão válida e retorna o tipo `platform_admin`

#### Scenario: Login da plataforma com conta de outro tipo
- **WHEN** uma conta `client` ou `admin` tenta entrar pelo fluxo de login da plataforma
- **THEN** o sistema rejeita as credenciais e não emite sessão

#### Scenario: Consulta da identidade autenticada
- **WHEN** uma conta `platform_admin` autenticada consulta sua identidade
- **THEN** o sistema retorna sua identidade e papel `platform_admin` com `account_id` nulo

#### Scenario: Administrador da plataforma associado a salão
- **WHEN** uma identidade `platform_admin` possui `account_id` preenchido
- **THEN** o sistema rejeita a identidade como inválida
