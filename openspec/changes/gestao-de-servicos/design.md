# Design

## Context

Situação atual relevante (motivação em `proposal.md`):

- **Xano.** `user` tem `role` (`client`/`admin`) e `account_id`, obrigatório só para administradores. `account` representa a empresa e tem `public_identifier` único.
  - Os grupos de API existentes são `Authentication` e `Members & Accounts`, este último com `company/public`.
  - Não existe função de autorização ligada ao domínio. `Getting Started Template/role_based_access_control` é genérica do quick-start.
  - Os endpoints que alteram dados registram eventos com `Getting Started Template/create_event_log`.
- **Reflex.** Todo o frontend está em `frontend/frontend/frontend.py` (836 linhas), com um único `State`.
  - O token Xano fica em `_auth_token`, uma variável de backend que não vai ao navegador.
  - Erros da API são traduzidos procurando trechos de texto na mensagem do Xano (`_api_error`, `_identifier_error`).
  - Depois do login ou cadastro, todos os usuários vão para `/boas-vindas`.
- **Testes.** O repositório não tem testes automatizados; a change anterior foi verificada manualmente.

## Goals / Non-Goals

**Goals:**
- Criar um padrão de autorização de administradora que as próximas entidades da empresa (profissionais, horários, agendamentos) possam reutilizar sem mudança.
- Garantir no banco a unicidade do nome por empresa, inclusive com cadastros simultâneos.
- Deixar o frontend dividido de forma que cada change futura acrescente arquivos, em vez de crescer um único módulo.
- Ter testes automatizados que cubram os cenários das specs pela API real, sem guardar credenciais no repositório.

**Non-Goals:**
- Paginação, busca ou filtros na lista de serviços; o volume esperado por empresa é pequeno.
- Testes de interface com navegador automatizado.
- Refatorar a lógica de identidade além do necessário para mudar o redirecionamento e separar os módulos.

## Decisions

### Tabela `service` com nome normalizado e índice único composto

Nova tabela `service` com os campos:
- `account_id`: obrigatório, referência a `account`;
- `name`: texto, sem espaços nas extremidades;
- `name_key`: nome sem espaços nas extremidades e em minúsculas, privado;
- `duration_minutes`: inteiro;
- `price_cents`: inteiro;
- `active`: booleano, padrão verdadeiro;
- `created_at`.

Índices:
- único em (`account_id`, `name_key`);
- btree em `account_id`.

O backend calcula `name_key` e nunca o recebe na requisição. A unicidade fica no banco porque uma verificação prévia isolada não protege cadastros simultâneos, o mesmo motivo usado para o identificador público.

O endpoint ainda faz uma verificação prévia para devolver uma mensagem clara. Se dois cadastros simultâneos passarem por ela, a violação do índice é tratada como o mesmo erro de nome em uso.

- *Alternativa — comparar sem diferenciar maiúsculas na consulta, sem índice:* não garante unicidade sob concorrência.
- *Alternativa — guardar o preço em decimal:* centavos inteiros evitam erros de arredondamento e simplificam a validação de limites. A conversão para "R$ 45,00" é apresentação e fica no frontend.

A exclusão é física (`db.del`). Ainda não há entidades que referenciem serviços. A regra de exclusão quando houver profissionais ou agendamentos vinculados fica para a change que criar esses vínculos.

### Função reutilizável de autorização da administradora

Criar a função `Autorizacao/empresa_da_administradora`:
- recebe o id do usuário autenticado;
- carrega o `user` correspondente;
- exige `role == "admin"` e `account_id` preenchido, retornando acesso negado caso contrário;
- devolve o `account_id`.

Todo endpoint administrativo começa chamando essa função com `$auth.id` e usa **apenas** o valor retornado para filtrar e gravar.

Os endpoints não declaram `account_id` como entrada. Assim, um `account_id` enviado no corpo é ignorado pelo Xano, como prevê o cenário "Tentativa de indicar outra empresa".

**Serviço de outra empresa.** Para editar, alterar situação ou excluir, o serviço é buscado por `id` **e** `account_id`. Se não for encontrado, a resposta é `notfound`, igual à de um serviço inexistente. Isso evita revelar que o id existe em outra empresa.

- *Alternativa — reutilizar `role_based_access_control`:* ela segue o modelo de papéis genérico do quick-start e não resolve a empresa. Adaptá-la mudaria código fora do escopo.

