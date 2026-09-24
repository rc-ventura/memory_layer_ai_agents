---
type: methodology
title: Metodologia de Análise de Traces
description: A metodologia empírica de analysis/ — a escada de trace bruto a unidade de memória candidata, o layout de pastas por análise datada, a regra de que a profundidade de validação deve casar com a força da alegação, e a disciplina de dados derivados/PII.
tags: [trace-analysis, empirical-methodology, validation, pii-discipline, memory-candidates, robustness-testing]
sources:
  - id: openwiki-source-747c216822a5f3a85d9b49e1
    resource: repo://analysis/2026-09-trace-law-flow/docs/03-procedimento-validacao.md
  - id: openwiki-source-631277a618f3e5073c6d0450
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/checklist.py
  - id: openwiki-source-0db414e3ad59b3a4b0ec3ea1
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/drill_down.py
  - id: openwiki-source-bf7dacbe9994bcd338b3c0c5
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/resultados/evidencia/relatorio_meta_11.1-11.10.md
  - id: openwiki-source-4e5bd038f77a72e191e7c372
    resource: repo://analysis/2026-09-trace-law-flow/README.md
  - id: openwiki-source-1748b7ddacfe941301be6af0
    resource: repo://analysis/base_utils.py
  - id: openwiki-source-968204141b3124543370ca68
    resource: repo://analysis/README.md
generated: { by: "claude-code", at: "2026-09-23T23:38:13.077Z" }
verified:
  - by: openwiki/0.5.1
    at: 2026-09-23T23:38:13.077Z
---

`analysis/` guarda as análises empíricas de traces brutos de agentes reais da esteira jurídica — a base de evidência de "memória de trabalho" para a hipótese de memória do projeto. Não é só um lugar para contar erros ou juntar gráficos: o objetivo recorrente é construir uma ponte empírica entre o **trace bruto** de um sistema de agentes real, os **mecanismos reais de falha** visíveis nesse trace, e a menor **lição/memória/correção operacional** reutilizável que poderia evitar a mesma falha de novo. A classificação de erro em si (sintoma → mecanismo → unidade → destino) tem sua própria metodologia dedicada — ver [Metodologia de Taxonomia de Erros (Genealogia)](metodologia-de-taxonomia-de-erros.md); esta página cobre o que envolve essa classificação: layout de pasta, disciplina de PII e a escada de validação.

## A escada de trace a memória

```text
                          ┌─────────────────────────────┐
                          │ Literatura                  │
                          │ - testa ajuste externo       │
                          │ - sugere novas análises      │
                          │ - dá vocabulário conceitual  │
                          └──────────────┬──────────────┘
                                         │
┌────────────────┐    ┌────────────────┐ │  ┌──────────────────────────┐
│ Trace bruto    │ -> │ Sintomas /     │-┼->│ Mecanismos / proxies     │
│ (fonte de verdade)│  │ agregados      │ │  │ de causa-raiz            │
└────────────────┘    └────────────────┘ │  └──────────────────────────┘
                                         │                │
                          ┌──────────────┴──────────────┐ ┌──────────────────────────┐
                          │ Validação                    │ │ Unidade de análise certa │
                          │ - recomputação                │ │ erro -> cascata ->       │
                          │ - testes de robustez           │ │ ocorrência -> unidade    │
                          │ - drill-down de caso            │ └──────────────────────────┘
                          │ - bruto > derivado              │                │
                          │ - auditorias independentes      │                v
                          └─────────────────────────────┘ ┌──────────────────────────┐
                                                          │ Lição reutilizável /     │
                                                          │ orientação                │
                                                          └──────────────────────────┘
                                                                           │
                                                                           v
                                                          ┌──────────────────────────┐
                                                          │ Unidade de memória       │
                                                          │ candidata / decisão      │
                                                          │ operacional              │
                                                          └──────────────────────────┘
                                                                           │
                                                                           v
                                                          ┌──────────────────────────┐
                                                          │ Pacote de evidência       │
                                                          │ + trilha de auditoria     │
                                                          └──────────────────────────┘
```

