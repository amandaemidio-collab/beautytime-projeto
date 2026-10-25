# salon-directory Specification

## Purpose
Permite que qualquer pessoa encontre os salões parceiros que aceitam reservas e chegue ao link público de agendamento de cada um, sem expor dados internos das empresas.

## Requirements

### Requirement: Consulta pública lista os salões que aceitam reservas
O sistema SHALL permitir, sem autenticação, listar as empresas que aceitam reservas, retornando somente o nome e o identificador público de cada uma, em ordem alfabética de nome. Uma empresa aceita reservas quando possui ao menos um serviço ativo vinculado a ao menos um profissional ativo da mesma empresa.

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
- **THEN** cada item contém apenas nome e identificador público, sem id interno, descrição, localização, dados de administradores, serviços, profissionais ou agendamentos

### Requirement: Tela pública "Encontrar salões"
O sistema SHALL oferecer, sem exigir login, uma tela "Encontrar salões" que apresenta a lista pública de salões com o nome de cada um e um botão que leva a `/agendar/{identificador}` do salão correspondente.

#### Scenario: Lista com salões
- **WHEN** uma pessoa abre a tela e a consulta retorna salões
- **THEN** a interface apresenta cada salão com nome e botão para agendar, e o botão abre `/agendar/{identificador}` daquele salão

#### Scenario: Lista vazia
- **WHEN** a consulta retorna uma lista vazia
- **THEN** a interface apresenta um estado vazio informando que ainda não há salões disponíveis para agendamento

#### Scenario: Falha ao carregar
- **WHEN** a consulta falha ou retorna dados em formato inesperado
- **THEN** a interface apresenta mensagem de erro sem exibir salões parciais e permite tentar novamente ao recarregar a página

#### Scenario: Acesso sem sessão
- **WHEN** uma pessoa sem sessão abre a tela
- **THEN** a interface apresenta a lista normalmente, sem encaminhar para login

#### Scenario: Uso no celular
- **WHEN** a tela é aberta em viewport de celular
- **THEN** o conteúdo respeita as margens laterais das demais telas, sem rolagem horizontal, e nomes longos quebram linha sem cortar o botão
