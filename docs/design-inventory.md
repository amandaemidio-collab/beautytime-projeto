# Inventário visual do BeautyTime

Este documento descreve a interface Reflex atualmente definida no repositório, para servir de referência a um redesenho. A fonte do inventário é o código da interface e seu design system (`frontend/frontend/theme.py`, `frontend/frontend/frontend.py` e `frontend/frontend/platform_panel.py`), não uma especificação de telas novas.

> Textos entre colchetes, como `[nome do salão]`, representam dados dinâmicos. Mensagens de erro retornadas pela API também são dinâmicas; os textos abaixo registram as mensagens fixas e os formatos implementados. A rota `/boas-vindas` é um redirecionamento, não uma tela.

## Tokens atuais

### Cores

| Token | Valor | Uso |
|---|---|---|
| `background` | `#F7F3EE` | Fundo das páginas |
| `surface` | `#FFFFFF` | Cards, painéis, campos |
| `accent` | `#8B6B4E` | Fundo dos botões principais |
| `accent_hover` | `#5C4433` | Hover de ações principais |
| `accent_text` | `#72563F` | Links e ações em texto sobre fundo claro |
| `detail` | `#C8A27A` | Acento decorativo e contorno de foco |
| `text` | `#2B2420` | Texto principal e títulos |
| `muted` | `#72675F` | Texto secundário; variante escurecida para contraste |
| `muted_brand` | `#7A6E66` | Variante semântica da paleta, sem uso amplo nos componentes |
| `border` | `#E8E0D6` | Bordas e divisores |
| `success` | `#286548` | Confirmações e mensagens de sucesso |
| `success_soft` | `#E9F3EC` | Fundo suave de status positivo |
| `error` | `#963F45` | Erros e ações destrutivas |
| `error_soft` | `#FBEAEC` | Fundo suave de erro |
| Navegação ativa | `#EFE7DE` | Fundo do item ativo no menu administrativo |
| Foco | `#C8A27A` | Outline de 3 px, offset de 2 px |

O Google Fonts declara **Inter** nos pesos 400, 500, 600 e 700 e **Playfair Display** nos pesos 500, 600 e 700. Texto usa `"Inter", sans-serif`; títulos usam `"Playfair Display", Georgia, serif`. Os fallbacks não dependem da fonte remota.

### Tipografia, pesos e tamanhos

- Texto e controles: Inter, pesos padrão 400; rótulos e botões 500/600; badges 600.
- Títulos: Playfair Display, peso padrão de componente; heading global com `line-height: 1.2`. Marca BeautyTime usa heading peso bold (700), tamanho Reflex `6`, cor `#72563F`, letter-spacing `-0.04em`.
- Rótulos de formulário: tamanho Reflex `2`, peso `medium` (500).
- Títulos usam tamanhos Reflex (`4`, `5`, `6`, `7`, `8`), não valores px definidos diretamente. Formulários variam heading `6` em mobile para `8` a partir do breakpoint `sm`.
- Texto auxiliar e de estado geralmente usa tamanho Reflex `2`; descrições usam line-height `1.6`.
- Inputs recebem fonte de 16 px globalmente. Botões têm peso 600 e altura mínima global de 48 px; diversas ações definem altura explícita de 44, 48, 50 ou 52 px.

### Cantos, sombras, bordas e foco

- Cards, painéis, tiles e estados vazios: raio de 16 px.
- Campos e botões: raio de 12 px.
- Badges: raio de 999 px.
- Links da navegação do salão: raio de 10 px.
- Bordas padrão: 1 px sólido `#E8E0D6`; seleção no serviço de agendamento: 2 px sólido `#8B6B4E`; estados vazios: borda tracejada de 1 px.
- Sombra de card: `0 8px 28px rgba(43, 36, 32, 0.07)`.
- Sombra de tile: `0 3px 14px rgba(43, 36, 32, 0.05)`.
- Foco de botões/links/cards: outline `3px solid #C8A27A`, offset `2px`. Inputs: borda `#8B6B4E` e halo `0 0 0 2px #8B6B4E33`.
- Transição global de botão: `background-color 160ms ease, box-shadow 160ms ease`.
- Cards clicáveis do painel do salão: hover eleva `translateY(-2px)`, usa sombra de card e borda detalhe.

### Espaçamento e dimensões

