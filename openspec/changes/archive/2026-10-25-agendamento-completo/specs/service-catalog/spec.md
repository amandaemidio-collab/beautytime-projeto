# Spec Delta

## MODIFIED Requirements

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
