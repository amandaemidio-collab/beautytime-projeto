# Spec Delta

## Purpose

Permite que a administradora acompanhe os agendamentos de sua empresa por dia e profissional, incluindo situações de cancelamento tardio, sem alterar ou cancelar reservas.

## ADDED Requirements

### Requirement: Administradora consulta agenda da própria empresa por dia
O sistema SHALL exibir à administradora autenticada os agendamentos da empresa associada à sessão para o dia selecionado, incluindo cliente, serviço, horário, situação e indicação de cancelamento tardio.

#### Scenario: Dia com agendamentos
- **WHEN** a administradora seleciona um dia com agendamentos
- **THEN** a agenda apresenta os registros da empresa com cliente, serviço, início e término, situação e marcação de cancelamento tardio quando aplicável

#### Scenario: Filtrar agenda por profissional
- **WHEN** a administradora escolhe um profissional da própria empresa como filtro
- **THEN** a agenda apresenta somente os agendamentos daquele profissional no dia selecionado

#### Scenario: Dia sem agendamentos
- **WHEN** a empresa não possui agendamentos no dia ou filtro selecionado
- **THEN** a interface apresenta estado vazio sem inserir registros de outros dias

#### Scenario: Cancelamento tardio aparece na agenda
- **WHEN** um agendamento da empresa foi cancelado tardiamente
- **THEN** a agenda mantém o registro visível no dia correspondente e o identifica como cancelamento tardio

### Requirement: Agenda administrativa respeita autorização e isolamento
O backend SHALL permitir a consulta da agenda somente à administradora autenticada e SHALL limitar os resultados à empresa associada à sessão, sem aceitar identificador de empresa enviado pela interface como autorização.

#### Scenario: Pessoa sem sessão ou cliente consulta agenda
- **WHEN** uma pessoa sem sessão válida ou uma cliente tenta consultar a agenda administrativa
- **THEN** o backend rejeita a consulta sem revelar agendamentos

#### Scenario: Administradora tenta consultar outra empresa
- **WHEN** uma administradora envia um identificador de outra empresa ou de profissional pertencente a outra empresa como filtro
- **THEN** o backend limita a consulta à empresa da sessão e não retorna dados de outra empresa

### Requirement: Agenda é somente para visualização
O sistema SHALL oferecer à administradora leitura dos agendamentos na agenda, sem ações de edição, cancelamento ou reagendamento nesta capability.

#### Scenario: Administradora consulta um agendamento
- **WHEN** a administradora seleciona ou abre um registro da agenda
- **THEN** os dados permanecem inalterados e nenhuma ação de edição, cancelamento ou reagendamento é oferecida
