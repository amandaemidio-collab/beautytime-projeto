# Spec Delta

## REMOVED Requirements

### Requirement: Administradora autenticada acessa o painel inicial
**Reason**: O painel inicial passará a apresentar indicadores operacionais, substituindo o comportamento que proibia números de resumo.
**Migration**: A administradora continuará acessando a mesma página inicial, agora com os indicadores e próximos horários definidos pela requirement “Administradora consulta os indicadores da própria empresa”.

## ADDED Requirements

### Requirement: Administradora consulta os indicadores da própria empresa
O sistema SHALL mostrar à administradora autenticada os indicadores e próximos horários da própria empresa no painel inicial, sem permitir acesso aos dados de outra empresa.

#### Scenario: Administradora abre o painel
- **WHEN** uma administradora autenticada acessa o painel inicial
- **THEN** a interface mostra o nome da empresa, o menu administrativo, os indicadores da própria empresa, os próximos horários de hoje e o link público do salão

#### Scenario: Métricas do painel
- **WHEN** uma administradora visualiza os indicadores
- **THEN** vê agendamentos de hoje não cancelados, total de agendamentos da semana incluindo cancelados, faturamento estimado da semana somando os preços registrados nos agendamentos não cancelados, taxa de cancelamento calculada como cancelados divididos pelo total da semana, os cinco serviços mais agendados na semana e até cinco próximos horários de hoje não cancelados

#### Scenario: Painel sem agendamentos na semana
- **WHEN** não há agendamentos na semana da empresa
- **THEN** o painel mostra totais e faturamento iguais a zero, taxa de cancelamento igual a zero e nenhuma entrada nos serviços mais agendados

#### Scenario: Próximos horários do dia
- **WHEN** existem agendamentos futuros de hoje para a empresa
- **THEN** o painel mostra até cinco horários não cancelados em ordem crescente de início, incluindo serviço e profissional

#### Scenario: Falha ao carregar indicadores
- **WHEN** a consulta dos indicadores falha ou retorna dados inválidos
- **THEN** o painel informa que não foi possível carregar os indicadores e não apresenta métricas parciais

#### Scenario: Isolamento por empresa
- **WHEN** uma administradora consulta o painel
- **THEN** todos os indicadores e próximos horários pertencem somente à empresa associada à sua sessão, sem aceitar um identificador de empresa enviado pela interface

#### Scenario: Cliente ou pessoa sem sessão tenta abrir o painel
- **WHEN** uma cliente ou pessoa sem sessão válida acessa uma rota administrativa protegida
- **THEN** a interface encaminha a pessoa para o login de administradora e não exibe dados administrativos

#### Scenario: Indicadores antes do link público
- **WHEN** a administradora abre o painel
- **THEN** os cards de indicadores e os próximos horários aparecem acima da seção “Link público do salão”
