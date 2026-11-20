# Design

## Context

O Xano já tem `user.role = "platform_admin"` e `authorize_platform_admin`. O endpoint `auth/me` hoje aceita apenas `client` sem empresa ou `admin` com empresa, portanto precisa reconhecer também a identidade de plataforma para que o Reflex valide a sessão.

O frontend Reflex concentra rotas, estado e chamadas à API em `frontend/frontend/frontend.py`, com transporte JSON em `frontend/frontend/api_client.py` e URLs de grupos em `frontend/frontend/api_config.py`. Hoje `/admin/login` e `/admin` pertencem às administradoras de salão.

Veja `proposal.md` e as especificações para o escopo funcional e as regras dos indicadores.

## Goals / Non-Goals

**Goals:**

- Adicionar um fluxo de plataforma separado tanto na API quanto na interface.
- Reutilizar o mecanismo de sessão, o cliente HTTP, a autorização existente e os validadores de dados do catálogo sempre que adequado.
- Manter os dados multiempresa coerentes: descobrir o salão afetado a partir do registro editado e usá-lo também no log de auditoria.
- Fazer com que cada edição e sua linha de auditoria sejam confirmadas como uma única operação.

**Non-Goals:**

- Mover, renomear ou substituir páginas e endpoints existentes para administradoras de salão.
- Criar um cadastro público de `platform_admin`.
- Adicionar dependências de frontend ou alterar tabelas existentes.
- Enviar alterações ao workspace Xano sem confirmação expressa após o dry-run.

## Decisions

- Criar o endpoint de login na API Authentication, espelhando o fluxo de `auth/admin/login`, mas exigindo `role = "platform_admin"` e `account_id = null`.
- Atualizar a validação de identidade de `auth/me` para aceitar a combinação `platform_admin` sem empresa. Isso é necessário porque o frontend valida a sessão buscando a identidade atual após o login e ao abrir rotas protegidas.
- Criar um grupo/API de plataforma para as seis rotas pedidas. Cada endpoint sob `/platform` exigirá autenticação Xano e chamará `authorize_platform_admin` antes de consultar ou editar registros.
- Nas consultas, filtrar serviços, profissionais e agendamentos pelo `account_id` relacionado ao salão consultado. Os contadores da lista contam todos os registros; o filtro por serviço considera somente serviços ativos.
- Calcular os limites de dia e semana no fuso `America/Sao_Paulo`. A semana começa segunda-feira e termina domingo; faturamento soma `service_price_cents` de agendamentos não cancelados. Usar `appointment.service_name` para preservar o nome histórico na classificação de serviços.
- Para cada PATCH, carregar o registro antes da edição, aceitar somente os campos listados na especificação, aplicar as validações já existentes e guardar em `event_log.metadata` os campos alterados com valores anteriores e novos. A edição e o evento devem ficar na mesma transação para não confirmar uma alteração sem auditoria.
- Descobrir o `account_id` do serviço ou profissional pela própria linha, sem confiar em empresa enviada pelo frontend. Para edição de conta, usar o `account_id` do caminho.
- Usar `/platform/login`, `/platform` e `/platform/saloes/[account_id]` no Reflex. As rotas não serão adicionadas à navegação pública; o acesso direto será checado por papel usando a identidade confirmada pelo Xano.
- Reutilizar a formatação de preço existente no frontend para converter centavos em reais, evitando divergência visual entre o painel de salão e o painel de plataforma.

## Risks / Trade-offs

- **Uma checagem apenas no Reflex poderia ser contornada por chamadas diretas à API** → Cada endpoint de plataforma valida a sessão e a autorização no backend.
- **Uma edição poderia ocorrer sem auditoria se a gravação do log falhar** → Persistir a edição e o registro `event_log` na mesma transação.
- **Consultas amplas podem retornar dados de outro salão** → Aplicar o identificador do salão em cada consulta de detalhe e calcular os relacionamentos a partir dele.
- **Alterar `auth/me` pode afetar os fluxos existentes** → Preservar exatamente as validações atuais de `client` e `admin` e adicionar apenas a combinação válida de `platform_admin` sem empresa.
- **As métricas podem divergir por fuso ou inclusão de cancelamentos** → Fixar no contrato os limites locais e a inclusão/exclusão de status por indicador.

## Migration Plan

1. Implementar e validar o login e a identidade no Xano.
2. Implementar os endpoints protegidos e as escritas auditadas; validar o XanoScript com o Xano Developer MCP.
3. Implementar as páginas Reflex no prefixo `/platform` e validar os fluxos de sessão, filtros, edição e formatação.
4. Rodar verificações relevantes e comparar cada comportamento com os cenários das especificações.
5. Se o usuário quiser publicar, executar primeiro `xano workspace push --dry-run`, apresentar o resultado e aguardar confirmação antes do push real.

Para reverter antes da publicação, remover os novos endpoints e grupo, restaurar a validação anterior de `auth/me` e remover as rotas e o estado Reflex de plataforma. A reversão não exige mudança de schema de dados.
