# Proposal

## Why

O BeautyTime ainda não tem uma identidade de produto coerente para clientes e administradores: a autenticação Xano presente no repositório é o quick-start genérico de membros e contas, não os dois tipos de usuário definidos pelo domínio. Esta mudança estabelece cadastro e login com papéis mutuamente exclusivos e uma empresa acessível por identificador público, preparando a plataforma para agendamentos sem incluir o fluxo de agendar.

## What Changes

- Adaptar o cadastro, o login e a representação de usuário existentes no Xano para distinguir cliente de administrador, mantendo a identidade e o e-mail únicos na plataforma.
- Permitir que o cadastro de administrador crie e associe uma única empresa à conta.
- Permitir à administradora escolher um identificador público único para o link da empresa, aceitando apenas letras minúsculas, números e hífen, com 3 a 40 caracteres, sem hífen nas extremidades ou hífens consecutivos; permitir a consulta pública da empresa na rota `/agendar/{identificador}`.
- Manter cadastro e login de clientes independentes de qualquer empresa, para que a mesma conta possa ser usada na plataforma inteira.
- Após login bem-sucedido, levar clientes e administradores a uma página simples de boas-vindas (placeholder).
- Não incluir profissionais, serviços, horários, agendamentos nem painel administrativo; essas experiências ficam para changes futuras.

## Capabilities

### New Capabilities

- `identity`: cadastro e login de clientes e administradores, com papéis exclusivos e vínculo do administrador a uma única empresa.
- `public-company`: criação da empresa no cadastro de administrador, identificador público único e consulta pública dos dados básicos da empresa.

### Modified Capabilities

Nenhuma. Ainda não existem specs consolidados no projeto.

## Impact

- Backend Xano: adaptar a tabela `user` e os endpoints `auth/signup`, `auth/login` e `auth/me`; adaptar a tabela `account` e o fluxo atual de criação de conta para representar uma empresa criada com seu administrador; ajustar os fluxos genéricos de adesão e alteração de papel que conflitam com os papéis exclusivos e com a regra de uma empresa por administrador.
- Frontend Reflex: acrescentar telas e chamadas para cadastro/login de cliente, cadastro/login de administrador com dados da empresa, página placeholder de boas-vindas após login e apresentação pública da empresa por identificador.
- Recomendação de reaproveitamento: reaproveitar a autenticação nativa Xano e a base de `user`/`account`, adaptando seu modelo e seus endpoints, em vez de criar um mecanismo de autenticação paralelo. A tabela `user` já tem e-mail único global e login com token; a tabela `account` já contém dados básicos de uma organização. Porém, o quick-start atual permite `member` sem empresa, entrada em outra conta e cadastro da empresa em etapa separada. Esses comportamentos precisam ser substituídos ou restringidos para cumprir as decisões do domínio.
- Os dados atuais do workspace Xano são apenas de teste e podem ser descartados; não é necessária migração de usuários ou contas legadas.
