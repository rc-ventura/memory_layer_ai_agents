---
type: methodology
title: "Análises Multi-Base: Três Extrações, um Método"
description: Como o projeto analisa três extrações independentes do mesmo trace de produção — as diferenças de formato e de máquina entre as bases, o livro-razão que registra cada ajuste do método, os módulos compartilhados de leitura/adaptação e a suite de testes sintéticos.
tags: [trace-analysis, multi-base, etl-pipeline, compliance-boundary, adjustment-ledger, observed-mode]
verified:
  - by: openwiki/0.6.0
    at: 2026-10-09T17:09:54.387Z
sources:
  - id: openwiki-source-ad06e2a4dd2b5ea3fcfeb3f3
    resource: repo://analysis/2026-09-trace-law-flow-second/README.md
  - id: openwiki-source-42c209f90bfa14372ad8f8aa
    resource: repo://analysis/2026-09-trace-law-flow/audit/README.md
  - id: openwiki-source-569719c5da69b38f321cdb6a
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/base_pipeline.py
  - id: openwiki-source-e252a5d791f4958574b4088a
    resource: repo://analysis/2026-10-trace-law-flow-third/docs/01-racionais.md
  - id: openwiki-source-4380ebe15eaa84879ea087cb
    resource: repo://analysis/2026-10-trace-law-flow-third/docs/05-pedido-queries.md
  - id: openwiki-source-ae8741ef52ecef7f0ae8a584
    resource: repo://analysis/2026-10-trace-law-flow-third/pipeline/executar.py
  - id: openwiki-source-94c25a5250b636767039ae69
    resource: repo://analysis/2026-10-trace-law-flow-third/pipeline/mineracao_observada.py
  - id: openwiki-source-56ecb9118a7d0aa06053e592
    resource: repo://analysis/adaptador_trace.py
  - id: openwiki-source-1748b7ddacfe941301be6af0
    resource: repo://analysis/base_utils.py
  - id: openwiki-source-b1f655aa6d87090fc6d82043
    resource: repo://analysis/decisoes.md
  - id: openwiki-source-99788feefdbe5f781b41ad79
    resource: repo://analysis/episodios_trace.py
  - id: openwiki-source-afeb1c5ba90e2da2476aeaf0
    resource: repo://analysis/glossario.md
  - id: openwiki-source-fdf27baf1c9125283297c6fc
    resource: repo://analysis/leitor_trace.py
  - id: openwiki-source-390363992e7f2499e94a84a2
    resource: repo://analysis/pipeline-entre-bases.md
  - id: openwiki-source-968204141b3124543370ca68
    resource: repo://analysis/README.md
  - id: openwiki-source-9f5a0a50fae31ae5a36eea6f
    resource: repo://analysis/tests/test_adaptador_trace.py
  - id: openwiki-source-3ab9661f76ec4f21f9c10b2e
    resource: repo://analysis/tests/test_integracao_carga_base3.py
  - id: openwiki-source-4003dfabf13d9651d0b0cc0f
    resource: repo://analysis/tests/test_mineracao_observada_base3.py
generated: { by: "claude-code", at: "2026-10-09T17:09:54.387Z" }
---

`analysis/` não é mais uma análise só: são **três extrações independentes** do mesmo sistema de agentes em produção (a esteira jurídica), cada uma numa pasta datada `AAAA-MM-slug/`, todas respondidas pelo mesmo método — a genealogia erro → memória descrita em [Metodologia de Taxonomia de Erros](metodologia-de-taxonomia-de-erros.md). Esta página cobre o que muda de uma base para outra e onde fica o quê; o método em si e a disciplina de PII/validação estão em [Metodologia de Análise de Traces](metodologia-de-analise-de-traces.md).

## As três bases

| | Base 1 | Base 2 | Base 3 |
|---|---|---|---|
| **Pasta** | `analysis/2026-09-trace-law-flow/` | `analysis/2026-09-trace-law-flow-second/` | `analysis/2026-10-trace-law-flow-third/` |
| **O que é** | Trace completo: cada execução com a memória inteira de cada papel (steps com e sem erro, system prompt, resposta final). 1.000 execuções, out/2025–ago/2026 | Amostra independente da base 1 (0 `exec_id` em comum), também trace completo | Parquet do Athena (query `ICTI_crossmemory_query_mineracao_erros`): **uma linha por passo com erro**, com uma janela em colunas (passo anterior, dois seguintes, custos, sinal de recuperação). 31.421 linhas: 30.141 erros estruturados + 1.280 suspeitas |
| **Onde roda** | Neste repositório | Na máquina de compliance — a pasta aqui guarda **só documentação** (README + roadmap + relatório reunido); o pipeline e os dados ficam lá | Neste repositório — é a base atual do projeto, a fonte de verdade |
| **Papel** | Análise fundacional: é onde nasceram a taxonomia, a triagem e a cadeia erro → memória | Réplica que testa o método — cada divergência vira um Ajuste no livro-razão | Testa o método contra uma extração de formato diferente: sem denominador, contexto em janela, textos cortados |

