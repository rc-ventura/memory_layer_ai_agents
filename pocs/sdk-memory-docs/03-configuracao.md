# Configuração

> Seção: **Documentação** · Página original: `docs/documentacao/configuracao` · [Índice](README.md) · Anterior: [Operações de memória](02-operacoes.md) · Próxima: [Persistência](04-persistencia.md)

Toda a configuração do `memory-sdk` é resolvida em uma estrutura imutável `Config` por instância de `MemoryClient`. Não há estado global — duas instâncias no mesmo processo podem ter configurações independentes.

## Precedência

As camadas são mescladas em ordem (mais alta vence):

1. **Kwargs** passados a `MemoryClient` (via `Config` pré-construído ou `overrides=` em `resolve_config`).
2. **Variáveis de ambiente** `MEMSDK_*` (e `GENAI_PROVIDER` como fallback).
3. **YAMLs** em `.memory/config.yaml` e `.memory/prompts.yaml`.
4. **Defaults** embutidos no pacote (`memory_sdk/config/defaults/`).

## Layout do diretório `.memory/`

A pasta `.memory/` é o **hub local do `memory-sdk`** dentro de um projeto: o SDK concentra ali tudo que precisa para operar — o vector store local do ChromaDB (em `chroma/`, criado automaticamente), o `config.yaml` com a configuração do motor e o `prompts.yaml` com a customização de prompts. Manter esses artefatos em uma única pasta versionável (ou montável como volume) deixa o estado do agente portável: levar `.memory/` para outra máquina é levar todo o contexto necessário, sem caminhos espalhados pelo sistema.

```
seu-projeto/
├── .memory/
│   ├── config.yaml      # engine, providers, importance
│   ├── prompts.yaml     # overlays de judge e responder
│   └── chroma/          # criado automaticamente — vector store
└── ...
```

`MemoryClient(user_id)` (sem args) sobe a árvore de diretórios procurando `.memory/`. Se não achar, cria `./.memory/` no CWD.

Para apontar explicitamente:

```python
client = MemoryClient(user_id="u", config="/caminho/para/.memory")
```

## Configuração do motor (`config.yaml`)

### `persistence`

```yaml
persistence:
  backend: chroma          # único backend implementado hoje
  chroma:
    path: chroma           # relativo ao .memory/ — vira .memory/chroma/
```

`path` aceita absoluto ou relativo. Relativos resolvem contra o `.memory/` descoberto, não contra o CWD.

### `providers`

Seis roles, cada um com `provider` e `model`:

```yaml
providers:
  judge:      { provider: azure_openai, model: gpt-4.1 }
  verifier:   { provider: azure_openai, model: gpt-4.1 }
  conflict:   { provider: azure_openai, model: gpt-4.1 }
  responder:  { provider: azure_openai, model: gpt-4.1 }
  multimodal: { provider: vertex,       model: gemini-2.5-flash }
  embeddings: { provider: azure_openai, model: text-embedding-3-large }
```

| Role | Estágio | Para que serve |
|---|---|---|
| `judge` | 2 | Decide ações de memória (`insert`/`update`/`respond_only`). |
| `verifier` | 3 | Avalia qualidade da extração (faithfulness, hallucination_risk, etc.). |
| `conflict` | 4 | Identifica memórias atuais que contradizem novas inserções. |
| `responder` | 6 | Gera a resposta do agente (apenas em `chat()`). |
| `multimodal` | 0 | Transcreve áudio e descreve imagens. |
| `embeddings` | 1 + writes | Embeddings para busca e armazenamento. |

Provedores aceitos: `azure_openai`, `vertex`, `bedrock`. As credenciais para todos vêm das mesmas variáveis do gateway GenAI — o gateway roteia internamente.

### `importance`

Parâmetros de scoring por categoria. Conceito explicado em [Conceitos → Scoring](07-scoring.md).

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
  gamma: 1.0                           # multiplicador de user_confirmed
  lambda: 1.0                          # multiplicador da penalidade de conflito
  reinforce_distance_threshold: 0.60   # distância máxima para reforço
  reinforce_cooldown_seconds: 600      # cooldown entre reforços
