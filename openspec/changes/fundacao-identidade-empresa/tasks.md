# Tasks

## 1. Modelo Xano sem migração legada

- [x] 1.1 Preparar o modelo Xano sem migração de usuários ou contas legadas, pois os dados atuais são apenas de teste e podem ser descartados; verificar que o novo modelo funciona sem depender desses registros.
- [x] 1.2 Adaptar `user` e `account` para cliente/administrador e empresa, incluindo campos obrigatórios, vínculo permitido por tipo e unicidade do identificador público; validar os arquivos XanoScript pelo Xano Developer MCP e executar `xano workspace push --dry-run`, apresentar o resultado e aguardar confirmação explícita antes de qualquer push real.
- [x] 1.3 Atualizar `docs/domain-model.md` com os invariantes finais de identidade, associação e identificador público; verificar que o documento corresponde ao modelo aplicado e aos requisitos das duas specs.

## 2. APIs de identidade e empresa no Xano

- [x] 2.1 Implementar cadastro e login de cliente e administrador com validação de tipo, e-mail único e sessão nativa Xano; verificar sucesso, e-mail duplicado, senha incorreta, tentativa de login pelo fluxo do outro tipo e rejeição de vínculo de cliente a empresa.
- [x] 2.2 Implementar cadastro transacional de administrador e empresa, com slug de 3 a 40 caracteres contendo apenas letras minúsculas ASCII, números ou hífen, sem hífen nas extremidades ou hífens consecutivos, e tratamento de colisão concorrente; verificar limites de 3/40, rejeição de 2/41 caracteres, caixa alta, hífens nas extremidades e hífens consecutivos, além da ausência de órfãos em caso de falha.
- [x] 2.3 Adaptar a resposta de identidade autenticada e bloquear os fluxos genéricos incompatíveis de adesão a conta e alteração de papel; verificar que o tipo e vínculo da conta não podem ser alterados por esses endpoints.
- [x] 2.4 Implementar consulta pública por slug com resposta limitada a campos públicos; verificar empresa existente, identificador inexistente e ausência de campos de autenticação ou dados privados.

## 3. Fluxos de interface em Reflex

- [ ] 3.1 Implementar cadastro e login de cliente integrados às APIs e tratamento dos erros de autenticação/cadastro; verificar os fluxos em execução, a ausência de dados sensíveis na sessão e a navegação para a página simples de boas-vindas após login.
- [ ] 3.2 Implementar cadastro de administrador com dados da empresa e login correspondente, apresentando erros de e-mail ou slug indisponível; verificar a criação da empresa, o tratamento de falha sem sucesso parcial na interface e a navegação para a página simples de boas-vindas após login.
- [ ] 3.3 Implementar a página pública da empresa usando o slug e a consulta sem autenticação; verificar apresentação dos dados públicos e estado de empresa não encontrada.

## 4. Verificação integrada

- [ ] 4.1 Percorrer os fluxos ponta a ponta de cliente, administrador e consulta pública, incluindo e-mail duplicado, papéis incompatíveis, tentativa de vincular cliente a empresa, slug duplicado, comprimentos fora de 3–40, caracteres não permitidos, hífen inicial/final ou consecutivo e empresa inexistente; verificar a página pela rota `/agendar/{identificador}`, todos os cenários das specs e que nenhum endpoint genérico permite contornar as regras.
