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
