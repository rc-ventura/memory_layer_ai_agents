# Diário de Campo — Rafael Coelho Ventura

## Semana de 24/08 a 30/08/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias) + camada semântica (síntese semanal ao final desta semana). Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 24/08/2026

**Tipo:** achado — **Sub-atividade:** 1.6 — **Canal:** pessoal

**Registro objetivo:** Ao finalizar a leitura do survey "Memory in the Age of AI Agents" (Hu, Liu et al.), na p.70, seção 7.2.2, encontrei um achado relevante para o desenho do mecanismo: o survey aponta que uma direção promissora para gerenciamento de memória verdadeiramente automatizado é integrar construção, evolução e recuperação de memória diretamente no loop de decisão do agente via chamadas explícitas de tool (tool calls) — fazendo o próprio agente raciocinar sobre as operações de memória (add/update/delete/retrieval), em vez de depender de módulos externos ou workflows hand-crafted. Segundo o survey, isso leva a um comportamento de memória mais coerente, transparente e contextualmente fundamentado, comparado a desenhos que separam o raciocínio interno do agente das suas próprias ações de gerenciamento de memória.

**Reflexão:** Isso me parece reforçar que integrar a gestão de memória no próprio loop do agente (via tool calls) é mais promissor do que um módulo externo separado — e se conecta direto com a comparação já prevista no Sub 1.6 (loop de aprendizado fechado nativo vs. memória transparente com controle programático explícito). Também traz um argumento de design a favor da abordagem "nativa": o agente sabe exatamente qual operação de memória executou (add/update/delete/retrieval), o que dá mais transparência e rastreabilidade — relevante pro contexto jurídico, onde auditabilidade importa. Nota à parte: a entrada de 20/08 já tinha registrado a leitura deste survey como finalizada; esta é uma segunda passada mais detida, chegando a achados específicos que a primeira leitura não tinha capturado.

**Decisão/próximo passo:** Considerar a abordagem de memória via tool calls integrada ao loop nativo do agente como candidata prioritária para os POCs mínimos do Sub 1.6, frente a um módulo externo separado.

**Tags:** memory-in-the-age-of-ai-agents, tool-based-memory, loop-nativo, sub-1.6, arquitetura, achado

### Achado — comparação galho a galho entre os mind maps do Zhang et al. e do Hu/Liu et al.

**Tipo:** achado — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Fiz a comparação pendente desde 21/08 entre as taxonomias dos dois surveys âncora, usando os dois mind maps já existentes no repo (`literature-review/visual-synthesis/`). Resultado registrado em [`discussion/zhang-vs-hu-taxonomy-reconciliation.md`](../discussion/zhang-vs-hu-taxonomy-reconciliation.md): os dois convergem fortemente no eixo operacional/de ciclo de vida (Writing/Management/Reading do Zhang ≈ Formation/Evolution/Retrieval do Hu) — inclusive "forgetting" aparece com o mesmo nome nos dois, exatamente no achado central do projeto. Divergem na moldura classificatória: Sources (Zhang) não tem equivalente no Hu, Functions (Hu) não tem equivalente no Zhang, e "Forms" corta diferente nos dois (Zhang mistura estrutura com recência/recuperação; Hu separa isso em galhos distintos).

**Reflexão:** Não é "incomensurável" como eu tinha repetido antes nesta sessão (herdado sem verificar de um export de memória externo, não de algo já registrado neste repo) — é convergência real na parte que mais importa, e divergência real só na moldura ao redor. A recomendação prática: usar a Operations do Zhang como vocabulário principal do relatório M1, citando a Dynamics do Hu quando precisar de mais granularidade (ex.: "Consolidation" em vez de só "management").

**Decisão/próximo passo:** Fecha o item "mind map dos dois surveys" que estava pendente desde 21/08.

**Tags:** zhang-survey, memory-in-the-age-of-ai-agents, mind-map, taxonomia, entregavel-m1, pendencia-fechada

### Decisão — pendência: terceiro survey + síntese de conceitos/taxonomias/técnicas para o M1

**Tipo:** decisão — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Fica registrado como pendência: finalizar a leitura do terceiro survey sobre memória ("From Storage to Experience", Luo et al., 2026, arXiv:2605.06716) e, a partir dos três surveys (Zhang et al., Hu/Liu et al. e este), criar uma síntese de conceitos, taxonomias e técnicas para balizar o relatório do Entregável M1.

