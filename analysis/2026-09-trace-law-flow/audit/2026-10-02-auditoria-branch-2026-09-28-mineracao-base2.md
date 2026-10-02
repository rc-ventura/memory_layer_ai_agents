# Auditoria independente — branch `2026-09-28-mineracao-base2` (PR #29, aberto)

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
