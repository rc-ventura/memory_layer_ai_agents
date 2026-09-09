# Auditoria independente — parecer sobre a cadeia de evidência

**Data:** 2026-09-08 · **Auditor:** agente de auditoria · **Objeto:** toda a cadeia
`85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` → `pipeline/analise_trace_esteira_juridica.ipynb` →
`docs/01-racionais.md` → gráficos → `docs/02-relatorio-achados.md`.

**Método:** leitura integral dos 4 documentos, do notebook (62 células) e dos CSVs derivados;
**recomputação independente de ~40 números** direto do trace cru com `csv.DictReader` + `json` + `ast`,
sem reusar código do notebook nem pandas do pipeline (4 passes sobre os 875 MB); execução do
`drill_down.py` no caso-vitrine. Scripts e saídas brutas em [`scripts/`](scripts/)
(`audit_out*.txt` são git-ignored — podem conter PII; regenerar com `python3 scripts/audit_recompute*.py`,
ajustando o caminho `TRACE`/`REPO` no topo de cada script).

---

## 1 · Veredito geral

**Os números centrais da tese são fidedignos e reproduzíveis.** O notebook foi executado numa única
passada limpa (execution_count 1→30 sequenciais, zero células com erro, 12 PNGs embutidos). A espinha
dorsal do relatório bate **exatamente** com o raw trace por um caminho de código totalmente diferente:

| Afirmação do relatório | Recomputado | Status |
|---|---|---|
| 498 erros (8,6%) em 5.781 steps · 840 execs · 142.613.752 tokens | 498 (8,6%) · 5.781 · 142.613.752 | ✅ exato |
| 37,3% das execuções com erro | 313 (37,3%) | ✅ |
| **86,3% / 17,7% / 11,9%** (resultado central) | 430/498 · 76 · 51 | ✅ exato |
| 0 de 1.550 trajetórias terminam em erro | 1.550 traj. · 0 terminam em erro | ✅ |
| Execução com erro custa ~3× (146k vs 48k) | 146.306 vs 47.884 | ✅ |
| Propagação 1,8× (17,7% vs 9,7%) | 17,7% / 9,7% / 1,8× | ✅ |
| Assinaturas 159/136/35/33/39/20 + 1 não classificado | idênticas | ✅ |
| Pareto 1%→16,8% · 5%→41,9% · 10%→54,6% | idênticos | ✅ |
| Papel × assinatura: 94% / 76% / 62% / 56% / 45+24% | 94/76/62/56/45+24 | ✅ exatos |
| Tokens/chamada: 141.673 · 50.624 · 27.988 · 18.775 · agregada 21.420 · mediana 12.192 | idênticos | ✅ |
| Desperdício: CalculoCivel 25,0% · ConversationAgent 7,5M (9,8%) · managerAgent 3,5M (7,6%) · RespostaBacen 21,3% | idênticos | ✅ |
| Sucesso por conteúdo 840 → 834 (99,3%) → 310 (37,2%) | idênticos | ✅ |
| Result-Ignore 103/3.053 (3,4%) · RAC 125 · Tool-Skip 10 | idênticos | ✅ |
| 90 ferramentas declaradas · 80 distintas chamadas · 821/730 top-2 · 12 ferramentas posicionais | idênticos | ✅ |
| Medianas mensais 54.086 / 94.585 / 81.927 / 75.430 / 91.623 / 61.524 | idênticas | ✅ |
| Tokens em erro 13,95M (9,8%) · 159 min de latência · exec mais cara 5,9M | 13.946.017 · 159,2 min · 5.908.703 | ✅ |
| Caso-vitrine: 10 repetições consecutivas, exec `2a407143…`/`managerAgent` | 10 consecutivas reais (11 erros em 13 steps); *thoughts* batem **verbatim** com as citações do `03` | ✅ |
| `resultados/`: erros 498 linhas · execuções 840/313 · payoff/reincidência | consistentes com a recomputação | ✅ |

O achado central ("o agente lê o erro e reincide") sobreviveu à verificação mais profunda possível: o
caso citado existe, a sequência é real e as frases citadas em `03-procedimento-validacao.md` estão no
trace palavra por palavra.

> **Nota de reorganização (pós-auditoria):** os arquivos foram reorganizados em subpastas após esta
> auditoria. Referências neste relatório foram atualizadas: `01-racionais.md` → `docs/01-racionais.md`,
> `02-relatorio-achados.md` → `docs/02-relatorio-achados.md`, `03-procedimento-validacao.md` →
> `docs/03-procedimento-validacao.md`, `analise_trace_esteira_juridica.ipynb` →
> `pipeline/analise_trace_esteira_juridica.ipynb`, `drill_down.py` → `pipeline/drill_down.py`. As
> descrições abaixo usam o nome curto do arquivo quando o contexto é a lógica (não o path).

## 2 · Discrepâncias encontradas (ordenadas por severidade)

**Todas são de apresentação/completude — nenhuma afeta o pipeline nem os números da tese.**

