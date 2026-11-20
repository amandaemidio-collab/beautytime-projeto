# Tasks

## 1. Backend - Identidade

- [x] 1.1 Adicionar `platform_admin` ao enum `role` da tabela `user` em `xano/table/user.xs`, preservando `client` e `admin`, e verificar que o arquivo continua válido no validador Xano.
- [x] 1.2 Confirmar a regra de dados de que toda conta `platform_admin` usa `account_id = null`, verificando o schema e os cenários de autorização planejados.

## 2. Backend - Autorização

- [x] 2.1 Criar a função `authorize_platform_admin` no padrão de `authorize_admin`, buscando o usuário por `$auth.id`, retornando erro 403 quando o usuário não existir ou não tiver `role = "platform_admin"` e verificando que o XanoScript é válido.
- [x] 2.2 Confirmar que `authorize_admin` continua exigindo `role = "admin"` e `account_id != null`, e testar pelo menos o caso em que `platform_admin` é rejeitado.

## 3. Backend - Cadastros

- [x] 3.1 Revisar `auth/signup` e verificar que ele continua persistindo somente `role = "client"` com `account_id` nulo, sem aceitar `platform_admin` por entrada.
- [x] 3.2 Revisar `auth/admin/signup` e verificar que ele continua persistindo somente `role = "admin"` associado à empresa criada, sem oferecer ou persistir `platform_admin`.

## 4. Verificação final

- [x] 4.1 Executar validação XanoScript dos arquivos alterados e corrigir somente erros relacionados a esta change.
- [x] 4.2 Comparar os arquivos finais com os cenários das especificações e confirmar que nenhuma tabela de teste (`MOCK_DATA`, `Teste`, `teste aula`, `TESTE_MOCK_DATA`, `STATUS_CPF` ou `Unicidade`) foi alterada.
- [x] 4.3 Executar `openspec validate add-platform-admin-role --strict` e garantir que os artefatos da change passam sem erros.
