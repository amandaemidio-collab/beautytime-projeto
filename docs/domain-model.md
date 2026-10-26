# Domain Model — BeautyTime

Este documento descreve os conceitos do domínio e seus relacionamentos. Ele não define tabelas, tipos de coluna ou endpoints; esses detalhes são decididos nas mudanças do OpenSpec.

## Visão geral dos relacionamentos

```text
Empresa
├── Administrador (1 ou mais)
├── Profissional (vários)
│   ├── Horário de atendimento (vários)
│   └── realiza → Serviço (vários)
├── Serviço (vários)
└── Agendamento (vários)
        ├── Cliente
        ├── Profissional
        └── Serviço
```

---

## Empresa

Representa um estabelecimento que usa o BeautyTime: salão de beleza, barbearia, esmalteria etc.

### Principais informações
- nome;
- identificador público usado na rota `/agendar/{identificador}`; contém 3 a 40 caracteres, somente letras minúsculas, números e hífen, sem hífens nas extremidades ou consecutivos;
- telefone e endereço.

### Relacionamentos
- Possui um ou mais administradores.
- Possui vários profissionais, serviços e agendamentos.
- Pode ser encontrada por clientes na lista pública de salões, quando aceita reservas.

### Regras estruturais
- O identificador do link é único entre todas as empresas e respeita o formato especificado acima.
- Todos os profissionais, serviços e agendamentos pertencem a exatamente uma empresa.
- Uma empresa aceita reservas quando possui ao menos um serviço ativo vinculado a ao menos um profissional ativo da própria empresa. Somente essas empresas aparecem na lista pública de salões, que expõe apenas nome e identificador público.

---

## Administrador

Usuário responsável por gerenciar uma empresa.

### Principais informações
- nome;
- e-mail (usado no login);
- senha.

### Relacionamentos
- Pertence obrigatoriamente a exatamente uma empresa.

### Regras estruturais
- Só gerencia dados da própria empresa.
- Administradores são as únicas contas associadas a uma empresa; uma conta de administrador gerencia uma única empresa.

---

## Cliente

Pessoa que agenda serviços.

### Principais informações
- nome;
- e-mail (usado no login);
- telefone;
- senha.

### Relacionamentos
- Possui vários agendamentos.

### Regras estruturais
- A conta da cliente é da plataforma, não de uma empresa: a mesma cliente pode agendar em empresas diferentes com a mesma conta.
- Nunca possui associação com uma empresa.
- Só vê e cancela os próprios agendamentos.
- Sua área permite consultar agendamentos próximos e passados, cancelá-los e encontrar, na lista pública de salões, as empresas que aceitam reservas.

---

## Profissional

Pessoa que realiza os serviços em uma empresa.

### Principais informações
- nome;
- situação (ativo ou inativo);
- data de criação.

### Relacionamentos
- Pertence a uma empresa.
- Realiza um ou mais serviços da mesma empresa.
- Possui horários de atendimento.
- Possui vários agendamentos.

### Regras estruturais
- Um profissional inativo não aparece para novos agendamentos.
- Cada profissional pertence a exatamente uma empresa; a empresa é determinada pela sessão da administradora ao cadastrar ou editar.
- O profissional realiza um ou mais serviços da mesma empresa. O vínculo entre profissional e serviço é persistido separadamente e não pode se repetir para o mesmo par.
- Só serviços ativos da empresa podem ser escolhidos em cadastro ou em uma nova seleção na edição. Se a edição não enviar uma nova seleção, os vínculos existentes são preservados.
- Se um serviço vinculado for desativado, o vínculo é preservado, mas não é válido para novos agendamentos enquanto o serviço estiver inativo. Ao reativar o serviço, o vínculo volta a ser válido.
- No escopo inicial, não possui login.

---

## Serviço

Algo que a empresa oferece, como corte, escova, barba ou manicure.

### Principais informações
- nome;
- duração em minutos inteiros;
- preço em centavos inteiros;
- situação (ativo ou inativo).