```

## Customização de prompts (`prompts.yaml`)

O `prompts.yaml` é o ponto onde o `memory-sdk` deixa de ser genérico e passa a falar a língua do seu domínio. Os defaults embutidos no SDK assumem **suporte a clientes de corporate banking** — o que significa persona, tom, objetivo do judge e taxonomia de memórias afinados para esse cenário. Aplicações em outros verticais (saúde, jurídico, educação, varejo, telecom, etc.) tipicamente precisam reescrever pelo menos o objetivo e os exemplos das categorias para que o judge classifique bem e o responder responda no tom esperado pelo usuário final.

### Roles customizáveis

Apenas `judge` e `responder` aceitam overlay. Os prompts de `verifier` e `conflict_checker` são internos ao SDK — qualquer chave `verifier:` ou `conflict_checker:` no overlay é rejeitada na validação.

| Role | Campos overlay-friendly |
|---|---|
| `judge` | `system_prompt`, `objective`, `memory_categories` (cada categoria com `description` e `examples`) |
| `responder` | `system_prompt`, `persona`, `tone` |

`system_prompt`, quando declarado, substitui o prompt-base inteiro daquele role. Os outros campos são *fragmentos* injetados em pontos específicos do prompt-base — geralmente esses fragmentos já cobrem 90% das necessidades de customização.

### Mecânica do overlay

O overlay é **deep-merge** contra os defaults do pacote: declare apenas o que quer sobrescrever; tudo o que não aparece no `prompts.yaml` herda do default.

```yaml
judge:
  system_prompt: |        # opcional — substitui o default inteiro
    ...
  objective: |
    Capture relevant information about the customer during corporate banking
    interactions...
  memory_categories:
    fixed_profile:
      description: "..."
      examples: ["...", "..."]

responder:
  system_prompt: |
    ...
  persona: You are a helpful assistant for corporate banking.
  tone: Professional and direct.
```

### Especialização para um domínio

Mesmo dentro do setor bancário, vale especializar o agente para um **subdomínio específico** — por exemplo, um assistente focado em **produtos de investimento** (renda fixa, fundos, ações, previdência). Os defaults do SDK falam de banking de forma genérica; reescrever o objetivo do judge, os exemplos das categorias e o tom do responder afina o agente para capturar o que importa nesse contexto: perfil de investidor, horizonte, tolerância a risco, posições e movimentos relevantes.

```yaml
judge:
  objective: |
    Capture information relevant to the customer's investment journey —
    investor profile (suitability), risk tolerance, time horizon, financial
    goals, current holdings and recent moves — so future interactions can
    recommend products aligned to the customer's profile and goals.
  memory_categories:
    fixed_profile:
      description: >
        Stable investor data that rarely changes once captured.
      examples:
        - suitability profile (conservative, moderate, aggressive)
        - approximate investable assets bracket
        - declared investment horizon (short, medium, long term)
        - tax residency
    preferences:
      description: >
        Stated preferences that should shape product recommendations.
      examples:
        - asset class preference (fixed income, equities, multimarket funds)
        - preference for ESG / sustainable products
        - tolerance for liquidity lock-up
        - interest in tax-advantaged vehicles (LCI, LCA, debêntures incentivadas)
    events:
      description: >
        Discrete portfolio actions and milestones worth remembering.
      examples:
        - new position opened (e.g., bought CDB until 2027)
        - position closed or rebalanced
        - contribution to private pension (PGBL/VGBL)
        - dividend received above a notable threshold

responder:
  persona: |
    You are a specialist assistant for retail investment products, supporting
    relationship managers in conversations with customers.
  tone: |
    Professional and clear. Be precise with financial figures and product
    names; never give personalized investment advice that bypasses the
    customer's suitability profile.
