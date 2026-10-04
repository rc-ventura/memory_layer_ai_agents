# Análise do trace cru — esteira de agentes do fluxo juridico

**Data:** 2026-09-08 · **Fonte:** `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` (1.000 execucoes, out/2025-ago/2026 — corrigido 23/09/2026: mes de execucao, nao lote de corte) · **schema das 11 colunas + o campo de status:** [`docs/05-schema.md`](docs/05-schema.md)

Analise empirica do primeiro trace cru da esteira juridica (1.000 execucoes, 5.781 steps,
142,6 milhoes de tokens). Taxonomia de erros por causa-raiz, custo em tokens/latencia, propagacao,
reincidencia entre execucoes, detectores de falha silenciosa, e candidatos a unidades de memoria.

**Duas analises, dois conjuntos de documentos.** A analise generica do trace (taxonomia, custo, propagacao,
candidatos) esta nos docs 01–02 e no notebook `analise_trace_esteira_juridica.ipynb`. A mineracao das unidades
nº2/nº10 — analise pre-registrada que derivou o schema real das ferramentas e decidiu o destino de cada
unidade — virou conjunto proprio em 18/09/2026: docs 05–06 e o notebook `mineracao_unidades_n2_n10.ipynb`
(numeracao "§9" e "§11.x" preservadas).

## Como ler esta pasta (ordem sugerida)

| # | Arquivo | O que e | Para quem |
|---|---|---|---|
| 1 | [`01-racionais.md`](docs/01-racionais.md) | A logica por tras da analise generica, em linguagem acessivel. Por que a taxonomia veio do trace e nao dos papers; o que e um teste de robustez; o que significa um achado ser corrigido vs. retirado. | Ler primeiro — da o contexto pra entender o resto |
| 2 | [`02-relatorio-achados.md`](docs/02-relatorio-achados.md) | O relatorio de achados em si: TL;DR, taxonomia por causa-raiz, custo vs. falha, o resultado central (agente le o erro e reincide), ponto cego, candidatos a memoria, o que a literatura refutou, limitacoes, proximos passos. | O documento principal — os numeros |
| 3 | [`03-procedimento-validacao.md`](docs/03-procedimento-validacao.md) | Roteiro de validacao das DUAS analises: como auditar os pipelines, em que ordem ler os papers, e como triangular qualquer numero agregado contra um caso concreto no trace cru (`drill_down.py`). Checklist pre-reuniao. | Antes de apresentar ou reusar o pipeline |
| 4 | [`04-roadmap.md`](docs/04-roadmap.md) | O backlog numerado desta analise (numeros estaveis, citados no projeto todo), o monitoramento e o que foi fechado. O "o que fazer agora", desta e de qualquer analise, fica em [`../plano-atual.md`](../plano-atual.md). | Para saber o proximo passo |
| 5 | [`05-schema.md`](docs/05-schema.md) | O schema do trace cru: as 11 colunas, o campo de status, a estrutura de `txt_etap_memo`, o que ficou em aberto. | Quando precisar ler o trace na mao |
| 6 | [`06-racionais-mineracao-unidades-n2-n10.md`](docs/06-racionais-mineracao-unidades-n2-n10.md) | A logica da segunda analise (mineracao nº2/nº10): os 8 passos pre-registrados, as analises fundas das duas unidades. Continua a numeracao do 01 (e a "§9 dos racionais"). | Depois do 01 — mesma funcao, outra analise |
| 7 | [`07-relatorio-mineracao-unidades-n2-n10.md`](docs/07-relatorio-mineracao-unidades-n2-n10.md) | O relatorio da mineracao: o schema real derivado do trace (§6.1), as analises fundas de `validar_quebra_sigilo` (§6.2) e `get_available_documents` (§6.3). Continua a numeracao do 02. | Os numeros da segunda analise |
| 8 | [`09-metodologia-erro-a-memoria.md`](docs/09-metodologia-erro-a-memoria.md) | O documento-metodo da cadeia de agregacao (erro, classify, submecanismo, SUB2UNI, unidade, triagem): os dois eixos paralelos, cardinalidades verificadas nos 498 erros, o exemplo trabalhado "Could not index" e o rastreio ponta a ponta com tres erros reais. E a instanciacao do metodo generico (pre-artigo) que vive em `discussion/hipoteses/trace-error-taxonomy-methodology/`. | Para ver a cadeia inteira num arquivo so — e o que cada grafico do notebook demonstra |
| 9 | [`10-racionais-protocolo-harness.md`](docs/10-racionais-protocolo-harness.md) | A familia "Protocolo do harness" (resposta sem bloco de codigo): por que existe (modo texto x JSON), a investigacao por camada (modo, modelo, contrato), o catalogo de mecanismos M1–M6 e a regra de destino. | Antes de investigar esta familia em qualquer base |
| 10 | [`11-relatorio-protocolo-harness.md`](docs/11-relatorio-protocolo-harness.md) | Os resultados da familia base por base: base 1 fechada (33 erros, M1/M2/M3), base 2 em andamento (incidente do modelo `gpt-5.6-terra`, RoteadorCivel com M4/M5), comparacao entre bases. | Os numeros da familia |
| 11 | [`12-procedimento-protocolo-harness.md`](docs/12-procedimento-protocolo-harness.md) | O roteiro para repetir a investigacao numa base nova: comandos em ordem, o que sai da maquina 2, leitura por caso, metadados dos steps, classificacao no catalogo. | Ao receber uma base nova |
| 12 | [`13-racionais-falhas-silenciosas.md`](docs/13-racionais-falhas-silenciosas.md) | O balde invisivel: por que a fonte de erros nao pode ser so a excecao, o funil que separa visivel e invisivel, os seis grupos do motivo e o dono, a forma do argumento (o gesto do `repr_colado`), os detectores de comportamento migrados da esteira. | Antes de medir falhas silenciosas em qualquer base |
| 13 | [`14-relatorio-falhas-silenciosas.md`](docs/14-relatorio-falhas-silenciosas.md) | Os numeros do balde invisivel nas duas bases: ~90% das falhas de ferramenta sao silenciosas, sucesso falso candidato por grupo, o `json_invalido` = `repr_colado` silencioso, os detectores na base 1. | Os numeros das falhas silenciosas |
| 14 | [`15-procedimento-falhas-silenciosas.md`](docs/15-procedimento-falhas-silenciosas.md) | O roteiro: rodar o balde, cobertura das regras de motivo (duas bases), dono pelo `--forma`, sucesso falso no caso, o que sai da maquina 2. | Ao receber uma base nova |

