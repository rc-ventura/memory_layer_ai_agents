# Diário de Campo — Rafael Coelho Ventura

## Semana de 31/08 a 04/09/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 31/08/2026

**Tipo:** reunião — **Sub-atividade:** 2.2 / 2.6 — **Canal:** formal-tutor

**Registro objetivo:** Registro da reunião de checkpoint com o tutor (Luis Felipe) de 28/08/2026, feito agora depois de cruzar o conteúdo com a documentação técnica já existente. Na reunião apresentei a hipótese de arquitetura inteira — o "mega brain" como memory layer agnóstico de framework, acessível por qualquer agente via uma tool MCP. Retorno geral: parte das ideias elogiada, parte não bloqueada mas desencorajada.

- **Gate seletivo STM→LTM.** O tutor desencorajou depender só de escrita incondicional de todo trace. Mesmo que não haja uma tool seletiva do que vira memória de longo prazo, é preciso ao menos um gate para que nem toda STM/trace vire LTM — a volumetria é grande demais e, nas palavras dele, a maioria dos traces "pode não ser nada", então persistir tudo é gravar ruído no mega brain. Precisamos de um mecanismo seletivo do tipo "analisei este trace e isto pode sim ser persistido no mega brain". Os artigos DMF e SAGE implementam algo parecido.
- **Sem tool ADD de memória.** Continuo não achando interessante ter uma tool de ADD de memória; a escrita deve fluir por trigger de sistema.
- **Update Engine como LLM** — o "cérebro" do memory layer — foi bem elogiado. A **camada de governança** (governance layer) também.
- **Banco de traces / signal ledger.** Já existe um banco de traces (o tutor vai fornecer para eu inspecionar), ou seja, já temos ou a base do nosso signal ledger, ou pelo menos um banco bruto para gerar os insights e ativar os triggers. A fonte de trigger do Update Engine passa a ser esse banco de traces, além do sinal de human feedback **negativo** (não o positivo). Ainda cabe termos um signal ledger próprio do Update Engine: um mecanismo determinístico analisa os traces, seleciona os que parecem relevantes/anômalos, junta com os sinais de human feedback e grava no signal ledger para o Update Engine monitorar e avaliar.
- Preciso ainda ler alguns artigos para ter ideia mais clara dos ajustes que teremos que fazer na infra.

Resumo factual da reunião em [`docs/checkpoints/checkpoint-2026-08-28-tutor.md`](../docs/checkpoints/checkpoint-2026-08-28-tutor.md); reflexões cross-cutting em [`discussion/checkpoint-2026-08-28-reflections.md`](../discussion/checkpoint-2026-08-28-reflections.md); atualizações datadas em `open-questions.md`, no doc de arquitetura e no `scope-and-terminology-decisions.md` (feitas na mesma sessão).

**Reflexão:** Cruzei o relato com a documentação antes de registrar, e ele bate — em um ponto eu estava sendo mais conservador do que precisava. O gate seletivo STM→LTM **não é uma modificação nova** do que a gente vinha pensando: é a resolução que já está no `open-questions.md` desde 27/08 — um split de duas camadas em que o **log episódico** recebe ADD incondicional (só texto, sem embedding, barato, serve auditoria e alimenta o Update Engine com sucesso *e* falha) e a **LTM** só recebe o que passa por um gate estilo SAGE (`R ≥ θ1`, ~20–30% do volume). A própria nota de 27/08 diz que SAGE e ADD incondicional nunca foram incompatíveis — a seletividade do SAGE é sobre *promoção para a LTM*, não sobre *escrever o log cru*. O que a reunião de 28/08 acrescenta é corroboração independente do tutor, chegando ao mesmo desenho pelo lado de volumetria e custo. DMF (score determinístico no write) e SAGE (mecânica θ1/θ2) que citei estão certos e já estão na arquitetura e no reading-queue; o gate reusa o `S` do DMF-lite e o decay `R = e^(−τ/S)`, sem máquina nova.

