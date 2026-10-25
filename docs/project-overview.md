# Project Overview — BeautyTime

## 1. Visão geral

O BeautyTime é um serviço web de agendamento online para salões de beleza, barbearias e estabelecimentos semelhantes. Cada estabelecimento cadastra sua empresa, seus profissionais e seus serviços, e divulga um link próprio para as clientes. Pelo link, que abre no navegador do celular, a cliente faz login e agenda um horário escolhendo o serviço, o profissional e o horário disponível.

O sistema é multiempresa: uma única instalação atende vários estabelecimentos, e cada um enxerga e gerencia apenas os próprios dados. Clientes também podem encontrar salões parceiros em uma lista pública de empresas ativas.

## 2. Problema

Muitos salões e barbearias ainda organizam a agenda por telefone, WhatsApp ou caderno. Isso gera:

- tempo gasto respondendo mensagens só para marcar horário;
- conflitos de horário e agendamentos duplicados para o mesmo profissional;
- dificuldade da cliente em saber quais horários estão livres;
- falta de uma visão organizada da agenda de cada profissional.

## 3. Objetivos

- Permitir que a cliente agende sozinha, a qualquer hora, sem precisar falar com o estabelecimento.
- Evitar conflitos de horário na agenda dos profissionais.
- Dar ao estabelecimento uma forma simples de cadastrar profissionais e serviços e acompanhar os agendamentos.
- Atender vários estabelecimentos na mesma plataforma, com os dados de cada um isolados.

## 4. Público-alvo / usuários

**Cliente** — pessoa que quer agendar um serviço. Acessa pelo link do estabelecimento, normalmente pelo celular. Faz login, agenda, consulta e cancela os próprios agendamentos.

**Administrador do estabelecimento** — dono ou responsável pelo salão/barbearia. Cadastra a empresa, os profissionais, os serviços e os horários de atendimento, e acompanha os agendamentos da empresa.

**Profissional** — pessoa que realiza os serviços (cabeleireira, barbeiro, manicure etc.). No escopo inicial, o profissional é um registro cadastrado pelo administrador e não precisa ter login próprio.

## 5. Escopo

- Cadastro e login de clientes.
- Cadastro e login de administradores de estabelecimento.
- Cadastro de empresa, com um link público de agendamento.
- Cadastro de profissionais, serviços e horários de atendimento.
- Indicação de quais serviços cada profissional realiza.
- Consulta de horários disponíveis e criação de agendamentos pela cliente.
- Consulta e cancelamento dos próprios agendamentos pela cliente.
- Visualização dos agendamentos da empresa pelo administrador.

## 6. Principais funcionalidades

**Para a cliente**
- Acessar o estabelecimento pelo link.
- Criar conta e fazer login.
- Escolher serviço, um profissional ou a opção “sem preferência”, e um horário disponível.
- Ver seus agendamentos futuros e passados.
- Cancelar um agendamento; até 8 horas antes do horário não há custo. Depois desse prazo, é exibido um aviso de taxa informativa de R$ 5,00 e o cancelamento fica registrado como tardio.
- Encontrar salões parceiros por uma lista pública de empresas ativas.
- Consultar a política de cancelamento também após a confirmação do agendamento.

**Para o administrador**
- Cadastrar a empresa e obter o link de agendamento.
- Acessar um painel inicial com os menus Serviços, Profissionais, Horários e Agenda, além do link público do salão e da opção de copiá-lo.
- Cadastrar, editar e desativar profissionais.
- Cadastrar, editar e desativar serviços, com duração e preço.
- Definir livremente um ou mais períodos de atendimento por dia para cada profissional, sem limite de horas diárias.
- Ver a agenda da empresa por dia e por profissional.
- Ver os cancelamentos tardios.

## 7. Requisitos e restrições importantes

- A interface deve funcionar bem no navegador do celular, pois a maioria das clientes acessará pelo link no smartphone.
- Um profissional não pode ter dois agendamentos sobrepostos.
- Só podem ser oferecidos horários dentro do horário de atendimento do profissional.
- Quando a cliente escolhe “sem preferência”, o sistema atribui qualquer profissional livre que realize o serviço.
- A disponibilidade considera os períodos de atendimento e exclui profissionais ocupados. Um dia sem horário livre para nenhum profissional fica indisponível no calendário.
- Os horários de início são oferecidos em intervalos de 15 minutos. O agendamento deve ocorrer com no mínimo 1 hora e no máximo 30 dias de antecedência.
- A duração do serviço escolhido define quanto tempo o agendamento ocupa na agenda.
- O cancelamento é gratuito até 8 horas antes do início. Após esse limite, o aviso informa a taxa de R$ 5,00 e o cancelamento é registrado como tardio para consulta da administradora. A taxa é apenas informativa; o aplicativo não processa pagamentos.
- Os dados de uma empresa nunca podem ser vistos ou alterados por outra empresa.

## 8. Arquitetura tecnológica

- **Backend:** Xano, desenvolvido em XanoScript. Responsável pelo banco de dados, pela autenticação, pelas regras de negócio e pela API.
- **Frontend:** Reflex. Responsável pelas telas, consumindo a API do Xano.
- **Versionamento:** Git e GitHub.
- **Sincronização com o Xano:** Xano CLI.
- **Desenvolvimento assistido por IA:** GitHub Copilot (modo Agent), com o Xano Developer MCP para documentação e validação de XanoScript.

## 9. Princípios de desenvolvimento

- Desenvolvimento incremental, uma mudança delimitada por vez.
- Especificar antes de implementar.
- Manter as regras de negócio no backend.
- Preferir soluções simples, adequadas ao escopo de um projeto acadêmico.

## 10. Segurança e integridade

- Toda regra de autorização é aplicada no backend (Xano). O frontend não é mecanismo de segurança.
- A cliente só pode ver e cancelar os próprios agendamentos.
- O administrador só pode ver e alterar os dados da própria empresa.
- A verificação de conflito de horário é feita no backend no momento de criar o agendamento, mesmo que a tela já mostre apenas horários livres.
- Senhas e tokens nunca são guardados em arquivos versionados.

## 11. Estratégia de desenvolvimento

O projeto será desenvolvido com OpenSpec, seguindo o ciclo Explore → Propose → Review → Apply → Archive. A implementação começa por uma primeira fatia funcional pequena e avança mudança por mudança, sem criar todo o banco ou todas as telas de uma vez.

## 12. Fonte de verdade e documentação

- `docs/project-overview.md` — visão geral do projeto (este documento).
- `docs/domain-model.md` — conceitos do domínio e seus relacionamentos.
- `AGENTS.md` — regras de trabalho para agentes de IA.
- `openspec/config.yaml` — contexto e regras dos workflows do OpenSpec.
- `openspec/specs/` — comportamento consolidado do sistema.
- `openspec/changes/` — mudanças em planejamento ou implementação.
