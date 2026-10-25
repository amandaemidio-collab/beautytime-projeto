# Design

## Context

Consulte `proposal.md` para a motivação e `specs/service-catalog/spec.md` e `specs/identity/spec.md` para os contratos observáveis desta mudança.

- **Xano:** `user` identifica clientes e administradoras por `role`; administradoras possuem `account_id`. `account` representa a empresa e tem `public_identifier` único. O grupo `Members & Accounts` já oferece a consulta pública da empresa.
- **Reflex:** as páginas e o estado atual estão concentrados em `frontend/frontend/frontend.py`. O token Xano fica no estado de backend. O frontend consome os grupos configurados em `frontend/frontend/api_config.py`.
- **Restrições:** o Xano é a autoridade para regras de negócio e isolamento por empresa. A mudança não introduz dependências; o `requirements.txt` oficial fica na raiz. O frontend deve sofrer somente extrações locais estritamente necessárias.

## Goals / Non-Goals

**Goals:**
- Implementar um padrão de autorização administrativa que derive a empresa da sessão autenticada e possa ser reutilizado em endpoints administrativos.
- Garantir persistência e consulta de serviços isoladas por empresa, com validação consistente no backend.
- Manter uma fatia funcional vertical: gestão administrativa e apresentação pública dos serviços ativos.
- Verificar os contratos por validação XanoScript, chamadas HTTP reais e inspeção manual da interface.

**Non-Goals:**
- Excluir fisicamente serviços ou definir regras de exclusão relacionadas a vínculos futuros.
- Criar infraestrutura de testes automatizados ou adicionar dependências de teste.
- Dividir o frontend em módulos de páginas, estados e componentes como objetivo próprio.
- Implementar seleção de serviço, profissionais, disponibilidade ou agendamentos.

## Decisions

### Persistir serviços vinculados à empresa e preservar o histórico por desativação

Criar uma tabela de serviço com `account_id` obrigatório, nome normalizado, duração em minutos, preço em centavos, situação e data de criação. O backend calcula a chave normalizada do nome; a requisição não define a empresa nem essa chave. Um índice único composto por empresa e chave do nome impede duplicatas inclusive em gravações concorrentes. A unicidade inclui serviços inativos, que podem ser reativados e não são removidos nesta mudança.

O nome mantém os limites já propostos: 2 a 80 caracteres após remover espaços nas extremidades, sem diferenciar maiúsculas e minúsculas para unicidade por empresa. A duração aceita inteiros de 15 a 480, inclusive, divisíveis por 15. O preço é persistido como inteiro de centavos, entre 0 e 9.999.999; a interface recebe/apresenta valor em reais e converte para centavos antes de enviar. Valores monetários não são armazenados como ponto flutuante.

**Alternativas consideradas:** calcular unicidade somente por consulta não protege contra gravações simultâneas; excluir fisicamente impediria preservar o serviço para relações e histórico futuros; armazenar preço decimal introduziria representação monetária menos previsível.

### Autorizar operações administrativas a partir da sessão

Criar uma função reutilizável que recebe o id autenticado, confirma que o usuário é `admin` e que possui uma empresa, e devolve o `account_id`. Todo endpoint administrativo chama essa função e usa somente o identificador retornado. `account_id` não é um campo de entrada aceito como fonte de escopo.

Ao editar ou alterar situação, carregar o serviço por `id` e `account_id`. Um serviço de outra empresa deve resultar no mesmo `notfound` de um id inexistente, sem revelar sua existência. A consulta pública localiza a empresa por `public_identifier` e devolve somente serviços ativos com os campos públicos definidos na spec.

**Alternativas consideradas:** confiar em um id enviado pelo browser ou filtrar apenas no Reflex não aplica autorização no backend; a função genérica de papéis do quick-start não resolve o vínculo da administradora com a empresa.

### Agrupar endpoints de catálogo no Xano

Criar o grupo `Catalogo` com estes contratos:

| Método e rota | Autenticação | Finalidade |
|---|---|---|
| `GET admin/services` | usuário | Dados públicos básicos da empresa e todos os seus serviços, ativos e inativos |
| `POST admin/services` | usuário | Cadastrar serviço ativo |
| `PATCH admin/services/{service_id}` | usuário | Alterar nome, duração ou preço com as mesmas validações do cadastro |
| `PATCH admin/services/{service_id}/status` | usuário | Ativar ou desativar serviço da própria empresa |
| `GET public/services?public_identifier=` | nenhuma | Serviços ativos, sem ids internos, ordenados por nome |

O grupo não terá endpoint DELETE. A validação comum é aplicada no cadastro e na edição. A API usa códigos estáveis para erros de nome, duração e preço, incluindo colisões do índice único, para permitir mensagens específicas no formulário. Operações administrativas que alteram dados mantêm o registro de eventos usado pelo workspace.