O que é genuinamente novo e vale como questão aberta: **quem é dono do gate de admissão?** O Curador (Update Engine) faz a gestão do que entra no mega brain, ou ele só faz a evolução/update da memória? O lean documentado hoje aponta para dois mecanismos separados — gate de admissão determinístico, barato, sem LLM (`R ≥ θ1`); Update Engine LLM, em lote, para evoluir a strategy layer — mas a linguagem "curador" da reunião borrou os dois. Isso se conecta a sub-perguntas ainda abertas no `open-questions.md` de 27/08 (o `S` do gate é o mesmo do DMF-lite ou um "promotion score" à parte? o gate avalia em schedule, no recall, ou os dois?).

Sobre o signal ledger: comecei conflando "banco de traces" com "signal ledger" e depois separei certo. O banco de traces ≈ fonte bruta para insights/triggers (lado episódico do Memory Store); o Signal Ledger (componente B) é outro store, que guarda os sinais de correção (thumbs, desfecho, flags do filtro determinístico) que o Update Engine monitora. O fluxo que descrevi no fim — filtro determinístico varre os traces → seleciona os relevantes/anômalos → junta com human feedback → grava no signal ledger → Update Engine monitora — é o cold path da arquitetura + o que já ficou registrado em 28/08 (reusar o banco existente, trace-ID + lista de consumidos, latência de sinal assimétrica por tipo de agente).

