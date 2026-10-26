# Proposal

## Why

Hoje a administradora cadastra os horários de um profissional um dia de cada vez: para um expediente igual de segunda a sábado, precisa repetir o mesmo formulário seis vezes, e cada repetição é uma chamada ao Xano, o que aproxima a tela do limite de requisições. Além disso, o backend aceita períodos sobrepostos no mesmo dia, o que permite configurações confusas, como 09:00–18:00 e 10:00–12:00 na mesma terça-feira.

## What Changes

- No formulário de novo período da tela Horários, a escolha de um único dia passa a ser a marcação de um ou mais dias (segunda a domingo), com o atalho "Todos os dias" que marca os sete.
- Nova rota administrativa que cria, numa única chamada, um período igual (mesmo início e término) para cada dia informado. A operação é tudo ou nada: se algum dia não puder receber o período, nenhum período é criado e a resposta indica qual dia falhou.
- A rota nova aplica, para cada dia, as mesmas validações do cadastro individual: administradora autenticada, empresa derivada da sessão, profissional ativo da própria empresa, dia válido e início anterior ao término.
- Nova regra para todos os cadastros de horário: um período não pode se sobrepor a outro período do mesmo profissional no mesmo dia. Períodos que apenas se encostam (um termina às 12:00 e outro começa às 12:00) continuam permitidos. A regra vale para o cadastro individual existente, para o cadastro em vários dias e para a edição, e a mensagem indica o dia em conflito.
- Dias com horários diferentes continuam sendo cadastrados em cadastros separados, um para cada grupo de dias.
- A edição e a remoção continuam sendo feitas por período individual; o formulário de edição mantém a escolha de um único dia.
- Atualizar `docs/domain-model.md` com a regra de não sobreposição de períodos.

### Fora do escopo

- Editar ou remover vários períodos de uma vez.
- Copiar os horários de um profissional para outro.
- Ajustar períodos sobrepostos que já existam no banco: eles continuam válidos; apenas uma edição deles passa a ser recusada se mantiver a sobreposição.
- Mudanças nas regras de disponibilidade, reserva ou cancelamento.
- Infraestrutura de testes automatizados.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `professional-hours`: cadastro de um período em vários dias numa única operação tudo ou nada, e proibição de períodos sobrepostos do mesmo profissional no mesmo dia (cadastro individual, em vários dias e edição).

## Impact

- **Backend (Xano):** nova rota `POST` no grupo `Agenda` para criação em vários dias; checagem de sobreposição adicionada às rotas existentes de criação (`hours_POST.xs`) e edição (`hour_id_PATCH.xs`) de período. Sem tabelas ou campos novos. Requer dry-run e confirmação antes do push.
- **Frontend (Reflex):** formulário da tela `/admin/horarios` em `frontend/frontend/frontend.py` (marcação de dias no cadastro, escolha de um dia mantida na edição) e tratamento das mensagens de erro por dia.
- **Documentação:** `docs/domain-model.md` (regra de não sobreposição de períodos).
- **Dados existentes:** períodos já sobrepostos não são alterados; a disponibilidade continua tratando esses casos como hoje.
