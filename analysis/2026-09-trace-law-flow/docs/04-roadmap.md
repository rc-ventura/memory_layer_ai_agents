# Roadmap — o que falta

**Atualizado:** 2026-09-08. Consolidação do que ficou em aberto ao longo da análise do primeiro trace.
Prioridades e decisões de escopo confirmadas com o Rafael. Ver também
[`../../../discussion/open-questions.md`](../../../discussion/open-questions.md) para a versão canônica da
discussão de escopo (groundedness determinístico vs. juiz) registrada no nível do projeto, não só desta pasta.

## Urgente — estrutural, não analítico

- [ ] **Criar branch e commitar todo o trabalho.** Hoje tudo (pasta `analysis/` inteira + edições em
  `.gitignore`, `CLAUDE.md`, `README.md`, `papers/reading-queue.md`) está direto no `main`, não versionado.
  Pela convenção do projeto: branch `2026-09-08-<slug>`, depois commit.

## Monitoramento — não é candidato ativo, mas tem gatilho de reabertura

- [ ] **"Resposta sem bloco de código" (Protocolo do harness).** Rebaixado da v1 por ficar concentrado em
  dez/2025 (31/33 casos) e sumir depois (0 em 3.461 steps de mai–ago/2026). Rótulo é `[INATIVO desde
  dez/2025]`, não `[RESOLVIDO]` — não sabemos a causa e não controlamos o harness. **Gatilho de reabertura:**
  ≥2 casos num mês, ou taxa > 1/1k steps (teto do IC95% do regime pós-incidente). Verificar a cada nova
  extração do trace. Ver `02-relatorio-achados.md` §6.

## Fora de escopo / adiado