```

Como o merge é profundo, apenas os campos declarados são sobrescritos: `dynamic_profile`, `experiences` e os demais fragmentos do responder continuam vindo dos defaults. Para ver tudo o que está sendo herdado, consulte o arquivo canônico em `memory_sdk/config/defaults/prompts.yaml` (ver Defaults completos).

> **Nota de transcrição:** a página "Defaults completos" citada aqui não foi fotografada.

## Variáveis de ambiente `MEMSDK_*`

Sobrescrevem o YAML sem precisar editar arquivo. Apenas as variáveis explicitamente setadas vencem; as demais herdam dos defaults.

| Variável | Caminho equivalente | Notas |
|---|---|---|
| `MEMSDK_CHROMA_PATH` | `persistence.chroma.path` | Use absoluto em produção. |
| `MEMSDK_<ROLE>_PROVIDER` | `providers.<role>.provider` | Roles: `JUDGE`, `VERIFIER`, `CONFLICT`, `RESPONDER`, `MULTIMODAL`, `EMBEDDINGS`. |
| `MEMSDK_<ROLE>_MODEL` | `providers.<role>.model` | Idem. |
| `GENAI_PROVIDER` | fallback de `providers.<role>.provider` | Aplicado a roles sem `MEMSDK_<ROLE>_PROVIDER` próprio. |

Fallbacks de provider entre roles (se a variável específica não estiver setada):

- `responder` → `MEMSDK_JUDGE_PROVIDER` → `GENAI_PROVIDER`
- `conflict` → `MEMSDK_VERIFIER_PROVIDER` → `GENAI_PROVIDER`
- `multimodal` → `MEMSDK_JUDGE_PROVIDER` → `GENAI_PROVIDER`

## Configuração programática

### Apontar para um diretório

```python
client = MemoryClient(user_id="u", config="/etc/myapp/.memory")
```

### Construir e injetar `Config`

`Config` é um modelo Pydantic *frozen* que representa a configuração já resolvida. Construa-o diretamente com `Config.model_validate(...)` quando a configuração vem de outra fonte que não o `.memory/` (ex.: parameter store, secrets manager, banco de configuração interno) — `MemoryClient` recebendo um `Config` pula totalmente a resolução de YAML/env e usa o objeto como está.

```python
from memory_sdk import MemoryClient
from memory_sdk.config import Config

cfg = Config.model_validate({
    "persistence": {
        "backend": "chroma",
        "chroma": {"path": "/var/data/memories"},
    },
    "providers": {
        "judge":      {"provider": "azure_openai", "model": "gpt-4.1"},
        "verifier":   {"provider": "azure_openai", "model": "gpt-4.1"},
        "conflict":   {"provider": "azure_openai", "model": "gpt-4.1"},
        "responder":  {"provider": "azure_openai", "model": "gpt-4o"},
        "multimodal": {"provider": "vertex",       "model": "gemini-2.5-flash"},
        "embeddings": {"provider": "azure_openai", "model": "text-embedding-3-large"},
    },
    "prompts": {},                                # vazio → usa defaults
    "importance": { ... },                        # ver seção Importance
})
client = MemoryClient(user_id="u", config=cfg)
```

`Config` tem `extra="forbid"` ligado, então o dict precisa cobrir todos os campos obrigatórios (`persistence`, `providers`, `prompts`, `importance`) — não há merge implícito com defaults. Quando você só quer **sobrescrever alguns caminhos** sem listar a configuração inteira, use a versão com `resolve_config(overrides=...)`:

```python
from memory_sdk import MemoryClient
from memory_sdk.config import resolve_config

cfg = resolve_config(overrides={
    "persistence": {"chroma": {"path": "/var/data/memories"}},
    "providers": {"judge": {"model": "gpt-4o"}},
})
client = MemoryClient(user_id="u", config=cfg)
```

`overrides` é um dict parcial — os caminhos não declarados herdam do resto da pirâmide de precedência. O retorno é um `Config` válido, pronto para passar a `MemoryClient`.
