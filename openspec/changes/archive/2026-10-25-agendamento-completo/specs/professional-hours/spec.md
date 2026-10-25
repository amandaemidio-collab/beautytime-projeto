# Spec Delta

## Purpose

Permite que administradoras configurem os períodos semanais em que cada profissional da própria empresa atende, como base para consultar disponibilidade e reservar serviços.

## ADDED Requirements

### Requirement: Administradora mantém períodos semanais de atendimento
O sistema SHALL permitir que a administradora crie, liste, edite e remova períodos semanais vinculados aos profissionais ativos da própria empresa. Cada período informa um dia da semana e horários de início e término; um profissional pode ter vários períodos no mesmo dia, sem limite de horas diárias.

#### Scenario: Cadastrar períodos em dias diferentes
- **WHEN** a administradora cadastra períodos válidos para um profissional ativo
- **THEN** os períodos ficam associados ao profissional e aparecem na lista de horários da empresa

#### Scenario: Cadastrar mais de um período no mesmo dia
- **WHEN** a administradora cadastra dois períodos de atendimento para o mesmo profissional e dia da semana
- **THEN** o sistema mantém os dois períodos sem impor limite de horas diárias

#### Scenario: Editar ou remover período
- **WHEN** a administradora altera ou remove um período da própria empresa
- **THEN** o sistema apresenta a configuração semanal atualizada sem modificar outros períodos do profissional

#### Scenario: Período inválido ou profissional inativo
- **WHEN** a administradora envia um dia inválido, um horário de início igual ou posterior ao término, ou tenta configurar um profissional inativo
- **THEN** o sistema rejeita a operação sem criar ou alterar o período

### Requirement: Horários respeitam autorização e isolamento por empresa
O sistema SHALL autorizar a manutenção de horários somente a administradoras autenticadas e SHALL determinar a empresa pela sessão, impedindo consulta ou alteração de horários de profissionais de outra empresa.

#### Scenario: Pessoa sem sessão ou cliente solicita horários administrativos
- **WHEN** uma pessoa sem sessão válida ou uma cliente consulta ou altera horários pela API administrativa
- **THEN** o sistema rejeita a operação sem revelar dados de horários

#### Scenario: Administradora envia profissional de outra empresa
- **WHEN** uma administradora tenta consultar, criar, editar ou remover período de profissional pertencente a outra empresa
- **THEN** o sistema rejeita a operação sem revelar nem alterar o período ou profissional alheio

#### Scenario: Identificador de empresa forjado
- **WHEN** uma administradora inclui na requisição um identificador de empresa diferente do associado à sessão
- **THEN** o sistema ignora o identificador enviado e restringe a operação à empresa da sessão
