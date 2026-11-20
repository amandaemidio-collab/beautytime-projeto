# Design

## Context

A tabela `user` já é a fonte de autenticação e possui um enum de tipo. O tipo `admin` representa administradoras vinculadas a uma empresa, enquanto `client` representa contas globais sem empresa.

Veja `proposal.md` para a motivação e o escopo da change.

## Goals / Non-Goals

**Goals:**

- Separar a identidade da administradora da plataforma da identidade da administradora de salão.
- Manter a regra atual de `authorize_admin` baseada em `role = "admin"` e empresa válida.
- Garantir que os cadastros públicos não possam criar `platform_admin`.

**Non-Goals:**

- Criar telas ou endpoints administrativos da plataforma.
- Criar fluxo público ou protegido para cadastrar contas `platform_admin`.
- Alterar os vínculos, permissões ou recursos das contas `client` e `admin`.
- Alterar tabelas ou dados de teste.

## Decisions

- Ampliar o enum `role` da tabela `user` com `platform_admin`.
- Considerar `platform_admin` válido somente quando `account_id` não estiver preenchido.
- Criar uma função independente `authorize_platform_admin`, seguindo o padrão de `authorize_admin`, mas verificando somente `$auth.id` e `role = "platform_admin"`.
- Não reutilizar `authorize_admin` para `platform_admin`, pois essa função continua dependendo de uma empresa válida.
- Não alterar os dados enviados pelos endpoints de cadastro: `auth/signup` continuará criando `client`; `auth/admin/signup` continuará criando `admin` com empresa.
- Não fazer alterações nas tabelas `MOCK_DATA`, `Teste` ou outras tabelas de exercício.

## Risks / Trade-offs

- **Risco: permissões inconsistentes entre enum e `account_id`** → Validar as duas condições na nova função e nos testes.
- **Risco: alteração acidental do tipo `admin`** → Manter `authorize_admin` sem mudança funcional e cobrir explicitamente a rejeição de `platform_admin`.
- **Risco: criação indevida de administrador da plataforma por cadastro público** → Cobrir ambos os endpoints de cadastro e manter seus dados de criação fixos no papel correto.

## Migration Plan

1. Ampliar o enum da tabela `user`.
2. Criar e validar `authorize_platform_admin`.
3. Revisar os dois endpoints de cadastro para confirmar que não oferecem ou persistem `platform_admin`.
4. Validar que `authorize_admin` continua rejeitando contas sem empresa, inclusive `platform_admin`.
5. Executar verificações apenas sobre os arquivos e objetos do escopo.
