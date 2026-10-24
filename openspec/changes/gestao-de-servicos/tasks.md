# Tasks

## 1. Preparação dos testes

- [ ] 1.1 Acrescentar `pytest` (versão fixada) a `requirements.txt`, instalar no `.venv` e criar `frontend/tests/unit/` e `frontend/tests/api/` com um `conftest.py`. Esse arquivo pula os testes de API quando `BEAUTYTIME_API_TESTS` não for `1`; verificar que `pytest frontend/tests` executa sem erros de coleta.

## 2. Frontend (Reflex): reorganização sem mudança de comportamento

- [ ] 2.1 Dividir `frontend/frontend/frontend.py` em `components/`, `states/session.py`, `states/public_company.py` e `pages/`, conforme o design. `frontend.py` fica responsável só por criar o app e registrar rotas, com rotas, textos e comportamentos atuais mantidos. Verificar que o app compila e inicia com `reflex run` sem erros.
- [ ] 2.2 Repetir o roteiro de identidade da change anterior para verificar que não houve regressão:
  - cadastro e login de cliente;
  - cadastro e login de administradora;
  - login pelo fluxo do outro tipo;
  - e-mail duplicado;
  - identificador inválido e duplicado;
  - `/agendar/{identificador}` existente e inexistente.

## 3. Backend (Xano): modelo e autorização

- [ ] 3.1 Consultar no Xano Developer MCP a sintaxe de tabelas com índice único composto, funções, `db.query` com filtro composto e tratamento de erro de índice único (`try_catch` ou equivalente). Registrar nas notas da tarefa o mecanismo escolhido para a violação do índice.
- [ ] 3.2 Criar `xano/table/service.xs` com:
  - `account_id` obrigatório;
  - `name`;
  - `name_key` privado;
  - `duration_minutes`;
  - `price_cents`;
  - `active` com padrão verdadeiro;
  - `created_at`;
  - índice único (`account_id`, `name_key`) e índice em `account_id`.

  Verificar que o arquivo passa na validação do Xano Developer MCP.
- [ ] 3.3 Criar a função `Autorizacao/empresa_da_administradora`. Ela retorna o `account_id` de um usuário `admin` com empresa e nega acesso a cliente, a usuário inexistente e a administrador sem empresa. Verificar que passa na validação do MCP.
- [ ] 3.4 Criar a função `Catalogo/validar_servico`, que normaliza o nome e valida:
  - nome com 2 a 80 caracteres;
  - duração múltipla de 5, de 5 a 480;
  - preço de 0 a 9.999.999 centavos.

  Ela devolve `name` e `name_key` e falha com os códigos `SERVICE_NAME_INVALID`, `SERVICE_DURATION_INVALID` e `SERVICE_PRICE_INVALID`. Verificar que passa na validação do MCP.
- [ ] 3.5 Atualizar `docs/domain-model.md` (seção Serviço) com:
  - limites de nome, duração e preço;
  - preço em centavos;
  - nome único por empresa sem diferenciar maiúsculas;
  - possibilidade de reativação e exclusão;
  - observação de que a regra de exclusão com vínculos será definida na change de profissionais.

  Verificar que o texto corresponde à spec `service-catalog`.

## 4. Backend (Xano): endpoints do catálogo

- [ ] 4.1 Criar o grupo de API `Catalogo` e os endpoints:
  - `GET admin/services`: empresa e serviços;
  - `POST admin/services`;
  - `PATCH admin/services/{service_id}`;
  - `PATCH admin/services/{service_id}/status`;
  - `DELETE admin/services/{service_id}`.

  Todos chamam primeiro `Autorizacao/empresa_da_administradora`, filtram por `id` e `account_id` (respondendo `notfound` para serviço de outra empresa), usam `Catalogo/validar_servico`, convertem a violação do índice em `SERVICE_NAME_TAKEN` e registram evento com `create_event_log`. Verificar que passam na validação do MCP.
- [ ] 4.2 Criar `GET public/services`, sem autenticação. Ele responde `notfound` para identificador desconhecido e devolve apenas `name`, `duration_minutes` e `price_cents` dos serviços ativos, ordenados por nome. Verificar que passa na validação do MCP.
- [ ] 4.3 Executar `xano workspace push --dry-run` e apresentar o resultado integralmente. Aguardar a confirmação explícita da usuária antes de qualquer push real, e só então executar o push. Verificar com `xano` ou pela API que o grupo `Catalogo` e os endpoints estão publicados.
- [ ] 4.4 Acrescentar a URL do grupo `catalogo` em `frontend/frontend/api_config.py` e escrever em `frontend/tests/api/` testes de API para todos os cenários de backend da spec `service-catalog`:
  - cadastro válido com nascimento ativo;
  - `account_id` enviado ignorado;
  - cliente e requisição sem sessão rejeitados;
  - limites aceitos e rejeitados de nome, duração e preço;
  - nome duplicado ignorando maiúsculas, incluindo um serviço inativo com o nome;
  - mesmo nome em outra empresa;
  - edição mantendo o nome;
  - edição, situação e exclusão de serviço de outra empresa e de serviço inexistente (`notfound`);
  - desativação e reativação refletidas na consulta pública;
  - nome liberado após exclusão;
  - consulta pública com ordem, campos permitidos, lista vazia e identificador desconhecido.

  Verificar que `BEAUTYTIME_API_TESTS=1 pytest frontend/tests/api` passa.

