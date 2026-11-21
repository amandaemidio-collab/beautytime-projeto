# Tasks

## 1. Backend - Métricas do dashboard (Xano)

- [x] 1.1 Extrair o cálculo atual para uma função reutilizável que recebe `account_id` e retorna exatamente o conjunto de métricas e definições documentados; validar datas na semana/dia de São Paulo, cancelamentos, ranking e horários próximos com dados representativos.
- [x] 1.2 Atualizar `GET /platform/accounts/{account_id}/dashboard` para chamar a função, mantendo autorização, validação de existência do salão e a resposta JSON idêntica à versão anterior; comparar todos os campos antes/depois.
- [x] 1.3 Criar `GET /admin/dashboard` usando `Catalogo/authorize_admin` e passando à função somente o `account_id` autorizado; verificar que não há parâmetro de conta na entrada e que administradora vê apenas o próprio salão, enquanto cliente, pessoa sem sessão ou administrador da plataforma recebe acesso negado.
- [x] 1.4 Validar a função e as rotas Xano pelo Xano Developer MCP; executar `xano workspace push --dry-run` e confirmar que o plano inclui somente os artefatos desta tarefa, sem executar push real sem confirmação explícita da pessoa usuária.

## 2. Frontend - Indicadores do salão (Reflex)

- [x] 2.1 Integrar o carregamento de `/admin/dashboard` ao evento de entrada da página `/admin`, validar a resposta antes de atualizar o estado e apresentar erro explícito sem métricas parciais; verificar os estados de sucesso, falha e payload inválido.
- [x] 2.2 Exibir os cards dos indicadores e os próximos horários de hoje acima de “Link público do salão”, formatando faturamento com `formatting.py`; verificar valores em reais, dados vazios, ordenação e apresentação responsiva sem alterar outras páginas.

## 3. Verificação integrada

- [x] 3.1 Compilar/importar o app Reflex e testar o painel com contas de salões diferentes, confirmando isolamento dos dados, redirecionamento de não administradores, correspondência das métricas com o dashboard da plataforma e que `/platform`, `/saloes`, área da cliente e agendamento permanecem sem alterações funcionais.
