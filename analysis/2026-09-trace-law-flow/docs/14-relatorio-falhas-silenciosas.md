# Relatório das falhas silenciosas — o balde invisível, por base

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Para que serve este documento:** os números do balde invisível em cada base, e o que eles querem dizer. Mesmo papel
do [`02-relatorio-achados.md`](02-relatorio-achados.md), só para o erro que não vira exceção. O **porquê** de cada
medida está em [`13-racionais-falhas-silenciosas.md`](13-racionais-falhas-silenciosas.md); como repetir numa base nova,
em [`15-procedimento-falhas-silenciosas.md`](15-procedimento-falhas-silenciosas.md). Base 1: saída do notebook
[`../pipeline/falhas_silenciosas.ipynb`](../pipeline/falhas_silenciosas.ipynb) (01/10; reexecutado em 02/10 com o
Ajuste 11). Base 1 conferida também por uma implementação independente
([`../audit/scripts/audit_recompute9.py`](../audit/scripts/audit_recompute9.py), 0 divergências). Base 2: fotos da máquina 2 do
`drill_down.py silenciosas` e `silenciosas --forma busca_obf` (01/10) — as mesmas funções; o notebook ainda não rodou lá.

---

## TL;DR

- **~90% das falhas de ferramenta são invisíveis à exceção** nas duas bases (93% e 87%): a ferramenta devolve a falha
  como texto, o step fica com `error: null`.
- **Elas passam sem rastro:** em 89–91% dos casos, o mesmo papel não tem nenhum erro com exceção nos 3 steps seguintes.
- **As memórias de contrato de retorno não nascem delas:** só 0–9% de `U_tipo_retorno` / `U_campo_inexistente` vêm logo
  depois de uma falha silenciosa. Continuam memória candidata.
- **O risco à resposta estaria na plataforma — hipótese, não achado:** 16/19 e **17/22** das falhas de plataforma
  terminam em `final_answer` na mesma chamada sem a ferramenta ter funcionado. São candidatos a sucesso falso (teto).
  Mas na leitura de 3 casos da base 2, **nenhum** usava o dado que faltou (§5).
- **O `json_invalido` é o `repr_colado` no canal silencioso:** 6/6 e 86/86 são o agente colando o print do
  `puxa_doc_decisao` no `busca_obf`. Na base 2, o canal silencioso é muito maior que o visível (86 × 18 — conferido em
  02/10). **Quase nunca** vira sucesso falso (0/6, **3/86** — os 3 no próprio step do
  `final_answer`, que a regra antiga não via): o custo é sobretudo retrabalho.

## 1 · O funil e a escala

| | Base 1 | Base 2 |
|---|---:|---:|
| falhas de ferramenta com exceção (ficam no balde visível) | 9 | 20 |
| **falhas silenciosas** | **120** | **134** |
| % silenciosas entre as falhas de ferramenta | 93% | 87% |
| execuções · meses | 90 · 10 | 124 · 7 |
| papéis · ferramentas | 13 · 22 | 10 · 18 |
| sobreposição visível × invisível (por step) | 0 | 0 |
| steps · sequências de steps consecutivos | 119 · 100 | 134 · 129 |

Base 1: os 120 estão em 119 steps (um step com duas ferramentas falhando). Base 2: papéis, steps, sequências e
sobreposição vêm do `audit_recompute9` rodado na máquina 2 (02/10; 0 divergências no resto).

## 2 · Por ferramenta (as principais)

| Base 1 | steps | silenciosas | % | | Base 2 | steps | silenciosas | % |
|---|---:|---:|---:|---|---|---:|---:|---:|
| `get_available_documents` | 667 | 57 | 9% | | `busca_obf` | 697 | 86 | 12% |
| `compare_documents` | 48 | 13 | 27% | | `get_peticao_inicial_from_pasta` | 380 | 8 | 2% |
| `answer_question_using_documents` | 744 | 11 | 1% | | `calculo_correcoes_monetarias` | 15 | 7 | 47% |
| `table_statistical_summary` | 10 | 8 | 80% | | `calculo_horas_extras` | 12 | 4 | 33% |
| `busca_obf` | 44 | 6 | 14% | | `draft_resposta` | 90 | 4 | 4% |

As ferramentas que dominam são diferentes em cada base — as esteiras usam ferramentas diferentes. O que se repete são os
grupos (§3).

## 3 · Os grupos do motivo

