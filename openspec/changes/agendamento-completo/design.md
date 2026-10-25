# Design

## Contexto

Consulte [proposal.md](./proposal.md) para motivação e as specs delta em `specs/` para os contratos observáveis. O Xano já contém tabelas de empresa, usuário, serviço, profissional e associação profissional-serviço; o grupo `Catalogo` oferece rotas administrativas e um helper que deriva a empresa da sessão. O frontend Reflex concentra páginas, estado e chamadas à API em `frontend/frontend/frontend.py`, com URLs centralizadas em `frontend/frontend/api_config.py`.

O backend é a autoridade para disponibilidade, autorização e integridade da reserva. A interface atual apresenta serviços na rota pública e encaminha a cliente autenticada para `/boas-vindas`; o painel administrativo já tem os itens Horários e Agenda como áreas futuras. A sintaxe e as operações específicas do XanoScript deverão ser confirmadas na documentação Xano Developer antes de implementar.

## Objetivos / Não objetivos

**Objetivos:**

- Integrar horários semanais, disponibilidade, reserva, cancelamento e consulta de agenda sem criar outra pilha tecnológica.
- Reutilizar a identidade, os vínculos e as práticas existentes de isolamento por empresa.
- Manter os valores históricos do serviço no agendamento e tornar a revalidação de conflito uma regra do backend.
- Planejar verificações HTTP e manuais sem introduzir framework ou infraestrutura automatizada.

**Não objetivos:**

- Criar política de férias, feriados, exceções por data, pagamentos ou notificações.
- Permitir reagendamento, cancelamento pela administradora ou conclusão do atendimento.
- Refatorar o frontend para uma arquitetura modular como objetivo independente.

## Decisões

### Manter as regras e a persistência no backend Xano

Adicionar uma tabela de períodos semanais vinculada ao profissional e uma tabela de agendamentos vinculada à empresa, cliente, profissional e serviço. O período contém dia da semana e horários locais de início e término. O agendamento contém início e término como instantes, situação `agendado` ou `cancelado`, indicação de cancelamento tardio e cópias do nome, duração em minutos e preço em centavos do serviço.

As rotas administrativas derivam `account_id` da identidade autenticada usando o padrão de `Catalogo/authorize_admin`; nunca usam empresa enviada pelo frontend para autorizar. Rotas da cliente exigem papel `client` e usam o id autenticado para leitura e cancelamento. Rotas públicas localizam a empresa pelo identificador da rota e expõem apenas opções públicas necessárias ao fluxo. As consultas de agenda administrativa sempre filtram pelo `account_id` da sessão.

**Alternativas consideradas:** concentrar regras no Reflex ou aceitar ids de empresa do navegador enfraqueceria autorização e permitiria acesso cruzado; manter disponibilidade apenas no frontend não evita reservas conflitantes.

### Agrupar os novos contratos sob um grupo Xano de agenda

Criar um grupo de API para operações de horários e agendamentos, com rotas distintas para manutenção administrativa de períodos, disponibilidade pública, criação e consulta/cancelamento da cliente e consulta administrativa da agenda. Configurar sua URL no helper central `api_config.py`. A interface envia apenas os dados necessários à ação; a API não recebe como fonte de autorização uma empresa, cliente ou preço escolhido pelo browser.

A disponibilidade aceita empresa pública, serviço, intervalo de datas e, opcionalmente, profissional. Para “sem preferência”, o backend considera os profissionais ativos vinculados ao serviço e calcula horários elegíveis; na criação, seleciona um profissional que continue livre. A consulta e a criação usam as mesmas regras de elegibilidade, mas a criação recalcula tudo com o horário do servidor para evitar confiar em dados de disponibilidade anteriormente exibidos.

**Alternativas consideradas:** espalhar endpoints de agendamento pelos grupos de autenticação e catálogo misturaria responsabilidades; duplicar regras de disponibilidade na interface e API criaria resultados divergentes.

### Tratar tempo como horário local de atendimento e instante de reserva

Os períodos semanais representam horas de parede no fuso fixo `America/Sao_Paulo`. Os inícios candidatos alinham-se aos quartos de hora do relógio local (`:00`, `:15`, `:30`, `:45`), inclusive quando um período começa fora desses minutos; cada início candidato é convertido para um instante para aplicar limites de antecedência, comparar sobreposições e persistir a reserva. A resposta da API inclui os instantes necessários para confirmar e a interface os apresenta no mesmo fuso. Os limites exatos de 1 hora e 30 dias são aceitos quando coincidem com um início válido; o cálculo final ocorre novamente no momento da criação.

O intervalo ocupado é semiaberto (`início` incluído, `término` excluído), permitindo que um atendimento comece exatamente quando o anterior termina. Um candidato somente é válido se a duração inteira do serviço terminar dentro do mesmo período; períodos distintos não são unidos para acomodar um serviço. Agendamentos em situação `agendado` ocupam horário; `cancelado` libera-o.

