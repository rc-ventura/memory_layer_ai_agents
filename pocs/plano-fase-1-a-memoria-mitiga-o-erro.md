> **Sub-atividade:** 1.6 / 1.7 (alimenta 2.4 e 3.6) · **Tipo:** Receita passo a passo, com racionais · **Status:** rascunho para discussão · **Data:** 12/11/2026

# Fase 1 — a memória, de fato, mitiga o erro? (agentes reais)

> Os termos do projeto (degrau da validação, unidade, memória de reforço) estão no [glossário](../analysis/glossario.md).
> Este documento usa nomes, não códigos. Os conceitos (replay, Holm, intervalos, quantas execuções para o erro aparecer)
> estão explicados à parte em [`conceitos-do-experimento.md`](conceitos-do-experimento.md).

## 0. Onde este documento entra

O [plano geral](plano-experimento-validacao-memorias.md) trata de **como** entregar a memória (nativa, por ferramenta, no
erro), **quem** a produz (revisada × autogerada) e **o que** ela diz (novo × reforço). Antes de qualquer uma dessas
perguntas existe uma mais básica, que este documento responde:

> **A memória que já temos mitiga o erro que ela descreve, quando injetada num agente real? E a que custo?**

| Fase | Pergunta | Agentes | Documento |
|---|---|---|---|
| **1 (este)** | a memória mitiga o erro? a que custo? | **os agentes reais**, com **inputs reais** de produção | este |
| 2 | qual entrega, qual origem, qual conteúdo | primeiro os agentes reais; os agentes-espelho do plano geral servem de ensaio e de reserva | [plano geral](plano-experimento-validacao-memorias.md) |

Só depois de a fase 1 dizer que a memória mitiga vale gastar execuções comparando formas de entrega, origens e conteúdos.
**O que já foi escrito não é descartado:** o núcleo estatístico do plano geral (§8 medidas, §9 amostra, §9.3 K e N, §12
análise) é reaproveitado aqui, e o plano geral continua valendo para a fase 2. A diferença é que a fase 1 roda no agente
real, e isso cria problemas que o espelho não tinha (§3 e §13).

## 1. A pergunta, e o que "mitiga" quer dizer

**Estimando principal.** Para cada par (agente, memória): a probabilidade de uma execução ter o erro-alvo **com** a
memória, comparada com a probabilidade **sem** ela, nos mesmos inputs. A redução relativa do risco é a medida de eficácia.

Há **quatro resultados possíveis**, e todos são resposta:

| Resultado | Leitura | Consequência |
|---|---|---|
| **mitiga e compensa** | o erro cai e a economia paga o custo de injetar | a memória vai para a fase 2 e para o piloto real |
| **mitiga, mas não compensa** | o erro cai, mas o erro é raro demais, ou a memória cara demais | fica monitorada até a incidência crescer |
| **não mitiga** | o erro fica igual | volta ao degrau 3: a causa não era a suposta |
| **piora** | o erro sobe, ou aparece outro | não injetar; investigar o texto |

**Uma consequência que muda o desenho.** Uma memória só paga se a incidência do erro passar de `c ÷ s` (custo de injetar ÷
economia de um erro evitado). Com valores de hipótese (memória de 20 tokens lida em 7 passos ≈ 140 tokens; um passo
perdido ≈ 13.135 tokens, a média da base 3), isso dá **cerca de 1% das execuções**: abaixo disso nenhuma memória paga,
nem com 100% de eficácia. No RoteadorCivel, em agosto, o erro dos imports apareceu em 0,8% das execuções **que tiveram algum erro** (dossiê do
sandbox, item 16); sobre todas as execuções do papel a taxa é ainda menor. **Nesse mês e nesse papel, a conta não
fecharia.** Esses dois valores são hipóteses; o custo real
de injetar e de um passo perdido por papel é uma das medidas da fase.

## 2. Quais pares (agente × memória)

O catálogo tem 3 memórias no degrau 3. Cruzadas com os quatro agentes que você indicou, **só o que o repositório sustenta**:

| Agente | Memória que mira o erro dele | O que se sabe (fonte) | O que falta |
|---|---|---|---|
| **ContestacaoCivel** | memória das funções proibidas (inspeção de valores com `repr`, `dir`, `__name__`) | foi o papel de maior volume dessa lição na leitura de 19/10 (450 de 523 antes dos ajustes seguintes; dossiê do sandbox) | o número **atual** por papel (317 no total) e por mês |
| **JoogleAnalytics** | par: memória dos imports + memória do pandas | 231 erros de `pandas` e 105 de `json`, na mesma linha; na base 2, 3 de 10 execuções (a base 2 tem só 10 execuções desse papel) | o denominador por mês na base 3 |
| **CalculoTrabalhista** | memória dos imports (`json`) | 41 erros de `json` na base 3 | o denominador; se a memória das funções proibidas também vale |
| **RespostaBacen** | **nenhuma do degrau 3 mira o erro dele** | os erros dele são de outras unidades (campo inexistente, protocolo, retorno-string); as memórias do sandbox dele são raras (1 erro) ou de reforço (5 erros) | — |