- **S1 — Gráfico 8.9 com rótulo errado.** A linha vertical é rotulada "mediana geral", mas plotada em
  21.420 — a **razão agregada**, não a mediana verdadeira (12.192). É o mesmo "erro de rótulo" que o
  §3.3 do relatório afirma ter sido corrigido "em todos os três documentos" — o gráfico ficou de fora.
  Efeito: a regra de destaque laranja ("2× a mediana") incluiria também `ConversationAgent` se usasse a
  mediana real. **Corrigir antes de apresentar.**
- **S2 — Markdown do notebook preso a número pré-correção.** A seção 8.2 diz "os **59** do fim são a
  evidência" — 59 é o número velho do método por prefixo (13,7% × 430 ≈ 59). O gráfico logo abaixo
  mostra 51, correto.
- **S3 — Tabela §2.3 do relatório: "Sintaxe inválida 11,5s, n=64" não existe nos dados.** Recomputado:
  **7,6s, n=39**. A conclusão da seção ("string não fechada ≈ 2× retorno é dict") permanece válida;
  a linha precisa ser corrigida.
- **S4 — Tabela de candidatos (§6) × CSV divergem:**
  - Candidato 4: relatório diz 19 erros/1,06M; CSV diz 11/907k. O combo sandbox real dá 19 erros mas
    **1,10M** (1.096.590) — nem as duas versões batem, nem "19/1,06M" fecha.
  - Candidato harness: relatório 7/7/**3 meses**/0,12M; combo real (Falha LLM + HTTP 422) = 7 erros,
    7 execs, **4 meses**, 0,12M.
  Ajustar a tabela **ou** os CSVs para que contem a mesma história.
- **S5 — Tabela de famílias (§2) não fecha visualmente:** as linhas somam 495; o texto afirma "497 dos
  498 classificados". Faltam as linhas "Suposição sobre dados" (2 erros, 0,4%) e a do não classificado.
  Cada percentual individual está certo contra 498 — é omissão de completude.
- **S6 — Menores:**
  - §2.1: `WorkflowManager` "0%" → na verdade 1 erro em 301 steps = 0,3%.
  - §3.6 e o racional omitem **nov/2025** (n=33, mediana 56.725) — passa no corte n≥20 e aparece no
    gráfico 8.11, mas não na tabela. Conclusão inalterada.
  - §3.1 diz "final_answer do `managerAgent`", mas **134 das 840 execuções** usam fallback para o
    último `is_final` de qualquer papel. Conclusão robusta (subset estrito: 99,2%/36,9%); a descrição
    técnica está imprecisa.
  - Notebook imprime "12 colunas" contando a derivada `mes` (o raw tem 11) — não-material.
  - Notebook cell 61: link quebrado (`relatorio-achados.md` → `02-relatorio-achados.md`).
  - Cell 33: "(96 dos 103 são chamadas caras)" é string **hardcoded** no notebook (veio de script à
    parte, documentado no `03` §1.6). Aceitável; ideal seria recomputado na célula.

## 3 · Bijeção racionais ↔ notebook

**Racional → análise: íntegra.** Toda seção do `01-racionais.md` tem célula correspondente no notebook
(§2 robustez → célula 33; §3 → célula 15; §4 → células 17/19/21/23/25; §5 → células 9/11).

**Análise → racional: parcial.** O `01` cobre com passo-a-passo exatamente os **8 achados da rodada
nova** (2.2, 2.3, 3.1–3.6) + os conceitos de robustez. Ficam sem tratamento próprio:
**o funil central 86,3%/11,9% (§5 do notebook)** — o resultado mais importante! —, a recuperação
0/1550 (§4), a reincidência entre execuções (§6), o teste ToolScan IAN/IAV (§2.1), os números de
Result-Ignore/RAC/Tool-Skip (§7) e a tabela de candidatos (§9). Esses blocos têm cobertura conceitual
esparsa no §1 do `01`, mas não o "passo 1-2-3" que os demais receberam. Recomendação: declarar
explicitamente no topo do `01` que ele cobre só os achados novos desta rodada, **ou** adicionar seções
compactas para esses blocos (o §5 merece, no mínimo, o mesmo tratamento dos outros).

## 4 · Gráficos: proveniência

Os 12 gráficos têm rastreabilidade completa — cada um nasce de variável viva do pipeline:

| Gráfico | Célula | Fonte de dados |
|---|---|---|
| 8.1 causas-raiz | 36 | `E` (célula 5) — contagens verificadas |
| 8.2 funil lê-e-reincide | 38 | vars `checked/reached/repeated/same_sig` (célula 29) — verificadas |
| 8.3 custo não-falha | 40 | `execs` (célula 3) — verificado |
| 8.4 causa × mês | 42 | pivot de `E` — consistente |
| 8.5 payoff por causa | 44 | `payoff` (célula 13) — verificado no CSV |
| 8.6 taxa por posição/papel | 46 | `steps` direto — taxas verificadas |
| 8.7 Lorenz | 48 | `execs.tok_tot` — 16,8/41,9/54,6 verificados |
| 8.8 assinatura por papel | 50 | crosstab `E` — 94/76/... verificados |
| 8.9 tokens/chamada | 52 | `EF` (célula 19) — valores verificados; **rótulo errado (S1)** |
| 8.10 ranking duplo | 54 | `OR` (célula 23) — verificado |
| 8.11 evolução mensal | 56 | groupby mês — verificado; inclui nov/2025 (S6) |
| 8.12 funil sucesso | 58 | `S` (célula 15) — 840/834/310/524 verificados |

