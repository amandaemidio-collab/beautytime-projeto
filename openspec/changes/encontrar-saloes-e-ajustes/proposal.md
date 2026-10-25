# Proposal

## Why

Hoje a cliente só chega a um salão pelo link divulgado pela empresa: na área `/meus-agendamentos` não há caminho para fazer um novo agendamento nem para repetir uma reserva anterior, e a lista pública de salões parceiros prevista em `docs/project-overview.md` ainda não existe. Além disso, a página pública `/agendar/{identificador}` apresenta problemas visuais no celular (conteúdo encostado na borda esquerda e cartão cortado) e a responsável pelo projeto relatou um texto de "em breve" que não corresponde ao fluxo de agendamento já disponível.

## What Changes

- Nova consulta pública, sem autenticação, que lista os salões que aceitam reservas, retornando somente nome e identificador público de cada empresa, em ordem alfabética.
- Nova tela pública "Encontrar salões" que apresenta essa lista, com um botão por salão que leva a `/agendar/{identificador}`, e estados de carregamento, vazio e erro.
- Na área `/meus-agendamentos`, um botão "Novo agendamento" que leva à tela "Encontrar salões".
- Em cada agendamento listado em `/meus-agendamentos` (próximos e passados, inclusive cancelados), um botão "Agendar de novo" que leva a `/agendar/{identificador}` do salão daquele agendamento.
- Ajuste de layout da página pública `/agendar/{identificador}` para usar as mesmas margens laterais das outras telas, sem conteúdo encostado na borda nem cartão cortado, em celular e desktop.
- Garantir que a página pública apresente um texto introdutório adequado ao fluxo de agendamento, sem mensagem de "em breve". Observação: o texto de "em breve" já tinha sido removido no commit `221b0dc`; o texto que estava no lugar ("Agende seu horário em poucos toques.") foi trocado por um que convida a escolher serviço, profissional, dia e horário.
- Atualizar `docs/domain-model.md` para definir que "empresa ativa" na lista pública é a empresa que aceita reservas.

### Fora do escopo

- Campo de situação (ativa/inativa) na empresa e qualquer controle de ativação ou desativação pela administradora.
- Busca, filtros, paginação, localização, descrição ou outros dados da empresa na lista.
- Link para "Encontrar salões" na página inicial ou em outras telas além de `/meus-agendamentos`.
- Preenchimento automático de serviço ou profissional ao usar "Agendar de novo": o fluxo começa do primeiro passo.
- Mudanças nas regras de disponibilidade, reserva ou cancelamento.
- Correção dos usos de dicionário responsivo em propriedades CSS fora dos estilos compartilhados de página, cartão e painel e do cartão de serviço da página pública (por exemplo, larguras de botões).
- Infraestrutura de testes automatizados.

## Capabilities

### New Capabilities

- `salon-directory`: lista pública dos salões que aceitam reservas, com consulta no backend e tela "Encontrar salões" que leva ao link de agendamento de cada salão.

### Modified Capabilities

- `client-appointments`: atalhos "Novo agendamento" e "Agendar de novo" na área da cliente, e requisitos de layout e de texto da página pública de agendamento.

## Impact

- **Backend (Xano):** uma nova rota pública de leitura no grupo `Members & Accounts`, sem novas tabelas ou campos. Requer dry-run e confirmação antes do push.
- **Frontend (Reflex):** nova página pública em `frontend/frontend/frontend.py`, novos botões na área da cliente e ajuste de layout da página `/agendar/{identificador}`. Sem novas dependências. A causa das margens está nos estilos compartilhados de página, cartão e painel; a correção deles muda as margens e o espaçamento interno de todas as telas, inclusive as administrativas.
- **Documentação:** `docs/domain-model.md` e `docs/project-overview.md` (definição das empresas da lista pública como as que aceitam reservas).
- **Privacidade:** a lista expõe somente nome e identificador público, dados que já são públicos pelo link de cada salão.
