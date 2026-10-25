# service-catalog Specification

## Purpose
Permite que a administradora mantenha os serviços da própria empresa e que qualquer pessoa consulte, pela página pública, somente os serviços ativos desse estabelecimento.

## Requirements

### Requirement: Administradora cadastra serviços da própria empresa
O sistema SHALL permitir que uma administradora autenticada cadastre serviços com nome, duração e preço, vinculando-os à empresa obtida da sessão autenticada. Todo serviço novo SHALL ser criado ativo.

#### Scenario: Cadastro válido
- **WHEN** uma administradora envia nome, duração e preço válidos
- **THEN** o sistema cria um serviço ativo na empresa da sessão e retorna seus dados

#### Scenario: Identificador de empresa enviado na requisição
- **WHEN** a administradora inclui um identificador de outra empresa no cadastro
- **THEN** o sistema ignora esse identificador e associa o serviço somente à empresa da sessão

#### Scenario: Cliente tenta cadastrar serviço
- **WHEN** uma cliente autenticada tenta cadastrar um serviço
- **THEN** o sistema rejeita a operação sem criar o serviço

#### Scenario: Requisição sem autenticação
- **WHEN** uma requisição sem sessão válida tenta cadastrar serviço
- **THEN** o sistema rejeita a operação sem criar o serviço

### Requirement: Dados do serviço são validados
O sistema SHALL validar o nome, a duração em minutos inteiros e o preço em centavos inteiros no cadastro e na edição, rejeitando dados inválidos sem criar ou alterar o serviço.

#### Scenario: Limites aceitos
- **WHEN** uma administradora envia nome com 2 ou 80 caracteres, duração de 15 ou 480 minutos e preço de 0 ou 9.999.999 centavos
- **THEN** o sistema aceita os dados

#### Scenario: Nome inválido
- **WHEN** uma administradora envia nome vazio, só com espaços, com menos de 2 ou mais de 80 caracteres após remover espaços das extremidades
- **THEN** o sistema rejeita a operação e identifica o campo de nome como inválido

#### Scenario: Duração inválida
- **WHEN** uma administradora envia duração abaixo de 15, acima de 480, não inteira ou não divisível por 15
- **THEN** o sistema rejeita a operação e informa que a duração deve ser múltipla de 15 entre 15 e 480 minutos

#### Scenario: Preço inválido
- **WHEN** uma administradora envia preço negativo, acima de 9.999.999 centavos ou não inteiro
- **THEN** o sistema rejeita a operação e identifica o campo de preço como inválido

#### Scenario: Preço exibido em reais
- **WHEN** o sistema exibe o preço de um serviço na interface
- **THEN** a interface apresenta o valor em reais com duas casas decimais, convertendo os centavos armazenados

### Requirement: Nome do serviço é único na empresa
O sistema SHALL impedir nomes repetidos na mesma empresa, comparando os nomes após remover espaços das extremidades e sem diferenciar maiúsculas de minúsculas, inclusive para serviços inativos.

#### Scenario: Nome repetido na mesma empresa
- **WHEN** uma administradora cadastra ou renomeia um serviço para um nome já usado por outro serviço da empresa, ativo ou inativo
- **THEN** o sistema rejeita a operação e informa que o nome já está em uso

#### Scenario: Mesmo nome em outra empresa
- **WHEN** uma administradora cadastra um nome que só existe em outra empresa
- **THEN** o sistema cria o serviço normalmente

#### Scenario: Edição mantendo o próprio nome
- **WHEN** uma administradora altera duração ou preço sem mudar o nome do próprio serviço
- **THEN** o sistema salva a edição sem tratar o serviço como duplicado

### Requirement: Administradora lista os serviços da própria empresa
O sistema SHALL listar à administradora autenticada os serviços ativos e inativos da empresa associada à sessão, sem expor serviços de outra empresa.

#### Scenario: Listagem da própria empresa
- **WHEN** uma administradora autenticada solicita a lista de serviços
- **THEN** o sistema retorna somente os serviços da empresa da sessão, com nome, duração, preço e situação

#### Scenario: Empresa sem serviços
- **WHEN** a empresa não possui serviços cadastrados
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Acesso à listagem sem permissão
- **WHEN** uma pessoa sem sessão válida ou uma cliente solicita a listagem administrativa
- **THEN** o sistema rejeita a operação sem revelar serviços

### Requirement: Administradora edita serviços da própria empresa
O sistema SHALL permitir que a administradora altere nome, duração e preço de um serviço da própria empresa, aplicando as validações de cadastro.

#### Scenario: Edição válida
- **WHEN** uma administradora envia dados válidos para editar um serviço da própria empresa
- **THEN** o sistema salva e retorna os dados atualizados

