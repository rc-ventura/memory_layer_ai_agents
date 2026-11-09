---
name: mineracao-residuo
description: "Minera o resíduo de uma base do trace de agentes (os erros que nenhuma regra explica: os baldes 'causa não identificada' e 'sintoma não reconhecido', unidades X_*), do zero, a partir da tabela de padrões que o script da análise grava para uma rodada: os baldes e as classes, o Pareto dos padrões por erros e por tokens, os que passam na recorrência, a chave sem impressão digital e os padrões de uma execução. A verificação é uma auditoria independente rodando em paralelo, confrontada com a tabela por script. Cada achado leva a evidência (comando, tabela, casos crus). Entrega os achados e as paradas; a leitura de casos (o agrupamento, de quem é a falha, que unidade) vai para a skill mineracao-investigacao com o roteiro residuo, e a regra nova é um Ajuste do pesquisador. Use quando pedirem 'minere o resíduo', 'o que sobra da taxonomia na base <X>', 'rode o resíduo', 'diminuir o resíduo'. Começa pela skill mineracao-base."
argument-hint: "<pasta da análise> [--rodada <id>]"
---

# Mineração do resíduo

**O que é minerar aqui:** ler a tabela de padrões que o script da análise grava para uma rodada, seguindo o
procedimento do resíduo, e dizer o que ela mostra, com a evidência de cada achado. Não há número "certo" para bater.
A verificação vem de duas fontes:
- **uma segunda implementação**, a auditoria independente em paralelo;
- **as conferências internas.**

**O método está na análise, não aqui.** O passo a passo é `docs/*procedimento-residuo*.md` e o porquê é
`docs/*racionais-residuo*.md` (na pasta de análise que guarda o método; se a pasta da base não tiver os dois, procure
nas outras pastas de `analysis/`). Se o procedimento e esta skill discordarem, vale o procedimento: registre a
discordância.

**O objetivo do pesquisador é diminuir o resíduo.** Esta skill não diminui nada: ela mostra onde estão os padrões que
valem uma regra. O resíduo só cai quando um Ajuste aprovado põe uma regra nova no pipeline e uma rodada nova roda. A
meta não é zerar: o padrão de uma execução só fica como cobertura.

## 1 · Preparação: a skill `mineracao-base`

- O Passo 0 inteiro, com uma diferença: **numa análise com rodada** (a pasta tem `pipeline/especificas/residuo.py`),
  a conferência da versão do código é a do próprio script, que compara a fonte, o código e o identificador da análise
  com o manifesto da rodada. Nessa análise o `conferir_versao.py` do kit não se aplica.
- **A rodada:** a pedida. Se não vier, pergunte: o script não escolhe a mais recente sozinho.
- **Numa análise sem esse script** (o pipeline de trace inteiro, com notebook), as tabelas são a
  `resultados/residuo_padroes.csv` do notebook e o `drill_down.py residuo`, e a verificação é a auditoria da
  classificação inteira da análise. O encontro desta skill não se aplica: registre isso como limite no relatório.

## 2 · As tabelas da mineração

Da raiz do repositório:

```
uv run python <pasta-da-analise>/pipeline/especificas/residuo.py --rodada <rodada_id>
```

Saída 1: **pare** e leve ao pesquisador a linha da PARADA. Não conserte. A causa é quase sempre uma rodada de outro
código ou uma fonte de outro hash. O script grava em `pipeline/resultados/mineracao/residuo/`:

| Tabela | O que tem |
|---|---|
| `residuo_padroes.csv` | um padrão por linha: balde, classe, padrão mascarado, erros, execuções, meses, papéis, tokens, a lista de meses e de papéis, a chave (`identificada` × sem impressão digital) e se passa na recorrência |
| `casos.csv` | um erro por linha, com o identificador de execução, o papel, a posição do passo, o mês, a classe, o padrão, os tokens e as três colunas de formato da mensagem. É a população para o `montar_evidencia.py` e para a investigação |
| `resumo.json` | os totais por balde e por classe, as conferências feitas e os identificadores da rodada e da fonte |

As conferências que o script faz são três: os baldes batem com a triagem da rodada; a decisão de cada balde é igual a
"algum padrão passa"; a soma dos padrões é igual aos erros. Copie-as para o relatório.

## 3 · Disparar a auditoria em paralelo (agente `auditor-independente`)

Logo depois do passo 2, que grava a população, entregue ao `auditor-independente`, para rodar da raiz:

```
uv run python <pasta-da-analise>/audit/scripts/audit_residuo_*.py --casos <pasta-da-analise>/pipeline/resultados/mineracao/residuo/casos.csv --fonte <fonte da rodada> --json <pasta-da-analise>/pipeline/resultados/mineracao/residuo/auditoria_residuo.json
```

A auditoria só recebe da mineração a população (quem é resíduo) e a classe de cada erro. A mensagem, o mês e os tokens
ela lê da fonte, e o padrão e a recorrência ela reescreve à parte. Sem subagentes no ambiente: rode você mesmo, e não
leia a saída até o passo 5.

## 4 · Minerar: passo a passo do procedimento, cada achado com a evidência

