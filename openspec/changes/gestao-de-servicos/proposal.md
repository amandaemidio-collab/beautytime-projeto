# Proposal

## Why

Depois da fundação de identidade e empresa, a administradora entra no sistema mas não tem o que gerenciar, e a página pública `/agendar/{identificador}` mostra apenas o nome da empresa. Serviços são o primeiro elemento do catálogo e pré-requisito de profissionais, horários e agendamentos; entregá-los agora também estabelece o padrão de autorização por empresa e a área administrativa que as próximas changes vão reutilizar.

## What Changes

- Criar o cadastro de serviços da empresa no Xano, com nome, duração e preço, isolado por empresa.
- Permitir que a administradora liste, cadastre, edite, desative, reative e exclua os serviços da própria empresa.
- Regras de serviço:
  - nome obrigatório, com 2 a 80 caracteres, único dentro da empresa sem diferenciar maiúsculas e minúsculas;
  - duração em minutos inteiros, múltipla de 5, entre 5 e 480;
  - preço obrigatório, armazenado em centavos inteiros, entre R$ 0,00 e R$ 99.999,99;
  - todo serviço novo nasce ativo.
- Introduzir no backend uma verificação reutilizável que obtém a empresa da administradora a partir da sessão autenticada; nenhum endpoint administrativo aceita o identificador da empresa vindo do cliente.
- Expor publicamente, por identificador da empresa, somente os serviços ativos com nome, duração e preço.
- Criar uma área administrativa mínima e protegida no Reflex, com a gestão de serviços, e levar a administradora a ela após login ou cadastro, no lugar da página de boas-vindas. A cliente continua indo para a página de boas-vindas.
- Exibir os serviços ativos na página pública da empresa, com estados de carregamento, lista vazia e erro.
- Criar um novo grupo de API no Xano para os endpoints do catálogo.
- Reorganizar o frontend Reflex em módulos (páginas, estados e componentes), sem alterar rotas nem comportamentos existentes.
- Introduzir testes automatizados (pytest) e um roteiro de verificação manual.
- Atualizar `docs/domain-model.md` com as regras de serviço definidas aqui.

### Fora do escopo

- Profissionais, vínculo profissional↔serviço, horários de atendimento, disponibilidade e agendamentos.
- Edição de telefone, endereço e situação (ativa/inativa) da empresa.
- Regras de exclusão de serviço com dependências (profissionais ou agendamentos vinculados); serão definidas quando esses vínculos existirem.
- Seleção de serviço pela cliente na página pública; nesta change a lista é apenas informativa.
- Categorias, fotos, descrições ou ordenação manual de serviços.
- Limpeza dos endpoints e tabelas de aula e teste presentes no workspace Xano.

## Capabilities

### New Capabilities

- `service-catalog`: cadastro e manutenção de serviços pela administradora, isolados por empresa, e consulta pública dos serviços ativos de uma empresa.

### Modified Capabilities

- `identity`: após login ou cadastro, a administradora é levada à área administrativa em vez da página de boas-vindas; a cliente mantém a página de boas-vindas.

## Impact

- **Backend Xano:** nova tabela de serviço vinculada a `account`; nova função reutilizável de autorização da administradora; novo grupo de API com endpoints administrativos autenticados e um endpoint público de serviços ativos. Os endpoints existentes de autenticação e `company/public` não mudam.
- **Frontend Reflex:** `frontend/frontend/frontend.py` dividido em módulos; novas rotas da área administrativa de serviços; página pública passa a listar serviços; redirecionamento da administradora após login ou cadastro; nova URL de grupo em `api_config.py`.
- **Dependências:** `pytest` acrescentado a `requirements.txt` para os testes automatizados (justificado no design). Nenhuma tecnologia de frontend ou serviço externo novo.
- **Documentação:** `docs/domain-model.md` (regras de serviço).