**Alternativas consideradas:** armazenar somente texto local como início do agendamento tornaria comparações e limites inconsistentes; usar o fuso do dispositivo faria a oferta variar conforme a cliente.

### Preservar snapshot do serviço e calcular cancelamento no backend

Ao criar a reserva, copiar para o agendamento nome, duração e preço vigentes do serviço. A duração copiada também define o término; consultas futuras usam os valores copiados, sem depender do catálogo atual. Uma alteração posterior no serviço não reescreve reservas existentes.

O backend calcula a antecedência no instante da confirmação do cancelamento: exatamente 8 horas ou mais é gratuito; menos de 8 horas exige a confirmação do aviso da interface e grava a indicação de cancelamento tardio. A interface nunca calcula nem define essa marcação como autoridade e não processa valores monetários. Reservas passadas ou já canceladas não são alteradas.

**Alternativas consideradas:** buscar o serviço atual ao mostrar uma reserva alteraria o histórico; confiar no cliente para decidir a situação tardia permitiria adulterar a política.

### Retomar fluxo público após autenticação sem guardar credenciais na navegação

Manter as escolhas não sensíveis do agendamento como continuação do fluxo (empresa, serviço, preferência/profissional, dia e início), retornando a cliente à rota pública daquela empresa após login ou cadastro. A continuação não inclui senha, token ou dados pessoais e só pode apontar para caminhos internos do BeautyTime. O backend trata todos os ids e o horário retornados como entrada não confiável e revalida-os antes de criar.

Após a confirmação, apresentar os dados do snapshot e a política de cancelamento. A área `/meus-agendamentos` consulta a API com a sessão da cliente e separa registros por início passado/futuro; a rota antiga `/boas-vindas` deixa de ser o destino pós-autenticação. A administradora recebe telas protegidas de Horários e Agenda; a segunda oferece filtros de dia e profissional e não oferece ações de escrita.

**Alternativas consideradas:** exigir que a cliente reinicie as escolhas após login prejudicaria a conversão; colocar token ou credencial em URL exporia informação de sessão; manter cópia local do agendamento sem confirmação do backend permitiria apresentar reserva inexistente.

### Atualizar o contrato documental do domínio junto à entrega

Atualizar `docs/domain-model.md` para remover “concluído” das situações de agendamento e incluir snapshots de serviço, indicação de cancelamento tardio e as regras relevantes desta change. O documento atual contém “concluído”, embora o escopo decidido para a mudança limite a situação a `agendado` e `cancelado`; a implementação deve deixar a documentação coerente com a especificação.

**Alternativas consideradas:** preservar o texto divergente criaria uma fonte conflitante para mudanças futuras; introduzir situação adicional contrariaria o escopo explícito.

## Riscos / Trade-offs

- [Uma alteração de período semanal pode ocorrer enquanto já há reservas futuras nesse período] → Preservar os agendamentos existentes; a edição não os cancela nem altera seus snapshots e a agenda continua exibindo-os.
- [A disponibilidade pode ficar desatualizada entre consulta e confirmação] → Recalcular elegibilidade e conflitos na criação e retornar erro explícito para a interface atualizar a seleção.
- [Duas confirmações muito próximas podem disputar o mesmo profissional] → Validar no Xano Developer o comportamento transacional disponível e manter a checagem de conflito junto da persistência; cobrir a tentativa de reserva conflitante nas verificações HTTP antes de publicar.
- [Conversões de fuso ou mudanças de horário podem exibir a hora incorreta] → Usar exclusivamente `America/Sao_Paulo` na geração, persistir instantes comparáveis e conferir manualmente valores próximos à virada de dia.
- [Agendamentos incluem dados pessoais da cliente] → Restringir projeções e consultas por papel e vínculo; validar por HTTP a separação entre duas clientes e entre duas empresas.
- [Uma publicação de backend sem frontend compatível pode interromper fluxos existentes] → Usar dry-run, revisar alterações, solicitar confirmação antes do push e validar os fluxos após a publicação autorizada.

## Plano de migração

1. Consultar a documentação Xano Developer antes de escrever XanoScript; definir estruturas, funções e endpoints sem remover tabelas ou fluxos existentes.
2. Implementar primeiro os períodos semanais, depois disponibilidade e operações de agendamento, e então as telas consumidoras.
3. Executar validação XanoScript e `xano workspace push --dry-run`; apresentar o resultado e aguardar confirmação explícita antes do push real.
4. Após a publicação autorizada, verificar as chamadas HTTP críticas e percorrer manualmente o fluxo cliente e as telas administrativas em navegador desktop e móvel.
5. Em caso de falha, retirar ou desativar as rotas/telas novas sem apagar registros de agendamentos; preservar dados para correção e nova validação.

Não há migração de reservas antigas prevista: não existe tabela de agendamentos no estado inspecionado do projeto.
