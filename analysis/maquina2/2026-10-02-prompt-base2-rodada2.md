# Prompt para o agente da máquina 2 — base 2, rodada 2 (02/10/2026; consolidação e triagem na consolidação acrescentadas em 04/10)

> **Como usar:** copie este arquivo para a máquina 2 e entregue-o inteiro ao agente. O agente roda os passos, preenche o
> **Relatório** do fim e o grava em `pipeline/resultados/relatorio_maquina2_2026-10-02_rodada2.md` (git-ignored). O
> Rafael fotografa o relatório e traz para a máquina 1.
> Origem: `analysis/plano-atual.md`, bloco "Decidido e entendido na revisão dos achados da base 2 (02/10)". Os termos
> estão explicados em `analysis/glossario.md`.

---

## Você é o agente da máquina 2

Você trabalha na pasta da **base 2**: `analysis/2026-09-trace-law-flow-second/`. Os comandos rodam de dentro de
`pipeline/`, no **terminal** (Git Bash), com `uv run` na frente. **Não rode notebooks pelo editor**: na rodada 1 eles não
terminaram lá.

Dois tipos de passo:

- **Passos 0–3:** rodar e copiar números. É conferência determinística: marque **[conferido]**.
- **Passos 4–5:** ler casos e classificar. É leitura assistida por LLM: marque **[assistido]**. Vale como hipótese.

### Regras (compliance)

1. **Do relatório só saem:** contagens, percentuais, nomes de papel, ferramenta, modelo e unidade, hashes, meses,
   sim/não, as categorias fechadas deste prompt e — **só na seção C** do script — **nomes de campo** do contrato das
   ferramentas (as chaves; nunca os valores).
2. **Nunca saem:** `exec_id`, texto de caso (pergunta, documento, resposta, observação, justificativa), código do agente,
   texto de prompt, mensagem de erro, nome de variável do agente.
3. **Não altere arquivos do repositório**, exceto as duas linhas do passo 0. Arquivos novos só em `pipeline/resultados/`.
   Nada de commit nem push.
4. **Não invente número.** Se um comando falhar, copie a última linha da mensagem de erro (sem dado de caso) e siga.
   Se um número divergir do esperado, registre os dois e **não tente consertar**.

---

## Passo 0 — As cópias são as da branch?

Copie da branch `2026-10-02-consolidacao-unidades` (o commit do plano 4.2c, de 04/10, ou posterior), **sem abrir no editor antes de
conferir**:

| Arquivo (destino na `-second`) | SHA-256, 16 primeiros caracteres (LF ou CRLF, os dois valem) |
|---|---|
| `pipeline/drill_down.py` | `5c39b55b5ea171dd` ou `d1305a7fdaf96911` |
| `pipeline/investigacao_achados.py` (novo) | `951524946316ede9` ou `4c82171f630658ac` |
| `pipeline/falhas_silenciosas.ipynb` | `97382af1666a6941` ou `c2409f364e81e1c4` |
| `pipeline/consolidacao_unidades.ipynb` (novo) | `2137e7d46b11d61a` ou `1a4278c6dbe195da` |
| `pipeline/analise_trace_esteira_juridica.ipynb` | `b856476c81233820` ou `a5e82ea87589473c` |
| `audit/scripts/audit_recompute9.py` | `0d14ef1d8db93249` ou `d38919318b61759d` |
| `pipeline/base_pipeline.py` — **antes** de editar | `21dba8f51c99a933` ou `b4189fa1fb3490d6` |

```
sha256sum drill_down.py investigacao_achados.py falhas_silenciosas.ipynb consolidacao_unidades.ipynb analise_trace_esteira_juridica.ipynb base_pipeline.py ../audit/scripts/audit_recompute9.py
```

Depois, no `base_pipeline.py`, troque **só** duas coisas: o nome do arquivo do `TRACE` (linha 34) para
`"a0b49c79-8e90-4fd7-8cd2-c7ab38eaa43e.csv"` e `BASE_ID = "base2"` (linha 37). Confira com
`diff <cópia da branch> base_pipeline.py`: só essas duas linhas podem aparecer.

