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
- identificador público usado no link de agendamento;
- telefone e endereço;
- situação (ativa ou inativa).

### Relacionamentos
- Possui um ou mais administradores.
- Possui vários profissionais, serviços e agendamentos.

### Regras estruturais
- O identificador do link é único entre todas as empresas.
- Todos os profissionais, serviços e agendamentos pertencem a exatamente uma empresa.

---

## Administrador

Usuário responsável por gerenciar uma empresa.

### Principais informações
- nome;
- e-mail (usado no login);
- senha.

### Relacionamentos
- Pertence a uma empresa.

### Regras estruturais
- Só gerencia dados da própria empresa.

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
- Só vê e cancela os próprios agendamentos.

---

## Profissional

Pessoa que realiza os serviços em uma empresa.

### Principais informações
- nome;
- situação (ativo ou inativo).

### Relacionamentos
- Pertence a uma empresa.
- Realiza um ou mais serviços da mesma empresa.
- Possui horários de atendimento.
- Possui vários agendamentos.

### Regras estruturais
- Um profissional inativo não aparece para novos agendamentos.
- No escopo inicial, não possui login.

---

## Serviço

Algo que a empresa oferece, como corte, escova, barba ou manicure.

### Principais informações
- nome;
- duração;
- preço;
- situação (ativo ou inativo).

### Relacionamentos
- Pertence a uma empresa.
- Pode ser realizado por um ou mais profissionais.

### Regras estruturais
- A duração define quanto tempo o agendamento ocupa na agenda do profissional.
- Um serviço inativo não aparece para novos agendamentos.

---

## Horário de atendimento

Período em que um profissional atende, por dia da semana. Exemplo: terça-feira, das 9h às 18h.

### Principais informações
- dia da semana;
- hora de início;
- hora de término.

### Relacionamentos
- Pertence a um profissional.

### Regras estruturais
- Só é possível agendar dentro desses períodos.

---

## Agendamento

Reserva de um horário de um profissional para realizar um serviço para uma cliente.

### Principais informações
- data e hora de início;
- data e hora de término (calculada pela duração do serviço);
- situação: agendado, cancelado ou concluído.

### Relacionamentos
- Pertence a uma empresa.
- Está associado a uma cliente, um profissional e um serviço.

### Regras estruturais
- O profissional deve realizar o serviço escolhido e pertencer à mesma empresa.
- O horário deve estar dentro do horário de atendimento do profissional.
- Um profissional não pode ter dois agendamentos ativos com horários sobrepostos.
- Agendamentos cancelados liberam o horário.
- Não é possível agendar no passado.
