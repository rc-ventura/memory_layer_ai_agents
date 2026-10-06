---
name: mineracao-protocolo
description: "Minera a família 'Protocolo do harness' (o erro 'resposta sem bloco de código': o harness não acha o <code> na resposta do LLM) de uma base do trace de agentes, do zero, a partir das tabelas que o drill_down.py protocolo grava: quando e onde (incidente ou fundo), a camada (modo do prompt, modelo, M1 medido), o cenário de cobertura e a fronteira de chamada. Não compara com relatório publicado: a verificação é uma auditoria independente rodando em paralelo, confrontada com as tabelas por script. Cada achado leva a evidência (comando, tabela, casos crus). Entrega os achados e as paradas; a leitura de casos e a classificação no catálogo de mecanismos vão para a skill mineracao-investigacao. Use quando pedirem 'minere o protocolo do harness', 'resposta sem bloco de código na base <X>', 'rode o protocolo'. Começa pela skill mineracao-base."
argument-hint: "<pasta da análise, ex.: analysis/<pasta-datada>>"
---

# Mineração do protocolo do harness

**O que é minerar aqui:** ler as tabelas que o pipeline produziu para esta base, seguindo o procedimento da análise,
e dizer o que elas mostram, com a evidência de cada achado. Não há número "certo" para bater. A verificação vem de
duas fontes:
- **uma segunda implementação**, a auditoria independente em paralelo;
- **as conferências internas.**

**O método está na análise, não aqui.** O passo a passo é `docs/*procedimento-protocolo-harness*.md`. O porquê e o
**catálogo de mecanismos** estão em `docs/*racionais-protocolo-harness*.md`. Se o procedimento e esta skill
discordarem, vale o procedimento: registre a discordância.

## 1 · Preparação: a skill `mineracao-base`

- O Passo 0 inteiro. Guarde o `BASE_ID`, a pasta da análise e o `TRACE`.
- Esta mineração precisa de `pipeline/resultados/erros_mecanismo.csv` e `execucoes.csv`. Se faltarem, rode de dentro
  de `pipeline/`:
  `uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 analise_trace_esteira_juridica.ipynb`.

## 2 · Disparar a auditoria em paralelo (agente `auditor-independente`)

Entregue ao `auditor-independente`, para rodar da pasta da análise:

```
uv run python audit/scripts/audit_recompute10.py --base <BASE_ID> --trace <TRACE> --json pipeline/resultados/auditoria_protocolo_<BASE_ID>.json
```

Sem subagentes no ambiente: rode você mesmo, antes do passo 3, e não leia a saída até o passo 5.

## 3 · As tabelas da mineração

De dentro de `pipeline/`: `uv run python drill_down.py protocolo`. O comando grava em
`resultados/evidencia/protocolo/`:

| Tabela | O que tem |
|---|---|
| `casos.csv` | um erro por linha: mês, papel, idx, versão do formato, forma, tamanho, tokens, recuperação, cascata, M1 (`sobreposicao_final`, `sobreposicao_obs_anterior`), `chamada` e `chamadas_do_papel` |
| `passos.csv` | steps por mês e papel (os denominadores) |
| `versoes.csv` | as versões do formato do prompt por papel: modo, steps, erros, meses |
| `modelos.csv` | por papel: o modelo e a versão do agente, com steps, erros e meses |

Se a família não existir na base, o comando diz "nenhum erro" e grava as três últimas tabelas. A mineração termina aí,
com essa afirmação e a evidência dela.

## 4 · Minerar: passo a passo do procedimento, cada achado com a evidência

A regra 0 da `mineracao-base` vale aqui: comando, tabela com filtro e casos crus. Nos comandos abaixo:
- `ME` é `uv run python <skill mineracao-base>/scripts/montar_evidencia.py <pasta-da-analise>`;
- `T` é `evidencia/protocolo/casos.csv`.

Em todo `ME`, passe `--afirmacao "<a frase do achado>"` e `--reproduzir "<o comando da coluna Reproduzir>"`. O
`bloco.md` que ele escreve entra no relatório por `cat`.