**Como isso funciona na prática**, em seis movimentos que se repetem em toda análise nova:

1. **Comece pelo trace bruto, não pela literatura ou por intuições.** CSVs derivados, notebooks e tabelas-resumo servem para contar e navegar — não são a autoridade final.
2. **Separe sintoma de mecanismo.** Uma exceção visível (`KeyError`, `TypeError`, "Could not index") é frequentemente só uma assinatura de superfície; se uma assinatura mistura vários fenômenos diferentes, refine-a até um mecanismo ou proxy de causa-raiz que realmente responda à pergunta de pesquisa.
3. **Use a unidade analítica certa.** Erros por step nem sempre são eventos independentes — quando falhas repetidas são, na verdade, um problema subjacente contínuo, a unidade certa pode ser uma **cascata**, uma **ocorrência**, ou uma **unidade escopada por papel**, não uma contagem por step que falhou.
4. **Vá de "o que falhou" para "o que deveria ser lembrado".** O produto final não é só um rótulo de erro — é a menor **lição/orientação** reutilizável que poderia ajudar uma execução futura a evitar a mesma falha (conhecimento factual/ambiental, conhecimento experiencial/estratégico, ou tratamento puramente operacional que não é memória de agente).
5. **A profundidade de validação deve casar com a força da alegação.** Contagens diretas (n de erros, tokens, execuções, totais mensais) costumam ser robustas por construção — recomputação independente basta. Alegações dependentes de heurística (thresholds, regras de correspondência, comparações de texto) precisam de testes de robustez contra alternativas plausíveis. Alegações prescritivas/causais/que viram memória ("esta é a lição a escrever", "esta ferramenta de fato retorna o schema X") merecem o tratamento mais forte: pacotes de evidência com casos brutos, seleção de caso por regra explícita, e relatórios de auditoria independentes.
6. **Trate artefatos derivados e pacotes de evidência como coisas diferentes.** Artefatos derivados são visões compactas para navegar/agregar; pacotes de evidência são pastas específicas de cada análise que preservam o link de volta aos casos brutos selecionados; auditorias independentes são uma segunda leitura que confere se a alegação da análise realmente se sustenta quando reaberta a partir do trace bruto — porque código pode estar errado de forma perfeitamente consistente, produzindo o mesmo número errado centenas de vezes.

## Layout de pasta por análise datada

Cada análise vive na sua própria pasta `analysis/AAAA-MM-slug/` (nova pasta por análise — não um diretório único crescente). O exemplo em produção, `analysis/2026-09-trace-law-flow/`, estabelece o padrão de subpastas que futuras análises devem seguir:

| Subpasta | Conteúdo |
|---|---|
| `pipeline/` | Os notebooks Jupyter executados (pipeline reprodutível, com outputs embutidos), um `base_pipeline.py` compartilhado quando a pasta hospeda mais de uma análise (carga do trace, explosão em steps, classificação de erro — cada notebook constrói sobre ele em vez de copiar células), e scripts companheiros: `drill_down.py` (triangula qualquer número agregado contra um caso concreto no trace bruto — comandos `caso`, `listar`, `mecanismo`, `ferramenta`, `evidencia`, `relogios`, `residuo`) e `checklist.py` (as verificações de intake de uma base nova — ver abaixo) |
| `docs/` | Os documentos narrativos, numerados por par racional/relatório: `01-racionais.md` + `02-relatorio-achados.md` para a primeira análise, `03-procedimento-validacao.md` (validação/auditoria) e `04-roadmap.md` (o que falta) completam o primeiro conjunto, `05-schema.md` documenta o schema do trace bruto. Uma segunda análise metodologicamente distinta na mesma pasta datada ganha seu próprio par numerado (`06-racionais-mineracao-unidades-n2-n10.md` + `07-relatorio-mineracao-unidades-n2-n10.md`, para o passe de mineração das unidades nº2/nº10), com o slug do doc casando com o slug do notebook (`mineracao_unidades_n2_n10.ipynb`) e preservando a numeração de seção original para que as referências cruzadas continuem resolvendo. `09-metodologia-erro-a-memoria.md` é a instanciação verificada (funções, números, o Sankey de genealogia) da metodologia geral de taxonomia de erros |
| `resultados/` | CSVs derivados, **git-ignored** — carregam nomes de clientes, números de processo e trechos de documento em claro. Regenerados rodando o notebook, nunca commitados |
| `audit/` (opcional) | Relatórios de auditoria independentes datados (`2026-09-08-…`, `2026-09-16-…`) e `scripts/audit_recompute*.py`, os scripts de recomputação independente do universo inteiro no CSV bruto |