A base 2 não tem racionais nem procedimento próprios, de propósito: **racional e procedimento são por método, não por base** — os resultados, a auditoria e o "como foi rodada" da base 2 ficam reunidos em `2026-09-trace-law-flow-second/docs/02-relatorio-base2.md`, com a origem de cada número linkada.

## O que muda quando a extração muda de formato — o "modo observado" da base 3

A base 3 não pode usar o `carregar_base()` das bases 1 e 2, porque o parquet não é o trace inteiro: não há denominador (os passos sem erro não vêm), o contexto é uma janela em volta do erro (não o histórico) e os textos vêm cortados (mensagem em 20.000, código em 12.000 caracteres). Em vez disso ela roda o **modo observado** (`pipeline/mineracao_observada.py`):

- **As mesmas regras, só onde decidem.** Cada regra da taxonomia precisa de certos insumos (a mensagem inteira, saber se o passo anterior teve erro, o histórico de chaves). O modo observado checa, erro a erro, se os insumos estão na janela: se sim, aplica a regra de sempre; se não, o erro fica **pendente** com o motivo escrito (`mensagem_limitada_ou_ausente`, `predecessor_nao_identificado_sql`…). Nenhuma regra nova foi criada para a base 3 — as regras foram comparadas por estrutura de código com as da base 2.
- **Pendente não é resíduo.** O pendente (a regra existe, o dado não chegou) fica sem unidade e aparece na cobertura com motivo e custo em tokens; o resíduo continua sendo só o que a regra viu e não explicou; o alarme de cobertura é calculado sobre o resíduo, não sobre os pendentes.
- **"Candidato observado", não "candidato".** A recorrência é medida só nos erros observáveis — uma unidade que não passa na régua tem *recorrência não demonstrada*, pode existir nos pendentes.
- **Nenhum destino é herdado.** A decisão de mineração de uma base (`DESTINO_MINERACAO` + `BASE_ID`, Ajuste 7) só vale na base em que foi tomada; na base 3 toda candidata começa com o destino em aberto.
- **Componente, não cascata exata.** A janela não traz a chamada nem o histórico, então a "componente" (sequência de erros ligados pela janela) é condicional — as contagens de ocorrência não são contagens exatas de episódios.

O que a base 3 não responde (taxas, falhas silenciosas, sucesso por conteúdo, protocolo do system prompt) está medido no procedimento §4 da pasta e virou o pedido de dados complementares (`docs/05-pedido-queries.md`), ordenado por valor: denominadores primeiro. A pasta também tem uma entrada única de comando (`pipeline/executar.py`) com os subcomandos `analisar`, `inventariar`, `validar`, `conferir` e `painel`.

## O livro-razão — `pipeline-entre-bases.md`

Quando uma base nova estressa o método, a resposta certa é **corrigir o método** — com a base 1 como teste de regressão — e não remendar a base. O livro-razão registra, ajuste por ajuste (hoje Ajustes 1–16), o que disparou a mudança, a evidência, o que foi alterado, como foi verificado e o efeito em cada base. O ciclo de um ajuste é sempre o mesmo:

1. **Evidência na base nova** (tabela por padrão, drill-down de caso);
2. **Diagnóstico** (de quem é a falha — agente × plataforma);
3. **Ajuste escrito e testado neste repo** — critério de aceitação: a base 1 muda só nos erros previstos, e a auditoria independente dá 0 divergências;
4. **Réplica** na cópia da base 2 (as funções mudadas estão listadas em cada ajuste);
5. **Registro** no livro-razão, no racional, no procedimento e no roadmap.

**Coerência:** um ajuste que muda número da base 1 refaz, no mesmo passo, notebook, Sankey e docs — as auditorias congeladas ganham um banner, não são reescritas. O livro-razão também guarda as Etapas (o histórico de cada rodada) e uma errata do que ficou velho. O "o que fazer agora" não mora aqui — vive nos roadmaps (ver [Governança das Análises](../referencia/governanca-das-analises.md)).

