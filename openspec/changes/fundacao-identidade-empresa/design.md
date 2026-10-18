# Design

## Context

O quick-start Xano já oferece autenticação nativa na tabela `user`, índice único de e-mail, emissão de token e endpoints de cadastro, login e identidade atual. `user` hoje usa `account_id` opcional e papéis `admin`/`member`; `account` contém nome, descrição e localização, sem identificador público. O cadastro cria inicialmente um `member` sem empresa, e há endpoints separados para criar conta, ingressar nela e alterar papéis.

O frontend Reflex ainda é um ponto de partida, sem os fluxos de identidade do produto. Os comportamentos esperados estão definidos em `specs/identity/spec.md` e `specs/public-company/spec.md`.

## Goals / Non-Goals

**Goals:**
- Preservar a autenticação e emissão de sessão nativas do Xano, mantendo uma única identidade por e-mail.
- Garantir no backend a exclusividade do tipo de conta, o vínculo de administradores e a unicidade do identificador público.
- Entregar os fluxos necessários em Xano e Reflex sem adicionar dependências tecnológicas, levando ambos os tipos de usuário a uma página simples de boas-vindas após login.

**Non-Goals:**
- Criar a administração de múltiplas empresas por uma conta, convites ou associação de usuários a empresas.
- Implementar painel administrativo, profissionais, serviços, horários, agendamentos, recuperação de senha ou verificação de e-mail nesta mudança.

## Decisions

### Reaproveitar o mecanismo de autenticação e adaptar o modelo atual

Manter a tabela autenticável `user`, o login por e-mail/senha e a emissão de token do Xano. Adaptar o campo de papel para os tipos `client` e `admin`; clientes nunca têm associação empresarial, enquanto cada administrador tem associação obrigatória e única a uma empresa. Tornar obrigatórios os dados essenciais de autenticação no cadastro. A unicidade global de e-mail existente permanece como regra para ambos os tipos.

Reutilizar `account` como registro da empresa, preservando o vínculo `user.account_id`, e adicionar o identificador público com unicidade no banco. Isso aproveita os vínculos e dados de organização existentes sem criar um sistema paralelo de contas. A alternativa de criar tabelas e autenticação independentes duplicaria credenciais, tokens e lógica de sessão, aumentando o risco de uma mesma pessoa obter identidades incompatíveis.

### Criar dois fluxos explícitos de cadastro e autenticação por tipo

O cadastro de cliente cria somente uma conta `client`, sem empresa. O cadastro de administrador valida os dados da conta, da empresa e do identificador antes de criar a conta `admin` vinculada à empresa. A gravação deve ser tudo-ou-nada: usar o mecanismo transacional suportado pelo Xano ou uma compensação que remova os registros parciais se a criação falhar. O login valida que o tipo da conta corresponde ao fluxo utilizado; a identidade autenticada retorna o tipo e, para administradores, a empresa associada.

Não reutilizar sem adaptação o fluxo `account` que cria empresa após o cadastro, nem os endpoints genéricos de ingresso em conta e alteração de papel. Eles permitem um usuário sem tipo de domínio ou associação posterior, incompatíveis com os invariantes desta change. O suporte a múltiplos administradores da mesma empresa não será introduzido por um fluxo de adesão nesta etapa.

### Validar e proteger o identificador público

Tratar o identificador escolhido como slug literal: aceitar somente letras minúsculas ASCII, números e hífen, com comprimento entre 3 e 40 caracteres, sem hífen no início ou no fim e sem hífens consecutivos. Não normalizar caixa. Validar o formato na API e impor unicidade no banco para resolver também cadastros concorrentes; uma verificação prévia isolada não é suficiente. Não gerar substitutos automaticamente: se houver colisão, informar o conflito para que a pessoa escolha outro identificador.

Criar uma consulta sem autenticação por slug que selecione apenas os campos públicos definidos pela API. Não serializar diretamente registros completos de `account` ou `user`; isso evita expor identificadores internos, informações de autenticação ou dados de administradores.

### Manter o frontend como consumidor da API

Implementar em Reflex fluxos separados para cadastro/login de cliente e cadastro/login de administrador com dados da empresa. Após qualquer login bem-sucedido, navegar para uma página simples de boas-vindas sem funcionalidades de agendamento nem painel administrativo. A página pública de empresa usa a rota `/agendar/{identificador}` e consulta a API usando o slug. Validação de formulário melhora a experiência, mas todas as regras e autorizações permanecem no Xano.

## Risks / Trade-offs

- [Descartar dados de teste causa perda dos registros atuais no workspace] → O grupo confirmou que o workspace contém apenas dados de teste e que usuários e contas podem ser descartados; não desenvolver migração de dados legados.
- [Dois cadastros simultâneos podem escolher o mesmo identificador] → Usar índice único no banco e tratar a violação como erro de identificador indisponível.
- [Falha entre a criação da empresa e da conta pode deixar registros órfãos] → Validar antes de gravar e garantir operação transacional ou compensação, cobrindo a falha em teste.
- [Resposta pública ampla pode revelar dados internos da empresa] → Construir uma resposta allowlisted com campos públicos explícitos e testar sua forma.
- [Rotas genéricas do quick-start podem permitir associação ou troca de papel que contorne o cadastro] → Desabilitar ou restringir esses fluxos antes de expor os novos endpoints.
- [Um dry-run pode revelar operações destrutivas ou inesperadas no workspace] → Após cada `xano workspace push --dry-run`, apresentar integralmente o resultado relevante e aguardar confirmação explícita da pessoa usuária antes de executar o push real correspondente; sem confirmação, não executar o push.

## Migration Plan

1. Considerar descartáveis os usuários, contas e demais dados existentes no workspace Xano, pois são apenas dados de teste; não executar migração legada.
2. Aplicar as alterações de modelo e endpoints e executar `xano workspace push --dry-run`. Apresentar o resultado e aguardar confirmação explícita antes de cada push real; se a confirmação não for dada, interromper sem publicar.
3. Publicar os endpoints adaptados e a consulta pública, removendo ou bloqueando os fluxos genéricos incompatíveis.
4. Publicar os fluxos Reflex e verificar cadastro, login, navegação para boas-vindas, associação da empresa e consulta pública ponta a ponta.
5. Se a implantação falhar, reverter a versão dos endpoints e da interface; recriar dados de teste conforme necessário.

## Open Questions

Nenhuma. O formato do identificador, a rota pública, os vínculos de identidade, a experiência placeholder pós-login e o gate de confirmação do push foram definidos nesta change.