### Novo grupo de API `Catalogo`

Criar o grupo `Catalogo`. Nele ficam os endpoints de gestão do catálogo e também as consultas públicas do catálogo, que as próximas changes (profissionais) vão estender. O nome sem acento evita problemas em URLs e no CLI.

| Método e rota | Auth | Finalidade |
|---|---|---|
| `GET admin/services` | user | Empresa da administradora (`name`, `public_identifier`) e todos os seus serviços |
| `POST admin/services` | user | Cadastrar (`name`, `duration_minutes`, `price_cents`) |
| `PATCH admin/services/{service_id}` | user | Editar nome, duração e preço |
| `PATCH admin/services/{service_id}/status` | user | Ativar ou desativar (`active`) |
| `DELETE admin/services/{service_id}` | user | Excluir |
| `GET public/services?public_identifier=` | — | Serviços ativos da empresa: `name`, `duration_minutes`, `price_cents`, por nome |

A listagem administrativa devolve os dados públicos da empresa para que a área administrativa mostre o nome do salão e o link público sem chamar outro endpoint.

A mudança de situação tem endpoint próprio para que a edição de dados e a ativação ou desativação não se misturem num mesmo formulário.

Os itens da listagem administrativa trazem `id`, necessário para as ações. A resposta pública não traz ids, conforme decidido no Explore. A seleção de serviço, que vai precisar de id, entra na change de agendamento.

A validação de nome, duração e preço é escrita uma vez numa função compartilhada (`Catalogo/validar_servico`), usada pelo cadastro e pela edição.

Cadastro, edição, alteração de situação e exclusão registram evento com `create_event_log`, como os endpoints existentes.

### Códigos de erro estáveis no início da mensagem

Os erros de validação dos novos endpoints usam mensagens que começam com um código fixo:
- `SERVICE_NAME_INVALID`
- `SERVICE_NAME_TAKEN`
- `SERVICE_DURATION_INVALID`
- `SERVICE_PRICE_INVALID`

Cada código é seguido de `:` e de um texto livre.

O frontend associa cada código a um campo e a uma mensagem em português. Hoje a tradução procura trechos de texto em inglês, o que quebra quando o texto muda. Os endpoints antigos não mudam.

### Frontend dividido em módulos

```text
frontend/frontend/
├── frontend.py          # cria o app e registra as rotas
├── api_client.py, api_config.py, theme.py   # inalterados (api_config ganha o grupo "catalogo")
├── formatting.py        # funções puras: duração, preço, conversão "45,00" → 4500
├── components/          # marca, cartão/página, campo de formulário, estados vazio/erro/carregando
├── states/
│   ├── session.py       # SessionState: _auth_token, papel, login/cadastro/logout, guarda de rota
│   ├── public_company.py
│   └── admin_services.py  # subestado de SessionState
└── pages/               # home, cliente, administradora, boas-vindas, página pública, admin/serviços
```

O estado de serviços é um **subestado** de `SessionState`, para ler `_auth_token` sem expô-lo ao navegador. A separação mantém rotas, textos e comportamentos atuais; a verificação de regressão entra nas tarefas.

`formatting.py` não importa Reflex, o que permite testá-lo sem subir o app.

### Área administrativa e redirecionamento

- **Rota da área administrativa:** `/admin/servicos`. Ela é a página inicial da administradora nesta change.
- **Proteção da rota:** o `on_load` valida a sessão com `auth/me` e exige o papel `admin`; sem isso, redireciona para `/admin/login`. O backend continua sendo a barreira real.
- **Redirecionamento:**
  - login e cadastro da administradora levam a `/admin/servicos`;
  - os da cliente continuam levando a `/boas-vindas`;
  - se uma sessão de administradora abrir `/boas-vindas`, ela é redirecionada para a área administrativa.

**Padrões de UI e UX:**
- **Layout:** pensado primeiro para o celular. Cada serviço aparece como um cartão: nome, "45 min · R$ 45,00", indicação "Inativo" e menu de ações.
- **Toque:** botões com pelo menos 44px de altura; a ação principal ocupa a largura toda no celular.
- **Cadastro e edição:** um diálogo com um único formulário.
  - Campos rotulados.
  - Duração em minutos (`type=number`, `step=5`, `min=5`, `max=480`).
  - Preço no formato brasileiro, com o prefixo "R$" visível.
  - Erros aparecem abaixo do campo (`role="alert"`, `aria-invalid`), e os valores digitados são preservados.
  - O botão fica desabilitado e mostra indicador enquanto a requisição está em andamento.
