# Degrau 3 do sandbox — os dois leitores na máquina da base (roteiro para a segunda, 02/11/2026)

O que falta para as três memórias que vão para o agente chegarem ao degrau 3 (revisada: "a causa é mesmo a que a regra
supõe?", [`17`](../../../2026-09-trace-law-flow/docs/17-validacao-memorias.md)): dois leitores, cada um às cegas, sobre a
amostra de 30 casos de cada memória já pronta na máquina (dossiê §2h, 27), e a concordância medida por script. As regras
contadas na população e a leitura de 10 casos mascarados por memória já estão feitas (§2h, 31): aqui os leitores veem o
caso inteiro (o pensamento do agente e as observações), o que a foto não mostra.

**O que muda em relação ao roteiro `candidata`** (skill `mineracao-investigacao`): **sem a leitura aberta.** Ela serve para
montar a lista de lições quando a lição ainda não é conhecida; aqui a lição de cada memória já está fixada (degraus 1 e 2)
e a pergunta é só se a causa é essa. A lista vai pronta abaixo e **precisa da aprovação do Rafael antes de rodar**. Os
dois leitores leem os 30 casos de cada memória (a leitura fechada pede pelo menos 20).

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

## Na máquina (segunda)

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
> `pipeline/resultados/leitura_degrau3_<MEM>_base3.csv` com `exec_id,role,idx` e essas colunas, mais `onde_no_cru`.
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
> `onde_no_cru`. **Não escreva na resposta nenhum trecho de caso:** só as contagens por categoria.

**3 · A concordância**, por script, da pasta `analysis/2026-10-trace-law-flow-third/pipeline/` (para cada `<MEM>`):
```
uv run python ../../../.github/skills/mineracao-investigacao/scripts/concordancia.py resultados/leitura_degrau3_<MEM>_base3.csv resultados/leitura2_degrau3_<MEM>_base3.csv --rotulo causa
uv run python ../../../.github/skills/mineracao-investigacao/scripts/concordancia.py resultados/leitura_degrau3_<MEM>_base3.csv resultados/leitura2_degrau3_<MEM>_base3.csv --rotulo conserto
```
e, na C.JoogleAnalytics, também `--rotulo tambem_json`.

## O que trazer (fotos)

1. A resposta de cada leitor: as **contagens por categoria** de cada coluna (3 memórias × 2 leitores).
2. A saída de cada `concordancia.py`: a linha `casos em comum · concordam · kappa` e as linhas de `discordância`.

**Como ler o kappa aqui:** se quase todos os casos caem numa categoria só (o esperado, se H0 vale), o kappa fica baixo ou
indefinido mesmo com os leitores concordando — o número que importa é a concordância simples e as discordâncias.

Não trazer: o CSV das leituras nem a tabela lado a lado (têm `exec_id` e frases dos leitores; ficam na máquina).
