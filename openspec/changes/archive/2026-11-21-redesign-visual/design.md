# Design

## Context

Consulte `proposal.md` e `specs/visual-design-system/spec.md`. O frontend Reflex está concentrado em `frontend/frontend/frontend.py` e `frontend/frontend/platform_panel.py`; `frontend/frontend/theme.py` já contém tokens globais, mas ainda há estilos de página e valores visuais repetidos nos módulos. Não foram encontrados testes automatizados de interface.

## Goals / Non-Goals

**Goals:**
- Fazer `theme.py` a fonte única de tokens e componentes de estilo compartilhados.
- Cobrir as rotas atuais sem alterar handlers, estado, URLs ou payloads de API.
- Validar contraste e layout em breakpoints móveis e desktop.

**Non-Goals:**
- Alterar lógica de negócio, estado, endpoints, conteúdo de dados ou fluxo de navegação.
- Adicionar dependências de frontend, alterar o Xano ou iniciar outro servidor Reflex.
- Reformular a arquitetura das páginas ou remover opções atualmente disponíveis.

## Decisions

### Centralizar tokens e estilos compartilhados em `theme.py`

Expandir o tema existente com cores semânticas, estilos globais e helpers reutilizáveis para shell de página, títulos, superfícies/cards, controles, botões primário/secundário, status, navegação ativa, carregamento, vazio e erro. `frontend.py` e `platform_panel.py` importarão o tema em vez de manter paletas e estilos de página concorrentes; `rxconfig.py` continuará apontando o tema Radix para a cor principal apropriada.

Alternativa considerada: criar um módulo separado de componentes visuais. Foi rejeitada porque o requisito pede explicitamente centralizar o design system em `theme.py` e o escopo pode ser coberto pelos helpers do tema existente.

### Usar pares de cores que atendam contraste

Usar os valores HEX do arquivo `docs/beautytime-design-tokens.json`: fundo `#F6F1EA`, superfícies `#FFFEFC`, campos e tiles `#FCFAF6`, texto principal `#2E2620`, secundário `#75675C`, primário `#4A3A2E`, hover `#382B22`, detalhe `#BF9C72` e borda `#E6DCD0`. O contraste calculado do texto principal sobre superfícies claras varia de 13,21:1 a 14,73:1; o texto secundário varia de 4,85:1 a 5,41:1. O primário varia de 9,65:1 a 10,76:1. O detalhe dourado tem contraste abaixo de 3:1 em fundos claros, portanto é somente decorativo ou acompanhado de texto acessível. Os tons de sucesso, aviso e erro sobre fundos suaves devem manter no mínimo 4,5:1.

Alternativa considerada: usar o dourado como texto pequeno sobre superfícies claras. Foi rejeitada porque `#BF9C72` tem contraste de 2,28:1 a 2,54:1 nesses fundos.

### Aplicar tipografia e estética sem nova dependência

Carregar Cormorant Garamond e Manrope pela folha de estilos do Google Fonts, com pilhas locais de fallback serif e sans-serif. Aplicar Cormorant Garamond a títulos e Manrope a texto e controles. Usar cards com raio de 28 px e padding 24 px no mobile/32 px no desktop, tiles e métricas de 20 px, campos de 14 px, botões pill, sombras discretas e espaçamento responsivo com breakpoints já suportados pelo Reflex.

Alternativa considerada: instalar biblioteca de componentes ou distribuir arquivos de fonte. Foi rejeitada por adicionar dependência/peso sem necessidade; as fontes são uma escolha visual com fallback funcional.

### Preservar todas as rotas e fluxos

Redesenhar as páginas já registradas: `/`, `/clientes/cadastro`, `/clientes/login`, `/admin/cadastro`, `/admin/login`, `/admin`, `/admin/servicos`, `/admin/profissionais`, `/admin/horarios`, `/admin/agenda`, `/meus-agendamentos`, `/saloes`, `/boas-vindas`, `/agendar/[identificador]`, `/platform/login`, `/platform` e `/platform/saloes/[account_id]`. O item ativo será determinado pela rota atual sem trocar destinos. Os cards Serviços, Profissionais, Horários e Agenda manterão seus links existentes e receberão estilo/indicação de foco e hover para comunicar que toda a superfície é clicável.

Alternativa considerada: reestruturar rotas ou criar novos wrappers com lógica própria. Foi rejeitada para preservar exatamente o comportamento existente.

### Melhorar clareza dos estados sem mudar a lógica

Reutilizar os estados de carregamento, erro e lista vazia já existentes no estado Reflex; aplicar componentes visuais e mensagens com próximo passo onde o contexto permite. Não adicionar chamadas de rede, retries, defaults de dados ou novas regras de negócio. Campos e mensagens manterão associações acessíveis, rótulos, foco visível, `role=alert`/`status` quando já apropriado e responsividade.

## Risks / Trade-offs

- [A atualização visual de todas as rotas pode deixar estilos residuais] → Centralizar busca e revisão de valores locais em `frontend.py` e `platform_panel.py`; validar compilação e abrir cada rota.
- [Fontes externas podem não carregar] → Declarar fallback coerente para serif e sans-serif e verificar a renderização sem dependência da fonte externa.
- [Combinações da paleta não atingem AA em todos os fundos] → Medir tokens de texto contra cada superfície e usar variantes acessíveis, sem perder as cores de marca como acentos.
- [Autenticação pode limitar a inspeção de páginas privadas] → Usar sessões válidas de demonstração no navegador para as áreas protegidas, sem alterar dados ou endpoints apenas para testes.
- [Servidor `localhost:3000` pode estar indisponível] → Não iniciar outro processo; registrar a indisponibilidade como bloqueio de validação visual e preservar o processo existente.

## Migration Plan

1. Atualizar o design system centralizado e aplicar os tokens/helpers às páginas da cliente e do salão.
2. Aplicar os mesmos tokens e componentes às páginas `/platform`.
3. Executar a compilação Reflex existente e validar os pares de contraste de texto/superfície.
4. Conferir as rotas no servidor já em execução, em viewports móveis e desktop; corrigir cortes, estados e inconsistências.

Rollback consiste em reverter apenas mudanças nos arquivos Reflex desta change; não há migração de dados nem efeitos no Xano.
