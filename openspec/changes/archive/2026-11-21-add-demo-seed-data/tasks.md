# Tasks

## 1. Backend — Função Xano

- [x] 1.1 Consultar a documentação Xano para parâmetros de função, senha, transações, datas/fuso horário e consultas; confirmar os esquemas usados e registrar a validação pelo Xano Developer MCP antes de implementar.
- [x] 1.2 Criar somente `xano/function/seed_demo_data.xs`, com pré-checagens, senha recebida na execução, criação de entidades ausentes e ignorando integralmente contas já existentes; validar a função pelo Xano Developer MCP.
- [x] 1.3 Ajustar o calendário para sete agendamentos passados e três hoje às 17:00, 17:00 e 18:00; validar antecedência, expediente até 19:00, ausência de sobreposição, dois cancelamentos e snapshots antes da gravação.

## 2. Backend — Publicação e execução controladas

- [x] 2.1 Rodar dry-run do workspace `149160` incluindo somente `xano/function/seed_demo_data.xs`; verificar que somente `seed_demo_data` aparece como `UPDATE` e não há alterações de outros arquivos ou operações de exclusão.
- [x] 2.2 Somente se o dry-run mostrar apenas a atualização de `seed_demo_data`, publicar esse arquivo e executar a função uma única vez com a senha fornecida em tempo de execução; verificar retorno de sucesso sem expor a senha.
- [x] 2.3 Conferir no banco os três salões, donos, quatro clientes, serviços, profissionais, horários e agendamentos; verificar dez agendamentos, dois cancelados e três de hoje por salão, snapshots completos e nenhum horário sobreposto.