| Elemento | Valores atuais |
|---|---|
| Shell de página | padding mobile `28px 16px`; a partir de `md`, `52px 24px`; min-height `100vh`; overflow-x hidden |
| Card de formulário | largura 100%, max-width 520 px; padding mobile `24px 20px`, a partir de `md` `36px` |
| Painel compartilhado | largura 100%; padding mobile `18px`, a partir de `sm` `24px` |
| Tile/lista | largura 100%; padding mobile `16px`, a partir de `sm` `20px` |
| Estado vazio | largura 100%; padding `20px`; conteúdo centralizado; pilha com spacing Reflex `2` |
| Cards de item | padding mobile `18px`, a partir de `sm` `22px` |
| Cabeçalho e formulário administrativo | padding mobile `20px`, a partir de `sm` `26px` |
| Card de detalhes | padding mobile `18px`, a partir de `sm` `24px` |
| Link de navegação ativa | padding `8px 12px` |
| Login da plataforma | padding `28px` |
| Campo | largura 100%; min-height 48 px |
| Botão | min-height 48 px; alturas pontuais 44/48/50/52/56 px conforme componente |
| Campo de formulário em label | pilha vertical; spacing Reflex `2` |
| Formulário e grupos | spacing Reflex `2`, `3` ou `4`; formulários de autenticação usam `4` |
| Shell de página | espaçamento entre marca e card `6`; pilhas de página em geral `5` |
| Grid/menus | spacing Reflex `2`, `3`, `4` ou `5`, conforme bloco |
| Margens explícitas | diálogo de cancelamento: `margin_top` de `12px` no corpo e `16px` nos botões; demais separações são controladas por `spacing` |
| Espaçamento vertical interno de lista | `padding_y="2"` em linhas da tabela/lista de agendamentos nas agendas |
| Página inicial | max-width 900 px; card principal padding mobile `28px 20px`, desktop `40px` |
| Login/cadastro (cliente e salão) | max-width 520 px |
| Área da cliente e busca de salões | max-width 720 px |
| Páginas do salão e fluxo de agendamento | max-width 720 px |
| Páginas administrativas do salão | max-width 820 px |
| Painel da plataforma | max-width 1100 px |
| Login da plataforma | formulário max-width 480 px |

`initial`, `sm`, `md` e `lg` são breakpoints responsivos do Reflex/Radix. Colunas em grids: página inicial 1 → 2 em `md`; métricas do salão 1 → 2 em `sm` → 4 em `lg`; filtros de plataforma 1 → 2 em `md`; cards de plataforma 1 → 2 em `md`; tabs administrativas empilham no mobile e alinham em linha a partir de `sm`. Valores `spacing="N"` e `padding_y="N"` são a escala de espaçamento do Reflex/Radix, não N pixels.

## Regras invariáveis para o redesenho

- Não mudar qualquer rota, destino de link, redirecionamento ou parâmetro de continuação do agendamento.
- Não mudar nomes, tipos, obrigatoriedade, validação ou ordem funcional dos campos; nem destinos de formulários e ações.
- Preservar chamadas e contratos da API, autenticação, estados, isolamentos, payloads, handlers e regras de negócio.
- Preservar o fluxo: serviço → profissional → dia/horário → confirmação; autenticação pode ocorrer antes de confirmar e mantém as escolhas.
- Manter a regra exibida de cancelamento gratuito com pelo menos 8 horas; após esse limite há aviso de taxa informativa de R$ 5,00, sem processamento de pagamento.
- Mensagens de disponibilidade e estados vazios não devem prometer ação que não existe. Não exibir dado de outra empresa nem expandir o escopo dos usuários.

## Elementos e comportamento compartilhados

- Em páginas públicas, o logotipo textual “BeautyTime” é link para `/`.
- Formulários têm rótulo acima do campo; inputs e selects ocupam 100% da coluna. Campos com erro têm mensagem associada e `role="alert"`.
- O botão principal usa fundo `#8B6B4E` e texto branco; ações secundárias usam variante outline/soft. Campos têm `min-height` 48 px e raio 12 px.
- Cabeçalhos do salão exibem marca, navegação “Painel”, “Serviços”, “Profissionais”, “Horários”, “Agenda” e botão “Sair”. O link da rota atual usa fundo `#EFE7DE`, texto escuro em bold e `aria-current="page"`. Mobile empilha menu em coluna; `sm` e acima organiza em linha.
- Cabeçalho da plataforma exibe “BeautyTime · Plataforma”, link “Salões”, nome do usuário quando disponível e botão “Sair”.
- Badges de situação distinguem status ativo/confirmado dos inativos/cancelados; valores e nomes dentro dos cards são dados da API.
- Estados de carregamento são textos na posição do conteúdo. Erros aparecem em texto de alerta. Estados vazios usam painel com borda tracejada, mensagem e, onde implementado, próximo passo.

## `/`

**Objetivo/usuários:** entrada pública para clientes e administradores de salão.

