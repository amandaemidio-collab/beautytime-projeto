# Tasks

## 1. Backend - Autenticação e identidade

- [x] 1.1 Criar `POST /auth/platform/login`, seguindo o formato de `auth/admin/login`, mas aceitando somente `role = "platform_admin"` com `account_id` nulo; verificar no Xano Developer MCP que o endpoint é válido e rejeita papéis diferentes sem emitir token.
- [x] 1.2 Atualizar `auth/me` para retornar identidade `platform_admin` sem empresa e rejeitar essa identidade se houver `account_id`; validar o XanoScript e confirmar que os casos existentes de `client` e `admin` continuam válidos.

## 2. Backend - Consulta de salões

- [x] 2.1 Criar `GET /platform/accounts` protegido por `authorize_platform_admin`, com filtros opcionais `search` e `service` e contagens totais de serviços, profissionais e agendamentos; verificar resultados para filtros vazios, combinados, sem correspondência, itens inativos e agendamentos cancelados.
- [x] 2.2 Criar `GET /platform/accounts/{account_id}` protegido por `authorize_platform_admin`, retornando o salão, seus serviços e profissionais ativos e inativos; verificar que um ID inexistente não retorna dados de outro salão.
- [x] 2.3 Criar `GET /platform/accounts/{account_id}/dashboard` protegido por `authorize_platform_admin`; verificar limites de dia e semana em `America/Sao_Paulo`, contagem diária e semanal, soma de valores não cancelados, taxa de cancelamento, top 5 serviços e até cinco próximos horários.

## 3. Backend - Edição e auditoria

- [x] 3.1 Criar `PATCH /platform/accounts/{account_id}` com edição parcial de `name`, `description` e `location`; validar entrada, salon inexistente e que campos não permitidos não são alterados.
- [x] 3.2 Criar `PATCH /platform/services/{service_id}` com edição parcial de `name`, `duration_minutes`, `price_cents` e `is_active`; reutilizar as regras de validação do catálogo e verificar unicidade por salão e preservação dos dados históricos de agendamentos.
- [x] 3.3 Criar `PATCH /platform/professionals/{professional_id}` com edição parcial de `name` e `is_active`; verificar que somente os campos permitidos mudam e que profissionais inexistentes são rejeitados.
- [x] 3.4 Registrar cada PATCH bem-sucedido em `event_log` com `user_id`, `account_id`, ação e valores anteriores e novos dos campos alterados; verificar que a alteração e o log são atômicos e que o salão relacionado é obtido do registro-alvo.
- [x] 3.5 Validar todos os arquivos XanoScript novos ou alterados pelo Xano Developer MCP e corrigir erros da change; não publicar no workspace sem pedir confirmação específica depois de apresentar o dry-run.

## 4. Frontend - Login e lista da plataforma

- [x] 4.1 Configurar a API da plataforma e adicionar o login Reflex em `/platform/login`; validar o tipo retornado e a identidade com `auth/me`, sem adicionar link para esse login à navegação pública.
- [x] 4.2 Proteger `/platform`, `/platform/saloes/[account_id]` e suas ações de carregamento, redirecionando sessão ausente ou papel diferente para `/platform/login`; verificar que as páginas existentes `/admin/login` e `/admin` continuam funcionando para `admin`.
- [x] 4.3 Implementar em `/platform` a busca por nome, filtro por serviço e cards com contagens, navegando ao detalhe ao selecionar um card; verificar filtros combinados e estado sem resultados.

## 5. Frontend - Detalhe, indicadores e edição

- [x] 5.1 Implementar `/platform/saloes/[account_id]` com cards do dashboard e abas “Dados do salão”, “Serviços” e “Profissionais”; verificar carregamento e mensagens de erro para salão inexistente.
- [x] 5.2 Implementar formulários de edição para salão, serviço e profissional usando somente os campos autorizados; verificar submissão, mensagens de sucesso/erro e atualização dos dados exibidos.
- [x] 5.3 Formatar preços em reais reaproveitando o helper existente; verificar que `4500` centavos aparece como `R$ 45,00` em todos os valores monetários do painel.
- [x] 5.4 Executar a verificação de compilação/importação do app com o ambiente `.venv` e revisar manualmente os fluxos de login, filtros, navegação, edição e redirecionamento sem sessão.

## 6. Documentação e verificação integrada

- [x] 6.1 Atualizar a documentação de visão geral e domínio para descrever o papel `platform_admin`, seu acesso separado e as novas rotas, preservando a descrição das administradoras de salão.
- [x] 6.2 Comparar a implementação com todos os cenários das especificações, validar a change em modo estrito e confirmar que tabelas de teste e cadastros existentes não foram alterados.

## Workflow follow-up

- Solicitar confirmação antes de qualquer `xano workspace push`; executar `--dry-run`, apresentar o resultado e aguardar nova confirmação antes do push real.
