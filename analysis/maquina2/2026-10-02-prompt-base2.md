# Prompt para o agente da máquina 2 — fechar a base 2 (02/10/2026)

> **Como usar:** copie este arquivo para a máquina 2 e entregue-o inteiro ao agente como prompt. O agente roda os
> passos, preenche o **Relatório** do fim e o grava em `pipeline/resultados/relatorio_maquina2_2026-10-02.md`
> (git-ignored). O Rafael cola o relatório na conversa da máquina 1.
> Origem: `analysis/plano-atual.md` itens 4.2a, 4.2b-0, 4.1b e D2; auditoria de 02/10, Parte II §II.6–II.7.

---

## Você é o agente da máquina 2

Você trabalha na pasta da **base 2** do projeto: `analysis/2026-09-trace-law-flow-second/`. Os comandos rodam de
dentro de `pipeline/`, com `uv run` na frente (Git Bash, Windows). O trabalho tem dois tipos de passo:

- **Passos 1–3:** rodar comandos e copiar números para o relatório. É conferência **determinística**: marque
  **[conferido]**.
- **Passos 4–5:** ler casos e classificá-los. É **leitura assistida por LLM**: marque cada classificação como
  **[assistido]**. Ela entra como hipótese, nunca como fato.

### Regras invioláveis (compliance)

1. **Do relatório só saem:** contagens, percentuais, nomes de papel, ferramenta, modelo e unidade, hashes de versão,
   meses, tamanhos, tokens, sim/não e as categorias fechadas deste prompt.
2. **Nunca saem:** `exec_id`, texto de caso (pergunta, documento, resposta, observação), código do agente, conteúdo
   de prompt, motivo de erro sem máscara. Se precisar citar um caso, use "caso 1, caso 2…".
3. **Não altere nenhum arquivo do repositório.** Pode criar arquivos só dentro de `pipeline/resultados/` (git-ignored).
   Não faça commit nem push.
4. **Não invente número.** Se um comando falhar, copie a mensagem de erro (sem dado de caso) e siga para o próximo
   passo. Se um número divergir do esperado, registre os dois; **não tente consertar**.
5. **Pré-condição:** `pipeline/base_pipeline.py` com `TRACE` apontando para o trace da base 2
   (`a0b49c79-8e90-4fd7-8cd2-c7ab38eaa43e.csv`) e `BASE_ID = "base2"`. `pipeline/drill_down.py` na versão do commit
   `bd85a61` ou posterior (o `casos.csv` das silenciosas tem a coluna `sucesso_falso_candidato`). Confira as duas
   coisas antes de começar e registre no relatório.

---

## Passo 1 — A esteira da base 2 (a triagem nunca vista depois do Ajuste 2.2)

```
uv run jupyter nbconvert --to notebook --execute --inplace analise_trace_esteira_juridica.ipynb
uv run python -c "import pandas as pd; c=pd.read_csv('resultados/candidatos_memoria.csv'); print(c[['unidade','decisão','destino (mineração)','ocorrências','erros','execuções','meses','papéis']].to_string())"
uv run python -c "import pandas as pd; k=pd.read_csv('resultados/criticos.csv'); print(len(k), 'críticos'); print(k[['role','mes','idx do erro crítico','steps no papel','erros antes','primeira unidade']].to_string())"
```

**Copiar para o relatório:** a tabela inteira de unidades e a linha dos críticos (sem `exec_id`).

**Esperado (conferir e marcar ✅/❌):**

| Item | Esperado | Origem |
|---|---|---|
| `U_repr_colado` | decisão `candidato` | Ajuste 2.2 |
| `U_resultado_bruto` | `fora: sem recorrência` (3 erros, 2 execuções, 1 mês) | Ajuste 9 |
| `U_codigo_lento` | ausente da tabela (0 erros) | Ajuste 9 |
| `H_timeout_ferramenta` | não-memória | Ajustes 4/8 |
| `U_campo_inexistente` | **não** `sinal de harness` (o destino da mineração só vale na base 1) | Ajuste 7 |
| críticos | 1 linha: CalculoCivel, fev/2026 | `11` §2.5 |

## Passo 2 — O `U_repr_colado` visível: 18 ou 7? *(depois do passo 1)*