**Ordem e conteúdo:**
1. Painel branco central com a marca “BeautyTime”.
2. Texto central: “Agende seu horário em poucos toques.”
3. Dois cards: “Sou cliente” / “Acesse sua conta global ou crie uma nova.” e “Sou administradora” / “Entre na sua empresa ou cadastre uma nova.”
4. Em cada card: botão “Entrar” e link “Criar conta”.
5. Texto: “Já tem o link de uma empresa? Acesse /agendar/identificador.”
6. Botão “Encontrar salões”.

**Ações/destinos:** Entrar cliente → `/clientes/login`; criar conta cliente → `/clientes/cadastro`; entrar administradora → `/admin/login`; criar conta empresa → `/admin/cadastro`; Encontrar salões → `/saloes`. O exemplo `/agendar/identificador` é texto explicativo, não botão.

**Layout/estilo:** shell centralizado, max-width 900 px; painel com borda, fundo branco, raio 16 px e sombra de card. Cards têm padding mobile 22 px, desktop 28 px, sombra tile, raio 16 px. Coluna no mobile; linha a partir de `md`; espaçamento principal `6`, cards `4`.

**Estados:** sem estado de carregamento, vazio ou erro próprio nesta tela.

**Responsividade:** conteúdo centralizado, 1 coluna em mobile, cards lado a lado a partir de `md`; botão Encontrar salões 100% no mobile.

## `/clientes/login`

**Objetivo/usuários:** cliente autentica para continuar agendamento ou consultar a área pessoal.

**Ordem:** link da marca “BeautyTime” → `/`; card com título “Entrar como cliente”; texto “Use a mesma conta em todas as empresas da plataforma.”; campos “E-mail” (tipo email, placeholder “voce@exemplo.com”) e “Senha” (password, placeholder “Sua senha”); área de erro; botão “Entrar”; link “Ainda não tem conta? Cadastre-se”.

**Ações:** submissão usa o login existente. Link de cadastro vai a `/clientes/cadastro`; quando a tela foi aberta pelo fluxo de agendamento, inclui `?retomar=agendamento`.

**Layout/estilo:** shell comum, card max-width 520 px, padding 24 px 20 px mobile / 36 px `md`; pilha alinhada à esquerda, spacing 4; marca e card empilhados com spacing 6. Heading Reflex 6 mobile / 8 `sm`.

**Estados:** durante envio, a interface padrão do formulário não possui rótulo de loading específico. Erros aparecem na área `role="alert"`: “Preencha todos os campos.”, “Informe seu e-mail e sua senha.”, “A API não retornou uma sessão válida.”, erros de credenciais/API como texto em português (`E-mail ou senha inválidos para este tipo de acesso.`, falha de conexão e demais respostas HTTP). A rota carrega sem tela de sucesso própria: sucesso redireciona ao destino do estado de autenticação ou retorna ao agendamento pendente.

**Responsividade:** card 100% da largura disponível até max-width 520 px; campos e botão 100%.

## `/clientes/cadastro`

**Objetivo/usuários:** criar conta de cliente, global e não vinculada a uma empresa.

**Ordem:** marca → título “Criar conta de cliente” → texto “Sua conta é global e não fica vinculada a uma empresa.” → campos “Nome” (text, “Seu nome”), “E-mail” (email, “voce@exemplo.com”), “Telefone” (tel, “(00) 00000-0000”), “Senha” (password, “Mínimo de 8 caracteres”, mínimo 8) → mensagem de erro → botão “Criar conta” → link “Já tem conta? Entrar”.

**Ações/destinos:** marca → `/`; o link de login aponta a `/clientes/login`; em continuação de agendamento, `?retomar=agendamento`.

**Layout/estilo:** mesmo formulário compartilhado: card 520 px, campos em coluna e botões 100%.

**Estados:** erro de campos obrigatórios: “Preencha todos os campos.”; outros erros podem mostrar “A conta não corresponde ao fluxo de acesso escolhido.”, “A conta de cliente possui um vínculo de empresa inválido.”, “A API não confirmou a criação da conta esperada.”, “A API não retornou uma sessão válida.”, erro de conexão/credenciais ou mensagem HTTP traduzida. Sucesso redireciona conforme estado existente; sem tela de sucesso separada.

**Responsividade:** igual a `/clientes/login`.

## `/admin/login`

**Objetivo/usuários:** autenticação da pessoa administradora do salão.

**Ordem:** marca → “Entrar como administradora” → “Acesse a conta vinculada à sua empresa.” → “E-mail” (email, “voce@exemplo.com”) → “Senha” (password, “Sua senha”) → mensagem de erro → “Entrar” → “Ainda não tem empresa? Cadastre-se”.

**Ações/destinos:** marca → `/`; cadastro → `/admin/cadastro`; sucesso → painel `/admin`.

**Layout/estilo:** formulário compartilhado max-width 520 px.

