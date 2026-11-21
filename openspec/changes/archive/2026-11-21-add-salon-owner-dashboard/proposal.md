# Proposal

## Why

O painel inicial da administradora do salão não mostra indicadores, embora a plataforma já calcule essas métricas para o painel da plataforma. Exibir os mesmos números para a administradora facilita acompanhar a operação, desde que o backend derive a empresa exclusivamente da identidade autenticada e impeça acesso aos dados de outros salões.

## What Changes

- Extrair o cálculo atual do dashboard da plataforma para uma função reutilizável que recebe `account_id`, mantendo sem alteração a resposta de `GET /platform/accounts/{account_id}/dashboard`.
- Criar `GET /admin/dashboard`, protegido por `authorize_admin`, que determina o salão pelo usuário autenticado e retorna as mesmas métricas.
- Atualizar `/admin` para apresentar indicadores e próximos horários do dia acima do link público do salão, formatando valores monetários em reais.
- Preservar os dados e comportamentos existentes do painel da plataforma.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `admin-dashboard`: substituir a restrição de não exibir indicadores por requisitos para apresentar as métricas e próximos horários da própria empresa à administradora autenticada.

## Impact

- Backend Xano: função reutilizável para calcular métricas e novo endpoint `GET /admin/dashboard`.
- Frontend Reflex: estado, carregamento, exibição de indicadores e próximos horários na página `/admin`; reutilização de `formatting.py`.
- Contrato existente: a resposta do endpoint de dashboard da plataforma deve permanecer igual.

Fora do escopo: qualquer mudança visual ou funcional em `/platform`, `/saloes`, área da cliente e fluxo de agendamento; novas métricas, relatórios ou alterações de tabelas.