**O que isso diz sobre o desenho.** Dos quatro agentes, **três são candidatos a alvo** (o erro acontece e a memória mira nele; a volumetria do §4 decide quais
sobram) e um,
o RespostaBacen, serve para **verificar dano**: as duas memórias globais (imports e funções proibidas) são injetadas nele
do mesmo jeito, e o experimento mede se elas atrapalham onde o erro é raro. É parente, não igual, do dano por memória
errada que o MERIT mede (memória desatualizada, contraditória ou distratora; Mishra e Mishra, 2026).

**Regra para um par entrar na fase 1:** o erro precisa aparecer o bastante para a conta do §4 fechar. Um par que não
fecha vai para "monitorada" e deixa de ser tema desta fase, em vez de rodar sem poder.

## 3. Antes de rodar qualquer coisa: o que o agente real impõe

Os agentes-espelho do plano geral rodavam ferramentas simuladas e dados sintéticos. O agente real tem ferramentas de
verdade e inputs de verdade. Cinco decisões precisam estar fechadas **antes** do primeiro disparo, e a leitura do código
do agente é o que as fecha.

**3.1 Ler o código do agente — roteiro.** Para cada um dos quatro agentes:

| O que achar no código | Por que importa |
|---|---|
| onde o **prompt de sistema** é montado, e se há um parâmetro de instruções extras | é por onde a região `<memory>` entra **sem editar o repositório** (o plano geral proíbe editar o prompt do repositório) |
| a lista de **ferramentas**, e para cada uma: só lê, ou escreve/envia? | decide se a execução pode ser repetida sem efeito colateral (3.3) |
| o **modelo** e os parâmetros (temperatura, limite de passos, intervalo de planejamento) | o modelo é um fator: o erro mudou com a troca de modelo em agosto/2026 (relatório da base 2, §2) |
| como o **input** chega ao agente (o formato do `TaskStep`) | para montar tarefas a partir de inputs reais |
| onde o **trace** de cada execução é gravado, e se há como ler uma execução pelo identificador | é o registro de cada rodada; também é de onde vêm os inputs reais |
| se há **memória própria da plataforma** ligada (checkpoints, memória nativa do Hermes) | precisa estar **desligada ou isolada**: se o agente lembrar de uma execução anterior, as repetições deixam de ser independentes |
| se existe **ambiente de desenvolvimento ou homologação** | é onde rodar |
| a **versão atual** do prompt e do código | o erro histórico pode ter sido corrigido depois |

**3.2 Onde roda.** Os inputs reais são conteúdo jurídico real. O plano geral veda mandar conteúdo de trace real a um LLM
externo, e a regra não muda: **a fase 1 roda dentro do ambiente da empresa, no gateway de LLM da própria plataforma**, e
de lá só saem contagens, hashes e nomes. Isso é uma aprovação a pedir (compliance e o tutor), não uma decisão minha.

**3.3 Ferramentas com efeito colateral.** Rodar o agente real de novo pode expedir ofício, gravar no banco ou enviar
mensagem. O blueprint e a arquitetura já registram que o desfecho jurídico "tem efeito colateral real". Três saídas, e a
leitura do código diz qual vale para cada agente:

| Saída | Como | Custo e risco |
|---|---|---|
| **ferramentas ao vivo, em homologação** | ambiente de homologação com dados que não fazem mal | o mais fiel; exige o ambiente |
| **gravar e repetir (record and replay)** | as respostas das ferramentas vêm da execução original (estão no trace) e são devolvidas ao agente quando ele chama a mesma ferramenta com os mesmos argumentos | sem efeito colateral e determinístico, mas **falha quando o agente chama de outro jeito**, e é justamente o que a memória pode provocar; precisa de uma política para o caso "não achei a resposta gravada". O precedente acadêmico é o servidor de API virtual com cache e simulador do StableToolBench (Guo et al., 2024); a prática de gravar no limite da ferramenta é descrita sobretudo em material de fornecedores, que é evidência fraca |
| **só ferramentas de leitura ao vivo, as de escrita simuladas** | classifica cada ferramenta; as de escrita devolvem um recibo falso | meio-termo; o agente pode reagir ao recibo falso |

