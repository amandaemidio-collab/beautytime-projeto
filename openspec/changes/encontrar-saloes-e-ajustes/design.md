# Design

## Context

Consulte [proposal.md](./proposal.md) para motivação e as specs delta em `specs/` para os contratos observáveis.

Estado atual relevante:

- A tabela `account` não tem campo de situação. O `docs/domain-model.md` descreve empresa "ativa ou inativa" e uma lista pública de empresas ativas, mas nada disso existe no backend. Por decisão da responsável pelo projeto, "empresa ativa" passa a significar empresa que aceita reservas.
- `service` e `professional` têm `is_active`; o vínculo fica em `professional_service`. As rotas públicas existentes (`Agenda/public/{identifier}/...`) já combinam esses três para decidir elegibilidade.
- A consulta pública de empresa por identificador fica no grupo `Members & Accounts` (`company/public`) e retorna só nome e identificador.
- `client/appointments` (GET) já retorna `public_identifier` de cada agendamento, e o frontend já guarda esse valor em cada item da lista. "Agendar de novo" não precisa de mudança no backend.
- A página `/agendar/{identificador}` usa `PAGE_STYLE` como as demais, mas coloca todo o fluxo dentro de um cartão com `CARD_STYLE` (padding próprio e `max_width`) dentro de um `vstack` com `max_width="720px"`, num contêiner `display: flex`. As telas da cliente usam blocos `_panel` sem esse cartão externo. O código atual já exibe "Agende seu horário em poucos toques."; o texto de "em breve" não existe no código nem no build local `.web`.

## Goals / Non-Goals

**Goals:**

- Calcular no backend quais empresas aceitam reservas, com a mesma noção de elegibilidade das rotas de disponibilidade (serviço ativo + profissional ativo vinculado, ambos da mesma empresa).
- Reaproveitar os padrões de página e de painel já existentes no Reflex.

**Non-Goals:**

- Considerar horários semanais ou vagas livres na definição de "aceita reservas" (uma empresa com serviço e profissional ativos, mas sem períodos, aparece na lista).
- Cache, paginação ou ordenação configurável da lista.

## Decisões

### Rota pública `companies/public` no grupo `Members & Accounts`

Criar `GET companies/public`, sem autenticação e sem entradas, que consulta `professional_service` com junção a `service` e `professional`, filtrando `service.is_active`, `professional.is_active` e `service.account_id == professional.account_id`. Do resultado, obter os `account_id` distintos, buscar as empresas e responder somente `{name, public_identifier}` ordenado por nome. A sintaxe de junção, distinct e ordenação deve ser confirmada no Xano Developer MCP antes de escrever o XanoScript.

**Alternativas consideradas:** colocar a rota no grupo `Agenda` (as regras de elegibilidade estão lá, mas a consulta pública de empresa já vive em `Members & Accounts`); adicionar `is_active` em `account` (descartado pela responsável, exigiria ainda um controle de desativação); filtrar no frontend a partir de outra consulta (violaria a regra de manter regras de negócio no backend).

### Tela pública `/saloes`

Adicionar a página `/saloes` ("Encontrar salões"), pública, com o mesmo cabeçalho de marca das telas da cliente e um `_panel` por salão contendo o nome (com `overflow_wrap="anywhere"`) e um botão "Agendar" que aponta para `/agendar/{identificador}`. O carregamento ocorre no `on_load`, com estados de carregamento, vazio e erro como nas demais listas. Itens sem nome ou identificador em formato válido (`IDENTIFIER_PATTERN`) são tratados como resposta inválida.

**Alternativas consideradas:** colocar a lista dentro de `/meus-agendamentos` (a tela é pública por decisão da responsável e deve funcionar sem sessão).

### Botões na área da cliente

"Novo agendamento" fica no painel do topo de `/meus-agendamentos`, como link para `/saloes`. "Agendar de novo" entra em `_client_appointment_card` como link para `/agendar/{public_identifier}` do item, ao lado do botão de cancelar quando ele existir. Ao abrir a página pública por esse link, o fluxo começa do zero: `load_public_company` já reinicia as escolhas quando não há retomada pendente para a mesma empresa.

### Layout da página pública

Alinhar `public_company_page` à estrutura das telas da cliente: manter `PAGE_STYLE` e a largura máxima de 720px, substituir o cartão externo com `CARD_STYLE` por `_panel`, e garantir `min_width="0"` e `width="100%"` nos contêineres flexíveis para que conteúdos largos (grade de dias, botões de horário, nomes longos) quebrem linha em vez de forçar largura maior que a tela. A causa exata do corte deve ser confirmada no navegador antes do ajuste, comparando com `/meus-agendamentos` no mesmo viewport.

## Riscos / Trade-offs

- [A lista inclui empresas sem períodos semanais, que não terão horários livres] → Aceito pela definição escolhida; a página do salão já mostra dias indisponíveis. Pode ser refinado numa change futura.
- [A lista cresce sem paginação] → Aceitável para o porte acadêmico do projeto; registrado como fora do escopo.
- [Empresas de teste aparecem na lista pública] → São dados do workspace de desenvolvimento; não há mudança de código para isso.
- [O texto de "em breve" relatado pode vir de uma versão antiga do app em execução] → Reiniciar o app Reflex antes da verificação manual e conferir o texto no celular e no desktop.
- [Um ajuste de layout na página pública pode afetar o fluxo de agendamento] → Percorrer o fluxo completo, incluindo retomada após login e confirmação, após o ajuste.

## Plano de migração

1. Consultar a documentação no Xano Developer MCP, escrever a rota e validá-la pelo MCP.
2. Executar `xano workspace push --dry-run`, apresentar o resultado e aguardar confirmação explícita antes do push.
3. Implementar as telas no Reflex e verificar manualmente em celular e desktop.
4. Rollback: remover a rota nova e a página `/saloes`; não há dados nem tabelas novas.
