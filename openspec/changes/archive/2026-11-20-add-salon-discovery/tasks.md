# Tasks

## 1. Backend - Descoberta pública (Xano)

- [x] 1.1 Criar `GET /public/accounts` sem autenticação, com parâmetros opcionais `search` e `service`, mantendo apenas salões que aceitam reservas e projetando explicitamente os campos públicos permitidos; verificar busca sem diferenciar caixa, filtro por serviço ativo, filtros combinados, resultado vazio e ausência de campos internos na resposta.
- [x] 1.2 Validar os arquivos XanoScript novos pelo Xano Developer MCP e corrigir erros; confirmar que nenhum endpoint `/platform` ou tabela foi alterado e executar `xano workspace push --dry-run` para revisar o escopo, sem fazer push real sem confirmação do usuário.

## 2. Frontend - Busca, filtros e cards (Reflex)

- [x] 2.1 Atualizar o carregamento de `/saloes` para consultar `public/accounts` com os filtros opcionais e rejeitar respostas fora do formato esperado; verificar erro sem exibir resultados parciais e estado sem resultados.
- [x] 2.2 Adicionar busca por nome e filtro por serviço à tela `/saloes` e mostrar cards com nome, localização e serviços ativos; reutilizar `formatting.py` para exibir `price_cents` em reais e verificar que `4500` aparece como `R$ 45,00`.
- [x] 2.3 Fazer o botão “Agendar” abrir `/agendar/{public_identifier}` e adicionar “Encontrar salões” na página inicial e na área da cliente; verificar os três caminhos sem alterar o fluxo de agendamento ou as páginas `/admin` e `/platform`.

## 3. Verificação integrada

- [x] 3.1 Compilar/importar o app Reflex e testar no navegador, sem login e com sessão de cliente: busca, filtro individual e combinado, cards e serviços, estado vazio, links da página inicial e da área da cliente, e navegação de agendamento; confirmar que `/admin` e `/platform` continuam intactos e validar a change em modo estrito.

## Workflow follow-up

- Executar push real no Xano somente após apresentar o dry-run e obter confirmação específica do usuário.
