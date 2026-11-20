# Platform Administration Specification

## Purpose

Define a autorização de contas que administram a plataforma, separando-as das contas de administradoras de salões e das contas de clientes.

## Requirements

### Requirement: Administrador da plataforma não possui empresa
O sistema SHALL permitir o tipo `platform_admin` na identidade de usuário somente sem associação a uma empresa.

#### Scenario: Conta de administrador da plataforma sem empresa
- **WHEN** uma conta possui o tipo `platform_admin`
- **THEN** o campo `account_id` da conta é nulo

#### Scenario: Dados associados a uma empresa
- **WHEN** uma operação tenta vincular uma conta `platform_admin` a uma empresa
- **THEN** o sistema rejeita o vínculo e preserva `account_id` como nulo

### Requirement: Autorização exclusiva de administrador da plataforma
O sistema SHALL fornecer uma autorização que aceita somente contas autenticadas cujo tipo seja `platform_admin`.

#### Scenario: Usuário autorizado
- **WHEN** uma conta autenticada possui tipo `platform_admin` e `account_id` nulo
- **THEN** a autorização considera o usuário autorizado

#### Scenario: Cliente tenta usar autorização da plataforma
- **WHEN** uma conta autenticada possui tipo `client`
- **THEN** a autorização rejeita a operação com erro 403

#### Scenario: Administrador de salão tenta usar autorização da plataforma
- **WHEN** uma conta autenticada possui tipo `admin`
- **THEN** a autorização rejeita a operação com erro 403

### Requirement: Cadastros públicos não criam administrador da plataforma
Os fluxos públicos de cadastro SHALL continuar criando somente os tipos definidos para cada fluxo e SHALL não aceitar `platform_admin`.

#### Scenario: Cadastro de cliente
- **WHEN** uma pessoa usa o fluxo `auth/signup`
- **THEN** o sistema cria uma conta `client` sem associação a empresa

#### Scenario: Cadastro de administradora de salão
- **WHEN** uma pessoa usa o fluxo `auth/admin/signup`
- **THEN** o sistema cria uma conta `admin` vinculada à empresa criada no mesmo cadastro

#### Scenario: Tentativa de selecionar administrador da plataforma
- **WHEN** uma pessoa envia ou altera dados de cadastro para solicitar o tipo `platform_admin`
- **THEN** os fluxos `auth/signup` e `auth/admin/signup` não criam esse tipo

### Requirement: Autorização de salão não aceita administrador da plataforma
A autorização de administradora de salão SHALL continuar aceitando somente contas `admin` vinculadas a uma empresa.

#### Scenario: Administrador da plataforma tenta entrar no painel de salão
- **WHEN** uma conta autenticada possui tipo `platform_admin` e `account_id` nulo
- **THEN** a autorização de salão rejeita a operação com erro 403

#### Scenario: Administradora de salão autenticada
- **WHEN** uma conta autenticada possui tipo `admin` e está vinculada a uma empresa válida
- **THEN** a autorização de salão permite continuar no painel da própria empresa