| Grupo | Base 1 | Base 2 | Falha real? | Dono |
|---|---:|---:|---|---|
| `sem_resultado` | 43 | 8 | não | ninguém |
| `fora_da_cobertura` | 2 | 10 | não | negócio |
| `argumento_do_agente` | **41** | 6 | sim | agente |
| `plataforma` | 19 | 22 | sim | plataforma / ferramenta |
| `json_invalido` | 6 | **86** | sim | a conferir → nas duas bases, o agente (§6) |
| `nao_reconhecido` | 9 | 2 | sim | cobertura |
| **falhas reais** | **75** | **116** | | |

Base 2: o [1b] bate grupo a grupo com o que fora calculado aplicando as regras às contagens do `--motivos` — conferido
rodando.

## 4 · O que vem depois

**[2] o 1º erro com exceção do mesmo papel em até 3 steps:**

| | Base 1 | Base 2 |
|---|---:|---:|
| (nenhum erro) | 107 | 122 |
| `U_tipo_retorno` | 4 | 3 |
| `H_bloco_code` | 2 | 3 |
| `U_campo_inexistente` | 0 | 3 |
| outros | 7 | 3 |

**[3] contrato de retorno precedido por falha silenciosa (até 3 steps antes, mesmo papel):**

| | Base 1 | Base 2 |
|---|---|---|
| `U_tipo_retorno` | 4/47 (9%) | 5/79 (6%) |
| `U_contrato_dict` | 1/96 (1%) | 0/0 |
| `U_campo_inexistente` | 0/10 (0%) | 3/38 (8%) |

**Leitura:** a falha silenciosa não deixa rastro no balde visível, e as memórias de contrato não são efeito dela.
**Nenhum Ajuste** nas unidades de contrato.

## 5 · Candidato a sucesso falso [4]

| Grupo | Base 1 | Base 2 |
|---|---|---|
| `plataforma` | **16/19 (84%)** | **17/22 (77%)** |
| `argumento_do_agente` | 30/41 (73%) | 2/6 |
| `nao_reconhecido` | 8/9 | 2/2 |
| `json_invalido` | **0/6** | **3/86 (3%)** |
| **total** | **54/75** | **24/116** |

**Ajuste 11 (02/10).** Candidato = o papel entregou `final_answer` **no próprio step da falha ou depois, na mesma
chamada**. Antes valia o 1º final estritamente depois, em qualquer chamada. Base 1: 53 → 54. Entrou 1 `nao_reconhecido`
(falha no próprio step do `final_answer`). Plataforma continua 16/19, mas um caso mudou de motivo: a falha estava no
step final, e a regra antiga o contava por um final de **outra** chamada. Base 2 (máquina 2, 02/10; `drill_down.py
silenciosas` e `audit_recompute9`): 20 → **24**. As 4 a mais são falhas no próprio step do `final_answer`: 1 de
plataforma (16 → 17/22) e **3 de `json_invalido`** (0 → 3/86). Nenhum final de outra chamada. Pela regra antiga, o
`audit_recompute9` dá exatamente o 20/116 publicado.

**Leitura dos casos — base 2 (plano 4.1b, máquina 2, 02/10; [assistido], 6 casos escolhidos, não sorteados).**

| Casos | O `final_answer` usa o dado que faltou? | De onde veio a resposta |
|---|---|---|
| 3 de `plataforma` (as 3 calculadoras) | **não** (0/3) | 1 não precisava do dado; 2 vieram de outra ferramenta |
| os 3 de `json_invalido` (falha e final no mesmo step) | **não** (0/3) | a resposta **declara a falha** — não omite, não inventa |

**0/6 sucessos falsos confirmados.** O [4] é um teto frouxo: ele conta como candidato tanto a resposta que achou o dado
por outro caminho quanto a **falha declarada** (a tarefa termina dizendo que não conseguiu). Essa terceira categoria
fica entre o sucesso e o sucesso falso, e o [4] não a separa. Com isso, "o risco à resposta está na plataforma" fica
como **hipótese não confirmada**, e não como achado, até uma medida melhor: o 4.1c (o retorno da ferramenta no
`txt_vrvl_locl`) e o S5 (sucesso em três níveis). Na base 1, os casos ainda não foram lidos.

**Base 2 fechada (05/10): nenhum sucesso falso confirmado.** A leitura ampliada de 04/10 cobriu os 20 candidatos de
plataforma e de JSON inválido: em 0 a resposta usou o dado que faltou (15 não, 2 indeterminados; nos 15, 10 não
precisavam do dado e 4 o pegaram de outra ferramenta). A regra determinística pelo estado final das variáveis
(`investigacao_achados.py` E, rodada 2) achou a resposta **declarando a falha em 24 de 24** candidatos; o único marcado
"sucesso falso provável" foi lido e não era. Na base 2, então, o candidato a sucesso falso é quase sempre **falha
declarada** — e o desfecho precisa de dois eixos (usou o dado? declarou a falha?), não de categorias exclusivas (plano
4.1c). Livro-razão, Etapa 10d.

