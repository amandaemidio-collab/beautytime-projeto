# Platform Admin Panel Specification

## Purpose

Define o acesso exclusivo da equipe da plataforma para pesquisar salões, consultar seus indicadores e manter dados com registro de auditoria.

## Requirements

### Requirement: Administrador da plataforma entra por login próprio
O sistema SHALL autenticar por e-mail e senha somente usuários `platform_admin` sem `account_id`, emitindo sessão válida sem expor senha ou hash.

#### Scenario: Login válido da plataforma
- **WHEN** uma conta `platform_admin` sem empresa informa credenciais corretas no login da plataforma
- **THEN** o sistema retorna uma sessão utilizável e a identidade com o papel `platform_admin`

#### Scenario: Credenciais de outro tipo
- **WHEN** uma conta `client` ou `admin` tenta entrar pelo login da plataforma
- **THEN** o sistema rejeita o acesso sem emitir uma sessão

#### Scenario: Identidade da sessão da plataforma
- **WHEN** uma sessão autenticada pertence a um usuário `platform_admin`
- **THEN** a consulta de identidade retorna seu papel e `account_id` nulo

### Requirement: Área da plataforma é separada e protegida
O sistema SHALL disponibilizar a área Reflex em `/platform/login`, `/platform` e `/platform/saloes/{account_id}`, mantendo as rotas `/admin` dos salões sem alteração.

#### Scenario: Acesso sem sessão
- **WHEN** uma pessoa sem sessão válida abre qualquer página sob `/platform`
- **THEN** a interface redireciona para `/platform/login` sem exibir dados da plataforma

#### Scenario: Acesso com papel diferente
- **WHEN** uma pessoa autenticada como `client` ou `admin` abre qualquer página sob `/platform`
- **THEN** a interface redireciona para `/platform/login` e não exibe dados da plataforma

#### Scenario: Rotas de salão preservadas
- **WHEN** uma administradora de salão acessa `/admin/login` ou `/admin`
- **THEN** o sistema mantém o fluxo existente de login e painel de salão

#### Scenario: Login da plataforma sem link público no aplicativo
- **WHEN** uma pessoa navega pelo aplicativo sem digitar uma URL da plataforma
- **THEN** os menus e links públicos do aplicativo não exibem `/platform/login`

### Requirement: Endpoints da plataforma exigem autorização de plataforma
Todos os endpoints da API sob `/platform` SHALL exigir sessão válida e autorização de `platform_admin`, independentemente das verificações feitas pela interface.

#### Scenario: Administrador da plataforma acessa endpoint
- **WHEN** um usuário autenticado `platform_admin` chama um endpoint sob `/platform`
- **THEN** o endpoint permite a operação se os dados solicitados forem válidos

#### Scenario: Usuário sem sessão chama endpoint
- **WHEN** uma pessoa sem sessão válida chama um endpoint sob `/platform`
- **THEN** a API rejeita a chamada sem retornar dados ou alterar registros

#### Scenario: Outro papel chama endpoint
- **WHEN** uma conta `client` ou `admin` chama um endpoint sob `/platform`
- **THEN** a API responde com acesso negado e não retorna dados nem altera registros

### Requirement: Lista de salões permite pesquisa e mostra contagens
O sistema SHALL listar todas as contas `account`, aplicando pesquisa por nome e filtro por serviço ativo quando informados, e SHALL retornar as contagens de serviços, profissionais e agendamentos de cada salão.

#### Scenario: Pesquisa por nome sem diferenciar caixa
- **WHEN** a plataforma lista salões com texto em `search`
- **THEN** o resultado contém salões cujo nome inclui o texto sem diferenciar maiúsculas de minúsculas

#### Scenario: Filtro por nome de serviço ativo
- **WHEN** a plataforma lista salões com texto em `service`
- **THEN** o resultado contém somente salões com pelo menos um serviço ativo cujo nome inclui o texto sem diferenciar maiúsculas de minúsculas

#### Scenario: Dois filtros aplicados
- **WHEN** `search` e `service` são informados na mesma consulta
- **THEN** o resultado satisfaz ambos os filtros

#### Scenario: Contagens da lista
- **WHEN** um salão aparece na listagem
- **THEN** o resultado inclui a quantidade total de seus serviços, profissionais e agendamentos, incluindo inativos e cancelados

