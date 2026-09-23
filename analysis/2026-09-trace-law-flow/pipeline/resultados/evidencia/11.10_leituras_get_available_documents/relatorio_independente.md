# Relatório independente — 11.10 Leituras de get_available_documents

> ⚠️ **Desatualizado desde 23/09/2026 — refazer.** Esta auditoria verificou a amostra de casos escolhida quando
> o `mes` vinha de `anomesdia` (o lote de corte). Hoje o `mes` vem de `dat_hor_inio_exeo` (quando a execução
> rodou) e as regras de escolha, que ordenam por mês, trocaram parte dos casos desta pasta. Não citar como
> verificação da amostra atual. → `docs/04-roadmap.md` (Agora) · `docs/03-procedimento-validacao.md` §1.12

Data: 2026-09-18

## Escopo

Auditoria da oitava evidência externa da análise nº2 (`U_contrato_dict`: "o caller não respeita o
contrato de retorno da ferramenta — lê a chave errada"). A §11.10 estende a contagem da nº2 ao
**universo completo** de leituras do retorno de `get_available_documents`, em vez dos 91 steps
com erro da contagem original. O resultado publicado afirma:

- 635 papéis declaram a ferramenta (todos `ConversationAgent`); **597 leituras** subsequentes
  rastreadas do retorno.
- **4 ocorrências silenciosas** de leitura com chave errada, sem guarda e sem `try/except`
  (`175cd9f2…`, `26e300f1…`, `910fde1e…`, `a47d6e3b…`) — 9 leituras registradas na tabela, sobre
  esses 4 steps únicos.
- **1 guarda de chave fantasma** (`15f6ad52…`): `if 'documents' in pasta_docs` — a chave testada
  não existe no schema real (`result` é a chave verdadeira) e o ramo `else` descarta os
  documentos reais.
- Das 597 leituras: 320 reais/desprotegidas, 1 real/protegida, 88 reais/guardadas, 110
  erradas/desprotegidas (todas com erro → subconjunto conhecido), 78 erradas/guardadas.
- Dos 93 registros de leitura errada+desprotegida+erro ("visível conhecido"): cobrem a massa dos
  91 steps de erro da nº2.
- **Nenhuma das 5 ocorrências confirmadas** (4 silenciosas + 1 guarda fantasma) produziu
  `DEGENERADO`, literal `None`/`null` ou resposta final em forma de dict no `managerAgent`.
- A análise **não muda** `destino` (memory) nem `impact` (null) da nº2 — só atualiza
  `validation.analise_funda`. Há uma retratação formal (§1.11 de `03-procedimento-validacao.md`):
  a exploração anterior olhou 3 casos escolhidos a dedo, usou uma lista de palavras-chave
  inventada sobre a saída intermediária do `ConversationAgent` e sugeriu dano à resposta —
  conclusão que a análise exaustiva não sustenta.

A auditoria reabre os 8 crus, verifica os 64 trechos salvos, **recomputa as 597 leituras
independentemente** sobre o CSV bruto e confere a tabela publicada célula a célula.

## Resumo executivo

Todos os números **conferem por recomputação independente — diff zero** contra
`leituras_universo_completo.csv` (597 linhas idênticas, incluindo flags `real`/`guardado`/
`protegido`/`tem_erro`/`visivel_conhecido`). As 4 ocorrências silenciosas, a guarda fantasma e os
0/5 em todos os três detectores de dano de resposta foram verificados no cru. A retratação de
§1.11 está correta: os mecanismos estruturais são reais e exhaustivamente contados; dano medido
na resposta final, zero.

Duas nuances de precisão registradas (nenhuma muda o veredito): (a) as 4 "leituras silenciosas"
são mecanisticamente heterogêneas — só `910fde1e…` é o ".get sem plano B" canônico; (b) a
reconciliação "93 leituras ≈ 91 steps de erro" publicada é aritmeticamente frouxa — são 93
leituras sobre **85 steps únicos**, e 11 erros da nº2 envolvem a **chave real** em profundidade
ou forma errada (outra face do mesmo mecanismo, não "chave errada").

## Corpus auditado

| item | valor |
|------|-------|
| derivados | 8 `derivados/*.json`, 9 linhas em `casos.csv` (uma tem motivo fundido) |
| crus | 8 `crus/<exec_id>.json` |
| trechos | 64 `trechos_do_cru` — **64/64 conferem com o cru** |
| tabelas | `leituras_universo_completo.csv` (597 linhas), `casos.csv`, contagens de `ocorrencias` |
| universo | 635 papéis `(exec_id, role)` `ConversationAgent` que declaram a ferramenta |

## Método

Sem reutilizar o código do notebook. Reimplementação independente (`csv.DictReader` +
`json.loads` + `ast`):

1. Varredura das 641 linhas do CSV bruto; `json.loads` nas linhas `ConversationAgent` com
   `get_available_documents` no memo → 635 papéis declarantes.
2. Por papel: toda chamada `get_available_documents(` em `code_action` marca a variável que
   recebe o retorno; toda leitura posterior (`Subscript`, `Attribute`, `.get(...)`, `for x in
   var`, `x in var`, comparações) sobre essas variáveis é uma **leitura** — 597 no total.
3. Flags por leitura: `real` (chave é `result` ou acesso em profundidade a partir dela vs. chave
   não presente no schema real), `guardado` (a leitura está sob um teste `if`/`IfExp` que menciona
   a variável), `protegido` (dentro de `try/except`), `tem_erro` (o step tem `Exception` em
   `observations`), `visivel_conhecido` (errada + desprotegida + com erro → o subconjunto já
   coberto pela nº2).
4. Veredito por ocorrência: leitura errada + sem guarda + sem proteção + **sem erro** =
   silenciosa; `x in var` com `x` não real sobre var de retorno = guarda de chave fantasma.
5. Dano na resposta: o `final_answer`/`action_output` do **`managerAgent`** da execução (não o
   intermediário `ConversationAgent`) é testado por três detectores — `DEGENERADO`, literal
   `None`/`null`, e resposta em forma de dict/objeto.
6. Integridade: 64 `trechos_do_cru` conferidos nó a nó contra os crus; a tabela publicada
   comparada célula a célula contra a recomputação.

## Resultado por componente

### 1. Universo — CONFIRMADO com diff zero

| medida | publicado | recomputado |
|--------|-----------|-------------|
| papéis declarantes | 635 | **635** (todos `ConversationAgent`) |
| leituras rastreadas | 597 | **597 — tabela idêntica, 0 divergências** |
| real=F, guardado=F, protegido=F | 110 | 110 |
| real=F, guardado=T, protegido=F | 78 | 78 |
| real=T, guardado=F, protegido=F | 320 | 320 |
| real=T, guardado=F, protegido=T | 1 | 1 |
| real=T, guardado=T, protegido=F | 88 | 88 |
| leituras erradas-desprotegidas-com-erro | 93 | **93** em 85 steps únicos |
| leituras erradas-desprotegidas-com-erro **fora** do conhecido | 8 | 8 |
| **ocorrências silenciosas (steps únicos)** | **4** | **4** — mesmos (exec,role,idx) |
| **guardas de chave fantasma** | **1** | **1** — única no trace inteiro |

### 2. As 4 ocorrências silenciosas — CONFIRMADAS, com nuance mecanística

Verificação direta do `code_action` + `observations` de cada step nos crus:

| ocorrência | mecanismo real (do cru) | por que é silenciosa |
|------------|------------------------|----------------------|
| `910fde1e…` idx0 | `.get("documents")` sobre o retorno-dict, sem plano B | retorna `None` → usado adiante; nenhum erro |
| `175cd9f2…` idx1 | `documents_result[0]` | o retorno era **string JSON** (63.548 chars — `U_tipo_retorno`), não dict: `str[0]` devolve `'{'` em silêncio |
| `26e300f1…` idx0 | `resultado[0]` | idem — **str** de 13.547 chars; `str[0]` devolve `'{'` |
| `a47d6e3b…` idx0 | `docs_list` recebe retorno; o acesso errado fica em `if docs_list is None:` | **fallback morto** — o ramo nunca executa; a leitura errada está lá mas não roda |

> **Nuance**: o rótulo "leitura silenciosa" descreve o veredito do detector (chave errada, sem
> guarda, sem proteção, sem erro), mas os 4 casos se dividem em 3 mecanismos distintos — só 1/4
> é o `.get` canônico. Dois são a interseção com `U_tipo_retorno` (retorno-string permite
> `x[0]` silencioso); um é código morto. A contagem está certa; a leitura mecanística é mais
> rica que o rótulo.

### 3. A guarda de chave fantasma — CONFIRMADA literalmente

`15f6ad52…` idx0, verificado no cru:

```python
if 'documents' in pasta_docs:
    docs_to_analyze = pasta_docs['documents']
else:
    docs_to_analyze = apoio_docs   # <- ramo sempre tomado
```

`'documents'` nunca existe no schema real (`result`) → o teste é sempre falso → os documentos
reais são **descartados por inteiro** em favor de `apoio_docs`. É a única guarda `x in var` com
`x` não-real em todo o trace (recomputado: `linhas_g = 1`).

### 4. Dano na resposta final — 0/5 confirmado

O `final_answer` do `managerAgent` de cada uma das 5 execuções foi testado:

| ocorrência | resposta final manager | DEGENERADO | None/null | forma-dict |
|------------|------------------------|------------|-----------|------------|
| `175cd9f2…` | texto entregue | 0 | 0 | 0 |
| `26e300f1…` | texto entregue | 0 | 0 | 0 |
| `910fde1e…` | texto entregue (324 chars) | 0 | 0 | 0 |
| `a47d6e3b…` | texto entregue | 0 | 0 | 0 |
| `15f6ad52…` | texto entregue | 0 | 0 | 0 |

> **Observação**: em `910fde1e…` o `ConversationAgent` intermediário entregou um payload de erro
> de "não encontrei documentos" — a falha foi visível na camada intermediária, mas em redação
> normal (não `DEGENERADO`). O veredito "0 dano medido" se sustenta nos três detectores
> validados sobre o `managerAgent`; este caso mostra por que `DEGENERADO` sozinho sub-detecta
> (a célula do notebook já o complementava com None/null e forma-dict).

### 5. Reconciliação com os 91 erros da nº2 — CONFIRMADA com precisão fina

Os 93 registros de leitura errada+desprotegida+com-erro cobrem **85 steps únicos** de erro. Os
**11 erros `U_contrato_dict` restantes** foram inspecionados um a um: são acessos com a **chave
real** `result` em profundidade/forma errada — `docs["result"][0][0]` (itera um doc como lista),
iteração direta do dict, `AttributeError`/`TypeError` correlatos. Ou seja: a mesma família de
mecanismo (o caller não respeita o contrato — forma/profundidade em vez de chave), mas não a
classe "chave errada" que a tabela rastreia. A afirmação publicada "93 ≈ 91+2" é frouxa na
aritmética (93 leituras / 85 steps + 11 erros de outra forma = os 91 steps) mas correta na
substância: as duas populações são faces do mesmo mecanismo.

### 6. Integridade — CONFIRMADA

- **64/64** `trechos_do_cru` conferem com o nó `cru` apontado.
- `leituras_universo_completo.csv`: recomputação independente produziu tabela **idêntica**
  (597 linhas, diff zero em todas as colunas).
- `casos.csv` (9 linhas / 8 steps únicos — `175cd9f2…` idx3 funde "silenciosa" + "primeiro da
  classe") confere com os grupos do universo.

### 7. Retratação de §1.11 — CONFIRMADA

A exploração anterior (3 casos escolhidos a dedo, palavras-chave inventadas sobre saída
intermediária do `ConversationAgent`, "2 confirmados" com sugestão de dano) foi substituída pela
contagem exaustiva + detectores sobre o `managerAgent`. A conclusão correta — mecanismos reais e
exaustivamente contados, **zero** dano medido — está agora sustentada pela evidência. `impact`
permanece `null` e `destino` permanece `memory`, como registra a análise.

## Ressalvas e limitações

1. **Heterogeneidade dos 4 silenciosos** — o rótulo único cobre `.get` canônico (1), `x[0]` em
   retorno-string (2) e código morto (1). Quem ler "4 leituras silenciosas" deve entender 4
   *vereditos do detector*, não 4 instâncias do mesmo bug.
2. **Aritmética da reconciliação** — "93 ≈ 91" publicado deveria ler "93 leituras sobre 85 steps
   + 11 erros de forma/profundidade com a chave real = os 91 steps de erro da nº2".
3. **O que esta análise não estabelece**: groundedness/completude factual das respostas — os
   três detectores medem forma (degeneração, nulidade, dict), não correção. A questão de se
   descartar os documentos reais (guarda fantasma) empobreceu a resposta permanece em aberto e
   não pode ser respondida por inspeção estrutural.

## Conclusões finais

1. **597 leituras, diff zero** — a recomputação independente reproduz a tabela publicada
   integralmente; todas as contagens de flags conferem.
2. **4 ocorrências silenciosas + 1 guarda fantasma — CONFIRMADAS** no cru, incluindo a leitura
   literal de `if 'documents' in pasta_docs`.
3. **0/5 dano medido na resposta final** — os três detectores (DEGENERADO, None/null,
   forma-dict) sobre o `managerAgent` falham em disparar nos 5 casos; a retratação da leitura
   exploratória anterior está correta.
4. **64/64 trechos conferem** — integridade evidência↔cru total.
5. **`impact=null`, `destino=memory` mantidos** — a §11.10 atualiza só `analise_funda` da nº2,
   o que está de acordo com o que os dados mostram: mecanismo real, dano não medido.
6. **Duas notas de precisão** (heterogeneidade mecanística dos 4 silenciosos; aritmética da
   reconciliação 93/85/11) — registradas para o próximo rerun, sem alterar o veredito.

## Referências

- `resultados/evidencia/11.10_leituras_get_available_documents/` — crus, derivados,
  `leituras_universo_completo.csv`, `casos.csv`
- `unidades_memoria.json` → `n2` → `validation.analise_funda` (o resultado auditado)
- `docs/03-procedimento-validacao.md` §1.11 (a retratação da exploração anterior)
- `docs/07-relatorio-mineracao-unidades-n2-n10.md` §6.3 (a narrativa auditada)
- Notebook §11.10 (a célula que materializou a evidência)
- `audit/scripts/audit_recompute8.py` — script desta recomputação independente