**Reflexão:** Isso dá sequência natural à comparação Zhang×Hu feita hoje mais cedo (`discussion/zhang-vs-hu-taxonomy-reconciliation.md`) — em vez de comparar os três dois a dois, a ideia discutida foi construir uma síntese unificada (um "quarto mapa", de autoria própria) usando o eixo operacional como espinha dorsal, e não apenas redesenhar os três lado a lado.

**Decisão/próximo passo:** Finalizar a leitura de "From Storage to Experience"; depois, montar a síntese de conceitos/taxonomias/técnicas cruzando os três surveys, como subsídio direto para o relatório M1.

**Tags:** from-storage-to-experience, sintese-taxonomias, entregavel-m1, pendencia, sub-1.1

### Reunião — transcrição da reunião de infra (21/08) anexada e processada

**Tipo:** reunião — **Sub-atividade:** 2.5 — **Canal:** pessoal

**Registro objetivo:** Anexei e processei a transcrição da reunião de infra dos agentes com Yoshio, Fed e o tutor (21/08, pendente desde então). Resumo filtrado em [`docs/checkpoint-2026-08-21-infra-arquitetura.md`](../docs/checkpoint-2026-08-21-infra-arquitetura.md), reflexões em [`discussion/checkpoint-2026-08-21-infra-reflections.md`](../discussion/checkpoint-2026-08-21-infra-reflections.md). Mapeei a arquitetura até onde a memória entra (Gateway → Manager ECS → coordenadores → agentes filhos, cada um em seu próprio ECS; MCP; Postgres único + Redis; modo síncrono vs. API "Yoda" assíncrona via Kafka) e os três mecanismos de memória que já coexistem na plataforma hoje, sem coordenação entre si: checkpoints LangGraph do Manager (do Fed), dump de memória por execução do Small Agent, e a memória nativa do Hermes (ainda não detalhada).

**Reflexão:** Achado forte: o Fed confirmou de próprio punho que o esquecimento no mecanismo dele "tá bem simples, a gente não consegue entrar muito no detalhe" — é a lacuna cross-trial × forgetting do Zhang et al. confirmada dentro da própria plataforma, não só na literatura. Também corrigi um erro meu: o que o Fed está construindo é LangGraph (checkpoints de estado), não GraphRAG — atualizei o motivo da trilha de leitura de GraphRAG no `reading-queue.md` pra refletir isso (o vínculo com o trabalho do Fed era mais fraco do que eu tinha registrado).

**Decisão/próximo passo:** Fecha a pendência de anexar a transcrição de 21/08. Novo item aberto: decidir se o mecanismo (M3) deve conviver, unificar ou substituir os três mecanismos de memória já existentes.

**Tags:** infra, yoshio, fed, langgraph, kafka, yoda, arquitetura, sub-2.5, transcricao-anexada, pendencia-fechada

### Leitura — sprint de sub-agentes sobre os papers da fila (SAGE, Memento, Mem-α, ExpeL, MemoryBank, Generative Agents, SCM, Retroformer, Casper et al.)

**Tipo:** leitura — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Numa conversa com o Claude sobre como o framework de memória (arquitetura "knowledge as infra") deveria ficar, pedi para ele disparar sub-agentes em paralelo pra ler de fato o texto completo (não só verificar metadado bibliográfico) dos papers prioritários da fila — SAGE, Memento, Mem-α, ExpeL, MemoryBank, Generative Agents, SCM, Retroformer e Casper et al. (confiabilidade de RLHF binário). Deixamos de fora Synapse/MetaGPT/TiM/RecAgent/S³ porque só servem pra completude do corpus, não pro desenho. **Importante: essa é leitura feita pelo Claude via sub-agentes, não leitura minha** — os achados estão registrados em [`../discussion/reading-sprint-2026-08-24-queue-papers.md`](../discussion/reading-sprint-2026-08-24-queue-papers.md), com essa distinção marcada explicitamente no topo do arquivo. 8 dos 9 sub-agentes retornaram relatório completo; o do Casper et al. ainda está pendente no momento deste registro.

