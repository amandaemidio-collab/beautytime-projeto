# Verificação integrada — agendamento completo

Registro das verificações do grupo 5, feitas com chamadas HTTP reais ao workspace Xano publicado em 25/10/2026, com contas fictícias criadas pelo cadastro (empresas `studio-r4a-959816` e `studio-r4b-959816`, duas clientes).

## Dias disponíveis (`GET public/{identifier}/available_days`)

| Verificação | Resultado |
|---|---|
| Profissional com períodos só em seg/ter/sáb retorna apenas esses dias | ok |
| Reserva que ocupa o único horário do dia remove o dia da lista | ok |
| Cancelamento dessa reserva devolve o dia à lista | ok |
| Janela de hoje até +30 dias (31 dias), conferida contra a disponibilidade por dia no primeiro e no último dia | ok |
| Serviço inativo, serviço de outra empresa e identificador desconhecido → 404 | ok |
| Profissional de outra empresa → lista vazia | ok |

## 5.1 — Fluxo completo e regras críticas

| Verificação | Resultado |
|---|---|
| Reserva com profissional escolhido, situação `agendado` | ok |
| Horário reservado deixa de aparecer na disponibilidade | ok |
| Conflito surgido após a consulta é rejeitado na criação (`appointment_slot_unavailable`) | ok |
| “Sem preferência” atribui o profissional ativo ainda livre | ok |
| “Sem preferência” sem profissional livre é rejeitado | ok |
| Serviço de outra empresa → 404; profissional de outra empresa → rejeitado | ok |
| Sem sessão → 401; administradora reservando como cliente → 403 | ok |
| Snapshot: preço da reserva permanece após a edição do serviço | ok |
| Cliente vê reservas de duas empresas; outra cliente não vê nem cancela (404) | ok |
| Agenda da administradora mostra só a própria empresa, com nome da cliente | ok |
| Filtro por profissional válido; profissional de outra empresa → 404; cliente sem acesso à agenda | ok |
| Cancelamento com 8 h ou mais de antecedência (≈ 8 h 05 min) é gratuito | ok |
| Cancelamento abaixo de 8 h sem confirmação é recusado (`late_cancellation_confirmation_required`) | ok |
| Cancelamento abaixo de 8 h confirmado fica marcado como tardio, e a agenda mostra a marcação | ok |
| Reserva já cancelada não pode ser cancelada de novo; o cancelamento libera o horário | ok |

Limitação: o instante exato de 8 h não pode ser atingido por HTTP. O limite foi conferido logo acima (≈ 8 h 05 min, gratuito) e abaixo (≈ 6 h 50 min, tardio); a regra no backend é `início < agora + 8 h` → tardio.

## 5.3 — Publicação

- Pushes desta rodada, cada um com dry-run e confirmação: rota `available_days` (nova).
- `xano workspace push --dry-run` completo depois dos pushes: “No changes to push”.
- Verificações HTTP repetidas após a publicação (tabelas acima). A verificação manual no navegador (5.2) fica com a responsável pelo projeto.
