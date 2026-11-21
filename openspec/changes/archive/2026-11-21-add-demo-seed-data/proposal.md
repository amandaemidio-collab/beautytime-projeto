# Proposal

## Why

O workspace precisa de dados realistas para demonstrar e verificar os fluxos de agendamento sem cadastrar cada empresa, catálogo, profissional, horário, cliente e reserva manualmente. Uma função idempotente permite preparar os mesmos cenários novamente sem duplicar nem alterar registros já existentes.

## What Changes

- Criar uma função Xano `seed_demo_data` que adiciona somente registros ausentes e não altera nem exclui dados existentes.
- Preparar três salões de São Paulo (beleza, barbearia e estúdio de unhas), cada um com administrador, serviços ativos, dois profissionais ativos associados aos serviços e horários de segunda a sábado.
- Preparar quatro clientes globais e dez agendamentos por salão na semana corrente de `America/Sao_Paulo`, incluindo hoje, horários passados e futuros, dois cancelamentos por salão e os dados históricos do serviço no agendamento.
- Usar identificadores e e-mails demo estáveis; pular integralmente um salão cuja `public_identifier` já exista e reutilizar clientes demo compatíveis já cadastrados.
- Receber a senha demo somente na invocação da função e persistir usuários pelo campo `password` do Xano, sem guardar a senha em arquivos versionados.
- Validar os arquivos Xano, revisar um dry-run restrito somente ao arquivo desta change e executar o push e a função uma única vez apenas se a prévia mostrar exclusivamente criação.

## Capabilities

### New Capabilities

- `demo-seed-data`: preparação idempotente e não destrutiva de dados de demonstração para empresas, usuários, catálogo, horários e agendamentos.

### Modified Capabilities

Nenhuma.

## Impact

- Backend Xano: nova função `seed_demo_data`, sem novo endpoint público e sem alteração de tabelas ou fluxos existentes.
- Dados do workspace Xano `149160`: somente inserções de dados demo para entidades ausentes; nenhum registro existente será atualizado ou removido.
- Execução da função: requer a senha de demonstração fornecida como entrada no momento da execução; não deve ser impressa em logs ou persistida no repositório.

Fora do escopo: interface Reflex, mudanças nas rotas de autenticação/agendamento, edição ou limpeza de registros existentes, criação de novas tabelas e commit Git.
