# Tasks

## 1. Design system central

- [x] 1.1 Atualizar `frontend/frontend/theme.py` com os tokens HEX de `docs/beautytime-design-tokens.json`, variantes de texto acessíveis, tipografia Cormorant Garamond/Manrope com fallback, shell responsivo, superfícies, botões, campos, badges, navegação ativa, estados e sombras; verificar por cálculo de contraste que os pares de texto/superfície usados atendem WCAG AA.
- [x] 1.2 Ajustar a configuração global Reflex para usar os tokens do tema sem alterar rotas ou lógica; verificar que o tema compila e que estilos globais continuam aplicados.

## 2. Páginas públicas, cliente e salão

- [x] 2.1 Aplicar o design system à página inicial, logins/cadastros de cliente e salão, área da cliente e busca `/saloes`; verificar campos rotulados, botões, estados vazio/erro/carregamento e navegação existentes sem mudar handlers ou destinos.
- [x] 2.2 Aplicar o design system a `/agendar/[identificador]`, incluindo seleção, resumo, confirmação e mensagens; verificar que serviços, horários, autenticação e ações de agendamento continuam usando os mesmos handlers e fluxo.
- [x] 2.3 Aplicar o design system ao painel e às páginas de Serviços, Profissionais, Horários e Agenda; verificar item de menu ativo, badges de status, estados visuais e que cada card do painel é clicável para sua rota atual.

## 3. Painel da plataforma

- [x] 3.1 Aplicar os tokens e componentes compartilhados às páginas `/platform/login`, `/platform` e `/platform/saloes/[account_id]`; verificar formulários, cards, abas, botões de edição e estados carregando/vazio/erro sem alterar a API nem as ações existentes.

## 4. Verificação integrada

- [x] 4.1 Executar a compilação Reflex existente e revisar o diff para confirmar que somente aparência/clareza foi modificada, sem alteração de rotas, endpoints, payloads, handlers ou regras; registrar o resultado.
- [x] 4.2 Usar o servidor já ativo em `http://localhost:3000` para abrir e conferir `/`, `/clientes/cadastro`, `/clientes/login`, `/admin/cadastro`, `/admin/login`, `/admin`, `/admin/servicos`, `/admin/profissionais`, `/admin/horarios`, `/admin/agenda`, `/meus-agendamentos`, `/saloes`, `/boas-vindas`, `/agendar/{identificador}`, `/platform/login`, `/platform` e `/platform/saloes/{account_id}`; testar viewport móvel e desktop, estados relevantes e ausência de cortes, sem iniciar outra instância.
- [ ] 4.3 Confirmar no navegador contraste WCAG AA para texto, fontes/fallbacks, alinhamento mobile, foco/interatividade dos controles e consistência visual; corrigir qualquer falha observada e revalidar as rotas afetadas.

### Resultados de validação

- `python -m reflex compile --dry`: sucesso; compilação Reflex concluída em 1,25 s.
- `python -m compileall -q frontend/frontend frontend/rxconfig.py`: sucesso.
- As declarações de rotas atuais coincidem com o baseline. O diff também contém a chamada a `admin/dashboard` já existente na alteração não commitada do painel; ela foi preservada, sem edição nesta mudança.
- As 17 rotas foram abertas em `localhost:3000` em viewports de 1440 px e 375 px; todas responderam HTTP 200 e não apresentaram overflow horizontal na medição do documento.
- O navegador reportou `ERR_CONNECTION_REFUSED` para o WebSocket de eventos em `localhost:8001`; as páginas não receberam estado dinâmico e o bundle servido mostrou a aparência antiga. Nenhum processo foi reiniciado. Por isso, a inspeção visual da tipografia, cores, estados e foco em execução permanece pendente em 4.3.
- Nesta tentativa final, a home renderizou em viewport de 375 px com Cormorant Garamond e Manrope; os pares de texto secundário e principal sobre fundos claros foram calculados acima de 4,5:1. Ao navegar pelas rotas, a conexão de eventos falhou e as páginas seguintes ficaram sem conteúdo renderizado; foco e estados visuais do app completo não puderam ser confirmados, então 4.3 permanece pendente.
- Uma execução de `reflex compile` sem `--dry` chegou a 100%, mas falhou na limpeza npm por `EBUSY` em `.web/node_modules` enquanto o servidor estava aberto; o `package-lock.json` já estava alterado antes da execução e permaneceu sem restauração.