**Reflexão:** O achado mais forte foi negativo, no bom sentido: nenhum dos 8 papers lidos combina as cinco coisas que o mecanismo do projeto precisa — memória não-paramétrica, sinal de correção externo/humano, atualização controlada em lote, versionamento/rollback, e esquecimento com delete de verdade. Cada um resolve um pedaço só (MemoryBank e SAGE têm decaimento tipo Ebbinghaus mas sem hard-delete de verdade; ExpeL e SCM têm lógica de atualização mas sem trilha de auditoria; Memento tem escrita explícita mas nunca descarta nada). Isso é uma confirmação bem mais concreta do achado central (interseção vazia cross-trial × forgetting) do que a tabela do survey — agora em nível de mecanismo, não só de checkmark. Também resolveu duas dúvidas de escopo: Mem-α é confirmadamente paramétrico (mesmo bucket do Retroformer/Memory-R1, fora de escopo), e SAGE não ameaça o achado central (reivindica cross-trial mas não isola isso experimentalmente — vira uma ressalva de uma frase no M1, não uma reformulação).

**Decisão/próximo passo:** Atualizar `cross-trial-vs-forgetting-gap.md`, `scope-and-terminology-decisions.md` e `open-questions.md` com essas resoluções, e anotar (sem marcar como lido por mim) os itens correspondentes em `papers/reading-queue.md`. Minha própria leitura desses papers continua em aberto na fila — isso não substitui ela.

**Tags:** sub-agentes, sage, memento, mem-alpha, expel, memorybank, generative-agents, scm, retroformer, casper, leitura-por-claude, sub-1.1, arquitetura-framework

## 25/08/2026

**Tipo:** achado — **Sub-atividade:** 1.2 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Pesquisei o conceito de "loop engineering" da LangChain (post oficial "The Art of Loop Engineering") em relação aos Deep Agents, pra ver se os conceitos de lá se alinham com a arquitetura de memória que estamos desenhando (KaI — knowledge as infra), caso a gente queira futuramente plugar o mecanismo num Deep Agent. O post descreve quatro loops aninhados: Agent (loop central de tool-calling), Verification (grader por rubrica + retry), Event-Driven (gatilho externo dispara execução), e Hill-Climbing (traces de produção alimentam um agente de análise que propõe mudança de configuração do harness — prompt, tool, grader — com revisão humana descrita como opcional antes do deploy). O post confirma explicitamente que memória é um dos alvos do hill-climbing: "auxiliary context like memory and retrieved skills can be improved the same way."

**Reflexão:** O mapeamento bate quase ponto a ponto com os componentes que já tínhamos desenhado — Loop 1 é o caminho quente (`recall_memory`), Loops 2/3 são a captura de sinal dupla (copiloto via rubrica / sistêmico via evento, mesmo formato do par Yoda/Kafka já mapeado), e o Loop 4 é essencialmente o nosso Update Engine. É uma confirmação independente, vinda da própria indústria e não da literatura acadêmica, de que a moldura "memory-update = harness-adjustment" — que o tutor já tinha confirmado com as próprias palavras dele em 20/08 — não é uma interpretação isolada nossa. Mas achei duas lacunas reais no design deles: revisão humana antes do deploy é descrita como opcional, não obrigatória, e não há menção nenhuma a versionamento, rollback ou trilha de auditoria — exatamente as duas coisas que o nosso Commit Gate (informado pelo SSGM, lido ontem) adiciona. Se formos plugar o mecanismo num Deep Agent no futuro, os Loops 1-3 encaixam quase sem atrito, mas o Loop 4 sozinho não seria suficiente pro contexto de compliance jurídico — precisaríamos sobrepor nosso próprio gate mais rígido, não reusar o deles como está.

**Decisão/próximo passo:** Atualizei `discussion/framework-comparison-hermes-smolagents-deepagents.md` e `discussion/knowledge-as-infra-architecture-hypothesis.md` (componente F) com esse mapeamento e essa ressalva.

**Tags:** loop-engineering, langchain, deep-agents, hill-climbing-loop, commit-gate, arquitetura-kai, sub-1.2, sub-2.2

## 26/08/2026

**Tipo:** decisão — **Sub-atividade:** 1.6 / 2.2 / 2.3 — **Canal:** pessoal

**Registro objetivo:** Resolvi começar a prototipar uma potencial memory layer. A premissa é montar algo agnóstico de framework, onde cada agente pudesse plugar como uma tool via MCP (infra já usada pela empresa). Mediante as discussões atuais sobre a era do "Knowledge as Infra", a ideia é que cada agente possa fazer uso dessa layer dentro do próprio loop da working memory através de uma tool call — não injeção silenciosa, mas uma chamada explícita e auditável dentro do próprio trace de raciocínio do agente. Pela revisão bibliográfica, entendi que pensar em memória é pensar em cada etapa da memória — neste registro, foquei no Write: o que desencadeia a escrita.

