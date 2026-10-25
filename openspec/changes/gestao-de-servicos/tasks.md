# Tasks

## 1. Modelo e regras no Xano

- [x] 1.1 Consultar a documentação Xano Developer MCP e criar a tabela de serviços, a função de autorização que deriva a empresa da sessão e a função compartilhada de validação; validar todos os arquivos XanoScript pelo MCP. Atualizar `docs/domain-model.md` com nome de 2–80 caracteres único por empresa sem diferenciar caixa, duração inteira de 15–480 minutos múltipla de 15, preço em centavos de 0–9.999.999 e preservação do serviço por desativação; conferir manualmente cada regra contra `specs/service-catalog/spec.md`.

## 2. APIs administrativas

- [x] 2.1 Implementar no grupo `Catalogo` os endpoints autenticados de listagem e cadastro; garantir que a empresa venha da função de autorização e que serviço novo seja ativo. Validar os arquivos pelo Xano Developer MCP e, após publicação autorizada, chamar os endpoints por HTTP com administradora, cliente e sem sessão; conferir empresa correta, rejeição por tipo/sessão e lista vazia.
- [x] 2.2 Implementar os endpoints autenticados de edição de nome, duração e preço e de ativação/desativação, reutilizando a validação e o isolamento por empresa sem remover registros. Validar XanoScript pelo MCP e, por HTTP, conferir edição válida, nome mantido, limites de duração/preço, alternância de situação, preservação dos dados e resposta `notfound` para serviço inexistente ou de outra empresa.
- [x] 2.3 Implementar a consulta pública sem autenticação por identificador da empresa, retornando apenas serviços ativos e campos públicos, em ordem alfabética. Validar XanoScript pelo MCP e, por HTTP, conferir empresa com serviços ativos/inativos, lista vazia e identificador desconhecido.

## 3. Publicação e verificação HTTP do backend

- [ ] 3.1 Executar `xano workspace push --dry-run`, revisar e apresentar o resultado e aguardar confirmação explícita antes de qualquer push real. Após publicação autorizada, percorrer por chamadas HTTP reais os cenários de `service-catalog`: limites de nome, duração e preço; nome repetido com variação de caixa, inclusive serviço inativo; mesmo nome em outra empresa; campo de empresa forjado ignorado; cliente e sessão ausente rejeitados; isolamento entre duas empresas; edição válida; serviço alheio/inexistente como `notfound`; desativação/reativação refletidas na resposta pública; lista vazia, identificador desconhecido e resposta pública sem campos internos. Registrar os resultados sem criar infraestrutura automatizada.

## 4. Área administrativa Reflex

- [x] 4.1 Integrar no frontend Reflex existente a rota protegida `/admin/servicos`, a listagem de serviços ativos e inativos, estados de carregamento/vazio/erro e o redirecionamento da administradora após login/cadastro, mantendo a cliente em `/boas-vindas`. Fazer somente extrações locais que sejam necessárias às telas. Verificar manualmente no navegador: sessão ausente e sessão de cliente são redirecionadas ao login administrativo; administradora vê somente sua lista e o link público; login/cadastro preservam seus destinos definidos.
- [x] 4.2 Implementar o formulário de cadastro e edição na área administrativa, com nome, duração em minutos múltipla de 15 e preço digitado/exibido em reais, convertido para centavos na chamada à API; mostrar erros junto ao campo e preservar os valores. Verificar manualmente no navegador e por chamadas HTTP reais cadastro/edição válidos, limites aceitos/rejeitados e nome duplicado, incluindo colisão sem diferenciar maiúsculas.
- [x] 4.3 Implementar controles de ativação e desativação sem ação de exclusão. Verificar manualmente no navegador que a situação atualiza a lista administrativa e, por HTTP, que serviço desativado não aparece na resposta pública e reativado volta a aparecer com os mesmos dados.

## 5. Página pública e verificação integrada

- [ ] 5.1 Exibir os serviços ativos em `/agendar/{identificador}`, com duração legível e preço em reais; preservar os dados da empresa nos estados de carregamento, lista vazia e falha específica ao carregar serviços. Verificar manualmente a rota em celular e desktop para empresa com serviços, sem serviços e com falha de consulta; confirmar por HTTP que somente ativos e campos públicos são retornados.
- [ ] 5.2 Percorrer manualmente o fluxo ponta a ponta e registrar o resultado: cadastrar administradora e empresa; entrar na área administrativa vazia; criar, editar, desativar e reativar serviços; conferir conversão de preço e duração; rejeitar nome duplicado; conferir a página pública com ativos apenas; testar rota protegida como cliente; e repetir o isolamento com uma segunda empresa. Confirmar que os fluxos anteriores de login/cadastro e `/agendar/{identificador}` da fundação continuam funcionando.

## Workflow follow-up

- Após revisão e conclusão das tarefas, arquivar a Change e confirmar que as specs `service-catalog` e `identity` foram consolidadas em `openspec/specs/`.
