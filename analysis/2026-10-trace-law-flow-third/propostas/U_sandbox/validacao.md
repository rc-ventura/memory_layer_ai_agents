# Validação do script proposto — `U_sandbox` (inventário do sandbox)

> Códigos e siglas: [glossário](../../../glossario.md). Regra do validador: procedimento
> [`16`](../../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md), § "O validador". O validador não
> corrige nada: este laudo é o resultado.

**Data:** 16/10/2026 · **Branch:** `2026-10-16-base3-comparar-rodadas` · **HEAD:** `c544928` no início; a conferência foi commitada depois, em `b4d1f78`, já com a chave corrigida (o commit não foi feito pelo validador)
**Objeto:** `propostas/U_sandbox/mineracao_U_sandbox.py` (sha256 `cd52eab0…aca772`), teste
`analysis/tests/test_mineracao_candidata_base3.py`, racional `propostas/U_sandbox/racional.md` (blob `3873ac4`).
**Base de confirmação:** o ensaio da base 1 no formato da base 3 — rodada `315935e87c57b25e…`, fonte
`fonte_base1_v1.parquet` (sha256 `afaf3e98…30717ae`, igual ao `fonte_id` da rodada).

## Veredito: **REPROVADO**

Todas as medidas da conferência independente batem com as do script (zero divergência de número). Dois itens
reprovam:
- **item 3:** o campo `validation` do arquivo final não tem o **encontro** nem as **listas autorizadas**, que o racional
  (passo 8) pede;
- **item 4:** a versão do racional que o script implementa (a de `c544928`) foi escrita **depois** da primeira rodada
  do script na base de confirmação. A nota de 16/10 só declara uma das duas mudanças.

## Itens

| # | Item | Comando | Resultado |
|---|---|---|---|
| 1 | Conferência independente, escrita só do racional | `uv run python analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/conferencia_independente.py --fonte <ensaio>/fonte_base1_v1.parquet --casos <ensaio>/rodada/perfis/U_sandbox/casos.csv --perfil <ensaio>/rodada/perfis/U_sandbox/perfil.csv --json <rascunho>/conferencia.json` | ok: 17 erros na população, cobertura 17/17, 2 listas autorizadas, 0 repetições |
| 2a | Teste do script | `uv run python -m unittest analysis.tests.test_mineracao_candidata_base3 -v` | ok: 13 testes, 13 passam |
| 2b | Script pelo comando de mineração | `uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script` | saída 0; passos 1 e 3 a 9 ok; o passo 2 diz "não conferido" (o monitoramento não tem as tabelas desta base); `resultados/` não foi tocado |
| 2c | Comparação medida por medida | script de comparação sobre os CSV/JSON das duas saídas | **todas iguais** (tabela abaixo) |
| 3 | Script contra o racional | leitura do script; `validar_memoria.py`; testes de caixa-preta | **reprovado:** falta `encontro` e faltam as listas no `validation` (detalhes abaixo) |
| 4 | Ordem do pré-registro | `git log --date=iso-strict` do racional × `gerado_em` do manifesto da rodada de ensaio × `mtime` dos arquivos | **reprovado:** a versão atual do racional é posterior à primeira rodada (detalhes abaixo) |

`<ensaio>` = `analysis/2026-10-trace-law-flow-third/pipeline/resultados/ensaio_base1`; `<rascunho>` = pasta de
rascunho do validador, fora do repositório.

## 2 · As medidas, uma a uma

| Medida | Conferência | Script | Igual? |
|---|---|---|---|
| População na rodada (`casos.csv`) | 17 | 17 | sim |
| População pela prosa do passo 1, direto da fonte | 17 (mesmas 17 chaves; 0 só de um lado) | — (é a auditoria do passo 7) | sim, contra a rodada |
| Por braço da prosa: função embutida · import/ModuleNotFound · outro Forbidden · variável-módulo | 7 · 3 · 1 · 6 | — | — |
| Excluídos por um sinal que o pipeline decide antes | 0 | — | — |
| Execuções · papéis · meses | 17 · 6 · 8 | 17 · 6 · 8 | sim |
| Com nome ÷ população (cobertura) | 17/17 = 1,0 | 17/17 = 1,0 | sim |
| Passa o limiar de 95% | sim | sim | sim |
| `sem_nome`, pela primeira palavra | {} | {} | sim |
| Erros por tipo: `funcao_proibida` · `modulo_sem_import` · `import_bloqueado` · `modulo_ausente` · `atributo_dunder` | 7 · 6 · 2 · 1 · 1 | 7 · 6 · 2 · 1 · 1 | sim |
| Inventário (tipo, nome; erros, execuções, papéis, meses) | 10 linhas | 10 linhas, na mesma ordem | sim (as 10 linhas) |
| Nome × papel | 14 células | 14 células | sim |
| Nome × mês | 15 células | 15 células | sim |
| Linha por erro (`exec_id`, `step_ref`, papel, mês, tipo, nome) | 17 | 17 | sim (as 17) |
| Listas autorizadas distintas | 2 (13 nomes: 1 erro, 1 papel, 1 mês; 11 nomes: 1 erro, 1 papel, 1 mês) | 2, com os mesmos nomes, papéis e meses | sim |
| Destino 1: lista única em todos os papéis e meses | não | não | sim |
| Destino 2: erros que repetem o nome na mesma execução e papel | 0 (17 grupos, 0 com repetição) | 0 (0 execuções com repetição) | sim |
| `location` | 6 casos, um por papel, na ordem (papel, mês, `step_ref`) | os mesmos 6, na mesma ordem | sim |
| `evidence` | 3 casos: `funcao_proibida`/repr, `modulo_sem_import`/json, `import_bloqueado`/autojson | os mesmos 3 | sim |
| `correction_guidance`: nomes por rótulo, na ordem | não chame 4 · não importe 2 · importe antes de usar 2 · não existe no ambiente 1 · não acesse 1 · uma lista por grupo de papéis (2) | os mesmos nomes, na mesma ordem, e as 2 listas separadas por papel | sim (nomes e ordem) |
| `occurrences` (perfil): erros · ocorrências · execuções · meses | 17 · 17 · 17 · 8 | 17 · 17 · 17 · 8 meses (em lista) | sim |
| `description`: erros, tipos, papéis | 17 erros, 5 tipos, 6 papéis | o mesmo | sim |

**Diferença de medida: nenhuma.**

**Sobre a conferência.** Na primeira versão dela, a fonte e a rodada eram casadas por (execução, agente, posição do
passo). Essa chave se repete em 26 casos na fonte: o mesmo passo aparece com dois papéis. Com ela, a conferência dava
cobertura 15/17. Corrigi a chave da conferência para (execução, agente, papel, posição do passo), que não se repete
nenhuma vez, e a cobertura passou a 17/17. O erro era meu, não do script, que casa pelo `step_ref`. Só a conferência
mudou; o script, o teste e o racional ficaram como estavam.

## 3 · O script contra o racional

| Conferência | Resultado |
|---|---|
| Só as regras do racional (passo 4: os 5 padrões na ordem, último trecho depois do último `due to:`, `sem_nome` pela primeira palavra, estado não íntegro → `sem_nome`) | ok. Há uma diferença sem efeito nesta base (abaixo, a e b) |
| Nenhuma chamada a LLM nem a serviço externo | ok: os únicos imports são `re` e `pandas`; não há rede nem subprocesso |
| Nenhum limiar ou constante fora do racional | ok: `LIMIAR_COBERTURA = 0.95`, `head(10)` e `[:3]` estão no racional. `ESTADOS_INTEGROS = {"sem_corte_sql"}` é a leitura de "estado íntegro" e não é um limiar |
| Nenhum texto de caso impresso ou gravado | ok: nenhum arquivo da saída tem trecho de mensagem (busca por `due to`, `Code execution`, `InterpreterError`, `Forbidden`, `Traceback`: 0 arquivos); o script não tem `print` nem `open` |
| Rodada lida pelo código do pipeline | ok, testado de fora: um `casos.csv` mexido numa cópia da rodada → para no passo 1 ("fora do manifesto", saída 1); uma fonte com outro hash → para no passo 4 ("a fonte não é a da rodada", saída 1) |
| Manifesto próprio | parcial: tem o hash do script (confere com o arquivo), o `rodada_id`, o `fonte_id` e o sha256 da fonte (conferem) e o hash de 14 arquivos gravados (todos conferem no disco). O `passo9_varredura.txt` é gravado e não entra no manifesto (c) |
| Arquivo final aprovado pelo `validar_memoria.py` | ok: `uv run python .claude/skills/mineracao-candidata/scripts/validar_memoria.py analysis/registros/esquema-memoria.json <rascunho>/saida_script/memoria_U_sandbox_base3.json` → "aprovado" (esquema 0.2; 9 campos checados, `impact` pendente) |
| Os campos do passo 8 | **divergência:** o racional pede `validation` = "cobertura, **encontro**, **listas autorizadas**, os números do passo 6; `destino: em aberto`". O arquivo tem `cobertura`, `destino_numeros` (que só traz a **contagem** de listas) e `destino`. Faltam o resultado do encontro (as 24 medidas do passo 7) e as listas. A função `memoria(perfil, t, conf, dest, ids)` nem recebe o encontro. Os outros campos (`category`, `scope`, `location`, `evidence`, `description`, `correction_guidance`, `occurrences`, `impact`) seguem o racional |

Observações que não reprovam, mas ficam registradas:
- **(a)** A lista autorizada é procurada **só no último trecho**; o racional diz "quando a mensagem tem". Nesta base,
  as duas leituras dão 2 listas.
