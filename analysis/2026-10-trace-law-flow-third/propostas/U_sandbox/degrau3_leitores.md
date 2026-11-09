# Degrau 3 do sandbox — os dois leitores no ambiente da base (roteiro para a segunda, 02/11/2026)

O que falta para as três memórias que vão para o agente chegarem ao degrau 3 (revisada: "a causa é mesmo a que a regra
supõe?", [`17`](../../../2026-09-trace-law-flow/docs/17-validacao-memorias.md)): dois leitores, cada um às cegas, sobre a
amostra de 30 casos de cada memória já pronta no ambiente (dossiê §2h, 27), e a concordância medida por script. As regras
contadas na população e a leitura de 10 casos mascarados por memória já estão feitas (§2h, 31): aqui os leitores veem o
caso inteiro (o pensamento do agente e as observações), o que os casos mascarados não mostram.

**O que muda em relação ao roteiro `candidata`** (skill `mineracao-investigacao`): **sem a leitura aberta.** Ela serve para
montar a lista de lições quando a lição ainda não é conhecida; aqui a lição de cada memória já está fixada (degraus 1 e 2)
e a pergunta é só se a causa é essa. A lista vai pronta abaixo e foi **aprovada pelo Rafael em 03/11, sem ajuste**. Os
dois leitores leem os 30 casos de cada memória (a leitura fechada pede pelo menos 20).

**Ajustes depois da primeira memória (03/11; dossiê §2h, 33).** Use `uv run --no-sync` nos comandos abaixo, porque o `uv run`
estava mudando pacotes do ambiente a cada execução. Feche as abas `leitura_*` antes de abrir o segundo leitor. Registre o
modelo de cada leitor e use a mesma dupla nas três memórias. Os leitores não gravam recorte de caso em arquivo, e o
`onde_no_trace` traz nomes de campo (dossiê §2h, 34).

## As hipóteses, escritas antes de ler

| Memória (amostra) | H0 — a causa que a memória supõe | Alternativas — o que se veria no caso |
|---|---|---|
| `U_sandbox.C` (30 de 423) | esqueceu o import (`json`, `re`, `datetime`) | o nome existia num passo antes e sumiu (o pensamento diz que já tinha importado); o import foi barrado; o nome é de uma função auxiliar |
| `U_sandbox.C.JoogleAnalytics` (30 de 231) | esqueceu o `import pandas as pd` — **e o `import json` na mesma linha** (§2h, 31: `json` na linha em 231 de 231) | o `pandas` existia antes e sumiu; o agente achava que o `pd` vinha pronto |
| `U_sandbox.E` (30 de 317) | chamou uma função ou atributo barrado para **inspecionar um valor** (ver tipo ou conteúdo) | outro uso: executar texto (`exec`), abrir arquivo (`open`), importar por nome (`__import__`), outro |

## A lista de categorias (a aprovar)

Uma categoria por coluna, por caso. `indeterminado` quando o caso não deixa ver; `outra:<rótulo>` quando nenhuma serve.

- **`causa`**
  - C e C.JoogleAnalytics: `esqueceu_import` · `nome_sumiu_entre_passos` · `import_barrado` · `outra:<rótulo>` · `indeterminado`
  - E: `inspecionar_valor` · `outra:<rótulo>` · `indeterminado`
- **`tambem_json`** (só na C.JoogleAnalytics): `sim` (a linha também usa `json` sem import) · `nao` · `indeterminado`
- **`conserto`** (o que o agente fez no passo seguinte): `corrigiu_a_licao` · `contornou` · `repetiu` · `desistiu` · `indeterminado`
- **`licao_livre`**: a lição em uma frase, com as próprias palavras, em termos gerais (sem nome, número ou trecho do caso)

## No ambiente (segunda)

**0 · Conferir.** Este arquivo copiado para `analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/`. As amostras
existem (de 26/10), da pasta `analysis/2026-10-trace-law-flow-third`:
```
ls pipeline/resultados/evidencia/inv_candidata_U_sandbox.*_base3/casos.csv
```
Devem aparecer 3 (C, C.JoogleAnalytics, E). O `concordancia.py` em `.github/skills/mineracao-investigacao/scripts/`.

**1 · Primeiro leitor — um chat novo do Copilot**, com este texto (troque `<MEM>` por `U_sandbox.C`, depois
`U_sandbox.C.JoogleAnalytics`, depois `U_sandbox.E`; pode ser o mesmo chat para as três):

> Você é o primeiro leitor do degrau 3 do sandbox. Leia `analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/degrau3_leitores.md`
> (as hipóteses e a lista de categorias) e siga o agente `investigador` da skill `mineracao-investigacao`, na leitura
> fechada. A amostra é `pipeline/resultados/evidencia/inv_candidata_<MEM>_base3/casos.csv` (30 casos). Para cada caso, de
> dentro de `analysis/2026-10-trace-law-flow-third/pipeline/`, rode `uv run python drill_down.py caso <exec_id> <role> <idx>`
> e leia o passo do erro e o seguinte (pensamento, código, mensagem). Classifique cada caso nas colunas da lista
> (`causa`, `conserto`, `licao_livre`, e `tambem_json` se for a C.JoogleAnalytics), só com as categorias da lista. Grave
> `pipeline/resultados/leitura_degrau3_<MEM>_base3.csv` com `exec_id,role,idx` e essas colunas, mais `onde_no_trace`.
> **Não escreva na resposta nenhum trecho de caso, nome, número de processo ou conteúdo de documento:** devolva só as
> contagens por categoria de cada coluna e quantos casos ficaram `indeterminado` ou `outra`.

**2 · Segundo leitor — um chat NOVO do Copilot** (o segundo leitor não pode ver o primeiro), com este texto:

> Você é o segundo leitor do degrau 3 do sandbox, às cegas. **Não abra nenhum arquivo `leitura_degrau3_*` nem o dossiê
> do sandbox.** Leia só `analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/degrau3_leitores.md` (a lista de
> categorias) e siga o agente `segundo-leitor` da skill `mineracao-investigacao`. A amostra é
> `pipeline/resultados/evidencia/inv_candidata_<MEM>_base3/casos.csv` (os 30 casos). Para cada caso, de dentro de
> `analysis/2026-10-trace-law-flow-third/pipeline/`, rode `uv run python drill_down.py caso <exec_id> <role> <idx>`.
> Classifique nas colunas `causa`, `conserto`, `licao_livre` (e `tambem_json` na C.JoogleAnalytics), só com as categorias
> da lista. Grave `pipeline/resultados/leitura2_degrau3_<MEM>_base3.csv` com `exec_id,role,idx`, essas colunas e
> `onde_no_trace`. **Não escreva na resposta nenhum trecho de caso:** só as contagens por categoria.

**3 · A concordância**, por script, da pasta `analysis/2026-10-trace-law-flow-third/pipeline/` (para cada `<MEM>`):
```
uv run python ../../../.github/skills/mineracao-investigacao/scripts/concordancia.py resultados/leitura_degrau3_<MEM>_base3.csv resultados/leitura2_degrau3_<MEM>_base3.csv --rotulo causa
uv run python ../../../.github/skills/mineracao-investigacao/scripts/concordancia.py resultados/leitura_degrau3_<MEM>_base3.csv resultados/leitura2_degrau3_<MEM>_base3.csv --rotulo conserto
```
e, na C.JoogleAnalytics, também `--rotulo tambem_json`.

## O que trazer

1. A resposta de cada leitor: as **contagens por categoria** de cada coluna (3 memórias × 2 leitores).
2. A saída de cada `concordancia.py`: a linha `casos em comum · concordam · kappa` e as linhas de `discordância`.

**Como ler o kappa aqui:** se quase todos os casos caem numa categoria só (o esperado, se H0 vale), o kappa fica baixo ou
indefinido mesmo com os leitores concordando — o número que importa é a concordância simples e as discordâncias.

Não trazer: o CSV das leituras nem a tabela lado a lado (têm `exec_id` e frases dos leitores; ficam no ambiente).

## Os 3 casos de `datetime` da memória C (gate de 04/11)

A amostra da C não trouxe nenhum `datetime`, e Rafael decidiu ler os 3 casos da população antes de aprovar o texto (dossiê
§2h, 36). São todos os casos, sem sorteio. Os comandos rodam de dentro de `analysis/2026-10-trace-law-flow-third/pipeline/`.

**1 · Separar os casos:**
```
uv run --no-sync python ../../../.github/skills/mineracao-base/scripts/amostrar.py resultados/mineracao/U_sandbox/erros_lidos.csv --saida resultados/amostra_degrau3_U_sandbox.C.datetime_base3.csv --onde memoria_id=U_sandbox.C --onde nome=datetime
```
A saída deve dizer `população (depois dos filtros): 3 · amostra: 3`. Com outro número, pare e traga a saída.

**2 · Primeiro leitor — um chat novo do Copilot, com o modelo `6.1 luna`:**

> Você é o primeiro leitor do degrau 3 do sandbox. Leia `analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/degrau3_leitores.md`
> (a lista de categorias da C) e siga o agente `investigador` da skill `mineracao-investigacao`, na leitura fechada. **Não
> abra nenhum arquivo `leitura_degrau3_*` ou `leitura2_degrau3_*` nem o dossiê do sandbox.** A amostra é
> `pipeline/resultados/amostra_degrau3_U_sandbox.C.datetime_base3.csv` (3 casos; `idx` é a coluna `step_pos`). Para cada caso,
> de dentro de `analysis/2026-10-trace-law-flow-third/pipeline/`, rode
> `uv run --no-sync python drill_down.py caso <exec_id> <role> <idx>` e leia o passo do erro e o seguinte (pensamento, código,
> mensagem). Classifique nas colunas `causa`, `conserto` e `licao_livre`, só com as categorias da lista. Grave
> `pipeline/resultados/leitura_degrau3_U_sandbox.C.datetime_base3.csv` com `exec_id,role,idx`, essas colunas e `onde_no_trace`
> (só nomes de campo). **Não grave recorte de caso em nenhum arquivo e não escreva na resposta nenhum trecho de caso, nome,
> número de processo ou conteúdo de documento:** devolva só as contagens por categoria.

**3 · Segundo leitor — um chat NOVO, com o modelo `5.3 codex`:** o mesmo texto, trocando "primeiro leitor" por
"segundo leitor, às cegas", `investigador` por `segundo-leitor` e o arquivo gravado por
`pipeline/resultados/leitura2_degrau3_U_sandbox.C.datetime_base3.csv`. Feche as abas `leitura_*` antes.

**4 · A concordância da causa:**
```
uv run --no-sync python ../../../.github/skills/mineracao-investigacao/scripts/concordancia.py resultados/leitura_degrau3_U_sandbox.C.datetime_base3.csv resultados/leitura2_degrau3_U_sandbox.C.datetime_base3.csv --rotulo causa
```
Com 3 casos, o kappa não informa nada: o que vale é a categoria de cada caso.

**5 · Os casos mascarados:**
```
uv run --no-sync python validacao/degrau3_sandbox.py casos U_sandbox.C --fonte ../data/base_erros_minerados_full_v2.parquet --n 3 --amostra resultados/amostra_degrau3_U_sandbox.C.datetime_base3.csv
```
A saída passa pelo varredor de PII antes de aparecer na tela. Ela mostra o código sem textos, comentários e números.

**O que trazer:** a resposta de cada leitor, a saída da concordância e a saída do passo 5.

## As 2 discordâncias reais da causa na memória E (gate de 04/11)

Antes de aprovar o texto da E, Rafael decidiu ler os 2 casos em que os leitores discordam de fato sobre a causa (dossiê §2h, 40):
`34c2c8ed…` e `87672291…`. Os comandos rodam de dentro de `analysis/2026-10-trace-law-flow-third/pipeline/`.

**1 · Separar os casos:**
```
uv run --no-sync python -c "
import csv
A='resultados/evidencia/inv_candidata_U_sandbox.E_base3/casos.csv'
B='resultados/amostra_degrau3_U_sandbox.E.discordancias_base3.csv'
with open(A,encoding='utf-8',newline='') as f: L=[r for r in csv.DictReader(f) if r['exec_id'][:8] in ('34c2c8ed','87672291')]
with open(B,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,L[0].keys()); w.writeheader(); w.writerows(L)
print(len(L),'casos')
for r in L: print(r['exec_id'],r['role'],r['idx'])
"
```
Deve dizer `2 casos`. Com outro número, pare e traga a saída.

**2 · Os casos mascarados:**
```
uv run --no-sync python validacao/degrau3_sandbox.py casos U_sandbox.E --fonte ../data/base_erros_minerados_full_v2.parquet --n 2 --amostra resultados/amostra_degrau3_U_sandbox.E.discordancias_base3.csv
```

**3 · O pensamento do agente, lido pelo pesquisador, para cada caso:**
```
uv run --no-sync python drill_down.py caso <exec_id> <role> <idx>
```
O texto fica no ambiente da base. Responda só: **antes do erro, o agente queria ver o tipo ou o conteúdo de um valor?** `sim`, `nao` ou
`nao_da_para_ver`.

**O que trazer:** a saída do passo 2 e as duas respostas do passo 3.

### Versão automatizada: um agente faz os passos 1 a 3 (09/11)

Rafael pediu que um agente do Copilot rode os passos 1 a 3 desta seção sozinho (dossiê §2h, 41). Com isso, **o desempate
passa a ser de um terceiro leitor às cegas, e não do pesquisador**: o agente `segundo-leitor`, sem acesso às duas leituras.
O pesquisador confere a resposta, e a decisão do texto e do destino da E continua sendo dele.

**0 · Trazer este roteiro para o ambiente da base.** Na raiz do repositório:
```
git fetch origin
git checkout 2026-10-26-degrau3-sandbox
git pull
```

**1 · Abrir um chat NOVO do Copilot, no modo agente.** Escolha um modelo diferente dos dois leitores (`6.1 luna` e
`5.3 codex`) e anote qual foi. Feche antes as abas `leitura_*`. Cole este texto:

> Você é o terceiro leitor, às cegas, das 2 discordâncias da causa na memória E do sandbox. Leia só a seção "As 2
> discordâncias reais da causa na memória E" de `analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/degrau3_leitores.md`
> e siga o agente `segundo-leitor` da skill `mineracao-investigacao`. **Não abra nenhum arquivo `leitura_degrau3_*` ou
> `leitura2_degrau3_*` nem o dossiê do sandbox, e não procure como os outros leitores classificaram esses casos.** Trabalhe
> de dentro de `analysis/2026-10-trace-law-flow-third/pipeline/` e use `uv run --no-sync` em todos os comandos.
>
> 1. Rode o comando do passo 1 da seção, sem mudar nada. Se a saída não disser `2 casos`, pare e devolva só a saída.
> 2. Rode o comando do passo 2. Se aparecer `BLOQUEADO`, pare e devolva só essa linha. Se não, guarde a saída para o fim.
> 3. Para cada um dos 2 casos, rode `uv run --no-sync python drill_down.py caso <exec_id> <role> <idx>` com os valores que o
>    passo 1 imprimiu. Leia a "saída do modelo" e o "código" do passo do erro e do passo anterior, e responda: **antes do
>    erro, o agente queria ver o tipo ou o conteúdo de um valor?**
>    - `sim`: o pensamento ou o código mostra que ele queria ver o tipo, a forma ou o conteúdo de um valor, e o erro veio
>      do jeito como tentou ver;
>    - `nao`: a chamada ou o atributo que deu erro servia a outro objetivo, que não era ver um valor;
>    - `nao_da_para_ver`: o pensamento e o código não permitem decidir.
> 4. Grave `pipeline/resultados/leitura3_degrau3_U_sandbox.E.discordancias_base3.csv` com as colunas
>    `exec_id,role,idx,resposta,onde_no_trace`. Em `onde_no_trace` vão só nomes de campo (por exemplo `error_model_output`,
>    `prev_code_action`). Não grave recorte de caso em nenhum arquivo.
> 5. Devolva, nesta ordem: a saída inteira do passo 2 e uma linha por caso no formato
>    `<8 primeiros caracteres do exec_id>: <resposta>`. **Não escreva na resposta nenhum trecho do pensamento, do código
>    sem máscara, nome, número de processo ou conteúdo de documento.**

**O que trazer:** a resposta do agente (a saída do passo 2 e as duas linhas `exec_id: resposta`) e o nome do modelo. Não
trazer o CSV do passo 4: ele fica no ambiente da base.