### Relacionamentos
- Pertence a uma empresa.
- Pode ser realizado por um ou mais profissionais.

### Regras estruturais
- O nome, após remover espaços das extremidades, contém de 2 a 80 caracteres e é único por empresa sem diferenciar maiúsculas e minúsculas; a unicidade também inclui serviços inativos.
- A duração é um número inteiro de 15 a 480 minutos, sempre múltiplo de 15.
- O preço é um número inteiro de 0 a 9.999.999 centavos.
- A duração define quanto tempo o agendamento ocupa na agenda do profissional.
- Um serviço inativo não aparece para novos agendamentos.
- A desativação preserva o registro e seus dados; serviços não são excluídos fisicamente.
- A desativação não remove associações com profissionais; essas associações voltam a ser válidas quando o serviço é reativado.

---

## Horário de atendimento

Período em que um profissional atende, por dia da semana. Exemplo: terça-feira, das 9h às 18h.

### Principais informações
- dia da semana;
- hora de início;
- hora de término.

Um profissional pode ter vários períodos no mesmo dia, por exemplo, das 9h às 12h e das 14h às 18h.
Os períodos se repetem semanalmente e representam horários locais no fuso `America/Sao_Paulo`.

### Relacionamentos
- Pertence a um profissional.

### Regras estruturais
- A empresa define livremente os períodos de atendimento; não há limite de horas diárias.
- Os períodos de um mesmo profissional no mesmo dia não podem se sobrepor. Períodos que apenas se encostam, como das 9h às 12h e das 12h às 18h, são permitidos.
- Um mesmo período (mesmo início e término) pode ser cadastrado em vários dias da semana de uma vez; a operação é tudo ou nada.
- Só é possível agendar dentro de um desses períodos.

---

## Agendamento

Reserva de um horário de um profissional para realizar um serviço para uma cliente.

### Principais informações
- data e hora de início;
- data e hora de término (calculada pela duração do serviço);
- situação: `agendado` ou `cancelado`;
- cópia do nome, da duração e do preço do serviço no momento da reserva;
- indicação de cancelamento tardio.

### Relacionamentos
- Pertence a uma empresa.
- Está associado a uma cliente, um profissional e um serviço.

### Regras estruturais
- O profissional deve realizar o serviço escolhido e pertencer à mesma empresa.
- A cliente pode escolher um profissional ou “sem preferência”. Nesse segundo caso, o sistema seleciona qualquer profissional livre da empresa que realize o serviço; o agendamento fica associado ao profissional selecionado.
- O horário deve estar dentro de um dos períodos de atendimento do profissional.
- Um profissional não pode ter dois agendamentos ativos com horários sobrepostos.
- Agendamentos cancelados liberam o horário.
- A disponibilidade exclui os profissionais ocupados. Se nenhum profissional tiver horário livre em um dia, esse dia fica indisponível no calendário.
- Os horários de início são oferecidos em intervalos de 15 minutos do relógio local (`:00`, `:15`, `:30`, `:45`) no fuso `America/Sao_Paulo`.
- A cliente só pode agendar com no mínimo 1 hora e no máximo 30 dias de antecedência.
- O nome, a duração e o preço do serviço são copiados para o agendamento e permanecem inalterados se o cadastro do serviço mudar depois.
- Agendamentos têm somente as situações `agendado` e `cancelado`. Um agendamento cancelado libera o horário.
- A cliente pode cancelar sem custo quando faltam 8 horas ou mais para o início. Com menos de 8 horas, o cancelamento é tardio e fica visível para a administradora.
- Antes de confirmar um cancelamento tardio, a interface informa a taxa de R$ 5,00 e solicita confirmação. A taxa é apenas informativa: o aplicativo não processa pagamentos nem cobra o valor. A política também é exibida após a confirmação do agendamento.
- Agendamentos passados não podem ser cancelados pela cliente.