**Não há figuras órfãs** (nenhuma imagem colada externamente nem dado sem célula de agregação
identificável). Pendem apenas os dois problemas de rótulo/texto (S1, S2) e a assimetria gráfico×tabela
do §3.6 (S6).

## 5 · Recomendações para a apresentação ao auditor fiscal

1. **Corrigir S1–S5 antes de apresentar** — trivial de consertar, blinda contra a pergunta mais óbvia
   de um auditor.
2. **Apresentar sem ressalva:** 86,3%/11,9%; 59% das causas-raiz; 3× custo; Pareto 54,6%; 0/1550;
   reincidência mês a mês; e o caso-vitrine de 10 repetições (ter o
   `drill_down.py caso 2a407143-c37d-687f-4b4a-45f8dc413734 managerAgent` pronto — peça mais forte,
   com a revisão de PII que o `docs/03-procedimento-validacao.md` manda fazer antes de copiar trecho para slide).
3. **Apresentar com o qualificador ao lado:** RAC 125 ("definição conservadora; sensível à escolha"),
   Tool-Skip 10 ("provisório"), pico de mar/2026 ("43 steps").
4. **Abertura honesta que se sustenta:** a trajetória `d69ebbd6…`/`WorkflowManager` é a única sem
   `final_answer` e **não tem erro nenhum** — ou seja, "100% das trajetórias *com erro* chegam a
   resposta" é estritamente verdade.
5. Pendências estruturais já conhecidas: branch/commit do trabalho (`docs/04-roadmap.md`, urgente);
   nesta sessão **não foi verificado** o `.gitignore` contra o raw CSV (comando git recusado) — checar
   antes de qualquer push. O `.gitignore` da pasta agora cobre também `audit/scripts/audit_out*.txt`.

---

*Auditoria executada com os princípios do próprio `docs/03-procedimento-validacao.md` §1.4: recomputo por
caminho de código diferente, direto no trace cru, e triangulação de número agregado contra caso
concreto (`pipeline/drill_down.py`).*

---

## 6 · Resposta à auditoria (08/09/2026)

Todos os achados foram **verificados de forma independente** antes de aceitos (recomputo do CSV derivado e
da saída real do notebook, não do texto do parecer) e **corrigidos**. Nenhum foi rejeitado.

| Achado | Verificação | Correção aplicada |
|---|---|---|
| **S1** rótulo do 8.9 | confirmado: código usava `sum/sum` (21.420) rotulado "mediana geral" | linha e regra de cor agora usam `mediana_por_exec` (12.192); rótulo "mediana por execução". Como previsto, o laranja passou a incluir `ConversationAgent` |
| **S2** "59" na célula 37 | confirmado | → 51 |
| **S3** duração §2.3 | confirmado **e subestimado**: além de "11,5s/n=64" (real: **7,6s/n=39**), a tabela **omitia 2 famílias** que passam no próprio corte n≥20 | tabela refeita com as 7 famílias, ordenada por mediana |
| **S4** candidatos × CSV | confirmado: real = **1.096.590 (1,10M)** e **4 meses** | 1,06M → 1,10M; 3 → 4 meses |
| **S5** soma 495 ≠ 497 | confirmado | linhas "Suposição sobre dados" (2) e "(não classificado)" (1) adicionadas — tabela agora soma 498 |
| **S6a** WorkflowManager "0%" | confirmado: 1 erro / 301 steps | → 0,3% |
| **S6b** nov/2025 omitido | confirmado: n=33, mediana 56.725, passa no corte | linha adicionada; prosa ajustada para "linha de base nov–dez/2025" |
| **S6** link quebrado / `literatura/` | já corrigidos na reorganização em `docs/`+`pipeline/`; build script realinhado para não regredi-los | — |
| **§3** bijeção parcial | confirmado: o achado central não tinha passo-a-passo | **§3 novo no `01-racionais.md`** com a cadeia completa (7 passos), + nota de cobertura no topo declarando o que o documento cobre e o que não |

**Item que a auditoria não conseguiu verificar (`.gitignore` vs. raw CSV): verificado, está limpo.**
`git check-ignore` confirma que o trace cru é coberto por `.gitignore:8` (`*.csv.xz`), os CSVs derivados pelo
`.gitignore:3` da pasta e as saídas da auditoria pelo `:7`. Um `git add -A` não vaza PII.

**Notas menores aceitas sem alteração:** "12 colunas" (conta a derivada `mes`) e a string hardcoded
"(96 dos 103 são chamadas caras)" na célula 33 — ambas documentadas, não-materiais.

Notebook reexecutado após as correções: **62 células, 0 erros, 12 gráficos**.
