# Proposal

## Why

Após o login, a administradora precisa de uma entrada clara para as funções da empresa, com acesso ao catálogo existente e às próximas áreas de gestão. Também precisa cadastrar e manter os profissionais e os serviços que cada um realiza, com os dados isolados por empresa no backend.

## What Changes

- Criar um painel inicial administrativo acessível após login e cadastro, com o menu Serviços, Profissionais, Horários e Agenda.
- Manter Serviços como funcionalidade disponível; apresentar Horários e Agenda como “Em breve” até que suas changes sejam implementadas.
- Mostrar no painel o link público do salão e uma ação para copiá-lo, sem indicadores ou números de resumo.
- Permitir à administradora cadastrar, listar, editar, desativar e reativar profissionais da própria empresa. O cadastro contém nome e um ou mais serviços ativos da empresa que o profissional realiza; novos profissionais começam ativos.
- Preservar registros de profissionais, sem exclusão física. Profissionais não têm login nesta fase.
- Aplicar autorização e isolamento por empresa nos endpoints do backend, seguindo o padrão da gestão de serviços.
- Manter a página pública `/agendar/{identificador}` sem exibir profissionais; essa apresentação pertence à change de agendamento.
- Descrever verificações em cada tarefa, usando testes manuais e chamadas HTTP reais, sem infraestrutura de testes automatizados.

### Fora do escopo

- Horários de atendimento, disponibilidade e agendamentos.
- Exibição ou seleção de profissionais na página pública `/agendar/{identificador}`.
- Foto, descrição, login ou conta própria do profissional.
- Indicadores, métricas ou números no painel inicial.
- Implementação das áreas de Horários e Agenda, que permanecem apenas como “Em breve”.
- Exclusão física de profissionais.
- Criação de infraestrutura automatizada de testes ou inclusão de dependências de teste.

## Capabilities

### New Capabilities

- `admin-dashboard`: painel inicial, navegação administrativa, link público copiável e áreas ainda não disponíveis.
- `professional-management`: cadastro e manutenção de profissionais e dos serviços ativos que realizam, isolados por empresa.

### Modified Capabilities

- `identity`: encaminhar a administradora ao painel inicial após login e cadastro, preservando o destino atual da cliente.

## Impact

- **Frontend Reflex:** adicionar o painel inicial, navegação entre o painel, Serviços e Profissionais, botão de cópia do link e telas protegidas de profissionais. A rota `/admin/servicos` continua disponível; login e cadastro de administradora passam a encaminhar para o painel.
- **Backend Xano:** criar persistência e APIs administrativas para profissionais e vínculo com serviços; a identidade autenticada determina a empresa e serviços associados são validados no backend como ativos e pertencentes à mesma empresa. Não será criada API pública de profissionais nesta change.
- **Página pública:** `/agendar/{identificador}` permanece com os dados e serviços já apresentados, sem profissionais.
- **Verificação:** validar XanoScript pelo Xano Developer MCP; descrever validação manual da interface e chamadas HTTP reais nas tarefas. Publicação real no Xano exige confirmação explícita após `xano workspace push --dry-run`.
- **Dependências:** nenhuma dependência nova e nenhuma infraestrutura automatizada de testes.

### Premissas

- “Serviços que realiza” significa pelo menos um serviço ativo da empresa; sem serviço ativo, a interface informa que é necessário cadastrar um serviço antes de criar um profissional.
- O link público é apresentado e copiado como URL completa do ambiente atual, terminando em `/agendar/{identificador}`.
