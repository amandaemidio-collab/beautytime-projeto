# Spec Delta

## ADDED Requirements

### Requirement: Área da cliente oferece novo agendamento
O sistema SHALL apresentar na área `/meus-agendamentos` um botão "Novo agendamento" que leva à tela "Encontrar salões", inclusive quando a cliente ainda não possui agendamentos.

#### Scenario: Cliente inicia novo agendamento
- **WHEN** a cliente autenticada seleciona "Novo agendamento"
- **THEN** a interface abre a tela "Encontrar salões"

#### Scenario: Cliente sem agendamentos
- **WHEN** a cliente autenticada não possui agendamentos
- **THEN** o botão "Novo agendamento" continua disponível junto ao estado vazio

### Requirement: Agendamento listado permite agendar de novo no mesmo salão
O sistema SHALL apresentar em cada agendamento listado em `/meus-agendamentos`, próximo ou passado, agendado ou cancelado, um botão "Agendar de novo" que leva a `/agendar/{identificador}` do salão daquele agendamento, sem preencher previamente serviço, profissional, dia ou horário.

#### Scenario: Agendar de novo a partir de um agendamento
- **WHEN** a cliente seleciona "Agendar de novo" em um agendamento
- **THEN** a interface abre `/agendar/{identificador}` do salão daquele agendamento, com o fluxo iniciado na escolha do serviço

#### Scenario: Agendamentos de salões diferentes
- **WHEN** a cliente possui agendamentos em mais de um salão
- **THEN** o botão de cada agendamento leva ao salão daquele agendamento, e não ao de outro

#### Scenario: Agendamento cancelado ou passado
- **WHEN** o agendamento está cancelado ou seu início já passou
- **THEN** o botão "Agendar de novo" continua disponível, sem oferecer a opção de cancelar quando ela não se aplica

#### Scenario: Salão que deixou de aceitar reservas
- **WHEN** a cliente usa "Agendar de novo" para um salão que não tem mais serviços disponíveis
- **THEN** a página pública apresenta o estado de empresa sem serviços disponíveis, sem criar reserva

### Requirement: Página pública de agendamento respeita as margens das demais telas
O sistema SHALL apresentar `/agendar/{identificador}` com as mesmas margens laterais das demais telas, sem conteúdo encostado na borda e sem cartão cortado ou rolagem horizontal, em viewport de celular e desktop, em todas as etapas do fluxo.

#### Scenario: Página no celular
- **WHEN** a página pública é aberta em viewport de celular, com o fluxo em qualquer etapa até a confirmação
- **THEN** o conteúdo fica centralizado dentro das margens laterais e o cartão aparece inteiro, sem rolagem horizontal

#### Scenario: Página no desktop
- **WHEN** a página pública é aberta em viewport de desktop
- **THEN** o conteúdo fica centralizado com a mesma largura máxima e as mesmas margens usadas nas demais telas da cliente

#### Scenario: Empresa não encontrada
- **WHEN** a página é aberta para um identificador desconhecido
- **THEN** a mensagem "Empresa não encontrada" respeita as mesmas margens, sem conteúdo cortado

### Requirement: Página pública apresenta texto do fluxo de agendamento
O sistema SHALL apresentar, abaixo do nome da empresa em `/agendar/{identificador}`, um texto introdutório que convide a cliente a escolher serviço, profissional, dia e horário, e SHALL NOT exibir mensagens que indiquem que o agendamento estará disponível futuramente.

#### Scenario: Empresa encontrada
- **WHEN** a página pública de uma empresa existente é carregada
- **THEN** a interface apresenta o texto introdutório do fluxo de agendamento e nenhuma mensagem de "em breve"
