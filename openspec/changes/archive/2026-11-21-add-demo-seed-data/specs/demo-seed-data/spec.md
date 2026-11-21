# Spec Delta

## Purpose

Permite preparar no Xano um conjunto consistente de dados fictícios para demonstrar salões, serviços, profissionais e agendamentos, sem duplicar nem modificar dados que já existam.

## ADDED Requirements

### Requirement: Criar os salões de demonstração e seus dados relacionados
A preparação SHALL criar somente os salões de demonstração ausentes e incluir para cada salão novo um usuário administrador, serviços ativos, profissionais ativos associados aos serviços e horários de atendimento de segunda a sábado.

#### Scenario: Criar os três salões configurados
- **WHEN** a preparação é executada e nenhum dos identificadores públicos dos salões existe
- **THEN** são criados `Salão Aurora - Pinheiros` (`salao-aurora`, dono `dono.salao-aurora@demo.beautytime`), `Barbearia Paulista` (`barbearia-paulista`, dono `dono.barbearia-paulista@demo.beautytime`) e `Estúdio Unhas Bela` (`estudio-unhas-bela`, dono `dono.estudio-unhas-bela@demo.beautytime`), todos localizados em São Paulo
- **AND** cada dono tem role `admin` e está associado à conta correspondente
- **AND** cada salão tem de quatro a cinco serviços ativos, dois profissionais ativos ligados aos serviços e horários de segunda a sábado

### Requirement: Criar e reutilizar clientes demo sem alterar usuários existentes
A preparação SHALL criar os clientes demo ausentes como usuários globais de role `client` e SHALL reutilizar somente usuários existentes com os mesmos e-mails, role `client` e sem associação a uma conta.

#### Scenario: Criar ou reutilizar os quatro clientes
- **WHEN** a preparação verifica os usuários `cliente1@demo.beautytime`, `cliente2@demo.beautytime`, `cliente3@demo.beautytime` e `cliente4@demo.beautytime`
- **THEN** cada cliente ausente é criado sem associação a uma conta e cada cliente já existente com role `client` é reutilizado sem alteração

#### Scenario: E-mail reservado já pertence a usuário incompatível
- **WHEN** um e-mail de cliente ou dono necessário já pertence a um usuário com role ou associação de conta incompatível
- **THEN** a preparação falha sem alterar esse usuário nem criar dados parciais

### Requirement: Não duplicar nem modificar registros existentes
A preparação SHALL ser idempotente e SHALL somente inserir registros ausentes, sem atualizar ou excluir dados existentes.

#### Scenario: Salão já existe pelo identificador público
- **WHEN** um salão demo já existe pelo seu `public_identifier`
- **THEN** esse salão e todos os seus registros relacionados são ignorados sem alteração, enquanto os outros salões ausentes ainda podem ser preparados

#### Scenario: Executar novamente após uma preparação completa
- **WHEN** a preparação é executada novamente sem mudanças nos dados demo
- **THEN** nenhum registro duplicado é criado e nenhum registro existente é atualizado ou excluído

### Requirement: Criar agendamentos demo consistentes na semana atual
A preparação SHALL criar dez agendamentos por salão novo na semana corrente de `America/Sao_Paulo`, incluindo sete passados e três hoje ainda futuros entre 17:00 e 18:45, com exatamente dois cancelados e snapshots do serviço no momento do agendamento.

#### Scenario: Semana atual com horários disponíveis
- **WHEN** existe uma combinação válida de horários na semana atual para cada salão novo
- **THEN** cada salão recebe dez agendamentos com clientes, serviços e profissionais associados, sendo sete passados e três na data de hoje
- **AND** os três agendamentos de hoje começam entre 17:00 e 18:45 no fuso de São Paulo e permanecem no futuro com pelo menos uma hora de antecedência
- **AND** os horários de hoje ficam dentro do expediente dos profissionais, sem sobreposição para o mesmo profissional
- **AND** exatamente dois agendamentos por salão têm status `cancelado`
- **AND** cada registro contém `service_name`, `service_duration_minutes` e `service_price_cents` correspondentes ao serviço
- **AND** nenhum intervalo de agendamento se sobrepõe a outro no mesmo salão
- **AND** os horários futuros respeitam o limite de uma hora a trinta dias, a disponibilidade e a duração do serviço

#### Scenario: Não há horários suficientes na semana corrente
- **WHEN** não é possível acomodar os dez agendamentos exigidos, incluindo horários passados, futuros e um horário hoje, respeitando o expediente e as regras de agendamento
- **THEN** a preparação falha sem inserir dados parciais

### Requirement: Receber a senha demo durante a execução
A preparação SHALL receber a senha de demonstração como entrada de execução e criar os usuários pelo campo seguro de senha do Xano, sem versionar ou registrar a senha em texto.

#### Scenario: Criar usuários usando a senha fornecida
- **WHEN** a preparação recebe a senha demo
- **THEN** todos os usuários novos usam essa senha por meio do mecanismo de armazenamento seguro do Xano e o valor não é incluído nos arquivos versionados nem na saída de logs

#### Scenario: Senha ausente
- **WHEN** a preparação é chamada sem a senha obrigatória
- **THEN** ela falha antes de criar ou alterar qualquer dado
