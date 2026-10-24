# Spec Delta

## Purpose

Permite que a administradora mantenha os serviços oferecidos pela própria empresa e que qualquer pessoa consulte, pela página pública, os serviços ativos dessa empresa.

## ADDED Requirements

### Requirement: Administradora cadastra serviços da própria empresa
O sistema SHALL permitir que uma conta de administrador autenticada cadastre serviços com nome, duração e preço, vinculando cada serviço à empresa da própria conta, obtida da sessão e nunca de um dado enviado na requisição. Todo serviço novo SHALL nascer ativo.

#### Scenario: Cadastro válido
- **WHEN** uma administradora autenticada envia nome, duração e preço válidos
- **THEN** o sistema cria o serviço ativo vinculado à empresa dela e o retorna com nome, duração, preço e situação

#### Scenario: Tentativa de indicar outra empresa
- **WHEN** uma administradora envia, junto ao cadastro, um identificador de empresa diferente da sua
- **THEN** o sistema ignora esse identificador e vincula o serviço somente à empresa da conta autenticada

#### Scenario: Cliente tenta cadastrar serviço
- **WHEN** uma conta de cliente autenticada tenta cadastrar um serviço
- **THEN** o sistema rejeita a operação com acesso negado e não cria o serviço

#### Scenario: Requisição sem autenticação
- **WHEN** uma requisição sem sessão válida tenta cadastrar, listar, editar, alterar situação ou excluir serviços administrativos
- **THEN** o sistema rejeita a operação sem criar, alterar ou revelar serviços

### Requirement: Dados do serviço são validados
O sistema SHALL exigir nome com 2 a 80 caracteres após remover espaços das extremidades, duração em minutos inteiros múltipla de 5 entre 5 e 480, e preço em centavos inteiros entre 0 e 9.999.999. Dados inválidos SHALL ser rejeitados sem criar nem alterar o serviço.

#### Scenario: Limites aceitos
- **WHEN** a administradora envia nome com 2 ou 80 caracteres, duração de 5 ou 480 minutos e preço de 0 ou 9.999.999 centavos
- **THEN** o sistema aceita os dados

#### Scenario: Nome fora do limite
- **WHEN** a administradora envia nome vazio, só com espaços, com 1 caractere ou com 81 caracteres
- **THEN** o sistema rejeita a operação informando que o nome é inválido

#### Scenario: Duração inválida
- **WHEN** a administradora envia duração de 0, 4, 481 ou 32 minutos, ou valor não inteiro
- **THEN** o sistema rejeita a operação informando que a duração deve ser múltipla de 5 entre 5 e 480 minutos

#### Scenario: Preço inválido
- **WHEN** a administradora envia preço negativo, acima de 9.999.999 centavos ou não inteiro
- **THEN** o sistema rejeita a operação informando que o preço é inválido

### Requirement: Nome do serviço é único na empresa
O sistema SHALL impedir dois serviços com o mesmo nome na mesma empresa, comparando nomes sem espaços nas extremidades e sem diferenciar maiúsculas de minúsculas, considerando serviços ativos e inativos. Empresas diferentes SHALL poder usar o mesmo nome.

#### Scenario: Nome repetido na mesma empresa
- **WHEN** a administradora cadastra ou renomeia um serviço para "corte feminino" e a empresa já tem um serviço "Corte Feminino", ativo ou inativo
- **THEN** o sistema rejeita a operação informando que já existe um serviço com esse nome

#### Scenario: Mesmo nome em outra empresa
- **WHEN** a administradora cadastra "Corte" e outra empresa já possui um serviço "Corte"
- **THEN** o sistema cria o serviço normalmente

#### Scenario: Edição mantendo o próprio nome
- **WHEN** a administradora edita a duração ou o preço de um serviço sem alterar o nome
- **THEN** o sistema não trata o próprio serviço como duplicado

### Requirement: Administradora lista os serviços da própria empresa
O sistema SHALL retornar à administradora autenticada todos os serviços da própria empresa, ativos e inativos, com nome, duração, preço e situação, e nunca serviços de outra empresa.

#### Scenario: Listagem da própria empresa
- **WHEN** uma administradora autenticada solicita seus serviços
- **THEN** o sistema retorna apenas os serviços da empresa dela, incluindo os inativos

#### Scenario: Empresa sem serviços
- **WHEN** a empresa da administradora ainda não possui serviços
- **THEN** o sistema retorna uma lista vazia

### Requirement: Administradora edita serviços da própria empresa
O sistema SHALL permitir que a administradora altere nome, duração e preço de um serviço da própria empresa, aplicando as mesmas validações do cadastro, e SHALL tratar serviços de outra empresa como inexistentes.

#### Scenario: Edição válida
- **WHEN** a administradora envia novos dados válidos para um serviço da própria empresa
- **THEN** o sistema atualiza o serviço e retorna os dados atualizados

