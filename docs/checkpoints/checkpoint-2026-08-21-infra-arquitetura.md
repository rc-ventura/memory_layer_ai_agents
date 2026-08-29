# Reunião de infra dos agentes — 21/08/2026

*Resumo filtrado da reunião entre Rafael Coelho Ventura, Rafael Yoshio Gomes Nomachi ("Yoshio", engenheiro de infra que conduziu a apresentação), Federico Carlos Amorin Criado ("Fed") e o tutor Luis Felipe Chary de Lima, 21/08/2026, ~53 min. Fonte: [`../sources/Infra_dos_agentes_2026-08-21.docx`](../sources/Infra_dos_agentes_2026-08-21.docx) (transcrição automática). Filtrado deliberadamente para o que é relevante ao plano de trabalho — a reunião cobriu bem mais detalhe de infra genérica (frontend Angular, nomes de repositório específicos, etc.) que não entra aqui. Mantido em português, seguindo o padrão do checkpoint de 20/08.*

## Arquitetura, no nível necessário para entender onde a memória entra

Fluxo de uma mensagem no chat: **frontend → API Gateway → proxy (Lambda)**, que verifica se o agente está habilitado. Se não estiver, vai direto para uma LLM tradicional (pergunta → resposta). Se estiver habilitado, a mensagem vai para o **Agent Manager** — um serviço ECS (não é um serviço gerenciado da AWS, é uma aplicação própria, apesar do nome sugerir isso) que decide o que fazer com a mensagem.

- O Manager lê a mensagem: se tiver uma menção `@agente` explícita, ele roteia para o **coordenador operacional** ("esteira") do domínio correspondente (ex.: `@testemunhas` → domínio trabalhista → agente de testemunhas). Se não tiver `@`, pode cair no **coordenador conversacional** (ex.: `@select` para busca de documentos).
- O Manager chama um sub-agente **Workflow** (roda dentro do mesmo ECS do Manager) que usa uma tool (**Trigger Worker**) para acionar o agente operacional específico — isso inicia um **novo runtime, em outro ECS**, um por agente filho (cível, trabalhista, cadastro cível, cadastro trabalhista, etc., cada um com seu próprio repositório).
- Cada agente filho expõe rotas HTTP próprias, atrás de um Load Balancer. Compartilhado entre todos: **um único Postgres** (por conta) e **Redis** (controle de concorrência/filas, para evitar que mensagens simultâneas corrompam o estado de um agente em execução).
- **MCP**: cada squad de produto deveria, em tese, ter seu próprio servidor MCP com as tools específicas do seu agente (hoje, na prática, o time central ainda cria a maioria das tools por enquanto). Existem tools cross-domain também (ex.: `@select`, busca de documento). Cada MCP tem seu próprio Load Balancer + ECS.
- **Autenticação**: não há validação centralizada — o token do usuário do frontend é propagado adiante (proxy → Manager → MCP, via headers), e cada aplicação decide se e como valida esse token. Não é imposto por uma camada comum.
- **Latência/modo de resposta**: chamadas síncronas têm limite de ~30s; a maior parte das respostas de agente é **assíncrona** — o resultado final é publicado num **tópico Kafka**, consumido pela squad que originou a chamada.
- Existe uma **API dedicada de agentes ("Yoda" — Your Omnichannel Digital Agent)** que pula a camada de frontend/chat inteiramente: permite acionar um agente diretamente via API (ex.: disparar o agente de cálculo pra uma pasta específica sem alguém digitar `@cálculo` no chat), com a resposta chegando pelo mesmo tópico Kafka assíncrono.

## Memória — o que já existe hoje na plataforma (três mecanismos distintos, não coordenados entre si)

1. **Memória do Manager (Fed, LangGraph)** — em desenvolvimento. Ontologia: um usuário tem N conversas; cada conversa tem N checkpoints; conversas podem ter documentos associados; checkpoints têm resumos. Mecânica: pega os últimos ~5–6 checkpoints e passa ao modelo; tudo antes dessa janela vira resumo, de forma incremental (resumos de resumos). Fed descreveu isso explicitamente como memória de sessão/conversa — "não é cross memory" (não é compartilhada entre usuários nem entre agentes). Fed mencionou que combinar grafo com busca vetorial é tecnicamente viável na infra atual, mas é só uma opção em aberto, não implementada. Sobre esquecimento, nas palavras do Fed: "tá bem simples, a gente não consegue entrar muito no detalhe."
2. **Memória por execução (Small Agent)** — cada execução de um agente cria uma entidade própria no banco (a "execução do agente"), guardando a resposta final e um dump da memória do Small Agent daquela run. Também explicitamente escopado à execução/chat, não cross-agent nem cross-usuário.
3. **Memória do Hermes (Adriano)** — usa o mecanismo de memória "nativo" do framework Hermes, disponibilizado na plataforma. Não detalhado nesta reunião — fica para a conversa com o Adriano, ainda pendente.

## Próximos passos que ficaram combinados na própria reunião

- Aprofundar com o Fed, numa conversa separada, o desenho da memória do Manager (LangGraph/checkpoints).
- Conversa com o Adriano sobre a memória do Hermes — mesma pendência já registrada desde 20/08.
- Rafael já tem "vários modelos acadêmicos já construídos" que pretende baixar e testar como referência de implementação.

## Não investigado aqui

Ver [`../../discussion/checkpoint-2026-08-21-infra-reflections.md`](../../discussion/checkpoint-2026-08-21-infra-reflections.md) para o que essa reunião confirma, corrige ou abre em relação ao que já estava registrado no repo.
