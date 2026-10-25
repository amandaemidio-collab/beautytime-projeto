# Spec Delta

## MODIFIED Requirements

### Requirement: Administradora mantém períodos semanais de atendimento
O sistema SHALL permitir que a administradora crie, liste, edite e remova períodos semanais vinculados aos profissionais ativos da própria empresa. Cada período informa um dia da semana e horários de início e término; um profissional pode ter vários períodos no mesmo dia, sem limite de horas diárias, desde que os períodos do mesmo dia não se sobreponham. Períodos que apenas se encostam, em que um termina no mesmo horário em que o outro começa, não são considerados sobrepostos.

#### Scenario: Cadastrar períodos em dias diferentes
- **WHEN** a administradora cadastra períodos válidos para um profissional ativo
- **THEN** os períodos ficam associados ao profissional e aparecem na lista de horários da empresa

#### Scenario: Cadastrar mais de um período no mesmo dia
- **WHEN** a administradora cadastra dois períodos de atendimento sem sobreposição para o mesmo profissional e dia da semana
- **THEN** o sistema mantém os dois períodos sem impor limite de horas diárias

#### Scenario: Períodos que se encostam
- **WHEN** a administradora cadastra, no mesmo dia, um período que começa exatamente quando outro período do profissional termina
- **THEN** o sistema aceita o cadastro e mantém os dois períodos

#### Scenario: Período sobreposto no cadastro
- **WHEN** a administradora cadastra um período que se sobrepõe total ou parcialmente a outro período do mesmo profissional no mesmo dia
- **THEN** o sistema rejeita a operação sem criar o período e informa o dia em conflito

#### Scenario: Período sobreposto na edição
- **WHEN** a administradora edita um período de modo que ele passe a se sobrepor a outro período do mesmo profissional no mesmo dia
- **THEN** o sistema rejeita a operação sem alterar o período e informa o dia em conflito; o próprio período em edição não conta como conflito

#### Scenario: Editar ou remover período
- **WHEN** a administradora altera ou remove um período da própria empresa
- **THEN** o sistema apresenta a configuração semanal atualizada sem modificar outros períodos do profissional

#### Scenario: Período inválido ou profissional inativo
- **WHEN** a administradora envia um dia inválido, um horário de início igual ou posterior ao término, ou tenta configurar um profissional inativo
- **THEN** o sistema rejeita a operação sem criar ou alterar o período

## ADDED Requirements

### Requirement: Administradora cadastra o mesmo período em vários dias
O sistema SHALL permitir que a administradora cadastre, numa única operação, um período com o mesmo início e término em um ou mais dias da semana de um profissional ativo da própria empresa, criando um período para cada dia informado. A operação SHALL ser tudo ou nada.

#### Scenario: Período em vários dias
- **WHEN** a administradora marca segunda, quarta e sexta com início 09:00 e término 18:00 e salva
- **THEN** o sistema cria três períodos de 09:00 às 18:00, um em cada dia marcado, e eles aparecem na lista de horários do profissional

#### Scenario: Todos os dias
- **WHEN** a administradora usa o atalho "Todos os dias" e salva um período válido
- **THEN** o sistema cria o período em cada um dos sete dias da semana

#### Scenario: Grupos de dias com horários diferentes
- **WHEN** a administradora cadastra 09:00 às 18:00 de segunda a sexta e depois 09:00 às 13:00 no sábado
- **THEN** o sistema mantém os seis períodos, cada grupo com o próprio horário

#### Scenario: Um dos dias tem conflito
- **WHEN** um dos dias marcados já tem período do profissional que se sobrepõe ao novo período
- **THEN** o sistema não cria o período em nenhum dos dias e informa qual dia está em conflito

#### Scenario: Nenhum dia, dia inválido ou dia repetido
- **WHEN** a requisição não informa nenhum dia, informa um dia fora de segunda a domingo ou repete o mesmo dia
- **THEN** o sistema rejeita a operação sem criar períodos

#### Scenario: Intervalo inválido ou profissional inativo
- **WHEN** o início é igual ou posterior ao término, ou o profissional está inativo
- **THEN** o sistema rejeita a operação sem criar períodos em nenhum dia

#### Scenario: Autorização e isolamento por empresa
- **WHEN** uma pessoa sem sessão, uma cliente ou uma administradora de outra empresa tenta cadastrar períodos em vários dias para um profissional
- **THEN** o sistema rejeita a operação sem criar períodos e sem revelar dados do profissional ou da empresa

### Requirement: Formulário de horários permite marcar vários dias
O sistema SHALL apresentar, no formulário de novo período da tela Horários, a marcação de um ou mais dias de segunda a domingo e o atalho "Todos os dias", enviando o cadastro ao backend numa única requisição; o formulário de edição SHALL manter a escolha de um único dia.

#### Scenario: Marcar dias e salvar
- **WHEN** a administradora marca um ou mais dias, informa início e término e salva
- **THEN** a interface envia uma única requisição e, após o sucesso, apresenta a lista atualizada com um período por dia marcado

#### Scenario: Salvar sem dia marcado
- **WHEN** a administradora tenta salvar sem marcar nenhum dia
- **THEN** a interface informa que é preciso marcar ao menos um dia e não envia a requisição

#### Scenario: Falha em um dos dias
- **WHEN** o backend rejeita o cadastro por conflito em um dos dias
- **THEN** a interface informa qual dia falhou, mantém os dias e horários marcados no formulário e não apresenta nenhum período novo como cadastrado

#### Scenario: Editar um período
- **WHEN** a administradora edita um período existente
- **THEN** o formulário apresenta a escolha de um único dia e a alteração afeta somente aquele período

#### Scenario: Uso no celular
- **WHEN** a tela é usada em viewport de celular
- **THEN** a marcação dos dias e o atalho "Todos os dias" ficam legíveis e tocáveis, sem rolagem horizontal