- **Confirmações:**
  - Excluir exige confirmação num diálogo de alerta, com o nome do serviço e a ação destrutiva em vermelho.
  - Desativar não pede confirmação, porque pode ser desfeito; a mudança aparece num aviso de sucesso.
- **Estados da tela:**
  - carregando: esqueleto da lista;
  - lista vazia: convite "Cadastre seu primeiro serviço";
  - erro de carregamento: mensagem e botão "Tentar novamente".
- **Ordem da lista:** ativos primeiro, depois inativos com opacidade reduzida; cada grupo em ordem alfabética.
- **Cabeçalho:** nome da empresa, link "Ver página pública" e "Sair".
- **Página pública:**
  - Lista de serviços com nome à esquerda e duração e preço à direita.
  - Sem botões que pareçam permitir agendar, já que a seleção ainda não existe.
  - A seção "Serviços" tem estados próprios de carregamento, lista vazia e erro, independentes do cabeçalho da empresa.

Toda a paleta e tipografia vêm de `theme.py`.

### Testes com pytest e roteiro manual

Acrescentar `pytest` a `requirements.txt`. É uma dependência só de desenvolvimento, padrão em Python, e não muda a execução do app. A alternativa `unittest`, da biblioteca padrão, resolveria, mas deixaria os testes de API mais verbosos.

- **`frontend/tests/unit/`:**
  - `formatting.py`: duração, preço e conversão "45,00" ↔ 4500, incluindo entradas inválidas;
  - tradução dos códigos de erro para campos.
- **`frontend/tests/api/`:**
  - Testes contra a API real do workspace, cobrindo os cenários de `service-catalog`:
    - limites de validação;
    - nome duplicado ignorando maiúsculas;
    - mesmo nome em outra empresa;
    - acesso de cliente, de sessão inexistente e de outra empresa;
    - desativação, reativação e exclusão;
    - forma da resposta pública.
  - Cada execução cria as próprias contas de administradora e cliente com e-mails aleatórios. Assim nenhuma credencial é guardada no repositório.
  - Esses testes rodam só com `BEAUTYTIME_API_TESTS=1`, para não fazer chamadas de rede por acidente.
- **Roteiro manual:** em `tasks.md`, para os comportamentos de interface que os testes automatizados não cobrem.

Testes nativos do Xano não serão usados nesta change. Os testes de API pela fronteira HTTP verificam o mesmo contrato e servem para qualquer endpoint.

## Risks / Trade-offs

- [O tratamento da violação do índice único depende de como o Xano expõe esse erro] → Na aplicação, consultar o Xano Developer MCP sobre como capturar o erro (por exemplo, `try_catch`). Se não for possível distinguir o erro, manter a verificação prévia e documentar que a corrida restante devolve um erro genérico, sem duplicar dados.
- [Os testes de API criam contas e empresas no workspace] → Os dados do workspace são de teste. Os testes usam o prefixo `teste-api-` nos identificadores e excluem os serviços que criam. As contas permanecem, porque não existe endpoint de exclusão de conta.
- [A divisão do frontend pode quebrar fluxos já entregues] → Separar os módulos numa tarefa própria, antes de qualquer funcionalidade nova, e repetir o roteiro de identidade da change anterior antes de seguir.
- [A sessão Reflex se perde se o servidor reiniciar] → Comportamento já existente. A proteção de rota redireciona para o login, sem erro. Persistir a sessão fica fora do escopo.
- [Excluir serviços passará a ter impacto quando existirem vínculos] → Registrar em `docs/domain-model.md` que a regra de exclusão com dependências será definida na change de profissionais.

## Migration Plan

1. Criar a tabela, as funções e o grupo `Catalogo` em `xano/`, validar pelo Xano Developer MCP e executar `xano workspace push --dry-run`. Apresentar o resultado e aguardar confirmação explícita antes do push real.
2. Os endpoints existentes não mudam de contrato. Não há migração de dados.
3. Publicar o frontend reorganizado e os novos fluxos; rodar os testes unitários, os de API e o roteiro manual.
4. **Rollback:** reverter os commits do frontend e publicar novamente a versão anterior de `xano/` sem a tabela e o grupo, com dry-run e confirmação. Como nada referencia `service`, removê-la não afeta identidade nem empresa.