**Decisão/próximo passo:** (1) Levar ao `open-questions.md` a questão "quem é dono do gate de admissão da LTM — mecanismo determinístico separado ou o Update Engine/curador?", ligando às sub-perguntas de 27/08 sobre o score e a cadência de avaliação do gate. (2) Tratar o gate seletivo STM→LTM como **necessário, não opcional** (lean de 27/08 agora com respaldo do tutor) — mas ainda dependente de calibração de θ1/θ2 no Sub 1.6/1.7. (3) Ler os artigos que sustentam o ajuste de infra, na ordem: SSGM (#1 — governance gate + rollback), SAGE (#19, urgência Tier 2 — a mecânica do promotion gate STM→LTM), DMF (#11 — o princípio do score determinístico) e DarwinMem (#42 — seleção por utilidade + poda, adicionado hoje). (4) Aguardar o tutor fornecer o banco de traces para validar as suposições de schema/conteúdo do trace e o que serve de sinal.

**Tags:** reuniao, tutor, mega-brain, memory-layer, mcp, gate-seletivo, stm-ltm, promotion-gate, sage, dmf, darwinmem, add-tool, update-engine, curador, governance-layer, signal-ledger, banco-de-traces, human-feedback-negativo, trigger, componente-a, componente-b, componente-c, open-questions, checkpoint-28-08, sub-2.2, sub-2.6

## 01/09/2026

**Tipo:** leitura — **Sub-atividade:** 2.1 — **Canal:** pessoal

**Registro objetivo:** Concluiu a leitura própria do SSGM (#1 da fila) e começou hoje a leitura do SAGE (#19 da fila). Avaliou o SSGM como um artigo muito esclarecedor e uma referência forte para a pesquisa. Abriu o SAGE especificamente para embasar a definição do limiar de promoção de conteúdo dos episodic logs para a LTM (o θ1 do gate STM→LTM).

**Reflexão:** A dupla SSGM→SAGE segue exatamente a ordem de leitura que ficou como próximo passo no registro de 31/08 (SSGM #1 → SAGE #19 → DMF #11 → DarwinMem #42), a lista que sustenta o ajuste de infra discutido no checkpoint com o tutor de 28/08. O SSGM já constava como "leitura finalizada" no digest da Semana 2, mas ali foi leitura de sprint por agente; a leitura própria agora fecha parte do item em aberto "leitura própria dos papers do sprint (o dos agentes não substitui)" do digest de 24–28/08, e a avaliação independente do Rafael confirma o valor da referência. O SAGE é o artigo com urgência Tier 2 no reading-queue justamente pela mecânica θ1/θ2 do promotion gate — insumo direto para a questão aberta de 31/08 sobre quem é dono do gate de admissão da LTM (mecanismo determinístico separado vs. Update Engine/curador) e para a calibração de θ1 prevista no Sub 1.6/1.7.

**Decisão/próximo passo:** Terminar a leitura do SAGE e extrair dele a mecânica de limiar (θ1/θ2) para o gate de promoção STM→LTM, alimentando a questão aberta sobre propriedade do gate de admissão. Seguir depois a ordem de 31/08: DMF (#11) e DarwinMem (#42).

**Tags:** leitura, ssgm, sage, promotion-gate, stm-ltm, limiar-ltm, theta1, theta2, episodic-log, ltm, gate-de-admissao, reading-queue, checkpoint-28-08, sub-2.1

### Observação livre — mecanismo de promoção de traces: promover uma "janela" do log cru?

**Tipo:** observação livre — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Continua elaborando o mecanismo de promoção de traces do log cru para a camada recuperável (case-episodic) do memory layer. Hoje existe um banco de traces crus. A opção em consideração: promover uma *janela* de traces crus, transformando-a numa unidade case-episodic armazenada no memory layer. Levanta a ressalva de que uma janela carregaria muito ruído. Registra que uma estratégia simples pode ser aceitável nesta fase.

**Reflexão:** A preocupação com ruído é a mesma premissa do tutor no checkpoint de 28/08 ("a maioria dos traces pode não ser nada") e a estimativa documentada de que ~90% dos casos "é o beabá". O enquadramento "janela" provavelmente precisa virar "stage" ou "caso" (`case_id`): janela deslizante vem de memória conversacional (MemGPT), mas o pipeline jurídico é de stages discretas com evento Kafka, não conversa contínua — a unidade natural de corte é a stage (trigger per-stage, working assumption de 26/08) ou o caso inteiro. Duas bifurcações de desenho ficaram explícitas nesta rodada de conversa: (a) a unidade promovida é o trace cru/estruturado ou um derivado sumarizado por janela — sumarizar no caminho de promoção poria um LLM onde o design hoje quer só um gate determinístico, e sumarização já é o papel da camada 3 (strategy layer); (b) a regra `R = e^(−τ/S) ≥ θ1` está fazendo dois trabalhos ao mesmo tempo — decidir a *entrada* (log → case-episodic) e a *permanência/rebaixamento* dentro da camada recuperável — mas `τ`-desde-recall e o reforço `S→S+1` só existem depois da promoção; fica mais limpo separar entrada (limiar sobre o `S` de nascimento, importância DMF-lite) de rebaixamento (`R ≥ θ1`). "Estratégia simples" é coerente com o "política estática por design" já documentado para o v1.

**Decisão/próximo passo:** Consolidar as duas bifurcações no `discussion/promotion-policy-log-to-ltm.md` como itens explícitos (hoje o doc assume "promove o trace cru" e funde entrada com permanência numa regra só). A escolha entre elas depende de inspecionar o banco de traces real do tutor — o que um trace contém e se os campos do score DMF-lite existem. Fechar antes do Sub 2.2 travar.

**Tags:** promocao-de-traces, log-episodico, case-episodic, memory-layer, gate-de-promocao, ruido, janela, stage, trace-cru, sumarizacao, entrada-vs-permanencia, r-theta1, s-dmf-lite, politica-estatica, promotion-policy, componente-a, sub-2.2

### Observação livre — arquitetura de memória em 3 camadas: janela → reflexão (camada 2 tipada) → meta-reflexão (strategy layer)

**Tipo:** observação livre — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** A partir da leitura do SAGE (em andamento) e da restrição do tutor de 28/08 (não armazenar episodic traces na memória do agente sem filtro, sob risco de ruído), consolidou uma proposta de arquitetura de memória em 3 camadas:

- **Camada 1** — logs crus, o banco de traces que já existe.
- **Camada 2** — de uma janela de contexto dos logs crus (inicialmente determinística e simples: N turnos, sem heurística aprofundada), o Update Engine gera uma primeira reflexão, produzindo significado semântico. A camada 2 é **tipada** (reflexão + log cru), enriquecida com métricas de ciclo de vida (algoritmos de decaimento, força de retrieval), indexada para retrieval do agente, e mantém referência cruzada à camada 1. Um retrieval já traz o significado semântico e também o log cru.
- **Camada 3 (strategy layer)** — o Update Engine gera a strategy layer após um sinal de qualidade; é uma segunda reflexão (meta-reflexão). Mantém referência cruzada aos logs crus da camada 1, para permitir reconsolidação — reajustar/refazer a strategy layer (ex.: corrigir semantic drift) re-executando a reflexão sobre a camada 1.

Pediu análise de consistência contra a conversa antes de gravar.

**Reflexão:** Cruzado com o que foi discutido e documentado hoje no `discussion/promotion-policy-log-to-ltm.md`: a proposta bate quase 1:1 com as subseções "Camada 2 tipada — exemplar + reflexão" e "Provenância entre camadas" adicionadas hoje — camada 2 tipada com o mesmo ciclo de vida nos dois tipos, camada 3 como meta-reflexão, referência cruzada camada 3 → camada 1 direto para a Reversible Reconciliation do SSGM (a camada 1 é a âncora durável porque a camada 2 decai / é evictada). Fundamento na literatura: Generative Agents (árvore de reflexão no mesmo stream recuperável) e SAGE (promove os `r`, não a trajetória crua).

Uma tensão a resolver: nesta proposta a janela vai direto ao Update Engine, **sem gate determinístico antes** — a reflexão do Update Engine passa a ser o único filtro de ruído. Isso diverge da convergência de mais cedo hoje ("tem que haver um gate de promoção"; lean por um filtro booleano determinístico como 1ª etapa). Consequências: (a) a LLM roda sobre janelas não filtradas, inclusive o ~90% "beabá" — o filtro determinístico de anomalia existe no desenho justamente como 1ª etapa para a LLM só rodar no que sobra; (b) todo item recuperável passa a ser mediado por LLM, regressão de auditabilidade frente ao caminho determinístico. Alternativa: janela → filtro determinístico barato (anomalia / sinal erro→recuperação) → Update Engine.

Notas menores: "N turnos" é enquadramento de memória conversacional; o pipeline é de stages Kafka discretas, então a unidade natural de janela é a stage ou o caso, não turnos. O caminho da camada 3 no desenho documentado ainda tem o Commit Gate (D) NLI antes do commit — não mencionado no resumo. A proveniência para replay completo precisa incluir os IDs do Signal Ledger consumidos, não só os trace-IDs da camada 1 (uma strategy acionada por padrão de 👎 não se reconstrói só com replay do log cru).

**Decisão/próximo passo:** Decidir se o v1 tem um filtro determinístico antes do Update Engine (preserva um caminho auditável, corta custo de LLM) ou se a reflexão do Update Engine é o único filtro (mais simples). Trocar "janela de N turnos" por "janela por stage/caso". Terminar a leitura do SAGE. A viabilidade do enriquecimento determinístico (score DMF-lite) segue dependente de inspecionar o banco de traces real do tutor.

**Tags:** arquitetura-3-camadas, memory-layer, camada-2-tipada, reflexao, meta-reflexao, strategy-layer, update-engine, janela-de-contexto, gate-de-promocao, ruido, referencia-cruzada, provenancia, reconciliacao-reversivel, semantic-drift, ssgm, sage, generative-agents, signal-ledger, commit-gate, promotion-policy, sub-2.2

## 02/09/2026

**Tipo:** leitura — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Finalizou a leitura própria do SAGE (#19 da fila). Achado extraído e registrado em [`papers/sage-2026.md`](../papers/sage-2026.md): o SAGE promove conteúdo para a LTM por **dois gatilhos independentes** ("Dual Triggers: Content + Time").

- **Time trigger (`τ`).** A retenção `R(I,τ) = e^(−τ/S)` cai com o tempo desde o último uso. `R ≥ θ1` → item ativo, fica na STM (`M_S`); `θ2 ≤ R < θ1` → decaiu além do uso ativo mas ainda vale para tarefas futuras → **transferido para a LTM**; `R < θ2` → irrelevante/expirado → descartado. É a regra de faixa do MemorySyntax (θ1 > θ2).
- **Content trigger (`r_t`).** Quando o Assistant resolve com sucesso um erro com o Checker, gera uma self-reflection `r_t` (regra/lição estruturada) escrita **direto** na LTM (`M_L ← M_L ∪ {r_t}`), sem limiar.

O Time trigger é o que interessou: gera uma métrica de retenção por unidade de memória — uso alto permanece na STM, uso moderado é promovido, uso baixo é descartado.

**Reflexão:** Pensando na nossa arquitetura: como o mecanismo quer ser um *knowledge infra* (agnóstico, externo ao agente), não temos acesso à STM do agente — só ao log cru / trajetória (o banco de traces que o tutor disse existir). Dúvida que levantei: esse log cru já conta como a STM do agente? Cruzando com o [`discussion/promotion-policy-log-to-ltm.md`](../discussion/promotion-policy-log-to-ltm.md) (posição de 31/08: não há tier STM à la SAGE, a camada 1 já é o holding area completo), a resposta é **não**: a `M_S` do SAGE é contexto de trabalho da tarefa em curso, dentro da janela do agente, e *descarta* o que cai abaixo de `θ2`; o nosso log cru é externo, persistente e **imutável — nunca apaga** (requisito de auditoria jurídica). Memória que esquece ≠ log que não pode apagar. A trajetória *enquanto se acumula* num caso é o análogo funcional do conteúdo da `M_S`, mas ela vive no harness do agente, que o design knowledge-infra deixa de fora de propósito — então não há `M_S` para o mecanismo gerir, ele começa no log.

O Content trigger do SAGE (`M_L ∪ {r_t}` na resolução de erro) é um precedente publicado do sub-sinal **erro→recuperação** já registrado na Estratégia 2 do `promotion-policy-log-to-ltm.md`; e mapeia no nosso caminho de **reflexão** (Update Engine → strategy layer / tipo `reflexão`), não no gate de promoção determinístico. O SAGE escreve o `r_t` direto na LTM sem gate de governança — é o gap que o nosso Commit Gate (componente D) fecha. Isso também resolve a dúvida conjunção-vs-disjunção que tinha ficado em aberto na nota do SAGE: são dois gatilhos separados (Content **ou** Time), não "decay `∧` reflexão".

**Decisão/próximo passo:** (1) Deixar explícito no `promotion-policy-log-to-ltm.md` que o log cru **não é** a STM do agente (argumento: a STM do SAGE descarta, o nosso log por auditoria nunca apaga) — feito nesta sessão. (2) Registrar o mapeamento dos dois gatilhos do SAGE (Time → gate determinístico; Content → caminho de reflexão / erro→recuperação) na tabela de contrastes daquela nota — feito. (3) Seguir a ordem de leitura de 31/08: DMF (#11), depois DarwinMem (#42).

**Tags:** leitura, sage, achado, dual-triggers, time-trigger, content-trigger, self-reflection, r-t, theta1, theta2, memorysyntax, stm-ltm, promotion-gate, knowledge-infra, log-cru, trajetoria, short-term-memory, camada-1, erro-recuperacao, strategy-layer, commit-gate, promotion-policy, sub-2.1, sub-2.2

### Observação livre — a LTM do SAGE é (implicitamente) tipada por caminho de escrita, mapeando na camada 2 tipada

**Tipo:** observação livre — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Elaborou sobre o achado do SAGE registrado mais cedo hoje. Lendo os dois gatilhos como produtores de **duas classes de unidade dentro da LTM (`M_L`)**: (a) a do *Time trigger* — informação de trabalho que decaiu para a faixa `θ2 ≤ R < θ1` e foi transferida da STM, **sem** uma lição destilada associada; (b) a do *Content trigger* — a self-reflection `rₜ` gerada na resolução de erro com o Checker, que **é** uma lição aprendida. Registrou também que o link "Code" da project page do SAGE (`jianhuiwemi.github.io/SAGE` → `github.com/codepassionor/sage`) retorna 404 — não há repositório oficial funcional (verificado nesta sessão); fontes primárias: arXiv abs/HTML/PDF + OpenReview.

**Reflexão:** As duas classes mapeiam quase 1:1 na **camada 2 tipada** (`exemplar` + `reflexão`) já proposta na entrada de 01/09 ("arquitetura de memória em 3 camadas") e em [`discussion/promotion-policy-log-to-ltm.md`](../../discussion/promotion-policy-log-to-ltm.md): a unidade do Time trigger ≈ `exemplar` (episódico, Case-based, admitido por gate determinístico, sem lição); a `rₜ` do Content trigger ≈ `reflexão` (semântico, saída do Update Engine). É a mesma coisa que a nota já registrava como "Time → gate determinístico / Content → caminho de reflexão", vista pelo lado do *tipo de unidade que sai*, não do mecanismo. Ressalvas checadas contra o paper antes de gravar: (a) "unidade episódica / semântica" são rótulos da nossa taxonomia (Sub 1.1, Hu/Liu), **não** do SAGE — o SAGE trata `M_L` como um conjunto só; a tipagem é inferida dos dois caminhos de escrita. (b) O que o caminho Time deposita na LTM é `I*ₜ` — episódico **já processado** pelo MemorySyntax (compressão/reescrita, `S* > S`); a notação do paper (`R(I*ₜ, τ)`, com asterisco) confirma que o roteamento roda sobre a forma otimizada, não a crua. Isso resolve parte da tensão com a linha 15 da nota ("promove os `r`, não a trajetória crua inteira"). Ressalva que fica: o *algoritmo* dessa otimização não está no texto primário — só o fato de que `Iₜ → I*ₜ` acontece. (c) Correção de uma imprecisão minha na descrição da regra de faixa: é `R ≥ θ1` (retenção **alta**) que **mantém** o item na STM; `θ2 ≤ R < θ1` promove para a LTM; `R < θ2` esquece — não é "R abaixo de um limiar → fica na STM".

**Atualização (mesma sessão):** o `I*ₜ` processado ressoa direto com a arquitetura de 3 camadas em prototipagem — camada 2 = forma *consolidada* da camada 1, não realocação do cru. Divergência a manter: a nossa camada 2 é **tipada** e guarda também o `exemplar` **verbatim** (auditoria/replay), coisa que o SAGE não faz (processa `Iₜ → I*ₜ`, não retém cópia crua na LTM); e a camada 3 (2ª ordem, Commit Gate) está além do SAGE.

**Decisão/próximo passo:** Dobrei o mapeamento (Dual Triggers → camada 2 tipada, `I*ₜ` processado, com as ressalvas) em `papers/sage-2026.md` (Dual Triggers + Relevance to the project), `discussion/promotion-policy-log-to-ltm.md` ("Camada 2 tipada" → Fundamento) e `discussion/knowledge-as-infra-architecture-hypothesis.md` ("SAGE reconsidered") nesta sessão. Seguir a ordem de leitura de 31/08: DMF (#11), depois DarwinMem (#42).

**Tags:** observacao-livre, sage, dual-triggers, time-trigger, content-trigger, unidade-episodica, unidade-semantica, camada-2-tipada, exemplar, reflexao, stm-ltm, decaimento, licao-aprendida, taxonomia-hu-liu, repo-quebrado, promotion-policy, arquitetura, sub-2.2