**3.4 Os inputs mudam de estado.** Um input real de ontem, rodado hoje, pode devolver outro retorno das ferramentas (o
processo andou). Para a comparação entre braços isso não pesa (os dois braços rodam o mesmo dia), mas pesa para comparar
com a taxa histórica. Por isso a taxa de hoje se **mede** (§6), em vez de se herdar da base 3.

**3.5 Custo e limites de uso.** Cada execução real custa tokens do gateway da empresa. O orçamento e os limites de
requisições são decisão do dono da plataforma. A estimativa está no §4.

## 4. Volumetria: quantas execuções, e por quê

A pergunta tem duas partes: **quantas execuções com o erro** são necessárias para enxergar uma redução (a parte
estatística), e **quantas execuções no total** precisam rodar para o erro aparecer essas vezes (a parte que depende do
agente real).

### 4.1 Quantas execuções com o erro, por braço

Detectar uma redução relativa do risco, poder de 80%, teste bilateral. A coluna "a = 0,01" é a de uma família de cerca de
cinco pares corrigida por Holm (um teste por par, §11). As contas são de 12/11/2026 e usam a fórmula de duas proporções
independentes, que é conservadora quando os braços rodam os mesmos inputs (a fórmula pareada do Miller, com os valores do
piloto, refina isso, §9.3 do plano geral).

| Taxa do erro sem memória | redução de 30% (a = 0,05 / 0,01) | de 50% | de 70% |
|---:|---:|---:|---:|
| 80% | 59 / 87 | 23 / 34 | 12 / 18 |
| 60% | 120 / 179 | 42 / 63 | 20 / 31 |
| 40% | 244 / 363 | 82 / 122 | 38 / 56 |
| 20% | 615 / 915 | 199 / 297 | 90 / 134 |
| 10% | 1.356 / 2.018 | 435 / 647 | 194 / 289 |
| 5% | 2.838 / 4.224 | 906 / 1.348 | 402 / 599 |
| 2% | 7.286 / 10.842 | 2.319 / 3.450 | 1.027 / 1.528 |
| 1% | 14.699 / 21.872 | 4.673 / 6.954 | 2.068 / 3.077 |

**A lição da tabela:** o número cresce muito quando o erro é raro. A taxa que importa **não** é a taxa do erro na produção
(a incidência), e sim a taxa **entre os inputs onde o erro aparece**, que é o que se consegue enriquecendo a amostra (4.3).

### 4.2 Quantas execuções no total, se os inputs forem sorteados

Se a amostra for sorteada da produção, o erro aparece com a frequência da incidência `π` (por braço):

| Incidência `π` | execuções para 60 com o erro | para 116 com o erro |
|---:|---:|---:|
| 20% | 300 | 580 |
| 10% | 600 | 1.160 |
| 5% | 1.200 | 2.320 |
| 2% | 3.000 | 5.800 |
| 1% | 6.000 | 11.600 |
| 0,8% | 7.500 | 14.500 |

Para o JoogleAnalytics, com 231 execuções com o erro de `pandas` em 6 meses, a base 3 só diz quantas **tiveram** o erro; o
denominador (quantas execuções o papel teve) é o que falta para a incidência. **Sorteio puro não é viável para erros de
1% ou menos**: o número de execuções chega a dezenas de milhares.

### 4.3 O desenho que torna isso viável: dois conjuntos de inputs

Como o plano geral já fazia com as tarefas-gatilho e as neutras, a fase 1 usa dois conjuntos de **inputs reais**:

| Conjunto | O que é | Para que serve | Como se monta |
|---|---|---|---|
| **gatilho** | inputs cuja execução original **teve** o erro | medir a **eficácia**: aqui o erro tem chance alta de aparecer | os identificadores das execuções com o erro (a base 3 os tem; o input vem do banco de traces) |
| **controle** | amostra sorteada de inputs do papel, sem olhar o erro | medir o **custo de injetar** onde o erro não acontece, o **dano** e a incidência de hoje | sorteio das execuções do papel |

**O risco desse desenho, e o controle.** Selecionar inputs porque erraram uma vez traz **regressão à média**: parte deles
não erra de novo, só por acaso (Barnett et al., 2005). Por isso o **braço sem memória é rodado de novo nos mesmos inputs**
e a comparação é entre os dois re-rodados, nunca entre "antes" e "depois". Além disso, a pergunta central do piloto
(§6) é **a taxa de reprodução**: dado que o input errou na produção, com que frequência ele erra de novo hoje, sem
memória? É ela que vira a "taxa do erro sem memória" da tabela 4.1.

### 4.4 Quantos inputs, e quantas repetições de cada (K e N)

