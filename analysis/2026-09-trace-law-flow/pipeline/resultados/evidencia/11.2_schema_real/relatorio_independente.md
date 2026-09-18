# Relatório independente — 11.2_schema_real

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.2_schema_real/` por leitura direta dos arquivos `crus/*.json`, usando `casos.csv` apenas como índice da amostra. O objetivo é verificar se a **forma do objeto que a mensagem de erro imprime** — chaves e tipos em nível relevante — confere com o que a análise 11.2 registrou, e se a chave pedida pelo agente de fato não existe nesse objeto.

Guidance consultado para interpretar a análise:

- `docs/`06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.7;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Resumo executivo

1. A pasta contém **10 casos**: o primeiro erro de cada forma distinta de objeto por unidade e função, incluindo a categoria `objeto não lido da mensagem`.
2. Em **6/10** casos, a mensagem de erro traz um objeto parseável no padrão `Could not index <objeto> with <chave>`.
3. Nesses 6/6 casos parseáveis, a leitura independente do cru confirma a forma registrada em `casos.csv`, e a chave pedida pelo agente **não** existe no objeto observado.
4. Em **4/10** casos, a própria mensagem não entrega um objeto parseável no formato acima; nesses casos, o rótulo `objeto não lido da mensagem` continua correto.
5. Portanto, a assunção central do 11.2 — de que é possível extrair do erro o schema real do retorno quando o objeto é impresso, e marcar separadamente quando ele não é — ficou sustentada nesta amostra.

## Corpus auditado

| contagem | valor |
|---|---:|
| casos totais | 10 |
| objeto parseável na mensagem | 6 |
| `objeto não lido da mensagem` | 4 |

Ferramentas representadas:

| ferramenta | n |
|---|---:|
| `get_available_documents` | 5 |
| `validar_quebra_sigilo` | 1 |
| `extrair_evidencias` | 1 |
| `meta_map` | 1 |
| `não resolvido` | 2 |

## Método

Para cada caso, a auditoria independente abriu o `ActionStep` alvo (`idx` do `casos.csv`) e leu:

- o trecho de `error.message` do próprio step;
- a chave pedida pelo agente na indexação que falha;
- o objeto efetivamente impresso na exceção, quando presente.

Quando a mensagem vinha no formato `Could not index <objeto> with '<chave>'`, o objeto foi tratado como fonte do schema real observado. Quando a exceção era de outro tipo (`Object ... has no attribute get`, `Empty DataFrame`, etc.), o caso foi mantido como `objeto não lido da mensagem`.

## Resultado por caso

| exec_id | ferramenta | chave pedida | forma registrada em `casos.csv` | leitura no cru | veredito independente |
|---|---|---|---|---|---|
| `1eed2931…` | `get_available_documents` | `0` | `{result: [[{hashDocumento, metadado, tipoExtracaoOcr}] | {<campo>: {<valor>: int}}]}` | a mensagem mostra o envelope `{'result': [[...], ...]}`; a chave/index `0` não existe no topo do objeto | **confere** |
| `d3d64194…` | `validar_quebra_sigilo` | `quebra_sigilo` | `{justificativa: str, vazamento_sigilo: str}` | a mensagem explicita `{'vazamento_sigilo': 'NAO', 'justificativa': ...}`; `quebra_sigilo` está ausente | **confere** |
| `915e77a7…` | `não resolvido` | `<colunas>` | `(objeto não lido da mensagem)` | a exceção relevante é de colunas de `DataFrame` vazio, não um `Could not index <objeto>` parseável | **confere** |
| `b63284df…` | `get_available_documents` | `nom_docm_juri_mode` | `{nomeMetadado: str, valorMetadado: str}` | o objeto impresso é um item de metadado com só `nomeMetadado` e `valorMetadado`; `nom_docm_juri_mode` não é chave desse dicionário | **confere** |
| `df4aac6a…` | `não resolvido` | `<attr>` | `(objeto não lido da mensagem)` | a exceção relevante é `Object hashDocumento has no attribute get`; o objeto não vem serializado em formato parseável | **confere** |
| `299694d3…` | `get_available_documents` | `0` | `{hashDocumento: str, metadado: [...], tipoExtracaoOcr: str}` | o objeto impresso já é um documento individual com `hashDocumento`, `metadado`, `tipoExtracaoOcr`; o índice `0` não existe nesse nível | **confere** |
| `3f44a68b…` | `get_available_documents` | `<attr>` | `(objeto não lido da mensagem)` | a exceção é `Object hashDocumento has no attribute get`; o runtime não entrega um dicionário parseável no corpo da mensagem | **confere** |
| `95344639…` | `extrair_evidencias` | `informacoes_evidencias` | `{dados_evidencias: [{data_inicio_atraso, final_cartao, nome_contrato, numero_contrato}]}` | a mensagem explicita `{'dados_evidencias': [...]}`; a chave pedida segue o prompt, mas não existe no retorno real | **confere** |
| `cd794f02…` | `meta_map` | `<attr>` | `(objeto não lido da mensagem)` | novamente a exceção relevante é `Object hashDocumento has no attribute get`; sem objeto parseável na mensagem | **confere** |
| `aa3de754…` | `get_available_documents` | `0` | `{result: [[{hashDocumento, iuDocsId, iuDocsTenantId, metadado, tipoExtracaoOcr}] | {<campo>: {<valor>: int}}]}` | a mensagem mostra o mesmo envelope `{'result': [[...]]}` e, dentro dos documentos, os campos adicionais `iuDocsId` / `iuDocsTenantId`; o índice `0` não existe no topo | **confere** |

## Achados principais

### 1. Quando o objeto aparece na mensagem, o 11.2 o lê corretamente

Os seis casos parseáveis se distribuem em formas realmente distintas e coerentes com a análise publicada:

- envelope inteiro de `get_available_documents` (`result` no topo);
- documento individual de `get_available_documents` (`hashDocumento`, `metadado`, `tipoExtracaoOcr`);
- item de metadado (`nomeMetadado`, `valorMetadado`);
- retorno de `validar_quebra_sigilo` (`vazamento_sigilo`, `justificativa`);
- retorno de `extrair_evidencias` (`dados_evidencias`);
- variante tardia do envelope de `get_available_documents` com `iuDocsId` e `iuDocsTenantId` nos documentos internos.

Em todos eles, a chave pedida pelo agente é incompatível com o objeto efetivamente impresso.

### 2. `objeto não lido da mensagem` é uma categoria metodológica necessária

Quatro casos desta pasta não trazem objeto parseável na mensagem. Eles não são contraexemplos do método; são exatamente o motivo de a categoria existir.

Os tipos de erro encontrados aqui foram:

- `Object hashDocumento has no attribute get`;
- indexação de colunas em `Empty DataFrame`.

Nessas situações, insistir em “reconstruir” um objeto real a partir do texto do erro seria inferência além do que o runtime entregou. O notebook foi correto em separar esses casos.

### 3. A regra “a chave pedida não existe no objeto” passa neste recorte

Nos seis casos em que o objeto é visível na mensagem, a auditoria independente confirma o ponto central do Passo 2: a chave/index pedido pelo agente **não está** no objeto que o runtime acabou de imprimir.

O balanço independente aqui é:

- **6/6 parseáveis: forma confirmada e chave ausente**;
- **4/4 não-parseáveis: categoria `objeto não lido` confirmada**.

## Conclusões finais

1. A pasta `11.2_schema_real/` sustenta a alegação de que o Passo 2 está lendo corretamente o schema real quando ele aparece no próprio texto do erro.
2. A distinção entre “objeto lido da mensagem” e “objeto não lido da mensagem” não parece arbitrária; ela coincide com diferenças reais no formato das exceções do cru.
3. A amostra independente não encontrou nenhum caso em que a forma registrada em `casos.csv` contradissesse o objeto efetivamente mostrado pelo runtime.
4. O resultado independente desta pasta é, portanto, favorável à assunção metodológica do 11.2.