- **(b)** A repetição do passo 6 agrupa por (execução, papel, **tipo**, nome); o racional diz "o mesmo nome". Um nome
  que aparecesse com dois tipos não seria contado como repetição. Nesta base, as duas leituras dão 0.
- **(c)** O `passo9_varredura.txt` é gravado depois do manifesto e fica fora dele. As tabelas da lição estão todas no
  manifesto.
- **(d)** O `status: "derived-and-checked"` é fixo no script. A condição do racional ("se a cobertura passa e o
  encontro fecha") depende de o `minerar.py` parar nos passos 5 e 7, como manda o procedimento 06. Não testei esse caso
  de fora (exigiria uma rodada com cobertura abaixo de 95%).
- **(e)** Empates: datetime e json têm 3 erros cada; ast e autojson, 1 cada; dir e eval, 1 cada. O racional não diz
  como desempatar. O script e a conferência desempatam pela ordem alfabética, e a ordem saiu igual. Os rótulos da
  `correction_guidance` começam todos com maiúscula ("Não importe"); o modelo do racional usa minúscula depois do
  primeiro.
- **(f)** A regra do racional saiu da própria base 1 ("De onde veio a regra": 17/17). Por isso o ensaio da base 1
  confere o código, mas não confirma a hipótese fora da amostra de origem. A confirmação é a rodada na base 3.

## 4 · A ordem do pré-registro

Comandos: `git log --format='%h %ad' --date=iso-strict -- <racional>`, `git diff 9640b13 c544928 -- <racional>`,
`gerado_em` em `<ensaio>/mineracao_U_sandbox/manifesto_mineracao.json`, `ls -D` dos arquivos.

| Momento (16/10/2026, −03:00) | Evento |
|---|---|
| 20:45:08 | commit `9640b13`: o racional original (blob `9477a4c`) |
| 20:46:28–20:47:34 | rodada de ensaio e auditoria gravadas |
| 20:48:43 | última modificação do script |
| **20:51:39** | **primeira rodada do script na base de confirmação** (`gerado_em` 23:51:39Z no manifesto de `<ensaio>/mineracao_U_sandbox/`, com o mesmo hash do script de hoje) |
| **20:51:50** | o `racional.md` é modificado (a nota de 16/10 e mais uma mudança) |
| 20:52:08 | commit `c544928`: o script, o teste, o `minerar.py` e o racional emendado (blob `3873ac4`) |

- O racional **original** (`9640b13`) é anterior à primeira rodada: **ok**.
- O racional **emendado** (a versão em vigor, e a que o script segue) é 11 s **posterior** à primeira rodada na base de
  confirmação: **reprovado**. A nota diz "antes de qualquer rodada na base 3", o que vale para a base 3, mas não para o
  ensaio, que é a base de confirmação desta validação.
- A emenda tem **duas** mudanças na linha da `correction_guidance`, e a nota declara só a primeira (o rótulo "não
  acesse"). A outra, "com mais de uma lista autorizada, uma por grupo de papéis", não é declarada. Ela repete o que a
  linha `scope` já dizia em `9640b13` ("a guidance as separa"). Nenhum limiar mudou.
- O racional não traz o próprio hash escrito: diz "o do commit que traz este arquivo".

## Contagens

- Medidas comparadas: 21 linhas na tabela do item 2; diferenças de número: **0**.
- Itens: 1 ok · 2 ok · 3 **reprovado** (falta o encontro e faltam as listas em `validation`; manifesto parcial) ·
  4 **reprovado** (racional emendado depois da primeira rodada; uma mudança não declarada).
- Observações que não reprovam: 6 (a–f).

---

# Revalidação — 16/10/2026, depois de `aa99b8f` e `2233be7`

**Objeto:** o script `mineracao_U_sandbox.py` (sha256 `087eb1fa…2978cf`), o teste, o `minerar.py` (não aberto, só
testado de fora) e o racional emendado (blob `b299938`). As regras são as do primeiro laudo. Não abri o
`audit_candidata_base3.py` nem o `minerar.py`. Não corrigi nada nem fiz commit. A conferência independente é a mesma do
primeiro laudo, sem nenhuma mudança.

## Veredito: **APROVADO** (falta a aprovação final do Rafael)

As medidas continuam iguais, sem nenhuma diferença. Os dois itens reprovados no primeiro laudo agora passam.

## Itens

| # | Item | Comando | Resultado |
|---|---|---|---|
| 1 | Conferência independente | a mesma do primeiro laudo, gravada em `<rascunho>/conferencia2.json` | ok: o JSON é **idêntico, byte a byte**, ao do primeiro laudo (`cmp`). População 17, cobertura 17/17, 2 listas, 0 repetições |
| 2a | Teste | `uv run python -m unittest analysis.tests.test_mineracao_candidata_base3` | ok: 13 testes, 13 passam. O teste da memória agora cobre o status com o encontro fechado (`derived-and-checked`) e aberto (`parcial`) |
| 2b | Script | `uv run python …/pipeline/especificas/minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script2` | ok: saída 0; passos 1 e 3 a 9 ok (o passo 2 continua "não conferido", como no primeiro laudo); 24 medidas iguais no encontro |
| 2c | Comparação medida por medida | o mesmo script de comparação, sobre a nova saída | **todas iguais:** linhas por erro (17), inventário (10, mesma ordem), nome × papel (14), nome × mês (15), listas (2), cobertura, destino, `location` (6), `evidence` (3), os nomes da guidance por rótulo e as 2 listas da guidance, `occurrences` |
| 3 | Script contra o racional | leitura do diff `b4d1f78..aa99b8f` do script e do teste; `validar_memoria.py`; testes de caixa-preta | **ok** (abaixo) |
| 4 | Ordem do pré-registro | `git log`/`git diff 9640b13 HEAD` do racional; o funil do `06`; `gerado_em` do ensaio refeito | **ok** (abaixo) |

## 3 · O que mudou no item 3

- **`validation`** agora tem `cobertura`, `encontro` (`medidas: 24`, `diferentes: 0`, que conferem com as 24 linhas
  `igual` do `passo7_encontro.json`), `listas_autorizadas` (2 entradas, com lista, erros, papéis e meses **iguais** às
  da conferência), `destino_numeros` e `destino: "em aberto"`. Isso é o que o passo 8 do racional pede. **Fechado.**
- **`status`** agora segue o passo 8: `derived-and-checked` só se a cobertura passa e o encontro fecha; senão,
  `parcial`, valor previsto no esquema (`derived-and-checked | parcial | hipotese`). Nesta base deu
  `derived-and-checked`. A observação (d) do primeiro laudo fica **fechada**.
- **Manifesto:** 15 arquivos, `passo9_varredura.txt` incluído. Todos os hashes conferem no disco, e só o próprio
  manifesto fica fora dele. O hash do script, o `rodada_id` e o sha256 da fonte também conferem. A observação (c) fica
  **fechada**.
- `validar_memoria.py analysis/registros/esquema-memoria.json <rascunho>/saida_script2/memoria_U_sandbox_base3.json`
  → **aprovado**.
- Nenhum texto de caso na saída: a mesma busca dá 0 arquivos. Nenhum import novo: o script continua só com `re` e
  `pandas`. Nenhum limiar novo.
- Caixa-preta, refeita com o `minerar.py` novo: um `casos.csv` mexido para no passo 1 (saída 1), e uma fonte com outro
  hash para no passo 4 (saída 1).
- Continuam abertas, sem efeito nesta base e sem reprovar: as observações (a) (a lista autorizada é procurada só no
  último trecho), (b) (a repetição agrupa também pelo tipo) e (e) (o desempate em ordem alfabética, que o racional não
  fixa, e os rótulos com maiúscula).

## 4 · O que mudou no item 4

- O diff `9640b13..HEAD` do racional mexe só em dois lugares: a linha `correction_guidance` (linha 87) e a emenda logo
  depois da tabela do passo 8. Nenhuma regra, limiar ou população mudou.
- A emenda (`aa99b8f`, 21:01:03) agora **declara as duas mudanças** da guidance e diz que foi feita depois do primeiro
  ensaio na base 1. A mudança que faltava declarar fica **fechada**.
- A emenda também diz que **a base de confirmação é a base 3**: o ensaio na base 1 confere o código, não a hipótese.
  É a observação (f) do primeiro laudo, que fica **fechada**. Com isso, a reprovação do item 4 deixa de valer. A regra
  saiu da base 1, então o ensaio nunca poderia confirmar a hipótese. E o conteúdo de que a ordem trata (regras, limiar,
  população) é o de `9640b13` (20:45:08), anterior a qualquer rodada do script.
- **O hash do pré-registro** está no funil do `06` (`2233be7`): "racional: `9640b13`, emenda `aa99b8f`". O racional
  aponta para lá. **Fechado.**
- O ensaio foi refeito às 21:01:09 (`gerado_em` 00:01:09Z), **depois** do commit `aa99b8f`.
- **Condição para a base 3:** a primeira rodada do script na base 3, na máquina 2, ainda não existe. Ela precisa rodar
  com um HEAD que contenha `aa99b8f`, e a data dela precisa ser posterior a 16/10/2026 21:01:03 (−03:00). Daqui não dá
  para conferir; quem rodar confere com o `git log`.

## Contagens da revalidação

- Medidas comparadas: as mesmas 21; diferenças de número: **0**. Encontro do script: 24 medidas, 0 diferentes.
- Itens: 1 ok · 2 ok · 3 ok · 4 ok (com a condição da base 3 acima).
- Observações do primeiro laudo: (c), (d) e (f) fechadas; (a), (b) e (e) continuam abertas, sem efeito nesta base.

---

**Revalidação 2 — 16/10/2026, depois de `1f76600` (só a observação b):** **fechada, e o veredito continua APROVADO.**
O script (sha256 `39481621…`, o mesmo do manifesto) agora agrupa a repetição do passo 6 por (execução, papel, nome),
sem o tipo, como diz o racional; o `minerar.py` não mudou neste commit. Comandos e resultados:
- `uv run python -m unittest analysis.tests.test_mineracao_candidata_base3`: 14 testes, 14 passam. O teste novo cobre
  um nome repetido com dois tipos.
- `minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script4`:
  saída 0, encontro com 24 medidas e 0 diferentes, `status` `derived-and-checked`, `validar_memoria.py` aprovado.
- Conferência: o JSON é idêntico ao do primeiro laudo.
- Destino, script × conferência: 2 listas distintas × 2; lista única = não × não; erros que repetem o nome na mesma
  execução e papel 0 × 0 (17 grupos, 0 com repetição); execuções com repetição 0 × 0. **Diferenças: 0.**

Observações que continuam abertas, sem efeito nesta base: (a) e (e).

---

# Revalidação 3 — 16/10/2026, depois de `fd93e93` (emenda 2 do racional)

**Veredito: continua APROVADO.** A emenda 2 está declarada e só mexe na população em prosa do passo 1. A conferência
foi atualizada por ela e segue com 17 erros. O script não mudou desde a revalidação 2 (sha256 `39481621…`) e as
saídas dele são as mesmas.

1. **A emenda (`git show fd93e93 -- …/racional.md`): ok.** O diff tem **um só trecho**, na prosa da população do
   passo 1. Os três sinais novos entram com os padrões literais: bloco de código (`regex pattern`), falha do LLM
   (`AgentGenerationError`, `internally hosted`, `Error code: 422`, `UnprocessableEntity`) e timeout de ferramenta
   (`excedeu o timeout`, `TimeoutError`). A nota diz **o que** mudou (os três sinais), **por quê** (a primeira rodada na
   base 3, `observada_e3ebc8274dcf108c`, divergiu em 1 erro de 3.653, com função proibida e timeout de ferramenta na
   mesma mensagem; o pipeline o pôs no timeout, a auditoria no sandbox; registrado em `passo7_divergencia.csv`),
   **quando** (depois da primeira rodada na base 3) e **quem** decidiu (Rafael). Não mudam a população da mineração (a
   da rodada), as regras do passo 4, a lista de imports nem o limiar de 95%. No mesmo commit também mudaram a auditoria
   e o teste, e o script não mudou.
2. **Conferência atualizada e rodada no ensaio: ok.** Acrescentei os três sinais com os padrões literais da emenda em
   `SINAIS_ANTES`. Comando:
   `conferencia_independente.py --fonte <ensaio>/fonte_base1_v1.parquet --casos … --perfil … --json <rascunho>/conferencia4.json`.
   - população pela prosa: **17**, as mesmas 17 chaves da rodada (0 só de um lado), 0 excluídos por sinal;
   - o JSON das medidas saiu **idêntico** ao do primeiro laudo;
   - nos erros com tipo do ensaio, os sinais novos casam assim: bloco de código 33, falha do LLM 7, timeout de
     ferramenta 0. Nenhum desses erros entraria no sandbox.
3. **Teste e script: ok.**
   - `uv run python -m unittest analysis.tests.test_mineracao_candidata_base3`: 16 testes, 16 passam.
   - `minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script5`:
     saída 0; passos 1 e 3 a 9 ok; encontro com 24 medidas e 0 diferentes; `status` `derived-and-checked`;
     `validar_memoria.py` aprovado; manifesto com 15 arquivos e hashes conferidos; nenhum texto de caso na saída.
   - As cinco tabelas CSV são iguais byte a byte às da revalidação 2. `passo5_confianca.json`, `passo6_destino.json` e
     o bloco `memoria` do arquivo final também são iguais.

**Observações (não reprovam):**
- **(g)** A emenda alinha a definição da auditoria ao pipeline **depois** de ver a divergência. Isso é aceitável: o
  princípio ("os sinais que o pipeline decide antes") já estava no pré-registro, só a lista estava incompleta, e a
  emenda está declarada e decidida pelo Rafael. Mesmo assim, na base 3 o encontro desse 1 erro deixa de ser às cegas:
  a divergência original continua sendo o achado e precisa ficar no `passo7_divergencia.csv`. Não conferi o
  1 de 3.653 porque a base 3 não está nesta máquina. Também não conferi a ordem de decisão do pipeline, porque não
  abri o `minerar.py` nem o pipeline.
- **(h)** A conferência deste validador já tirava esse caso antes da emenda. A minha leitura de "tempo do
  interpretador" (`[Tt]ime ?out|timed out|execution time`) cobre `TimeoutError` e `excedeu o timeout`. Duas leituras
  independentes da mesma prosa deram fronteiras diferentes, e a emenda deixa o padrão literal.

**Contagens:** população 17 = 17 · medidas 21, diferenças 0 · encontro 24/24 · testes 16/16 · observações abertas
(a), (e), (g), (h).

---

# Revalidação 4 (emenda 4, 19/10)

**Objeto:** o script `pipeline/especificas/mineracao_U_sandbox.py` (sha256 `6c28c037…fd656`, o mesmo do manifesto),
o `minerar.py` (sha256 `ae17ddcc…`), o teste `analysis/tests/test_mineracao_candidata_base3.py`, o racional com as
emendas 3 e 4 (blob `811bbd3`, commit `c36641c`). HEAD `76c58f8`. Rodada de ensaio `bf2d034f248cfd74…` (regravada em
19/10 12:51), fonte `fonte_base1_v1.parquet` (sha256 `afaf3e98…30717ae` = `fonte_id`). O validador não corrigiu
nada nem fez commit; só a `conferencia_independente.py` (que é dele) mudou.

## Veredito: **REPROVADO**

As medidas da lição (população, cobertura, inventário, listas, destino, erros por parte, erro → memória, catálogo)
batem. Mas o passo 8 por parte tem **4 medidas diferentes**, e o script tem regras de montagem que o racional não
tem (item 3). Pelas regras do validador, não há aprovação com divergência.

## Itens

| # | Item | Comando | Resultado |
|---|---|---|---|
| 1 | Conferência independente, só do racional (emendas 3 e 4) | `uv run python …/propostas/U_sandbox/conferencia_independente.py --fonte <ensaio>/fonte_base1_v1.parquet --casos <ensaio>/rodada/perfis/U_sandbox/casos.csv --perfil <ensaio>/rodada/perfis/U_sandbox/perfil.csv --json <rascunho>/conferencia_rev4.json` | ok: população pela prosa **16** = rodada 16 (0 só de um lado). A emenda 3 tira **1** erro (`globals` que verifica e guarda a criação). Cobertura 16/16. Partes: C 6 · E 7 · D 3 · B 0 · sem parte 0. Memórias: `U_sandbox.C`, `U_sandbox.E`, `U_sandbox.D.ConversationAgent`, `U_sandbox.D.managerAgent`. Rodada duas vezes, o JSON sai idêntico (`cmp`) |
| 2a | Teste | `uv run python -m unittest analysis/tests/test_mineracao_candidata_base3.py` | ok: 19 testes, 19 passam |
| 2b | Script | `uv run python …/pipeline/especificas/minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script` | saída 0. Passos 1 e 3 a 9 ok; o passo 2 diz "não conferido", como antes. Encontro: **28 medidas, 28 iguais** (4 delas são as partes). 4 memórias gravadas, catálogo com 3 fechadas e 1 fora (E, destino em aberto). `resultados/` não foi tocado |
| 2c | Comparação medida por medida | `<rascunho>/comparar_base.py` (14 medidas da lição) e `<rascunho>/comparar.py` (71 medidas das memórias e do catálogo) | lição: **14/14 iguais**. Memórias e catálogo: **67/71 iguais, 4 diferentes** (abaixo) |
| 3 | Script contra o racional | leitura do script; `validar_memoria.py` em cada arquivo; manifesto; busca de texto de caso; imports | **reprovado:** há regras de montagem do passo 8 que não estão no racional (abaixo). O resto está ok |
| 4 | Ordem | `git log --date=iso-strict` do racional; `git show c36641c --stat`; `gerado_em` dos manifestos | B está declarada como descritiva: ok, como o racional declara. Há regras novas **não declaradas** (abaixo) |

`<ensaio>` = `analysis/2026-10-trace-law-flow-third/pipeline/resultados/ensaio_base1`; `<rascunho>` = pasta de
rascunho do validador, fora do repositório.

## 2 · As medidas

**A lição (14 medidas, todas iguais).** São estas: população 16; população pela prosa igual à da rodada; execuções,
papéis e meses (16 · 5 · 7); as 16 linhas por erro; o inventário (10 linhas, na mesma ordem); nome × papel; nome ×
mês; as listas autorizadas (2, com os mesmos papéis e meses); a cobertura (16/16, passa); o `sem_nome` (vazio); o
destino (2 listas, lista única = não, 0 repetições); os erros por parte (C 6 · D 3 · E 7); e a memória de cada erro
(as 16 chaves).

**As memórias e o catálogo (71 medidas, 4 diferentes).**

| Medida | Conferência (racional) | Script | Igual? |
|---|---|---|---|
| Ids das memórias | C, D.ConversationAgent, D.managerAgent, E | os mesmos | sim |
| Erros · execuções · papéis · meses por memória (`partes.csv`) | C 6·6·2·3 · D.Conv 2·2·1·1 · D.mgr 1·1·1·1 · E 7·7·3·6 | os mesmos | sim |
| `scope.role` | C e E `null`; cada D no seu papel | o mesmo | sim |
| Destino | C, D: memória; E: em aberto | o mesmo | sim |
| `status` | derived-and-checked nas 4 | o mesmo | sim |
| `location` de C, E, D.managerAgent | o primeiro de cada papel, na ordem (papel, mês, `step_ref`) | os mesmos casos | sim |
| **`location` de D.ConversationAgent** | **1 caso** (o primeiro do papel, que é o único) | **2 casos** (todos do papel, até 10) | **não** |
| **`evidence` de C** | **1 caso** (C tem um tipo só, `modulo_sem_import`) | **2 casos** (um por **nome**: datetime, json) | **não** |
| **`evidence` de E** | **2 casos**, um por tipo: `funcao_proibida`/repr, `atributo_dunder`/`__name__` | **3 casos**, um por **nome**: repr, dir, globals; o `atributo_dunder` fica de fora | **não** |
| `evidence` das duas D | um por tipo | os mesmos casos (em D, cada tipo tem um só nome) | sim |
| **`correction_guidance` de E** | "não chame: repr, dir, eval, globals; não acesse: `__name__`" | "não chame: repr, dir, **globals, eval**; não acesse: `__name__`" | **não** (o empate entre nomes com 1 erro) |
| `correction_guidance` de C e das duas D (rótulos e nomes; D com a lista do papel no mês mais recente) | C: importe antes de usar datetime, json · D.Conv: não importe autojson, não existe openpyxl, lista de 13 · D.mgr: não importe ast, lista de 11 | os mesmos | sim |
| `occurrences` (erros, execuções, meses) por memória | as contagens da parte | as mesmas | sim |
| Catálogo: ids | C, D.ConversationAgent, D.managerAgent (destino memória e derived-and-checked) | os mesmos; E fica fora | sim |
| Catálogo: sem `location`/`evidence`; só memória + derived-and-checked; `category`/`scope`/`description`/`correction_guidance` iguais aos dos arquivos; `sha256_16` confere com o arquivo | sim | sim | sim |

## 3 · O script contra o racional

| Conferência | Resultado |
|---|---|
| A parte de cada erro (emenda 4: C, E, B pela lista, D os outros) | ok. O script aplica o pacote de topo (`nome.split('.')[0]`) a todos os nomes de B; o racional dá o framework e os nomes exatos. Nesta base não muda nada (B = 0) |
| Escopo e destino por parte | ok (`PARTES`) |
| D com a lista do papel no mês mais recente | ok. Em caso de empate, o script escolhe "a mais frequente" e depois a ordem alfabética, o que o racional não diz. Nesta base não muda nada (1 lista por papel no mês) |
| **`location` por papel** | **fora do racional:** em B e D, o script grava até 10 casos do papel (`head(10)`). O racional diz "o primeiro de cada papel" |
| **`evidence`** | **fora do racional:** o script pega um caso por **nome** (`P.nome.value_counts()[:3]`). O racional diz "o primeiro de cada um dos três **tipos** mais frequentes". Era por tipo até a revalidação 3 |
| **`category`** | **fora do racional:** "Inventário do sandbox · \<rótulo da parte\> (factual · ambiente)". O racional dá "Inventário do sandbox (factual · ambiente)", e os 4 rótulos das partes (`PARTES`) não estão nele |
| **`correction_guidance` de B** | **fora do racional:** a frase fixa "As ferramentas já estão no escopo como funções: chame-as direto, sem import." é texto livre (o racional diz "montada da tabela, sem texto livre"). Além disso, `modulo_ausente` vai para "Não importe", e não para "não existe no ambiente". O teste fixa essa frase (`test_ferramenta_por_papel`). Nesta base não aparece (B = 0) |
| `correction_guidance`: o empate | o racional não fixa o desempate ("por ordem de erros"). O script usa a ordem do `value_counts` e a conferência, a alfabética. Em E, os três nomes com 1 erro saíram em ordem diferente. É a observação (e) de antes, que agora muda o resultado |
| `occurrences` por parte | o script grava `ocorrencias = erros` da parte (o perfil é da unidade inteira). O racional diz "do perfil da rodada" e a emenda 4 não diz como fazer por parte. As contagens batem com as da conferência |
| `description` | é montada das contagens, mas por **nome** e com o rótulo da parte; o racional diz "de que tipos". Não reprova sozinha |
| Sem LLM nem serviço externo | ok: o script importa só `re` e `pandas`. O `subprocess` do `minerar.py` roda só os scripts locais (auditoria e validador) |
| Limiar | ok: `LIMIAR_COBERTURA = 0.95` |
| Texto de caso | ok: busca por `due to`, `Code execution`, `InterpreterError`, `Forbidden`, `Traceback`, `at line` → 0 arquivos na saída |
| Rodada pelo código do pipeline e manifesto | ok: o manifesto tem o hash do `minerar.py`, do script, da auditoria e do esquema, o `rodada_id` e o sha256 da fonte (conferem), e **21 artefatos, todos com o hash conferido no disco**. Só o próprio manifesto fica fora dele |
| `validar_memoria.py` (esquema 0.3) | ok: `uv run python .claude/skills/mineracao-candidata/scripts/validar_memoria.py analysis/registros/esquema-memoria.json <rascunho>/saida_script/memoria_<id>_base3.json` → **aprovado** nos 4 arquivos |
| Catálogo | ok: só as 3 memórias com destino memória e derived-and-checked; E (em aberto) fica fora; nenhuma entrada tem `location` nem `evidence` |

## 4 · A ordem

- Emenda 4: commit `c36641c`, 2026-10-19 12:52:50 −03:00. É **o mesmo commit** que traz a versão do script com as
  partes. O racional em vigor tem o blob `811bbd3`.
- A rodada de ensaio foi regravada às 12:51 (antes do commit). Em `resultados/ensaio_base1/mineracao_U_sandbox/`, o
  manifesto é de 11:00:42 −03:00 e tem o script **antigo** (`39481621…`), anterior à emenda 4. O ensaio do script com
  as partes, que o commit cita ("ensaio base 1 ok"), não ficou gravado, então não dá para datar. A rodada deste
  validador é de 13:03 −03:00, depois do commit.
- **Base 3 (a base de confirmação):** a primeira rodada do script com as partes ainda não está nesta máquina. Ela tem de
  rodar com um HEAD que contenha `c36641c` e ser posterior a 19/10 12:52:50 −03:00. Quem rodar confere.
- **Declarado no racional:** a lista de B foi escrita olhando a base 3 (rodada `85706f1e`, dossiê §2b) e é descritiva,
  não pré-registrada. Está declarada, então não reprova.
- **Emenda 3** (`0e76a98`, 11:02:15): ainda não tinha sido revalidada. Entrou na conferência agora e dá o mesmo
  resultado (o mesmo erro sai, 17 → 16). Ela foi escrita depois da primeira mineração na base 3 (é o gatilho do
  Ajuste 21), mas o racional só diz isso pela referência ao Ajuste 21. Não diz que é descritiva.
- **Regras novas que o racional NÃO declara** (estão no script de `c36641c`, não estão na emenda 4):
  1. `location` com até 10 casos do papel em B e D;
  2. `evidence` por nome, e não por tipo;
  3. a `category` com o rótulo da parte, e os 4 rótulos;
  4. a frase fixa da guidance de B, e `modulo_ausente` sob "Não importe";
  5. o desempate da lista do papel ("a mais frequente");
  6. `occurrences` por parte com `ocorrencias = erros`;
  7. o rótulo "imports autorizados neste papel".

## Divergências, medida por medida

1. `U_sandbox.D.ConversationAgent` · `location`: conferência 1 caso × script 2 casos.
2. `U_sandbox.C` · `evidence`: 1 caso (um tipo) × 2 casos (um por nome).
3. `U_sandbox.E` · `evidence`: 2 casos (repr, `__name__`) × 3 casos (repr, dir, globals; sem o `atributo_dunder`).
4. `U_sandbox.E` · `correction_guidance`: a ordem de dir, eval e globals, empatados com 1 erro cada. O racional não fixa o
   desempate.

## Contagens da revalidação 4

- Testes 19/19 · encontro do script 28/28 · medidas da lição 14/14 · memórias e catálogo **67/71 (4 diferentes)**.
- População 16 = 16 (a emenda 3 tira 1). Memórias: 4 (C 6, E 7, D.ConversationAgent 2, D.managerAgent 1; B 0).
  `validar_memoria` aprova as 4. Catálogo: 3 fechadas, 1 fora.
- Itens: 1 ok · 2 **4 divergências** · 3 **reprovado** (regras de montagem fora do racional) · 4 B declarada; 7 regras
  novas não declaradas.

---

# Revalidação 5 (19/10)

**Objeto:** o script `pipeline/especificas/mineracao_U_sandbox.py` (sha256 `42f79ff7…c8187a`, o mesmo do manifesto),
o `minerar.py` (sha256 `ae17ddcc…25f7`), a auditoria `audit/scripts/audit_candidata_base3.py` (`acb36184…`), o teste
`analysis/tests/test_mineracao_candidata_base3.py` e o racional com a tabela "O arquivo final de cada parte" (blob
`b6a94a5`, commit `f4037cc`). HEAD `f4037cc`. Rodada de ensaio `bf2d034f248cfd74…`, fonte `fonte_base1_v1.parquet`
(sha256 `afaf3e98…30717ae` = `fonte_id`). O validador não corrigiu nada nem fez commit; só a
`conferencia_independente.py` (que é dele) mudou.

## Veredito: **REPROVADO**

As 7 regras que a revalidação 4 achou fora do racional agora estão na tabela da emenda 4, e as 4 diferenças da
revalidação 4 fecharam. Sobra **1 regra fora do molde**, que dá **4 medidas diferentes**: o script fecha a
`description` de cada memória com um ponto final. O molde do racional não tem esse ponto. As moldes da
`correction_guidance` têm o ponto escrito; o da `description` termina em "…". Tirando o ponto, as 4 descrições são
iguais à da conferência. Pelas regras do validador, não há aprovação com divergência. Para fechar, ou o racional põe o
ponto no molde ou o script tira o ponto. A escolha é do Rafael.

## Itens

| # | Item | Comando | Resultado |
|---|---|---|---|
| 1 | Conferência independente, só do racional (a tabela nova da emenda 4) | `uv run python …/propostas/U_sandbox/conferencia_independente.py --fonte <ensaio>/fonte_base1_v1.parquet --casos <ensaio>/rodada/perfis/U_sandbox/casos.csv --perfil <ensaio>/rodada/perfis/U_sandbox/perfil.csv --json <rascunho>/conferencia_rev5_1.json` | ok. A conferência monta, para cada memória, `category`, `scope`, `location`, `evidence`, `description`, `correction_guidance`, `occurrences`, a parte na `validation` e `impact`, todos tirados da tabela. Nomes por erros, e no empate a ordem alfabética. A lista do papel D vem do mês mais recente; no empate, a com mais erros e depois a alfabética. População **16** = rodada 16; a emenda 3 tira **1** erro. Cobertura 16/16. Partes: C 6 · E 7 · D 3 · B 0. Rodada duas vezes: JSON idêntico (`cmp`) |
| 2a | Teste | `uv run python -m unittest analysis/tests/test_mineracao_candidata_base3.py` | ok: **19 testes, 19 passam** |
| 2b | Script | `uv run python …/pipeline/especificas/minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script` | saída 0. Passos 1 e 3 a 9 ok; o passo 2 diz "não conferido", como antes. Encontro: **28 medidas, 28 iguais**. 4 memórias aprovadas no esquema 0.3. Catálogo: 3 fechadas, 1 fora (E, destino em aberto). Varredura limpa. `resultados/ensaio_base1/mineracao_U_sandbox/` não foi tocado (`stat` antes e depois, iguais) |
| 2c | Comparação medida por medida | `python3 <rascunho>/comparar.py <rascunho>` | lição: **14/14 iguais**. Memórias e catálogo: **92/96 iguais, 4 diferentes** (o ponto final da `description`, abaixo). Total 106/110 |
| 3 | Script contra o racional | leitura do script; `validar_memoria.py` em cada arquivo; manifesto; busca de texto de caso; imports | **reprovado só pelo ponto final da `description`** (um caractere fixo que não está no molde; é a mesma divergência do item 2). O resto está ok (abaixo) |
| 4 | Ordem | `git log --date=iso-strict` do racional e do script; `gerado_em` do manifesto do rascunho | ok no que dá para ver. A tabela nova se declara descritiva, e a emenda 3 também. A primeira rodada do script novo na base 3 ainda não existe: fica como **condição** (abaixo) |

`<ensaio>` = `analysis/2026-10-trace-law-flow-third/pipeline/resultados/ensaio_base1`; `<rascunho>` = pasta de
rascunho do validador, no scratchpad, fora do repositório.

## 2 · As medidas

**A lição (14 medidas, todas iguais).** População; população pela prosa = rodada; nenhum erro só de um lado;
execuções · papéis · meses (16 · 5 · 7); as 16 linhas por erro; o inventário (10 linhas, na mesma ordem); nome × papel;
nome × mês; as 2 listas autorizadas (erros, papéis, meses); a cobertura (16/16, passa); o `sem_nome` (vazio); o
passo 6 (2 listas, lista única = não, 0 repetições); os erros por parte (C 6 · D 3 · E 7); a memória de cada erro (16
chaves).

**As memórias e o catálogo (96 medidas, 4 diferentes).** Para cada uma das 4 memórias (C, D.ConversationAgent,
D.managerAgent, E), estas medidas:

| Medida (por memória) | Igual nas 4? |
|---|---|
| cabeçalho (`id`, `parte`, `esquema` 0.3); erros · execuções · papéis · meses (`partes.csv`: C 6·6·2·3 · D.Conv 2·2·1·1 · D.mgr 1·1·1·1 · E 7·7·3·6) | sim |
| `category` (com o rótulo da parte) | sim |
| `scope` (`role` null em C e E; o papel em D; `tool` null) | sim |
| `location.total_erros` e os casos: em C e E, o primeiro de cada papel, na ordem (papel, mês, `step_ref`); em D, os 10 primeiros, na ordem (mês, `step_ref`). D.ConversationAgent agora tem 2 = 2 | sim |
| `location`: `fonte_id` e `rodada_id` em cada caso | sim |
| `evidence`: o primeiro caso de cada um dos 3 nomes com mais erros (C: datetime, json · E: repr, `__name__`, dir · D: um por nome) | sim |
| **`description`** | **não, nas 4: o script põe um "." no fim** |
| `correction_guidance` (E: "Não chame: repr, dir, eval, globals; Não acesse: `__name__`." · C: datetime, json · D com a lista do papel no mês mais recente) | sim |
| `occurrences` (erros, `ocorrencias` = erros, execuções, a lista dos meses) | sim |
| `status` derived-and-checked | sim |
| `validation`: a parte (código, rótulo, escopo "global"/"papel", como a emenda 4 diz); cobertura; o encontro fecha; as listas autorizadas da parte; o passo 6 com as repetições do nome na parte (0); o destino (C, D: memória; E: em aberto); onde foi decidido (C, D: preenchido; E: null) | sim |
| `impact` null | sim |

Catálogo: os ids (C, D.ConversationAgent, D.managerAgent); nenhuma entrada com `location` ou `evidence`; só as fechadas
(destino memória e derived-and-checked); `category`, `scope`, `description` e `correction_guidance` iguais às dos
arquivos; `occurrences` igual; `sha256_16` confere com o arquivo; `rodada_id` e `fonte_id` conferem. **Tudo igual.**
O catálogo copia a `description` do arquivo, então o ponto final está nele também.

**Uma correção na conferência (é do validador).** Na primeira passada, a conferência esperava o nome do papel no
`validation.parte.escopo` das D. A emenda 4 dá o escopo de cada parte como "global" (C, E) ou "uma memória por papel"
(B, D), e o script grava "global"/"papel". Isso segue o racional, então a conferência passou a esperar isso. Não é
divergência do script.

## 3 · O script contra o racional

| Conferência | Resultado |
|---|---|
| As 7 regras que a revalidação 4 achou fora do racional: `location` em B/D; `evidence` por nome; `category` com os 4 rótulos; a frase fixa de B e `modulo_ausente` sob "Não importe"; o desempate da lista do papel; `occurrences` por parte com `ocorrencias` = erros; "imports autorizados neste papel" | **todas declaradas** na tabela da emenda 4, e o código faz o que a tabela diz |
| O desempate (por erros, empate alfabético) | ok: `_por_erros` na guidance, na `evidence` e na `description`. `_lista_do_papel`: mais erros, depois alfabética (`sort_index` e então ordenação estável por contagem). A docstring diz só "empate: a mais frequente" |
| **`description`** | **fora do molde:** `… + ".")`. O molde do racional não tem ponto final |
| A parte de cada erro | ok, a mesma observação da revalidação 4: o script testa o pacote de topo (`nome.split('.')[0]`) também nos nomes `tools`, `tool_usage`, `tool_functions`, `python_interpreter`, e o racional dá esses nomes exatos. Nesta base não muda nada (B = 0) |
| A lista autorizada | o script a lê do último trecho (depois de `due to:`); o racional diz "quando a mensagem tem". Nesta base dá o mesmo (2 listas, iguais às da conferência) |
| Sem LLM nem serviço externo | ok: o script importa só `re` e `pandas`. O `subprocess` do `minerar.py` roda só os scripts locais (auditoria e validador). Nenhum `http`, `requests` nem cliente de modelo |
| Limiar e constantes | ok: `LIMIAR_COBERTURA = 0.95`. `PARTES` (rótulos, escopo, destino) e `FERRAMENTAS` estão no racional. `ESTADOS_INTEGROS = {"sem_corte_sql"}` é a mensagem íntegra do passo 4 |
| Texto de caso | ok: busca na saída por `due to`, `Code execution`, `InterpreterError`, `Forbidden`, `Traceback`, `at line`, `is not allowed`, `is not defined`, `No module named` → **0 arquivos** |
| Rodada pelo código do pipeline e manifesto | ok: a rodada e a fonte são lidas por `mo.ler_artefato` e `bp.carregar_carga`. O manifesto traz o hash do `minerar.py`, do script, da auditoria e do esquema (conferem com o disco), o `rodada_id` e o `fonte_id`/`fonte_sha256` (conferem), e **21 artefatos, 21 com o hash conferido**. Nenhum arquivo gravado fica fora dele, só o próprio manifesto |
| `validar_memoria.py` (esquema 0.3) | ok: `uv run python .claude/skills/mineracao-candidata/scripts/validar_memoria.py analysis/registros/esquema-memoria.json <rascunho>/saida_script/memoria_<id>_base3.json` → **aprovado** nos 4 arquivos |
| Catálogo | ok: só as 3 memórias com destino memória e derived-and-checked; E (em aberto) fica fora; nenhuma entrada tem `location` nem `evidence` |

## 4 · A ordem

- Racional em vigor: blob `b6a94a5`, commit `f4037cc`, 2026-10-19T13:08:44−03:00. Esse commit traz também a mudança do
  script (`_por_erros`). A rodada deste validador é de 13:26:38 −03:00 (`gerado_em` do manifesto do rascunho), depois do
  commit.
- **Declarado no racional:** a tabela "O arquivo final de cada parte" foi escrita depois do ensaio na base 1 e da
  rodada `85706f1e` da base 3. É descritiva e não muda população, regras do passo 4 nem limiar. A emenda 3 agora se diz
  descritiva (escrita depois da primeira mineração na base 3 e do teste da regra (b) nela). A lista de B já estava
  declarada. Nada do que o script faz fica sem declaração, fora o ponto final da `description`.
- **Condição, não divergência:** a primeira rodada do script de `f4037cc` na base 3 (a base de confirmação) ainda não
  existe nesta máquina. Ela tem de rodar com um HEAD que contenha `f4037cc` e depois de 2026-10-19T13:08:44−03:00. Quem
  rodar confere.

## Divergências, medida por medida

1. `U_sandbox.C` · `description`: conferência "…: datetime 3, json 3" × script "…: datetime 3, json 3**.**"
2. `U_sandbox.D.ConversationAgent` · `description`: a mesma diferença (o "." no fim).
3. `U_sandbox.D.managerAgent` · `description`: a mesma diferença.
4. `U_sandbox.E` · `description`: a mesma diferença.

As quatro vêm de uma regra só: o ponto final que o script acrescenta e o molde não tem. As 3 entradas do catálogo
carregam a mesma `description` do arquivo.

## Contagens da revalidação 5

- Testes 19/19 · encontro do script 28/28 · medidas da lição 14/14 · memórias e catálogo **92/96 (4 diferentes,
  uma regra só)** · total 106/110.
- População 16 = 16 (a emenda 3 tira 1). Memórias: 4 (C 6, E 7, D.ConversationAgent 2, D.managerAgent 1; B 0).
  `validar_memoria` aprova as 4. Catálogo: 3 fechadas, 1 fora. Manifesto: 21/21 hashes.
- Das 4 divergências da revalidação 4, as 4 fecharam. Das 7 regras não declaradas, as 7 estão declaradas.
- Itens: 1 ok · 2 **4 divergências** (o ponto final da `description`) · 3 **reprovado** pelo mesmo ponto, o resto ok
  · 4 ok, com a condição da primeira rodada na base 3.

---

# Revalidação 5, conclusão (19/10)

**Objeto:** o racional do commit `ef36e2c` (2026-10-19T13:54:31−03:00). A única mudança é uma linha: o molde da
`description`, na tabela da emenda 4, ganhou o ponto final. O script, o `minerar.py`, a auditoria, o teste, o esquema e
o `validar_memoria.py` estão como em `f4037cc` (`git diff f4037cc HEAD` sobre eles: vazio). Os hashes do manifesto
também batem: `minerar.py` `ae17ddcc…`, script `42f79ff7…`, auditoria `acb36184…`, esquema `9fdd70fe…`. O validador
não corrigiu nada; só a `conferencia_independente.py` (que é dele) mudou: o molde da `description` agora termina com
ponto.

## Veredito: **APROVADO** (falta a aprovação final do Rafael)

A divergência que restava, o ponto final da `description`, fechou no racional. Não sobra nenhuma divergência nem
nenhum item faltando.

| # | Item | Resultado |
|---|---|---|
| 1 | Conferência só a partir do racional (`ef36e2c`) | ok: população 16 = 16; cobertura 16/16; partes C 6 · E 7 · D 3 · B 0. Rodada duas vezes, o JSON sai idêntico (`cmp`) |
| 2a | Teste (`uv run python -m unittest analysis/tests/test_mineracao_candidata_base3.py`) | ok: 19/19 |
| 2b | Script (`minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script`) | saída 0. Encontro 28/28 iguais; 4 memórias; catálogo com 3 fechadas e 1 fora (E). `resultados/` não foi tocado (`stat` antes e depois) |
| 2c | Comparação medida por medida (`python3 <rascunho>/comparar.py <rascunho>`) | lição **14/14**; memórias e catálogo **96/96**; total **110/110** |
| 3 | Script contra o racional | ok: o ponto final está no molde. O resto é como na seção anterior: sem LLM nem serviço externo, limiar 0.95, nenhum texto de caso (0 arquivos), manifesto com 21/21 hashes conferidos, `validar_memoria.py` aprova as 4, catálogo só com as fechadas e sem `location`/`evidence`. As duas observações de antes não mudam nada nesta base: o pacote de topo nos nomes de B (B = 0) e a lista autorizada lida do último trecho |
| 4 | Ordem | ok no que dá para ver: racional em `ef36e2c` (13:54:31 −03:00), rodada deste validador às 13:55:00 −03:00. A mudança é de forma e está declarada na própria linha ("revalidação 5"). Como a tabela inteira, é descritiva |

**Condição da ordem, na base 3 (não é divergência):** a primeira rodada deste script na base 3, a base de
confirmação, ainda não existe nesta máquina. Ela tem de rodar com um HEAD que contenha `ef36e2c` e depois de
2026-10-19T13:54:31−03:00, e quem rodar confere a data contra o `git log` do racional.

## Contagens da conclusão

- Testes 19/19 · encontro do script 28/28 · lição 14/14 · memórias e catálogo 96/96 · total 110/110 · 0 divergências.
- Memórias: 4 (C 6, E 7, D.ConversationAgent 2, D.managerAgent 1; B 0), as 4 aprovadas pelo `validar_memoria`
  (esquema 0.3). Catálogo: 3 fechadas, 1 fora (E, destino em aberto). Manifesto: 21/21.

---

# Revalidação 6 (emendas 5 e 6, 19/10)

**Objeto:**
- o racional com as emendas 5 (`364cbd8`, 2026-10-19T14:32:13−03:00) e 6 (`7b4e4e0`, 14:43:26−03:00; blob `1fd0ac7`);
- o script `mineracao_U_sandbox.py` (sha256 `9ea1c33b…`, de `7b4e4e0`);
- o `minerar.py` (`ae17ddcc…`, sem mudança);
- a auditoria `audit_candidata_base3.py` (`e9ef1180…`, de `364cbd8`);
- o `base_pipeline.py` da base 3 (`8429c4a3…`);
- o teste `test_mineracao_candidata_base3.py`.

HEAD `7b4e4e0`. A rodada de ensaio foi refeita: `3e5d9127c1aa1225…`, 2026-10-19T14:31:19−03:00, com a fonte
`fonte_base1_v1.parquet` (`afaf3e98…`). O validador não corrigiu nada nem fez commit; só a
`conferencia_independente.py` (que é dele) mudou.

## Veredito: **APROVADO** (falta a aprovação final do Rafael), com uma observação para a base 3

Todas as medidas batem (114/114), e cada mudança do script corresponde a uma regra das emendas 5 e 6. A observação
(abaixo) é sobre a regra da emenda 5 no pipeline e na auditoria, não sobre o script. Na base 1 ela não aparece (0 casos),
então não é divergência medida.

| # | Item | Comando | Resultado |
|---|---|---|---|
| 1 | Conferência só a partir do racional (emendas 5 e 6) | `uv run python …/propostas/U_sandbox/conferencia_independente.py --fonte <ensaio>/fonte_base1_v1.parquet --casos <ensaio>/rodada/perfis/U_sandbox/casos.csv --perfil <ensaio>/rodada/perfis/U_sandbox/perfil.csv --json <rascunho>/conferencia_rev6_1.json` | ok. Emenda 5: a emenda 3 vale também para `eval`, só pelo braço da função escrita pelo agente (não embutida), que recebe o nome entre aspas e cria a variável na linha, e com a chamada que não é `globals`/`locals`/`vars`/`eval`. Emenda 6: E tem destino memória, e a guidance de E ganha o complemento fixo. Na base 1, o único `eval` fica em E. Resultado: população **16** = rodada 16 (0 só de um lado); a emenda 3 tira 1 erro; cobertura 16/16; partes C 6 · E 7 · D 3 · B 0. Rodada duas vezes, o JSON sai idêntico (`cmp`) |
| 2a | Teste | `uv run python -m unittest analysis/tests/test_mineracao_candidata_base3.py` | ok: **19/19** |
| 2b | Script | `uv run python …/pipeline/especificas/minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script` | saída 0. Passos 1 e 3 a 9 ok; o passo 2 diz "não conferido", como antes. Encontro **28/28**; 4 memórias aprovadas no esquema 0.3; catálogo com **4 fechadas, 0 fora** (E entrou). `resultados/` não foi tocado (`stat` antes e depois) |
| 2c | Comparação medida por medida | `python3 <rascunho>/comparar.py <rascunho>` | lição **14/14**; memórias e catálogo **100/100** (com as 4 entradas de E no catálogo); total **114/114** |
| 3 | Script contra o racional | `git diff ef36e2c HEAD` do script, do teste, da auditoria e do pipeline; `validar_memoria.py` em cada arquivo; manifesto; busca de texto de caso | ok. O script mudou só no que a emenda 6 manda: E com destino `"memória"` em `PARTES`, e `GUIA_E` igual, caractere por caractere, ao complemento do racional, depois de "…." e de um espaço. `destino_decidido_em` de E: "decisoes.md, 19/10". Sem LLM nem serviço externo (só `re` e `pandas`). Nenhuma constante nova além de `GUIA_E`, que está no racional. Texto de caso: 0 arquivos. Manifesto com os hashes do código, a rodada e a fonte, e **21/21** artefatos conferidos; nada gravado fora dele. `validar_memoria.py` → **aprovado** nos 4 arquivos. Catálogo: só as fechadas, sem `location`/`evidence` |
| 4 | Ordem | `git log --date=iso-strict` do racional, do script e do `base_pipeline.py`; `gerado_em` dos manifestos | ok: as emendas 5 (14:32:13) e 6 (14:43:26) vêm antes da rodada do script deste validador (14:45:07−03:00). As duas se declaram: a 5 como descritiva, a 6 como decisão do Rafael depois da investigação. A rodada do pipeline (14:31:19) é 54 s anterior ao commit `364cbd8`, mas foi gerada com o mesmo `base_pipeline.py`: o hash `8429c4a3…` do manifesto da rodada é igual ao do HEAD, e o passo 1 do `minerar.py` confere o código |

`<ensaio>` = `analysis/2026-10-trace-law-flow-third/pipeline/resultados/ensaio_base1`; `<rascunho>` = pasta de
rascunho do validador, no scratchpad, fora do repositório.

## O que mudou nas medidas

- E: `validation.destino` "memória" e `destino_decidido_em` preenchido. Antes, "em aberto" e null.
- E: a `correction_guidance` agora é "Não chame: repr, dir, eval, globals; Não acesse: `__name__`." mais, depois de um
  espaço, o complemento fixo da emenda 6. É igual na conferência e no script.
- O catálogo tem 4 entradas (C, D.ConversationAgent, D.managerAgent, E), todas com campos iguais aos dos arquivos e
  `sha256_16` conferido.
- O resto não muda em relação à revalidação 5: população, cobertura, inventário, listas, partes, `location`,
  `evidence`, `description`, `occurrences`, `status` e `impact`.

## Observação para a base 3 (não medida aqui: 0 casos na base 1)

A emenda 5 diz que, para `eval`, o nome é verificado "por uma função escrita pelo agente". O `base_pipeline.py` e a
auditoria, iguais entre si, são mais largos que essa prosa em três pontos:
- (a) aceitam como verificadora qualquer função que receba o nome entre aspas, inclusive uma embutida, como
  `eval('x')`;
- (b) para `eval`, aceitam também os braços diretos da emenda 3 (`'x' in globals()`, `globals().get('x')`);
- (c) também em `globals`/`locals`/`vars`, uma variável que recebe `eval(...)` deixa de contar como criada. A emenda 3
  só exclui `globals`/`locals`/`vars`.

Como o pipeline e a auditoria fazem igual, o encontro fecha mesmo onde a prosa diria outra coisa. Na base 3 (46 `eval`
no ContestacaoCivel, segundo o comentário do Ajuste 23), quem rodar deve contar quantos erros caem nesses três pontos.
Se algum cair, cabe ao Rafael decidir se a prosa da emenda 5 ou o código é o certo.

## Condição da ordem, na base 3 (não é divergência)

A primeira rodada deste script na base 3, a base de confirmação, ainda não existe nesta máquina. Ela tem de rodar com
um HEAD que contenha `7b4e4e0` e depois de 2026-10-19T14:43:26−03:00, e quem rodar confere a data contra o `git log` do
racional.

## Contagens da revalidação 6

- Testes 19/19 · encontro do script 28/28 · lição 14/14 · memórias e catálogo 100/100 · total 114/114 · 0 divergências.
- População 16 = 16 (a emenda 3 tira 1; a emenda 5 não tira nenhum na base 1). Memórias: 4 (C 6, E 7,
  D.ConversationAgent 2, D.managerAgent 1; B 0), as 4 aprovadas no esquema 0.3. Catálogo: 4 fechadas, 0 fora.
  Manifesto: 21/21.
- Itens: 1 ok · 2 ok · 3 ok (1 observação sobre o pipeline e a auditoria, para a base 3) · 4 ok, com a condição da
  primeira rodada na base 3.

---

# Revalidação 7 (emendas 7, 8 e 9, 20/10)

**Objeto:**
- o racional com a emenda 7 (`c832da3`, 2026-10-20T15:55:08−03:00) e as emendas 8 e 9 (`cc27360`, 17:49:51−03:00);
- o script `mineracao_U_sandbox.py` (sha256 `5902a220…`, de `cc27360`; muda só pela emenda 9);
- o `minerar.py` (`ae17ddcc…`, sem mudança) e o esquema `esquema-memoria.json` (`3a33f772…`, 0.4);
- a auditoria `audit_candidata_base3.py` (`5c0b760c…`; a emenda 7 entra em `c832da3`, as 8 e 9 em `cc27360`);
- os dois `base_pipeline.py`, com os Ajustes 26 e 27 (base 3 `54669540…`, base 1 `db9c8399…`);
- os testes `test_mineracao_candidata_base3.py`, `test_ferramenta_nao_declarada.py` e `test_verificacao_try_nameerror.py`
  (classe `TestAjuste27`).

HEAD `cc27360`. Ensaio novo: rodada `6d054fbb12098c5f…`, gerada às 17:51:55−03:00 com o `base_pipeline.py` do HEAD (o
hash do manifesto da rodada é o mesmo do arquivo), e a fonte `fonte_base1_v1.parquet` (`afaf3e98…`). O validador não
corrigiu nada nem fez commit. Mudaram só a `conferencia_independente.py`, que é do validador, e este laudo.

## Veredito: **APROVADO** (falta a aprovação final do Rafael), com três observações para a base 3

Todas as medidas batem (189/189), e cada mudança do script corresponde a uma regra da emenda 9. As emendas 7 e 8 não
tiram nenhum erro na base 1, como o racional diz. As observações (abaixo) tratam de pontos que a base 1 não exercita
(0 casos); por isso não são divergências medidas.

| # | Item | Comando | Resultado |
|---|---|---|---|
| 1 | Conferência só a partir do racional (emendas 7–9) | `uv run python …/propostas/U_sandbox/conferencia_independente.py --fonte <ensaio>/fonte_base1_v1.parquet --casos <ensaio>/rodada/perfis/U_sandbox/casos.csv --perfil <ensaio>/rodada/perfis/U_sandbox/perfil.csv --json <rascunho>/conferencia_rev7_1.json` | ok. **Emenda 7:** sai o import cujo nome (pela raiz, no último trecho) é `get_document_text`. **Emenda 8:** sai, no papel `ontestacaoCivel`, a função proibida `globals`/`locals`/`vars` numa linha com `in globals()`/`in locals()`/`in vars()` ou `<f>().get(`. **Emenda 9:** C global = os módulos (`pd`→`pandas`, `np`→`numpy`) que estão em todas as listas distintas; os outros vão para Cp (`U_sandbox.C.<papel>`). B com o texto novo e o complemento do framework. `globals`/`locals`/`vars`/`eval` passam para F (em aberto). E fica com o complemento curto. Todas as partes ganham `validation.nomes`. Resultado: população **16** = rodada 16 (0 só de um lado); a emenda 3 tira 1, as 7 e 8 tiram 0; cobertura 16/16; partes C 3 · Cp 3 (C.ConversationAgent 2, C.CalculoTrabalhista 1) · D 3 · E 5 · F 2 · B 0. Rodada duas vezes, o JSON sai idêntico (`cmp`) |
| 2a | Testes | `uv run python -m unittest analysis/tests/test_mineracao_candidata_base3.py` · `…/test_ferramenta_nao_declarada.py` · `…/test_verificacao_try_nameerror.py` · `uv run python -m unittest discover -s analysis/tests` | ok: **21/23 + 2 pulados** · **5/5** · **12/12** (3 da `TestAjuste27`) · suíte **296, OK (2 pulados)**. Os 2 pulados são os de ponta a ponta. Eles leem a pasta fixa `resultados/ensaio_base1`, de outro código. Rodados contra o ensaio novo (`uv run python <rascunho>/rodar_ponta_a_ponta.py`, que só troca a pasta da classe, sem editar o teste): **2/2 ok** |
| 2b | Script | `uv run python …/pipeline/especificas/minerar.py U_sandbox --rodada <ensaio>/rodada --fonte <ensaio>/fonte_base1_v1.parquet --saida <rascunho>/saida_script` | saída 0. Passos 1 e 3 a 9 ok; o passo 2 diz "não conferido", como antes. Encontro com a auditoria **31/31**, com as 7 partes. **7 memórias** aprovadas no esquema 0.4. Catálogo: **6 fechadas, 1 fora** (F, em aberto). `resultados/` da análise e `registros/memorias.json` não foram tocados (`stat` e `cmp` antes e depois) |
| 2c | Comparação medida por medida | `python3 <rascunho>/comparar.py <rascunho> <ensaio>/fonte_base1_v1.parquet` | lição **14/14**; memórias e catálogo **175/175**; total **189/189**. A primeira passada deu 187/189. As 2 diferenças eram leituras erradas do validador, corrigidas na conferência (ver "Divergências") |
| 3 | Script contra o racional | `git diff 7b4e4e0 HEAD` do script, da auditoria, dos dois pipelines e dos testes; `validar_memoria.py analysis/registros/esquema-memoria.json <arquivo>` em cada memória; manifesto; busca de texto de caso | ok. O script muda só no que a emenda 9 manda: `PARTES` ganha Cp (papel, memória) e F (global, em aberto); a parte do erro sai de `listas_comuns` (interseção das listas da população; com nenhuma, tudo em C); o molde do import segue o racional; B tem o texto novo e o complemento do framework pela raiz; F usa "Não chame: …."; `GUIA_E` é igual ao complemento curto; `validation.nomes` sai da mesma tabela da guidance. Não há LLM nem serviço externo (o script importa só `re` e `pandas`). As constantes novas estão no racional: `APELIDOS`, `INTROSPECCAO_F`, os nomes do framework. `DECIDIDO_EM` preenche o campo `destino_decidido_em` que o racional pede; ver a observação 3. Texto de caso: 0 arquivos com trecho das mensagens ou do código dos 16 erros (616 trechos procurados). O manifesto traz os hashes do código (4/4 iguais aos arquivos), da rodada e da fonte, e **24/24** artefatos conferidos; nada fica fora dele. `validar_memoria.py` → **aprovado** nos 7 arquivos. O catálogo tem só as fechadas, sem `location`/`evidence`, com `nomes` igual ao do arquivo (6/6). **A auditoria diz o mesmo que a prosa.** Emenda 7: `NAO_DECLARADAS = {get_document_text}`, pela raiz, no último trecho. Emenda 8: `PAPEIS_QUE_VERIFICAM = {ontestacaoCivel}`, a função proibida em `globals`/`locals`/`vars` e a linha com `in <f>()` ou `<f>().get(`, sem exigir criação nem aspas. Emenda 9: C global pela interseção das listas e `U_sandbox.C.<papel>` para o resto; `globals`/`locals`/`vars`/`eval` em `U_sandbox.F`. Os blocos dos Ajustes 26 e 27 são iguais nos dois `base_pipeline.py`; a base 1 não tem o caminho `_mecanismo_com_evidencia`, que é só da base 3 |
| 4 | Ordem | `git log --date=iso-strict` do racional, do script, da auditoria, dos pipelines e dos testes; `git show <commit>:<arquivo>` em `14b0652`, `c832da3` e `cc27360`; `gerado_em` dos manifestos | ok. A emenda 7 entra em `c832da3` (15:55:08), no mesmo commit do Ajuste 26 nos dois pipelines, da emenda 7 da auditoria e do `test_ferramenta_nao_declarada.py`. As emendas 8 e 9 entram em `cc27360` (17:49:51), no mesmo commit do Ajuste 27 nos dois pipelines, das emendas 8 e 9 da auditoria, da emenda 9 do script e da `TestAjuste27`. Em `14b0652` não há nenhuma das três. Nenhuma emenda chega depois do código que a aplica. A rodada deste validador (17:51:55) e o script (17:53:44) vêm depois de `cc27360`. As emendas 7 e 8 se declaram descritivas (escritas depois da base 2 e da medição na base 3); a 9 se declara decisão do Rafael |

`<ensaio>` = `analysis/2026-10-trace-law-flow-third/pipeline/resultados/ensaio_base1_revalidacao7`; `<rascunho>` = pasta
de rascunho do validador, no scratchpad, fora do repositório.

## O que mudou nas medidas (em relação à revalidação 6)

- População, cobertura, inventário, as tabelas nome × papel e nome × mês, as listas autorizadas (2) e os números do
  passo 6 não mudam. Na base 1, as emendas 7 e 8 tiram 0 erros.
- De 4 memórias para **7**:
  - C 6 vira **C 3** (`datetime`) + **C.ConversationAgent 2** + **C.CalculoTrabalhista 1** (as duas com `json`). O
    `json` não está na lista do managerAgent, então não está em todas as listas e vai para Cp.
  - E 7 vira **E 5** (`repr`, `dir`, `__name__`) + **F 2** (`eval`, `globals`).
  - D.ConversationAgent 2 e D.managerAgent 1 não mudam, a não ser por `validation.nomes`.
- Cp: o papel ConversationAgent tem lista com `json`, e o CalculoTrabalhista não tem lista vista; nos dois o texto é
  "Importe antes de usar: import json." e não há pedaço "Não está na lista autorizada deste papel".
- E: a guidance perde "; para ler JSON, use json.loads". F: "Não chame: eval, globals."; destino em aberto, com
  `destino_decidido_em` nulo e fora do catálogo.
- `validation.nomes` nas 7 memórias e nas 6 entradas do catálogo. Esquema 0.3 → 0.4.
- Catálogo: de 4 fechadas para **6 fechadas e 1 fora**. Os números de referência do dossiê (16 erros, 100%, 7 memórias,
  6 no catálogo, F fora) conferem.

## Divergências, medida por medida

Nenhuma entre o script e o racional. A primeira comparação deu 2 diferenças, as duas por leitura errada do validador.
Elas foram corrigidas na `conferencia_independente.py`, e a segunda passada deu 189/189:
1. `U_sandbox.E` · `validation.nomes.nao_usar`: conferência `repr, dir, __name__` (funções e depois atributos) ×
   script `repr, __name__, dir`. O racional diz "em toda lista de nomes, a ordem é por erros, e no empate a alfabética"
   (emendas 4 e 9), e `nao_usar` é uma lista só. O script está certo.
2. `U_sandbox.F` · `destino_decidido_em` presente: o comparador esperava o campo preenchido em todas as partes ×
   script nulo na F. A F tem destino "em aberto", que não é destino decidido. É a mesma leitura das revalidações 5 e 6,
   que aceitaram nulo para a E quando ela estava em aberto. O script está certo.

## Observações para a base 3 (não medidas aqui: 0 casos na base 1)

1. **A linha da emenda 8.** O pipeline e a auditoria, iguais entre si, aceitam espaço dentro e em volta dos parênteses
   (`in globals( )`, `globals() .get (`). A prosa escreve a forma literal. Os dois também leem a função proibida na
   primeira `Forbidden function evaluation` da mensagem inteira, não no último trecho. A conferência usou a forma
   literal. Na base 3, quem rodar deve contar os erros que caem só nessas variantes; o esperado da emenda 8 é 135.
2. **`nao_importar` de B "pela raiz".** O script dá as raízes na ordem da primeira aparição na lista dos nomes crus
   (por erros). A conferência soma os erros por raiz. Os dois só diferem se dois nomes crus com a mesma raiz mudarem a
   ordem (ex.: `smolagents` e `smolagents.x`). Na base 1 B = 0. Na base 3 a B.OBFCivel tem 44 erros, todos de nomes do
   framework.
3. **Os números das decisões em `destino_decidido_em`.** O script grava "decisão 5" em C, Cp e E, "decisão 3" em D e
   "decisões 1 e 4" em B. O `decisoes.md` não numera as entradas, e o racional liga a decisão 5 à E (o "não chame
   `globals`"). A numeração parece ser a do dossiê, §2h. O racional não fixa essa numeração e pede só "com a data e a
   decisão", então não é divergência. Mas quem ler só o `decisoes.md` não acha "decisão 5". Cabe ao Rafael dizer se o
   campo deve citar a entrada pelo título. Também a D: a "decisão 3" é a de monitorar, não injetar, e o arquivo segue com
   destino "memória" e no catálogo. Isso está de acordo com o racional (a emenda 9 não muda D) e com o monitoramento no
   nível da memória.

## Condição da ordem, na base 3 (não é divergência)

A primeira rodada deste script na base 3, a base de confirmação, ainda não existe nesta máquina: todos os manifestos
de mineração do `U_sandbox` achados têm a fonte `afaf3e98…`, da base 1. Uma delas,
`resultados/ensaio_base1_20out/mineracao`, foi gerada às 17:45:45−03:00 com o script deste HEAD (`5902a220…`), 4 min
antes de `cc27360`. É ensaio na base 1, não confirmação. A rodada da base 3 tem de usar um HEAD que contenha `cc27360`
e começar depois de 2026-10-20T17:49:51−03:00. Quem rodar confere a data contra o `git log` do racional e os esperados
das emendas: 167 erros para `U_ferramenta_nao_declarada` (sandbox 1.401 → 1.234, B.OBFCivel 211 → 44) e 135 para
`U_verificacao_existencia` pela emenda 8.

## Contagens da revalidação 7

- Testes: 21/23 + 2 pulados (2/2 contra o ensaio novo) · 5/5 · 12/12 · suíte 296 OK (2 pulados) · encontro do script
  31/31 · lição 14/14 · memórias e catálogo 175/175 · total 189/189 · 0 divergências.
- População 16 = 16 (a emenda 3 tira 1; as emendas 5, 7 e 8 tiram 0 na base 1). Memórias: 7 (C 3, C.ConversationAgent
  2, C.CalculoTrabalhista 1, D.ConversationAgent 2, D.managerAgent 1, E 5, F 2; B 0), as 7 aprovadas no esquema 0.4.
  Catálogo: 6 fechadas, 1 fora (F). Manifesto: 24/24 artefatos e 4/4 hashes de código.
- Itens: 1 ok · 2 ok · 3 ok (3 observações para a base 3) · 4 ok, com a condição da primeira rodada na base 3.
