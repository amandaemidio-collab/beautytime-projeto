# Spec Delta

## MODIFIED Requirements

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