#### Scenario: Serviço de outra empresa
- **WHEN** a administradora tenta editar, alterar a situação ou excluir um serviço que pertence a outra empresa
- **THEN** o sistema responde como não encontrado, sem alterar o serviço nem revelar seus dados

#### Scenario: Serviço inexistente
- **WHEN** a administradora tenta editar, alterar a situação ou excluir um serviço que não existe
- **THEN** o sistema responde como não encontrado

### Requirement: Administradora desativa e reativa serviços
O sistema SHALL permitir que a administradora desative um serviço ativo e reative um serviço inativo da própria empresa, preservando seus dados.

#### Scenario: Desativação
- **WHEN** a administradora desativa um serviço ativo da própria empresa
- **THEN** o serviço passa a inativo, continua na listagem administrativa e deixa de aparecer na consulta pública

#### Scenario: Reativação
- **WHEN** a administradora reativa um serviço inativo da própria empresa
- **THEN** o serviço volta a ativo com os mesmos nome, duração e preço e volta a aparecer na consulta pública

### Requirement: Administradora exclui serviços
O sistema SHALL permitir que a administradora exclua definitivamente um serviço da própria empresa. A interface SHALL pedir confirmação explícita antes de excluir.

#### Scenario: Exclusão confirmada
- **WHEN** a administradora confirma a exclusão de um serviço da própria empresa
- **THEN** o sistema remove o serviço, que deixa de aparecer nas listagens administrativa e pública

#### Scenario: Exclusão cancelada
- **WHEN** a administradora abre a confirmação de exclusão e desiste
- **THEN** a interface não envia a exclusão e o serviço permanece inalterado

#### Scenario: Nome liberado após exclusão
- **WHEN** a administradora exclui um serviço e depois cadastra outro com o mesmo nome
- **THEN** o sistema cria o novo serviço normalmente

### Requirement: Consulta pública lista serviços ativos da empresa
O sistema SHALL permitir que qualquer pessoa, sem autenticação, consulte os serviços ativos de uma empresa pelo identificador público, retornando somente nome, duração e preço, ordenados por nome. Serviços inativos, identificadores internos e dados de outras empresas SHALL ficar fora da resposta.

#### Scenario: Empresa com serviços ativos e inativos
- **WHEN** uma pessoa consulta os serviços de uma empresa que tem serviços ativos e inativos
- **THEN** o sistema retorna apenas os ativos, com nome, duração e preço, em ordem alfabética

#### Scenario: Empresa sem serviços ativos
- **WHEN** uma pessoa consulta uma empresa existente sem serviços ativos
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Identificador desconhecido
- **WHEN** uma pessoa consulta os serviços de um identificador não associado a empresa
- **THEN** o sistema responde como não encontrado, sem retornar serviços

### Requirement: Página pública apresenta os serviços ativos
A interface SHALL exibir na página `/agendar/{identificador}` os serviços ativos da empresa com nome, duração em formato legível (por exemplo, "45 min" ou "1h 30min") e preço em reais (por exemplo, "R$ 45,00"), sem exigir login e sem mostrar informações administrativas.

#### Scenario: Serviços exibidos
- **WHEN** uma pessoa abre a página pública de uma empresa com serviços ativos
- **THEN** a interface lista nome, duração e preço de cada serviço ativo, legíveis no celular

#### Scenario: Nenhum serviço disponível
- **WHEN** a empresa não possui serviços ativos
- **THEN** a interface informa "Esta empresa ainda não tem serviços disponíveis."

#### Scenario: Falha ao carregar serviços
- **WHEN** a consulta dos serviços falha por erro de rede ou do servidor
- **THEN** a interface mantém os dados da empresa e informa que não foi possível carregar os serviços

### Requirement: Área administrativa de serviços é protegida
A interface SHALL oferecer à administradora uma área de serviços com listagem, formulário de cadastro e edição, ações de desativar, reativar e excluir, e feedback de carregamento, sucesso e erro. Somente uma administradora autenticada SHALL acessar essa área.

#### Scenario: Acesso sem sessão de administradora
- **WHEN** uma pessoa sem sessão, ou com sessão de cliente, abre a área administrativa
- **THEN** a interface a leva ao login de administradora sem exibir serviços

#### Scenario: Primeira visita sem serviços
- **WHEN** a administradora abre a área de serviços e a empresa não possui serviços
- **THEN** a interface mostra um estado vazio com a ação de cadastrar o primeiro serviço

#### Scenario: Erro de validação no formulário
- **WHEN** a administradora envia o formulário com dado inválido ou nome repetido
- **THEN** a interface mostra a mensagem junto ao campo correspondente e preserva os valores digitados

#### Scenario: Situação visível na listagem
- **WHEN** a empresa possui serviços ativos e inativos
- **THEN** a listagem administrativa diferencia visualmente os inativos e oferece a ação de reativá-los