**Estados:** erro “Informe seu e-mail e sua senha.”; “A API não retornou uma sessão válida.”; credenciais inválidas: “E-mail ou senha inválidos para este tipo de acesso.”; “Muitas tentativas em pouco tempo. Aguarde e tente novamente.”; demais respostas HTTP/conexão traduzidas. Sem estado de sucesso persistente.

**Responsividade:** igual às outras páginas de autenticação.

## `/admin/cadastro`

**Objetivo/usuários:** cadastro de administradora e empresa.

**Ordem:** marca → “Cadastrar empresa” → “Crie sua conta administradora junto com a empresa.” → “Seu nome” (text, “Nome da administradora”) → “E-mail” (email, “voce@exemplo.com”) → “Senha” (password, “Mínimo de 8 caracteres”, mínimo 8) → “Telefone (opcional)” (tel, sem placeholder explícito) → “Nome da empresa” (text, “Nome do salão”) → “Endereço público da empresa” (text, placeholder de exemplo `salao-da-ana`, obrigatório) → ajuda “Exemplo: salao-da-ana” e erro de identificador → “Descrição (opcional)” (text area, “Conte um pouco sobre a empresa”) → “Localização (opcional)” → mensagem geral de erro → “Criar empresa e conta” → “Já tem conta administradora? Entrar”.

**Validação do identificador:** 3–40 caracteres, letras minúsculas, números e hífen, sem hífen nas extremidades nem consecutivos. Texto de formato: “Use de 3 a 40 caracteres: letras minúsculas, números e hífen, sem começar ou terminar com hífen.” Duplicado: “Este endereço já está em uso. Escolha outro.”

**Ações/destinos:** marca → `/`; login → `/admin/login`; sucesso → `/admin`.

**Layout/estilo:** formulário longo em uma coluna; max-width 520 px. A rolagem da página é vertical; campos ocupam largura do card.

**Estados:** erro geral “Preencha todos os campos obrigatórios.”, de formato/duplicidade do identificador, erro de acesso, resposta HTTP ou conexão. Não há tela de sucesso dedicada.

**Responsividade:** uma coluna em mobile e desktop; card e campos reduzem à largura disponível.

## `/admin`

**Objetivo/usuários:** painel inicial da administradora de salão.

**Ordem:**
1. Cabeçalho: marca, navegação “Painel”, “Serviços”, “Profissionais”, “Horários”, “Agenda”; “Sair”.
2. Card “Painel administrativo” e nome dinâmico da empresa.
3. Indicadores: “Agendamentos hoje”, “Agendamentos na semana”, “Faturamento estimado”, “Taxa de cancelamento”.
4. Card “Link público do salão”: link dinâmico `/agendar/[identificador]`, estado “Preparando o link público...” antes de disponível; botão “Copiar link”; mensagem de cópia.
5. Quatro cards de navegação: “Serviços” / “Cadastre e mantenha o catálogo da empresa.”; “Profissionais” / “Gerencie a equipe e os serviços realizados.”; “Horários” / “Configure os períodos semanais de cada profissional.”; “Agenda” / “Consulte os agendamentos por dia e profissional.”
6. Duas áreas: “Serviços mais agendados na semana” e “Próximos horários de hoje”.

**Ações:** cards levam a `/admin/servicos`, `/admin/profissionais`, `/admin/horarios` e `/admin/agenda`. “Copiar link” copia o link público; sem link, botão desabilitado. Navegação e Sair seguem destinos existentes.

**Layout/estilo:** max-width 820 px; blocos brancos com padding 20 px mobile / 26 px desktop, raio 16 px, borda e sombra tile. Grids de métricas 1 coluna → 2 em `sm` → 4 em `lg`; quatro cards de área em 1 → 2 colunas em `sm`. Loading “Carregando indicadores...”; falha dinâmica de API; detalhes vazios “Sem agendamentos nesta semana.” e “Não há próximos horários hoje.”

**Estados:** loading do dashboard, erro em alerta, link preparando, falha/cópia bem-sucedida (`“Link copiado.”`) ou falha (`“Não foi possível copiar. Selecione e copie o link exibido.”`). Cards de áreas têm hover/foco interativos.

**Responsividade:** navegação em coluna no mobile e linha em `sm`; cards em uma coluna no mobile.

## `/admin/servicos`

**Objetivo/usuários:** cadastrar e manter serviços do salão.

**Ordem:** cabeçalho administrativo → card “Serviços da empresa”, nome do salão e link público `/agendar/[identificador]` → card de formulário “Cadastrar serviço” ou “Editar serviço” → formulário “Nome” (text, “Ex.: Corte feminino”, 2–80 caracteres), “Duração” (select, placeholder “Selecione a duração”, opções de 15 a 480 minutos em passos de 15), “Preço (R$)” (number, “Ex.: 75,00”, mínimo 0, máximo 99999.99, passo 0.01) → erros e mensagem de sucesso → botão “Cadastrar serviço” ou “Salvar alterações”; em edição, botão “Cancelar edição” → seção “Catálogo” → cards de serviços.