Duas coisas mudaram de lugar e vivem na raiz de `analysis/`, não dentro da pasta datada:

- **`literature/`** — as notas 🔎 dos papers de taxonomia de erro (texto completo lido por um agente, verificado contra o PDF, mas não lido pelo Rafael) foram promovidas a `analysis/literature/`, compartilhadas entre análises em vez de pertencer a uma pasta só — ver [Revisão de Literatura e Disciplina de Citação](revisao-de-literatura-e-disciplina-de-citacao.md) para o que 🔎 significa.
- **`base_utils.py`** — primitivas genéricas de análise de trace de CodeAgent (formato smolagents): agrupar steps em sequências ordenadas `(exec_id, role)`, o inventário autoritativo de ferramentas (`def name(...)` no system prompt), helpers de AST sobre `code_action` e extração de entidades tipadas + checagem de suporte. Nada nele conhece a esteira jurídica nem a taxonomia de erros — a fronteira declarada é: **hipótese sobre uma base** (`classify()`, `submecanismo()`, `SUB2UNI`, `carregar_base()`) fica no `base_pipeline.py` da pasta datada e é **copiado** para a pasta nova; **mecânica do formato do trace** mora em `base_utils.py` e é importada. Criado em 22/09/2026 e verificado reproduzindo exatamente os números dos detectores de falha silenciosa da §7.

## Uma segunda base existe — e o intake dela virou checklist

A segunda extração (**base 2**, outra amostra independente de 1.000 execuções) já rodou o mesmo pipeline — e provou na prática por que intake precisa de procedimento: trouxe um `error.type` que a taxonomia nunca tinha visto (`AgentMaxStepsError`, n=1) e um erro que parecia extinto reapareceu com força, reabrindo a triagem do bucket "Protocolo do harness" (22/09/2026). O setup mecânico de uma base nova (pasta datada, cópia de `base_pipeline.py` + `drill_down.py` + `checklist.py` + `.gitignore`, dump em `data/`, apontar `TRACE`) está descrito no `analysis/README.md`; o que não é mecânico virou `pipeline/checklist.py`, que roda antes de qualquer notebook:

1. **Drift de colunas** — `base_pipeline.py` lê seis colunas por nome; uma extração diferente pode renomear ou derrubar alguma;
2. **Saúde do JSON** — quantas memórias parseiam vs. quebram em silêncio no `except` da explosão;
3. **Censo de `error.type`** — regex no cru × parse pelo pipeline, com flag de divergência: diz se a taxonomia cobre a base *antes* de ela jogar erros desconhecidos no resíduo;
4. **Contexto** — período real das execuções × lotes de corte, versões de agente, papéis no JSON;
5. **Sobreposição (opcional)** — `python checklist.py <outra-base.csv>` cruza `cod_idef_exeo` entre duas extrações — obrigatório antes de chamar duas bases de réplicas independentes ou de somá-las.

### Os três relógios — `anomesdia` não é a data da execução