## Passo 1 — A esteira (o notebook inteiro, no terminal)

```
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 analise_trace_esteira_juridica.ipynb
```

**Esperado (da rodada 1):** 479 erros · 16 unidades · 1 erro crítico. Se o notebook terminar, os números têm de repetir.
**Mudou em 04/10:** a esteira **não faz mais a triagem** — as candidatas e as contagens por unidade saem do passo 2b
(consolidação), e o `candidatos_memoria.csv` é gravado lá.

## Passo 2 — O balde invisível (o notebook inteiro, no terminal)

```
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 falhas_silenciosas.ipynb
uv run python ../audit/scripts/audit_recompute9.py --base base2 --trace ../data/a0b49c79-8e90-4fd7-8cd2-c7ab38eaa43e.csv
```

**Esperado:** 20 falhas de ferramenta com exceção · 134 silenciosas · 87% · sobreposição entre os baldes 0 ·
candidatos a sucesso falso 24 de 116 · detectores: inventário 116, retorno ignorado 203 de 8.661, chamada repetida 350,
ferramenta não chamada 3 de 1.000, chamadas × declaradas 103 × 116 · a conferência independente com **0
divergências**.

## Passo 2b — A consolidação (o notebook inteiro, no terminal; depois do passo 2)

```
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 consolidacao_unidades.ipynb
```

O `audit_recompute9` do passo 2 já traz o **bloco G** (a mesma unidade, recalculada de forma independente).

**Esperado (Ajuste 12 e plano 4.2c):** §14.2 — 16 unidades · **8 candidatas (370 erros)** · 1 erro crítico · "nome usado
sem ter sido definido" 118 erros · "colar o print do retorno" 18 erros visíveis (os números da triagem da rodada 1, que
agora sai daqui). §14.1 — steps nos dois canais **0**; "colar o print do retorno" (`U_repr_colado`): 18
ocorrências visíveis, 86 silenciosas, **0 execuções em comum**. §14.3 — só ela muda: ocorrências e execuções **18 →
104**; nenhuma decisão muda; nenhuma unidade nova. Bloco G: ocorrências 104 e execuções 104 OK; meses e papéis "a
conferir" (copie os números). Se a §14.3 listar outra unidade ou outra coluna, copie a tabela inteira.

## Passo 3 — As seis perguntas abertas

```
uv run python investigacao_achados.py > resultados/investigacao_achados_base2.txt
```

Copie a saída inteira para o relatório. Ela só tem contagens e nomes. Para cada seção, a pergunta é:

| Seção | Pergunta | O que decide |
|---|---|---|
| A · colar o print, canal visível | os 18 erros visíveis estão na chamada do `busca_obf`? | se sim, é o mesmo gesto dos 86 do canal silencioso, na mesma ferramenta |
| B · nome usado sem ter sido definido | o nome nunca existiu, se perdeu, foi definido numa chamada anterior do papel, é ferramenta? Que modelo? Vem depois de uma resposta sem bloco de código? | o que é a maior candidata da base 2 |
| C · campo inexistente no retorno | qual chave foi pedida, quais o retorno tinha, de que ferramenta; o prompt menciona a chave pedida? | se é a mesma essência da base 1 (o prompt induz o nome errado) |
| D · o erro crítico | em que chamada aparece o `'DEFAULT'`; as outras chamadas se recuperaram; o pensamento menciona a falha; a ferramenta é chamada de novo | se o `'DEFAULT'` desencadeia a cascata |
| E · desfecho dos 24 candidatos a sucesso falso | não dependia · falha declarada · a resposta repassa o texto do erro · sucesso falso provável · ler (os candidatos já excluem os que se recuperaram) | quantos são sucesso falso de verdade |
| F · versões da declaração do `busca_obf` | a taxa de JSON inválido muda com a versão? | experimento natural sobre a declaração |

## Passo 4 — A regra da seção E bate com a leitura da rodada 1? *[assistido]*

