# Operações de memória

> Seção: **Documentação** · Página original: `docs/documentacao/operacoes` · [Índice](README.md) · Anterior: [Quickstart](01-quickstart.md) · Próxima: [Configuração](03-configuracao.md)

O `memory-sdk` expõe um conjunto reduzido de operações para lidar com memória de longo prazo. Todas elas são acessadas pelo objeto `MemoryClient`, que é o ponto de entrada do SDK e gerencia o ciclo de vida das memórias para um único `user_id`.

Toda operação que recebe `messages` espera o mesmo formato usado pelo padrão de chat de LLMs — uma lista de dicionários com `role` (`user` ou `assistant`) e `content`. **O caller é dono dessa lista** e a passa em toda chamada; o SDK não acumula histórico de conversa internamente.

```python
from memory_sdk import MemoryClient

client = MemoryClient(user_id="user")
```

Para customizar provedores, modelos e parâmetros de scoring, ver [Configuração](03-configuracao.md).

## Sumário das operações

| Operação | Assinatura | O que faz | Retorno |
|---|---|---|---|
| `store_memories` | `store_memories(messages)` | Extrai e persiste memórias a partir da última fala do usuário (estágios 0–5). Não gera resposta. | `dict` com `executed_actions` e `execution_summary` |
| `get_relevant_memories` | `get_relevant_memories(messages)` | Recupera memórias relevantes para a última fala (estágio 1). Não chama judge nem grava nada. | `str` — bloco de texto pronto para injeção no contexto |
| `get_all_memories` | `get_all_memories()` | Devolve todas as memórias armazenadas para o `user_id` corrente. | `list[dict]` com `id`, `content`, `metadata` |
| `mem_count` | `mem_count()` | Quantidade total de memórias persistidas para o `user_id` corrente. | `int` |
| `delete_memory` | `delete_memory(memory_id)` | Remove um registro específico pelo seu `id`. | — |
| `clear_memories` | `clear_memories()` | Apaga todas as memórias do `user_id` corrente e limpa estado de clarificação pendente. | — |
| `chat` | `chat(messages, attachments=None)` | Pipeline completo (estágios 0–6): extrai, persiste e gera resposta do agente. Coordena clarificação temporal entre turnos. | `tuple[str, dict]` — `(reply, decision)` |

## Detalhes de cada operação

### `store_memories(messages) -> dict`

Extrai e persiste memórias a partir da última fala do usuário em `messages`. Roda os estágios 0–5 do pipeline (pré-processamento multimodal, retrieve, judge, verifier, conflict checker, writes), mas **não gera resposta** — útil quando o agente já tem outro caminho para responder ao usuário e quer apenas atualizar a memória.

Retorna um dicionário com:

- `executed_actions` — lista das ações executadas no turno (`insert`, `update` ou `respond_only`), com categoria, `subject_key`, score do verifier e indicação de conflito.
- `execution_summary` — resumo textual das ações para inspeção rápida.

```python
messages = [
    {"role": "user", "content": "Meu nome é Bruno e tenho interesse em investimentos."},
]
result = client.store_memories(messages)
```

### `get_relevant_memories(messages) -> str`

Recupera as memórias mais relevantes para a última fala do usuário e devolve um bloco de texto pronto para ser injetado no contexto de outro modelo. Roda o estágio 1 (retrieve per-categoria + reranking por `W_global`) e nada mais — não chama judge nem grava nada.

```python
context = client.get_relevant_memories(messages)
```

A ordem das memórias é definida pelo score `W_global`, não pela similaridade de embedding. Detalhes em [Scoring de importância](07-scoring.md) e [Pipeline → Retrieve](09-pipeline.md#1-retrieve).

### `get_all_memories() -> list[dict]`

Devolve todas as memórias armazenadas para o `user_id` corrente. Útil para auditoria e para reconstruir o histórico vinculado de um tópico (ver [Histórico vinculado](08-historico-duplicatas.md)).

Cada item do retorno tem `id`, `content` e `metadata` (categoria, `subject_key`, `is_current`, `previous_memory_id`, `mention_count`, etc.).

### `mem_count() -> int`

Quantidade total de memórias persistidas para o `user_id` corrente.

### `delete_memory(memory_id)`

Remove um registro específico pelo seu `id`. Não atualiza cadeias de `previous_memory_id` apontando para ele — use com cuidado se quiser preservar a integridade do histórico.

### `clear_memories()`

Apaga **todas** as memórias do `user_id` corrente e limpa o estado de clarificação temporal pendente. Tipicamente útil em testes e em fluxos de "esqueça tudo sobre mim".

### `chat(messages, attachments=None) -> tuple[str, dict]`

Pipeline completo (estágios 0–6). Além de extrair e persistir memórias, executa o **responder** para gerar a resposta do agente ao usuário.

Retorna uma tupla `(reply, decision)`:

- `reply` — string com a resposta do agente.
- `decision` — dicionário com `assistant_reply`, `actions` (executadas) e `retrieved_memories` (memórias usadas como contexto).

O parâmetro opcional `attachments` recebe uma lista de dicts (com `mime` e dados em base64) e ativa o estágio 0 multimodal — ver [Pré-processamento multimodal](12-multimodal.md).

```python
reply, decision = client.chat(messages)
```

`chat()` também coordena, entre turnos, a clarificação disparada pela [Guarda temporal](11-guarda-temporal.md). Quando o motor detecta uma data ambígua, a operação retorna uma pergunta de confirmação em vez de gravar a memória; na chamada seguinte, o cliente injeta o contexto pendente automaticamente.

## Notas operacionais

- **Isolamento por usuário.** Cada `MemoryClient` opera em um único `user_id`. Instâncias diferentes no mesmo processo não interferem entre si — cada uma tem seu próprio repositório namespaced.
- **Caller é dono do histórico.** O SDK não acumula a conversa: passe sempre a lista completa `messages` que faz sentido para o turno atual. Apenas a última fala do usuário é usada como input principal; as anteriores entram como histórico de curto prazo nos prompts.
- **Único bit de estado per-instância.** `chat()` mantém internamente um flag `_pending_temporal` para orquestrar a clarificação de data entre turnos. Esse flag é consumido na chamada seguinte e zerado ao chamar `clear_memories()`.

## Exemplo end-to-end

```python
from dotenv import load_dotenv
from memory_sdk import MemoryClient

load_dotenv()
client = MemoryClient(user_id="user")

# Turno 1 — apenas extrai e armazena.
client.store_memories([
    {"role": "user", "content": "Meu nome é Bruno e moro em São Paulo."},
])

# Turno 2 — nova sessão; recupera memórias para enriquecer o contexto.
new_session = [
    {"role": "user", "content": "Pode me sugerir agências próximas?"},
]
context = client.get_relevant_memories(new_session)

# Turno 3 — pipeline completo, gerando resposta com memórias em contexto.
reply, decision = client.chat([
    {"role": "user", "content": "Acabei de me mudar para Curitiba."},
])
print(reply)
print(f"{client.mem_count()} memórias persistidas no total")
```