#### Scenario: Nenhum salão corresponde
- **WHEN** os filtros não correspondem a nenhum salão
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Lista de salões na interface
- **WHEN** um administrador da plataforma abre a página principal da plataforma
- **THEN** a interface mostra pesquisa por nome, filtro por serviço e salões em cards que abrem o detalhe do salão selecionado

### Requirement: Detalhe do salão inclui seus cadastros
O sistema SHALL permitir consultar os dados de um salão junto com seus serviços e profissionais, incluindo registros ativos e inativos.

#### Scenario: Consulta de salão existente
- **WHEN** um administrador da plataforma consulta um `account_id` existente
- **THEN** o sistema retorna os dados da conta, seus serviços e seus profissionais

#### Scenario: Salão inexistente
- **WHEN** um administrador da plataforma consulta um `account_id` inexistente
- **THEN** o sistema responde como não encontrado e não retorna dados de outro salão

#### Scenario: Abas da página do salão
- **WHEN** um administrador da plataforma abre o detalhe de um salão
- **THEN** a interface mostra os cards de indicadores no topo e as abas “Dados do salão”, “Serviços” e “Profissionais”, com opção de editar os dados de cada aba

### Requirement: Dashboard do salão apresenta indicadores definidos
O sistema SHALL calcular os indicadores do salão usando o fuso `America/Sao_Paulo` e a semana de segunda-feira a domingo.

#### Scenario: Indicadores do dia e da semana
- **WHEN** o dashboard é consultado para um salão
- **THEN** retorna o total de agendamentos não cancelados iniciados hoje, o total de agendamentos da semana incluindo cancelados, e o faturamento estimado da semana em centavos somando somente agendamentos não cancelados

#### Scenario: Taxa de cancelamento
- **WHEN** existem agendamentos na semana do salão
- **THEN** a taxa é o número de agendamentos cancelados dividido pelo total de agendamentos da semana

#### Scenario: Semana sem agendamentos
- **WHEN** não existem agendamentos na semana do salão
- **THEN** a taxa de cancelamento e o faturamento estimado são zero

#### Scenario: Serviços mais agendados
- **WHEN** o dashboard é consultado
- **THEN** retorna até cinco serviços ordenados pela quantidade de agendamentos da semana, contando os registros cancelados

#### Scenario: Próximos horários de hoje
- **WHEN** existem agendamentos não cancelados ainda não iniciados hoje
- **THEN** o dashboard retorna até cinco em ordem crescente de início

### Requirement: Administrador da plataforma pode editar salões e seus cadastros
O sistema SHALL permitir atualizar somente `name`, `description` e `location` de um salão, `name`, `duration_minutes`, `price_cents` e `is_active` de um serviço, e `name` e `is_active` de um profissional.

#### Scenario: Atualização válida
- **WHEN** um administrador da plataforma envia um ou mais campos editáveis válidos para um registro existente
- **THEN** o sistema salva e retorna os dados atualizados sem alterar identificadores ou vínculos

#### Scenario: Dados inválidos
- **WHEN** um administrador da plataforma envia valores que violam as regras existentes de nome, duração, preço ou unicidade de serviço
- **THEN** o sistema rejeita a alteração e mantém os dados originais

#### Scenario: Identificador inexistente
- **WHEN** um administrador da plataforma tenta editar um salão, serviço ou profissional inexistente
- **THEN** o sistema responde como não encontrado sem alterar outros registros

#### Scenario: Edição não altera agendamentos existentes
- **WHEN** um serviço ou profissional é editado
- **THEN** os dados históricos já copiados para agendamentos existentes permanecem inalterados

### Requirement: Toda alteração pela plataforma é auditada
O sistema SHALL registrar cada alteração bem-sucedida de salão, serviço ou profissional em `event_log`, associando o usuário autenticado, o salão afetado, a ação e os valores alterados.

#### Scenario: Auditoria de alteração
- **WHEN** um administrador da plataforma salva uma alteração
- **THEN** é gravado um evento com `user_id`, `account_id`, `action` e metadados dos campos alterados e seus valores anteriores e novos

#### Scenario: Falha ao registrar auditoria
- **WHEN** uma alteração não pode ser registrada em `event_log`
- **THEN** a alteração do cadastro não é confirmada

### Requirement: Painel exibe preços em reais
O sistema SHALL apresentar preços em centavos na interface como valores em reais, com duas casas decimais.

#### Scenario: Formatação de preço
- **WHEN** a interface apresenta o valor `4500` em centavos
- **THEN** exibe `R$ 45,00`
