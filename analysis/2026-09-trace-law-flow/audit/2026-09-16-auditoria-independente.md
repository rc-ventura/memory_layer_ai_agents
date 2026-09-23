# Auditoria independente #2 — parecer sobre a cadeia de evidência

> ⚠️ **Parcialmente desatualizado desde 23/09/2026.** Os números por mês desta auditoria usam o mês de
> `anomesdia` (o lote de corte); hoje o pipeline e os `scripts/audit_recompute*.py` usam o mês de
> `dat_hor_inio_exeo` (quando a execução rodou). Números que não dependem de mês continuam valendo.
> → `docs/04-roadmap.md` (Agora) · `docs/03-procedimento-validacao.md` §1.12

**Data:** 2026-09-16 · **Auditor:** agente de auditoria · **Objeto:** a cadeia completa
`data/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` → `pipeline/analise_trace_esteira_juridica.ipynb`
(estado pós-15/09/2026, com a triagem por mecanismo da §9) → `docs/01-racionais.md` →
gráficos → `docs/02-relatorio-achados.md` → `docs/03-procedimento-validacao.md`. Segunda rodada
independente: a auditoria de [2026-09-08](2026-09-08-auditoria-independente.md) antecedeu a refação de
15/09 (triagem por submecanismo, gráfico da §9.3, regra oficial dos steps não parseáveis, quarta régua
do achado central) — esta audita justamente o que ela não cobria, e reverifica o núcleo.

**Método.** (1) Leitura integral dos 5 documentos e do notebook (65 células). (2) **Recomputação
independente** do trace cru com `csv.DictReader` + `json` + `ast` puros — dois scripts novos
([`scripts/audit_recompute5.py`](scripts/audit_recompute5.py), nível assinatura; e
[`scripts/audit_recompute6.py`](scripts/audit_recompute6.py), nível mecanismo, cuja função de
submecanismo foi reescrita **a partir da especificação em prosa** de `docs/01-racionais.md` §7 Passo 2,
não do código do notebook) + reexecução fresca dos 4 scripts da auditoria anterior
(`audit_recompute*.py`). Saídas: `scripts/audit_out5.txt`, `audit_out6.txt` (git-ignored — podem conter
PII). (3) **Triangulação caso a caso** com `pipeline/drill_down.py` (semântica documentada em
`docs/03-procedimento-validacao.md`). (4) **Verificação externa da literatura** nos artigos reais via
web + PDF (não só fichamentos): MAST v3 em HTML, ToolScan v2 em HTML, AgentDebug e Hu et al. em PDF
(`curl` + `pdftotext`).

**Nota de ambiente:** o trace cru vive em `data/`; `drill_down.py` e os scripts de auditoria o esperam na
raiz do repo (`../../../85cb...` a partir de `pipeline/`). Sem isso as ferramentas não rodam. Criei um
**symlink** na raiz (o nome casa com `*.csv.xz` do `.gitignore` — não vai a git). Nenhum código do
pipeline foi modificado.

---

## 1 · Veredito geral

**Mantém-se o veredito da 1ª auditoria, agora estendido à camada de mecanismo: os números são fidedignos
e reproduzíveis por caminho de código totalmente independente.** O notebook foi revisado na integridade:
65 células (32 de código), `execution_count` 1→32 sequenciais, **zero** células com erro, **13** PNGs
embutidos (12 da §8 + o gráfico de candidatos da §9.3) — coerente com a estrutura documentada.

### 1.1 · Núcleo revertificado hoje (directo do trace cru, 2026-09-16)

