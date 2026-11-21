# visual-design-system Specification

## Purpose

Define uma apresentação responsiva, acessível e consistente para as jornadas públicas, da cliente, da administradora do salão e da administradora da plataforma no BeautyTime.

## Requirements

### Requirement: Aplicar uma linguagem visual única em todas as rotas do app
Todas as páginas SHALL compartilhar uma linguagem visual neutra e refinada, com tipografia, cores, superfícies, espaçamento e componentes coerentes.

#### Scenario: Navegar entre áreas do app
- **WHEN** a pessoa visita as páginas inicial, de autenticação, área da cliente, diretório de salões, agendamento, administração do salão ou administração da plataforma
- **THEN** cada página apresenta a mesma paleta, tipografia, escala de espaçamento e tratamento visual de botões, campos, cards e mensagens

#### Scenario: Usar os tokens visuais da marca
- **WHEN** um elemento usa as cores de marca
- **THEN** o fundo principal é `#F6F1EA`, os campos e tiles internos usam `#FCFAF6`, os cards e painéis usam `#FFFEFC`, a cor principal é `#4A3A2E`, a principal em hover é `#382B22`, o detalhe é `#BF9C72`, o texto principal é `#2E2620`, o secundário é `#75675C` e as bordas são `#E6DCD0`, com variantes acessíveis quando necessário

#### Scenario: Usar tipografia e componentes do design system aprovado
- **WHEN** a interface aplica tipografia, espaçamento ou forma aos componentes
- **THEN** títulos usam Cormorant Garamond e textos usam Manrope, com fallback local; cards usam raio de 28px e padding 24px no mobile e 32px no desktop, tiles e métricas usam raio de 20px, campos raio de 14px e botões formato pill

### Requirement: Manter contraste de texto conforme WCAG AA
Texto SHALL manter contraste mínimo de 4,5:1 para texto normal e 3:1 para texto grande, inclusive em controles, badges e estados.

#### Scenario: Texto sobre fundo claro
- **WHEN** texto aparece sobre uma superfície branca ou o fundo `#F7F3EE`
- **THEN** sua combinação de cores alcança o contraste mínimo aplicável da WCAG AA
- **AND** tons de detalhe que não atingem esse contraste são usados apenas como decoração ou com uma cor de texto acessível

### Requirement: Adaptar páginas a telas móveis sem cortar conteúdo
As páginas SHALL priorizar telas estreitas, centralizar o conteúdo em uma largura legível e manter espaçamento lateral que impeça cortes ou conteúdo encostado nas bordas.

#### Scenario: Abrir páginas em viewport móvel
- **WHEN** uma rota é exibida em uma tela estreita
- **THEN** títulos, campos, botões, cards, navegação e listas cabem na viewport sem corte horizontal nem sobreposição

### Requirement: Apresentar controles e navegação de forma consistente
Botões, campos, cards, status e menus SHALL ter estilos reconhecíveis, estados interativos claros e hierarquia visual consistente.

#### Scenario: Preencher formulários
- **WHEN** a pessoa acessa um formulário de login, cadastro, busca ou edição existente
- **THEN** cada campo tem rótulo visível, bordas e foco claros, e ações principal e secundária são visualmente distinguíveis

#### Scenario: Consultar situação e área ativa
- **WHEN** uma página apresenta status de agendamento ou navegação de uma área administrativa
- **THEN** badges distinguem estados como confirmado e cancelado e o item correspondente à rota atual fica destacado

#### Scenario: Abrir uma área do painel do salão
- **WHEN** a pessoa seleciona um dos cards Serviços, Profissionais, Horários ou Agenda no painel do salão
- **THEN** o card é claramente identificável como interativo e navega para sua rota existente correspondente

### Requirement: Explicar estados de carregamento, vazio e erro
As páginas que carregam ou exibem dados SHALL apresentar estados visuais claros para carregamento, ausência de resultados e falha.

#### Scenario: Dados estão carregando
- **WHEN** uma página aguarda dados de uma operação já existente
- **THEN** a interface informa de forma visível que os dados estão carregando

#### Scenario: Lista sem resultados
- **WHEN** a consulta termina sem itens para exibir
- **THEN** a interface apresenta uma mensagem amigável que explica a ausência e indica um próximo passo aplicável

#### Scenario: Operação falha
- **WHEN** uma operação existente retorna erro
- **THEN** a mensagem de erro é clara, legível, acessível e visualmente distinta do conteúdo normal

### Requirement: Preservar integralmente o comportamento funcional
O redesenho SHALL modificar somente a apresentação e a clareza visual, preservando rotas, destinos de navegação, chamadas de API, regras de negócio, autenticação e fluxo de agendamento existentes.

#### Scenario: Usar um fluxo existente após o redesenho
- **WHEN** a pessoa conclui um login, cadastro, busca, edição, navegação ou agendamento por uma página redesenhada
- **THEN** o fluxo mantém os mesmos dados, destinos, integrações e resultados funcionais de antes do redesenho