## Pipeline e ferramentas

| Arquivo | O que faz |
|---|---|
| [`base_pipeline.py`](pipeline/base_pipeline.py) | A espinha compartilhada — carga do trace, explosao em `steps`/`RAW`/`execs`, classificacao (`classify`/`submecanismo`/`UNI`/`EU`), triagem e `S`/`DEGENERADO`. Qualquer analise nova parte daqui |
| [`analise_trace_esteira_juridica.ipynb`](pipeline/analise_trace_esteira_juridica.ipynb) | Notebook executavel — a analise generica (§§1–10) sobre a base compartilhada, com outputs embutidos |
| [`consolidacao_unidades.ipynb`](pipeline/consolidacao_unidades.ipynb) | Notebook executavel da consolidacao (§14.x): junta as ocorrencias dos dois baldes (visivel e invisivel) no formato comum e faz a triagem final das unidades, com a recorrencia contada sobre a uniao; mostra o que muda contra a triagem so do visivel (base 1: so a `U_repr_colado`, 6 → 12). Ajuste 12 |
| [`falhas_silenciosas.ipynb`](pipeline/falhas_silenciosas.ipynb) | Notebook executavel do balde invisivel (§13.x): falhas de ferramenta devolvidas como texto (`error: null`), grupos do motivo, sucesso falso candidato, forma do argumento, detectores de comportamento (o antigo §7 da esteira) e a tabela de ocorrencias para a consolidacao. Mesmas funcoes do `drill_down.py silenciosas` |
| [`mineracao_unidades_n2_n10.ipynb`](pipeline/mineracao_unidades_n2_n10.ipynb) | Notebook executavel da mineracao (§11.x, numeracao preservada). Standalone: o setup §0 chama `carregar_base()` e reconstroi `RAW`, `EU`, `UNI`, `S` a partir do trace |
| [`drill_down.py`](pipeline/drill_down.py) | Script para triangular um numero agregado contra um caso concreto no trace cru. `ferramenta <nome>` mostra como o system prompt declara uma ferramenta no trace inteiro; `evidencia [<analise>]` completa as pastas de evidencia que o notebook grava (trace cru + visao derivada de cada caso) — ver `03-procedimento-validacao.md`, "Evidencia por analise" |
| [`indice_evidencia.ipynb`](pipeline/indice_evidencia.ipynb) | Indice navegavel das pastas de evidencia: lista os casos de uma pasta, os blocos de um caso e o caminho de cada trecho no cru — para achar no trace o que se viu no derivado |

## Fichamentos teoricos

[`literature/`](literature/) — quatro papers de taxonomia de erro de agentes, lidos em texto
completo (apendices incluidos) por subagentes em 08/09/2026. Nivel 🔎 (agente leu, nao Rafael leu).
Ver o [`literature/README.md`](literature/README.md) para o indice e o que cada paper aporta.

## Dados derivados

