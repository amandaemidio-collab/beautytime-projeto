# Design

## Context

Consulte [proposal.md](./proposal.md) para motivação e o delta em `specs/professional-hours/spec.md` para os contratos observáveis.

Estado atual relevante:

- A tabela `professional_hours` guarda `professional_id`, `day_of_week` (1 = segunda … 7 = domingo), `start_minute` e `end_minute` (minutos desde 00:00, horário local).
- `hours_POST.xs` cria um período: autoriza com `Catalogo/authorize_admin` (empresa derivada da sessão), exige profissional ativo da empresa e valida dia (1–7) e intervalo (`0 ≤ início < término ≤ 1440`). `hour_id_PATCH.xs` aplica as mesmas validações na edição. Nenhuma das duas checa sobreposição.
- A disponibilidade (`availability_GET.xs`, `available_days_GET.xs`) já tolera períodos sobrepostos, descartando inícios repetidos; ela não muda nesta change.
- No Reflex, `/admin/horarios` usa um único formulário para cadastro e edição, com `hours_day` (um dia, via `select`) e `submit_hour`, que chama `POST` ou `PATCH` conforme `editing_hour_id`. Os dias da semana estão em `WEEKDAY_OPTIONS`.
- Valores responsivos em propriedades CSS precisam usar `rx.breakpoints(...)`; dicionários simples só funcionam em props do Radix (lição da change `encontrar-saloes-e-ajustes`).

## Goals / Non-Goals

**Goals:**

- Uma única regra de sobreposição, compartilhada pelas três rotas de escrita de períodos.
- Criação em vários dias atômica do ponto de vista da administradora: ou todos os períodos são criados, ou nenhum.

**Non-Goals:**

- Garantir exclusão mútua entre duas requisições simultâneas para o mesmo profissional (cenário improvável com uma administradora por empresa; ver Riscos).
- Limpar sobreposições já existentes no banco.

## Decisions

### Função compartilhada de sobreposição

Criar a função `Agenda/find_hours_overlap` com entradas `professional_id`, `day_of_week`, `start_minute`, `end_minute` e `exclude_hour_id` opcional, que consulta `professional_hours` do profissional naquele dia e indica se existe período com `início_existente < término_novo` e `término_existente > início_novo`, ignorando `exclude_hour_id`. A comparação estrita deixa períodos que se encostam como válidos. `hours_POST.xs`, `hour_id_PATCH.xs` e a rota nova chamam essa função depois das validações atuais e antes de gravar.

**Alternativas consideradas:** repetir a condição em cada rota (duplicação que pode divergir); checar sobreposição só na rota nova (descartado pela responsável: as regras dos cadastros ficariam diferentes).

### Rota nova `POST admin/professionals/{professional_id}/hours/bulk`

No grupo `Agenda`, com entradas `days_of_week` (lista de inteiros), `start_minute` e `end_minute`. Ordem:

1. Autorizar com `Catalogo/authorize_admin` e buscar o profissional ativo da empresa da sessão (404 se não pertencer a ela), como em `hours_POST.xs`.
2. Validar a lista: ao menos 1 e no máximo 7 dias, cada um entre 1 e 7, sem repetição (`count` igual ao `count` após `unique`).
3. Validar o intervalo com a mesma regra do cadastro individual.
4. Para cada dia, em ordem crescente, chamar `Agenda/find_hours_overlap`; no primeiro conflito, interromper com erro que identifica o dia.
5. Só então, dentro de `db.transaction`, criar um registro por dia e responder a lista criada.

Como todas as checagens acontecem antes da primeira gravação, uma falha de validação não cria nada; a transação cobre falhas inesperadas durante as gravações. A sintaxe de lista de inteiros, `unique`, `db.transaction` e o formato do erro devem ser confirmados no Xano Developer MCP.

**Alternativas consideradas:** a tela chamar a rota individual uma vez por dia (até 7 chamadas, risco de limite de requisições e de criação parcial); aceitar uma lista de períodos completos com horários diferentes por dia (mais complexo e fora do pedido: grupos com horários diferentes são cadastros separados).

### Erro que identifica o dia

Em conflito, as três rotas respondem `inputerror` com uma mensagem estável que contém o código e o número do dia, no formato `hours_overlap:<dia>` (por exemplo, `hours_overlap:3`). O frontend converte o número no nome do dia com `WEEKDAY_OPTIONS` e mostra, por exemplo, "Quarta-feira já tem um período que se sobrepõe a este horário. Nenhum período foi cadastrado." Se o MCP indicar um mecanismo melhor para dados estruturados no erro (como `payload`), usar esse mecanismo mantendo o mesmo conteúdo.

### Formulário no Reflex

- Novo estado `hours_days: list[str]` para o cadastro; `hours_day` continua sendo usado só na edição.
- No cadastro, o `select` de dia é substituído por sete caixas de marcação (segunda a domingo) e uma caixa "Todos os dias", marcada quando os sete estão marcados; ao marcá-la, os sete são marcados; ao desmarcá-la, todos são desmarcados. Na edição, o `select` de um dia permanece.
- `submit_hour` passa a chamar a rota nova quando não há `editing_hour_id`, com os dias em ordem crescente; sem nenhum dia marcado, mostra erro sem chamar a API. Em erro, mantém dias e horários marcados; em sucesso, limpa o formulário e recarrega a lista, como hoje.
- As mensagens `hours_overlap:<dia>` são traduzidas também no cadastro individual e na edição.
- Layout: as caixas em grade com props do Radix (por exemplo, `columns` com `rx.breakpoints`), sem dicionários responsivos em propriedades CSS.

## Riscos / Trade-offs

- [Duas requisições simultâneas para o mesmo profissional podem passar pela checagem e gravar períodos sobrepostos] → Aceito: há uma administradora por empresa e a disponibilidade já tolera sobreposição. A checagem fica imediatamente antes da gravação.
- [Períodos já sobrepostos no banco passam a impedir edições que mantenham a sobreposição] → A mensagem indica o dia em conflito; a administradora pode remover ou ajustar o outro período. Registrado como comportamento esperado.
- [A rota individual passa a recusar casos que antes aceitava] → Mudança intencional, refletida na spec; conferir por HTTP antes e depois.

## Plano de migração

1. Consultar o Xano Developer MCP; escrever a função e a rota nova e alterar `hours_POST.xs` e `hour_id_PATCH.xs`; validar todos os arquivos pelo MCP.
2. Executar `xano workspace push --dry-run` incluindo somente os arquivos desta change, apresentar o resultado e aguardar confirmação antes do push.
3. Testar por HTTP e só então implementar o formulário no Reflex.
4. Rollback: remover a rota nova e a função e restaurar as duas rotas anteriores pelo Git; não há dados nem tabelas novas.