```
uv run python -c "import pandas as pd; M=pd.read_csv('resultados/erros_mecanismo.csv'); x=M[M.unidade=='U_repr_colado']; print(len(x), 'erros ·', x.exec_id.nunique(), 'execuções'); print(x.groupby(['role','mes']).size().to_string())"
```

**Esperado:** 18 erros em 18 execuções (o que o `audit_recompute9` viu). Os docs citam 7, mas esse número era só o
RoteadorCivel do Ajuste 2.2. **Copiar:** o total e a tabela papel × mês.

## Passo 3 — O balde invisível (notebook)

```
uv run jupyter nbconvert --to notebook --execute --inplace falhas_silenciosas.ipynb
uv run python drill_down.py silenciosas
```

**Copiar do notebook:**
- §13.1, o funil: falhas com exceção, silenciosas, %, steps, sobreposição visível × invisível;
- §13.5: o [4] por grupo;
- §13.7, os detectores: inventário declarado, Result-Ignore (n de N atribuições), RAC, Reasoning-action mismatch
  (só registro), Tool-Skip (n de N execuções), ferramentas chamadas × declaradas.

**Esperado:**

| Item | Esperado |
|---|---|
| falhas com exceção · silenciosas · % | 20 · 134 · 87% |
| steps com falha silenciosa | 134 |
| sobreposição visível × invisível | **0** (se não for 0, o funil quebrou: registre e pare o passo) |
| [4] por grupo | plataforma 17/22 · argumento 2/6 · `json_invalido` 3/86 · não reconhecido 2/2 · total **24/116** |
| §13.7 | sem esperado: é a primeira vez na base 2. Referência da base 1: inventário 90; Result-Ignore 103/3.053; RAC 125; Tool-Skip 10/840; 80 × 90 |

O `drill_down.py silenciosas` regrava `resultados/evidencia/silenciosas/casos.csv` com a coluna
`sucesso_falso_candidato`. O passo 4 precisa dela.

## Passo 4 — 4.1b: o candidato a sucesso falso é sucesso falso? *[assistido]*

Liste os candidatos **só na sua tela**. Esta lista tem `exec_id` e **não vai para o relatório**:

```
uv run python -c "import pandas as pd; c=pd.read_csv('resultados/evidencia/silenciosas/casos.csv'); x=c[c.sucesso_falso_candidato & c.grupo.isin(['plataforma','json_invalido'])]; print(x[['exec_id','role','idx','chamada','ferramenta','grupo','idx_final_depois']].to_string())"
```

Escolha **3 casos de `plataforma`**, de ferramentas diferentes se der, e **os 3 de `json_invalido`**. Para cada um:

```
uv run python drill_down.py caso <exec_id> <papel>
```

Leia o step `idx` (a falha) e o step `idx_final_depois` (o `final_answer` da **mesma chamada**) e responda:

| Pergunta | Opções |
|---|---|
| P1. A falha e o `final_answer` estão no mesmo step? | sim · não |
| P2. O `final_answer` usa um dado que deveria ter vindo da ferramenta que falhou? | **sim** (sucesso falso) · **não** (a resposta não depende dela) · **indeterminado** |
| P3. Se sim: o `final_answer` declara a falha ao usuário? | declara · omite · inventa um valor no lugar |
| P4. Se não: de onde veio o dado? | outra ferramenta · nova chamada da mesma ferramenta · resposta não precisa do dado · outro |

## Passo 5 — D2: os 4 erros de protocolo do RespostaBacen *[assistido]*

```
uv run python drill_down.py protocolo        # só se resultados/evidencia/protocolo/casos.csv não existir
uv run python drill_down.py protocolo --casos RespostaBacen 4
uv run python drill_down.py ferramenta resposta_final
uv run python metadados_steps.py RespostaBacen
```

Para cada um dos 4 arquivos `erro_RespostaBacen_*.txt`, use o roteiro A–D do
`docs/12-procedimento-protocolo-harness.md` §Passo 4:

| Pergunta | Opções |
|---|---|
| A. O que escreveu no lugar do código | resposta em texto/markdown · `final_answer(` sem `<code>` · só o plano · tag errada · JSON do negócio · pergunta ao usuário · fragmento · vazio |
| B. O que havia antes | primeiro step do papel · observação normal · `Last output… None` · erro de ferramenta · JSON de uma ferramenta de "resposta final" |
| C. Step seguinte | recuperou com `final_answer` · outra ferramenta · nada · o mesmo conteúdo reembrulhado |
| D. Fim do prompt | pede formato? · "pode responder diretamente"? · resposta final = saída de ferramenta? |
| Mecanismo | **M1** (resposta fora do envelope) · **M2** (`resposta_final` concorre com o `final_answer`: "achou que terminou") · M3 · M4/M5 · outro |
| Declaração do `resposta_final` no step | `resposta_gerada` · `json_resposta` · outra · ausente (só o nome do argumento) |