**Leitura dos números:** o que vale nas duas bases é o contraste entre `plataforma` (quase sempre termina sem a ferramenta ter
funcionado: 84% e 77%) e `json_invalido` (quase nunca: 0% e 3% — em geral o agente refaz a chamada e acerta; nos 3
casos da base 2, a falha e o `final_answer` estão no mesmo bloco). O grupo argumento do agente não tem padrão
entre as bases (73% × 2/6) — "o erro do agente se recupera" **não** vale como regra. É teto: a conferência no caso dos
16 de plataforma de cada base é o plano 4.1b.

## 6 · A forma do argumento no `json_invalido`

| `busca_obf`, forma do 1º argumento | Base 1 | Base 2 |
|---|---:|---:|
| `str(dict/lista colado de um retorno impresso)` — gesto do `repr_colado` | 6 | 80 |
| string literal colada de um retorno impresso — gesto do `repr_colado` | 0 | 6 |
| `json.dumps(...)` ou variável devolvida por outra ferramenta | 0 | 0 |

**Leitura:** o dono é o agente, nas duas bases: ele cola o print do `puxa_doc_decisao` (`{"anteriores": [{"resultado":
…, "resumo": …}]}`) em vez de passar a variável. É o mesmo gesto do `U_repr_colado` (base 1: 6 erros; base 2: **18** em 18 execuções, só
RoteadorCivel — conferido na triagem de 02/10; o "7" antigo era o recorte do Ajuste 2.2) — no
canal silencioso, e na base 2 ~12× maior que no visível. Destino: memória (a lição do `repr_colado` estendida) **e**
aviso à plataforma (o tipo `(str)` de `textos_decisoes` convida ao `str(...)`).

**Na consolidação (Ajuste 12, 04/10)** a unidade conta os dois canais:

| `U_repr_colado` | Base 1 | Base 2 |
|---|---:|---:|
| ocorrências visíveis | 6 | 18 |
| ocorrências silenciosas (cascata × unidade) | 6 | 86 |
| **consolidada** — ocorrências · execuções | **12 · 12** | **104 · 104** [conferido, 05/10] |
| meses · papéis | 4 · 2 | 4 · 1 |
| decisão | candidata (igual) | candidata (igual) |

Base 1 [conferido]: notebook de consolidação §14.3 (só esta unidade muda) e `audit_recompute9` bloco G (0
divergências). Base 2: passo 2b do prompt da rodada 2.

Base 1, as outras formas (todas as 120 silenciosas): o gesto colado aparece também em 4 falhas de argumento do agente,
1 de plataforma e 1 não reconhecida; `json.dumps` aparece em 2 de plataforma — ali o argumento estava certo e a falha é
da ferramenta, como o grupo diz.

## 7 · Detectores de comportamento

Migrados do §7 do notebook da esteira (01/10), com os mesmos números na base 1. Base 2: recalculados na máquina 2
pela lógica da §13.7 (02/10; o notebook não foi reexecutado inteiro lá).

| Detector | Base 1 | Base 2 | Estado |
|---|---|---|---|
| inventário declarado (união dos papéis) | 90 ferramentas | 116 | — |
| **Result-Ignore** | **103 de 3.053 atribuições (3,4%)** | **203 de 8.661 (2,3%)** | robusto; base 1: 96 dos 103 em chamadas caras ([`02`](02-relatorio-achados.md) §5) |
| **RAC** | 125 repetições redundantes | 350 | sensível à definição (conservador) |
| Reasoning-action mismatch | 45 steps | 23 | **retirado** — só registro |
| Tool-Skip | 10 de 840 execuções (1,2%) | 3 de 1.000 (0,3%) | **provisório** (inventário por papel: roadmap item 5) |
| ferramentas chamadas × declaradas | 80 × 90 | 103 × 116 | — |

São contagens de detector, não falhas confirmadas. O Result-Ignore fica na mesma faixa nas duas bases (2–3%).

## 8 · O que falta

- **Base 2: finalizada (05/10, decisão do Rafael).** `audit_recompute9` com 0 divergências, inclusive a consolidação
  (104 · 104 · 4 · 1); sucesso falso: nenhum confirmado. Fica para a próxima ida à máquina 2 reexecutar os notebooks no
  terminal, com cópia íntegra dos arquivos.
- **4.1b:** base 2 fechada (§5); falta a base 1, que roda aqui com a mesma regra. Medida em dois eixos: plano 4.1c.
- **Aviso à plataforma (4.9):** a ferramenta devolve falha como texto; o passe dict → string JSON entre
  `puxa_doc_decisao` e `busca_obf`.