| Afirmação | Recomputado | Status |
|---|---|---|
| 1.000 linhas · 840 execs c/ memória · 5.781 ActionSteps · 142.613.752 tokens | idênticos | ✅ exato |
| 498 erros (8,6%) · 313 execs com erro (37,3%) · 13.946.017 tok em erro (9,8%) · 159,2 min latência | idênticos | ✅ |
| Exec. mais cara 5.908.703 tokens | idêntico | ✅ |
| Assinaturas 159/136/39/35/33/22/20/11/8/8/6/6/5 + 1 não classificado | **todas exatas** | ✅ |
| Tabela famílias §2 fecha em 498 com os percentuais publicados | soma=498 ✔ | ✅ |
| **Achado central: 498→430 (86,3%)→76 (17,7%)→51 (11,9%)→58 (13,5% por mecanismo)** | **idênticos, todas as 4 réguas** | ✅ exato |
| 0/1.550 trajetórias terminam em erro · 1.549 chegam a `final_answer` | idênticos | ✅ |
| Mediana 146.306 vs. 47.884 tokens · 7 vs. 5 steps com/sem erro | idênticos | ✅ |
| Propagação 17,7% vs. 9,7% → **1,8×** | idênticos | ✅ |
| Pareto: 1%→16,8% · 5%→41,9% · 10%→54,6% · 20%→69,1% · 50%→89,8% | idênticos | ✅ |
| Taxas por papel: 35%/29%/18%/11%/9%/8%/0,3% | idênticos | ✅ |
| Sucesso por conteúdo: 840 resolvidas (134 por fallback) → 834 (99,3%) → 310 (37,2%) | idênticos | ✅ |
| Medianas mensais (9 meses, incl. jan/mar com n pequeno como documentado) | idênticas | ✅ |
| Reincidência por assinatura: string-não-fechada 125 exec/8 meses · retorno-é-dict 119/7 | idênticos | ✅ |
| Detectores silenciosos: Result-Ignore 103/3.053 (3,4%) · RAC 125 · Tool-Skip 10/840 · IFN zero | idênticos | ✅ |
| Inventário: 90 ferramentas declaradas · 80 chamadas distintas · 821/730 top-2 · 12 positional | idênticos | ✅ |
| **Steps não parseáveis: 224, dos quais 100% com erro, queimando 5.502.380 tokens (3,9%)** | idênticos | ✅ — sustenta a Ressalva 2 do §3.3 |
| Tokens/chamada regra oficial: 141.673 · 50.624 · 27.988 · 18.775 · agregada **22.280** · mediana/exec **12.192** | idênticos (réplica e reimplementação própria) | ✅ |
| Desperdício §3.5: CalculoCivel 25,0% · ConversationAgent 7,5M (9,8%) · managerAgent 3,5M (7,6%) · RespostaBacen 21,3% | idênticos | ✅ |
| Durações §2.3: string-não-fechada 15,3s (n=159) vs. retorno-é-dict 7,7s (n=136) | idênticos | ✅ |
| `classify()` sobrepõe regras: **364/498 (73,1%)** casam >1 regra; combinações 159/98/38/35 | idênticos; ordem específica→genérica faz o trabalho documentado | ✅ |
| grep cru `"Could not index"` no arquivo = **580** (vs. 136 no campo certo) | idêntico | ✅ — a "armadilha" do §1.4 existe como descrita |

### 1.2 · Camada de mecanismo (triagem de candidatos — o que a 1ª auditoria não cobria)

Reimplementei `submecanismo()` do zero a partir da prosa do racional e comparei **erro a erro** com
`pipeline/resultados/erros_mecanismo.csv`:

