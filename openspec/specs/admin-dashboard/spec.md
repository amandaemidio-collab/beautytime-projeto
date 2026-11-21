# admin-dashboard Specification

## Purpose
Define a entrada administrativa do BeautyTime e a navegação entre as áreas disponíveis, mantendo visíveis como futuras as funções ainda não implementadas.

## Requirements

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

### Requirement: Painel oferece navegação administrativa
O sistema SHALL apresentar no painel os itens Serviços, Profissionais, Horários e Agenda, encaminhando para as respectivas áreas administrativas disponíveis.

#### Scenario: Áreas disponíveis
- **WHEN** a administradora seleciona Serviços ou Profissionais
- **THEN** a interface abre a área administrativa correspondente

#### Scenario: Horários e Agenda ainda não disponíveis
- **WHEN** a administradora seleciona Horários ou Agenda após esta mudança estar disponível
- **THEN** a interface abre a área administrativa correspondente, sem exibir “Em breve”

#### Scenario: Áreas protegidas
- **WHEN** uma cliente ou pessoa sem sessão válida tenta abrir Horários ou Agenda
- **THEN** a interface encaminha a pessoa ao login de administradora sem exibir dados administrativos

### Requirement: Administradora pode copiar o link público do salão
O sistema SHALL mostrar à administradora o link público completo da própria empresa e permitir copiá-lo para a área de transferência.

#### Scenario: Copiar link público
- **WHEN** a administradora aciona o botão de copiar
- **THEN** a URL completa da página `/agendar/{identificador}` da própria empresa é copiada e a interface confirma a cópia

#### Scenario: Falha ao copiar link
- **WHEN** o navegador não permite copiar o link para a área de transferência
- **THEN** a interface informa que a cópia falhou e mantém o link visível para cópia manual
