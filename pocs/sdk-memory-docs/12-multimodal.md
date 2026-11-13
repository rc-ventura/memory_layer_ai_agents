# Pré-processamento multimodal

> Seção: **Conceitos** · Página original: `docs/conceitos/multimodal` · [Índice](README.md) · Anterior: [Guarda temporal](11-guarda-temporal.md)

O **estágio 0** do pipeline transforma anexos não-textuais (áudio, imagem) em descrição textual rica antes que o restante do motor toque na fala do usuário. O resto do pipeline trabalha apenas com texto — qualquer informação de uma foto ou de um áudio precisa estar fielmente representada como string para ser recuperada, julgada, verificada e gravada.

## Quando roda

Apenas dentro de `chat()`, e apenas quando o parâmetro `attachments` é uma lista não-vazia. Sem anexos, o estágio 0 é uma passagem direta: `enriched_text = user_text`.

A operação `store_memories()` do `MemoryClient` **não expõe `attachments`** hoje — o ponto de entrada para fluxos multimodais é `chat()`.

## Formato esperado dos anexos

`attachments` é uma lista de dicionários com duas chaves:

| Chave | Descrição |
|---|---|
| `mime` | Mime type do anexo. Áudio: começa com `audio/` (e.g. `audio/mp3`, `audio/wav`). Imagem: qualquer outro `image/*` (e.g. `image/png`, `image/jpeg`). |
| `data_b64` | Conteúdo binário do anexo codificado em base64. |

```python
import base64

with open("foto.png", "rb") as f:
    data_b64 = base64.b64encode(f.read()).decode()

attachments = [
    {"mime": "image/png", "data_b64": data_b64},
]

reply, decision = client.chat(
    [{"role": "user", "content": "O que diz neste documento?"}],
    attachments=attachments,
)
```

Múltiplos anexos no mesmo turno são suportados — o motor detecta presença de áudio e/ou imagem e monta instruções específicas para cada modalidade.

## O que o LLM produz

O motor envia uma única chamada ao LLM `multimodal` com um prompt construído a partir dos tipos detectados:

### Áudio

"Transcribe the audio EXACTLY and IN FULL (do not summarize). Then add a section `[AUDIO ANALYSIS]` noting: detected language, tone of voice (e.g. calm, anxious, cheerful, irritated, hesitant), emotional state, speech pace, and any notable paralinguistic cues (sighs, laughter, pauses)."

A saída esperada combina **transcrição literal** + um bloco `[AUDIO ANALYSIS]` com idioma detectado, tom de voz, estado emocional, ritmo da fala e cues paralinguísticos. Esses sinais são úteis para o judge entender contexto (e.g. uma reclamação dita em tom irritado pesa diferente de uma narrada em tom neutro).

### Imagem

"Describe the image in RICH DETAIL. Include: main subject, visible text/numbers, colors, objects, people (approximate age, expression, posture if visible), setting/environment, brands/logos, document type if applicable, and any other relevant visual information. Do not omit details."

Para fotos de documentos, a saída inclui números e textos visíveis — o que viabiliza extrair, por exemplo, dados de um comprovante ou de um boleto que o cliente compartilhou.

## Como entra no resto do pipeline

A saída do estágio 0 é concatenada à fala do usuário com um marcador explícito, e essa string composta é o `enriched_text` consumido pelos estágios seguintes:

```
<texto digitado pelo usuário>

[ATTACHMENT CONTENT]
<transcrição/descrição produzida pelo LLM multimodal>
```

Quando não há texto digitado (usuário enviou só o anexo), o marcador é omitido e a saída do LLM vira a fala efetiva do turno.

A partir daí, **nada muda**: a busca por embeddings, o judge, o verifier, o conflict checker e o responder enxergam apenas texto. O `[ATTACHMENT CONTENT]` aparece nos prompts e no histórico de curto prazo como qualquer outra fala.

## Falha grácil

Se a chamada ao LLM `multimodal` lançar exceção, o estágio **não interrompe o turno**:

- Se o usuário também digitou um texto, o pipeline segue com o texto puro.
- Se o turno era só anexo, o pipeline segue com um marcador `[multimodal preprocess failed; attachments: <mimes>]` no lugar — o judge tem contexto suficiente para emitir um `respond_only` ou pedir nova tentativa.

## Provedor padrão e configuração

Por padrão o motor usa **Vertex / `gemini-2.5-flash`** para o estágio multimodal — o gateway GenAI roteia internamente, e a credencial é a mesma usada pelos demais roles. Para trocar o provedor ou o modelo:

```yaml
# .memory/config.yaml
providers:
  multimodal:
    provider: vertex
    model: gemini-2.5-flash
```

Variáveis de ambiente equivalentes: `MEMSDK_MULTIMODAL_PROVIDER` e `MEMSDK_MULTIMODAL_MODEL`. Ver [Configuração](03-configuracao.md#variáveis-de-ambiente-memsdk_) para a tabela completa de roles.