| Passo | O que registrar | Reproduzir | Evidência crua (montar) |
|---|---|---|---|
| **1 · Contar** | erros, execuções, papéis e taxa por 1k steps; por mês, com o gatilho do procedimento (concentrado num período = incidente; espalhado = fundo); por papel; forma; recuperação; o que vem depois | `uv run python drill_down.py protocolo` [1]–[6] | `ME --nome protocolo_mes_<mês>_<BASE_ID> --de T --onde mes=<mês do pico> --regra semente --n 10` e `ME --nome protocolo_papel_<papel>_<BASE_ID> --de T --onde role=<papel do topo>` (se o papel erra num mês só, também `--regra semente --n 10`) |
| **2 · Camada** | o **modo** (as versões em texto têm erro e as em JSON não?), pela `versoes.csv`; o **modelo** (um modelo novo só no período do pico?), pela `modelos.csv`; o **M1 medido** por papel ([9]) | `uv run python drill_down.py protocolo` [7], [8], [9] | `ME --nome protocolo_m1_<BASE_ID> --de T --onde "sobreposicao_final>=0.5"` |
| **3 · Cobertura** | a tabela acumulada por papel. **Parada P0:** até onde ler é decisão do pesquisador | `uv run python <esta skill>/scripts/cobertura.py <pasta-da-analise>` | — (a tabela é a derivada) |
| **Fronteira de chamada** | os erros fora da 1ª chamada do papel (`chamada > 1`) e os erros em papéis chamados mais de uma vez. **Parada:** se houver, nenhuma sequência desses papéis se lê como "loop" sem conferir onde a chamada recomeça | as colunas `chamada`/`chamadas_do_papel` do `casos.csv` | `ME --nome protocolo_fronteira_<BASE_ID> --de T --onde "chamada>=2"` |

**Passos 4 a 7 do procedimento** (ler casos, metadados, classificar no catálogo, destino) são leitura e decisão.
Aqui se registram as paradas, que vão para o roteiro `protocolo` da `mineracao-investigacao`:
- **P1 · A camada do surto:** abre quando o passo 1 achou um período concentrado e a camada (modo ou modelo) não
  explica sozinha;
- **P2 · O mecanismo de cada caso:** abre sempre que há erros nos papéis do cenário de cobertura.

## 5 · O encontro: auditoria × tabelas

Quando o auditor terminar, da pasta da análise:

```
uv run python <esta skill>/scripts/comparar_auditoria.py . pipeline/resultados/auditoria_protocolo_<BASE_ID>.json
```

O script confronta as quatro tabelas com o JSON do auditor, medida por medida, inclusive cada versão do formato e
cada modelo. Ele também roda as conferências internas: soma por papel = soma por mês = total; todo erro tem forma; o
"vem depois" soma o total; os erros nas versões e por modelo = total.

- **Saiu com 0:** os achados estão verificados. No relatório, a verificação leva os dois comandos e o caminho do JSON.
- **Saiu com 1:** **pare**. Registre cada DIVERGE ou FALHA e não tire conclusão das medidas que divergem. Não edite a
  auditoria, o pipeline nem as tabelas.

## 6 · Saída

- **Relatório:** `pipeline/resultados/relatorio_protocolo_<BASE_ID>_<AAAA-MM-DD>.md`, no esqueleto da
  `mineracao-base`, com a evidência de cada achado, o encontro, as conferências e as paradas, cada uma com a pasta de
  evidência.
- **Sigilo:** o relatório completo fica no ambiente. Para sair: `versao_para_sair.py` e depois `varrer_pii.py` no
  `_saida.md`.
- **Para o pesquisador:** os achados principais desta base em contagens (incidente ou fundo, a camada, o M1); o
  resultado do encontro e das conferências internas; as paradas (P0, fronteira, P1, P2), com a pasta de evidência de
  cada uma; o caminho do relatório completo.
- **Não leia casos nesta mineração.** O pesquisador escolhe o que vai para a investigação (`/investigar`, skill
  `mineracao-investigacao`).
