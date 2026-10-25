# professional-management Specification

## Purpose
Permite que administradoras mantenham os profissionais da própria empresa e indiquem quais serviços ativos cada profissional realiza, sem expor esses dados na página pública nesta etapa.

## Requirements

### Requirement: Administradora mantém profissionais da própria empresa
O sistema SHALL permitir que uma administradora autenticada cadastre, liste e edite profissionais pertencentes à empresa associada à sua sessão.

#### Scenario: Cadastro válido
- **WHEN** a administradora informa o nome e pelo menos um serviço ativo da própria empresa
- **THEN** o sistema cria o profissional associado à empresa da sessão, vinculado aos serviços escolhidos e ativo por padrão

#### Scenario: Edição válida
- **WHEN** a administradora altera o nome ou os serviços de um profissional da própria empresa usando serviços ativos da empresa
- **THEN** o sistema salva e retorna os dados atualizados do profissional

#### Scenario: Nome vazio
- **WHEN** a administradora tenta cadastrar ou editar um profissional sem nome após remover espaços das extremidades
- **THEN** o sistema rejeita a operação sem criar ou alterar o profissional

#### Scenario: Empresa ainda não possui serviço ativo
- **WHEN** a administradora tenta cadastrar um profissional e a empresa não possui serviço ativo para selecionar
- **THEN** a interface informa que é necessário cadastrar um serviço ativo antes de criar o profissional

### Requirement: Serviços associados ao profissional são ativos e da mesma empresa
O sistema SHALL aceitar em cadastro ou edição somente serviços ativos pertencentes à empresa da administradora autenticada.

#### Scenario: Serviço ativo da própria empresa
- **WHEN** a administradora associa ao profissional um serviço ativo da própria empresa
- **THEN** o sistema mantém o vínculo entre o profissional e o serviço

#### Scenario: Serviço inativo ou de outra empresa
- **WHEN** a administradora tenta associar ao profissional um serviço inativo ou pertencente a outra empresa
- **THEN** o sistema rejeita a operação sem criar ou alterar vínculos

#### Scenario: Serviço vinculado é desativado
- **WHEN** um serviço associado a um profissional é desativado
- **THEN** o vínculo permanece armazenado, mas não conta como serviço válido enquanto o serviço estiver inativo

#### Scenario: Serviço vinculado é reativado
- **WHEN** um serviço associado anteriormente é reativado
- **THEN** o vínculo preservado volta a contar como válido sem precisar ser recriado

#### Scenario: Edição apresenta somente serviços ativos para seleção
- **WHEN** a administradora edita os serviços de um profissional
- **THEN** somente serviços ativos da própria empresa podem ser escolhidos; uma edição que não envia uma nova seleção preserva os vínculos existentes, inclusive os de serviços inativos

### Requirement: Administradora consulta profissionais ativos e inativos
O sistema SHALL listar para a administradora somente os profissionais da empresa associada à sessão, incluindo os ativos e inativos e os serviços associados.

#### Scenario: Empresa com profissionais
- **WHEN** a administradora autenticada lista os profissionais
- **THEN** o sistema retorna os profissionais da própria empresa com nome, situação e serviços associados

#### Scenario: Empresa sem profissionais
- **WHEN** a empresa não possui profissionais cadastrados
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Cliente ou pessoa sem sessão solicita a lista
- **WHEN** uma cliente ou pessoa sem sessão válida solicita a lista administrativa
- **THEN** o sistema rejeita a operação sem revelar profissionais

### Requirement: Dados e operações de profissionais respeitam o isolamento por empresa
O sistema SHALL determinar a empresa pelo administrador autenticado e SHALL impedir leitura ou alteração de profissionais de outra empresa.

#### Scenario: Identificador de empresa forjado
- **WHEN** uma administradora envia na requisição um identificador de empresa diferente do vínculo da sua sessão
- **THEN** o sistema ignora o identificador enviado e restringe a operação à empresa da sessão

#### Scenario: Profissional de outra empresa ou inexistente
- **WHEN** uma administradora tenta editar ou alterar a situação de profissional de outra empresa ou inexistente
- **THEN** o sistema responde como não encontrado, sem revelar nem alterar o profissional

### Requirement: Profissionais podem ser desativados e reativados sem exclusão física
O sistema SHALL permitir que a administradora altere a situação de um profissional da própria empresa entre ativo e inativo, preservando seus dados e vínculos, sem oferecer exclusão física.

#### Scenario: Desativação
- **WHEN** a administradora desativa um profissional ativo da própria empresa
- **THEN** o profissional passa a inativo e permanece disponível na listagem administrativa

#### Scenario: Reativação
- **WHEN** a administradora reativa um profissional inativo da própria empresa
- **THEN** o profissional volta a ativo com o mesmo nome e vínculos de serviços

#### Scenario: Exclusão física não disponível
- **WHEN** uma pessoa tenta excluir fisicamente um profissional pela interface ou API desta capability
- **THEN** a operação de exclusão não está disponível e o registro permanece inalterado

### Requirement: Profissionais não possuem acesso próprio
O sistema SHALL tratar profissionais como registros da empresa, sem login ou credenciais próprias nesta etapa.

#### Scenario: Profissional não entra como usuário
- **WHEN** uma pessoa tenta autenticar-se como profissional pelas funções disponíveis
- **THEN** o sistema não cria nem autentica uma conta de profissional

### Requirement: Página pública não apresenta profissionais nesta etapa
O sistema SHALL manter os profissionais fora da página pública `/agendar/{identificador}` até que a apresentação faça parte da change de agendamento.

#### Scenario: Empresa possui profissionais cadastrados
- **WHEN** uma pessoa abre a página pública de uma empresa que possui profissionais
- **THEN** a interface não apresenta nomes, perfis ou seleção de profissionais
