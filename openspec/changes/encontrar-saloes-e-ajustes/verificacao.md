# Verificação — encontrar salões e ajustes

## 1.1 / 1.2 — Rota `GET companies/public` (grupo `Members & Accounts`)

- XanoScript validado pelo Xano Developer MCP (`xano_validate_xanoscript`): válido.
- Dry-run com somente o arquivo novo (`-i api/members_accounts/companies/public_GET.xs`): 1 rota criada, nada alterado ou removido. Push feito em 25/10/2026 após confirmação da responsável pelo projeto.
- O push exibiu o aviso “table professional_service does not exist” (o push parcial não envia a tabela). Conferido em seguida: a rota responde com dados reais, e um novo dry-run do arquivo retorna “No changes to push”, ou seja, a consulta publicada é a completa, sem placeholder.

Chamadas HTTP reais em 25/10/2026, com três empresas fictícias criadas pelo cadastro (`dir-c1-f5ea46`, `dir-c2-f5ea46`, `dir-c3-f5ea46`), respeitando no máximo 8 chamadas a cada 20 segundos:

| Verificação | Resultado |
|---|---|
| Responde 200 sem sessão | ok |
| Empresa com 2 serviços ativos e 2 profissionais ativos vinculados aparece uma única vez | ok |
| Empresa com serviço ativo cujo único profissional está inativo não aparece | ok |
| Empresa com profissional ativo vinculado só a serviço inativo não aparece | ok |
| Cada item tem somente `name` e `public_identifier` | ok |
| Ordem alfabética por nome, sem diferenciar maiúsculas | ok |
| Nenhum identificador repetido | ok |
| Ao reativar o profissional, a empresa volta à lista | ok |

## 2 a 4 — Frontend: checagens automáticas (antes da verificação manual)

Feitas em 25/10/2026 com `reflex compile --dry` (44 páginas, sem erro), renderização dos componentes em Python e uma instância isolada do app em modo produção (cópia em diretório temporário, porta própria), medida com Chrome headless e emulação de viewport via protocolo de depuração (390×844 e 1280×900).

| Verificação | Resultado |
|---|---|
| `/saloes` carrega a lista real da rota, sem sessão | ok |
| Lista inválida (identificador fora do formato) vira mensagem de erro, sem lista parcial; falha 500 mostra erro; lista vazia mostra estado vazio | ok |
| “Agendar” e “Agendar de novo” limpam as escolhas anteriores do salão antes de abrir `/agendar/{identificador}`; identificador inválido não navega | ok |
| Causa das margens: `padding` responsivo como dicionário gerava CSS inválido (`.css-… padding { }`) nos estilos compartilhados de página, cartão e painel | confirmada |
| Após trocar por `rx.breakpoints`: página com `padding` 28px 16px no celular e 56px 24px no desktop, conteúdo com 358 px de 390 px | ok |
| `/agendar/{identificador}`, `/saloes`, `/clientes/login` e “Empresa não encontrada” sem elemento fora da tela e sem rolagem horizontal, no celular e no desktop | ok |
| Texto introdutório da página pública: “Escolha o serviço, o profissional, o dia e o horário para fazer seu agendamento.”; nenhum “em breve” | ok |

## Ajustes finais

- `docs/project-overview.md` descreve a lista pública de salões como as empresas que aceitam reservas, igual ao `docs/domain-model.md`.
- Cartão de serviço da página pública: espaçamento interno aplicado com o novo `TILE_STYLE` de `theme.py` (padding com `rx.breakpoints`: 16px no celular, 20px a partir de 48em). Conferido na instância isolada, em 390×844 e 1280×900: texto e botão afastados da borda, borda de seleção mantida, sem rolagem horizontal.
- Os demais usos de dicionário responsivo em propriedades CSS (por exemplo, larguras de botões) continuam fora do escopo.

## 2.1 a 5.1 — Verificação manual no navegador

Feita pela responsável pelo projeto em 25/10/2026, em desktop e celular. Todos os cenários passaram:

| Verificação | Resultado |
|---|---|
| `/saloes` com a lista e o botão “Agendar” | ok |
| “Novo agendamento” em `/meus-agendamentos` | ok |
| “Agendar de novo” em `/meus-agendamentos` | ok |
| Margens e texto novo na página pública | ok |
| Margens nas demais telas | ok |
| Agendamento com login no meio do fluxo | ok |
| Cancelamento | ok |

O espaçamento interno do cartão de serviço foi aplicado depois dessa verificação e conferido apenas pelas capturas da instância isolada.
