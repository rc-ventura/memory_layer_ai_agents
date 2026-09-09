# Análise do trace cru — esteira de agentes do fluxo juridico

**Data:** 2026-09-08 · **Fonte:** `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` (1.000 execucoes, nov/2025-ago/2026)

Analise empirica do primeiro trace cru da esteira juridica (1.000 execucoes, 5.781 steps,
142,6 milhoes de tokens). Taxonomia de erros por causa-raiz, custo em tokens/latencia, propagacao,
reincidencia entre execucoes, detectores de falha silenciosa, e candidatos a unidades de memoria.

## Como ler esta pasta (ordem sugerida)

| # | Arquivo | O que e | Para quem |
|---|---|---|---|
| 1 | [`01-racionais.md`](docs/01-racionais.md) | A logica por tras da analise, em linguagem acessivel. Por que a taxonomia veio do trace e nao dos papers; o que e um teste de robustez; o que significa um achado ser corrigido vs. retirado. | Ler primeiro — da o contexto pra entender o resto |
| 2 | [`02-relatorio-achados.md`](docs/02-relatorio-achados.md) | O relatorio de achados em si: TL;DR, taxonomia por causa-raiz, custo vs. falha, o resultado central (agente le o erro e reincide), ponto cego, candidatos a memoria, o que a literatura refutou, limitacoes, proximos passos. | O documento principal — os numeros |
| 3 | [`03-procedimento-validacao.md`](docs/03-procedimento-validacao.md) | Roteiro de validacao: como auditar o pipeline, em que ordem ler os papers, e como triangular qualquer numero agregado contra um caso concreto no trace cru (`drill_down.py`). Checklist pre-reuniao. | Antes de apresentar ou reusar o pipeline |
| 4 | [`04-roadmap.md`](docs/04-roadmap.md) | O que ainda falta: item estrutural (branch/commit), itens fora de escopo/adiados, e a lista analitica em aberto priorizada. | Para saber o proximo passo |

## Pipeline e ferramentas

| Arquivo | O que faz |
|---|---|
| [`analise_trace_esteira_juridica.ipynb`](pipeline/analise_trace_esteira_juridica.ipynb) | Notebook executavel — o pipeline reproduzivel com outputs embutidos |
| [`drill_down.py`](pipeline/drill_down.py) | Script para triangular um numero agregado contra um caso concreto no trace cru |

## Fichamentos teoricos

[`literature/`](literature/) — quatro papers de taxonomia de erro de agentes, lidos em texto
completo (apendices incluidos) por subagentes em 08/09/2026. Nivel 🔎 (agente leu, nao Rafael leu).
Ver o [`literature/README.md`](literature/README.md) para o indice e o que cada paper aporta.

## Dados derivados

`resultados/` — CSVs derivados do trace cru (**git-ignored**: contem nomes de clientes, numeros
de processo e trechos de documentos em claro). Regenerar rodando o notebook.