| Afirmação (relatório §6 / racionais §7) | Recomputado | Status |
|---|---|---|
| 498 erros → **437 ocorrências** (cascata × unidade) · 88 seguidores · 410 cascatas | idênticos | ✅ exato |
| **Zero divergência** entre minha classificação (da prosa) e o CSV: 498/498 | 0 diffs | ✅ — a prosa do §7 Passo 2 descreve fielmente a regra |
| 14 unidades × 6 colunas (ocorrências, erros, execuções, meses, papéis, tokens) | **as 14 linhas batem campo a campo** | ✅ exato |
| Cobertura das 10 candidatas: 447/498 erros (89,8%→90%) · 91,9%→92% dos tokens | idênticos | ✅ |
| Limítrofe: só nº 9 sai com ≥5 execs/≥3 meses | 5 ocorrências, 4 execs, 3 meses — confere | ✅ |
| Ressalva "Explicação solta": 26/33 erros e **92% dos tokens** em dez/2025; 7 das 12 ocorrências logo após erro de protocolo; ocorrências próprias abr–jun = {abr:1, mai:1, jun:2} = 4 | idênticos | ✅ |
| §2.2 por mecanismo: CadastroTrabalhista 94% (17/18) · CalculoCivel 76% (13/17) · managerAgent 62% (112/180) · ConversationAgent 43%+29% · RespostaBacen 33%/33%/29% | idênticos — e o corte `role_vol` ∈ {3,5,10,15} **não muda** dominante nem % | ✅ robusto (confirma a leitura honesta do Passo 6) |
| Escopo por papel: nº 2 só no ConversationAgent (96/96); nº 6 = 17/18 do CadastroTrabalhista; nº 3 = 13/17 do CalculoCivel; nºs 10+3 = 16/24 do RespostaBacen | idênticos | ✅ sustenta a tese `(papel, unidade)` |
| Reincidência entre execuções por mecanismo: nº 1 em 149 execs/9 meses · nº 2 em 87/6 · nº 3 em 36/7 | idênticos | ✅ |
| Cascata recorde: 10 erros seguidos (`2a407143…`/managerAgent, dez/2025) | 10 consecutivas reais (11 erros em 13 steps) | ✅ |

## 2 · Gráficos: proveniência e correção (item 4 do plano)

Os **13 gráficos** têm fonte identificável; auditei as células de agregação e os valores plotados:

- **8.1–8.8, 8.10–8.12:** contam sobre tabelas revertificadas acima (assinaturas, funil 86,3/11,9,
  mediana 146k/48k, mecanismo × mês, payoff, taxas por papel, Lorenz 16,8/41,9/54,6, papel × mecanismo,
  ranking duplo, medianas mensais, funil de sucesso 840→834→310/524). **Todas as fontes revertificam.**
- **8.9 (tokens/chamada):** a linha vertical agora usa `mediana_por_exec` (12.192) rotulada "mediana por
  execução" e a regra laranja é `> 2× mediana` — **a correção S1 da 1ª auditoria está efetivamente no
  código**; o markdown da célula declara a distinção mediana × razão agregada e a ressalva sobre `null`/
  `ontestacaoCivel`. ✅
- **8.2 (funil central):** o gráfico usa as variáveis `checked/reached/repeated/same_sig(+same_mec)` da
  célula de agregação, revertificadas valor a valor (498/430/76/51/58). ✅
- **9.3 (candidatos):** o gráfico nasce diretamente do DataFrame `T` da triagem — o **mesmo** objeto
  exportado para `candidatos_memoria.csv`, que revertifiquei linha a linha contra o trace cru. Valores
  das barras (tokens) e rótulos (tokens · ocorrências) conferem com as minhas contagens; agrupamento por
  decisão, ordenação por tokens, cores por tipo e marca "limítrofe" correspondem aos dados. ✅

**Nenhuma figura órfã.** Assimetria gráfica×texto anterior (S1/S2/S3/S6 da 1ª auditoria) verificada como
corrigida no estado atual.

## 3 · Triangulação com casos no trace cru (`drill_down.py`)

Rodei os 4 casos citados pelos documentos; **todos existem e a narrativa bate verbatim**:

| Caso | O que os docs afirmam | O que o trace mostra |
|---|---|---|
| `2a407143…` / managerAgent | 10 erros seguidos; thoughts citados palavra a palavra ("Ocorreu um erro porque a resposta anterior não estava dentro de um bloco `<code>`…", "O erro foi causado por um texto explicativo dentro do bloco `<code>`…") | **Exato** — 13 steps, erros 2–12 (10 "Sintaxe inválida" consecutivos após o de protocolo), thoughts verbatim. O agente diagnostica a falha corretamente e repete — a prova textual do achado central |
| `42891135…` / CalculoCivel | ferramenta devolve string JSON; step 3 indexa quebra; step 4 autocorrige com `isinstance(str)+json.loads` | **Exato**, incluindo o texto da exceção `string indices must be integers` |
| `1be966e7…` / RespostaBacen | `validar_quebra_sigilo` devolve `vazamento_sigilo`; agente pede `quebra_sigilo`; step seguinte escreve o mapeamento | **Exato**, observação e correção no trace |
| `cd794f02…` / ConversationAgent e `95344639…` / RespostaBacen | os 2 padrões de divergência entre a régua por mensagem e a régua por mecanismo (§3 Passo 8: 9 + 2 pares) | **Exato**: `cd794f02` = duas mensagens, mesma confusão de formato (`docs[0][0]` no step 2 → itera um único documento como lista no step 3); `95344639` = mesma mensagem ("Could not index"), duas lições diferentes (campo inexistente × texto de erro indexado) |