Cada input é repetido `K` vezes (o agente erra num dia e acerta no outro), e há `N` inputs. O número de execuções com o
erro por braço é `N × K`, mas as repetições do mesmo input se parecem, e o ganho de repetir cai conforme a parte da
variação que é do input (`ρ`). A regra do plano geral (§9.3) vale aqui sem mudança: `N = n · (1 + (K − 1)·ρ) / K`.

**Por que o caso dos agentes reais é favorável.** Você disse que as tarefas deles são geralmente fechadas, quase a mesma
tarefa. Isso sugere que o erro depende **pouco do input** e muito da sorte da execução, isto é, `ρ` perto de zero. Se for
assim, repetir o mesmo input rende tanto quanto trocar de input, e `N × K` é o que conta. Para `n = 116` por braço (com 122, os números sobem cerca de 5%):

| K | N com ρ = 0 | N com ρ = 0,5 |
|---:|---:|---:|
| 1 | 116 | 116 |
| 3 | 39 | 78 |
| 5 | 24 | 70 |

O `ρ` se mede no piloto. Se for alto, são poucos inputs que sempre erram e muitos que nunca erram, e a eficácia só vale
para o tipo de input que erra: o resultado fica restrito a essa família (§13).

**Uma ressalva sobre "tarefa fechada".** Inputs quase iguais se comportam como grupos de perguntas relacionadas
(Miller, 2024, §2.2). Tudo vale para a **família de inputs do agente**, e a análise agrupa por família (§11).

### 4.5 A conta, resumida, para cada par

1. Medir no piloto: a taxa de reprodução `p` (sem memória, no conjunto gatilho), a incidência de hoje `π` (no conjunto
   controle) e o `ρ`.
2. Ler `n` na tabela 4.1, na linha de `p`.
3. Escolher `K` e `N` pela tabela 4.4.
4. **O par é viável** se o conjunto gatilho tem inputs suficientes para fechar `N`. Se não tem, o par fica monitorado.

Um exemplo, **com valores de hipótese e só para ilustrar**: `p` = 40%, redução de 50%, família de cinco pares (a = 0,01):
122 execuções com o erro por braço; com `K = 3` e `ρ` = 0, são 41 inputs; dois braços (sem memória e com memória) dão
cerca de 250 execuções por par no conjunto gatilho; mais o conjunto controle e o placebo. **Os números reais saem do
piloto.**

## 5. O que se mede e como

Tudo o que não for julgamento é calculado por script, sobre o registro da execução. A base é o §8 do plano geral; aqui só
o que muda ou se acrescenta por causa do agente real.

| O que | Definição | Por que |
|---|---|---|
| **eficácia (principal)** | a execução teve o erro-alvo? (sim ou não), classificado pelas regras do pipeline | é a pergunta da fase |
| **custo em tokens** | tokens de entrada e saída da execução inteira, com × sem memória | a memória custa leitura em todo passo |
| **custo em tempo** | duração decomposta em modelo, ferramenta e interpretador | a ferramenta real tem latência; o espelho não tinha |
| **passos por execução e tamanho da cascata** | número de passos e de erros seguidos | o ganho por erro evitado |
| **adesão à lição (taxa de uso da memória)** | quando a memória estava lá e o erro era possível, o código fez o que ela diz? (por AST) | separa "o agente ignorou a memória" de "a memória não funciona". O MERIT chama a fração em que o agente não usa a memória certa de *Ignore Rate* e mediu cerca de 45% nos casos difíceis |
| **outros erros** | taxa de qualquer erro fora da unidade, com × sem memória | "sem criar outro" |
| **qualidade da resposta final** | ver abaixo | guarda: a memória não pode piorar o que o agente entrega |
| **robustez entre inputs** | fração dos inputs em que a memória melhora, não muda ou piora | uma média boa pode esconder inputs que pioram; no SkillsBench, 16 de 84 tarefas pioraram com skills curadas (resumo da v1) |
| **estabilidade** | fração dos inputs em que todas as `K` repetições passam (`pass^k`, Yao et al., 2024) | a métrica de estabilidade do Plano de Trabalho |

**A qualidade da resposta final é o ponto difícil.** Num agente real não há resposta certa conhecida. Quatro níveis, do
mais barato ao mais caro, e nenhum usa um LLM como juiz, porque um juiz sem calibração é o risco que o projeto já
registrou (o melhor juiz do TRAIL alcança 11% de acerto conjunto; perguntas abertas):

1. **Estrutural:** a execução terminou com resposta final, no formato pedido, sem falha silenciosa.
2. **Presença (determinístico):** os números, datas e identificadores da resposta final aparecem nas observações da
   mesma execução (a medida "groundedness-as-presence" do roadmap da base 1).
