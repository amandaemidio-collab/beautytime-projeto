# Proposal

## Why

As páginas atuais usam estilos e cores inconsistentes, com tipografia pouco hierarquizada e espaçamento que pode cortar conteúdo em telas estreitas. Um design system centralizado deve tornar a experiência mais clara, acessível e coerente em toda a jornada, sem mudar o comportamento do app.

## What Changes

- Consolidar tokens, tipografia, layout responsivo, campos, botões, cards, badges e estados visuais em `frontend/frontend/theme.py`.
- Aplicar o design system às páginas da cliente, administradora do salão e administradora da plataforma, incluindo autenticação, busca de salões, agendamento e painéis.
- Adotar a paleta neutra indicada, tipografia Inter e Playfair Display, superfícies e controles arredondados e sombras discretas.
- Garantir contraste WCAG AA para texto. Usar variantes de texto mais escuras nos fundos claros quando as cores literais da paleta não alcançarem 4,5:1; reservar o detalhe `#C8A27A` para decoração ou combiná-lo com texto escuro.
- Melhorar adaptação mobile, respiro lateral, legibilidade de títulos, estados de carregamento/erro/lista vazia e destaque visual da navegação ativa.
- Tornar os quatro cards existentes do painel do salão claramente clicáveis, mantendo seus destinos atuais.
- Conferir visualmente todas as rotas no servidor Reflex já em execução, sem iniciar outra instância.

Não serão alterados rotas, endpoints, chamadas de API, regras de negócio, autenticação ou fluxo de agendamento; não haverá publicação no Xano.

## Capabilities

### New Capabilities

- `visual-design-system`: apresentação consistente, responsiva e acessível das páginas BeautyTime.

### Modified Capabilities

Nenhuma.

## Impact

- Frontend Reflex: `frontend/frontend/theme.py`, `frontend/frontend/frontend.py`, `frontend/frontend/platform_panel.py` e, se necessário para configuração visual global, `frontend/rxconfig.py`.
- Verificação: compilação Reflex existente e inspeção visual das rotas servidas em `http://localhost:3000`; não iniciar um novo servidor.
- Nenhuma alteração ao backend Xano, banco de dados ou dependências funcionais.
