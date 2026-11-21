# Design

## Context

O dashboard da plataforma já agrega as métricas semanais e os próximos horários usando o fuso `America/Sao_Paulo`. O endpoint administrativo de catálogo autentica a sessão com `Catalogo/authorize_admin`, que retorna o `account_id` da própria administradora. A página Reflex `/admin` atualmente carrega a identidade e o catálogo e apresenta o link público, mas não consome métricas.

## Goals / Non-Goals

**Goals:**
- Reutilizar o mesmo cálculo e o mesmo formato de métricas nos dashboards da plataforma e do salão.
- Obter a conta do endpoint de salão exclusivamente da autorização da sessão.
- Exibir indicadores, preços em reais e próximos horários no painel inicial da administradora.

**Non-Goals:**
- Alterar métricas, filtros, conteúdo ou interface do painel `/platform`.
- Adicionar tabelas, dependências ou novos conceitos de métricas.
- Alterar `/saloes`, a área da cliente ou o fluxo de agendamento.

## Decisions

- Extrair o cálculo atual para uma função Xano reutilizável que recebe `account_id` e retorna o mesmo objeto com `appointments_today`, `appointments_week`, `estimated_revenue_cents`, `cancellation_rate`, `top_services` e `upcoming_today`. Manter na rota `/platform` a autorização `authorize_platform_admin` e a validação de existência do salão; depois delegar o cálculo à função.
- Criar `GET /admin/dashboard` com autenticação de usuário e `Catalogo/authorize_admin`. O valor retornado pela autorização é a única origem do `account_id`; a rota não declara parâmetro de conta. A função compartilhada recebe esse valor e fornece as métricas. Isso evita duplicar a regra de cálculo e evita confiar em identificadores enviados pelo cliente.
- No Reflex, carregar o dashboard no evento que já prepara a página `/admin`, usando o token existente e o endpoint `/admin/dashboard`. Validar a resposta antes de atualizar o estado para evitar renderizar payload parcial ou inválido.
- Reutilizar `price_label`/`formatting.py` para converter `estimated_revenue_cents` para reais. Mostrar cards de indicadores e uma lista compacta dos próximos horários, posicionados antes do card “Link público do salão”, mantendo o restante da página.
- Preservar as definições que já existem no endpoint da plataforma: horários e limites da semana calculados em `America/Sao_Paulo`; agendamentos de hoje contam somente os não cancelados; total semanal e ranking de serviços consideram todos os agendamentos da semana; faturamento soma apenas os não cancelados; a taxa é cancelados/total e vale zero sem agendamentos; próximos horários são os cinco primeiros futuros de hoje, não cancelados, em ordem de início.

Alternativa considerada: copiar as consultas e fórmulas para o endpoint `/admin/dashboard`. Foi rejeitada porque permitiria divergência entre os dois painéis e quebraria a manutenção da definição única das métricas.

## Risks / Trade-offs

- [O formato da função compartilhada pode diferir do retorno atual da rota] → manter o mesmo objeto e testar a resposta da rota de plataforma antes e depois da extração.
- [A sessão ou resposta do novo endpoint pode expirar ou vir inválida] → manter os dados em estado vazio durante a carga, apresentar erro explícito e não exibir métricas parciais.
- [Uma regressão pode cruzar dados de empresas] → a rota de salão não aceita `account_id` de entrada e obtém a conta exclusivamente de `authorize_admin`; validar também tentativa com outra conta.
- [Valores e horários podem ser exibidos em unidades/formato incorretos] → reutilizar o formatador existente e verificar casos de preço em centavos e horários locais.

## Migration Plan

Não há migração de dados. Publicar a função e as rotas Xano validadas após revisão do dry-run; então entregar a interface Reflex que consome a rota de salão. Para rollback, reverter a interface e restaurar a implementação anterior do endpoint da plataforma; remover a rota de salão e a função compartilhada somente se não houver outros consumidores.
