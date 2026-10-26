# Tarefas

## 1. Backend (Xano): sobreposição e cadastro em vários dias

- [x] 1.1 Consultar no Xano Developer MCP a sintaxe de função, lista de inteiros, `unique`, `db.transaction` e o formato de erro; criar a função `Agenda/find_hours_overlap` (profissional, dia, início, término e período a ignorar opcional, com comparação estrita para aceitar períodos que se encostam). Validar o XanoScript pelo MCP.
- [x] 1.2 Adicionar a checagem de sobreposição a `hours_POST.xs` e `hour_id_PATCH.xs` (a edição ignora o próprio período), respondendo `hours_overlap:<dia>` em conflito, sem alterar as demais validações. Validar o XanoScript pelo MCP.
- [x] 1.3 Criar `POST admin/professionals/{professional_id}/hours/bulk` no grupo `Agenda`: autorização e profissional ativo da empresa da sessão, lista de 1 a 7 dias válidos e sem repetição, intervalo válido, checagem de sobreposição de todos os dias antes de gravar e criação dos períodos em `db.transaction`. Validar o XanoScript pelo MCP.
- [x] 1.4 Executar `xano workspace push --dry-run` incluindo somente os arquivos desta change, apresentar o resultado e aguardar confirmação explícita antes do push real. Após o push, conferir por HTTP, com dados fictícios e respeitando o limite de requisições: criação em três dias e em sete dias; um único dia; lista vazia, dia 0 ou 8 e dia repetido rejeitados sem criar nada; início igual ou posterior ao término; conflito em um dos dias rejeitado sem criar nenhum período e indicando o dia; períodos que se encostam aceitos; cadastro individual e edição recusando sobreposição e a edição aceitando manter o próprio intervalo; sem sessão, cliente, profissional inativo e profissional de outra empresa rejeitados. Registrar em `verificacao.md`.
- [x] 1.5 Atualizar `docs/domain-model.md` com a regra de que períodos do mesmo profissional no mesmo dia não podem se sobrepor (encostar é permitido); conferir que o documento corresponde ao delta de `professional-hours`.

## 2. Frontend (Reflex): formulário de horários

- [x] 2.1 No formulário de novo período de `/admin/horarios`, substituir a escolha de um dia por sete caixas de marcação (segunda a domingo) e o atalho "Todos os dias"; manter o `select` de um único dia na edição. Usar props do Radix ou `rx.breakpoints` para o layout responsivo. Verificar que a página compila (`reflex compile --dry`) e renderiza.
- [x] 2.2 Enviar o cadastro pela rota nova numa única requisição, com erro local quando nenhum dia estiver marcado; traduzir `hours_overlap:<dia>` para uma mensagem com o nome do dia no cadastro em vários dias, no cadastro individual e na edição; em erro, manter dias e horários marcados; em sucesso, limpar o formulário e recarregar a lista. Verificar manualmente no navegador, em celular e desktop: cadastro em vários dias, "Todos os dias" marcando e desmarcando, dois grupos de dias com horários diferentes, conflito em um dos dias com a mensagem do dia e nenhum período criado, salvar sem dia marcado, edição de um período, remoção, e ausência de rolagem horizontal.

## 3. Verificação integrada

- [x] 3.1 Percorrer manualmente no navegador, em celular e desktop, a configuração de horários de um profissional em vários dias e conferir que esses dias e horários aparecem na página pública de agendamento; confirmar que login de administradora, as demais telas administrativas e o fluxo de agendamento da cliente continuam funcionando. Registrar os resultados em `verificacao.md`, sem infraestrutura de testes automatizados.

## Workflow follow-up

- Arquivar a change após revisão e confirmação de que a implementação atende às specs.
- Verificar que o delta de `professional-hours` foi consolidado em `openspec/specs/`.
