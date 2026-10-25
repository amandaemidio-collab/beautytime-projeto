# Tarefas

## 1. Backend de horários

- [x] 1.1 Consultar a documentação Xano Developer, definir e implementar a persistência dos períodos semanais e as operações administrativas de listar, cadastrar, editar e remover horário por profissional; validar todos os arquivos XanoScript pelo MCP e conferir por HTTP o CRUD, múltiplos períodos no mesmo dia, preservação dos demais períodos e rejeição de dia/intervalo inválido.
- [x] 1.2 Aplicar autorização administrativa derivada da sessão e isolamento por empresa em todas as operações de horários; validar por HTTP com duas empresas que sessão ausente, cliente, profissional de outra empresa e identificador de empresa forjado não revelem nem alterem horários alheios.

## 2. Backend de disponibilidade e agendamento

- [x] 2.1 Implementar disponibilidade pública por empresa, serviço, profissional opcional e datas, considerando profissionais e serviços ativos, períodos semanais, inícios nos quartos de hora do relógio em `America/Sao_Paulo`, duração inteira dentro de um único período e janela de 1 hora a 30 dias; validar XanoScript pelo MCP e conferir por HTTP limites, serviço que não cabe no período, sobreposição, cancelado que libera horário e dia sem nenhum horário livre.
- [x] 2.2 Implementar criação autenticada com revalidação de empresa, serviço, profissional, antecedência, período e conflito no backend; para “sem preferência”, selecionar profissional ativo vinculado ao serviço que continue livre. Validar XanoScript pelo MCP e conferir por HTTP reserva normal, atribuição sem preferência, ausência de profissional livre, conflito surgido após consulta, ids de outra empresa e snapshot de nome/duração/preço após alteração posterior do serviço.
- [x] 2.3 Implementar consulta e cancelamento de agendamentos da cliente autenticada, com situação `agendado`/`cancelado` e cálculo tardio no backend; validar XanoScript pelo MCP e conferir por HTTP listagem entre empresas da mesma cliente, isolamento de duas clientes, cancelamento gratuito exatamente a 8 horas, cancelamento tardio abaixo de 8 horas, recusa do cancelamento, agendamento passado e reserva já cancelada.
- [x] 2.4 Implementar consulta administrativa da agenda por dia e filtro opcional de profissional, incluindo cliente, serviço, início/término, situação e cancelamento tardio, sem operações de escrita; validar XanoScript pelo MCP e conferir por HTTP isolamento entre empresas, filtro válido e filtro por profissional de outra empresa.
- [x] 2.5 Atualizar `docs/domain-model.md` para documentar períodos semanais, dados copiados para a reserva, regra de cancelamento tardio e somente as situações agendado/cancelado; conferir que o documento não mantenha “concluído” como situação e que corresponda às specs desta change.

## 3. Telas da administradora

- [x] 3.1 Implementar a área protegida de Horários no Reflex, com seleção de profissional, períodos semanais múltiplos por dia e estados de carregamento, vazio e erro; verificar manualmente no navegador cadastro, edição e remoção, mais de um período no mesmo dia, redirecionamento de cliente/sem sessão e ausência de dados de outra empresa.
- [x] 3.2 Implementar a Agenda protegida no Reflex com seleção de dia, filtro por profissional e exibição de cliente, serviço, horário, situação e marcação tardia, sem controles de edição/cancelamento; verificar manualmente dia com e sem reservas, filtro de profissional e que administradora de outra empresa e cliente não veem dados.

## 4. Fluxo da cliente

- [x] 4.1 Completar `/agendar/{identificador}` no Reflex com escolha sequencial de serviço, profissional ou “sem preferência”, dia e horário; retomar as escolhas após login/cadastro e apresentar a confirmação somente após sucesso do backend. Verificar manualmente em desktop e celular o caminho principal, retorno com escolhas preservadas e erro ao confirmar horário que ficou ocupado.
- [x] 4.2 Substituir a página de boas-vindas pela área `/meus-agendamentos`, separando próximos e passados, exibindo o resumo da reserva e a política; apresentar aviso e confirmação da taxa informativa antes do cancelamento tardio. Verificar manualmente login/cadastro, estados vazio e preenchido, valores históricos do serviço, cancelamentos nos dois lados do limite de 8 horas, recusa e impossibilidade de cancelar agendamento passado.

## 5. Verificação integrada

- [ ] 5.1 Percorrer por chamadas HTTP reais o fluxo completo e as regras críticas com duas empresas e duas clientes: disponibilidade e conflito, reserva escolhida e “sem preferência”, revalidação na criação, snapshot do serviço, cancelamento exatamente a 8 horas e abaixo desse limite, isolamento entre empresas e entre clientes e visualização administrativa. Registrar os resultados sem adicionar infraestrutura de testes automatizados.
- [ ] 5.2 Percorrer manualmente no navegador, em viewport móvel e desktop, a configuração de horários, o agendamento público com autenticação intermediária, a confirmação/política, a área da cliente e a Agenda da administradora; confirmar estados vazios, falhas e permissões e que nenhum fluxo existente de login/cadastro ou página pública foi quebrado.
  - Na rodada de verificação final, testar o cancelamento de um agendamento criado no próprio dia, cujo horário de início já tenha passado.
- [ ] 5.3 Executar `xano workspace push --dry-run`, revisar e apresentar as alterações e aguardar confirmação explícita antes de qualquer push real; após publicação autorizada, repetir as verificações HTTP e manuais afetadas.

## Workflow follow-up

- Arquivar a change após revisão e confirmação de que a implementação atende às specs.
- Verificar que as novas specs foram consolidadas em `openspec/specs/`.
