# Relatório independente — 11.5_estabilidade

> ⚠️ **Desatualizado desde 23/09/2026 — refazer.** Esta auditoria verificou a amostra de casos escolhida quando
> o `mes` vinha de `anomesdia` (o lote de corte). Hoje o `mes` vem de `dat_hor_inio_exeo` (quando a execução
> rodou) e as regras de escolha, que ordenam por mês, trocaram parte dos casos desta pasta. Não citar como
> verificação da amostra atual. → `docs/04-roadmap.md` (Agora) · `docs/03-procedimento-validacao.md` §1.12

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.5_estabilidade/` por leitura direta dos arquivos `crus/*.json`, usando `casos.csv` apenas como índice da amostra. O objetivo é verificar se a **forma do retorno** das ferramentas candidatas permanece estável ao longo dos meses com erro, sempre **por nível da estrutura**, e se a única divergência registrada (`campos a mais`) se sustenta no cru.

Guidance consultado para interpretar a análise:

- `docs/`06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.9;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Resumo executivo

1. A pasta contém **11 casos**: o primeiro caso de cada mês em cada nível observado, mais o caso cuja forma difere da comum.
2. A auditoria independente confirmou estabilidade em **todos os níveis representados**, com **uma única variação** já registrada pelo notebook: um caso de ago/2026 em `get_available_documents` com **dois campos adicionais** nos documentos internos (`iuDocsId`, `iuDocsTenantId`).
3. Essa variação **não remove** nenhuma das chaves da forma comum e, no caso auditado, os dois campos extras aparecem **nulos em todos os documentos** do retorno.
4. `validar_quebra_sigilo` permaneceu com a mesma forma `{justificativa, vazamento_sigilo}` em abr, mai e jun/2026.
5. Assim, a leitura independente confirma o veredito publicado: **estável** nas duas ferramentas candidatas, com ressalva de leitura estrita em `get_available_documents` por causa dos campos extras de ago/2026.

## Corpus auditado

| ferramenta | nível | meses na amostra | casos |
|---|---|---|---:|
| `get_available_documents` | `{result}` — retorno inteiro | dez/2025, abr–ago/2026 | 7 |
| `get_available_documents` | `{hashDocumento, metadado, tipoExtracaoOcr}` — documento | jun/2026 | 1 |
| `validar_quebra_sigilo` | `{justificativa, vazamento_sigilo}` | abr–jun/2026 | 3 |

## Método

Para cada caso, a auditoria independente leu o `ActionStep` alvo e extraíu, a partir da própria mensagem de erro:

- as chaves de topo do objeto impresso;
- quando havia envelope `result`, as chaves do primeiro documento dentro de `result[0]`.

A comparação foi feita por nível, como define o procedimento de validação:

- retorno inteiro de `get_available_documents` (`{result}`);
- documento interno de `get_available_documents` (`{hashDocumento, metadado, tipoExtracaoOcr}`);
- retorno inteiro de `validar_quebra_sigilo` (`{justificativa, vazamento_sigilo}`).

## Resultado por caso

| exec_id | mês | ferramenta / nível | comparação registrada | leitura no cru | veredito independente |
|---|---|---|---|---|---|
| `1eed2931…` | 2025-12 | `get_available_documents` / `{result}` | idêntica | topo `['result']`; documentos com `hashDocumento`, `metadado`, `tipoExtracaoOcr` | **confere** |
| `0cd5e2c0…` | 2026-04 | `get_available_documents` / `{result}` | idêntica | mesma forma do caso de dez/2025 | **confere** |
| `0572af0b…` | 2026-05 | `get_available_documents` / `{result}` | idêntica | mesma forma | **confere** |
| `008d142f…` | 2026-06 | `get_available_documents` / `{result}` | idêntica | mesma forma | **confere** |
| `124ca0ef…` | 2026-07 | `get_available_documents` / `{result}` | idêntica | mesma forma | **confere** |
| `575122c5…` | 2026-08 | `get_available_documents` / `{result}` | idêntica | mesma forma ainda presente em ago/2026; documentos com só as 3 chaves usuais | **confere** |
| `aa3de754…` | 2026-08 | `get_available_documents` / `{result}` | campos a mais | topo segue `['result']`; documentos trazem `hashDocumento`, `metadado`, `tipoExtracaoOcr` **mais** `iuDocsId` e `iuDocsTenantId` | **confere** |
| `299694d3…` | 2026-06 | `get_available_documents` / documento | idêntica | o objeto impresso já é um documento com `hashDocumento`, `metadado`, `tipoExtracaoOcr` | **confere** |
| `d3d64194…` | 2026-04 | `validar_quebra_sigilo` | idêntica | topo `['justificativa', 'vazamento_sigilo']` | **confere** |
| `1be966e7…` | 2026-05 | `validar_quebra_sigilo` | idêntica | mesma forma | **confere** |
| `21a4fa6c…` | 2026-06 | `validar_quebra_sigilo` | idêntica | mesma forma | **confere** |

## Achados principais

### 1. A forma comum de `get_available_documents` realmente se repete nos meses observados

Nos sete casos de nível `{result}`, a estrutura comum aparece de forma estável:

- chave de topo: `result`;
- dentro de `result[0]`, lista de documentos;
- documentos com `hashDocumento`, `metadado`, `tipoExtracaoOcr`.

A presença dessa mesma forma em dez/2025, abr, mai, jun, jul e ago/2026 sustenta bem a leitura de estabilidade temporal.

### 2. A divergência de ago/2026 é localizada e limitada a “campos a mais”

No caso `aa3de754…`, a auditoria independente confirmou a divergência registrada:

- os documentos continuam trazendo as 3 chaves da forma comum;
- aparecem ainda `iuDocsId` e `iuDocsTenantId`;
- no cru auditado, **todos** esses campos extras estão `None` nos 18 documentos do retorno.

Isso reforça a interpretação publicada de que o caso representa **variação entre execuções**, não ruptura do schema básico usado pela memória.

### 3. `validar_quebra_sigilo` é estável nos meses com erro

Os três casos auditados — abr, mai e jun/2026 — trazem exatamente a mesma forma de topo:

```json
{"justificativa": str, "vazamento_sigilo": str}
```

Não apareceu nenhuma variação de chave ou tipo nessa amostra mensal.

### 4. A leitura “estrita” e a leitura “adotada” continuam bem separadas

A leitura independente confirma a separação metodológica do relatório:

- **leitura adotada**: `get_available_documents` segue estável porque os campos da forma comum continuam presentes, e a divergência é só de campos adicionais simples;
- **leitura estrita**: ago/2026 difere da forma comum por ter campos extras.

Ou seja, a distinção não é retórica; ela corresponde a um padrão real no cru.

## Conclusões finais

1. A pasta `11.5_estabilidade/` sustenta bem a alegação de que o schema das ferramentas candidatas é estável nos meses observados, desde que comparado por nível da estrutura.
2. A única divergência registrada — `aa3de754…`, ago/2026, `get_available_documents` com `iuDocsId`/`iuDocsTenantId` — foi confirmada no cru e é compatível com a classificação “campos a mais”.
3. `validar_quebra_sigilo` permaneceu idêntica nos três meses auditados.
4. O balanço independente desta pasta é favorável ao veredito publicado: **estável**, com ressalva estrita apenas para os campos extras de ago/2026 em `get_available_documents`.
