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

## A · Denominadores: uma linha por execução, agente e papel

**O que falta hoje.** O parquet só tem os passos com erro. Não dá para calcular nenhuma taxa (erros por passo, por
execução, por papel, por mês, por versão) nem saber quanto do orçamento de tokens os erros consomem. Hoje não dá para
separar "este papel erra mais" de "este papel roda mais" — e a base 3 mostrou que quase toda candidata se concentra
em um ou dois papéis ([relatório §3](02-relatorio-achados.md#3--triagem-o-destino-de-cada-unidade)).

**O que pedir.** Uma tabela com **uma linha por execução + agente + papel**, com todos os passos (com e sem erro):

| Coluna | Para quê |
|---|---|
| execução, agente, papel, mês de início, versão do agente, status da execução | chave da junção e recortes |
| número de ActionSteps, TaskSteps e PlanningSteps | denominador por passo; funil da execução |
| tokens de entrada, de saída e total, somados sobre todos os ActionSteps | orçamento; custo do erro como % do orçamento |
| duração somada dos ActionSteps | tempo como % do total |
| número de chamadas de ferramenta (tamanho de `tool_calls` somado) | tokens por chamada de ferramenta |
| se algum ActionStep do papel é resposta final; se o último ActionStep tem erro | trajetórias que terminam em erro |
| **número de erros estruturados e de suspeitas no papel** | **conferência**: somado por chave, tem que bater com as linhas do parquet atual |
| total de execuções na tabela no período, inclusive sem memória (uma contagem só) | primeira barra do funil |

Opcional, se for possível calcular na própria consulta sem exportar texto: uma marca de **resposta final vazia ou
degenerada** (sim/não), para o sucesso por conteúdo.

**O que destrava** (gráficos do notebook da base 1): custo de uma execução com erro × sem erro; taxa de erro por
papel, por mês e por versão; concentração de custo (curva de Lorenz); desperdício como % do orçamento de cada papel;
tokens por chamada de ferramenta; evolução mensal do custo por execução; o funil completo da execução. Com a marca
opcional, o sucesso por conteúdo.

**Não destrava:** falhas silenciosas e reincidência ao longo da execução inteira (exigem o conteúdo de todos os passos).

**Conferência no recebimento:** a soma dos erros estruturados da tabela = 30.141; a soma das suspeitas = 1.280; toda
execução + agente + papel do parquet atual existe na tabela.

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
