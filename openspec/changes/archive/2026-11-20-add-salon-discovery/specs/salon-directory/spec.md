# Spec Delta

## MODIFIED Requirements

### Requirement: Consulta pública lista os salões que aceitam reservas
O sistema SHALL permitir, sem autenticação, listar empresas que aceitam reservas e retornar somente seus dados públicos: nome, descrição, localização, identificador público e serviços ativos com nome, duração em minutos e preço em centavos. A empresa SHALL ter ao menos um serviço ativo vinculado a um profissional ativo da mesma empresa.

#### Scenario: Empresas que aceitam e que não aceitam reservas
- **WHEN** existem empresas com serviço ativo vinculado a profissional ativo e empresas sem essa combinação
- **THEN** o sistema retorna somente as primeiras, cada uma uma única vez, em ordem alfabética de nome

#### Scenario: Serviço ativo sem profissional ativo
- **WHEN** a empresa tem serviços ativos, mas todos os profissionais vinculados a eles estão inativos ou não há vínculo
- **THEN** a empresa não aparece na lista

#### Scenario: Profissional ativo vinculado só a serviços inativos
- **WHEN** a empresa tem profissional ativo, mas ele só está vinculado a serviços inativos
- **THEN** a empresa não aparece na lista

#### Scenario: Nenhuma empresa aceita reservas
- **WHEN** nenhuma empresa atende à condição
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Somente dados públicos
- **WHEN** uma pessoa consulta a lista
- **THEN** cada salão contém somente `name`, `description`, `location`, `public_identifier` e uma lista de serviços com somente `name`, `duration_minutes` e `price_cents`, sem identificadores internos, usuários, contagens, profissionais ou campos administrativos

#### Scenario: Pesquisa por nome do salão
- **WHEN** uma pessoa informa `search` com parte do nome de um salão
- **THEN** o sistema retorna somente salões cujo nome contém o texto, sem diferenciar maiúsculas de minúsculas

#### Scenario: Filtro pelo nome de serviço ativo
- **WHEN** uma pessoa informa `service` com parte do nome de um serviço
- **THEN** o sistema retorna somente salões com ao menos um serviço ativo cujo nome contém o texto, sem diferenciar maiúsculas de minúsculas

#### Scenario: Filtros combinados
- **WHEN** uma pessoa informa `search` e `service` na mesma consulta
- **THEN** o sistema retorna somente salões que correspondem aos dois filtros

#### Scenario: Sem correspondência para os filtros
- **WHEN** os filtros informados não correspondem a nenhum salão
- **THEN** o sistema retorna uma lista vazia

### Requirement: Tela pública "Encontrar salões"
O sistema SHALL oferecer, sem exigir login, a tela `/saloes` com busca por nome, filtro por serviço, cards com nome, localização e serviços ativos com preços em reais, e botão que leva a `/agendar/{public_identifier}`.

#### Scenario: Lista com salões
- **WHEN** uma pessoa abre a tela e a consulta retorna salões
- **THEN** a interface apresenta cada salão com nome, localização, serviços ativos e seus preços formatados em reais, e o botão “Agendar” abre `/agendar/{public_identifier}` daquele salão

#### Scenario: Lista vazia
- **WHEN** a consulta retorna uma lista vazia
- **THEN** a interface apresenta um estado vazio informando que ainda não há salões disponíveis para agendamento

#### Scenario: Falha ao carregar
- **WHEN** a consulta falha ou retorna dados em formato inesperado
- **THEN** a interface apresenta mensagem de erro sem exibir salões parciais e permite tentar novamente ao recarregar a página

#### Scenario: Acesso sem sessão
- **WHEN** uma pessoa sem sessão abre a tela
- **THEN** a interface apresenta a lista normalmente, sem encaminhar para login

#### Scenario: Pesquisa e filtro na tela
- **WHEN** uma pessoa envia uma busca por nome, um filtro por serviço ou ambos
- **THEN** a tela exibe somente os salões correspondentes aos filtros enviados

#### Scenario: Preço em reais
- **WHEN** a interface apresenta um serviço com preço de `4500` centavos
- **THEN** exibe `R$ 45,00`

#### Scenario: Links para encontrar salões
- **WHEN** uma pessoa abre a página inicial ou a área da cliente
- **THEN** encontra um link “Encontrar salões” que leva a `/saloes`

#### Scenario: Uso no celular
- **WHEN** a tela é aberta em viewport de celular
- **THEN** o conteúdo respeita as margens laterais das demais telas, sem rolagem horizontal, e nomes longos quebram linha sem cortar o botão
