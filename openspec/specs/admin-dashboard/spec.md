# admin-dashboard Specification

## Purpose
Define a entrada administrativa do BeautyTime e a navegação entre as áreas disponíveis, mantendo visíveis como futuras as funções ainda não implementadas.

## Requirements

### Requirement: Administradora autenticada acessa o painel inicial
O sistema SHALL oferecer à administradora autenticada um painel inicial da própria empresa, sem exibir indicadores ou números de resumo.

#### Scenario: Administradora abre o painel
- **WHEN** uma administradora autenticada acessa o painel inicial
- **THEN** a interface mostra o nome da empresa, o menu administrativo e o link público do salão

#### Scenario: Cliente ou pessoa sem sessão tenta abrir o painel
- **WHEN** uma cliente ou pessoa sem sessão válida acessa uma rota administrativa protegida
- **THEN** a interface encaminha a pessoa para o login de administradora e não exibe dados administrativos

#### Scenario: Painel sem indicadores
- **WHEN** uma administradora visualiza o painel inicial
- **THEN** a interface não apresenta contagens, métricas ou indicadores numéricos

### Requirement: Painel oferece navegação administrativa
O sistema SHALL apresentar no painel os itens Serviços, Profissionais, Horários e Agenda, encaminhando somente para áreas disponíveis.

#### Scenario: Áreas disponíveis
- **WHEN** a administradora seleciona Serviços ou Profissionais
- **THEN** a interface abre a área administrativa correspondente

#### Scenario: Horários e Agenda ainda não disponíveis
- **WHEN** as changes de Horários ou Agenda ainda não estão disponíveis
- **THEN** o painel exibe cada item com o rótulo “Em breve” e não abre uma funcionalidade inexistente

### Requirement: Administradora pode copiar o link público do salão
O sistema SHALL mostrar à administradora o link público completo da própria empresa e permitir copiá-lo para a área de transferência.

#### Scenario: Copiar link público
- **WHEN** a administradora aciona o botão de copiar
- **THEN** a URL completa da página `/agendar/{identificador}` da própria empresa é copiada e a interface confirma a cópia

#### Scenario: Falha ao copiar link
- **WHEN** o navegador não permite copiar o link para a área de transferência
- **THEN** a interface informa que a cópia falhou e mantém o link visível para cópia manual
