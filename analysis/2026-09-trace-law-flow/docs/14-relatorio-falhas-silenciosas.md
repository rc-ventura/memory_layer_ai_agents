# Relatório das falhas silenciosas — o balde invisível, por base

**Para que serve este documento:** os números do balde invisível em cada base, e o que eles querem dizer. Mesmo papel
do [`02-relatorio-achados.md`](02-relatorio-achados.md), só para o erro que não vira exceção. O **porquê** de cada
medida está em [`13-racionais-falhas-silenciosas.md`](13-racionais-falhas-silenciosas.md); como repetir numa base nova,
em [`15-procedimento-falhas-silenciosas.md`](15-procedimento-falhas-silenciosas.md). Base 1: saída do notebook
[`../pipeline/falhas_silenciosas.ipynb`](../pipeline/falhas_silenciosas.ipynb) (01/10). Base 2: fotos da máquina 2 do
`drill_down.py silenciosas` e `silenciosas --forma busca_obf` (01/10) — as mesmas funções; o notebook ainda não rodou lá.

---

## TL;DR

- **~90% das falhas de ferramenta são invisíveis à exceção** nas duas bases (93% e 87%): a ferramenta devolve a falha
  como texto, o step fica com `error: null`.
- **Elas passam sem rastro:** em 89–91% dos casos, o mesmo papel não tem nenhum erro com exceção nos 3 steps seguintes.
- **As memórias de contrato de retorno não nascem delas:** só 0–9% de `U_tipo_retorno` / `U_campo_inexistente` vêm logo
  depois de uma falha silenciosa. Continuam memória candidata.
- **O risco à resposta está na plataforma:** 16/19 e 16/22 das falhas de plataforma terminam em `final_answer` sem a
  ferramenta ter funcionado (candidatos a sucesso falso, teto).
- **O `json_invalido` é o `repr_colado` no canal silencioso:** 6/6 e 86/86 são o agente colando o print do
  `puxa_doc_decisao` no `busca_obf`. Na base 2, o canal silencioso é ~12× o visível (86 × 7). Nunca vira sucesso falso
  (0/6, 0/86): o custo é retrabalho.

## 1 · O funil e a escala

| | Base 1 | Base 2 |
|---|---:|---:|
| falhas de ferramenta com exceção (ficam no balde visível) | 9 | 20 |
| **falhas silenciosas** | **120** | **134** |
| % silenciosas entre as falhas de ferramenta | 93% | 87% |
| execuções · meses | 90 · 10 | 124 · 7 |
| papéis · ferramentas | 13 · 22 | — · 18 |
| sobreposição visível × invisível (por step) | 0 | — |

Base 1: os 120 estão em 119 steps (um step com duas ferramentas falhando).

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
| `plataforma` | **16/19 (84%)** | **16/22 (73%)** |
| `argumento_do_agente` | 30/41 (73%) | 2/6 |
| `nao_reconhecido` | 7/9 | 2/2 |
| `json_invalido` | **0/6** | **0/86** |
| **total** | **53/75** | **20/116** |

**Leitura:** o que vale nas duas bases é o contraste entre `plataforma` (quase sempre termina sem a ferramenta ter
funcionado) e `json_invalido` (nunca: o agente refaz a chamada e acerta). O grupo argumento do agente não tem padrão
entre as bases (73% × 2/6) — "o erro do agente se recupera" **não** vale como regra. É teto: a conferência no caso dos
16 de plataforma de cada base é o plano 4.1b.

## 6 · A forma do argumento no `json_invalido`

| `busca_obf`, forma do 1º argumento | Base 1 | Base 2 |
|---|---:|---:|
| `str(dict/lista colado de um retorno impresso)` — gesto do `repr_colado` | 6 | 80 |
| string literal colada de um retorno impresso — gesto do `repr_colado` | 0 | 6 |
| `json.dumps(...)` ou variável devolvida por outra ferramenta | 0 | 0 |

**Leitura:** o dono é o agente, nas duas bases: ele cola o print do `puxa_doc_decisao` (`{"anteriores": [{"resultado":
…, "resumo": …}]}`) em vez de passar a variável. É o mesmo gesto do `U_repr_colado` (base 1: 6 erros; base 2: 7) — no
canal silencioso, e na base 2 ~12× maior que no visível. Destino: memória (a lição do `repr_colado` estendida) **e**
aviso à plataforma (o tipo `(str)` de `textos_decisoes` convida ao `str(...)`). A unidade passa a contar os dois canais
na consolidação (plano 4.2b).

Base 1, as outras formas (todas as 120 silenciosas): o gesto colado aparece também em 4 falhas de argumento do agente,
1 de plataforma e 1 não reconhecida; `json.dumps` aparece em 2 de plataforma — ali o argumento estava certo e a falha é
da ferramenta, como o grupo diz.

## 7 · Detectores de comportamento (base 1)

Migrados do §7 do notebook da esteira (01/10), com os mesmos números:

| Detector | Base 1 | Estado |
|---|---|---|
| inventário declarado (união dos papéis) | 90 ferramentas | — |
| **Result-Ignore** | **103 de 3.053 atribuições (3,4%)** | robusto; 96 dos 103 em chamadas caras ([`02`](02-relatorio-achados.md) §5) |
| **RAC** | 125 repetições redundantes | sensível à definição (conservador) |
| Reasoning-action mismatch | 45 steps | **retirado** — só registro |
| Tool-Skip | 10 de 840 execuções (1,2%) | **provisório** (inventário por papel: roadmap item 5) |
| ferramentas chamadas × declaradas | 80 × 90 | — |

Base 2: a rodar (o notebook novo, na máquina 2).

## 8 · O que falta

- **Base 2:** rodar o notebook (`falhas_silenciosas.ipynb`) — funil por step, sobreposição, detectores da §13.7.
- **4.1b:** conferir no caso os 16 candidatos a sucesso falso de plataforma de cada base.
- **4.2b:** a consolidação — o `json_invalido` colado entra na `U_repr_colado`.
- **Aviso à plataforma (4.9):** a ferramenta devolve falha como texto; o passe dict → string JSON entre
  `puxa_doc_decisao` e `busca_obf`.
