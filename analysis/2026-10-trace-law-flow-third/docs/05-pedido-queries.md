# Pedido de dados complementares — o que falta na extração atual e o que cada pedido destrava

> Códigos e siglas: [glossário](../../glossario.md).

**Para que serve este documento:** levar ao tutor o que pedir na tabela de origem (`tbnm9100_exeo_aget`) para
completar a análise da base 3. Descreve **o que** cada pedido precisa trazer e **por quê** — não traz a consulta
pronta. Cada pedido aponta a limitação medida que ele resolve ([procedimento §4](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas))
e como conferimos o recebimento.

**Ordem de valor:** A (denominadores) destrava as taxas e quase todos os gráficos de custo da base 1; B (complemento
dos pendentes) fecha os 24% de erros que hoje ficam sem unidade; C (ajustes na extração de erros) corrige o resto.
A e B são independentes e podem vir antes de C.

**Regra comum aos três:** usar **o mesmo recorte da extração atual** — mesmo período, mesma escolha de snapshot por
execução + agente, mesmo tratamento do JSON da memória, mesmos ActionSteps — e mudar só o que cada pedido descreve.
Sem isso, as tabelas não se juntam com o parquet atual. Cada pedido traz uma coluna de conferência para provar a
junção.

---

## A · Denominadores: o total de passos e de tokens de cada papel

**O que pedir (a frase para o tutor):**

> Quero uma tabela com **uma linha por execução, agente e papel**, trazendo o **total de ActionSteps e o total de tokens (entrada, saída e total)** de todas as execuções, a **data e hora de início**, a **versão do agente** e **quantos erros estruturados e quantas suspeitas cada linha tem**. Use o mesmo recorte e as mesmas definições da consulta atual. O parquet só guarda os passos com erro, então preciso desses totais para calcular a taxa de erro por papel, mês e versão; a soma dos erros e das suspeitas tem que dar 30.141 e 1.280, para eu confirmar que a tabela se junta ao parquet. Só números e marcas de sim/não, sem texto, em parquet no mesmo ambiente do parquet atual.