A infra proposta evidencia o componente principal, o componente A: Memory Store. Qualquer agente com a tool `recall_memory` pode acessar via MCP e fazer o retrieve da memória. A escrita não tem uma tool específica como `add_memory`, visto que isso poderia fazer com que o agente não registrasse um caso — e registrar não deve ser decisão do agente (completeness gap para auditabilidade jurídica). Então o write de memória é definido de forma incondicional por um trigger de pipeline de cada agente: um agente de cadastro, ao finalizar sua task (gerar novo cadastro e publicar o evento), trigga o write da memory layer. Esse trace passa por uma camada de transform na memory store — para add metadata, calcular um score de sobrevivência (princípio DMF, não a implementação completa de 8 camadas), passar por embedding e qualquer estratégia que queiramos implementar a partir do dado bruto antes de armazenar na memória.

Inicialmente a memory store pode ser um banco de dados com armazenamento vetorial para retrieval — o substrate exato ainda está aberto (candidato leading: Postgres+pgvector, mesma lógica de "evitar nova dependência operacional" já usada para descartar git como substrate; vector DB dedicado não descartado). O conteúdo seria texto plano 1D (flat), não grafo — "1D" refere-se à estrutura do conteúdo (string linear), não ao substrate. Grafos foram explicitamente decididos contra para v1 (a ablação LoCoMo do Mem0g só ajuda em raciocínio temporal/relacional, não é ganho genérico), revisitável em v2 se Sub 1.4 confirmar necessidade relacional/multi-hop. Ali residirão os episodic traces — matéria-prima da Case-based/Experiential Memory (não Factual Memory: na taxonomia Hu/Liu que o projeto adota, Factual e Experiential são categorias distintas em Functions; os traces crus são Experiential/Case-based, e o que se aproxima de factual/semantic é a strategy layer derivada, output do processamento).

Leituras importantes para este componente: SAGE, MemoryBank, DMF e SSGM (esta última central pelo Reversible Reconciliation — append-only immutable log como source-of-truth + strategy layer mutável e replayable, e pelo decay Weibull mais expressivo que o exponential do MemoryBank).

**Reflexão:** É importante registrar que toda esta arquitetura é uma hipótese, não uma arquitetura fechada — ela só se gradua em decisão depois dos POCs mínimos do Sub 1.6 e da comparação implícito-vs-explícito do Sub 1.7 testarem-na contra comportamento real. A prototipagem que decidi começar é justamente esse teste. Há uma tensão não-resolvida que estou levando comigo: SAGE tem um promotion gate seletivo (só itens que cruzam θ1 viram LTM), em conflito direto com o ADD incondicional que escolhi — o doc de arquitetura marca isso explicitamente como aberto, e vale investigar se o gate seletivo do SAGE deveria ser adotado para algo outro que não o log episódico completo (ex.: como mecanismo decidindo o que é promovido para a strategy layer). A granularidade do trigger ("ao finalizar a task" = per-stage) é working assumption meu de 26/08, ainda não validada com o tutor — cada agente filho (cadastro, subsídios, contestação) já publica seu resultado em tópico Kafka ao completar sua stage (infra confirmada live), então cada publicação é um trigger candidato natural. Há também cinco gaps abertos no write-path do componente A que estou entrando na prototipagem ciente: schema exato, substrate físico, categoria de vector storage, estratégia de chunking, e — o mais profundo, upstream dos outros quatro — o que um "episodic trace" efetivamente contém (business-record summary vs. trajetória ExpeL/ReAct completa).

**Decisão/próximo passo:** Iniciar a prototipagem do componente A (Memory Store) como POC mínima. Resolver o gap mais upstream primeiro: definir o que um "episodic trace" contém, antes de atacar schema/chunking/substrate. Validar a granularidade per-stage do trigger com o tutor antes de tratá-la como decidida. Investigar a tensão SAGE-seletivo vs. ADD-incondicional como parte da prototipagem, não como decisão prévia.

**Tags:** knowledge-as-infra, memory-store, componente-a, mcp, tool-call, write-trigger, dmf, sage, memorybank, ssgm, pgvector, hipotese, sub-1.6, sub-2.2, sub-2.3, prototipagem
