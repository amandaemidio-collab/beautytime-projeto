# Proposal

## Why

A área pública `/saloes` já permite encontrar salões que aceitam reservas, mas hoje mostra apenas o nome e um botão de agendamento, sem busca, filtro ou informações dos serviços. A change amplia essa descoberta com dados públicos úteis para escolher um salão, preservando a regra de elegibilidade e o fluxo de agendamento existente.

## What Changes

- Criar um endpoint público `GET /public/accounts`, sem login, com busca opcional por nome do salão e filtro opcional por nome de serviço ativo.
- Retornar somente nome, descrição, localização, identificador público e os campos públicos dos serviços ativos: nome, duração e preço em centavos.
- Manter a listagem limitada a salões que aceitam reservas, segundo a regra existente de serviço ativo vinculado a profissional ativo da mesma empresa.
- Ampliar a página Reflex `/saloes` com campos de busca e filtro, cards com nome, localização e serviços ativos, e preços exibidos em reais usando o formatador existente.
- Fazer o botão “Agendar” abrir o link público `/agendar/{public_identifier}` existente.
- Incluir o link “Encontrar salões” na página inicial e na área da cliente.
- Não modificar endpoints `/platform`, páginas administrativas ou o fluxo de agendamento existente.
- Não publicar alterações no Xano sem solicitar confirmação específica após apresentar um dry-run.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `salon-directory`: permitir busca e filtro na listagem pública e exibir detalhes públicos e serviços ativos de salões que aceitam reservas.

## Impact

- **Xano:** novo endpoint público no grupo de API público, consultando `account`, `professional_service`, `service` e `professional` sem retornar identificadores internos, usuários ou dados administrativos.
- **Reflex:** ampliar o estado e a tela existente `/saloes`, adicionar links na página inicial e na área de cliente; reutilizar o cliente HTTP e o formatador de moeda existentes.
- **Compatibilidade:** preservar as rotas e telas `/admin` e `/platform`; o botão de agendamento continua usando `/agendar/{identificador}`.
- **Fora do escopo:** mudanças no endpoint `/platform/accounts`, no agendamento, login, tabelas ou registros existentes.
