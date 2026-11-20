# Proposal

## Why

O tipo `platform_admin` e a função `authorize_platform_admin` já existem no Xano, mas ainda não há um fluxo de login ou uma interface para a equipe da plataforma consultar e manter os salões. Um painel separado permitirá essa gestão sem misturar as permissões nem as rotas já usadas pelas administradoras de salão.

## What Changes

- Criar login de administrador da plataforma por `POST /auth/platform/login`, autenticando somente contas `platform_admin`.
- Permitir que a identidade autenticada `platform_admin` seja consultada pelo endpoint de identidade sem alterar o acesso de clientes ou administradoras de salão.
- Criar endpoints protegidos sob `/platform` para listar e consultar salões, obter indicadores, atualizar dados do salão, serviço e profissional.
- Proteger todos os endpoints `/platform` com `authorize_platform_admin`.
- Registrar em `event_log` cada alteração feita por um administrador da plataforma, com usuário, salão relacionado, ação e campos alterados.
- Criar no Reflex um login e painel privados em `/platform/login`, `/platform` e `/platform/saloes/{id}`. Essas rotas não substituirão `/admin/login` nem `/admin`, que continuam destinadas às administradoras de salão.
- Permitir pesquisa por nome e filtro por serviço, mostrar salões em cards e detalhes com indicadores e abas de dados, serviços e profissionais.
- Exibir preços armazenados em centavos no formato de reais.
- Não publicar alterações no workspace Xano sem pedir confirmação antes do push real.

## Capabilities

### New Capabilities

- `platform-admin-panel`: login, consulta, painel e manutenção administrativa da plataforma, com autorização e auditoria.

### Modified Capabilities

- `identity`: incluir a autenticação e a consulta de identidade do tipo `platform_admin`, mantendo os fluxos de cliente e administradora de salão.

## Impact

- **Xano:** endpoint de login; validação de identidade em `auth/me`; novo grupo de endpoints `/platform`; tabelas existentes `account`, `user`, `service`, `professional`, `appointment` e `event_log`.
- **Reflex:** rotas `/platform/login`, `/platform` e `/platform/saloes/[id]`; estado e chamadas à API para sessão, filtros, consulta, edição e formatação de moeda.
- **Compatibilidade:** as rotas existentes `/admin/login`, `/admin` e demais páginas de salão permanecem reservadas ao papel `admin`.
- **Auditoria:** alterações administrativas usam o `account_id` do salão alvo e registram os valores alterados em `event_log.metadata`.
- **Fora do escopo:** criação de contas `platform_admin`, alterações em tabelas de teste e publicação automática no Xano.
