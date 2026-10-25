# Proposal

## Why

Depois da fundação de identidade e empresa, a administradora ainda não consegue manter o catálogo do estabelecimento, e a página pública `/agendar/{identificador}` não informa quais serviços são oferecidos. Esta mudança entrega a gestão essencial de serviços e sua apresentação pública, estabelecendo também o isolamento por empresa no backend.

## What Changes

- Permitir que a administradora liste, cadastre, edite, ative e desative serviços da própria empresa.
- Validar o nome (2 a 80 caracteres, único por empresa sem diferenciar maiúsculas e minúsculas), duração inteira em minutos (múltipla de 15, entre 15 e 480) e preço em centavos inteiros. Serviços novos começam ativos.
- Obter a empresa exclusivamente da sessão autenticada nos endpoints administrativos; não aceitar identificador de empresa fornecido pelo frontend como fonte de autorização ou propriedade.
- Expor publicamente apenas serviços ativos da empresa identificada pelo identificador público, com nome, duração e preço.
- Exibir os serviços ativos em `/agendar/{identificador}` e oferecer uma área administrativa protegida para gerenciá-los.
- Manter a implementação Reflex no módulo atual, reorganizando código somente se for necessário para integrar essas telas.
- Atualizar `docs/domain-model.md` com as regras acordadas para Serviço.
- Verificar as tarefas com validação XanoScript, chamadas HTTP reais e verificações manuais da interface, conforme aplicável. Não criar infraestrutura de testes automatizados nesta mudança.

### Fora do escopo

- Exclusão física de serviços: um serviço existente pode ser desativado ou reativado, preservando seus dados.
- Profissionais, relação profissional-serviço, horários, disponibilidade e agendamentos.
- Seleção de serviço ou início de agendamento pela cliente; a lista pública é somente informativa.
- Edição de telefone, endereço ou situação da empresa.
- Categorias, fotos, descrições ou ordenação manual dos serviços.
- Reorganização ampla do frontend, criação de módulos de teste ou inclusão de dependências de teste.
- Limpeza dos endpoints e tabelas de aula e teste presentes no workspace Xano.

## Capabilities

### New Capabilities

- `service-catalog`: gestão administrativa de serviços por empresa e consulta pública dos serviços ativos.

### Modified Capabilities

- `identity`: após login ou cadastro, a administradora é encaminhada à área de serviços; a cliente continua na página de boas-vindas.

## Impact

- **Backend Xano:** tabela de serviços vinculada à empresa; validação e autorização administrativa; endpoints autenticados para listar, criar, editar e alterar situação; endpoint público para serviços ativos. Toda autorização e filtragem empresarial ocorre no backend.
- **Frontend Reflex:** área protegida de serviços, formulário de cadastro/edição, controles de ativação e exibição dos serviços na página pública. Reutilizar `frontend/frontend/frontend.py` e os helpers existentes, limitando qualquer extração de código ao mínimo necessário. A URL do novo grupo de API será configurada em `frontend/frontend/api_config.py`.
- **Verificação:** validar XanoScript pelo Xano Developer MCP, executar `xano workspace push --dry-run` e aguardar confirmação explícita antes de qualquer publicação real; usar chamadas HTTP reais e verificações manuais descritas nas tarefas.
- **Dependências:** nenhuma dependência nova. `requirements.txt` na raiz do repositório permanece a fonte oficial de dependências.
- **Documentação:** atualizar `docs/domain-model.md` com o comportamento de serviço acordado.