A seção E grava `resultados/evidencia/silenciosas/desfechos.csv` (tem `exec_id`: **não sai da máquina**). Na rodada 1,
você leu 6 candidatos: 3 de plataforma (as calculadoras `calculo_correcoes_monetarias`, `calculo_enquadramento`,
`calculo_horas_extras`) e os 3 de JSON inválido do `busca_obf`. Para cada um, compare o `desfecho` do CSV com a sua
leitura:

| Sua leitura (rodada 1) | Desfecho do script que concorda |
|---|---|
| a resposta não precisava do dado / veio de outra ferramenta | "não dependia" |
| a resposta declara a falha | "falha declarada" ou "a resposta repassa o texto do erro" |
| a resposta usa o dado que faltou | "sucesso falso provável" |

Traga só: **concorda em n de 6**, e, para os que discordam, o grupo e as duas categorias.

## Passo 5 — Ler o que a regra não decide *[assistido]*

Liste na sua tela (não vai para o relatório):

```
uv run python -c "import pandas as pd; d=pd.read_csv('resultados/evidencia/silenciosas/desfechos.csv'); print(d['desfecho'].value_counts().to_string()); print(d[d['desfecho'].str.contains('ler')][['exec_id','role','idx','ferramenta','grupo','idx_final','desfecho']].to_string()); print(d[~d['desfecho'].str.contains('ler')].sample(min(5, int((~d['desfecho'].str.contains('ler')).sum())), random_state=20261002)[['exec_id','role','idx','ferramenta','grupo','idx_final','desfecho']].to_string())"
```

Leia **todos os marcados "— ler"** (até 8) e a **amostra sorteada de 5** dos demais, com
`uv run python drill_down.py caso <exec_id> <papel> --json` (o `--json` mostra o `action_output` inteiro do step final).
Para cada caso:

| Pergunta | Opções |
|---|---|
| A resposta final usa um dado que deveria ter vindo da ferramenta que falhou? | sim · não · indeterminado |
| Se sim: a resposta declara a falha, omite, ou inventa um valor no lugar? | declara · omite · inventa |
| Se não: de onde veio o dado? | outra ferramenta · nova chamada · a resposta não precisa do dado · outro |
| O desfecho do script estava certo? | sim · não (qual seria) |

---

## Relatório (gravar em `pipeline/resultados/relatorio_maquina2_2026-10-02_rodada2.md`)

```markdown
# Relatório da máquina 2 — base 2, rodada 2 — 02/10/2026

## 0. Cópias
| arquivo | hash confere com a branch? |
|---|---|
base_pipeline.py: o diff mostra só TRACE e BASE_ID? sim/não

## 1. Esteira [conferido]
Terminou no terminal? sim/não (se não: a última linha do erro)
erros · unidades · críticos — e se repetem a rodada 1 (as candidatas saem no 2b)

## 2. Balde invisível [conferido]
Terminou? sim/não · funil · candidatos a sucesso falso · detectores · conferência independente: n divergências

## 2b. Consolidação [conferido]
Terminou? sim/não · §14.1: steps nos dois canais · U_repr_colado visíveis/silenciosas/execuções em comum ·
§14.2: unidades · candidatas (erros) · críticos · nome não definido · colar o print — e se repetem a rodada 1 ·
§14.3: a tabela do que muda (inteira) · §14.8: a linha "sensibilidade (≥5 execuções, ≥3 meses): n de N" ·
bloco G do audit_recompute9: ocorrências, execuções, meses, papéis, divergências

## 3. As seis perguntas [conferido]
<a saída inteira do investigacao_achados.py, seções A a F>

## 4. A regra do desfecho × a leitura da rodada 1 [assistido]
concorda em n de 6 · discordâncias (grupo, leitura, script)

## 5. Leitura dos casos que a regra não decide + amostra sorteada [assistido]
| caso | grupo | ferramenta | usa o dado que faltou? | declara/omite/inventa | de onde veio | o script estava certo? |
|---|---|---|---|---|---|---|
Resumo: sucessos falsos confirmados n de N lidos; o script acertou em n de N

## 6. O que chamou atenção e não estava no roteiro (sem dado de caso)
```
