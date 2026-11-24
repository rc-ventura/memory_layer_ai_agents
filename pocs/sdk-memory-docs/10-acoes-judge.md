# Ações do judge

> Seção: **Conceitos** · Página original: `docs/conceitos/acoes` · [Índice](README.md) · Anterior: [Pipeline do motor](09-pipeline.md) · Próxima: [Guarda temporal](11-guarda-temporal.md)

No estágio 2 do pipeline, o **judge LLM** lê a fala do usuário, o histórico de curto prazo e as memórias recuperadas, e emite uma lista de **ações**: o que deve ser feito com a memória do usuário neste turno. Esta página descreve o formato dessas ações, a semântica de cada tipo e como elas são validadas antes de seguir para os estágios seguintes.

## O JSON emitido

O judge produz um único objeto JSON com a lista de ações:

```
{
  "actions": [
    {
      "type": "insert" | "update" | "respond_only",
      "text": "string",
      "feedback": "short string",
      "category": "fixed_profile" | "dynamic_profile" | "preferences" | "events" | "experiences" | null,
      "subject_key": "snake_case" | null,
      "target_memory_id": "string" | null
    }
  ]
}
```

Um turno pode emitir **várias ações simultaneamente** — por exemplo, uma fala como "Acabei de me mudar para Curitiba e acabei de abrir uma reclamação sobre meu cartão" pode gerar um `update` (cidade atual) + um `insert` (evento de reclamação) na mesma decisão.

## Os três tipos

### `insert`

Cria uma nova memória. Usado quando a fala traz um fato novo que ainda não existe na base — ou quando existe, mas em uma categoria onde cada ocorrência é única (`events`, `experiences`).

Campos relevantes:

- `text` — o fato em primeira pessoa do extrator, mono-tópico.
- `category` — uma das cinco fixas. Ver [Categorias de memória](06-categorias.md).
- `subject_key` — identificador estável em `snake_case` para o tópico (`name`, `current_city`, `card_dispute_2026`, etc.). Quando o judge vê uma memória recuperada com o mesmo tópico, ele é instruído a **reaproveitar exatamente esse `subject_key`** — evita variantes (`current_city` vs. `cidade_atual` vs. `address`).

No estágio 5, antes de gravar, o motor checa duplicatas (texto > 0.85 de similaridade contra a memória mais próxima da mesma categoria) e processa os conflitos retornados pelo conflict checker. Detalhes em [Histórico vinculado e duplicatas](08-historico-duplicatas.md).

### `update`

Substitui uma memória atual por uma nova versão, demovendo a anterior para `is_current = "no"` e linkando via `previous_memory_id`. Preferido quando a fala atualiza um fato já capturado — mudança de cidade, de estado civil, de preferência.

Campos adicionais:

- `target_memory_id` — id explícito da memória a ser substituída, quando o judge sabe qual é. Quando não, o motor usa uma **cascata de busca**:
  1. Pelo `target_memory_id` (se emitido e o `subject_key` confere).
  2. Por filtro `categoria + subject_key + is_current = "yes"`.
  3. Por similaridade — top-5 da categoria, filtrando por `subject_key`; sem `subject_key`, exige similaridade textual mínima de 0.25.

Se nenhuma das três encontrar um nó anterior, o `update` vira na prática um `insert` isolado.

### `respond_only`

Sinaliza que **nenhuma memória deve ser gravada** neste turno. Usado quando:

- O assunto é sensível e bloqueado por guardrail (política, religião, orientação sexual, drogas — ver [Categorias → Tópicos sensíveis bloqueados](06-categorias.md#tópicos-sensíveis-bloqueados)).
- A fala não traz informação nova relevante (saudação, agradecimento, confirmação trivial).
- O judge decidiu deferir a captura para um turno futuro (e.g. esperando uma clarificação).

`text` e `category` ficam vazios; `feedback` carrega a justificativa para inspeção.

## Validação e normalização

Antes de chegar aos estágios seguintes, o motor passa as ações por uma camada de parsing pura (`pipeline/actions.py`):

- **Tolerância a markdown fences.** Saídas como ```` ```json {...} ``` ```` são limpas antes do parse — o judge ocasionalmente envolve a resposta mesmo quando o prompt pede JSON cru.
- **Normalização de `category`.** Strings fora das cinco categorias fixas viram `dynamic_profile`. Comparação é case-insensitive.
- **Normalização de `subject_key`.** Lowercase, caracteres não-alfanuméricos viram `_`, sem `_` nas pontas. Vazio vira `general_note`.
- **Filtragem de ações inválidas.** `type` desconhecido é descartado. `insert`/`update` sem `text` é descartado. `respond_only` é mantido mesmo sem `text`.
- **Clamp de scores.** Valores numéricos do verifier (estágio 3) são forçados ao intervalo `[0, 1]` com fallback `0.5` em caso de parse falho.

## Múltiplas ações por turno

O judge é instruído a decompor falas compostas. Exemplo:

"Mudei de São Paulo para Curitiba e abri uma reclamação sobre cobrança indevida no meu cartão."

Saída esperada:

```json
{
  "actions": [
    {
      "type": "update",
      "text": "The user moved from São Paulo to Curitiba.",
      "feedback": "Update of dynamic profile: current city.",
      "category": "dynamic_profile",
      "subject_key": "current_city",
      "target_memory_id": "mem_..."
    },
    {
      "type": "insert",
      "text": "The user opened a charge dispute on their credit card.",
      "feedback": "New banking event captured.",
      "category": "events",
      "subject_key": "card_charge_dispute",
      "target_memory_id": null
    }
  ]
}
```

Cada ação é depois verificada pelo verifier (qualidade) e pelo conflict checker (contradições com memórias atuais) **em paralelo** — ver [Pipeline → Verifier e Conflict checker](09-pipeline.md#3-verifier-paralelo-a-4).