3. **Pareado e cego, em amostra:** especialistas do domínio comparam, sem saber qual é qual, as respostas dos dois braços
   para o mesmo input. Uma amostra pequena por agente.
4. **Equivalência com a resposta original da produção**, onde ela existir. É apenas uma referência, não é verdade:
   a execução original pode estar errada.

**Custos que o plano geral já tinha e continuam:** a compensação em tokens e em segundos (`c`, `s`, `π`, §8.2 e §8.3 do
plano geral), com a duração real do passo com erro vinda da base 3.

## 6. O piloto (só o braço sem memória)

O piloto não testa a memória: **mede o terreno**. É o passo que decide se cada par é viável, e com que `K` e `N`.

| O que se mede | Como | Decide |
|---|---|---|
| **o erro ainda existe hoje?** | o conjunto gatilho, sem memória, na **versão atual** do agente | se não existe mais, a memória descreve um erro do passado: o par fica monitorado |
| **a taxa de reprodução `p`** | fração das execuções do conjunto gatilho que erram de novo | a linha da tabela 4.1 |
| **a incidência de hoje `π`** | fração das execuções do conjunto controle com o erro | a conta de compensação (§1) |
| **o `ρ`** | análise de variância entre e dentro dos inputs (plano geral, §9.3) | `K` e `N` |
| **tokens e tempo por execução**, por papel | média e mediana | a conta de custo e o orçamento |
| **a taxa de recaída do ambiente** | quantas execuções falham por motivo que não é do agente (ferramenta fora do ar, tempo-limite) | as falhas de infraestrutura se separam e se repetem, fora da nota |

**Tamanho do piloto, por par:** 20 inputs do conjunto gatilho × 5 repetições mais 20 inputs do conjunto controle × 3
repetições = 160 execuções (a mesma ordem do plano geral, que estima o `ρ` com erro de cerca de ±0,10). Com quatro a cinco pares,
de 640 a 800 execuções reais.

**Portas de decisão do piloto** (escritas antes dos dados):

| Porta | Regra | Se falhar |
|---|---|---|
| erro ainda existe | o limite inferior do intervalo da taxa de reprodução `p` é maior que zero | par monitorado |
| viável | inputs do conjunto gatilho × `K` × `p` ≥ `n` da tabela 4.1 | par monitorado ou exploratório |
| seguro | todas as ferramentas do agente foram classificadas e a saída do §3.3 está definida | não roda |
| orçamento | execuções × tokens médios ≤ o teto fixado com a plataforma | reduz pares ou `K` |

## 7. As memórias e o injetor

**Qual lição vai para qual agente.** Pelo catálogo (campos `nao_vale_em` e `vale_junto_com`) e pelo §2:

- memória dos imports: todos os agentes, **exceto o `managerAgent`**;
- memória do pandas: só o JoogleAnalytics, **sempre junto com a dos imports** (as duas formam um par);
- memória das funções proibidas: global (o ContestacaoCivel é o alvo; o RespostaBacen é a verificação de dano).

**O injetor.** O texto injetado é o texto literal aprovado no degrau 3, sem reescrita, porque a revisão vale para aquele
texto. Ele entra na região `<memory>` (o formato do plano geral, §6), composta na hora de montar a execução, pelo
parâmetro de instruções extras do agente, **sem alterar o prompt do repositório**. O injetor registra, em cada execução,
quais memórias entraram e qual a versão do texto.

## 8. O experimento

**Braços (fase 1):** (1) sem memória; (2) memória nativa (a região `<memory>`); (3) placebo (a mesma região, texto do mesmo
tamanho, verdadeiro e sem relação com a tarefa), para separar o efeito do conteúdo do efeito de "mais texto". O placebo
custa cerca de metade a mais de execuções; **é uma decisão sua** (§14) se roda em todos os pares ou só nos de maior
volume. Sem o placebo, "a memória mitiga" não se separa de "mexer no prompt mitiga".

**Regras de execução** (as do plano geral, §13, mais as do agente real):

- os braços de um mesmo input rodam juntos, em **ordem sorteada**, para a deriva do provedor cair igual em todos;
- **sessão nova** a cada execução; memória própria da plataforma desligada ou isolada (§3.1);
- o **mesmo modelo, a mesma versão do agente e os mesmos parâmetros** em todos os braços; a versão e o modelo ficam
  registrados;
- o **pré-registro** (§10) congela os pares, os conjuntos de inputs (por hash), os textos das memórias, `K`, `N`, as
  medidas e os critérios **antes** do confirmatório;
- os inputs do piloto ficam **fora** do confirmatório;
- falhas de infraestrutura se separam, se classificam (as 8 causas do Eval Engineering) e se repetem fora da nota.

