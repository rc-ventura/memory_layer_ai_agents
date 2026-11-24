# Scoring de importância

> Seção: **Conceitos** · Página original: `docs/conceitos/scoring` · [Índice](README.md) · Anterior: [Categorias de memória](06-categorias.md) · Próxima: [Histórico vinculado e duplicatas](08-historico-duplicatas.md)

Toda memória recebe um score `W_global` que combina seis fatores. Esse score é o que o motor usa para **rankear memórias na recuperação** — não a similaridade de embedding, que serve apenas para escopar candidatos top-K dentro de cada categoria.

A consequência prática: uma memória semanticamente próxima da query mas estagnada e velha **perde** para uma memória menos próxima mas importante e fresca.

## A fórmula

```
W_global = B × F × Q × U × C × R
```

| Fator | Nome | Como é calculado |
|---|---|---|
| B | Base weight | Peso fixo da categoria (configurável). |
| F | Frequency | `1 + α × (1 − e^(−mentions / β))` — saturação suave. |
| Q | Extractor confidence | `q_m` produzido pelo verifier no estágio 3, clampado em `[0.1, 1.0]`. |
| U | User confirmation | `1 + γ × user_confirmed` — sobe via reforço de recuperação. |
| C | Conflict penalty | `1 / (1 + λ × conflict_count)` — desce a cada conflito detectado. |
| R | Recency | `2^(−dias_desde_last_mentioned / half_life)` — decaimento exponencial. |

## Defaults por categoria

```yaml
importance:
  b:
    fixed_profile: 5.0
    dynamic_profile: 3.0
    preferences: 4.0
    events: 1.0
    experiences: 2.0
  half_life_days:
    fixed_profile: 10.0
    dynamic_profile: 8.0
    preferences: 10.0
    events: 2.0
    experiences: 5.0
  alpha:
    fixed_profile: 0.3
    dynamic_profile: 0.4
    preferences: 0.6
    events: 0.8
    experiences: 0.5
  beta:
    fixed_profile: 3.0
    dynamic_profile: 3.0
    preferences: 3.0
    events: 2.0
    experiences: 3.0
  gamma: 1.0
  lambda: 1.0
```

A intuição:

- `fixed_profile` tem **B alto e half-life longo**: nome do cliente importa muito e demora a "envelhecer".
- `events` tem **B baixo e half-life curto**: a contestação de ontem é relevante; a de seis meses atrás, nem tanto.
- α mais alto em `events`/`preferences` faz cada nova menção pesar mais — útil quando repetição sinaliza importância.

## Os fatores em detalhe

### B — peso base

Constante por categoria, vem direto de `importance.b` no YAML. Valores típicos entre 1 e 5. Mexer aqui muda o ranking global mais agressivamente que qualquer outro fator.

### F — frequência com saturação

```
F = 1 + α × (1 − exp(−mention_count / β))
```

`mention_count` cresce a cada vez que a memória é (re)inserida (duplicatas) ou recuperada com distância pequena (reforço — ver abaixo). A função satura em `1 + α`, então memórias com 50 menções não dominam memórias com 10.

### Q — confiança do extrator

Calculada pelo verifier (estágio 3) a partir de oito dimensões:

| Dimensão | Peso |
|---|---|
| `faithfulness` | 0.25 |
| `scope_completeness` | 0.10 |
| `category_fit` | 0.10 |
| `subject_fit` | 0.10 |
| `temporal_fit` | 0.15 |
| `polarity_fit` | 0.10 |
| `atomicity` | 0.10 |
| `1 − hallucination_risk` | 0.10 |

Mais penalidades:

- `hallucination_risk > 0.20` → `q_m ≤ 0.60`.
- `faithfulness < 0.70` → `q_m ≤ 0.55`.
- `temporal_fit < 0.60` → `q_m ≤ 0.60`.
- `polarity_fit < 0.60` → `q_m ≤ 0.60`.
- `category_fit < 0.50` ou `subject_fit < 0.50` → `q_m ≤ 0.50`.
- `atomicity < 0.60` → `q_m ≤ 0.55`.

O resultado é clampado em `[0.1, 1.0]` antes de virar Q. Memórias extraídas com baixa confiança nunca somem da base, mas perdem poder na recuperação.

### U — confirmação do usuário

```
U = 1 + γ × user_confirmed
```

`user_confirmed ∈ [0.0, 1.0]`. Memórias começam em `1.0` (assumimos boa-fé do extrator). O fator existe para que memórias confirmadas explicitamente pelo usuário possam ganhar boost adicional via mecanismos futuros.

### C — penalidade de conflito

```
C = 1 / (1 + λ × conflict_count)
```

`conflict_count` é incrementado pelo conflict checker (estágio 4) sempre que uma nova memória contradiz a antiga. Memórias com muitos conflitos viram redundantes/desatualizadas, e o motor as reduz no ranking sem precisar deletá-las.

### R — recência

```
R = 2 ^ (−dias_desde_last_mentioned / half_life_days[categoria])
```

Decai pela metade a cada `half_life_days`. Atualizada toda vez que `last_mentioned_at` muda — em INSERT inicial, duplicata reincidente, UPDATE, ou reforço por recuperação.

## Recuperação per-categoria

Quando você chama `get_relevant_memories()`, o motor **não** roda uma única busca top-K. Ele faz uma busca por categoria:

1. Para cada uma das 5 categorias, busca top-K candidatos no ChromaDB com `where={"categoria": <cat>}`.
2. K é proporcional ao peso B da categoria — categorias mais importantes contribuem com mais candidatos.
3. Para cada candidato, recalcula `W_global` ao vivo (recência muda com o tempo).
4. Reranqueia por `W_global` e seleciona os top da categoria.
5. Junta as seleções de todas as categorias e ordena de novo por `W_global`.

Isso garante que cada categoria tenha representatividade no contexto retornado, mesmo que uma categoria tenha embeddings consistentemente mais "longe" da query.

## Reforço de recuperação

Para cada memória recuperada com **distância de embedding ≤ `reinforce_distance_threshold`** (default `0.60`) e cujo cooldown (default 600s) já expirou, o motor:

- incrementa `mention_count`
- atualiza `last_mentioned_at` para agora
- seta `user_confirmed = 1.0`

Efeito: memórias frequentemente relevantes se reforçam sozinhas. Memórias sem trato perdem importância pelo decaimento de R sem ganho compensador.
