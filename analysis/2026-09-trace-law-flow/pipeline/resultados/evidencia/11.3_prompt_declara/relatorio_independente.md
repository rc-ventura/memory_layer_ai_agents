# Relatório independente — 11.3_prompt_declara

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.3_prompt_declara/` por leitura direta dos arquivos `crus/*.json`, usando `casos.csv` apenas como índice da amostra. O objetivo é verificar **o que o bloco `def ferramenta(...)` do system prompt declara sobre o retorno de cada ferramenta** e se:

1. a chave pedida pelo agente aparece nesse bloco;
2. as chaves reais observadas no 11.2 aparecem ou não nele;
3. o bloco está **errado**, **omisso** ou **compatível** com o retorno real.

Como complemento, foi usado `uv run python pipeline/drill_down.py ferramenta <nome>` para conferir se o bloco visto no caso é representativo das variantes da ferramenta no trace inteiro.

Guidance consultado para interpretar a análise:

- `docs/`06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.7 e §1.8;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Resumo executivo

1. A pasta contém **3 casos**, um por ferramenta cujo schema foi lido no 11.2: `get_available_documents`, `validar_quebra_sigilo` e `extrair_evidencias`.
2. Em `validar_quebra_sigilo`, o bloco do prompt **declara explicitamente um schema que não bate com o retorno real**: fala em `quebra_sigilo` / `motivo`, enquanto o runtime devolve `vazamento_sigilo` / `justificativa`.
3. Em `extrair_evidencias`, o bloco do prompt também **declara explicitamente um schema diferente do retorno real**: fala em `informacoes_evidencias`, enquanto o runtime devolve `dados_evidencias`.
4. Em `get_available_documents`, o bloco do prompt **não declara chave nenhuma de saída**; ele diz apenas que a tool retorna documentos e um resumo. Aqui o problema não é “prompt errado”, mas **prompt omisso**.
5. Portanto, a auditoria independente confirma a distinção importante do 11.3: há ferramentas em que o prompt **contradiz** o retorno real, e outras em que o prompt apenas **não o especifica**.

## Corpus auditado

| exec_id | ferramenta | chaves reais levadas do 11.2 |
|---|---|---|
| `1eed2931…` | `get_available_documents` | `hashDocumento; iuDocsId; iuDocsTenantId; metadado; nomeMetadado; result; tipoExtracaoOcr; valorMetadado` |
| `d3d64194…` | `validar_quebra_sigilo` | `justificativa; vazamento_sigilo` |
| `95344639…` | `extrair_evidencias` | `dados_evidencias; data_inicio_atraso; final_cartao; nome_contrato; numero_contrato` |

## Método

Para cada caso, a checagem independente:

- abriu o `ActionStep` alvo no cru;
- extraiu literalmente o bloco `def ferramenta(...)` do `system` prompt desse step;
- confrontou esse texto com:
  - a chave pedida pelo agente no erro;
  - as chaves reais observadas no retorno (conforme 11.2);
- verificou, via `drill_down.py ferramenta <nome>`, se o bloco visto no caso era representativo do traço inteiro daquela ferramenta.

## Resultado por ferramenta

| ferramenta | o bloco declara sobre o retorno | a chave pedida aparece? | as chaves reais aparecem? | leitura independente |
|---|---|---|---|---|
| `get_available_documents` | não há seção `Outputs:` nem chave explícita; o texto fala em “returns a list of documents and a summary of the kinds of documents” | não se aplica ao índice `0`; nenhuma chave de retorno é fixada | `result` não aparece; `hashDocumento`, `metadado`, `tipoExtracaoOcr` etc. também não | **prompt omisso** |
| `validar_quebra_sigilo` | `{"quebra_sigilo": "SIM" ou "NÃO", "motivo": "justificativa"}` | sim: `quebra_sigilo` aparece como chave declarada | `vazamento_sigilo` não aparece; `justificativa` aparece apenas como valor textual de `motivo`, não como chave de retorno | **prompt errado / contraditório** |
| `extrair_evidencias` | `{"informacoes_evidencias": [<lista de informações extraídas>]}` | sim: `informacoes_evidencias` aparece como chave declarada | `dados_evidencias` não aparece; as subchaves reais também não | **prompt errado / contraditório** |

## Achados principais

### 1. `validar_quebra_sigilo` declara um contrato que o runtime não cumpre

No cru auditado, o bloco da ferramenta diz literalmente que o output será:

```json
{"quebra_sigilo": "SIM" ou "NÃO", "motivo": "justificativa"}
```

Já o retorno real observado no Passo 2 é:

```json
{"vazamento_sigilo": "NAO", "justificativa": "..."}
```

A divergência é dupla:

- muda a chave booleana principal (`quebra_sigilo` → `vazamento_sigilo`);
- muda a chave do texto explicativo (`motivo` → `justificativa`).

A checagem com `drill_down.py ferramenta validar_quebra_sigilo` mostrou **2 variantes** do bloco no trace inteiro, mas a diferença é só de quebra de linha; o contrato declarado é o mesmo nas duas.

### 2. `extrair_evidencias` também declara um contrato incompatível com o retorno real

No cru auditado, o bloco declara:

```json
{
  "informacoes_evidencias": [...]
}
```

Mas o retorno real observado no 11.2 vem como:

```json
{"dados_evidencias": [...]} 
```

Aqui o agente também parece estar seguindo o prompt ao pedir `informacoes_evidencias`, e o runtime devolve outro nome de campo. A checagem com `drill_down.py ferramenta extrair_evidencias` encontrou **1 única variante** do bloco, estável nas execuções observadas.

### 3. `get_available_documents` não contradiz o real; ele simplesmente não o especifica

No caso de `get_available_documents`, o bloco lido no cru não traz um schema em formato de chaves. Ele diz apenas, em inglês, que a ferramenta retorna documentos e um summary.

A checagem com `drill_down.py ferramenta get_available_documents` encontrou **5 variantes** do bloco ao longo do trace, mas nenhuma delas declara a chave `result`. Portanto:

- não há evidência de que o prompt tenha mandado usar explicitamente `result` ou `docs[0]`;
- também não há evidência de que ele tenha prometido um schema incompatível com o retorno real;
- o problema aqui é melhor descrito como **omissão de contrato de saída**.

### 4. O 11.3 acerta ao separar “prompt errado” de “prompt omisso”

Esta distinção, que é central nos racionais e no procedimento de validação, ficou bem sustentada no cru:

- **prompt errado / contraditório**: `validar_quebra_sigilo`, `extrair_evidencias`;
- **prompt omisso**: `get_available_documents`.

Essa separação é importante porque leva a interpretações diferentes do comportamento do agente:

- quando o prompt declara uma chave errada, o agente pode estar apenas obedecendo ao contrato que recebeu;
- quando o prompt não declara chave nenhuma, o erro já depende mais da inferência que o agente faz sobre a estrutura do retorno.

## Conclusões finais

1. A pasta `11.3_prompt_declara/` sustenta bem a alegação de que o system prompt não falha sempre do mesmo jeito: às vezes ele **contradiz** o runtime; às vezes ele só **não o detalha**.
2. A auditoria independente confirma que `validar_quebra_sigilo` e `extrair_evidencias` têm blocos de documentação que declaram chaves diferentes das observadas no retorno real.
3. Também confirma que `get_available_documents` não declara o envelope `result`, de modo que o erro associado a essa ferramenta não deve ser descrito como “prompt diz a chave errada”, e sim como “prompt não especifica a chave de saída”.
4. A distinção analítica adotada no 11.3, portanto, ficou **validada por leitura direta do cru**.
