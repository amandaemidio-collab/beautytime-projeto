# client-appointments Specification

## Purpose
Permite que clientes concluam reservas pelo link do salão, acompanhem os próprios agendamentos em uma área autenticada e cancelem reservas conforme a política informativa do BeautyTime.

## Requirements

### Requirement: Fluxo público guia a cliente até a confirmação
O sistema SHALL conduzir a cliente em `/agendar/{identificador}` pela escolha de serviço, profissional ou “sem preferência”, dia, horário e confirmação da reserva.

#### Scenario: Selecionar serviço, profissional, dia e horário
- **WHEN** a cliente avança pelo fluxo de uma empresa válida
- **THEN** a interface apresenta cada escolha em sequência e permite confirmar somente após selecionar um horário disponível

#### Scenario: Confirmação bem-sucedida
- **WHEN** o backend confirma a criação do agendamento
- **THEN** a interface apresenta resumo com empresa, serviço, profissional, início, duração e preço registrados na reserva, junto à política de cancelamento

#### Scenario: Reserva rejeitada pelo backend
- **WHEN** a confirmação falha por indisponibilidade ou por outra validação do backend
- **THEN** a interface informa que a reserva não foi concluída e permite rever os horários sem apresentar confirmação de sucesso

### Requirement: Autenticação preserva as escolhas do fluxo público
O sistema SHALL exigir login ou cadastro de cliente antes de confirmar uma reserva e SHALL retornar a cliente autenticada ao fluxo da mesma empresa sem perder serviço, profissional, dia e horário já selecionados.

#### Scenario: Cliente sem sessão segue para login
- **WHEN** uma pessoa sem sessão seleciona o serviço, profissional, dia e horário e escolhe entrar na conta
- **THEN** após autenticar-se como cliente, retorna ao fluxo da mesma empresa com as escolhas preservadas

#### Scenario: Nova cliente se cadastra durante o fluxo
- **WHEN** uma pessoa sem conta seleciona o serviço, profissional, dia e horário e conclui cadastro de cliente
- **THEN** retorna ao fluxo da mesma empresa com as escolhas preservadas e pode confirmar a reserva

#### Scenario: Autenticação incompatível ou falha
- **WHEN** a pessoa cancela ou falha no login/cadastro, ou tenta autenticar uma conta administrativa como cliente
- **THEN** não é criada reserva e nenhuma escolha é apresentada como confirmada

### Requirement: Cliente consulta seus agendamentos próximos e passados
O sistema SHALL disponibilizar à cliente autenticada uma área que separe seus agendamentos por início futuro ou passado e SHALL mostrar somente registros vinculados à identidade da sessão, inclusive entre empresas diferentes.

#### Scenario: Cliente consulta agendamentos de mais de uma empresa
- **WHEN** a cliente autenticada abre sua área
- **THEN** vê seus agendamentos próximos e passados com os dados registrados na reserva, agrupados conforme o horário de início

#### Scenario: Cliente sem agendamentos
- **WHEN** a cliente autenticada ainda não possui agendamentos
- **THEN** a área apresenta estado vazio sem dados de outra cliente

#### Scenario: Cliente tenta consultar agendamento de outra pessoa
- **WHEN** uma cliente tenta acessar, por identificador ou requisição, um agendamento de outra cliente
- **THEN** o backend não revela nem retorna os dados desse agendamento

#### Scenario: Pessoa sem sessão abre a área da cliente
- **WHEN** uma pessoa sem sessão válida acessa a área autenticada
- **THEN** a interface encaminha para login de cliente sem exibir agendamentos

### Requirement: Cliente cancela reservas dentro da política de 8 horas
O sistema SHALL permitir que a cliente cancele seus agendamentos futuros ainda agendados; o cancelamento será gratuito quando ocorrer a 8 horas ou mais do início e tardio quando ocorrer a menos de 8 horas.

#### Scenario: Cancelamento com pelo menos 8 horas de antecedência
- **WHEN** a cliente confirma o cancelamento exatamente 8 horas ou mais antes do início
- **THEN** o agendamento passa a cancelado com indicação de cancelamento tardio desativada

#### Scenario: Aviso e confirmação de cancelamento tardio
- **WHEN** a cliente inicia o cancelamento com menos de 8 horas até o início
- **THEN** antes de efetivar, a interface informa a taxa apenas informativa de R$ 5,00 e solicita confirmação

#### Scenario: Cancelamento tardio confirmado
- **WHEN** a cliente confirma o cancelamento após receber o aviso
- **THEN** o agendamento passa a cancelado e fica marcado como cancelamento tardio, sem processar pagamento

#### Scenario: Cliente desiste do cancelamento tardio
- **WHEN** a cliente fecha ou recusa a confirmação do aviso de taxa
- **THEN** o agendamento permanece agendado e sem alteração

#### Scenario: Agendamento passado ou já cancelado
- **WHEN** a cliente tenta cancelar um agendamento cujo início já passou ou cuja situação já é cancelado
- **THEN** o backend rejeita a operação e preserva os dados existentes

#### Scenario: Cliente tenta cancelar reserva de outra pessoa
- **WHEN** uma cliente envia solicitação de cancelamento para agendamento pertencente a outra cliente
- **THEN** o backend rejeita a operação sem revelar nem alterar o agendamento
