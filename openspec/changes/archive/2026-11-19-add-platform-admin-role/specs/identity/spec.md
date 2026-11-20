# Spec Delta

## MODIFIED Requirements

### Requirement: Conta de usuário tem um único tipo
O sistema SHALL identificar cada conta como cliente, administrador de salão ou administrador da plataforma, sem permitir que a mesma conta exerça dois tipos ou troque de tipo por meio de cadastro ou login.

#### Scenario: Cadastro com e-mail usado pelo outro tipo
- **WHEN** uma pessoa tenta cadastrar uma conta do tipo cliente, administrador de salão ou administrador da plataforma com e-mail já associado a outro tipo
- **THEN** o sistema rejeita o cadastro e preserva o tipo e os vínculos existentes da conta

#### Scenario: Credenciais válidas para o tipo incorreto
- **WHEN** uma pessoa tenta entrar pelo fluxo de cliente com credenciais de administrador, ou pelo fluxo de administrador com credenciais de cliente
- **THEN** o sistema não autentica a conta nesse fluxo e não altera seu tipo

#### Scenario: Administrador da plataforma não usa cadastro público
- **WHEN** uma pessoa tenta selecionar o tipo `platform_admin` nos fluxos públicos de cadastro
- **THEN** o sistema não cria essa conta e mantém os tipos disponíveis de cada fluxo