**Card de serviço:** nome, badge “Ativo”/“Inativo”, duração formatada, preço, botão “Editar” e botão “Desativar”/“Reativar”.

**Estados:** loading “Carregando serviços...” e erro dinâmico; vazio “Sua empresa ainda não tem serviços cadastrados.” com botão “Cadastrar o primeiro serviço” que leva ao formulário `#service-form`. Os erros específicos de nome, duração e preço são mensagens inline; erros de API são apresentados em texto.

**Layout/estilo:** max-width 820 px; cabeçalho e formulário em painéis; lista em coluna. Cada card padding 18 px mobile / 22 px `sm`, raio 16 px, sombra tile. No mobile conteúdo do card empilha e ações ocupam largura total; a partir de `sm`, os botões ficam em linha.

## `/admin/profissionais`

**Objetivo/usuários:** gerenciar equipe e serviços realizados por cada profissional.

**Ordem:** cabeçalho administrativo → card “Profissionais da empresa” e nome do salão → card de formulário “Cadastrar profissional”/“Editar profissional” → aviso condicional “Cadastre um serviço ativo antes de criar um profissional.” → campo “Nome” (text, “Nome do profissional”) e erro inline → grupo “Serviços que realiza” com checkbox por serviço ativo; vazio “Não há serviços ativos para selecionar.” → erro geral e mensagem de sucesso → botão “Cadastrar profissional”/“Salvar alterações”; em edição “Cancelar edição” → seção “Equipe” → cards de profissionais.

**Card:** nome, badge “Ativo”/“Inativo”, serviços associados (ou “Nenhum serviço associado.”), botões “Editar” e “Desativar”/“Reativar”.

**Estados:** “Carregando profissionais...”; erro de API em alerta; vazio “Sua empresa ainda não tem profissionais cadastrados.” e botão “Cadastrar o primeiro profissional” (`#professional-form`). O cadastro fica desabilitado se não houver serviço ativo. Mensagens de sucesso são dinâmicas.

**Layout/estilo:** max-width 820 px; painéis em coluna; checklist vertical; cards com padding 18 px / 22 px em `sm`. Conteúdo e ações empilham no mobile, em linha a partir de `sm`.

## `/admin/horarios`

**Objetivo/usuários:** definir períodos semanais de atendimento por profissional.

**Ordem:** cabeçalho administrativo → card “Horários de atendimento”, nome da empresa e select “Profissional” (placeholder “Selecione um profissional”) → card de formulário “Cadastrar período” ou “Editar período” → criação: campo de dias, checkbox “Todos os dias” e checkboxes “Segunda-feira” a “Domingo”; edição: select “Dia da semana” → campos “Início” (text, `09:00`) e “Término” (text, `18:00`; também permite `24:00`) → ajuda “Use o formato HH:MM. Para encerrar à meia-noite, use 24:00.” → erros/sucesso → botão “Cadastrar período”/“Salvar alterações”; em edição “Cancelar edição” → seção “Períodos semanais” → cards com dia, intervalo e ações “Editar” e “Remover”.

**Estados:** loading “Carregando horários...”; se não houver profissional ativo: “Cadastre e ative um profissional antes de configurar horários.”; vazio por profissional: “Este profissional ainda não tem períodos de atendimento. Cadastre um período no formulário acima.”; erros incluem seleção de profissional/dia inválidos e conflito de períodos sobrepostos (nomeia o dia; cadastro em lote informa “Nenhum período foi cadastrado.”). Sucesso indica período cadastrado/atualizado/removido.

**Layout/estilo:** max-width 820 px; card superior e formulário padding 20 px mobile / 26 px `sm`, raio 16 px; horários em lista vertical. Campos início/término em coluna no mobile e linha em `sm`; dias em grid 2 → 4 colunas.

## `/admin/agenda`

**Objetivo/usuários:** consulta da agenda da empresa por dia e profissional.

**Ordem:** cabeçalho administrativo → card “Agenda do salão” e nome da empresa → campo “Dia” (date) → select “Profissional” (placeholder “Todos os profissionais”) → resultados.

**Card de agendamento:** serviço, horário inicial, badge “Agendado”/“Cancelado”, “Cliente: [nome]”, “Profissional: [nome]”, “Término: [horário]”; se tardio, callout “Cancelamento tardio”.

**Estados:** “Carregando agenda...”; erro dinâmico; vazio “Não há reservas para este dia e filtro.” e “Selecione outra data ou outro profissional.”

