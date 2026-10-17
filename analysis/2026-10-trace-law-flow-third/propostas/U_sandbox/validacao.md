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
