# Proposal

## Why

O sistema precisa distinguir administradores de salões de administradores da própria plataforma. Hoje a tabela `user` aceita apenas `client` e `admin`, e `admin` está reservado às contas vinculadas a uma empresa.

Esta change cria o terceiro tipo de usuário sem alterar o significado ou o acesso do tipo `admin`, permitindo futuras áreas exclusivas da plataforma com autorização separada.

## What Changes

- Adicionar `platform_admin` ao enum `role` da tabela `user`.
- Definir como obrigatório que uma conta `platform_admin` tenha `account_id = null`.
- Criar a função `authorize_platform_admin`, que busca o usuário autenticado por `$auth.id` e permite a ação somente quando o usuário for `platform_admin`.
- Preservar `authorize_admin` como autorização exclusiva de contas `admin` vinculadas a uma empresa.
- Confirmar que os cadastros `auth/signup` e `auth/admin/signup` continuam criando somente `client` ou `admin`, respectivamente.
- Não alterar nenhuma tabela de teste.

## Capabilities

### New Capabilities

- `platform-administration`: autorização da plataforma separada da administração de salões.

### Modified Capabilities

- `identity`: ampliar o conjunto de tipos de conta, mantendo os comportamentos existentes de `client` e `admin`.

## Impact

- Tabela: `xano/table/user.xs`.
- Nova função Xano: `xano/function/.../authorize_platform_admin.xs`.
- Função existente: `xano/function/catalogo/authorize_admin.xs`, sem alteração no critério de função `admin`.
- Endpoints consultados: `xano/api/authentication/auth/signup_POST.xs` e `xano/api/authentication/auth/admin/signup_POST.xs`.
- Nenhuma alteração em frontend, regras de agendamento, isolamento entre empresas ou tabelas de teste.