## 9. Critério de sucesso

Uma memória "**mitiga**" num agente se as quatro condições valerem:

1. **Eficácia.** A taxa do erro-alvo com a memória é menor que sem ela, com p < 0,05 depois do ajuste de Holm sobre os
   pares (cerca de 0,01 por par, numa família de cinco), e o intervalo de 95% da redução relativa **não inclui zero**.
2. **Especificidade.** A memória é melhor que o placebo na mesma medida.
3. **Sem dano.** A estrutura da resposta final não piora; a presença não piora; a taxa de outros erros não sobe; o
   resultado do cego, se feito, não favorece o braço sem memória; e nenhuma fração relevante dos inputs piora (a
   robustez do §5, com limite fixado no pré-registro).
4. **Robustez.** O resultado vale nas duas metades dos inputs (primeira e segunda metade, ou duas famílias) e, se o
   piloto rodou em dois modelos, nos dois.

Ela "**compensa**" se, além disso, a **incidência de equilíbrio** `c ÷ (c + s)` ficar abaixo da incidência de hoje `π` do
agente, com o limite superior do intervalo ainda abaixo de `π`. A conta é em **tokens**, em **segundos** (reportada, não
condição, porque a velocidade do provedor da plataforma é outra) e em **dinheiro** (tokens × o preço do gateway).

**Há um outro jeito de fixar a régua de eficácia**, mais rigoroso, que eu sugiro discutir: em vez de "reduz mais que
zero", exigir que a redução seja **maior que o efeito mínimo que paga o custo**, `e_min = c ÷ (π · s)`. Com os valores de
hipótese do §1, isso vai de 5% da redução (incidência de 20%) a mais de 100% (incidência de 1%, o caso em que nenhuma
memória paga). Ele liga a eficácia ao custo, mas exige mais amostra; é a **decisão 3 do §14**.

**Quais custos além de tokens e latência** (a pergunta sobre critérios de sucesso):

| Custo ou critério | Medida |
|---|---|
| tokens e dinheiro | compensação; custo por acerto (Erol et al., 2025) |
| latência | p50 e p95, decomposta; só descritiva como condição |
| **adesão** | taxa de uso da memória (o contrário do *Ignore Rate*) |
| **dano de memória fora de hora** | o RespostaBacen (§2): memórias globais injetadas onde o erro é raro; mede custo e piora |
| **estabilidade** | `pass^k` |
| **validade no tempo** | a memória foi validada para um modelo e uma versão; a troca de modelo ou do prompt reabre a validação (gatilho) |
| **auditabilidade** | cada injeção registrada (qual memória, qual versão, em qual execução) |

## 10. A receita, ponta a ponta

Cada passo diz **quem faz** (**Claude** aqui, com a base 1 e dados sintéticos; **Rafael** no ambiente da empresa, trazendo
só contagens, como nas outras bases) e **o que sai**. As durações são estimativas em dias úteis.

| # | Passo | Quem | Sai com | Critério para seguir | Dias |
|---|---|---|---|---|---:|
| 1 | **Ler o código** dos quatro agentes (roteiro do §3.1) | Rafael | o roteiro preenchido, uma ficha por agente | todas as linhas do roteiro respondidas | 2 |
| 2 | **Aprovações:** onde roda, gateway, orçamento, ambiente de homologação (§3.2, 3.5) | Rafael | o ok escrito | autorização para rodar agentes reais | a estimar |
| 3 | **Classificar as ferramentas** de cada agente e fechar a saída do §3.3 | Rafael, com o Claude | a tabela ferramenta × efeito colateral × saída | nenhuma ferramenta de escrita sem tratamento | 1 |
| 4 | **Contar a volumetria**: por agente e por mês, execuções, execuções com cada erro, passos, tokens, duração, modelo (§4) | Claude escreve e testa na base 1; Rafael roda | a tabela de volumetria (só contagens) | números conferidos por uma segunda implementação | 2 |
| 5 | **Fechar os pares** viáveis e os inputs disponíveis (§2, §4.3) | Rafael e Claude | a lista de pares, com o tamanho do conjunto gatilho | cada par tem inputs suficientes, ou vai a monitorada | 1 |
| 6 | **Montar os conjuntos de inputs** (gatilho e controle), sem repetir inputs quase iguais, com hash (§4.3) | Rafael, no ambiente | os conjuntos, **dentro do ambiente** | hash gravado | 1 |
| 7 | **O injetor**: a região `<memory>`, o registro, os filtros do catálogo (§7) | Claude escreve e testa; Rafael integra no agente | o injetor testado | uma execução de cada braço lida inteira | 3 |
| 8 | **O registro e o classificador** do erro-alvo, com segunda implementação (§5) | Claude | o código testado na base 1 | as duas implementações batem | 2 |
| 9 | **O piloto** (só sem memória), §6 | Rafael | taxa de reprodução, incidência, `ρ`, tokens, tempo | as portas de decisão aplicadas | 2 |
| 10 | **Decidir `K` e `N`** por par (§4.4 e §9.3 do plano geral) e **pré-registrar** | Rafael e Claude | o pré-registro com hash | aprovação do Rafael | 1 |
| 11 | **O confirmatório** (§8) | Rafael | os registros crus + o manifesto | todas as execuções previstas existem | 3–5 |
| 12 | **Análise e auditoria independente** (§11) | Claude escreve; Rafael roda | tabelas e o veredito por par | as duas implementações batem | 3 |
| 13 | **Leitura de uma execução inteira por braço**, e do cego, se houver | Rafael | o relato | — | 1–2 |
| 14 | **Fechamento:** o degrau 4 no catálogo, o relatório, e o que passa para a fase 2 | Rafael e Claude | os documentos | gate do pesquisador | 2 |