Os comandos `mecanismo` e `listar` do `drill_down.py` funcionam como documentados
(`mecanismo "Retorno pode chegar como string"` devolve 47 erros / 36 execs — consistente).

## 4 · Literatura — verificada nos artigos reais, não só nos fichamentos

Os **seis papers citados existem, têm os metadados corretos e sustentam o uso que o relatório faz**:

| Paper | Estado | O que confirmei na fonte real |
|---|---|---|
| **MAST** — arXiv:2503.13657 (Berkeley, NeurIPS 2025 D&B) | ✅ | 14 modos/3 categorias; κ=0,88 (humanos) e 0,77 (juiz). A citação-chave do escopo **existe verbatim na v3** ("We acknowledge that some MAS failures can stem from fundamental limitations of current LLMs… we do not claim MAST is exhaustive") — a afirmação "exceção de código está fora do escopo, deliberadamente" é leitura correta do conjunto taxonomia+declaração. ⚠️ Menor: na **v2** em HTML essa frase não aparece — o fichamento cita v3 corretamente; sempre citar a versão (como o próprio fichamento manda). |
| **TRAIL** — arXiv:2505.08638 (Patronus AI) | ✅ | 148 traces · 841 erros · 1.987 spans (575 com erro = 28,9%) · melhor modelo 11% (Gemini 2.5 Pro) — tudo confere com o paper e a página oficial do dataset. O "35,5% Instruction Non-compliance no split SWE-Bench" é consistente com a frequência 91/256 derivada da Fig. 3a. |
| **AgentDebug** — arXiv:2509.25370 | ✅ | Citações verbatim conferidas no PDF: "focusing on root-cause errors, rather than attempting to fix every surface-level mistake…" (ablação), "Error propagation is the primary bottleneck in LLM agent reliability. Early mistakes rarely remain confined; instead, they cascade…" (Key Insight), "the critical error is defined as the earliest step whose correction directly prevents the final failure" (§C), e os campos `root_cause`/`correction_guidance` ("Actionable advice for the agent to avoid the same mistake"). Os números 45,0% passo / 24,3% estrito batem com a **Tabela 1** — e a ressalva do roadmap está certa: o texto de Findings do paper diz 50,0/42,5, que não bate com a própria tabela. Taxonomia de 17 tipos / 5 módulos confirmada (repo oficial). A correção de 14/09 ("AgentDebug não propõe tipos de memória nem roteamento módulo→tipo") está correta — não há nada disso no paper. |
| **ToolScan/SpecTool** — arXiv:2411.13547 (Salesforce, ICLR 2025 WS) | ✅ | Os 7 tipos reais são **IAC, IAV, IAN, IAT, RAC, IFN, IFE** (contraste com a taxonomia inventada que a v1 citou — a condenação da v1 é justa). v1 do arXiv se chama **SpecTool** — confirmado pelo próprio HTML v1. O verbatim de §8.1.2 ("model success rate is higher when model is provided with feedback…") existe. Nota: a contagem "1 caso de IAN, zero de IAV" é um achado *do projeto* sobre o trace — plausível, mas não o reversei caso a caso nesta rodada (verifiquei, por amostra, que as mensagens `'does not support multiple positional'` são de fato ValueError emitido pelo harness). |
| **Memory in the Age of AI Agents** — Hu, Liu et al., arXiv:2512.13564 | ✅ | Régua de tipos do §6/§7 confirmada verbatim no PDF: "What does the agent know?" (factual), "How does the agent improve?" (experiential), §4.1.2 ("entities and states external to the user, encompassing long documents, codebases, tools, and interaction traces") e §4.2.2 *Insights* ("distilling discrete pieces of knowledge, such as granular decision rules and reflective heuristics, from past trajectories"). O mapeamento das 10 candidatas em factual·ambiente × experiencial·estratégia é uso **coerente** da taxonomia. |
| **ToolFailBench** — arXiv:2607.04686 (Soni, UC Berkeley, ICML 2026 Workshop) | ✅ | Existe, autor único, workshop; domínios incluem **direito** e os 4 modos (Tool-Skip, Result-Ignore, Output-Fabrication, Unnecessary-Tool-Use) — a ressalva "o snippet da v1 trazia só 3" é precisa. |