## 5. Frontend (Reflex): utilitários de apresentação

- [ ] 5.1 Criar `frontend/frontend/formatting.py`, sem importar Reflex, com:
  - formatação de duração ("45 min", "1h", "1h 30min");
  - formatação de preço ("R$ 1.234,50");
  - conversão de texto em formato brasileiro para centavos, rejeitando entradas inválidas.

  Verificar com testes em `frontend/tests/unit/` que cobrem limites e entradas inválidas.
- [ ] 5.2 Criar o mapeamento dos códigos `SERVICE_*` para o campo e a mensagem em português correspondentes, com mensagem genérica para erros sem código. Verificar com testes unitários.

## 6. Frontend (Reflex): área administrativa de serviços

- [ ] 6.1 Criar a proteção de rota da área administrativa, que valida a sessão com `auth/me` e exige o papel `admin`, e mudar o redirecionamento:
  - login e cadastro da administradora levam a `/admin/servicos`;
  - a cliente continua em `/boas-vindas`;
  - sessão de administradora em `/boas-vindas` é redirecionada para a área administrativa.

  Verificar em execução os três casos de acesso: sem sessão, com sessão de cliente e com sessão de administradora.
- [ ] 6.2 Criar `states/admin_services.py`, como subestado de `SessionState`, e a página `/admin/servicos` com:
  - cabeçalho com nome da empresa, "Ver página pública" e "Sair";
  - lista em cartões, com ativos primeiro e inativos diferenciados;
  - estados de carregamento, lista vazia com convite e erro com "Tentar novamente".

  Verificar em execução no viewport de celular (cerca de 390px) e de desktop.
- [ ] 6.3 Criar o diálogo de cadastro e edição com campos rotulados, duração com `step` 5 e preço com prefixo "R$". Ele mostra erros abaixo do campo com `role="alert"`, preserva os valores digitados e desabilita o envio durante a requisição. Verificar em execução o cadastro válido, a edição e cada erro de validação, inclusive o nome duplicado.
- [ ] 6.4 Criar as ações desativar e reativar, com aviso de sucesso, e a ação excluir, com diálogo de confirmação que mostra o nome do serviço. Verificar em execução que cancelar o diálogo não exclui e que confirmar remove o serviço da lista.

## 7. Frontend (Reflex): serviços na página pública

- [ ] 7.1 Carregar `public/services` em `states/public_company.py` e exibir na página `/agendar/{identificador}` a seção "Serviços":
  - nome, duração e preço formatados;
  - estado vazio "Esta empresa ainda não tem serviços disponíveis.";
  - erro de carregamento próprio, sem esconder os dados da empresa;
  - nenhum botão de agendar.

  Verificar em execução no celular, com empresa que tenha serviços, empresa sem serviços e falha simulada (URL do grupo inválida).

## 8. Verificação integrada

- [ ] 8.1 Rodar `pytest frontend/tests` (unitários) e `BEAUTYTIME_API_TESTS=1 pytest frontend/tests/api`, e percorrer o roteiro manual de ponta a ponta:
  1. Cadastrar uma administradora e verificar que ela chega a `/admin/servicos` com o estado vazio.
  2. Cadastrar três serviços, um deles com duração de 90 min e preço "45,50", e conferir a exibição "1h 30min · R$ 45,50".
  3. Tentar cadastrar o mesmo nome com outra caixa e ver o erro junto ao campo.
  4. Desativar um serviço, abrir `/agendar/{identificador}` em janela anônima e verificar que ele não aparece; reativá-lo e verificar que volta.
  5. Excluir um serviço, primeiro cancelando e depois confirmando.
  6. Entrar como cliente e tentar abrir `/admin/servicos`; verificar o redirecionamento ao login de administradora.
  7. Com uma segunda administradora, verificar que nenhum serviço da primeira empresa aparece na área dela.
  8. Repetir as telas no viewport de celular.

## Workflow follow-up

- Revisar a change e, após a aprovação, executar `/openspec-apply-change`.
- Após a implementação e a verificação, arquivar a change e confirmar que as specs `service-catalog` e `identity` foram consolidadas em `openspec/specs/`.