**O que falta hoje.** O parquet só tem os passos com erro. Sabemos que um papel tem 5.028 erros, mas não se ele erra
muito ou se roda muito, e não dá para calcular nenhuma taxa por papel, mês ou versão ([relatório §7](02-relatorio-achados.md#7--leituras-do-painel)).
Só temos a taxa global do guia: 30.141 erros em 283.925 ActionSteps, cerca de 10,6%.

**Como a tabela é usada.** O tutor entrega o **total**; o parquet já tem a parte **com erro**; a parte **sem erro sai
por diferença** (total menos erros estruturados, nos passos e nos tokens). As suspeitas (1.280) não têm erro formal e
não saem do total.

| Coluna | Para quê |
|---|---|
| execução, agente, papel (`cod_idef_exeo`, `cod_idef_aget`, `papel`) | a chave da junção com o parquet: agrupo o parquet pelas três e junto |
| data e hora de início (`dat_hor_inio_exeo`), versão do agente (`cod_vers_aget`) | taxa por mês, por dia e por versão |
| total de ActionSteps | o denominador de toda taxa |
| tokens de entrada, de saída e total, somados sobre os ActionSteps do papel | custo dos erros no gasto total; a entrada e a saída separadas testam a hipótese de que o custo do erro é o contexto acumulado (a única célula do notebook da base 1 que usa entrada e saída é a razão entrada ÷ saída por passo; as outras 12 usam só o total) |
| quantos erros estruturados e quantas suspeitas a linha tem | **conferência**: somados por chave, têm que bater com o parquet (30.141 e 1.280) |

**Regras:** o **mesmo recorte** da query atual (mesmo período, mesma escolha de snapshot por execução e agente, mesmo
filtro de tamanho, mesmo tratamento do JSON) e as **mesmas definições** de erro estruturado e de suspeita. Entram as
execuções **sem erro** e os papéis **sem nenhum ActionStep** (na base 1, 31% das linhas): a subtração só funciona se o
total cobrir todas. **Só números e marcas de sim/não, nenhum texto.**

**O tamanho.** A tabela só tem números: da ordem de 70 a 200 mil linhas (1 a 3 papéis por execução, como na base 1),
bem menor que o parquet atual, que carrega texto longo.

**Exemplo do formato (fictício; só a tabela nova):**

| exec | agente | papel | início | versão | ActionSteps | tokens entrada | tokens saída | tokens total | erros | suspeitas |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| E1 | 200 | RoteadorCivel | 2026-05-12 14:03 | 5 | 4 | 13.268 | 723 | 13.991 | 0 | 0 |
| E2 | 1 | managerAgent | 2026-05-12 14:10 | 5 | 4 | 40.360 | 6.293 | 46.653 | 2 | 0 |
| E2 | 1 | WorkflowManager | 2026-05-12 14:10 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| E3 | 168 | RespostaBacen | 2026-05-13 09:41 | 5 | 6 | 80.000 | 4.000 | 84.000 | 1 | 1 |

**O que destrava** (gráficos do notebook da base 1): taxa de erro por papel, mês e versão; custo de uma execução com
erro × sem erro; concentração de custo (curva de Lorenz); desperdício como % do orçamento de cada papel; evolução
mensal do custo por execução; o funil das execuções; e a resposta para "agosto teve mais execuções ou mais erro por
execução?".

**Não destrava:** falhas silenciosas e reincidência ao longo da execução inteira (exigem o conteúdo de todos os
passos); o sucesso por conteúdo (exige a resposta final).

**Conferência no recebimento:** a soma de `erros` = 30.141 e a de `suspeitas` = 1.280; toda chave (execução, agente,
papel) do parquet existe na tabela, com o mesmo número de erros e de suspeitas por chave.

**Entre as bases:** o agente é um identificador numérico (`cod_idef_aget`); o papel é o nome gravado dentro da memória
da execução. Na base 1, cada execução tem 1 agente, e o agente orquestrador carrega 3 papéis juntos (`managerAgent`,
`ConversationAgent`, `WorkflowManager`); a versão está vazia em 514 de 1.000 linhas e vale `0` nas demais. Por isso a
unidade é a linha de execução, agente e papel.

---

## B · Complemento dos pendentes: fecha os 24% sem unidade

**O que falta hoje.** 7.107 erros estruturados (24%, 143 mi de tokens) ficam pendentes: a regra de classificação
existe, mas a janela da extração não traz o dado que ela precisa. Cada motivo pede um dado diferente
([relatório §2](02-relatorio-achados.md#2--cobertura-o-que-as-regras-conseguem-decidir)). No teste com a base 1, os
pendentes da mesma extração foram 83 de 498, e todos têm causa conhecida (o corte da mensagem e o histórico).

**O que pedir.** Uma tabela **só das linhas com erro estruturado** (as mesmas 30.141), com a mesma chave do parquet
atual (execução, agente, papel, posição do passo), e estas colunas:

| Pendência (erros) | O que trazer | Com isso |
|---|---|---|
| Nome não definido sem passo anterior identificado (5.818) | a **posição do ActionStep dentro do papel** (0 = primeiro) e o total de ActionSteps do papel; se existe ActionStep anterior e se ele teve erro | a regra de sempre decide entre "nome de um passo que falhou" e "nome nunca definido" |
| | se o nome que falta **aparece no texto da tarefa** do papel e se **aparece no system prompt** (sim/não, calculado na consulta) | testa as hipóteses do [roadmap #1](04-roadmap.md): nome pedido pela tarefa ou pelo prompt × nome inventado |
| | se a mesma conversa (`cod_idef_cvsa_asnc`) teve uma execução anterior com o mesmo papel (sim/não) | testa a hipótese "o agente espera estado de uma chamada anterior" |
| Mensagem cortada em 20.000 caracteres (1.009) | o **comprimento original** da mensagem e os **últimos 4.000 caracteres** dela | o sintoma volta a ser reconhecido; na base 1, 81 dos 96 erros do retorno-dict só se reconhecem pelo fim |
| Timeout sem prompt e código (215) | o comprimento original do código e o **código inteiro** (ou o fim dele) quando passa de 12.000; os **nomes das ferramentas declaradas** no system prompt do papel, numa tabelinha à parte (papel, versão, nome da ferramenta) | a regra separa código lento, timeout do interpretador e resultado bruto na resposta |
| Linha rejeitada sem o código inteiro (46) | o mesmo comprimento e fim do código | a regra acha a linha rejeitada |
| Histórico insuficiente para separar retorno colado (14) | **quantos pares `"chave": "texto"`** apareceram nas observações dos passos anteriores do papel (um número, calculado na consulta) | a regra decide entre retorno colado e texto em literal |
| Numeração ambígua do passo anterior (5) | a posição do ActionStep e o **número da chamada** (contador de TaskStep antes do passo) | a regra decide se o passo anterior é da mesma chamada |

**O que destrava:** todos os 7.107 pendentes passam a ter os dados que a regra pede. Isso não garante que todos
caiam numa unidade — alguns podem ir para o resíduo — mas tira a pendência por falta de dado. Também traz de volta a
recorrência do retorno-dict, que hoje aparece com 2 erros por causa do corte.

**Conferência no recebimento:** 30.141 linhas; toda chave existe no parquet atual; nos erros sem corte, o fim da
mensagem é igual ao fim da mensagem atual.

---

## C · Ajustes na extração de erros (a próxima versão da query)

O que ainda não é coberto por A e B. Cada item, a limitação que resolve e a evidência:

| Ajuste | Limitação ([procedimento §4](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas)) | Evidência | O que destrava |
|---|---|---|---|
| Incluir o **agente** na partição que monta o passo anterior e os seguintes | 6 | a partição atual é execução + papel | janelas e cascatas sem misturar agentes |
| No filtro de tamanho, tratar texto ausente como **comprimento zero** em vez de excluir a execução | 7 | base 3: 20.971 de 20.986 execuções com erro têm resposta final gravada (base 1: 34 de 318) | confirma se execuções sem resposta final estão sendo cortadas — e, se estiverem, as traz de volta |
| Reconhecer **"Error calling tool"** nas observações como sinal próprio (falha de ferramenta sem erro estruturado) | 3 | base 1: a regra de suspeita atual pega 0 das 119 falhas silenciosas | o balde das falhas silenciosas |
| Trazer o **nome do modelo** e uma **versão do system prompt** (um hash basta) | 4 | colunas ausentes | separar erro do modelo de erro do prompt nas candidatas concentradas num papel |
| Trazer **todas** as ferramentas chamadas no passo, não só a primeira | 8 | base 1: a primeira é sempre o interpretador (5.742 de 5.742) | a ferramenta que de fato falhou |

---

## O que não pedir

- Texto de caso além do que B descreve (o fim da mensagem e do código). As marcas sim/não e as contagens são
  calculadas na consulta justamente para não exportar a tarefa, o prompt ou as observações.
- Identificadores fora do ambiente da máquina 2: as tabelas ficam lá, como o parquet atual.