**Os comandos literais para o ambiente** (linhas completas, sem variáveis) saem **depois** que os scripts dos passos 4, 6
e 9 existirem e forem testados na base 1; até lá, este documento é o plano, não o roteiro de comandos.

## 11. Análise

Reaproveita o §12 do plano geral, com três acréscimos:

- **Uma unidade de inferência por par:** o input. As `K` repetições viram uma média por input; a incerteza se calcula
  sobre os inputs (Miller, 2024, §3.1), por bootstrap agrupado por **família de input** (o MERIT agrupa por arco do
  mesmo jeito).
- **Um teste por par, Holm sobre os pares.** Uma afirmação geral sobre vários agentes (a taxa conjunta) usa o teste de
  Cochran-Mantel-Haenszel com os agentes como estratos; **não** se somam agentes de custo e erro diferentes.
- **Pouca amostra:** intervalos bayesianos ou exatos, não a aproximação normal (Bowyer et al., 2025).

## 12. Literatura: como se mede memória

Não achei, na busca de 12/11/2026, **um protocolo-padrão** que reúna eficácia, passos, custo, uso da memória recuperada e
comparação com e sem memória. O mais próximo, para agentes que executam tarefas, é o **MERIT**. O nível de leitura de
cada fonte está na coluna da direita; nenhuma foi lida pelo Rafael.

| Fonte | O que mede, e o que levamos | Nível |
|---|---|---|
| **Mishra e Mishra (2026), *When Does Memory Help? A Cost-Aware Evaluation of Long-Term Memory in Tool-Using LLM Agents*** (arXiv:2609.05441) | sucesso em tarefas que dependem da memória, com linha de base sem memória; **utilidade marginal por dólar** (variação do sucesso ÷ variação do custo, e o "valor de equilíbrio da tarefa"); **taxa de uso da memória recuperada** (*Ignore Rate*); **dano por memória errada**; comparações pareadas, bootstrap agrupado e Holm. Levamos: a linha de base sem memória, a utilidade por dólar, a taxa de uso e o dano. Limite: tarefas sintéticas, três domínios, latência não medida | 📝 lido pela página do arXiv por um modelo pequeno (não pelo método de texto completo) |
| **Gloaguen et al. (2026), *Evaluating AGENTS.md*** (arXiv:2602.11988) | sem contexto × gerado por LLM × escrito por humano; sucesso, passos, custo e se o agente segue as instruções; testes estratificados | 📝🔎 página do arXiv lida por um modelo pequeno (ver [`literature/`](literature/README.md)) |
| **SkillsBench (2026)** (arXiv:2602.12670) | taxa de acerto e ganho normalizado; skills curadas ajudam, as autogeradas não; skills focadas, com no máximo três módulos, superam pacotes maiores; algumas tarefas pioram. Levamos a **robustez entre inputs** | 📝 só resumos |
| **Hu, Wang e McAuley (2025), MemoryAgentBench** (arXiv:2507.05257) | quatro competências (recuperação exata, aprendizado em tempo de teste, entendimento de longo alcance, seleção do que esquecer); aprendizado em tempo de teste é a mais próxima | 📝 só resumo |
| **Wei et al. (2025), Evo-Memory** (arXiv:2511.20857) | memória em fluxo de tarefas; a memória ajuda mas é frágil em estabilidade e reuso procedural. Reforça medir **estabilidade** | 📝 só resumo |
| **Yuan, Su e Yao (2026), recuperação × uso** (arXiv:2603.02473) | diagnóstico em três pontos: relevância do que foi recuperado, uso, classificação de falha. Reforça separar "a memória não chegou" de "chegou e o agente ignorou" | 📝 só resumo |
| **Xiong et al. (2025), gestão de memória** (arXiv:2505.16067) | o agente copia o que está na memória; erro guardado se propaga. É a razão do braço de dano e do gate | 📝 só resumo |
| **Kapoor et al. (2024)** (arXiv:2407.01502) · **Erol et al. (2025)** (arXiv:2504.13359) · **Yao et al. (2024)** (arXiv:2406.12045) | custo e acerto juntos, custo por acerto, `pass^k` | 📝 só resumos |
| **Guo et al. (2024), StableToolBench** (arXiv:2403.07714) | servidor de API virtual com cache e simulador, para repetir avaliações sem depender de ferramenta real. Base do §3.3 | 📝 só resumo |
| **Miller (2024)** (arXiv:2411.00640) | a estatística: decomposição da variância, K e N, pareamento | 🔎 ([`literature/miller-2411.00640.md`](literature/miller-2411.00640.md)); falta o ✅ |