A regra 0 da `mineracao-base` vale aqui: comando, tabela com filtro e casos crus. Nos comandos abaixo:
- `ME` é `uv run python <skill mineracao-base>/scripts/montar_evidencia.py <pasta-da-analise>`;
- `T` é `mineracao/residuo/casos.csv`.

Em todo `ME`, passe `--afirmacao "<a frase do achado>"` e `--reproduzir "<o comando do passo 2>"`. O `bloco.md` que
ele escreve entra no relatório por `cat`.

| Achado | O que registrar | Evidência crua (montar) |
|---|---|---|
| **1 · Tamanho** | erros e tokens do resíduo, por balde e por classe, e a fração dos erros da rodada (a triagem). A decisão de cada balde na triagem | — (o `resumo.json` e a triagem são a derivada) |
| **2 · Pareto** | os padrões ordenados por erros e por tokens. Quantos padrões fazem metade do resíduo. Quantos são de uma execução só | — (a `residuo_padroes.csv`) |
| **3 · Recorrentes** | cada padrão que passa na recorrência: erros, execuções, meses, papéis. **Parada R1–R3** para cada um | `ME --nome residuo_<n>_<BASE_ID> --de T --onde "padrao=<padrão exato>"` (até 10 casos; acima disso, `--regra primeiro-por-mes`) |
| **4 · Topo de tokens** | os padrões que não passam na recorrência mas estão entre os que mais custam: são a segunda fila. **Parada** se o pesquisador quiser lê-los | o mesmo `ME`, um por padrão |
| **5 · Sem impressão digital** | os erros cuja mensagem não tem nome de exceção (nunca contam como recorrentes), por tipo do erro. **Parada R1** se forem muitos: a chave pode estar escondendo um padrão | `ME --nome residuo_sem_nome_<BASE_ID> --de T --onde "padrao=<a chave>"` |
| **6 · Formato da mensagem** | na classe de sintaxe, quantos erros têm `linha_rejeitada_ok` falso: estão no resíduo por falta de formato, não por diagnóstico | `ME --nome residuo_formato_<BASE_ID> --de T --onde submecanismo=codigo_mal_escrito --onde linha_rejeitada_ok=False` |

**O passo 0 do procedimento (cruzar com as outras bases pelo mecanismo)** não é desta mineração: a skill descreve a
base que está na mesa. Registre no relatório os padrões recorrentes, para o pesquisador procurá-los nas outras bases.

**Os passos de leitura e de regra** (conferir o agrupamento, de quem é a falha, que unidade, escrever a regra) são
leitura e decisão. Aqui se registram as paradas, que vão para o roteiro `residuo` da `mineracao-investigacao`:
- **R1 · O agrupamento:** a máscara juntou erros diferentes?
- **R2 · De quem é a falha:** agente, harness/infra ou limite do LLM ou do interpretador;
- **R3 · Que unidade:** estender uma existente ou criar uma nova.

## 5 · O encontro: auditoria × tabelas

Quando o auditor terminar, da raiz:

```
uv run python <esta skill>/scripts/comparar_auditoria.py <pasta-da-analise> <pasta-da-analise>/pipeline/resultados/mineracao/residuo/auditoria_residuo.json
```

O script confronta padrão por padrão (erros, execuções, meses, papéis, tokens, chave, passa) e os totais por balde.
Ele também roda as conferências internas: a soma dos padrões é igual aos casos; os baldes batem nas duas tabelas;
todo caso tem padrão.

- **Saiu com 0:** os achados estão verificados. No relatório, a verificação leva os dois comandos e o caminho do JSON.
- **Saiu com 1:** **pare**. Registre cada DIVERGE ou FALHA e não tire conclusão das medidas que divergem. Não edite a
  auditoria, o pipeline nem as tabelas.

## 6 · Saída

- **Relatório:** `pipeline/resultados/relatorio_residuo_<BASE_ID>_<AAAA-MM-DD>.md`, no esqueleto da `mineracao-base`.
  Ele traz a evidência de cada achado, as conferências do script, o encontro e as paradas, cada parada com a pasta de
  evidência.
- **A tabela que sai do ambiente:** a `residuo_padroes.csv` sem as listas de papéis, se o pesquisador pedir. Ela só
  tem contagens, a classe, o padrão mascarado e os meses. Passe-a e o relatório pelo `versao_para_sair.py` e pelo
  `varrer_pii.py`.
- **Para o pesquisador:**
  - o tamanho do resíduo e a decisão de cada balde;
  - o Pareto: quantos padrões fazem metade;
  - os padrões recorrentes, com as paradas R1–R3 e a pasta de evidência de cada um;
  - o topo de tokens;
  - o resultado do encontro;
  - o caminho do relatório completo.
- **Não leia casos nesta mineração.** O pesquisador escolhe a ordem dos padrões que vão para a investigação
  (`/investigar residuo R1 <padrão>`, skill `mineracao-investigacao`). Cada regra que sair de lá é um Ajuste: a
  interpretação se fecha com o pesquisador, a proposta de código vem depois, e a mudança só depois da aprovação.