**Alternativas consideradas:** colocar catálogo no grupo de autenticação misturaria responsabilidades; expor ids internos na resposta pública não é necessário para a apresentação informativa desta mudança.

### Manter o frontend no módulo existente

Reutilizar `frontend.py`, o estado atual, `api_client.py`, `api_config.py` e `theme.py`. Adicionar apenas a configuração de URL do grupo e o código mínimo de estado/renderização necessário para a lista, formulário, situação e seção pública. Extrair um helper ou componente somente se isso simplificar diretamente as telas novas; nenhuma estrutura modular ampla é requisito.

A administradora é encaminhada a `/admin/servicos` após login ou cadastro. O carregamento da rota verifica a identidade e o papel com `auth/me`; o backend continua sendo a barreira de autorização efetiva. A cliente permanece em `/boas-vindas`. A gestão lista ativos e inativos, permite criar/editar e ativar/desativar; não há ação de excluir. A interface pública apresenta apenas os ativos, sem ação de agendamento.

**Apresentação e erros:** duração em formato legível (por exemplo, `45 min` ou `1h 30min`); preço em reais com duas casas decimais. No formulário administrativo, a duração é escolhida em uma lista com opções de 15 em 15 minutos, de 15 minutos a 8 horas, com rótulos legíveis (`15 min`, `30 min`, `45 min`, `1h`, `1h 15min` etc.); o valor enviado à API continua sendo a duração inteira em minutos. A validação de duração no backend permanece inalterada. O formulário converte o valor decimal do preço em centavos inteiros antes da chamada HTTP. Erros de validação aparecem junto ao campo correspondente e os valores preenchidos são preservados para nova tentativa; carregamento, lista vazia e falha de consulta dos serviços têm estados explícitos. A falha da lista pública não deve ocultar os dados públicos da empresa.

**Alternativas consideradas:** criar uma árvore de páginas/estados/componentes agora ampliaria o risco de regressão sem entregar capacidade adicional; testes de browser automatizados e infraestrutura pytest foram explicitamente retirados do escopo.

### Verificação e publicação

Consultar a documentação Xano Developer MCP antes de escrever XanoScript, validar cada artefato XanoScript pelo MCP e verificar os contratos publicados por chamadas HTTP reais. Descrever os dados necessários, a chamada e o resultado esperado na própria tarefa. A interface é validada manualmente em fluxos reais e em viewport móvel.

Executar `xano workspace push --dry-run`, apresentar o resultado e aguardar confirmação explícita antes de qualquer push real. O dry-run não autoriza publicação.

**Alternativas consideradas:** não adicionar pytest ou outra dependência; comandos manuais HTTP evitam criar infraestrutura de teste fora do escopo e validam o contrato real da API.

## Risks / Trade-offs

- [Uma chamada de API pode enviar valor monetário malformado ou fracionado] → Converter e validar os centavos no backend; converter a entrada em reais no frontend e verificar limites via chamadas HTTP.
- [Duas criações simultâneas podem tentar usar o mesmo nome] → Aplicar índice único composto no banco e mapear a violação para o erro de nome em uso, após confirmar o mecanismo suportado pelo Xano.
- [Um endpoint administrativo pode escapar ao escopo da empresa] → Reutilizar a função que deriva a empresa da sessão; testar com duas administradoras, cliente e requisição sem sessão.
- [Uma refatoração desnecessária pode regredir fluxos entregues] → Manter a estrutura Reflex existente e verificar login, cadastro e página pública da empresa no roteiro manual.
- [A publicação pode alterar o workspace remoto de modo inesperado] → Inspecionar o dry-run e aguardar confirmação explícita antes de publicar.
- [Desativação mantém o nome reservado] → Documentar e verificar que a unicidade inclui serviços inativos; a reativação preserva nome, duração e preço.

## Migration Plan

1. Validar a tabela, as funções e os endpoints XanoScript com o Xano Developer MCP.
2. Executar `xano workspace push --dry-run`, revisar o resultado e aguardar autorização explícita antes do push real.
3. Confirmar por chamadas HTTP os endpoints administrativos e públicos, inclusive a autorização e os erros de validação.
4. Publicar o frontend com área de gestão e apresentação pública, verificando manualmente os fluxos da cliente e administradora.
5. **Rollback:** reverter as alterações de código e, caso seja necessária alteração remota no Xano, avaliar o dry-run reverso e obter confirmação antes de qualquer publicação. Não apagar serviços fisicamente como forma de rollback.

## Open Questions

Nenhuma decisão necessária para esta Change permanece em aberto. O comportamento futuro de profissionais, vínculos, horários e agendamentos será definido nas Changes correspondentes.
