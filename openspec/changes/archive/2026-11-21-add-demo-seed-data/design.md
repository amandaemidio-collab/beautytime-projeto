# Design

## Context

Consulte `proposal.md` e `specs/demo-seed-data/spec.md` para motivação e contrato. A função usa as tabelas já existentes `account`, `user`, `service`, `professional`, `professional_service`, `professional_hours` e `appointment`; não há endpoint novo nem alteração de schema.

## Goals / Non-Goals

**Goals:**
- Construir a árvore de cada salão ausente com identificadores estáveis.
- Validar colisões e planejar todo o calendário antes de gravar.
- Permitir repetição segura sem alterar contas, clientes ou outros dados existentes.

**Non-Goals:**
- Atualizar, corrigir ou apagar registros preexistentes.
- Forçar a troca de senha de clientes demo que já existam.
- Fazer a seed por endpoint HTTP ou adicionar interface Reflex.

## Decisions

### Criar cada salão como uma unidade indivisível

Consultar `account.public_identifier` antes de qualquer inserção da árvore. Se existir, ignorar essa conta e seus dados relacionados sem inspecionar nem completar seus registros. Para uma conta ausente, tratar colisão de e-mail do dono ou de identificadores únicos como erro; nunca reaproveitar um usuário dono com associação de conta diferente. Usuários demo de cliente só são reutilizados se forem globais e tiverem role `client`; os demais e-mails reservados em conflito fazem a execução falhar.

Alternativa considerada: reparar árvores incompletas ou reaproveitar usuários existentes por e-mail. Foi rejeitada por exigir atualizações ou poder associar uma pessoa a uma conta não pretendida.

### Pré-validar dados e agenda antes de gravar

Usar a data local de `America/Sao_Paulo` para obter a semana de segunda a sábado. Preparar sete intervalos passados e três intervalos hoje, às 17:00, 17:00 e 18:00; os dois horários das 17:00 pertencem a profissionais diferentes. Os três usam um serviço de até 60 minutos, permanecem dentro do expediente até 19:00 e têm ao menos uma hora de antecedência no momento da execução. Nenhum horário se sobrepõe para o mesmo profissional. Marcar dois dos sete registros passados como cancelados. Se não houver combinação possível na semana em curso ou a janela de uma hora não for atendida, falhar antes da primeira gravação.

Alternativa considerada: datas e horas fixas. Foi rejeitada porque deixaria de atender “semana atual”, “hoje” e às regras de disponibilidade conforme a data e o horário da execução.

### Usar senha de entrada, sem segredo no repositório

Exigir a senha de demonstração como entrada da invocação e repassá-la ao campo `password` do Xano no mesmo padrão do cadastro existente. A função não deve registrá-la, devolvê-la em resultado ou defini-la como constante. Usuários que já existem não terão senha substituída. A documentação Xano será consultada antes de escolher o tipo exato do parâmetro e a forma de fornecer a entrada em execução.

Alternativa considerada: constante dentro da função. Foi rejeitada para não versionar credenciais e para respeitar a regra de segurança do projeto.

### Inserir somente após todas as verificações

Primeiro validar senha, colisões, registros que serão necessários e todas as agendas. Depois inserir somente dados novos, sem `update` ou `delete`. Usar transação documentada pelo Xano para impedir gravação parcial em falha; confirmar a sintaxe e o suporte na documentação do Xano antes da implementação. Se a operação transacional não puder ser usada com segurança, interromper a implementação para rever o desenho, em vez de aceitar estado parcial.

Alternativa considerada: inserir cada registro assim que for calculado. Foi rejeitada porque um conflito encontrado mais tarde deixaria uma seed incompleta.

### Catálogo e contas estáveis

Cada salão terá cinco serviços ativos:

