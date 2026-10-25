# appointment-scheduling Specification

## Purpose
Permite que clientes consultem horários livres de uma empresa e reservem serviços com profissionais elegíveis, enquanto o backend mantém a agenda consistente diante de conflitos e alterações concorrentes.

## Requirements

### Requirement: Disponibilidade considera serviço, períodos e janela de agendamento
O sistema SHALL oferecer horários de início nos quartos de hora do relógio local (`:00`, `:15`, `:30`, `:45`) no fuso `America/Sao_Paulo`, somente quando a duração completa do serviço couber em um único período semanal do profissional e o início estiver entre 1 hora e 30 dias a partir do momento da consulta.

#### Scenario: Horários cabem no período de atendimento
- **WHEN** uma cliente consulta horários para um serviço ativo e um profissional ativo que o realiza
- **THEN** o sistema retorna somente inícios alinhados aos quartos de hora do relógio que respeitam a janela de antecedência e cujo serviço termina até o fim do mesmo período de atendimento

#### Scenario: Serviço não cabe antes do fim do período
- **WHEN** o serviço ultrapassaria o término do período semanal, ainda que o profissional tenha outro período mais tarde
- **THEN** o sistema não oferece aquele início

#### Scenario: Limites de antecedência
- **WHEN** a cliente consulta disponibilidade
- **THEN** o sistema não oferece inícios anteriores a 1 hora nem posteriores a 30 dias a partir do instante da consulta

#### Scenario: Dia sem horários livres
- **WHEN** nenhum profissional elegível possui horário livre em um dia dentro da janela
- **THEN** o dia é apresentado como indisponível no calendário

### Requirement: Disponibilidade exclui agendamentos ativos sobrepostos
O sistema SHALL considerar ocupado um profissional ativo quando um agendamento em situação agendado se sobrepõe ao intervalo do serviço consultado; agendamentos cancelados não ocupam horários.

#### Scenario: Horário ocupado por agendamento agendado
- **WHEN** um horário consultado se sobrepõe total ou parcialmente a outro agendamento agendado do profissional
- **THEN** o sistema não oferece esse horário para o profissional

#### Scenario: Horário liberado após cancelamento
- **WHEN** o agendamento que ocupava um horário passa à situação cancelado
- **THEN** o horário pode voltar a ser oferecido se atender às demais regras de disponibilidade

### Requirement: Cliente pode criar agendamento para profissional ou sem preferência
O sistema SHALL permitir que uma cliente autenticada reserve um serviço ativo da empresa com um profissional ativo vinculado ao serviço ou com a opção “sem preferência”.

#### Scenario: Reserva com profissional escolhido
- **WHEN** a cliente confirma um horário livre com profissional escolhido
- **THEN** o sistema cria um agendamento associado à cliente, à empresa, ao serviço e ao profissional selecionados, inicialmente na situação agendado

#### Scenario: Reserva sem preferência
- **WHEN** a cliente confirma um horário usando “sem preferência”
- **THEN** o sistema associa o agendamento a qualquer profissional ativo da empresa, vinculado ao serviço ativo e livre durante todo o intervalo

#### Scenario: Nenhum profissional disponível para sem preferência
- **WHEN** não existe profissional elegível livre no horário confirmado
- **THEN** o sistema rejeita a reserva e não cria agendamento

### Requirement: Criação revalida disponibilidade e evita conflitos
O backend SHALL revalidar a empresa, o serviço, o profissional, o período, a janela de antecedência e a ausência de sobreposição no instante de criar o agendamento, sem confiar na disponibilidade previamente exibida.

#### Scenario: Horário fica ocupado antes da confirmação
- **WHEN** outra reserva ocupa o horário após a consulta e antes da criação
- **THEN** o backend rejeita a nova reserva sem criar agendamento sobreposto

