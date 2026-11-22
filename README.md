# BeautyTime

## 1. Apresentação

O **BeautyTime** é uma aplicação web de agendamento online para salões de beleza, barbearias, esmalterias e estabelecimentos semelhantes.

O sistema resolve problemas comuns de agendas organizadas por telefone, mensagens ou caderno: reduz a troca de mensagens para encontrar horários, evita conflitos de agendamento e permite que clientes consultem a disponibilidade sem depender do atendimento do salão.

O público-alvo é:

- **Clientes** que desejam encontrar um salão, agendar serviços e acompanhar suas reservas.
- **Donos e responsáveis por salões** que precisam organizar serviços, profissionais, horários e agenda.
- **Administradores da plataforma BeautyTime** que operam e acompanham os salões cadastrados.

O BeautyTime é multiempresa: cada salão administra somente os próprios dados. As clientes usam uma conta global e podem agendar em diferentes empresas.

## 2. Acesso ao aplicativo

O aplicativo é executado localmente para desenvolvimento e demonstração; **não há deploy do frontend**. O backend e as APIs já estão publicados no Xano.

### Requisitos

- Windows com PowerShell.
- Git.
- Python compatível com as dependências do projeto.
- Acesso à internet para instalar dependências e carregar as fontes web.

### Clonar e instalar

No PowerShell, escolha uma pasta de trabalho e execute:

