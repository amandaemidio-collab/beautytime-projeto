# Tarefas

## 1. Backend (Xano): lista pública de salões

- [ ] 1.1 Consultar no Xano Developer MCP a sintaxe de junção, valores distintos e ordenação; implementar `GET companies/public` no grupo `Members & Accounts`, sem autenticação, retornando somente `name` e `public_identifier` das empresas com serviço ativo vinculado a profissional ativo da mesma empresa, sem repetição e em ordem alfabética. Validar o XanoScript pelo MCP.
- [ ] 1.2 Executar `xano workspace push --dry-run`, apresentar o resultado e aguardar confirmação explícita antes do push real; após o push, conferir por HTTP: empresa que aceita reservas aparece uma única vez mesmo com vários serviços e profissionais; empresa com serviço ativo sem profissional ativo, e empresa com profissional ativo vinculado só a serviço inativo, não aparecem; ordem alfabética; resposta sem id, descrição, localização ou outros campos.
- [ ] 1.3 Atualizar `docs/domain-model.md` para definir que a lista pública de salões mostra as empresas que aceitam reservas (serviço ativo vinculado a profissional ativo), removendo a "situação (ativa ou inativa)" da empresa; conferir que o documento corresponde à spec `salon-directory`.

## 2. Frontend (Reflex): tela "Encontrar salões"

- [ ] 2.1 Configurar a URL da nova rota em `api_config.py`, se necessário, e criar a página pública `/saloes` com cabeçalho de marca, um painel por salão com nome e botão "Agendar" para `/agendar/{identificador}`, e estados de carregamento, vazio e erro; tratar item sem nome ou com identificador inválido como resposta inválida. Verificar manualmente no navegador, sem sessão e com sessão de cliente, em celular e desktop: lista preenchida, botão abrindo o salão certo, nome longo quebrando linha sem rolagem horizontal, e estado de erro (por exemplo, com a rede desligada).

## 3. Frontend (Reflex): atalhos na área da cliente

- [ ] 3.1 Adicionar o botão "Novo agendamento" no painel do topo de `/meus-agendamentos`, levando a `/saloes`. Verificar manualmente com cliente sem agendamentos (botão visível junto ao estado vazio) e com agendamentos, em celular e desktop.
- [ ] 3.2 Adicionar "Agendar de novo" em cada agendamento listado (próximos, passados e cancelados), levando a `/agendar/{public_identifier}` do item, com o fluxo começando na escolha do serviço. Verificar manualmente com uma cliente que tenha agendamentos em dois salões que cada botão abre o salão certo, que o botão aparece em passados e cancelados sem a opção de cancelar, e que o layout do cartão continua correto no celular.

## 4. Frontend (Reflex): ajustes da página pública de agendamento

- [ ] 4.1 Reiniciar o app Reflex e confirmar no navegador a causa do conteúdo encostado na borda e do cartão cortado em `/agendar/{identificador}`, comparando com `/meus-agendamentos` no mesmo viewport; ajustar `public_company_page` para a estrutura das telas da cliente (mesma largura máxima e margens, painel no lugar do cartão externo, contêineres sem largura mínima forçada). Verificar manualmente em celular e desktop todas as etapas (serviço, profissional, grade de dias, horários, resumo, confirmação) e a tela "Empresa não encontrada", sem rolagem horizontal nem cartão cortado.
- [ ] 4.2 Confirmar que o texto introdutório abaixo do nome da empresa convida a escolher serviço, profissional, dia e horário e que nenhuma mensagem de "em breve" aparece; ajustar o texto atual ("Agende seu horário em poucos toques.") somente se ele não atender à spec. Verificar manualmente no celular e no desktop, com o app reiniciado.

## 5. Verificação integrada

- [ ] 5.1 Percorrer manualmente no navegador, em celular e desktop: `/meus-agendamentos` → "Novo agendamento" → `/saloes` → "Agendar" → agendamento completo; e "Agendar de novo" a partir de um agendamento passado. Confirmar que login, cadastro, retomada do fluxo após autenticação, cancelamento e as telas administrativas continuam funcionando. Registrar os resultados em `verificacao.md` da change, sem infraestrutura de testes automatizados.

## Workflow follow-up

- Arquivar a change após revisão e confirmação de que a implementação atende às specs.
- Verificar que a spec `salon-directory` e o delta de `client-appointments` foram consolidados em `openspec/specs/`.