**Erro conceitual ativo encontrado: nenhum.** As três "refutações" do §7 (mapeamento MAST estruturalmente
inválido por mudança de denominador trace×step; classe de retorno-manipulação ausente no ToolScan;
taxonomia inventada do sumarizador) são conclusões corretas e, no caso dos dois primeiros papers,
suportadas pelas fontes primárias verificadas hoje.

## 5 · Discrepâncias encontradas nesta rodada (ordenadas por severidade)

**Nenhuma afeta os números da tese.** São de higiene/precisão documental:

- **M1 — Existem duas pastas `resultados/` divergentes.** A viva é `pipeline/resultados/` (data
  15/09, esquema das 14 unidades). A raiz `analysis/2026-09-trace-law-flow/resultados/` é uma cópia
  **obsoleta de 08/09** (esquema antigo de 7 candidatos; **não contém** `erros_mecanismo.csv` nem
  `triagem_assinaturas.csv`; 4 de 5 arquivos comuns diferem em conteúdo). Pior: o
  `audit_recompute4.py` lê a cópia obsoleta na sua seção "CSV derivados" — rodado hoje, imprime
  contagens da versão antiga sem nenhum aviso. **Ação:** apagar/git-ignore a cópia da raiz (ou
  substituir por symlink para `pipeline/resultados/`) e ajustar o script ou o README para não restar
  ambiguidade sobre onde o notebook escreve.
- **M2 — Caminho do trace.** `drill_down.py` e os scripts de auditoria esperam o `.csv.xz` na raiz do
  repo; o arquivo vive em `data/`. O docstring do `drill_down.py` diz "na raiz do repo", o README da
  análise aponta para `data/` — hoje a ferramenta só funciona com trabalho manual (resolvi com
  symlink). **Ação:** padronizar o caminho (ideal: `../data/` relativo a partir de `pipeline/`) e
  atualizar o docstring.
- **M3 — Precisão de atribuição no §5 do relatório.** "O TRAIL classifica seus 841 erros por
  visibilidade a exceção de runtime: ≥59%…" — os 841 e as categorias são do TRAIL, mas **o bucketing
  por visibilidade é julgamento do analista aplicado sobre as frequências da Fig. 3a** (A=497→59,1%;
  B=316; C=28→3,3%) — não é uma medida publicada pelo paper. O `03-procedimento-validacao.md` deixa
  a proveniência mais clara ("número do dataset do TRAIL, não do nosso trace"), mas o §5 do relatório,
  isolado, lê como se o TRAIL tivesse feito essa classificação. **Ação:** reescrever a frase como
  "classificando as categorias do TRAIL por visibilidade a exceção (mapeamento nosso):
  ≥59% dos 841 erros do dataset deles caem em tipos que nossa regex não pegaria".
- **M4 — Splits do TRAIL no fichamento.** `literature/trail-2505.08638.md` diz `gaia` (117) /
  `swe_bench` (31); a página oficial do dataset diz **118 GAIA / 30 SWE-Bench**. Diferença de 1 trace
  por split; o fichamento não conseguiu acessar o dataset gated — **Ação:** confirmar contra o dataset
  com autenticação e corrigir uma linha do fichamento (não afeta nenhum número do relatório).
