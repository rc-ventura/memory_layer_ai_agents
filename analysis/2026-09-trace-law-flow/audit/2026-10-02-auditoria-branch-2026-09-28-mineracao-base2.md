# Auditoria independente — branch `2026-09-28-mineracao-base2` (PR #29, aberto)

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

> **Fechada em 02/10/2026 — ver a [Parte II](#parte-ii--revisão-do-autor-e-fechamento-02102026).** A Parte I é o
> parecer do auditor, mantido como foi entregue (o PR #29 foi mergeado depois dele). A Parte II é a resposta do autor:
> confere a auditoria, fecha as ressalvas, cobre a lacuna de método que ela deixou e registra o que ainda depende da
> máquina 2. Índice de todas as auditorias: [`README.md`](README.md).

# Parte I — Parecer do auditor

**Data:** 2026-10-02 · **Auditor:** agente de auditoria (Devin) · **Objeto:** os 43 commits da branch
`2026-09-28-mineracao-base2` (tip `d98a2ca`), sobre a base da branch anterior `2026-09-25-residuo-base2`.
**Método:** leitura integral do diff (29 arquivos, +5.004/−591) e dos documentos novos; **recomputação
independente na base 1** num worktree destacado (`/tmp/audit-0928`, dados linkados do diretório `data/` da cópia
local, git-ignored): pipeline rodado do zero com o código da branch, auditoria nº 6 (`audit_recompute6.py`) e
`drill_down.py protocolo`/`silenciosas`/`ferramenta` executados na íntegra.

## Veredito

**Os números publicados da base 1 reproduzem exatamente** — todas as contagens conferidas batem na casa da unidade.
A documentação é honesta sobre a epistemologia: distingue "conferido" (determinístico) de "assistido" (leitura por
LLM) e "conferido" de "esperado" na base 2, registra leituras retiradas e reverts com data e motivo. A qualidade da
evidência é compatível com a regra declarada ("nenhum número agregado sem apontar o caso concreto").

**Limites desta auditoria:** a base 2 roda na máquina de compliance e não é verificável aqui — todos os números da
base 2 (o incidente do `gpt-5.6-terra`, 134 falhas silenciosas, 86/86 gesto colado, a cadeia do erro crítico) foram
auditados como **coerência interna e reprodutibilidade do procedimento** (docs 12 e 15), não como recomputação. O
que a base 2 afirma precisa ser re-verificado quando o notebook `falhas_silenciosas.ipynb` rodar lá (o próprio doc
14 §8 lista isso como pendente).

## 1. Números recomputados na base 1 — tabela de conferência

Executado: `carregar_base()` + `triagem()` + `triagem_por_papel()` + `falhas_silenciosas()` +
`erro_depois_da_falha`/`contrato_precedido`/`sucesso_falso_candidato`/`formas_das_falhas` (as mesmas funções que o
notebook e o `drill_down.py` chamam), `audit_recompute6.py` (reimplementação independente a partir da prosa dos
racionais) e `drill_down.py` na íntegra.

| Afirmação (fonte) | Publicado | Recomputado | Status |
|---|---|---|---|
| Erros / execuções / steps (01, 02, 09) | 498 / 313 / 5.781 | 498 / 313 / 5.781 | ✅ |
| Execuções do trace · com memória | 1.000 · 840 | 1.000 · 840 | ✅ |
| Tokens totais | 142,6M | 142,61M | ✅ |
| Unidades: 10 candidatas + 1 sinal + 2 não-memória + 2 revisar (01 §7, 02, 09, schema) | — | idêntico | ✅ |
| Cobertura das candidatas | 440/498 = 88% · 91% dos tokens | 440/498 = 88,4% · 91,1% | ✅ |
| Sinal de harness = nº10 `U_campo_inexistente` | 10 erros · 10 execs · 6 meses | idêntico (única com esse destino) | ✅ |
| Limítrofe na régua estrita | só `U_estado_perdido` | só `U_estado_perdido` | ✅ |
| Por papel (9.4/9.5): células / candidatas / herdadas / reveladas / caem na estrita | 31 · 18 · 13 · 0 · 8 de 18 | 31 · 18 · 13 · 0 · 8 de 18 | ✅ |
| Distribuição scoped por papel | Conversation 9, manager 3, Roteador 2, +1 × 4 | idêntico | ✅ |
| Resíduo base 1 | 7 causa + 1 sintoma; alarme não dispara (0,2%) | idêntico | ✅ |
| `audit_recompute6.py` | 0 divergências; 437 ocorrências; 15 unidades | **0 divergências; 437; 15 OK** | ✅ (ver §3.A) |
| Protocolo base 1: erros e calendário | 33 erros; out 24, nov 1, dez 7, fev 1; 0 desde mar | idêntico (`drill_down protocolo` [1]) | ✅ |
| Por papel | manager 21, RespostaBacen 7, Conversation 3, CalculoCivel 2 | idêntico ([2]) | ✅ |
| Forma | 31 texto sem marcador, 2 em ```` ``` ````, mediana 2.859 car. | idêntico ([4]) | ✅ |
| Recuperação | 33/33 | 33/33 ([5]) | ✅ |
| Cascata | 7 `U_texto_solto` | 7 `U_texto_solto` + **1 `U_estado_perdido`** | ⚠️ omissão menor (§3.B) |
| Modos (10 §2, 11 §1.2): JSON 4.590 steps 0 erros; texto out/2025 | `a34f495f` 2.195/0 + `febfeb55` 2.395/0; `82de8f07` 130/21; `2f96aa69` 83/3; `b0f37eea` 193/9 | idêntico ([7]) | ✅ |
| Modelos base 1 | manager gpt-4.1 12 + não registrado 9; RespostaBacen `o4-mini` 7 em 116 steps (60/1k) | idêntico ([8]) | ✅ |
| Contrato `resposta_final` (M2) | `resposta_gerada`: 88 steps/20 execs jan–jun/2026, 0 erros · `json_resposta`: 47/6, só dez/2025 | idêntico (`ferramenta resposta_final`); os 7 erros de dez estão todos no papel/versão | ✅ |
| Falhas silenciosas base 1 | 9 com exceção · 120 silenciosas (93%) · 90 execs · 10 meses · 13 papéis · 22 ferramentas · 119 steps | idêntico | ✅ |
| Sobreposição visível × invisível (13 §2, notebook §13.1) | 0 | 0 | ✅ |
| Grupos do motivo | 43 sem_resultado · 41 argumento · 19 plataforma · 6 json_invalido · 2 fora · 9 não reconhecido = 120 · reais 75 | idêntico | ✅ |
| [2] rastro no visível | "(nenhum erro)" 107; `U_tipo_retorno` 4; `H_bloco_code` 2; outros 7 | idêntico | ✅ |
| [3] contrato precedido | `U_tipo_retorno` 4/47 · `U_contrato_dict` 1/96 · `U_campo_inexistente` 0/10 | idêntico | ✅ |
| [4] sucesso falso candidato | 53/75 total · plataforma 16/19 · argumento 30/41 · json 0/6 · não-rec 7/9 | idêntico | ✅ |
| `busca_obf`, forma do argumento | 6/6 `str(dict colado)`; gesto colado +4 argumento +1 plataforma +1 não-rec; `json.dumps` 2 em plataforma | idêntico (6/6; colado: 4/1/1; dumps: 2) | ✅ |
| Detectores §13.7 (= antigo §7 da esteira) | inventário 90 · Result-Ignore 103/3.053 · RAC 125 · mismatch 45 (retirado) · Tool-Skip 10/840 · 80×90 | idêntico nos outputs embutidos; inventário 90 reconfirmado pelo audit6 (F) | ✅ |
| Por-ferramenta base 1 (doc 14 §2) | `get_available_documents` 667/57/9% etc. | idêntico (`silenciosas` [1]) | ✅ |
| Classes de erro | `AgentExecutionError` 465 · `AgentParsingError` 33 | idêntico | ✅ |
| Erros de interpretador/limite na base 1 | zero (CSVs inalterados, só colunas novas) | zero (nenhuma unidade nova aparece) | ✅ |
| `criticos.csv` na base 1 | 0 linhas | 0 | ✅ |

## 2. Coerência código ↔ documentação

- **`base_pipeline.py`**: `BASE_ID`/`DESTINO_MINERACAO` (Ajuste 7) implementa exatamente o declarado — o destino da
  mineração só vale na base onde foi tomado; reconfirmado: com `base1`, `U_campo_inexistente` = `sinal de harness` e
  `U_contrato_dict` = `memória`. O roteamento do tempo do interpretador (Ajustes 8/9) — ferramenta declarada →
  `timeout_interpretador`/`H_timeout_ferramenta`; `final_answer` sem laço → `U_resultado_bruto`; senão
  `U_codigo_lento` — e a família `Erro crítico`/`C_limite_passos` (Ajuste 10) correspondem à prosa do ledger e de
  `01` §7 Passo 2.
- **Os reverts estão honestamente registrados**: Ajuste 6 (composição entre bases) revertido com justificativa de
  overengineering; a primeira versão do Ajuste 9 (7340154 → 6b15f37) revertida no mesmo dia com nota de processo;
  leituras retiradas marcadas ("Leitura retirada", §2.3/§2.5 do doc 11; "Correção registrada" no ledger para o
  commit 4f6ecaa). É a prática correta de controle de versões metodológico.
- **Divisão conferido/assistido**: o doc 11 §2.5 marca cada afirmação do caso CalculoCivel como [conferido] (AST,
  regex reproduzida, contagem) ou [assistido] (leitura de LLM na máquina 2, hipótese) — alinhado à regra "nenhum
  LLM no caminho da classificação" (plano-atual §1).
- **Integridade do funil** (doc 13 §2): recomputado — 0 steps nos dois baldes; a soma dos grupos = total.
- **Docs mutuamente consistentes**: os números da §1.16/§1.15 do doc 03, do `09`, do `schema-e-taxonomia.md` e do
  README foram atualizados juntos para o estado pós-Ajuste 5 (10 candidatas/440/88%/91%); as ocorrências restantes
  de "11 candidatas" são todas em contexto datado/histórico correto (ledger, banner da auditoria de 16/09, relato
  mensal congelado em 25/09).
- **README**: índice de docs atualizado (10–15) e a entrada do notebook novo; consistente.

## 3. Ressalvas e itens de atenção (nenhum invalida as conclusões)

**A. Checagem E do `audit_recompute6.py` diverge — conhecida e declarada.** Imprime esperado 26/33 vs. atual
1/33 em dez/2025 (a troca do relógio em 23/09 tornou a expectativa obsoleta: dez/2025 era mês de *lote*; por mês de
execução são 25/33 em out/2025). Está registrada como pendente (roadmap item 36; doc 03 §1.16; ledger Etapa 7).
As checagens A/B/C/D/F/G dão 0 divergências. **Recomendação:** atualizar a expectativa do E — uma auditoria que
imprime divergência crônica condiciona o leitor a ignorar divergências futuras.

**B. Omissão menor na cascata do protocolo (base 1).** Doc 11 §1.1 e o ledger dizem "logo depois, 7
`U_texto_solto`"; o [6] mostra também **1 `U_estado_perdido`** (25 steps sem erro + 7 + 1). Os 7 conferem; o 1 não
está mencionado. Sem impacto na decisão; convém uma linha de correção no próximo passe.

**C. Granularidade ambígua num label do `drill_down.py silenciosas`.** O cabeçalho imprime "steps com a ferramenta
(chamada ou falha): 3.573" — que são **pares step×ferramenta** (`len(F)`); o notebook §13.1 imprime 3.373 **steps
distintos**. Mesmo fato, granularidades diferentes, label igual ("steps"): 200 steps chamam >1 ferramenta.
Cosmético; vale renomear o label para "chamadas".

**D. A medida de sobreposição do M1 não é reproduzível pelo repo.** "managerAgent 15/21, mediana 97%" foi feita
avulsa em 30/09 e não vive no código — o doc 10 §7 declara isso como limite, então é honesto, mas para a base ser
reauditável vale transformar em função (`base_pipeline.py` ou `drill_down.py`) numa próxima etapa.

**E. Base 2 = inteiramente fora do alcance desta máquina.** As contagens reportadas (69 erros de protocolo, 61 em
ago; terra 54/478 vs gpt-4.1 0/381; 134 silenciosas; 86/86 gesto colado; custo do crítico ~2,09M tokens) vieram de
fotos e leituras do Rafael na máquina de compliance — a documentação o declara consistentemente ("conferido
rodando" vs. "esperado"). Os Ajustes 4, 9 e 10 têm efeito na base 2 marcado como **"esperado"** (não conferido) no
ledger — importante: a contagem final da base 2 pode divergir discretamente quando os notebooks rodarem lá, e os
docs já preveem isso.

**F. Cabeçalho do livro-razão desatualizado.** `pipeline-entre-bases.md` linha 3 ainda diz "atualizado 29/09" embora
o arquivo tenha recebido as Etapas 10b/10c e o registro S2 de 01–02/10. Cosmético.

**G. Relatório mensal congelado em 25/09.** `relatorio-mensal-2026-09.md` diz "11 unidades candidatas ~90%/92%" —
coerente com a data de emissão (25/09, antes do Ajuste 5 de 28/09) e declarado como "o que foi submetido no
formulário". Correto como registro histórico; se o arquivo for reaproveitado como fonte de números atuais, precisa
de nota de data.

**H. Higiene do ambiente, não do conteúdo.** Existe um worktree abandonado apontando para a branch
(`wt-mineracao`, já listado em `plano-atual.md` §5 como pendente) e o PR #29 permanece aberto — o que está
consistente com o plano.

## 4. O que foi auditado, arquivo a arquivo

| Arquivo | Mudança | Veredito |
|---|---|---|
| `pipeline/base_pipeline.py` (+405) | Ajustes 5–10 + balde invisível | ✅ regras conferem com docs; reproduzem números |
| `pipeline/drill_down.py` (+554) | `protocolo`, `critico`, `tempo`, `silenciosas`, `--forma`, `--motivos` | ✅ saídas reexecutadas batem com docs |
| `pipeline/metadados_steps.py` (+140) | metadados de steps p/ M4/M5 | ✅ código coerente com o procedimento 12 passo 5; números são da base 2 |
| `pipeline/falhas_silenciosas.ipynb` (+1.586) | notebook do balde invisível §13.x | ✅ outputs embutidos = recompute; funil/§13.7 conferidos |
| `analise_trace_esteira_juridica.ipynb` (−798 líquido) | §7 migrou; 9.2–9.5 com sinal de harness | ✅ output embutido = recomputado (10 candidatas, 440/498…) |
| `paleta.py`, `genealogia_sankey.py` | família Erro crítico (preto), SINAL-HARNESS | ✅ regra "só acrescenta cor" respeitada |
| `docs/10–12`, `13–15` | conjuntos novos (protocolo, silenciosas) | ✅ internamente consistentes; números base 1 verificados |
| `docs/01/02/03/04/09`, `README`, `schema` | atualizações de Ajustes | ✅ alinhadas; números rebatidos |
| `pipeline-entre-bases.md` (+593) | ledger Ajustes 5–10, Etapas 5b/10b/10c | ✅ registro completo gatilho→evidência→mudança→verificação |
| `plano-atual.md` (+219) | plano vivo | ✅ marcos "feito" confirmados |
| `relatorio-mensal-2026-09.md` | relatório institucional | ✅ congelado em 25/09; coerente para a data (ver §3.G) |
| `discussion/*` (+9) | sinal de harness na hipótese/arquitetura e método genérico | ✅ coerente com Ajuste 5 |
| `audit_recompute6.py`, banner de 16/09 | auditoria atualizada | ✅ E fora de fase conhecido (§3.A) |

## 5. Conclusão

Do ponto de vista de auditoria, **os resultados da branch são confiáveis para tomada de decisão**, com duas
reservas explícitas que o próprio trabalho declara: (1) os números da base 2 são de segunda mão por construção
(máquina de compliance) e dependem da conferência final quando os notebooks rodarem lá — em particular, o efeito
"esperado" dos Ajustes 4/9/10 e o run de `falhas_silenciosas.ipynb` na base 2; (2) a medida M1 de sobreposição
(mediana 97%) deveria ser promovida a função versionada. Recomendações de menor risco: atualizar a expectativa E do
`audit_recompute6`, a linha de cascata do doc 11 (o `U_estado_perdido`), o label "steps" do `silenciosas` e o
cabeçalho do ledger.

---

# Parte II — Revisão do autor e fechamento (02/10/2026)

**Quem:** o autor do trabalho auditado (Rafael, com o Claude Code), na branch `2026-10-02-consolidacao-unidades`.
**Objeto:** a Parte I inteira — cada ressalva (A–H), a tabela de conferência (§1) e o método da própria auditoria.
**Método:** rodar de novo, na base 1, tudo o que a auditoria afirma; escrever uma **implementação independente** do
que ela só tinha reexecutado; e, para cada coisa que mudou, registrar **contexto → solução → por que precisamos dela →
evidência → verificação**. Os comandos estão em cada item, para qualquer pessoa repetir.

**Veredito em uma frase.** A auditoria **faz sentido e está correta** em tudo o que afirma. Todas as ressalvas
reproduzem. A lacuna era de método: no balde invisível ela **reexecutou** as funções do pipeline em vez de
**verificá-las**. Cobrir essa lacuna confirmou todos os números (0 divergências) e achou **um defeito de definição**, no
[4], corrigido como **Ajuste 11** (base 1: 53/75 → 54/75). Achou também uma anotação errada numa regra de motivo e uma
pré-condição que faltava na consolidação (4.2b). **Nenhuma conclusão nem destino de unidade muda.**

## II.1 · A auditoria faz sentido? Conferindo a conferência

Antes de agir sobre uma auditoria, é preciso saber se ela está certa. Cada ressalva foi reproduzida rodando o código
na base 1:

| Ressalva | O que a auditoria diz | Reproduzi? | Evidência (base 1) | Destino |
|---|---|---|---|---|
| **A** | checagem E do `audit_recompute6` espera o mês do lote | ✅ | com a expectativa antiga, divergia; pelo mês da execução, 25/33 em out/2025, 90% dos tokens | corrigida (II.5) |
| **B** | a cascata do protocolo omite 1 `U_estado_perdido` | ✅ | `drill_down.py protocolo` [6]: 25 sem erro · 7 `U_texto_solto` · **1 `U_estado_perdido`** | corrigida (II.5) |
| **C** | o rótulo "steps" do `silenciosas` conta pares | ✅ | 3.573 linhas de `falhas_silenciosas()` = pares step × ferramenta; 3.373 steps distintos | corrigida (II.5) |
| **D** | a sobreposição do M1 não é reproduzível pelo repo | ✅ | não havia função; reconstruída e versionada | **função nova** (II.4) |
| **E** | a base 2 está fora do alcance | ✅ | correto por construção (máquina de compliance) | **roteiro** para a máquina 2 (II.6) |
| **F** | cabeçalho do livro-razão "atualizado 29/09" | ✅ | linha 3 do `pipeline-entre-bases.md` | corrigida |
| **G** | o relatório mensal está congelado em 25/09 | ✅ | correto como registro histórico | nenhuma ação (é o que foi submetido) |
| **H** | worktree abandonado e PR aberto | ✅, e havia mais um | o `wt-mineracao` já tinha sido removido e o PR #29 mergeado; o worktree **da própria auditoria** (`/tmp/audit-0928`, detached `d98a2ca`) continuava registrado | removido (o trace lá era cópia idêntica: mesmo SHA-256) |

**Conclusão do II.1:** nenhuma afirmação da auditoria precisou ser retirada. Ela é confiável como está, e por isso
as recomendações foram seguidas, não reinterpretadas.

## II.2 · A lacuna de método: reexecutar não é verificar

**Contexto.** A tabela da Parte I §1 tem duas espécies de linha:

- as do balde visível (unidades, cascatas, cobertura, triagem): conferidas pelo `audit_recompute6.py`, que
  **reimplementa** a classificação a partir da prosa do `01-racionais.md` e compara erro a erro com o CSV. Isso é
  verificação independente;
- as do **balde invisível** (funil 9/120, grupos do motivo, [2], [3], [4], forma do `busca_obf`): a própria auditoria
  diz que foram conferidas com "as mesmas funções que o notebook e o `drill_down.py` chamam". Isso é
  **reprodutibilidade**: prova que o código dá sempre o mesmo número, não que o número esteja certo. Um erro de
  definição dentro de `falhas_silenciosas()` se reproduziria perfeitamente.

**Por que isso importa aqui.** O balde invisível sustenta quatro decisões já tomadas:

1. `U_tipo_retorno` e `U_campo_inexistente` **continuam memória candidata**, porque o [3] mostra que só 0–9% delas
   vêm depois de uma falha silenciosa;
2. o dono do `json_invalido` é **o agente** (a forma: 6/6 e 86/86 gesto colado);
3. o **risco à resposta está na plataforma** (o [4]: 16/19 e 16/22);
4. o tamanho da `U_repr_colado` na consolidação (4.2b: 6 → 12 e 7 → 93).

Pela regra de ouro do projeto (nenhum número agregado sem caso concreto, nenhuma decisão de destino sem verificação),
uma decisão de destino não pode depender de um número que só foi reexecutado.

**Solução.** [`scripts/audit_recompute9.py`](scripts/audit_recompute9.py) — uma segunda implementação do balde
invisível, no padrão dos `audit_recompute7/8`:

- **escrita a partir da prosa** do `13-racionais-falhas-silenciosas.md` (§2 o funil, §3 os grupos, §4 as medidas, §5 a
  forma) e do Ajuste 11;
- **sem pandas e sem importar o `base_pipeline`**: `csv` + `lzma` + `json` + `re`;
- o único insumo tirado do código é a **tabela** `MOTIVO_REGRAS`, lida do fonte por `ast`. A tabela é a especificação
  dos grupos (palavra-chave → grupo); a aplicação (normalização sem acento, ordem, a 1ª que casa decide) é
  reimplementada;
- o `erros_mecanismo.csv` entra como insumo para [2]/[3] — ele já é verificado erro a erro pelo `audit_recompute6`
  (checagem A, 0 divergências);
- escolhas **deliberadamente diferentes** das do pipeline, para que um erro de implementação apareça como divergência:
  o 1º argumento do `busca_obf` é recortado por contagem de parênteses (o pipeline usa uma janela de 600 caracteres);
  cada execução é lida uma vez só (o pipeline não deduplica linhas — a sonda F confirma 0 duplicadas na base 1);
- **roda na máquina 2** (`--base base2 --trace … --em … --fonte …`) e imprime só contagens e nomes: pode ser
  fotografado.

**Limite honesto.** A independência é de **implementação**, não de leitor: quem escreveu o `audit_recompute9` leu o
código do pipeline antes. O que protege é a construção por outro caminho e a comparação número a número.

**Evidência — resultado na base 1** (`python audit/scripts/audit_recompute9.py`, 02/10):

| Bloco | Conferido | Resultado |
|---|---|---|
| A · funil | 3.573 pares · 3.373 steps · 9 com exceção · **120 silenciosas** em 119 steps · 90 execuções · 10 meses · 13 papéis · 22 ferramentas · silenciosas ∩ `erros_mecanismo.csv` = 0 | todos OK |
| B · grupos | 43 · 2 · 41 · 19 · 6 · 9; 75 reais; soma = 120 | todos OK |
| C · [2] e [3] | 107 / 4 / 2 / 0 / 7 · `U_tipo_retorno` 4/47 · `U_contrato_dict` 1/96 · `U_campo_inexistente` 0/10 | todos OK |
| D · [4] | 30/41 · 16/19 · 0/6 · 8/9 · total **54/75** (depois do Ajuste 11) | todos OK |
| E · forma | `busca_obf`, `json_invalido`: 6/6 `str(literal colado)` | OK |
| **total** | | **0 divergências** |

O cruzamento "silenciosas ∩ tabela do balde visível = 0" substitui a conferência tautológica da Parte I. O notebook
confere a sobreposição dentro da mesma função que cria os baldes; aqui são **duas tabelas, de dois programas**.

## II.3 · O que a reimplementação encontrou

### II.3.1 · O [4] não era teto → Ajuste 11

**Contexto.** O [4] ("candidato a sucesso falso") pergunta: numa falha real de ferramenta, o papel entregou
`final_answer` sem a ferramenta ter funcionado? Ele é declarado **teto**: conta tudo o que *pode* ser sucesso falso,
e a leitura do caso confirma (plano 4.1b). É o número por trás do achado "o risco à resposta está na plataforma".

**O problema.** O código procurava o 1º `final_answer` **estritamente depois** da falha (`f > i`) e em **qualquer
chamada** do papel. A prosa do `13` §4 não diz nem uma coisa nem outra, e as duas escolhas erram em sentidos
opostos:

| Defeito | Por que é errado | Base 1 |
|---|---|---:|
| falha no **próprio step** do `final_answer` ficava fora | é o sucesso falso mais direto: o mesmo bloco chama a ferramenta, recebe `"Error calling tool…"` como texto e entrega a resposta | 2 falhas reais |
| final de **outra chamada** do papel valia | o papel pode ser chamado várias vezes na mesma execução (491 de 2.252 papéis); o final de outra tarefa não diz nada sobre esta falha | 2 falhas reais |

Os dois casos se cruzam num só. A falha de plataforma do `trigger_worker_execution` está no step final da chamada
dela; a regra antiga não via esse final e achava o de uma chamada **seguinte** — contava o caso certo pelo motivo
errado.

**Solução.** `falhas_silenciosas()` ganha a coluna `chamada` (quantos `TaskStep` vêm antes do step, na lista do papel).
O `idx_final_depois` passa a ser o 1º `final_answer` **com `f >= i` e na mesma chamada**. O
`sucesso_falso_candidato()` não muda.

**Por que precisamos dela.**

- Um teto que deixa fora o caso mais direto não é teto, e o plano 4.1b (ler os casos) partiria de uma lista
  incompleta.
- A fronteira de chamada é a mesma lição do S4 (o `idx` mistura as chamadas e já induziu uma leitura errada no erro
  crítico). Corrigir aqui evita que o [4] carregue o mesmo defeito para a base 2.
- A mudança vale para qualquer base: não usa nome de ferramenta nem de papel (regra "não escrever regra com uma base
  só").

**Evidência e verificação (base 1).**

| Grupo | Antes | Depois | O que mudou |
|---|---:|---:|---|
| `plataforma` | 16/19 | 16/19 | 1 caso mudou de **motivo** (final na mesma chamada), não de resultado |
| `argumento_do_agente` | 30/41 | 30/41 | — |
| `nao_reconhecido` | 7/9 | **8/9** | entra a falha do `validate_info_final_answer` no próprio step final |
| `json_invalido` | 0/6 | 0/6 | — |
| **total** | 53/75 | **54/75** | |

Três programas dão o mesmo número: o `drill_down.py silenciosas`, o notebook `falhas_silenciosas.ipynb` reexecutado
(nenhuma outra saída mudou — diff das saídas antes e depois) e o `audit_recompute9.py`. Os CSVs da esteira não são
tocados (o notebook da esteira não chama essas funções), e a `ocorrencias.csv` não tem as colunas que mudaram.

**A leitura publicada continua de pé.** O contraste plataforma (16/19) × `json_invalido` (0/6) não mudou. Na base 2, o
[4] publicado (20/116; plataforma 16/22) é de antes do ajuste e está marcado "a reconferir" no `14` §5. A regra nova só
**acrescenta** falhas no step final e **tira** finais de outra chamada, então uma virada da leitura é improvável — mas
quem confirma é a foto da máquina 2.

**Registro:** livro-razão §3, Ajuste 11 · `13` §4 e §7 · `14` §5 · commit `675523b`.

### II.3.2 · A regra `'DEFAULT'` estava anotada com a base errada

**Contexto.** Cada regra de `MOTIVO_REGRAS` anota a base de onde veio (`b1`, `b2`). A anotação é a prova da regra
"nenhuma regra nova olhando uma base só".

**Achado.** O `audit_recompute9` conta os disparos por regra. A regra `^'default'$`, anotada **só `b2`**, dispara **2
vezes na base 1**: CalculoCivel, `calculo_correcoes_monetarias`, fev/2026. É **a mesma calculadora** cuja falha
silenciosa começou a cadeia do erro crítico da base 2 (`11` §2.5).

**Solução.** A anotação passa a `b1 b2`. Nenhum grupo muda (a regra já se aplicava). **Por que importa:** o fato de a
mesma ferramenta devolver `'DEFAULT'` como resultado nas duas bases reforça o item da plataforma no aviso (4.9).
Deixa de ser um caso isolado da base 2.

### II.3.3 · A consolidação (4.2b) precisa definir o que é uma "ocorrência" no balde invisível

**Contexto.** O 4.2b junta as tabelas de ocorrências dos dois baldes e recalcula a recorrência das unidades. A
previsão do plano era: `U_repr_colado` passa de 6 para 12 (base 1) e de 7 para 93 (base 2).

**Achado.** As duas tabelas não têm a mesma granularidade:

- no **visível**, ocorrência = **cascata × unidade** (erros seguidos do mesmo papel contam uma vez);
- no **invisível**, `ocorrencias.csv` tem **uma linha por falha**.

Somar sem regra conta o mesmo gesto, repetido em steps seguidos, várias vezes de um lado e uma vez do outro.

**Evidência (base 1, sonda F do `audit_recompute9`).** As 120 silenciosas estão em 119 steps, que formam **100
sequências** de steps consecutivos. Nos 6 `json_invalido`, 6 falhas = 6 sequências, e **nenhuma execução em comum**
com os 6 `U_repr_colado` visíveis. Na base 1, então, "6 → 12" vale com qualquer das duas regras. Na base 2 (86 falhas)
não se sabe — o agente refaz a chamada e acerta, o que sugere falhas isoladas, mas é preciso contar.

**Solução.** O 4.2b ganha uma **pré-condição**: escolher a regra de ocorrência do balde invisível (falha × sequência)
olhando as duas bases, antes de consolidar. Os dois números que faltam saem da sonda F rodada na máquina 2 (II.6).
Registrado também como limite no `13` §7.

### II.3.4 · Sondas sem achado — o que elas descartam

| Sonda | Base 1 | O que descarta |
|---|---:|---|
| falha silenciosa sem a ferramenta chamada no step (o texto de erro reaparece porque o agente imprimiu uma variável antiga) | 2 (`sem_resultado`) e 0 com o motivo já visto antes | dupla contagem por eco de `print` — nenhuma falha real é eco |
| linhas repetidas da mesma execução no trace | 0 | dupla contagem por duplicata (o pipeline não deduplica — conferir na base 2) |
| papel com chave literal `"null"` | 2 execuções, 1 falha (`validador_calculo`) | só registro: entra nos "13 papéis" |
| regras anotadas `b1` que não disparam na base 1 | nenhuma | regra morta |

## II.4 · Ressalva D — a medida do M1 virou função

**Contexto.** O M1 ("resposta final fora do envelope") foi reconhecido em 30/09 por uma medida de sobreposição: o
texto que o modelo escreveu no lugar do bloco `<code>` reaparece na resposta final entregue depois → ele *antecipou* a
resposta e esqueceu o envelope. O número publicado (managerAgent 15/21, mediana 97%) sustenta o destino "sinal de
harness" do M1. A medida foi feita avulsa: não estava no repo e ninguém podia reproduzir.

**Solução.** `sobreposicao(texto, outro, n=5)` e `M1_LIMIAR = 0.5` no `base_pipeline.py`. O
`drill_down.py protocolo` ganha a seção **[9]**: por papel, quantos erros antecipam a resposta final (≥ limiar), a
mediana da sobreposição e quantos copiaram a observação anterior. As duas sobreposições por caso vão para o
`casos.csv`.

**Por que precisamos dela.** Um destino ("sinal de harness") que depende de uma medida não versionada não é auditável,
e não pode ser repetido na base 2 nem numa base 3. É também a primeira peça da Etapa C (mineração da família
Protocolo, 4.8), que vai transformar o catálogo M1–M6 em regras.

**Evidência — a reconstrução reproduz as 4 linhas publicadas** (`python drill_down.py protocolo`, [9]):

| Papel | Antecipou (publicado) | Antecipou ([9]) | Mediana | Cópia da observação (publicado → [9]) |
|---|---:|---:|---:|---:|
| managerAgent | 15/21, mediana 97% | **15/21** | **97%** | 2/21 → **2/21** |
| RespostaBacen | 1/7 | **1/7** | 0% | 1/7 → **1/7** |
| ConversationAgent | 0/3 | **0/3** | 14% | 0/3 → **0/3** |
| CalculoCivel | 0/2 | **0/2** | 1% | 0/2 → **0/2** |

**O limiar é reconstruído, e isso está declarado.** O de 30/09 não ficou registrado. Pelos valores por caso no
`casos.csv`, qualquer limiar em **(0,479; 0,523]** reproduz as 8 contagens. Em 0,479 ou abaixo, entra na antecipação
um caso do managerAgent com 0,479 (16/21). Acima de 0,523, sai da cópia o caso com 0,523 (1/21). Fica 0,5, dentro do
intervalo, e a margem é estreita dos dois lados: o número é sensível ao limiar. Isso está no `10` §4 e §7.
**Verificação:** as seções [1]–[8] do `protocolo` ficaram byte a byte iguais (diff da saída antes e depois).

**Limite que continua:** o falso negativo quando o LLM reescreve ao reembrulhar (ConversationAgent, 0/3 pela medida,
3/3 pela leitura). O [9] indica, a leitura confirma.

## II.5 · Ressalvas A, B, C e F — o que mudou e por quê

| | Mudança | Por que precisamos dela |
|---|---|---|
| **A** | `audit_recompute6.py`, checagem E: mês da execução, esperado 25/33 em out/2025 (90%), 7 das 12 ocorrências logo depois de erro de protocolo, 4 próprias em mar–jun/2026; comentário obsoleto ("fora de dez") reescrito. Roadmap 36 fechado; `03` §1.16 e livro-razão atualizados | uma auditoria que imprime divergência sempre ensina o leitor a ignorar divergência — a próxima real passaria. Agora A–G dão 0 divergências e qualquer `DIVERGE` volta a significar algo |
| **B** | `11` §1.1 e livro-razão: "25 steps sem erro, 7 `U_texto_solto` e 1 `U_estado_perdido`" | o texto tem que bater com a saída do comando que ele cita; o `U_estado_perdido` é um dos rótulos que o M6 esconde (`10` §4), então omiti-lo apagava um dado da S3 |
| **C** | `silenciosas`: "chamadas de ferramenta (step × ferramenta…): 3.573 em 3.373 steps" | dois números diferentes com o mesmo rótulo ("steps") parecem uma divergência entre o comando e o notebook (§13.1) — agora os dois aparecem com o nome certo |
| **F** | cabeçalho do livro-razão: "atualizado 02/10", estado com os Ajustes 10 e 11 e ponteiro para o `plano-atual.md` | o cabeçalho é a primeira coisa que se lê para saber se o arquivo está vivo |

## II.6 · O que continua aberto — e o roteiro para a máquina 2

A base 2 continua sendo verificada por fotos (ressalva E). Para fechá-la, o Rafael roda na `-second`:

```
# copiar do repo: pipeline/base_pipeline.py (restaurar TRACE e BASE_ID = "base2"), pipeline/drill_down.py,
#                 pipeline/falhas_silenciosas.ipynb, audit/scripts/audit_recompute9.py
uv run jupyter nbconvert --to notebook --execute --inplace falhas_silenciosas.ipynb
uv run python drill_down.py silenciosas
uv run python drill_down.py protocolo
uv run python ../audit/scripts/audit_recompute9.py --base base2 --trace ../data/<trace da base 2>.csv.xz \
       --em resultados/erros_mecanismo.csv --fonte base_pipeline.py
```

**Trazer (só contagens, pode fotografar):**

1. a saída inteira do `audit_recompute9` — os blocos A–C e E têm o publicado da base 2 como expectativa (o que não foi
   publicado aparece como "a conferir"). Qualquer `DIVERGE` vira um item do plano;
2. o bloco D do `audit_recompute9` (ou o [4] do `silenciosas`): **o [4] novo da base 2**, por grupo, que substitui o
   20/116;
3. o bloco F: os `json_invalido` em sequências e as execuções em comum com o `U_repr_colado` visível — a pré-condição
   do 4.2b;
4. o `protocolo` [9] (o M1 medido na base 2, até hoje só lido) e as §13.1/§13.7 do notebook (funil por step e
   detectores, ainda não rodados lá).

O resto continua no `plano-atual.md` (4.1b, 4.2b, 4.2c, S3–S6, D2), agora com estas pré-condições.

## II.7 · A base 2 rodada (02/10, tarde) — o que o roteiro II.6 trouxe

O Rafael rodou o roteiro na máquina 2: `drill_down.py silenciosas`, `drill_down.py protocolo` e `audit_recompute9.py
--base base2` (fotos de 02/10). Na primeira tentativa, o script falhou com "input format not supported by decoder". O
trace da base 2 é `.csv` sem compressão e o script abria tudo como `.xz`. Ele passou a reconhecer o formato pelo
conteúdo do arquivo (commit `2ba2c1f`, testado na base 1 nos dois formatos).

**Resultado: 0 divergências na base 2.** Funil (20 · 134 · 124 execuções · 7 meses · 18 ferramentas · 87%), os 6
grupos, [2], [3] e a forma (86/86: 80 `str(literal colado)` + 6 string colada) batem com o publicado. Silenciosas ∩
balde visível = 0 — a sobreposição da base 2, que só o notebook mostraria, ficou conferida. Os pares (8.232) e os
steps (2.771) batem com o cabeçalho do `silenciosas`. Pela regra antiga, a reimplementação dá **exatamente o 20/116
publicado**, o que confirma a independência também na base 2.

**O Ajuste 11 na base 2 — o que mudou de fato:**

| Grupo | Antes | Depois | Por quê |
|---|---:|---:|---|
| `plataforma` | 16/22 | **17/22** | 1 falha no próprio step do `final_answer` |
| `json_invalido` | 0/86 | **3/86** | 3 falhas no próprio step do `final_answer` |
| `argumento_do_agente` | 2/6 | 2/6 | — |
| `nao_reconhecido` | 2/2 | 2/2 | — |
| **total** | 20/116 | **24/116** | 4 no próprio step final; 0 finais de outra chamada |

**O que isso muda na leitura.** O II.3.1 previa "uma virada da leitura é improvável", e o contraste plataforma ×
`json_invalido` continua (77% × 3%). Mas uma frase publicada caiu: "o `json_invalido` **nunca** vira sucesso falso
(0/86)". Na base 2, em 3 casos o agente cola o print, recebe o erro como texto e entrega o `final_answer` no mesmo
bloco. Agora é **"quase nunca"**. Foi exatamente o tipo de caso que a regra antiga não enxergava — a melhor
evidência de que o ajuste era necessário. Corrigido no `14` (TL;DR, §1, §5), no livro-razão e no plano.

**O que a sonda F trouxe para a consolidação (4.2b-0).** Os 86 `json_invalido` são 86 sequências em 86 execuções, sem
execução em comum com o visível. A regra de ocorrência não muda o canal silencioso em nenhuma das duas bases. A sonda
achou outra coisa: o `U_repr_colado` **visível** da base 2 tem **18 erros em 18 execuções** no `erros_mecanismo.csv`
atual, não os 7 que os docs citam. O 7 vinha do Ajuste 2.2, que contou só o RoteadorCivel, e o próprio livro-razão
registra que "a triagem da base 2 depois do 2.2 ainda não foi vista". Não muda o destino (a unidade já é candidata),
mas muda o tamanho consolidado previsto (93 → 104, se forem 18). Está registrado como pendência do 4.2b-0, com o
comando de conferência.

**M1 na base 2 (`protocolo` [9]).** RoteadorCivel 0/56, OBFCivel 0/4, CalculoCivel 0/4 (mas 3/4 copiam a observação
anterior), RespostaBacen **2/4**, CalculoTrabalhista 0/1. O surto de agosto **não é M1**, como a leitura do `11` §2.3 já
indicava (M4/M5). Registrado no `11` §2.6.

## II.8 · Estado final

- **Auditoria de 02/10: fechada nas duas bases.** As ressalvas A–D, F e H foram resolvidas e G não pede ação. A E
  (base 2) ficou conferida pelo II.7; falta só a foto das §13.1/§13.7 do notebook (detectores), que não entram nos
  números auditados.
- **Ajuste 11** feito e verificado nas duas bases (54/75 e 24/116).
- **Balde invisível com verificação independente nas duas bases** (`audit_recompute9`, 0 divergências).
- **Uma pendência nova, fora do escopo auditado:** o `U_repr_colado` visível da base 2 (18 × 7), no 4.2b-0 —
  **resolvida no mesmo dia**: são 18 (triagem da base 2 pelo agente da máquina 2; livro-razão Etapa 10c, "Base 2
  rodada").
- **Nenhuma decisão de destino mudou.** As quatro decisões que dependem do balde invisível (II.2) foram confirmadas por
  um segundo programa.

| Commit | O quê |
|---|---|
| `675523b` | ressalvas A–C, F; M1 [9] (D); Ajuste 11; anotação `'DEFAULT'`; `audit_recompute9.py` |
| `2f953ea` | Parte II deste relatório; `audit/README.md` (índice de auditorias); `plano-atual.md`; índices |
| `2ba2c1f` | `audit_recompute9` lê `.csv` sem compressão (o trace da base 2) |
| (este) | II.7 — base 2 rodada; `14`, `11`, livro-razão e plano com os números da base 2 |