A errata metodológica mais importante do ciclo: até 23/09/2026 o `mes` do pipeline vinha de `anomesdia`, que é a data do **lote de extração** (partição), não da execução — um lote acumula vários meses de execuções. Um teste de três relógios independentes por execução (`anomesdia` × `dat_hor_inio_exeo` × `timing.start_time` gravado pelo runtime dentro do JSON) mostrou que os dois últimos concordam em 840/840 e o primeiro diverge com mediana de 46 dias de defasagem — e **zero** execuções começam depois dele. Consequências: execuções passaram a ser datadas por `dat_hor_inio_exeo`; a cobertura da base 1 é **out/2025–ago/2026** (11 meses), não nov/2025–ago/2026; o incidente do harness foi em out/2025 (não dez/2025); e todas as colunas "meses" da triagem foram recalculadas — as decisões de triagem em si não mudaram. O comando `drill_down.py relogios` reproduz a evidência (`resultados/evidencia/A3_relogios/`). **Efeito colateral:** as auditorias independentes das pastas `11.x` verificaram a amostra escolhida sob a datação antiga — `relatorio_meta_11.1-11.10.md` e os `relatorio_independente.md` carregam um banner "Desatualizado desde 23/09/2026 — refazer" e não devem ser citados como verificação da amostra atual até serem refeitos.

## A metodologia de "passe" — como uma pasta de análise cresce

Cada análise específica dentro de uma pasta datada é um **passe**: um método pré-registrado aplicado a um conjunto de unidades. Um passe cobre todas as unidades que compartilham o mesmo método (o passe de mineração de schema, por exemplo, cobriu duas unidades de uma vez porque as duas precisavam do mesmo método); unidades de natureza diferente esperam o passe do método delas. A fronteira do notebook é o **método**, não a unidade nem um notebook monolítico único — não se cria um notebook por unidade, nem se acumula tudo num notebook só.

Cada notebook de passe é **dono de uma faixa de números de seção**, nunca reutilizada: o primeiro passe usa uma faixa (por exemplo §1–§10 para a análise genérica, §11.x para a mineração das unidades nº2/nº10), o próximo passe pega a faixa seguinte (§12.x), e assim por diante. Essa numeração de seção é o que amarra o notebook ao seu par de documentos `docs/` correspondente e às pastas de evidência que ele gera — nunca se reaproveita um número de seção já usado por outro passe.

Dentro de `resultados/`, cada passe produz pastas de evidência em `resultados/evidencia/<seção>_<análise>/`, prefixadas pelo número de seção do notebook que as gerou (ex.: `11.4_conserto/` = §11.4 do notebook de mineração), cada uma contendo `casos.csv` (casos escolhidos por regra explícita), `leia-me.md`, `crus/` (a linha inteira do trace, sem alteração — a fonte) e `derivados/` (tabelas e a visão de cada caso, que só espelha o cru). A geração é em **duas etapas**: o notebook grava a parte estrutural (`casos.csv`, `leia-me.md`, `derivados/`); o script de drill-down grava os `crus/` e as visões derivadas, conferindo cada trecho contra a linha crua do trace no momento em que escreve.

`resultados/unidades_memoria.json` é o **registro canônico** das unidades de memória candidatas — não é um arquivo por notebook: cada passe lê o arquivo existente e o regrava com seus próprios registros adicionados ou atualizados, então o arquivo acumula o resultado de todos os passes já rodados na pasta.

## Auditoria independente por pasta de evidência, mais um meta-relatório consolidado

O passe de mineração §11 (unidades nº2/nº10) estabeleceu o padrão concreto de auditoria: cada uma das dez pastas de evidência que ele produziu (`11.1_origem_do_erro/` a `11.10_leituras_get_available_documents/`) ganhou seu próprio `relatorio_independente.md` — uma segunda leitura, feita a partir dos `crus/` de cada pasta (não do notebook ou do código que os gerou), que confere se a alegação daquele passo específico se sustenta. Para os passos mais fortes (existência de um campo, contagem de entregas fora do padrão esperado), a auditoria foi além da releitura dos crus salvos e recomputou o universo inteiro a partir do CSV bruto com um caminho de código independente (`csv.DictReader` puro, sem reusar `pandas` nem as funções do notebook) — o mesmo princípio de "recomputar por fora" já em uso na análise original, agora aplicado passo a passo e preservado em `audit/scripts/audit_recompute*.py`. Um `relatorio_meta_11.1-11.10.md` consolida essas dez auditorias num veredito único por passo (sustentado / sustentado com ressalva / retratado), para que a pergunta "essa cadeia de validação se sustenta reaberta do zero?" tenha uma resposta central em vez de dez respostas espalhadas. **Ressalva temporal:** essa rodada de auditorias verificou a amostra escolhida sob a datação antiga (`anomesdia`); depois da errata dos três relógios as pastas `11.x` foram regeneradas com a data real e os relatórios aguardam refação — estão marcados como desatualizados no próprio meta-relatório.