| Salão | Serviço | Duração | Preço |
|---|---|---:|---:|
| Salão Aurora - Pinheiros | Corte feminino | 60 min | R$ 120,00 |
| Salão Aurora - Pinheiros | Escova | 45 min | R$ 80,00 |
| Salão Aurora - Pinheiros | Coloração de raiz | 120 min | R$ 220,00 |
| Salão Aurora - Pinheiros | Hidratação capilar | 60 min | R$ 140,00 |
| Salão Aurora - Pinheiros | Manicure clássica | 60 min | R$ 65,00 |
| Barbearia Paulista | Corte clássico | 45 min | R$ 60,00 |
| Barbearia Paulista | Corte degradê | 60 min | R$ 75,00 |
| Barbearia Paulista | Barba completa | 45 min | R$ 55,00 |
| Barbearia Paulista | Corte e barba | 90 min | R$ 105,00 |
| Barbearia Paulista | Pigmentação de barba | 30 min | R$ 40,00 |
| Estúdio Unhas Bela | Manicure clássica | 60 min | R$ 60,00 |
| Estúdio Unhas Bela | Pedicure | 60 min | R$ 70,00 |
| Estúdio Unhas Bela | Esmaltação em gel | 75 min | R$ 110,00 |
| Estúdio Unhas Bela | Alongamento em gel | 120 min | R$ 180,00 |
| Estúdio Unhas Bela | Manutenção de alongamento | 90 min | R$ 140,00 |

Os profissionais são Ana Lima e Bruna Costa (Salão Aurora), Lucas Martins e Pedro Souza (Barbearia Paulista), Camila Rocha e Júlia Santos (Estúdio Unhas Bela). Os dois profissionais de cada salão serão associados a todos os serviços. Cada um terá disponibilidade de segunda a sábado, 09:00–19:00, no fuso local do salão. Os dez agendamentos usam os quatro clientes em rotação e gravam os três campos snapshot do serviço. As métricas devolvidas para a execução serão consultadas diretamente da tabela `appointment`.

### Publicação e execução controladas

O arquivo Xano incluído na change será somente `xano/function/seed_demo_data.xs`. Validar a função pelo Xano Developer MCP e executar o dry-run do workspace `149160` com `--include` limitado a esse arquivo. Se a prévia contiver qualquer operação diferente de `CREATE`, não publicar e pedir orientação. Somente se todas as operações forem `CREATE`, publicar e invocar a função uma única vez com a senha fornecida na execução; não repetir a invocação automaticamente em caso de resultado ambíguo.

## Risks / Trade-offs

- [Data e hora podem tornar impossível cumprir todos os cenários na semana atual] → Validar o calendário completo com o fuso de São Paulo e falhar antes de gravar se não houver solução válida.
- [Um e-mail ou identificador pode já estar em uso por dado incompatível] → Fazer pré-checagem de unicidade e interromper sem tentar corrigir ou reaproveitar a entidade.
- [Uma falha de execução pode deixar dados incompletos] → Usar transação suportada/documentada pelo Xano e validar a operação antes da implementação.
- [Uma segunda chamada após timeout pode parecer segura mas esconder se a primeira foi concluída] → A função é idempotente por identificador público; ainda assim, consultar o estado antes de reexecutar manualmente.
- [Clientes demo já existentes podem ter outra senha] → Reutilizá-los sem alteração; a senha informada só se aplica às contas novas.

## Migration Plan

1. Validar o XanoScript e a compatibilidade das consultas, transação e entrada de senha com a documentação do Xano.
2. Executar dry-run com inclusão limitada ao arquivo novo e revisar que o resultado contém exclusivamente `CREATE`.
3. Só nessa condição, fazer o push e executar a função uma vez, fornecendo a senha sem gravá-la no repositório.
4. Verificar os três salões, usuários, serviços, vínculos, horários e agendamentos. Em falha ou prévia com `UPDATE`, não publicar nem tentar compensar com exclusões.

Não há migração de schema. Não há rollback automático: apagar os dados criados seria destrutivo e está fora do escopo; uma repetição segura pula salões já existentes.
