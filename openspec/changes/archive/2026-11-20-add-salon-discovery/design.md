# Design

## Context

A tela Reflex `/saloes` hoje carrega `companies/public` sem filtros e apresenta somente o nome do salão e a ação de agendar. O endpoint público retorna salões que têm serviço ativo associado a profissional ativo da mesma empresa. A página de agendamento busca os serviços ativos separadamente; `frontend.formatting.price_label` já formata preços em reais.

Ver `proposal.md` e `specs/salon-directory/spec.md` para motivação e contrato de comportamento.

## Goals / Non-Goals

**Goals:**

- Fazer a busca e os dados públicos serem servidos por uma única consulta pública própria para a listagem.
- Retornar explicitamente uma lista permitida de campos para evitar exposição acidental de registros ou campos internos do Xano.
- Reutilizar o estado e a navegação existentes de `/saloes` e `/agendar/{public_identifier}`.

**Non-Goals:**

- Modificar ou reutilizar endpoints do grupo `/platform`.
- Alterar o endpoint existente `companies/public`, a página de agendamento ou regras de autenticação.
- Criar novos modelos de dados ou dependências.

## Decisions

- Adicionar `public/accounts` ao grupo Xano `Members & Accounts`, como endpoint GET sem autenticação. Esse grupo já contém endpoints públicos de empresas; usar um grupo separado ou alterar a rota protegida da plataforma criaria uma superfície desnecessária.
- Manter a elegibilidade já adotada pela listagem: incluir uma empresa uma única vez somente quando houver serviço ativo vinculado a profissional ativo da mesma empresa. Listar todos os serviços ativos da empresa, conforme a consulta pública de catálogo existente; o filtro `service` é satisfeito quando ao menos um desses serviços ativos contém o texto informado.
- Aplicar `search` ao nome da empresa e `service` ao nome dos serviços ativos sem diferenciar maiúsculas de minúsculas. Quando ambos forem informados, exigir que os dois critérios sejam satisfeitos; texto vazio ou omitido não restringe os resultados.
- Montar a resposta com campos públicos explícitos para salão e serviço, sem retornar os objetos do banco. Isso evita incluir IDs internos, `account_id`, ligações, usuário, contagens ou outros campos administrativos.
- Atualizar a página existente `/saloes` para consultar o novo endpoint, renderizar os serviços e formatar `price_cents` com o helper compartilhado `price_label`. Preservar a navegação de agendamento existente em vez de reimplementar login ou reserva.
- Adicionar links explícitos para `/saloes` à página inicial e à área da cliente sem alterar os acessos `/admin` ou `/platform`.

## Risks / Trade-offs

- **Uma resposta pública pode vazar campos internos ao serializar registros do banco** → Construir cada campo do salão e de serviço explicitamente, conforme a lista permitida pela spec.
- **Busca e filtro podem divergir do que os cards exibem** → Aplicar o filtro de serviço aos mesmos serviços ativos retornados na resposta.
- **Mudar a listagem pode quebrar o caminho de agendamento** → Continuar usando o identificador público e a navegação já usada para `/agendar/{identificador}`; validar o fluxo no navegador.
- **Listas longas de salões/serviços podem ampliar a resposta** → Manter o escopo simples nesta change e retornar somente salões correspondentes e seus serviços ativos; paginação fica fora do contrato solicitado.

## Migration Plan

1. Criar e validar o endpoint público em Xano sem editar ou publicar endpoints `/platform`.
2. Atualizar a tela e os links Reflex, depois validar os filtros, os campos retornados e a navegação até o agendamento.
3. Antes de qualquer publicação Xano, executar `xano workspace push --dry-run`, apresentar o resultado e aguardar confirmação específica.
4. Se necessário reverter antes da publicação, remover o endpoint novo e reverter as alterações de `/saloes` e os links, sem alterar dados persistidos.