```powershell
git clone https://github.com/amandaemidio-collab/beautytime-projeto.git
cd beautytime-projeto
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Iniciar o frontend Reflex

Ainda na raiz do repositório, entre na pasta `frontend` e inicie o app:

```powershell
cd frontend
..\.venv\Scripts\python.exe -m reflex run
```

Quando o servidor estiver pronto, abra [http://localhost:3000](http://localhost:3000) no navegador. Para encerrar a execução local, use `Ctrl+C` no terminal em que o Reflex está rodando.

O frontend consome as APIs do Xano já configuradas no projeto. A inicialização local do Reflex não publica nem altera o backend.

## 3. Perfis de usuários

### Cliente (`client`)

Usa uma conta global, não vinculada a um salão. Pode:

- Criar uma conta e entrar no aplicativo.
- Encontrar salões que aceitam reservas ou acessar diretamente o link público de um salão.
- Consultar serviços, profissionais e horários disponíveis.
- Fazer e consultar os próprios agendamentos.
- Cancelar os próprios agendamentos.

Uma cliente não pode consultar nem cancelar reservas de outra pessoa.

### Dono ou responsável pelo salão (`admin`)

Sua conta está vinculada a uma empresa. Pode:

- Cadastrar e manter os serviços da própria empresa.
- Cadastrar profissionais e associar a eles os serviços que realizam.
- Configurar os períodos de atendimento de cada profissional.
- Consultar a agenda da empresa por dia e profissional.
- Acompanhar os indicadores do dashboard do salão.
- Consultar e copiar o link público de agendamento.

O acesso administrativo é isolado por empresa. Uma administradora não pode gerenciar os dados de outro salão.

### Administrador da plataforma (`platform_admin`)

É um perfil operacional da equipe BeautyTime, separado dos administradores de salão. Acessa a área restrita em `/platform` e pode:

- Pesquisar salões por nome e filtrar por serviço ativo.
- Consultar o dashboard e os dados de um salão.
- Editar dados de salões, serviços e profissionais, conforme as permissões do backend.

Esse perfil não pertence a uma empresa e não usa as telas `/admin` como administrador de salão. O acesso é concedido pela equipe responsável pela plataforma.

## 4. Funcionalidades

### Cliente

- Cadastro, login e sessão global.
- Busca pública de salões em `/saloes`.
- Agendamento pelo link específico do salão.
- Escolha de serviço, profissional ou opção sem preferência, data e horário disponível.
- Consulta de reservas futuras e passadas em `/meus-agendamentos`.
- Cancelamento das próprias reservas e aviso sobre a política aplicável.

### Dono do salão

- Cadastro da empresa e criação do link público.
- Dashboard com indicadores e próximos horários.
- Cadastro, edição e ativação/desativação de serviços.
- Cadastro, edição e ativação/desativação de profissionais.
- Associação dos serviços realizados por cada profissional.
- Configuração de horários de atendimento.
- Agenda filtrada por dia e profissional.
- Cópia do link público do salão.

### Administrador da plataforma

- Busca de salões por nome.
- Filtro por serviço ativo.
- Dashboard e consulta de dados de cada salão.
- Edição de informações do salão, serviços e profissionais.

## 5. Manual de utilização

### Jornada da cliente

#### Criar conta ou entrar

1. Na página inicial, escolha **Sou cliente** e depois **Criar conta** para se cadastrar, ou **Entrar** se já tiver uma conta.
2. No cadastro, informe nome, e-mail, telefone e senha.
3. No login, informe e-mail e senha.
4. Após autenticar, a cliente pode continuar um agendamento iniciado ou acessar a área de agendamentos.

**Resultado esperado:** a cliente entra com uma conta global e pode usá-la para agendar em diferentes salões.

![print](docs/prints/cliente-login.png)

#### Encontrar um salão pela busca

1. Abra `/saloes` pelo botão **Encontrar salões**.
2. Consulte os salões que aceitam reservas.
3. Selecione **Agendar** ou o link do salão desejado.

**Resultado esperado:** a página pública do salão abre no endereço `/agendar/{identificador}`.

![print](docs/prints/busca-saloes.png)

#### Agendar pelo link do salão

1. Abra o link público recebido do salão ou encontrado em `/saloes`.
2. Escolha um serviço disponível.
3. Escolha um profissional ou **Sem preferência**, quando a opção estiver disponível.
4. Escolha uma data e um horário livre.
5. Confira o resumo do agendamento.
6. Entre ou crie uma conta de cliente, se solicitado, e confirme.

**Resultado esperado:** a aplicação confirma o agendamento e apresenta os dados escolhidos. A disponibilidade e a prevenção de conflitos são verificadas pelo backend.

![print](docs/prints/agendamento-etapas.png)

![print](docs/prints/agendamento-confirmado.png)

#### Consultar e cancelar reservas

1. Abra **Meus agendamentos** em `/meus-agendamentos`.
2. Consulte as listas de próximos e passados.
3. Para cancelar uma reserva futura, use a ação de cancelamento do respectivo agendamento e confirme no diálogo.

**Resultado esperado:** a cliente vê apenas as próprias reservas. A tela informa o resultado do cancelamento e, quando aplicável, o aviso de cancelamento tardio. O aviso de taxa é informativo; o app não processa pagamentos.

![print](docs/prints/meus-agendamentos.png)

### Jornada do dono do salão

#### Criar conta da empresa

1. Na página inicial, escolha **Tenho um salão** e **Criar conta**.
2. Informe seus dados, e-mail e senha, nome da empresa e os campos opcionais apresentados.
3. Envie o cadastro.

**Resultado esperado:** a conta administradora é vinculada à empresa e o responsável pode entrar na área administrativa.

![print](docs/prints/cadastro-salao.png)

#### Cadastrar serviços

1. Entre como administradora do salão.
2. No painel, abra **Serviços**.
3. Informe o nome, a duração e o preço do serviço.
4. Envie o formulário. Para alterar a situação ou os dados, use as ações disponíveis em cada item do catálogo.

**Resultado esperado:** o serviço aparece no catálogo da empresa e, quando ativo e associado a um profissional ativo, pode ser oferecido para agendamento.

![print](docs/prints/admin-servicos.png)

#### Cadastrar profissionais

1. No menu administrativo, abra **Profissionais**.
2. Informe o nome do profissional.
3. Selecione os serviços que ele realiza e envie o formulário.
4. Para editar, desativar ou reativar, use as ações do item correspondente.

**Resultado esperado:** o profissional aparece na equipe da empresa; os serviços associados determinam quais opções podem ser oferecidas com esse profissional.

![print](docs/prints/admin-profissionais.png)

#### Configurar horários de atendimento

1. Abra **Horários** no painel administrativo.
2. Selecione o profissional.
3. Escolha um ou mais dias da semana e informe os horários de início e término.
4. Cadastre o período. Use `HH:MM`; para término à meia-noite, informe `24:00`.
5. Edite ou remova períodos existentes pelas ações correspondentes.

**Resultado esperado:** os períodos cadastrados passam a definir quando o profissional pode receber agendamentos.

![print](docs/prints/admin-horarios.png)

#### Consultar a agenda e o dashboard

1. Abra **Agenda** para consultar as reservas da empresa.
2. Filtre pelo dia e, opcionalmente, pelo profissional.
3. Volte ao **Painel** para ver os indicadores, próximos horários e o resumo do salão.

**Resultado esperado:** a agenda exibe os agendamentos que correspondem aos filtros; o dashboard apresenta os indicadores e próximos horários da própria empresa.

![print](docs/prints/admin-agenda.png)

![print](docs/prints/admin-dashboard.png)

#### Copiar o link público

1. No painel administrativo, localize **Link público do salão**.
2. Use **Copiar link**.
3. Compartilhe a URL com as clientes. Ela também pode ser copiada manualmente a partir do link exibido.

**Resultado esperado:** a URL pública do salão fica disponível para divulgação e abre o fluxo de agendamento.

![print](docs/prints/link-publico.png)

### Jornada do administrador da plataforma

#### Pesquisar e filtrar salões

1. Abra `/platform/login` e autentique-se com uma conta `platform_admin autorizada`.
2. Na página `/platform`, informe o nome do salão no campo de busca e/ou um serviço no filtro.
3. Use **Buscar**.
4. Abra o card do salão desejado.

**Resultado esperado:** a lista exibe os salões correspondentes aos critérios; cada card leva à página de detalhes do salão.

![print](docs/prints/platform-busca.png)

#### Consultar dashboard e editar cadastros

1. Na página do salão, consulte o dashboard e as informações disponíveis.
2. Selecione a aba **Dados do salão**, **Serviços** ou **Profissionais**.
3. Edite os campos necessários e envie as alterações.

**Resultado esperado:** a página informa o resultado da operação e exibe os dados atualizados conforme as permissões do backend. As alterações são feitas somente pela área administrativa da plataforma.

![print](docs/prints/platform-dashboard.png)

![print](docs/prints/platform-edicao.png)

## 6. Exemplos de utilização

### Contas de demonstração de salões

As contas de demonstração dos salões usam a senha pública de demonstração `Demo@2026`:

| Salão | E-mail |
|---|---|
| Salão Aurora - Pinheiros | `dono.salao-aurora@demo.beautytime` |
| Barbearia Paulista | `dono.barbearia-paulista@demo.beautytime` |
| Estúdio Unhas Bela | `dono.estudio-unhas-bela@demo.beautytime` |

### Contas de demonstração de clientes

As contas de clientes de demonstração são `cliente1@demo.beautytime`, `cliente2@demo.beautytime`, `cliente3@demo.beautytime` e `cliente4@demo.beautytime`. Elas usam a mesma senha pública de demonstração `Demo@2026`.

### Acesso do administrador da plataforma

O administrador da plataforma entra em `/platform/login` com credenciais fornecidas pela equipe responsável. Não há credencial de demonstração de `platform_admin` publicada neste README.

### Endereços úteis

- Página inicial: `/`
- Busca pública de salões: `/saloes`
- Área da cliente: `/meus-agendamentos`
- Painel do salão: `/admin`
- Login da plataforma: `/platform/login`

O link público de cada empresa segue o formato `/agendar/{identificador}`. Os exemplos de demonstração incluem `salao-aurora`, `barbearia-paulista` e `estudio-unhas-bela`.