- ~~**Groundedness semântico** (o juiz que confirma se a citação está CERTA, não só se aparece)~~ —
  fora de escopo do v1. Exige LLM-as-judge ou humano — não-determinístico, incompatível com o princípio já
  documentado de que o v1 inteiro é regra fixa e auditável (ver
  [`../../../discussion/open-questions.md`](../../../discussion/open-questions.md), item "Which parameters...
  should become adaptive"). Pertence a observabilidade/agent-evals como disciplina própria, ou a um v2 que
  relaxe a restrição de determinismo.
- **Minerar o candidato 1 automaticamente** (schema de retorno sem LLM) — adiado, não é prioridade agora.

## Analítico — em aberto, em ordem de valor

| # | Item | O que falta, em uma frase |
|---|---|---|
| 1 | **Groundedness-como-presença (determinístico)** | Extrair tokens tipados (CNJ, CPF/CNPJ, data, valor) do `final_answer` e checar se o texto aparece literalmente em alguma observação anterior — regex puro, zero LLM. **Reclassificado de "fora de escopo" pra ativo em 2026-09-08**: é proxy (presença ≠ correção), mas é determinístico, cabe no pipeline "por hora" tanto quanto os 8 achados de hoje. |
| 2 | **Rodar detectores nas execuções sem erro — versão determinística primeiro** | 91,4% dos steps (5.283 de 5.781) nunca foram olhados semanticamente. Antes de cogitar juiz LLM, tentar o proxy determinístico já esboçado durante a leitura do AgentDebug: contar `code_action` com padrão de validação (`assert`, `if not`, `len(`, `is None`, `try/except` com recuperação) vs. steps que só consomem sem checar. Juiz LLM/anotação manual só se o proxy não bastar. |
| 3 | **Segunda extração sem `LIMIT`** | O trace tem exatamente 1.000 linhas (provável `LIMIT`) — amostra, não população. Confirmar também com o time da esteira o que os status 1/2/3/34 realmente significam (hoje inferido por correlação). |
| 4 | **Instruction Non-compliance** | Nossa taxonomia inteira é baseada em exceção; o TRAIL mostra que, na arquitetura idêntica à nossa, esse é o erro nº 1 (35,5%) e nunca levanta exceção. Escrever um detector determinístico por regra explícita do system prompt. |
| 5 | **Resolver Tool-Skip de vez** | Nunca convergiu: deu 14 / 8 / 10 execuções em três rodadas, dependendo do inventário de ferramentas usado. Corrigir extraindo o inventário **por papel**, não a união de todos; depois testar robustez como os outros seis achados desta sessão. |
| 6 | **Reasoning-action mismatch — versão determinística primeiro** | A versão por palavra-chave foi retirada por estar conceitualmente errada (comparava thought pré-execução com erro pós-execução) — isso não muda. Mas existe uma versão determinística diferente, já esboçada: comparar o nome de agente/ferramenta que o *thought* anuncia (regex) contra o que o `code_action` de fato chama (AST), no mesmo step — divergência = candidato, sem juiz. Só tentar juiz LLM/anotação manual se essa comparação estrutural não capturar o fenômeno. |
| 7 | **Erro estrutural de argumento de tool — determinístico** | Distinto do item 5 (ferramenta que faltou) e do item 6 (thought anuncia X, código chama Y): comparar a chamada real (AST do `code_action`) contra a **assinatura declarada no system prompt** de cada tool — nº de args, nomes, posicional-onde-era-nomeado, tipo incompatível, args trocados. "Camada 1.5": mais fundo que `TypeError`, mais raso que "por que o agente errou". 100% determinístico; o detector "argumento posicional" (n=35) já é um pedaço. **Não** cobre erro de *valor* ("mandou CPF no campo do CNPJ") — isso precisa de oráculo/juiz. Valor menor que os itens acima: o trace é dominado por erro no código gerado, não por chamada malformada de tool declarada. |
| 8 | **Decompor o custo por chamada de ferramenta (§3.3) em alavancas** | O `141.673 tokens/chamada` do `CalculoCivel` mistura duas causas com consertos diferentes: **(a) contexto re-enviado** — os mesmos documentos/histórico entram no `tok_in` de cada step (alavanca: prompt caching, poda de histórico, sumarização) vs. **(b) trajetória longa** — muitos steps por chamada de ferramenta (alavanca: cortar passos de raciocínio/formatação). Medir por papel: `tok_in` médio por step × nº de steps por chamada de ferramenta; e, dentro do `tok_in`, a fração que é conteúdo repetido entre `model_input_messages` de steps consecutivos. Determinístico. **Não** é o split "in vs out" (esse seria quase plano — input já domina ~33:1, `01-racionais.md` §3.3). Não muda a tese (erro→memória) — é observabilidade/custo, valor operacional. |
| 9 | **Decompor a subida mensal do §3.6 (erro × baseline limpo × trajetória)** | §3.6 mostra a mediana de tokens/execução subindo em 2026 (dez/2025 ~54k → abr 95k, mai 82k, jul 92k) e conclui "sem melhora orgânica" — mas mediana subir não distingue "o mesmo trabalho ficou mais caro" de "a carga mudou". Por mês (7 meses com `n ≥ ~20`): (1) taxa de erro (erros/1k steps ou % execuções com ≥1 erro); (2) **% dos tokens do mês gastos em steps com erro** (o "% desperdiçado" do §3.5, agora mensal); (3) **mediana de tokens/execução removendo os steps com erro** — baseline "limpo"; (4) mediana de steps/execução (trajetória). Se os meses caros também lideram (1)/(2) → gasto de token **é** sinal de desperdício por erro, memória ataca direto; se lideram (3)/(4) com erro normal → é carga/trajetória, alavanca é o item 8. **Não** é correlação estatística (7 pontos — é "o padrão bate ou não") e erro × trajetória são confundidos (erro gera retry que alonga a trajetória — §3: 7 vs. 5 steps). Determinístico; o dado já existe. Resolve a ressalva anexada ao §3.6. |

**Sub-recorte do item 1 (priorização):** antes de rodar o check de groundedness em tudo, cruzar as **310
execuções que tiveram erro e ainda entregaram resposta de conteúdo** (`01-racionais.md` §4 / `02-relatorio-achados.md`
§3.1) **por assinatura de erro** — `pd.crosstab`, o dado já existe (§2 classificou os 498 steps). Ordenar a
fila: execução que "se recuperou" de erro de **schema/dado** (dict como lista, `KeyError` num campo, tipo
diferente do esperado) é onde a resposta final mais corre risco de citar valor errado → checar primeiro;
execução que só teve erro **cosmético** (string não fechada reescrita e seguida) → risco baixo, fim da fila.
Ver também "iniciador vs. seguidor" na §"Fundamentação emprestada do AgentDebug" #2.

**Sub-passo do item 8 (fazer antes de medir):** §3.4 prova que 10% das execuções concentram 54,6% do gasto,
mas **nunca caracteriza o perfil dessa cauda** — a execução mais cara (5,9M tokens, ~60–120× a mediana) só é
citada como curiosidade solta (`01-racionais.md` §3.4 Passo 1). Antes de rodar o item 8 em escala, **ler o JSON
das ~10 execuções do topo** (ordenar as 840 por `tok_tot`, abrir com `drill_down.py`): um parágrafo por
execução sobre onde os tokens foram — contexto re-enviado (mesmo documento no `model_input_messages` de N
steps) vs. trajetória longa vs. recursão de subagente vs. repetição da mesma chamada (o recorde de 10
repetições consecutivas de §4 pode viver aqui). Para as 84 do decil (ler todas é demais): **agregados
estruturais** só — nº de steps, tamanho médio de contexto, nº de delegações, nº de chamadas repetidas. Isso é
a ponta qualitativa que **gera a hipótese de alavanca** que o item 8 então quantifica; rodar o item 8 sem esse
olhar é medir no escuro. Ressalvas: (a) **PII** — os JSONs do topo têm nome de cliente, nº de processo, texto
de peça em claro; só terminal local, e o que se escreve é **estrutura**, nunca conteúdo (mesma regra do
`drill_down.py`); (b) **n≈10 é anedota**, não taxa — a saída é "hipóteses para o item 8", não número de
relatório; (c) se a #1 for só um **loop patológico** (as repetições consecutivas), ela dobra na história de
reincidência de §4, não é história de custo — vale saber qual dos dois é.

### Camadas de "causa" — o que a taxonomia atual alcança e o que não

Nota conceitual, registrada 09/09/2026. Os erros do relatório estão classificados na **camada 1**:

- **Camada 0** — a exceção crua (`KeyError: 'valor_causa'` na linha 3).
- **Camada 1** — a categoria de *mecanismo* que o `classify()` produz ("retornou dict, agente indexou como lista"). Determinística, do texto do trace. **É o teto do v1.**
- **Camada 2** — *por que* o agente escreveu aquele código (schema alucinado? visto-e-esquecido? o schema mudou? system prompt errado? ruído de sampling?). Precisa de LLM sobre os casos **ou** de um oráculo (a assinatura real da tool).

Estado: camada 2 só existe como **hipótese escrita à mão** para as 7 assinaturas-candidato (o "conteúdo proposto" da tabela `CAND`, `01-racionais.md` §7) — não derivada, não validada. Para as ~5 assinaturas excluídas do §7, não existe (foram excluídas por não terem causa única). O achado central (86,3% leram / 11,9% reincidiram) é o único corte de camada 2 feito por método, e é sobre o *fenômeno* "reincidência", não por assinatura. A derivação por método é a fase "Construir os candidatos de memória de verdade" (abaixo).

## Fundamentação emprestada do AgentDebug (arXiv:2509.25370)

Três achados do paper que embasam decisões acima. **Todos são sobre os benchmarks do AgentDebug**
(ALFWorld/WebShop/GAIA — espaço de ação fechado, reward automático, single-agent), **não medidos neste
trace** — entram como justificativa atribuída, com a ressalva de domínio. Registro completo e caveats em
[`../literature/agentdebug-2509.25370.md`](../literature/agentdebug-2509.25370.md).

1. **"Focar em causa-raiz, não em consertar todo erro de superfície, é o que dá ganho"** (ablação, §1,
   verbatim: *"focusing on root-cause errors, rather than attempting to fix every surface-level mistake, is
   key to efficient debugging and meaningful performance gains"*). Ressalva: ablação no benchmark deles.
   **Sustenta** a política de escrita **"uma unidade de memória por cascata, na raiz"** — não uma por step
   com erro (≈498 steps com erro → ~150–250 raízes de cascata, menos após dedup por assinatura). Ver
   [`../../../discussion/knowledge-as-infra-architecture-hypothesis.md`](../../../discussion/knowledge-as-infra-architecture-hypothesis.md)
   §C.

2. **"Error propagation is the primary bottleneck… early mistakes cascade"** (insight central, §2.1).
   Ressalva: afirmação do paper, **ilustrada não medida** — o AgentDebug não tem métrica de propagação (só
   a Figura 8, ilustrativa). **Sustenta** priorizar as análises de cascata abaixo (candidatas a entrar na
   tabela analítica acima), além do coeficiente básico `1,8×` já computado (`03-procedimento-validacao.md`
   §1.6):
   - **Coeficiente de propagação estratificado** — `P(erro em k+1 | erro em k)` vs.
     `P(erro em k+1 | sem erro em k)`, por papel e por tipo de erro.
   - **Iniciador vs. seguidor** — distribuição de `first_err_type` vs. `err_type` em todos os steps: se
     diferem, alguns tipos iniciam a cascata e outros só a seguem.
   - **Custo por cascata** — `sum(tokens | step ≥ first_err_step)` vs. `sum(tokens | step < first_err_step)`:
     decompõe o "~3× mais tokens" em quanto vem da cascata vs. do erro isolado.
   - **Posição normalizada** — `SyntaxError` concentra cedo (agente formatando), `KeyError`/`TypeError`
     concentram tarde (agente manipulando dados): separa erro de forma de erro de conteúdo por posição.

3. **Detecção de erro crítico: 45% de acerto de passo / 24,3% no critério estrito** (passo + módulo + tipo),
   com dependência de **ordem de magnitude** no modelo analista (GPT-4.1 ~32% estrito vs. modelos menores
   ~2% — Tabela 1 e Figura 7b). Ressalva: usar a Tabela 1 — o box "Findings" do paper reporta 50,0/42,5,
   que não bate com a própria tabela nem com a Figura 7b; citar sempre os dois valores (passo e estrito).
   **Sustenta** o princípio já aplicado nos itens 1, 4 e 6: um LLM pedido para localizar o step / classificar
   a causa é **gerador de candidatos, não rotulador** — o backbone tem de ser determinístico (tipo de
   exceção, AST do `code_action`, presença de texto no `model_input_messages`), com juiz LLM só onde o
   determinístico comprovadamente não captura o fenômeno. Ver `03-procedimento-validacao.md` Frente 2.

## Propagação vs. propagação crítica — achado robusto, e como apresentá-lo

Nota registrada 09/09/2026. Separação que evita um mal-entendido na reunião:

- **Propagação existe e está medida.** Coeficiente `1,8×` (`P(erro em k+1 | erro em k)` vs. sem erro —
  `03-procedimento-validacao.md` §1.6, robusto por construção); runs consecutivos (48/354 pares, recorde 10);
  custo ~3× tokens para quem entra em cascata.
- **Propagação crítica — a que descarrila a execução em falha, como na definição de "critical error" do
  AgentDebug — não ocorre neste trace.** `0 de 1.550` trajetórias terminam em erro; 99,3% entregam resposta
  de conteúdo. O agente contorna e entrega. É por isso que o construto "critical error" do AgentDebug não
  transfere (ver [`../literature/agentdebug-2509.25370.md`](../literature/agentdebug-2509.25370.md) §B
  addendum) e a âncora da unidade de memória é **custo + reincidência**, não falha de tarefa.

**É evidência forte e segura de apresentar** — `0/1.550` é contagem crua, sem régua arbitrária. Sustenta o
enquadramento: o mecanismo de memória não vende "prevenir falha catastrófica", vende **cortar o desperdício
de ~3× tokens e o imposto de erro recorrente**.

**Caveats que têm que ir junto** (senão a 1ª pergunta na reunião derruba):

1. **"Recupera" ≠ "acerta"** — o teste checa que a resposta existe e não é recusa, não que está factualmente
   certa. A recuperação pode esconder corrupção silenciosa (groundedness, item 1, não medida).
2. **Amostra de ~1.000 linhas, provável `LIMIT`** (item 3) — "0 falhas" é "0 nesta amostra".
3. **Status do banco não confiável** (`01-racionais.md` §4 Passo 1) — "sem falha" é em parte inferido.
4. **Detector de "degenerada" pega só 2 frases exatas** — os 99,3% provavelmente estão inflados (pedidos de
   esclarecimento contam como sucesso).

**Frase para o slide:** *"Nesta amostra, nenhuma trajetória trava — o agente sempre produz uma resposta. O
erro aparece como custo (~3× tokens) e reincidência, não como abandono da tarefa. O que não verificamos é se
essas respostas recuperadas estão factualmente certas — essa é a pergunta de groundedness, ainda aberta."*

## Fechado nesta sessão

- [x] **Auditoria independente respondida** — 6 discrepâncias (S1–S6) verificadas uma a uma contra o dado
  (não contra o texto do parecer) e corrigidas; S3 mostrou-se pior que o relatado (1 linha errada **+ 2
  famílias omitidas**). O gap de bijeção também foi fechado: o achado central ganhou passo-a-passo próprio
  (`01-racionais.md` §3) e o documento ganhou nota declarando o que cobre. O item que a auditoria não
  conseguiu verificar (`.gitignore` vs. raw CSV) foi verificado — está limpo. Ver
  [`../audit/2026-09-08-auditoria-independente.md`](../audit/2026-09-08-auditoria-independente.md) §6.

- [x] **Gráficos para os 8 achados novos** — 6 construídos (Pareto, assinatura por papel, tokens/chamada,
  ranking duplo, evolução mensal, funil de sucesso verificado), 2 avaliados e deliberadamente não construídos
  (3.2 e 2.3 — poucos pontos / achado principal retirado no teste de robustez). Três bugs achados e corrigidos
  ao conferir visualmente (rótulos sobrepostos, percentual com base errada, legenda truncada).

## Fora da análise do trace em si

- **Promover os fichamentos de 🔎 pra ✅** — [x] **`AgentDebug` promovido a ✅ em 09/09/2026** (leitura dirigida
  em sessão — taxonomia, 5 módulos, Stages 1–3, erro crítico, re-rollout, o que adotar/não adotar). Faltam
  **MAST, TRAIL e ToolScan** — ainda lidos só por subagente.
- **A reunião de apresentação ainda não aconteceu** — toda a sessão até aqui foi preparação.
- **Construir os candidatos de memória de verdade**, reusando este pipeline — ainda não começado. É a fase de
  derivar a **camada 2** (ver nota "Camadas de 'causa'" acima): hoje o "conteúdo proposto" da tabela `CAND`
  (`01-racionais.md` §7) é hipótese à mão por assinatura. "De verdade" = derivar a camada 2 das 7 assinaturas-
  candidato (LLM sobre os casos de cada assinatura **+** validação de amostra com concordância reportada —
  disciplina do Commit Gate, não "roda o LLM e confia") e **não** forçar camada 2 nas assinaturas sem causa
  única. Sequenciar para quando começar a construção, não antes — trace, assinaturas de tool e memória do time
  estão mais frescos nesse momento.
