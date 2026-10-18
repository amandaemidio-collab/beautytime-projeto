# Spec Delta

## Purpose

Permite que a empresa seja criada junto ao cadastro de seu administrador e localizada publicamente por um identificador estável e único na plataforma.

## ADDED Requirements

### Requirement: Empresa é criada com identificador público único
O sistema SHALL exigir que o identificador público escolhido tenha de 3 a 40 caracteres, contenha somente letras minúsculas ASCII, números ou hífen, não comece nem termine com hífen, não contenha hífens consecutivos e seja único entre as empresas.

#### Scenario: Cadastro com identificador disponível
- **WHEN** o cadastro de administrador envia dados válidos de empresa e um identificador público ainda não utilizado
- **THEN** o sistema cria a empresa com esse identificador e a associa à conta de administrador

#### Scenario: Identificador já utilizado
- **WHEN** o cadastro de administrador envia um identificador já utilizado por outra empresa
- **THEN** o sistema rejeita o cadastro e não cria uma segunda empresa com o mesmo identificador

#### Scenario: Identificador inválido
- **WHEN** o identificador enviado tem menos de 3 ou mais de 40 caracteres, contém caracteres diferentes de letras minúsculas ASCII, números e hífen, começa ou termina com hífen, ou contém hífens consecutivos
- **THEN** o sistema rejeita o cadastro e informa que o identificador deve ser corrigido

### Requirement: Consulta pública localiza empresa pelo identificador
O sistema SHALL permitir que qualquer pessoa consulte, sem autenticação, uma empresa pelo identificador público na rota frontend `/agendar/{identificador}` e SHALL retornar somente informações próprias para apresentação pública.

#### Scenario: Empresa encontrada
- **WHEN** uma pessoa consulta um identificador associado a uma empresa
- **THEN** o sistema retorna os dados públicos básicos dessa empresa, incluindo seu nome e identificador

#### Scenario: Acesso pela rota pública de agendamento
- **WHEN** uma pessoa abre `/agendar/{identificador}` para um identificador associado a uma empresa
- **THEN** a interface carrega a página pública correspondente à empresa sem exigir autenticação

#### Scenario: Identificador desconhecido
- **WHEN** uma pessoa consulta um identificador não associado a nenhuma empresa
- **THEN** o sistema retorna uma resposta de não encontrado sem revelar dados de outras empresas

#### Scenario: Dados privados da empresa
- **WHEN** uma pessoa consulta uma empresa publicamente
- **THEN** a resposta não inclui credenciais, dados de autenticação, nem informações privadas de administradores ou de outras empresas