#### Scenario: Serviço ou profissional deixa de ser elegível
- **WHEN** o serviço é desativado, deixa de pertencer à empresa indicada ou o profissional é desativado ou deixa de realizar o serviço antes da criação
- **THEN** o backend rejeita a reserva sem persistir dados

#### Scenario: Cliente envia empresa incompatível
- **WHEN** a cliente tenta criar um agendamento usando identificador de serviço ou profissional de outra empresa
- **THEN** o backend rejeita a reserva sem revelar nem alterar dados da outra empresa

### Requirement: Agendamento preserva os dados do serviço no momento da reserva
O sistema SHALL armazenar no agendamento o nome, a duração e o preço do serviço vigentes no momento da reserva, sem substituir esses valores quando o serviço for alterado depois.

#### Scenario: Serviço é alterado após a reserva
- **WHEN** a empresa altera o nome, duração ou preço do serviço após um agendamento ser criado
- **THEN** o agendamento continua apresentando os valores originais registrados na reserva

### Requirement: Reserva exige cliente autenticada e respeita isolamento
O sistema SHALL exigir uma sessão de cliente válida para criar um agendamento e SHALL restringir os dados associados à empresa identificada pelo link público e à cliente autenticada.

#### Scenario: Pessoa sem sessão ou administradora tenta reservar
- **WHEN** uma pessoa sem sessão ou uma administradora envia uma solicitação de criação de agendamento como cliente
- **THEN** o backend rejeita a operação sem criar reserva

#### Scenario: Dados de outra empresa
- **WHEN** uma cliente consulta disponibilidade para uma empresa ou serviço inexistente ou pertencente a outra empresa
- **THEN** o sistema não retorna disponibilidade nem dados privados de outra empresa

### Requirement: Consulta pública de profissionais por serviço
O sistema SHALL permitir, sem autenticação, listar os profissionais ativos vinculados a um serviço ativo de uma empresa localizada pelo identificador público, retornando somente o id e o nome de cada profissional, para apoiar a escolha de profissional no agendamento.

#### Scenario: Serviço com profissionais vinculados
- **WHEN** uma pessoa consulta os profissionais de um serviço ativo da empresa
- **THEN** o sistema retorna apenas os profissionais ativos vinculados a esse serviço, com id e nome, sem outros dados

#### Scenario: Profissional inativo ou não vinculado
- **WHEN** um profissional da empresa está inativo ou não realiza o serviço consultado
- **THEN** o sistema não o inclui na lista

#### Scenario: Serviço inativo, inexistente ou de outra empresa
- **WHEN** o serviço consultado está inativo, não existe ou pertence a outra empresa
- **THEN** o sistema responde como não encontrado sem revelar profissionais

#### Scenario: Identificador desconhecido
- **WHEN** o identificador público não corresponde a nenhuma empresa
- **THEN** o sistema responde como não encontrado

### Requirement: Consulta pública de dias com horários livres
O sistema SHALL oferecer, sem autenticação e em uma única consulta, a lista de dias locais em `America/Sao_Paulo`, de hoje até 30 dias à frente, que possuem ao menos um início disponível para um serviço ativo da empresa e, opcionalmente, um profissional, aplicando as mesmas regras de disponibilidade; a interface SHALL usar essa lista para marcar os dias indisponíveis no calendário antes da escolha do dia.

#### Scenario: Dias com e sem horários livres
- **WHEN** uma pessoa consulta os dias disponíveis de um serviço ativo
- **THEN** o sistema retorna somente os dias da janela que têm ao menos um horário livre, e a interface apresenta os demais como indisponíveis antes da seleção

#### Scenario: Filtro por profissional
- **WHEN** a consulta indica um profissional ativo vinculado ao serviço
- **THEN** o sistema considera somente os períodos e agendamentos desse profissional

#### Scenario: Serviço ou empresa inválidos
- **WHEN** o identificador da empresa é desconhecido ou o serviço está inativo, não existe ou pertence a outra empresa
- **THEN** o sistema responde como não encontrado sem retornar dias