- **M5 — Ressacas documentais de 14/15-09:** (a) `literature/README.md` ainda apresenta o AgentDebug
  como fonte do "roteador módulo→tipo de memória" — a própria correção registrada em
  `01-racionais.md` §1 e em `02-relatorio-achados.md` §8 diz que isso **não existe no paper** e que a
  régua de tipos é Hu et al.; (b) a Frente 2 do `03-procedimento-validacao.md` (linha "A tabela
  'módulo → tipo de memória' é inferência minha…") e o item do checklist ("…formei opinião sobre o
  mapeamento módulo → memória") ficaram desatualizados pela mesma correção. **Ação:** trocar por
  "conferir a taxonomia do AgentDebug" e a checklist idem.
- **M6 — Menor:** `01-racionais.md` §5 (Ressalva 2) arredonda 5.502.380 → "5,50M (3,9%)" — correto
  contra o total (3,86%); e NB: o número "224" da tabela Δ-oficial soma certinho por papel
  (141+72+5+1+3+1+1=224). Nada a corrigir; registrado como conferido.

## 6 · Estado das correções da 1ª auditoria (S1–S6)

Todas estão **efetivamente aplicadas e revertificáveis**: S1 (linha mediana do 8.9) está no código;
S3 (§2.3 refeita com 7 famílias: 15,6/15,6/15,3/7,7/7,6/7,5/3,2s) bate com minha recomputação;
o §3 novo dos racionais existe e o passo-a-passo dele reproduz os 4 números (86,3/17,7/11,9/13,5);
a nota N1 (dois scripts, duas réguas) está coerente com o que reproduzi hoje: regra inclusiva
22.280/12.192 e regra estrita (descarta steps sem parse no agregado por papel) 21.420 aparecem lado a
lado no `audit_recompute4.py` atualizado.

## 7 · Ressalvas que viajam com qualquer apresentação (independente desta auditoria)

As limitações continuam sendo as que os próprios documentos declaram, e estão corretas — dois pontos que
o auditor dá de graça se não estiverem na lâmina:

1. **"Recupera" ≠ "acerta"** — o detector de degenerada pega só as 2 frases exatas do system prompt;
   99,3% provavelmente inflado; groundedness factual permanece **não medida** (verificável como o maior
   risco material da esteira).
2. **Amostra = 1.000 linhas (provável LIMIT)** — "0 falhas em 1.550 trajetórias" é "0 nesta amostra";
   a confirmação com o time da esteira (status 1/2/3/34; sem LIMIT) segue o item estrutural mais urgente.
3. O ponto cego ≥59% **é estimativa por mapeamento** sobre o dataset do TRAIL, não medida direta neste
   trace (ver M3).

## 8 · Veredito

**A cadeia de evidência se sustenta.** Trace → notebook → CSVs derivados → documentos → gráficos: todos
os elos conferem, inclusive a camada mais nova (mecanismo/triagem §7–§9), que agora reproduz **sem olhar
o código** — a prosa do racional é suficiente para reimplementar o classificador com zero divergência,
que é exatamente a propriedade que o `03-procedimento-validacao.md` defende. O achado central
(86,3% leem / 11,9–13,5% reincidem) está entre os mais robustos que já vi recomputados: quatro réguas
independentes convergem e o caso-vitrine existe palavra por palavra no trace. A fundamentação na
literatura passou no teste mais estrito (citações verbatim conferidas nos PDFs originais hoje), e a
correção "AgentDebug não é régua de tipos de memória, Hu et al. é" está conceitualmente certa.

Pendências desta auditoria, nenhuma bloqueante: **M1 (pastas `resultados/` duplicadas)** é a única que
eu resolveria antes de apresentar o material a terceiros, porque é a armadilha concreta de reuso
(scripts antigos leem a versão antiga em silêncio); M2–M5 são ajustes de apontamento.

---

*Auditoria executada segundo o próprio padrão do `docs/03-procedimento-validacao.md` §1.4: recomputo por
caminho de código independente, direto no trace cru (~5 passes sobre os dados), triangulação de número
agregado contra caso concreto, e conferência das fontes primárias — desta vez incluindo a web.*