**Layout/estilo:** max-width 820 px; filtros em coluna no mobile e linha a partir de `sm`; card do filtro padding 20/26 px; resultados em coluna, cards brancos com padding 18/22 px e raio 16 px.

## `/meus-agendamentos`

**Objetivo/usuários:** cliente consulta agendamentos próximos e passados e pode cancelar os elegíveis.

**Ordem:** marca → botão “Sair” → painel “Meus agendamentos”; saudação condicional “Olá, [nome].”; botão “Novo agendamento” e link “Encontrar salões” → política de cancelamento → aviso de operação, se houver → “Próximos” e “Passados” com listas de cards.

**Card de agendamento:** nome do serviço, data/hora, badge “Agendado”/“Cancelado”, empresa e profissional, duração e preço; se cancelamento tardio, “Cancelamento tardio: taxa informativa de R$ 5,00.” Ações condicionais “Agendar de novo” e “Cancelar agendamento”.

**Modal de cancelamento:** título “Cancelar agendamento” ou “Cancelamento tardio”; identificação do agendamento; para cancelamento tardio: “Faltam menos de 8 horas para o início. O cancelamento será marcado como tardio, com taxa apenas informativa de R$ 5,00. Nenhum pagamento é processado.”; caso contrário: “O cancelamento é gratuito porque faltam 8 horas ou mais para o início.”; botões “Manter agendamento” e “Confirmar cancelamento”/“Confirmar cancelamento tardio”.

**Ações/destinos:** Novo agendamento e Encontrar salões → `/saloes`; Agendar de novo abre `/agendar/[identificador]`; Sair encerra sessão. Após cancelar, pode aparecer “Agendamento cancelado. O cancelamento foi registrado como tardio.” ou “Agendamento cancelado sem taxa.”; caso deixe de ser cancelável: “Este agendamento não pode mais ser cancelado.”

**Estados:** “Carregando agendamentos...”; vazio próximos: “Você não tem agendamentos futuros. Use “Novo agendamento” para encontrar um salão.”; vazio passados: “Nenhum agendamento passado.”; erro: “Sua sessão expirou. Entre novamente.” ou “Não foi possível carregar seus agendamentos.”; erro de cancelamento aparece no diálogo.

**Layout/estilo:** max-width 720 px; blocos em coluna, spacing 5; cards com conteúdo empilhado no mobile; ações em coluna no mobile e linha em `sm`.

## `/saloes`

**Objetivo/usuários:** cliente encontra empresas públicas que aceitam reservas.

**Ordem:** marca; link condicional “Meus agendamentos” para cliente autenticada → painel “Encontrar salões” e texto “Escolha um salão para ver os serviços e agendar seu horário.” → painel de filtros: campo de busca “Nome do salão” (search) e campo “Nome do serviço” (text), botão “Buscar” → estado/lista de salões.

**Card do salão:** nome, botão “Agendar”, localização se informada, título “Serviços ativos”; lista com nome, duração e preço. Sem serviço no card: “Nenhum serviço disponível no momento.”

**Estados:** “Carregando salões...”; erro “Não foi possível carregar os salões. Recarregue a página para tentar novamente.” ou “A lista de salões veio em formato inválido. Recarregue a página para tentar novamente.”; vazio “Ainda não há salões disponíveis para agendamento. Tente novamente mais tarde ou acesse pelo link direto da empresa.”

**Layout/estilo:** max-width 720 px; header e painéis em coluna, spacing 5; filtros empilhados no mobile e em linha a partir de `md`; cards empilhados; botão Agendar ocupa 100% no mobile e largura automática em `sm`.

## `/boas-vindas`

**Objetivo/usuários:** compatibilidade de navegação após entrada de cliente.

**Comportamento:** não apresenta conteúdo próprio. Redireciona imediatamente para `/meus-agendamentos`, que requer sessão da cliente. O destino pode redirecionar para `/clientes/login` se não houver autenticação válida.

**Layout/estados:** nenhum layout nem estado visual próprio.

## `/agendar/{identificador}` — página e cabeçalho do fluxo

**Objetivo/usuários:** cliente vê a página pública do salão e inicia uma reserva.

**Ordem:** marca → link condicional “Meus agendamentos” se autenticada → card de até 720 px. Salão encontrado: nome da empresa e “Escolha o serviço, o profissional, o dia e o horário para fazer seu agendamento.”; em seguida etapas progressivas. Identificador inválido/não encontrado: título “Empresa” e mensagem de situação.

**Estados da página:** “Empresa não encontrada”; “Não foi possível carregar os dados públicos da empresa.”; “Não foi possível carregar os dados públicos.”. Serviços: loading, erro “Não foi possível carregar os serviços desta empresa.” ou vazio com próximo passo (“Esta empresa ainda não tem serviços disponíveis.” / “Entre em contato com o salão para saber quando novos serviços estarão disponíveis.”).

