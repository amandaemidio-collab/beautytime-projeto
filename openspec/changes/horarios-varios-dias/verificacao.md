# Verificação — horários em vários dias

## 1.1 a 1.3 — XanoScript

- Documentação consultada no Xano Developer MCP: funções, `int[]` em `input`, `precondition`, `db.transaction` e os filtros `count`, `unique`, `filter` e `to_text`.
- Validados pelo MCP (`xano_validate_xanoscript`): `function/agendamento/find_hours_overlap.xs`, `hours_POST.xs`, `hours/hour_id_PATCH.xs` e `hours/bulk_POST.xs`.

## 1.4 — Publicação e chamadas HTTP

- Dry-run com somente os 4 arquivos da change: 1 função e 1 rota criadas, 2 rotas alteradas, nada removido. Push feito em 25/10/2026 após confirmação da responsável pelo projeto.
- O push parcial exibiu avisos de tabelas e funções “inexistentes” (as referências não estavam no push). Conferido em seguida: novo dry-run dos mesmos arquivos retorna “No changes to push”, e todas as chamadas abaixo funcionaram.

Chamadas HTTP reais em 25/10/2026, com dados fictícios (empresas `hrs-a-ddacac` e `hrs-b-ddacac`, profissional 33, um profissional inativo e uma cliente), respeitando no máximo 8 chamadas a cada 20 segundos:

| Verificação | Resultado |
|---|---|
| Vários dias: seg/qua/sex 09:00–12:00 cria 3 períodos | ok |
| Todos os dias: 13:00–14:00 cria 7 períodos | ok |
| Um único dia pela rota nova | ok |
| Lista vazia → `days_of_week_invalid`; dia 0 e dia 8 → `day_of_week_invalid`; dia repetido → `days_of_week_repeated` | ok |
| Início igual ou posterior ao término → `hours_interval_invalid` | ok |
| Conflito em um dos dias (ter/qua/qui, conflito na quarta) → `hours_overlap:3` | ok |
| Tudo ou nada: após as recusas, a lista do profissional continua igual (nada criado em ter/qui) | ok |
| Vários dias encostando em períodos existentes (12:00–13:00 entre 09:00–12:00 e 13:00–14:00) é aceito | ok |
| Cadastro individual sobreposto → `hours_overlap:5` | ok |
| Cadastro individual encostando é aceito | ok |
| Edição que passa a sobrepor → `hours_overlap:1` | ok |
| Edição mantendo o próprio intervalo é aceita (o período não conflita consigo) | ok |
| Edição que estende sem sobrepor é aceita | ok |
| Edição que muda o dia para um com sobreposição → `hours_overlap:3` | ok |
| Sem sessão → 401; cliente → 403; administradora de outra empresa → 404; profissional inativo → 404 | ok |
| Nenhum período criado pelas tentativas não autorizadas | ok |

## 1.5 — Documentação

- `docs/domain-model.md` (Horário de atendimento, regras estruturais): períodos do mesmo profissional no mesmo dia não se sobrepõem, encostar é permitido, e o mesmo período pode ser cadastrado em vários dias de uma vez, tudo ou nada. Corresponde ao delta de `professional-hours`.

## 2.1 / 2.2 — Frontend: checagens automáticas (antes da verificação manual)

- `reflex compile --dry` numa cópia isolada do app: 44 páginas, sem erro. A tela `/admin/horarios` renderiza.
- Lógica de `submit_hour` executada em Python contra a API real, com a administradora fictícia `hrs-a-ddacac`:

| Verificação | Resultado |
|---|---|
| Salvar sem dia marcado: “Marque ao menos um dia da semana.” e nenhuma chamada à API | ok |
| Sábado e domingo 18:00–19:00 numa única requisição: “Período cadastrado em 2 dias.” e formulário limpo | ok |
| Conflito no sábado: “Sábado já tem um período que se sobrepõe a este horário. Nenhum período foi cadastrado.”, mantendo dias e horários no formulário | ok |
| Um único dia: “Período cadastrado com sucesso.” | ok |
| Tradução de `hours_overlap:<dia>` para edição: nome do dia, sem a frase de cadastro em vários dias (testada só na função de mensagem; a edição real fica para a verificação manual) | ok |

A interação na tela (caixas de marcação, “Todos os dias”, edição, remoção e layout no celular) depende da verificação manual no navegador (tarefas 2.2 e 3.1).

## 2.2 / 3.1 — Verificação manual no navegador

Feita pela responsável pelo projeto em 25/10/2026, em desktop e celular, em `/admin/horarios`. Todos os cenários passaram:

| Verificação | Resultado |
|---|---|
| Sete caixas de dia e “Todos os dias” marcando e desmarcando todas; 2 colunas no celular, sem rolagem horizontal | ok |
| Vários dias (seg a sex 09:00–18:00): “Período cadastrado em 5 dias.” e cinco períodos na lista | ok |
| Grupos com horários diferentes (sábado 09:00–13:00 junto dos dias úteis) | ok |
| Conflito em um dos dias: mensagem com o dia, nenhum período criado, formulário mantido | ok |
| Período que só encosta em outro é aceito | ok |
| Salvar sem dia: “Marque ao menos um dia da semana.” | ok |
| Edição com escolha de um único dia; conflito na edição com o nome do dia; salvar sem mudança funciona | ok |
| Remoção apaga somente o período escolhido | ok |
| Dias e horários aparecem na página pública de agendamento; login de administradora e demais telas funcionando | ok |
