# Proposta

## Por quê

O BeautyTime já permite cadastrar serviços e profissionais, mas ainda não oferece os horários semanais, a consulta de disponibilidade nem a reserva, consulta e cancelamento de agendamentos. Completar esse fluxo agora permite que clientes agendem pelo link do salão e que a administradora acompanhe a agenda, mantendo as regras de negócio e o isolamento no backend.

## O que muda

- Permitir que a administradora configure um ou mais períodos semanais de atendimento por profissional e consulte, edite e remova esses períodos da própria empresa.
- Calcular disponibilidade no backend em intervalos de 15 minutos, no fuso `America/Sao_Paulo`, considerando serviço, períodos de atendimento, antecedência mínima de 1 hora, limite máximo de 30 dias e conflitos com agendamentos ativos.
- Completar `/agendar/{identificador}` com seleção de serviço, profissional ou “sem preferência”, dia e horário; preservar as escolhas durante login ou cadastro de cliente; confirmar a reserva e exibir resumo e política de cancelamento.
- Revalidar no backend a empresa, serviço, profissional, período e conflito no momento da criação. Na opção “sem preferência”, atribuir um profissional ativo, vinculado ao serviço ativo e livre no horário.
- Persistir no agendamento os dados do serviço no momento da reserva (nome, duração e preço), além do horário, cliente, profissional, empresa, situação e indicação de cancelamento tardio.
- Substituir a página de boas-vindas da cliente por sua área de agendamentos, separando próximos e passados e limitando consultas e cancelamentos aos agendamentos da própria cliente.
- Permitir cancelamento pela cliente sem custo até 8 horas antes do início; após esse limite, apresentar aviso da taxa informativa de R$ 5,00 antes da confirmação e registrar cancelamento tardio. Não processar pagamentos nem permitir cancelamento de agendamentos passados.
- Disponibilizar no painel administrativo as áreas Horários e Agenda. A Agenda exibirá por dia os agendamentos da própria empresa, com filtro por profissional, cliente, serviço, horário, situação e indicação de cancelamento tardio; será somente para visualização.
- Atualizar `docs/domain-model.md`: a descrição atual inclui “concluído”, em conflito com esta decisão, que limita as situações do agendamento a “agendado” e “cancelado”.
- Verificar os caminhos principais, as regras críticas e o isolamento com chamadas HTTP e navegação manual em desktop e celular, sem criar infraestrutura de testes automatizados.

### Fora do escopo

- Lista pública de salões parceiros, notificações, pagamentos, reagendamento e cancelamento pela administradora.
- Exceções de feriados e férias, conclusão do atendimento ou uma situação “concluído”.
- Edição de disponibilidade por datas específicas, além dos períodos semanais recorrentes.
- Alterações não relacionadas às áreas de agendamento, horários e agenda.

## Capabilities

### Novas capabilities

- `professional-hours`: períodos semanais de atendimento configurados por profissional.
- `appointment-scheduling`: consulta de dias e horários disponíveis e criação de agendamentos com revalidação no backend.
- `client-appointments`: área da cliente, continuidade do fluxo após autenticação, resumo da reserva e cancelamento com regra de 8 horas.
- `admin-appointments`: consulta da agenda diária da empresa com filtro por profissional e indicação de cancelamento tardio.

### Capabilities modificadas

- `identity`: após login ou cadastro, encaminhar a cliente para sua área de agendamentos, mantendo o destino administrativo existente.
- `admin-dashboard`: tornar Horários e Agenda áreas disponíveis, removendo o rótulo “Em breve” e encaminhando para as telas correspondentes.

## Impacto

- **Backend Xano:** novas estruturas e endpoints para períodos semanais, disponibilidade, criação e gestão de agendamentos. Toda autorização, associação à empresa e revalidação de conflito ficará no backend; clientes consultarão e cancelarão somente os próprios registros e administradoras verão somente dados da empresa da sessão.
- **Frontend Reflex:** evolução do módulo atual para as telas administrativas de Horários e Agenda, fluxo público de agendamento e área autenticada da cliente. O fluxo deve conservar as escolhas ao redirecionar para login/cadastro e voltar à empresa selecionada.
- **Modelo de dados:** horários ligados a profissionais; agendamentos ligados à empresa, cliente, profissional e serviço, com dados de serviço copiados no momento da reserva e situações limitadas a agendado/cancelado.
- **Dependências e publicação:** nenhuma nova tecnologia ou infraestrutura de testes. Na implementação, consultar e validar XanoScript com o Xano Developer MCP; executar `xano workspace push --dry-run` e solicitar confirmação explícita antes de qualquer publicação real.
