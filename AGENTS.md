 # AGENTS.md — BeautyTime

Instruções para agentes de IA que trabalham neste projeto.

## Documentação

- Antes de qualquer alteração significativa, leia `docs/project-overview.md` e `docs/domain-model.md`.
- Em caso de conflito entre o que foi pedido e esses documentos, aponte o conflito antes de implementar.

## Desenvolvimento

- Toda mudança funcional deve passar pelo OpenSpec (Explore → Propose → Review → Apply → Archive).
- Implemente somente o que está nas tarefas da change atual. Não antecipe funcionalidades de outras changes.
- Não modifique funcionalidades não relacionadas à change atual sem justificativa.

## Arquitetura

- O backend é Xano, escrito em XanoScript, na pasta `xano/`.
- O frontend fica na pasta `frontend/` e deve ser implementado exclusivamente com Reflex. O ambiente Python é o `.venv` na raiz do projeto, e as dependências ficam em `requirements.txt`. Não introduza outra tecnologia de frontend sem uma decisão arquitetural explicitamente aprovada.
- Regras de negócio ficam no backend. O frontend apenas exibe dados e chama a API.
- Não introduza tecnologias, serviços ou bibliotecas novas sem justificativa.

## XanoScript

- Não presuma a sintaxe do XanoScript. Consulte a documentação pelo Xano Developer MCP antes de escrever código.
- Valide o XanoScript com o Xano Developer MCP antes de concluir uma tarefa.
- Não execute `xano workspace push` sem `--dry-run` antes e sem confirmação do usuário.

## Segurança

- Toda regra de autorização é aplicada no backend.
- Toda consulta e alteração de dados deve respeitar o isolamento por empresa.
- A cliente só acessa os próprios agendamentos; o administrador só acessa dados da própria empresa.
- Nunca grave tokens, senhas ou chaves em arquivos versionados.

## Código

- Reutilize código existente quando apropriado e evite duplicação.
- Prefira soluções simples e legíveis.

## Testes

- Toda mudança funcional deve ter uma forma de verificação descrita na change.
- Execute as verificações relevantes antes de marcar uma tarefa como concluída.

## Git

- Não faça commit nem push sem confirmação do usuário.
- Não versione `.venv/` nem arquivos com credenciais.

## Idioma

- Escreva documentação, artefatos OpenSpec e mensagens em português brasileiro.