## Código compartilhado na raiz de `analysis/` — a fronteira hipótese × mecânica

A regra de divisão é explícita: **o que é hipótese sobre uma base** (`classify()`, `submecanismo()`, `SUB2UNI`, `carregar_base()`) fica no `base_pipeline.py` da pasta datada e é **copiado** quando uma base nova chega; **o que é mecânica do formato do trace** mora na raiz de `analysis/` e é **importado**. Quatro módulos compartilhados:

- **`leitor_trace.py`** — o leitor único do trace cru: CSV puro, `.xz`, `.gz` ou um único parquet, detectado por bytes mágicos, não pela extensão. Entrega o mesmo contrato all-text do `pd.read_csv(dtype=str)` nos dois formatos — em parquet, datas viram `AAAA-MM-DD HH:MM:SS`, colunas aninhadas viram JSON via `json.dumps` (nunca `str()`), e a normalização fica em `df.attrs["formato"]`. É o único ponto compartilhado até pelos `audit_recompute*` (que não podem importar o pipeline, para a lógica deles continuar independente).
- **`base_utils.py`** — primitivas genéricas de trace de CodeAgent (formato smolagents): agrupar steps em sequências `(exec_id, role)` ordenadas, o inventário autoritativo de ferramentas (`def name(...)` no system prompt), helpers de AST sobre `code_action`, extração de entidades tipadas. Nada nele conhece a esteira jurídica nem a taxonomia.
- **`adaptador_trace.py`** — núcleo estrutural das fontes de steps: normaliza as janelas da extração legada e o censo compacto v2 para um contrato comum. Não classifica erro nem cria memória; texto ausente/cortado não equivale a ausência no trace.
- **`episodios_trace.py`** — componentes observadas de problemas (a "cascata condicional" da base 3): separa consecutivos estruturados de consecutivos `error_like`, usa só vínculos candidatos compatíveis no modo janela, e não inventa ActionStep ordinal nem same-call.

## Testes e auditoria

- **`analysis/tests/`** — suite unittest/pytest sobre **fixtures sintéticas**, sem nenhum dado de cliente nos testes versionados: cobre o adaptador (`test_adaptador_trace`), a entrada única da base 3 (`test_comandos_third`), a carga estrutural (`test_integracao_carga_base3`), mecanismos/episódios (`test_mecanismos_episodios_base3`), a mineração observada (`test_mineracao_observada_base3`), sintomas/custos (`test_sintomas_base3`) e a recomputação de validação (`test_validacao_base3`).
- **Auditorias independentes** — `2026-09-trace-law-flow/audit/` guarda os relatórios e os `audit_recompute*.py`: segundas implementações feitas da prosa dos racionais (`csv` + `json` + `ast`, sem pandas e sem importar o pipeline), porque "reexecutar não é verificar". Todos aceitam `--trace <arquivo>` (CSV ou parquet); o `audit_recompute9` aceita `--base` e `--json`, que é como o [kit de mineração](kit-de-mineracao.md) o roda em paralelo a uma rodada — inclusive na máquina de compliance, de onde só saem contagens. Uma auditoria só fecha quando o relatório ganha uma Parte II (a resposta do autor); os estados estão em `audit/README.md`.

## A fronteira da máquina de compliance

Da máquina onde a base 2 roda **só saem** contagens, nomes de classe de exceção, nomes de papel/ferramenta/modelo, meses, verdadeiro/falso, tamanhos, tokens e esqueletos mascarados — nunca texto de caso, código do agente, nome de cliente, número de processo nem `exec_id`. Por isso a pasta `-second` aqui é só documentação, e por isso a leitura de casos crus da base 2 é sempre do Rafael, de volta vindo categorias (`[assistido]` entra como hipótese, `[conferido]` é o determinístico — ver o glossário em [Governança das Análises](../referencia/governanca-das-analises.md)).

## Como se conecta ao resto do projeto

- O método que as três bases compartilham: [Metodologia de Taxonomia de Erros (Genealogia)](metodologia-de-taxonomia-de-erros.md) e [Metodologia de Análise de Traces](metodologia-de-analise-de-traces.md) (layout de pasta, intake, PII).
- O estado do trabalho (roadmaps por base, decisões, glossário de códigos, registros JSON): [Governança das Análises](../referencia/governanca-das-analises.md).
- Como uma rodada de mineração roda igual em qualquer base/ambiente: [Kit de Mineração de Traces](kit-de-mineracao.md).
