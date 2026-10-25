# Design

## Context

Consulte `proposal.md` e as specs delta para motivação e contratos funcionais. O frontend Reflex mantém estado, páginas e rotas em `frontend/frontend/frontend.py`; o cliente HTTP e as URLs por grupo ficam em `frontend/frontend/api_client.py` e `frontend/frontend/api_config.py`. Login e cadastro da administradora atualmente levam para `/admin/servicos`, cuja rota valida o papel com `auth/me`. O endpoint `GET Catalogo/admin/services` já retorna nome e identificador público da empresa autenticada.

No Xano, a empresa da administradora é obtida da sessão por `Catalogo/authorize_admin`, e os serviços são armazenados em `service` com `account_id`. O backend é a autoridade para autorização, validação de vínculos e isolamento empresarial.

## Goals / Non-Goals

**Goals:**
- Aproveitar os padrões existentes de sessão, autorização por empresa, chamadas HTTP e componentes Reflex.
- Manter `/admin/servicos` funcional e adicionar painel inicial e gestão protegida de profissionais.
- Persistir profissionais e associações profissionais-serviços sem permitir vínculos entre empresas.
- Preservar a página pública atual, sem endpoint ou exibição pública de profissionais.

**Non-Goals:**
- Criar infraestrutura modular ampla no frontend ou dependências novas.
- Implementar horários, disponibilidade, agenda ou fluxo de agendamento.
- Incluir métricas no painel ou dados biográficos dos profissionais.

## Decisions

### Usar `/admin` como painel inicial e preservar a rota de serviços

Registrar `/admin` como a nova rota de entrada administrativa. Login e cadastro de administradora redirecionam para essa rota; o fluxo da cliente continua em `/boas-vindas`. O painel e as demais rotas administrativas validam sessão e papel, enquanto cada endpoint Xano continua aplicando a autorização real.

Os itens Serviços e Profissionais navegam para `/admin/servicos` e `/admin/profissionais`. Horários e Agenda são apresentados sem navegação funcional e com “Em breve”. Não criar rotas provisórias para essas funções.

**Alternativa considerada:** transformar `/admin/servicos` em painel exigiria deslocar o catálogo já implementado e quebraria URLs existentes. Uma rota raiz administrativa separa a navegação sem remover a tela atual.

### Reutilizar a consulta administrativa existente para os dados da empresa

O painel pode usar `GET Catalogo/admin/services` para obter nome e identificador público da empresa, apresentados também na resposta do catálogo atual. Assim, a inclusão do painel não exige um endpoint paralelo apenas para dados já disponíveis. O estado não deve usar `account_id` enviado pelo navegador para determinar empresa.

Montar a URL pública completa com a origem atual do aplicativo e `/agendar/{identificador}`. O botão usa a capacidade de área de transferência do navegador sem nova dependência, informa sucesso e mantém a URL visível caso a cópia falhe.

**Alternativa considerada:** criar uma API de dashboard duplicaria dados e regras do endpoint existente. Uma URL relativa não atende à premissa de entregar um link completo que possa ser compartilhado diretamente.

### Modelar profissionais e a relação com serviços no Xano

Adicionar uma tabela `professional` com empresa obrigatória, nome, situação e data de criação, e uma relação muitos-para-muitos com `service`, com unicidade do par profissional-serviço. O nome não recebe uma regra de unicidade, pois essa decisão não foi definida pelo grupo.

Os endpoints administrativos usam a função existente `Catalogo/authorize_admin`. A listagem retorna somente profissionais da empresa da sessão, incluindo situação e serviços associados, e fornece a lista de serviços ativos da mesma empresa para os formulários. Cadastro e edição validam no backend todos os IDs enviados: deve haver pelo menos um, e todos devem apontar a serviços ativos da empresa autenticada. A empresa nunca é escolhida pela requisição.

Separar operações em consulta/listagem e cadastro, edição e alteração de situação; não criar endpoint DELETE. As atualizações de profissional e de suas associações devem evitar estado parcial: validar todos os serviços e o profissional da empresa antes de persistir as alterações. Serviços já associados que depois sejam desativados permanecem relacionados e podem ser identificados como inativos na interface, mas não podem ser selecionados em novos cadastros ou alterações.

**Alternativas consideradas:** armazenar IDs de serviços em texto ou como lista dentro do profissional enfraqueceria integridade e filtragem; uma tabela de relação representa o vínculo e permite validar cada serviço contra a empresa. Confiar apenas no frontend deixaria abertas associações forjadas.

### Manter a implementação Reflex concentrada no módulo atual

Reutilizar o estado e os padrões já presentes em `frontend/frontend/frontend.py`, adicionando os campos e eventos necessários para carregar, criar, editar, ativar e desativar profissionais e para o painel. Manter as configurações de API em `api_config.py` e chamadas pelo `api_client.py`. Extrair lógica somente se for necessária para evitar duplicação imediata entre telas.

**Alternativa considerada:** criar módulos e dependências de UI agora aumentaria a superfície de alteração sem ser necessário para esta fatia.

### Validar por chamadas HTTP reais e inspeção manual

Cada tarefa descreve chamadas HTTP reais aos endpoints e verificações manuais no navegador, incluindo sessões de administradora, cliente e sem autenticação, duas empresas e vínculos inválidos. Não adicionar suíte automatizada ou infraestrutura de teste. Consultar e validar os arquivos XanoScript com o Xano Developer MCP durante a implementação.

**Alternativa considerada:** testes automatizados exigiriam infraestrutura expressamente fora do escopo definido pelo grupo.

## Risks / Trade-offs

- [A relação de um profissional com vários serviços pode ficar parcialmente gravada se uma operação falhar] → Validar a associação inteira antes de alterar os registros e usar a estratégia transacional ou compensatória suportada pelo Xano, validada na implementação.
- [A permissão de área de transferência pode ser negada pelo navegador] → Manter o endereço visível e comunicar claramente a falha.
- [O frontend pode ser aberto diretamente por uma sessão de cliente] → Validar papel em todas as rotas administrativas e manter a autorização de cada operação no backend.
- [Serviços vinculados podem ser desativados após associação] → Preservar o vínculo existente e impedir que serviço inativo seja enviado em novos cadastros ou edições.

## Migration Plan

1. Criar as tabelas e endpoints no workspace Xano e validar cada arquivo XanoScript pelo Xano Developer MCP.
2. Executar `xano workspace push --dry-run`, revisar o resultado e solicitar confirmação explícita antes de qualquer publicação real.
3. Com a publicação autorizada, testar endpoints com chamadas HTTP reais antes de habilitar as telas Reflex.
4. Publicar a interface com `/admin` como novo destino de login/cadastro, mantendo `/admin/servicos` acessível.
5. Se houver rollback, reverter as rotas e telas e deixar os registros persistidos sem exclusão física; não remover dados profissionais já criados.

## Open Questions

Nenhuma. As premissas de serviço obrigatório e URL completa copiável estão registradas na proposta.