**Layout:** shell comum e card de conteúdo max-width 720 px; seleção vertical; cada etapa usa divisor, título e conteúdo com spacing 3–4. A página e todos os controles ocupam largura disponível.

### Etapa 1 — Serviço

Título “1. Serviço”. Cada tile mostra nome, duração e preço e botão “Escolher”/“Selecionado”. Seleção recebe borda 2 px principal. Tiles em coluna, padding 16 px mobile / 20 px `sm`.

**Estados:** “Carregando serviços...”; erro de serviços; vazio explicado acima.

### Etapa 2 — Profissional

Surge após selecionar serviço. Título “2. Profissional”. Opções são botões com nomes recebidos da API, incluindo “Sem preferência”. A opção atual tem aparência de selecionada.

**Estados:** “Carregando profissionais...”; erros: “Não foi possível carregar os profissionais deste serviço.”, “Este serviço não está mais disponível.” ou “Nenhum profissional realiza este serviço no momento. Escolha outro serviço ou entre em contato com a empresa.”

### Etapa 3 — Dia e horário

Surge após selecionar profissional. Título “3. Dia e horário”; texto “Escolha um dia entre hoje e os próximos 30 dias. Dias riscados não têm horários livres.”; calendário em grid de dias com abreviação e data; dias indisponíveis aparecem riscados e desabilitados. Após escolher dia, opções de horário em botões.

**Estados:** “Carregando dias disponíveis...”, “Carregando horários...”; erros de carregamento são mensagens de alerta da API. Sem horários: “Dia indisponível: não há horários livres. Escolha outro dia.” Dia disponível permite selecionar somente uma opção retornada.

### Etapa 4 — Confirmação

Surge após selecionar horário. Título “4. Confirmação”; resumo “[serviço] · [duração] · [preço]”, “Profissional: [nome ou Sem preferência resolvida]”, “Dia [data] às [horário]”; callout com política: “Cancelamento gratuito com 8 horas ou mais de antecedência. Com menos de 8 horas, o cancelamento fica marcado como tardio, com taxa apenas informativa de R$ 5,00. Nenhum pagamento é processado pelo BeautyTime.”

Cliente autenticada: botão “Confirmar agendamento”, que pode indicar loading durante envio. Sem autenticação: texto “Entre ou crie sua conta de cliente para confirmar. Suas escolhas serão mantidas.” e botões “Entrar para confirmar” e “Criar conta”; abrem as rotas de autenticação com continuação do agendamento.

**Estados:** conflito/indisponibilidade de horário apresenta mensagem no callout; exemplo: “A reserva não foi concluída: o horário pode ter ficado indisponível. Escolha outro horário.” Se reserva foi aceita mas não houve resumo: “A reserva foi registrada, mas não foi possível exibir o resumo. Confira em Meus agendamentos.”

### Sucesso da reserva

Callout “Agendamento confirmado!”; card com nome do serviço, data/hora, “Empresa: [nome]”, “Profissional: [nome]”, “Duração: [duração] · Preço: [preço]”; política de cancelamento; botão “Ver meus agendamentos” → `/meus-agendamentos`; botão “Fazer outro agendamento” reinicia fluxo na mesma empresa.

## `/platform/login`

**Objetivo/usuários:** administrador da plataforma entra na área interna, separado do acesso do salão.

**Ordem:** formulário central com “Acesso da plataforma”; “Entre com a conta administradora da plataforma.”; campo “E-mail” (email, sem placeholder explícito); “Senha” (password); erro condicional; botão “Entrar” ou “Entrando...” enquanto autentica.

**Ações:** autenticação válida redireciona a `/platform`. Cabeçalho interno não é apresentado na tela de login.

**Estados de erro:** “Informe seu e-mail e sua senha.”; “E-mail ou senha inválidos para o acesso à plataforma.”; “A API não retornou uma sessão válida.”; “Esta conta não tem acesso ao painel da plataforma.”; “Entre com uma conta administradora da plataforma.”; demais falhas aparecem em português com status HTTP/conexão.

**Layout/estilo:** shell comum; formulário max-width 480 px, padding 28 px, fundo branco, borda, raio 16 px e sombra card; coluna e spacing 4.

**Responsividade:** campos/botão 100%; largura máxima 480 px.

## `/platform`

**Objetivo/usuários:** administrador da plataforma pesquisa e abre salões.

**Ordem:** cabeçalho “BeautyTime · Plataforma”, link ativo “Salões”, nome do usuário, botão “Sair” → título “Salões” → formulário em painel: “Buscar por nome” (search, placeholder “Nome do salão”) e “Filtrar por serviço ativo” (text, placeholder “Nome do serviço”), botão “Buscar” → loading, erro, vazio ou resultados.