Do `metadados_steps.py`, copie por caso: tokens de saída, caracteres visíveis e `finish_reason`, só os números.

---

## Hipóteses que estes passos testam

No fim do relatório, diga para cada uma: **apoia · contradiz · sem dados**, com o número que decide.

| H | Hipótese | Passo |
|---|---|---|
| H1 | A `U_repr_colado` é uma unidade só, com dois canais. Na base 2: 18 visíveis + 86 silenciosas = **104** (não 93) | 1, 2 |
| H2 | Os candidatos de plataforma são sucesso falso de verdade (a resposta usa o dado que não veio) | 4 |
| H3 | Os 3 `json_invalido` no step final são resposta errada, não só retrabalho | 4 |
| H4 | O M2 reaparece no RespostaBacen (o `resposta_final` concorre com o `final_answer`); o sinal é o 2/4 do M1 no `protocolo` [9] | 5 |
| H5 | O M6 (narração executada como código) se esconde sob rótulos de memória: 5 `U_estado_perdido` e 3 `U_texto_solto` logo depois do protocolo | sem passo hoje (S3); registre só se aparecer na leitura |
| H6 | Os 3/4 do CalculoCivel que copiam a observação fazem parte da cadeia do erro crítico | sem passo hoje; registre se aparecer |
| H7 | O M4 gasta tokens em raciocínio oculto do `gpt-5.6-terra` (242 tokens para 138 caracteres) | não testável com o trace |
| H8 | A triagem da base 2 depois dos Ajustes 2.2–10 mantém as candidatas e deixa o `U_resultado_bruto` fora | 1 |

---

## Relatório (preencher e gravar em `pipeline/resultados/relatorio_maquina2_2026-10-02.md`)

```markdown
# Relatório da máquina 2 — base 2 — 02/10/2026

## 0. Pré-condições
- TRACE da base 2: sim/não · BASE_ID = "base2": sim/não · drill_down.py com a coluna sucesso_falso_candidato: sim/não
- Comandos que falharam (mensagem sem dado de caso):

## 1. Esteira — triagem da base 2 [conferido]
<tabela de unidades: unidade · decisão · destino · ocorrências · erros · execuções · meses · papéis>
Críticos: <n> · <papel, mês, idx, steps no papel, erros antes, primeira unidade>
Esperados: U_repr_colado ✅/❌ · U_resultado_bruto ✅/❌ · U_codigo_lento ✅/❌ · H_timeout_ferramenta ✅/❌ · U_campo_inexistente ✅/❌ · críticos ✅/❌

## 2. U_repr_colado visível [conferido]
<n erros · n execuções> · <papel × mês>

## 3. Balde invisível [conferido]
§13.1: <exceção · silenciosas · % · steps · sobreposição>
§13.5 [4]: <por grupo e total>
§13.7: inventário <n> · Result-Ignore <n/N> · RAC <n> · mismatch <n> (registro) · Tool-Skip <n/N> · chamadas × declaradas <a × b>
Divergências do esperado: <lista ou "nenhuma">

## 4. Sucesso falso — leitura [assistido]
| caso | grupo | ferramenta | P1 mesmo step | P2 usa o dado | P3 | P4 |
|---|---|---|---|---|---|---|
Resumo: plataforma <sim/3> · json_invalido <sim/3>

## 5. RespostaBacen — leitura [assistido]
| caso | mês | modelo | A | B | C | D | mecanismo | declaração | tokens saída | caracteres | finish |
|---|---|---|---|---|---|---|---|---|---|---|---|
Resumo: M1 <n> · M2 <n> · outro <n>

## 6. Hipóteses
| H | apoia / contradiz / sem dados | número que decide |
|---|---|---|
| H1 | | |
| H2 | | |
| H3 | | |
| H4 | | |
| H5 | | |
| H6 | | |
| H7 | | |
| H8 | | |

## 7. O que chamou atenção e não estava no roteiro (sem dado de caso)
```