## Disciplina de dados derivados e PII

Traces brutos (arquivos `*.csv.xz`, na raiz do repositório ou em qualquer outro lugar) **nunca** são versionados em claro — contêm dados jurídicos reais não anonimizados. `resultados/`, dentro de cada pasta de análise, é sempre git-ignored pelo mesmo motivo: guarda CSVs derivados, pastas de evidência por caso (`crus/` com a linha inteira do trace sem alteração, `derivados/` com as tabelas e a visão de cada caso) e os registros finais de unidades de memória candidatas. Regenerar esses artefatos é sempre uma questão de rodar o notebook de novo a partir do trace bruto local, nunca de puxar de um commit.

## Práticas de validação em uso

Da análise de referência (`2026-09-trace-law-flow/`), três práticas concretas que qualquer análise nova deveria repetir:

- **Recomputar "por fora" com um caminho de código diferente** — não reusar a mesma função de classificação nem o mesmo notebook, só para provar que um número não é artefato de um bug específico de uma lógica. Um recomputo independente com `csv.DictReader` puro (sem pandas) confirmou um número do relatório exatamente.
- **Testar robustez com pelo menos duas heurísticas de correspondência diferentes antes de reportar um número como firme.** Quando duas heurísticas divergem bastante (num caso real, de 13,7% para 4,3% trocando correspondência por prefixo por correspondência por sufixo), isso normalmente aponta para o método errado, não para o dado errado — investigável com o script de drill-down de caso.
- **Auditar a função de classificação central lendo uma amostra de suas entradas na mão** — a checagem de maior alavancagem quando toda uma taxonomia depende de uma cadeia de regras de correspondência de texto, porque qualquer erro ali contamina tudo a jusante.

## Quando código nascido de uma análise vira código portátil

O precedente já se realizou uma vez: [`analysis/base_utils.py`](../../analysis/base_utils.py) é o módulo portátil que vive na raiz de `analysis/` com a mecânica genérica do formato de trace CodeAgent — criado quando uma segunda base chegou e a fronteira "hipótese por base × mecânica do formato" precisou virar código. O próximo candidato registrado é `2026-09-trace-law-flow/pipeline/genealogia_sankey.py`, que renderiza a genealogia de erros como um diagrama Sankey com um motor de layout genérico (ordenação de colunas por baricentro + altura mínima de nó para legibilidade) que não depende de nada específico de taxonomia de erro — só a metade de preparação de dados do arquivo é específica da análise. Ainda não foi extraído para seu próprio módulo (um único chamador não basta para validar a fronteira certa): se uma análise futura precisar de um Sankey igualmente legível com muitos nós, esse é o código a reaproveitar, e `analysis/` (este nível, não dentro de uma pasta datada) é o lugar natural para esse tipo de código portátil — o mesmo raciocínio já aplicado a `schema-e-taxonomia-de-erros.md`, um documento de referência reutilizável que também vive na raiz de `analysis/`, fora de qualquer pasta datada, por não ser um artefato de um único passe.

## Como se conecta ao resto do projeto

- As unidades de memória candidatas que essas análises produzem são o insumo empírico mais concreto para os componentes do Memory Store e do Update Engine da [Hipótese de Arquitetura "Knowledge as Infra"](../arquitetura/hipotese-knowledge-as-infra.md).
- Os papers de taxonomia de erro lidos para fundamentar cada análise seguem a mesma disciplina de verificação (📝/🔎/✅) documentada em [Revisão de Literatura e Disciplina de Citação](revisao-de-literatura-e-disciplina-de-citacao.md).
- O método de classificação de erro que produz as unidades de memória candidatas mencionadas aqui é detalhado em [Metodologia de Taxonomia de Erros (Genealogia)](metodologia-de-taxonomia-de-erros.md).