**Card do salão:** nome, localização, badges “Serviços: [n]”, “Profissionais: [n]”, “Agendamentos: [n]”. Toda superfície é link para `/platform/saloes/{id}`.

**Estados:** “Carregando salões...”; erro dinâmico; vazio “Nenhum salão corresponde aos filtros.” e “Revise os termos ou tente uma busca diferente.”

**Layout/estilo:** max-width 1100 px; painel e cards brancos com raio 16 px; formulário em 1 coluna no mobile e 2 em `md`; resultados 1 coluna mobile / 2 em `md`; spacing principal 5.

## `/platform/saloes/{id}`

**Objetivo/usuários:** administrador da plataforma consulta e edita dados do salão, catálogo, profissionais e indicadores.

**Ordem:**
1. Cabeçalho “BeautyTime · Plataforma”, “Salões” (ativo), usuário e “Sair”.
2. Loading “Carregando dados do salão...” ou erro “Não foi possível abrir o salão”, detalhe do erro e link “Voltar para salões”.
3. Se encontrado: título dinâmico do salão.
4. Indicadores: “Agendamentos hoje”, “Agendamentos na semana”, “Faturamento estimado”, “Taxa de cancelamento”.
5. Cards “Serviços mais agendados na semana” e “Próximos horários de hoje”, com itens de serviço/quantidade e horário/serviço/profissional.
6. Mensagem de sucesso e erro de edição se houver.
7. Abas “Dados do salão”, “Serviços” e “Profissionais”; a ativa recebe visual sólido.
8. Conteúdo da aba:
   - **Dados do salão:** heading “Dados do salão”; botão “Editar”; leitura “Nome:”, “Descrição:”, “Localização:” e “Identificador público:”. Editando, campos “Nome”, “Descrição”, “Localização”, botões “Salvar” e “Cancelar”.
   - **Serviços:** cards com nome, badge “Ativo”/“Inativo”, “Duração: [n] min”, “Preço: [valor]”, botão “Editar”. Edição: “Nome”, “Duração (minutos)”, “Preço (centavos)”, checkbox “Serviço ativo”, botões “Salvar” e “Cancelar”.
   - **Profissionais:** cards com nome, badge “Ativo”/“Inativo”, botão “Editar”. Edição: “Nome”, checkbox “Profissional ativo”, botões “Salvar” e “Cancelar”.

**Estados:** dashboard vazio: “Sem agendamentos nesta semana.” e “Não há próximos horários hoje.”; listas vazias: “Este salão ainda não tem serviços.” / “Cadastre os serviços pelo painel do salão.” e “Este salão ainda não tem profissionais.” / “Cadastre os profissionais pelo painel do salão.” Erro de id: “Identificador do salão inválido.”; 404: “Salão não encontrado.”; erros de API variam com status. Sucessos: “Dados do salão atualizados.”, “Serviço atualizado.”, “Profissional atualizado.”; validação: “O nome do salão não pode ficar vazio.” e “Informe duração e preço usando números inteiros.”

**Layout/estilo:** max-width 1100 px; indicadores 1 → 2 colunas em `sm` → 4 em `lg`; detalhes 1 → 2 em `md`; cards e abas empilham ou quebram linha conforme largura; spacing principal 5.

## Rotas registradas

| Rota | Título do documento | Carregamento inicial |
|---|---|---|
| `/` | BeautyTime | Página inicial |
| `/clientes/cadastro` | Criar conta de cliente | Preserva continuação de agendamento quando aplicável |
| `/clientes/login` | Entrar como cliente | Preserva continuação de agendamento quando aplicável |
| `/admin/cadastro` | Cadastrar empresa | Limpa mensagem anterior |
| `/admin/login` | Entrar como administradora | Limpa mensagem anterior |
| `/admin` | Painel administrativo | Carrega painel |
| `/admin/servicos` | Serviços da empresa | Carrega serviços |
| `/admin/profissionais` | Profissionais da empresa | Carrega profissionais |
| `/admin/horarios` | Horários de atendimento | Carrega horários |
| `/admin/agenda` | Agenda do salão | Carrega agenda |
| `/meus-agendamentos` | Meus agendamentos | Carrega agendamentos da cliente |
| `/saloes` | Encontrar salões | Carrega diretório público |
| `/boas-vindas` | Meus agendamentos | Redireciona para `/meus-agendamentos` |
| `/agendar/[identificador]` | Página pública da empresa | Carrega empresa e serviços |
| `/platform/login` | Acesso da plataforma | Verifica sessão de plataforma |
| `/platform` | Salões da plataforma | Carrega pesquisa/lista |
| `/platform/saloes/[account_id]` | Detalhe do salão | Carrega dados e indicadores do salão |
