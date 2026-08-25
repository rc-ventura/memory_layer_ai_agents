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
