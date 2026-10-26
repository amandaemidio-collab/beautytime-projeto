# Backlog — versão 2

Melhorias identificadas durante as changes da primeira versão e deixadas para uma próxima versão. Cada item deve virar uma change própria no OpenSpec antes de ser implementado.

## Funcionalidades

1. **Desativar e reativar o salão pela administradora:** o salão desativado some da lista pública de salões e pode ser reativado com o mesmo login.
2. **Editar os dados do salão:** permitir que a administradora altere o nome, o endereço e as demais informações do salão.

## Interface

3. **Revisão de design e ajuste fino do visual:** revisar o visual das telas e fazer os ajustes finos de aparência e consistência.
4. **Corrigir os estilos responsivos restantes que o Reflex ignora:** trocar por `rx.breakpoints` as larguras de botões e os espaçamentos que ainda usam dicionários em propriedades CSS.

## Backend

5. **Centralizar a regra de horários livres:** reunir num único lugar a regra hoje repetida em três pontos do backend (`availability`, `available_days` e `find_available_professional`).
6. **Padronizar o filtro `trim` no identificador da rota de disponibilidade:** aplicar ao identificador da rota `availability` o mesmo `filters=trim` já usado em `available_days`.
7. **Ordenar no backend os dias do cadastro de horários em vários dias:** ordenar os dias recebidos antes da checagem, para que o dia de conflito informado seja sempre o primeiro da semana.