#### Scenario: Serviço de outra empresa
- **WHEN** uma administradora tenta editar um serviço de outra empresa
- **THEN** o sistema responde como não encontrado sem alterar nem revelar o serviço

#### Scenario: Serviço inexistente
- **WHEN** uma administradora tenta editar um serviço inexistente
- **THEN** o sistema responde como não encontrado

### Requirement: Administradora ativa e desativa serviços
O sistema SHALL permitir que a administradora altere a situação de um serviço da própria empresa entre ativo e inativo sem remover seus dados.

#### Scenario: Desativação
- **WHEN** uma administradora desativa um serviço ativo da própria empresa
- **THEN** o serviço passa a inativo, permanece na listagem administrativa e deixa de aparecer publicamente

#### Scenario: Reativação
- **WHEN** uma administradora reativa um serviço inativo da própria empresa
- **THEN** o serviço volta a ativo com os mesmos dados e aparece novamente na consulta pública

#### Scenario: Serviço de outra empresa ou inexistente
- **WHEN** uma administradora tenta alterar a situação de um serviço de outra empresa ou inexistente
- **THEN** o sistema responde como não encontrado sem modificar qualquer serviço

### Requirement: Serviços não são excluídos nesta capability
O sistema SHALL preservar os serviços cadastrados e SHALL permitir sua retirada da oferta somente por desativação, sem endpoint ou ação de exclusão física.

#### Scenario: Tentativa de exclusão
- **WHEN** uma pessoa tenta excluir fisicamente um serviço por meio da interface ou API desta capability
- **THEN** a operação de exclusão não está disponível e o registro permanece inalterado

### Requirement: Consulta pública lista serviços ativos da empresa
O sistema SHALL permitir consulta sem autenticação dos serviços ativos de uma empresa localizada pelo identificador público, retornando o id de cada serviço, para permitir o agendamento, sem retornar outros ids internos, serviços inativos ou dados de outras empresas.

#### Scenario: Empresa com serviços ativos e inativos
- **WHEN** uma pessoa consulta uma empresa que possui serviços ativos e inativos
- **THEN** o sistema retorna apenas os ativos, com id, nome, duração e preço, em ordem alfabética

#### Scenario: Empresa sem serviços ativos
- **WHEN** uma pessoa consulta uma empresa existente sem serviços ativos
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Identificador desconhecido
- **WHEN** uma pessoa consulta serviços para um identificador sem empresa correspondente
- **THEN** o sistema responde como não encontrado sem retornar serviços

### Requirement: Página pública apresenta os serviços ativos
A interface SHALL exibir na rota `/agendar/{identificador}` os serviços ativos com nome, duração legível e preço em reais, sem exigir login nem oferecer agendamento nesta capability.

#### Scenario: Serviços exibidos
- **WHEN** uma pessoa abre a página pública de uma empresa com serviços ativos
- **THEN** a interface lista os serviços com duração legível e preço em reais com duas casas decimais

#### Scenario: Nenhum serviço disponível
- **WHEN** a empresa não possui serviços ativos
- **THEN** a interface informa que a empresa ainda não tem serviços disponíveis

#### Scenario: Falha ao carregar serviços
- **WHEN** a consulta dos serviços falha por erro de rede ou do servidor
- **THEN** a interface mantém os dados públicos da empresa e informa que não foi possível carregar os serviços

### Requirement: Área administrativa de serviços é protegida
A interface SHALL oferecer à administradora uma área protegida para listar, cadastrar, editar e ativar ou desativar os serviços da própria empresa, com estados de carregamento, sucesso, vazio e erro.

#### Scenario: Acesso sem sessão administrativa
- **WHEN** uma pessoa sem sessão ou com sessão de cliente abre a área administrativa de serviços
- **THEN** a interface a encaminha ao login de administradora sem exibir dados de serviços

#### Scenario: Primeira visita sem serviços
- **WHEN** uma administradora abre a área de serviços de uma empresa sem serviços cadastrados
- **THEN** a interface mostra um estado vazio com a ação de cadastrar o primeiro serviço

#### Scenario: Erro de validação
- **WHEN** a administradora envia dados inválidos ou um nome já utilizado pela empresa
- **THEN** a interface mostra o erro junto ao campo correspondente e preserva os valores digitados

#### Scenario: Duração escolhida em lista
- **WHEN** a administradora cadastra ou edita um serviço
- **THEN** a interface oferece opções de duração em passos de 15 minutos, de 15 minutos a 8 horas, com rótulos legíveis, e envia o valor selecionado à API em minutos

#### Scenario: Situação visível na listagem
- **WHEN** a empresa possui serviços ativos e inativos
- **THEN** a interface diferencia os inativos e oferece a ação de reativá-los