`pipeline/resultados/` — CSVs derivados do trace cru (**git-ignored**: contem nomes de clientes, numeros
de processo e trechos de documentos em claro). Regenerar rodando os notebooks (escrevem nessa pasta, nao na raiz
da analise — uma copia orfa em `resultados/` na raiz existiu ate 16/09/2026 e foi removida por auditoria, ver
`audit/2026-09-16-auditoria-independente.md` M1).

**Dono e ciclo de vida dos arquivos do topo.** Os CSVs do topo (`erros_classificados`, `execucoes`,
`erros_mecanismo`, `triagem_assinaturas`, `candidatos_memoria`, `reincidencia`, `payoff_assinaturas`) tem **um
dono so**: o notebook da analise generica (ultima celula). Sao **snapshot, nao estado vivo** — descrevem o
trace + a classificacao do `base_pipeline.py`, e so mudam se um dos dois mudar (o que invalidaria numeros
publicados; por isso a triagem fica congelada como estava quando rodou). Passes de mineracao **nao escrevem
neles nem dependem deles** — leem a base em memoria via `carregar_base()`. `drill_down.py` le dois
(`erros_mecanismo.csv` no comando `mecanismo`; `casos.csv` das pastas). `candidatos_memoria.csv` nao carrega
o desfecho da mineracao: desfecho vive em `unidades_memoria.json`. **O que falta minerar** = candidatas com
`decisao = candidato` no CSV menos as unidades com registro no JSON.

**Como a pasta cresce — a metodologia.** Cada analise especifica e um **passe** — um metodo pre-registrado
aplicado a um conjunto de unidades — e ganha **um notebook proprio** sobre `base_pipeline.py`. Um passe cobre
todas as unidades que compartilham o mesmo metodo (o passe de mineracao de schema cobriu nº2 e nº10 juntas);
unidades de outra natureza esperam o passe do metodo delas. Nao e um notebook por unidade nem um notebook unico:
a fronteira e o metodo. Cada notebook e **dono de um intervalo de secoes**: a mineracao e §11.x, o proximo
notebook usa §12.x, e assim por diante — secao numerada, nunca reutilizada.

**Exemplo — minerar as unidades nº6 e nº7 (mesmo metodo → um passe):**

```
pipeline/mineracao_unidades_n6_n7.ipynb     notebook novo, dono da §12.x (§0 = carregar_base())
docs/08-racionais-mineracao-unidades-n6-n7.md   pre-registro do passe 2
docs/09-relatorio-mineracao-unidades-n6-n7.md   numeros do passe 2
resultados/evidencia/12.1_*/  12.5_*/ ...   nascem sozinhas: registrar_evidencia() cria ao rodar;
                                            drill_down.py evidencia 12.x preenche crus/ + visoes
resultados/unidades_memoria.json            {nº2, nº10} -> {nº2, nº10, nº6, nº7} — um arquivo so
```

O unico numero que se escolhe e o prefixo da secao (o proximo livre); pastas de evidencia, `casos.csv` e
`leia-me.md` o notebook gera. Se a unidade nova precisar de metodo diferente (ex.: validacao contrafactual
das unidades experienciais), e outro passe com secao propria — nao se aperta a nº2/nº10 dentro do notebook
delas.

`pipeline/resultados/evidencia/<secao>_<analise>/` — uma pasta por analise, prefixada pela secao do notebook
que a gerou (`11.4_conserto/` = §11.4 do notebook de mineracao): `casos.csv` (casos escolhidos por regra),
`leia-me.md`, `crus/` (a linha inteira do trace, sem alteracao — a fonte) e `derivados/` (tabelas e a visao de
cada caso, que so espelha o cru). **Geracao em duas etapas**: o notebook grava a parte estrutural (`casos.csv`,
`leia-me.md`, `derivados/`); `drill_down.py evidencia <pasta>` grava os crus e as visoes, conferindo cada trecho
contra o cru ao gravar. Excecao: `avulso/` recebe casos pontuais via `drill_down.py evidencia_avulsa`. Mesma
regra: git-ignored, com PII.

`pipeline/resultados/unidades_memoria.json` — o **registro canonico** das unidades de memoria. Nao e por
notebook: cada passe le o arquivo e regrava com seus registros adicionados/atualizados (hoje: nº2 e nº10, da
§11.8/§11.9). O mapeamento unidade → evidencia fica nos registros e nos `leia-me.md`.

`data/` — o trace cru (`85cb11b5-....csv.xz`, **git-ignored**). `pipeline/drill_down.py` e os scripts de
`audit/scripts/` resolvem o caminho relativo ao proprio arquivo, nao ao diretorio corrente.

`audit/` — as auditorias independentes e os `audit_recompute*.py`. O indice do que ja foi auditado (objeto, estado,
onde estao as respostas) e [`audit/README.md`](audit/README.md).