**O que a literatura não resolve, e é nosso:** o agente real, com input real e ferramenta real, e a medida da qualidade
da resposta sem verdade conhecida (§5). Vale uma busca mais dirigida, e provavelmente um fichamento do MERIT em texto
completo, antes de fixar o §5.

## 13. Riscos específicos do agente real

| Risco | Controle |
|---|---|
| O erro histórico já foi corrigido na versão de hoje | o piloto mede, na versão atual, antes de gastar o confirmatório (§6) |
| Regressão à média: inputs escolhidos por terem errado | re-rodar o braço sem memória nos mesmos inputs e comparar os re-rodados (§4.3) |
| Efeito colateral de uma ferramenta | as saídas do §3.3; nada roda sem a ferramenta classificada |
| A ferramenta devolve outro estado hoje | os braços de um input rodam juntos; a taxa de hoje se mede, não se herda |
| O agente chama a ferramenta de outro jeito e a resposta gravada não existe | política para "não achei a resposta gravada"; contar quantas vezes acontece por braço |
| A família de inputs é estreita, e o resultado só vale para ela | declarado como limite; a análise agrupa por família; mais de uma família por agente, quando houver |
| O modelo ou o prompt mudam durante o experimento | modelo e versão congelados e registrados; qualquer troca invalida a rodada |
| Memória própria da plataforma contamina as repetições | desligada ou isolada (§3.1) |
| Uma execução real sem resposta conhecida: como saber se piorou | os quatro níveis do §5; o cego pareado em amostra |
| Custo | o teto fixado antes (§6, porta de orçamento) |
| Dados jurídicos reais fora do ambiente | tudo roda dentro; de lá só saem contagens e hashes |
| O agente de verificação de dano (RespostaBacen) não tem o erro, então a medida principal não existe nele | ali se mede **dano**, não eficácia |

## 14. Decisões que dependem do Rafael (uma por vez)

1. **O placebo roda em todos os pares, só nos de maior volume, ou fica para a fase 2?** Custa cerca de metade a mais de
   execuções; sem ele, "mitiga" não se separa de "mexer no prompt".
2. **A saída para as ferramentas com efeito colateral** (§3.3): ao vivo em homologação, gravar e repetir, ou só leitura
   ao vivo. Depende da leitura do código (passo 1).
3. **A régua de eficácia:** "reduz mais que zero" (o §9, condição 1) ou "reduz mais que o efeito mínimo que paga o
   custo" (`e_min`). A segunda é mais rigorosa e exige mais amostra.
4. **A qualidade da resposta final:** quem faz o cego pareado (quais especialistas, quantos casos por agente)?
5. **O papel do RespostaBacen:** verificação de dano (como proposto) ou fora da fase 1?
6. **A família de inputs:** o que define uma família em cada agente (o tipo de processo, o conjunto de campos)? Sai da
   leitura do código.

## 15. O que este documento reaproveita, e o que muda no plano geral

- **Reaproveitado sem mudança:** as medidas (§8 do plano geral), a estatística (§12), K e N (§9.3), os três níveis de
  replay (§7.1), a região `<memory>` (§6), o catálogo (`nao_vale_em`, `vale_junto_com`), os adendos por unidade.
- **O que a fase 1 muda no plano geral:** os agentes-espelho (a trilha 1) deixam de ser o caminho principal e passam a
  **ensaio e reserva** (construir o executor, o registro, a análise e o injetor, e servir quando um agente real não puder
  rodar); a trilha 2 (agentes reais) passa a ser **a fase 1**. Os experimentos de entrega, origem e conteúdo viram a
  fase 2, e só rodam para os pares em que a fase 1 mostrar que a memória mitiga.
