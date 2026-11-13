# Quickstart

> Seção: **Documentação** · Página original: `docs/documentacao/quickstart` · [Índice](README.md) · Próxima: [Operações de memória](02-operacoes.md)

O `memory-sdk` é um SDK de motor de **memória de longo prazo** para agentes conversacionais em contexto bancário.

Com ele, seu agente passa a lembrar de fatos e informações importantes que o cliente compartilhou em conversas anteriores, proporcionando uma experiência mais fluida e personalizada.

## Instalação

O SDK é distribuído como um pacote Python e pode ser instalado via pip:

```bash
pip install memory-sdk \
    --extra-index-url <índice interno de pacotes 1> \
    --extra-index-url <índice interno de pacotes 2>
```

> **Nota de transcrição:** os endereços dos dois índices internos de pacotes foram omitidos.

## Configuração

O `memory-sdk` possui uma configuração muito **flexível**, permitindo customizar provedores, modelos, importância das memórias, e muito mais.

Porém, o SDK foi desenvolvido para ser usado com o **mínimo de configuração**, exigindo apenas as credenciais do gateway GenAI via variáveis de ambiente:

```bash
GENAI_CLIENT_ID=...
GENAI_CLIENT_SECRET=...
```

## Primeiros passos

Para entender como o SDK pode ser usado, considere o seguinte exemplo:

```python
from dotenv import load_dotenv
from memory_sdk import MemoryClient


# Carrega as credenciais do gateway GenAI do arquivo .env
load_dotenv()

# MemoryClient é a interface principal para uso do motor de memória
client = MemoryClient(user_id="user")

# Exemplo de conversa entre um usuário humano e um agente
messages = [
    {"role": "user", "content": "Meu nome é Bruno e tenho interesse em investimentos."},
]

# Método store_memories extrai memórias a partir da conversa e salva internamente as memórias
client.store_memories(messages)

####### Simulando nova sessão de conversa, sem contexto de curto prazo #######
new_session_messages = [
    {"role": "user", "content": "Boa tarde! Quero ajuda com produtos de investimento."},
]

# Recuperando memórias para enriquecer o contexto da nova sessão de conversa
memories = client.get_relevant_memories(new_session_messages)

print(memories)
# Memórias encontradas:
#
# 1. id=mem_20260520_132537_069769; categoria=fixed_profile; subject_key=name;is_current=yes; previous_memo…
#    text=The user's first name is Bruno.
#    (distance=1.5359; w=10.8328; final_score=10.8328; Registrado em: 2026-06-08)
#
```

> **Nota de transcrição:** a linha `# 1. id=…` estava cortada na borda direita da tela, depois de `previous_memo`.

No exemplo acima:

1. Instanciamos o `MemoryClient` para o usuário identificado como `"user"`. É por meio desse objeto `MemoryClient` que o SDK realiza todo o gerenciamento de memória do Memory SDK para o usuário, como extração, armazenamento e recuperação de memórias.
2. Usamos `store_memories` para armazenar fatos importantes de uma conversa.
   - nesse caso, o motor identifica que 2 memórias podem ser extraídas:
     - o **nome** do usuário
     - e seu **interesse em investimentos**.
3. Sem memória de longo prazo, ao iniciar uma nova sessão, não seria possível saber ter as informações das mensagens anteriores. Usando o método `get_relevant_memories`, obtemos um texto com as memórias do usuário que pode ser utilizado para responder o usuário (por ex, adicionando ao contexto da conversa).

Para saber mais sobre todas as operações oferecidas pelo Memory SDK, consulte [Operações de memória](02-operacoes.md).

### Memory Dashboard

Uma forma prática para testar o Memory SDK é executar o `memory-dashboard`, no terminal:

```bash
memory-dashboard
```

Uma aplicação web será iniciada e estará disponível em `http://localhost:8000`:

> **Figura (captura do dashboard, estado inicial).** Cabeçalho com o logo do SDK e o campo `usuário: demo-user`. Dois painéis:
>
> - **Conversa** (esquerda): "Nenhuma mensagem ainda — inicie a conversa."; caixa "Envie uma mensagem...", botão de microfone e botão **Enviar**; dica: "Enter envia · Shift+Enter quebra linha · arraste uma imagem · clique no microfone para gravar".
> - **Painel de memória** (direita), com as abas **Turno atual** | **Todas memórias**: card **Memórias recuperadas** ("Aguardando primeiro turno...") e card **Memórias salvas** ("Aguardando primeiro turno...").

Para testar o motor, basta conversar com o agente usando a interface de chat. O dashboard exibe, em tempo real, as memórias que estão sendo recuperadas e salvas a cada turno, além de uma visão geral de todas as memórias salvas para o usuário.

> **Figura (captura do dashboard, depois de um turno).**
>
> - **Usuário:** "I'm a data scientist and I'm interested in banking products"
> - **Agente:** "Thank you for sharing your profession and interest. Could you please specify which type of banking products you would like to know more about? For example: credit cards, investments, loans, or business solutions? This way, I can provide information tailored to your needs."
> - **Memórias recuperadas (0):** "Nenhuma memória recuperada neste turno."
> - **Memórias salvas (2):**
>   - `[+] FIXED · declared_profession_or_occupation` — "The user stated that their profession is data scientist (time not specified)." — conf 1.00
>   - `[+] PREF · interest_in_banking_products` — (texto não visível nas fotos)
>
> **Nota de transcrição:** a parte do meio dessa captura não foi fotografada.

## Próximos passos

Para entender melhor como funciona o Memory SDK e aproveitar tudo que o SDK tem a oferecer, consulte o restante desta documentação, organizada em duas seções:

**Documentação** — referência prática de uso do SDK:

- [Operações de memória](02-operacoes.md) — todas as chamadas do `MemoryClient` (`store_memories`, `get_relevant_memories`, `chat`, etc.) e quando usar cada uma.
- [Configuração](03-configuracao.md) — provedores, modelos, parâmetros de scoring, customização de prompts e variáveis de ambiente `MEMSDK_*`.
- [Persistência](04-persistencia.md) — onde as memórias ficam salvas e como apontar para diretórios customizados.

**Conceitos** — como o motor funciona por dentro:

- [Categorias de memória](06-categorias.md) — taxonomia das memórias (perfil fixo, dinâmico, preferências, eventos, experiências).
- [Scoring de importância](07-scoring.md) — como o `W_global` ordena as memórias retornadas.
- [Histórico vinculado e duplicatas](08-historico-duplicatas.md) — encadeamento via `previous_memory_id` e tratamento de duplicatas.
- [Pipeline do motor](09-pipeline.md) — os estágios 0–6 que cada turno percorre.
- [Ações do judge](10-acoes-judge.md) — `insert`, `update` e `respond_only` decididas pelo judge.
- [Guarda temporal](11-guarda-temporal.md) — clarificação automática de datas ambíguas entre turnos.
- [Pré-processamento multimodal](12-multimodal.md) — como anexos (imagens, PDFs) entram no pipeline.
