> **Sub-atividade:** 1.6 / 1.7 (alimenta 2.4 e 3.6) · **Tipo:** Receita passo a passo, com racionais · **Status:** desenho aprovado bloco a bloco em 13/11/2026 (os oito blocos e o 1-B; estado no §14); **revisto na auditoria de 13/11/2026** (§14, "Revisão de 13/11"): porta zero antes do injetor, replay reposicionado como triagem, baseline histórico removido, sete desfechos; falta ler Berger e Hsu e fazer o pré-registro depois do piloto · **Data:** 12/11/2026

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

**O que a fase 1 é, e o que ela não é.** Ela faz duas coisas: (a) **calibra o instrumento experimental** que a fase 2
inteira vai reutilizar — a taxa de hoje, o classificador reimplementado, o injetor, o `ρ`, o custo real por execução e as
aprovações de ambiente; e (b) responde à pergunta-gate: *a memória revisada mitiga o erro que descreve, a um custo que
compensa?* O que ela **não** decide é a tese do mecanismo — gate de promoção, esquecimento auditável, destino memória ×
harness —, que mora na fase 2 e no que este plano deliberadamente não testa. Um desfecho legítimo da fase 1 é "nada
testável hoje" (§6, porta zero).

## 1. A pergunta e a medida

> **Aprovado pelo Rafael em 13/11/2026 (bloco 1 do desenho).**

**A pergunta.** A memória que já temos mitiga o erro que ela descreve, quando injetada num agente real? E a que custo?

**A unidade de observação** é uma **execução**: o agente recebe um input e trabalha até a resposta final.

**Medida principal de eficácia: sim ou não por execução.** O erro-alvo aconteceu pelo menos uma vez nesta execução? Quem
responde é o classificador determinístico da taxonomia, a mesma regra da mineração, sem LLM. Ele é reimplementado sobre os
registros novos e conferido por uma segunda implementação.

- A **taxa de erro** de um braço é a fração de execuções com "sim".
- A **eficácia** é a **redução relativa**: `1 − (taxa com memória ÷ taxa sem memória)`. Exemplo: 35% e 17,5% dão 50%. A
  diferença absoluta (17,5 pontos) é reportada ao lado.
- Os **mesmos inputs** rodam nos dois braços (comparação pareada).

**Por que contar execuções e não passos com erro.** A execução é a unidade independente. Os passos da mesma execução
compartilham input e contexto, e o agente costuma repetir o mesmo erro, então contá-los como observações separadas faz o `p`
sair pequeno demais. O denominador também mudaria com a memória (uma execução mais curta teria menos passos). O que se perde é
a gravidade (uma execução com cinco erros conta igual a uma com um), mas nos erros do sandbox a média é de 1,0 a 1,4 erro por
execução que teve o erro (JoogleAnalytics 1,43; ContestacaoCivel 1,02; RoteadorCivel 1,00).

**Segunda medida: o custo.** Os **tokens totais** (entrada e saída) e a **duração em segundos** de cada execução.

- **Custo líquido** = tokens médios com memória − tokens médios sem memória. Negativo quer dizer que a memória economiza.
- O **placebo** também adiciona tokens, do mesmo tamanho; a diferença entre memória e placebo isola a economia dos passos
  poupados.
- A distribuição tem cauda longa (execuções com erro são mais longas): reporto a média, a mediana e o p90, com intervalo por
  bootstrap.
- O tempo é **reportado**, não é condição de sucesso. O dinheiro é tokens × o preço do gateway.

**Medidas secundárias, só descritivas (fora do veredito):** erros por execução e passos até a resposta final.

**Os sete resultados possíveis, e todos são resposta:**

| Resultado | Leitura | Consequência |
|---|---|---|
| **mitiga e compensa** | o erro cai e a economia paga o custo de injetar | a memória vai para a fase 2 |
| **mitiga, compensação incerta** | a redução é real e a estimativa passa do `e_min`, mas o intervalo da eficácia inclui valores abaixo dele (§9) | vai para a fase 2 com a ressalva declarada; a versão rigorosa da régua decide se a amostra fecha |
| **mitiga, mas não compensa** | o erro cai, mas o erro é raro demais, ou a memória cara demais | fica monitorada até a incidência crescer |
| **não mitiga** | o erro fica igual, **e o intervalo da redução exclui o `e_min`** (senão é "inconclusivo", §9) | volta ao degrau 3: a causa não era a suposta |
| **piora** | o erro sobe, ou aparece outro | não injetar; investigar o texto |
| **não testável hoje** | o erro não aparece mais no agente de hoje, então não há o que comparar | fica monitorada; **a memória não foi julgada** |
| **inconclusivo** | o intervalo da redução ainda inclui efeitos acima do `e_min`: a amostra não bastou para afirmar que não mitiga (§9) | repetir o par com mais inputs |

**Como estas medidas se ligam ao critério (§9, bloco 7).** A eficácia medida é comparada com o efeito mínimo que paga o
custo, `e_min = c ÷ (π · s)`: cerca de 6% no JoogleAnalytics e 33% no ContestacaoCivel, com o custo do passo com erro medido
(§4.6, Tabela 3 do [relatório da volumetria](relatorio-volumetria-fase-1.md)). O custo medido é comparado com a previsão da
compensação. Onde o erro é raro e o passo é barato, nenhuma eficácia paga: no RoteadorCivel a memória precisaria evitar 360%
dos erros.

**Limite conhecido.** A regra que define o erro é a mesma que o mede. Se a memória mudar *como* o erro aparece, a medida pode
errar. O §1.1 diz como isso se detecta.

### 1.1 A confiabilidade da medida

> **Aprovado pelo Rafael em 13/11/2026 (bloco 1-B do desenho).**

**O problema: o número pode estar errado de quatro jeitos.** O experimento conta, em cada braço, as execuções em que o
classificador diz "sim". Se o classificador erra, a contagem erra:

| # | O que acontece | Efeito no número |
|---|---|---|
| a | a regra **não casa** um erro que existe (um erro da mesma unidade com outro padrão) | a contagem **subestima** |
| b | a regra **casa** algo que não é o erro-alvo | a contagem **superestima** |
| c | a memória **muda a forma** do erro, e ele passa a aparecer num padrão que a regra não reconhece | a **queda é falsa**: o erro migrou |
| d | a execução **falha antes** de chegar ao ponto em que o erro seria possível | o erro não podia acontecer, e a taxa por execução mistura isso com "a memória funcionou" |

**O que o problema estraga e o que não estraga.** Se a regra erra **do mesmo jeito nos dois braços**, o número absoluto fica
errado, mas a **redução relativa continua certa**. Exemplo: os valores verdadeiros são 20 e 10 erros em 1.000 execuções; se a
regra só enxerga 60% dos erros nos dois braços, aparece 12 e 6, e a redução é 50% nos dois casos. O perigo é a falha que
**difere entre os braços**, o caso (c). Por isso a proteção principal não é refinar a regra, e sim **detectar o deslocamento**.

**As proteções, e por que cada uma.**

1. **Medir o próprio classificador.** Uma amostra de execuções é lida **sem saber o braço**, e o rótulo do programa é
   comparado com o do leitor. A **sensibilidade** (dos erros que existem, quantos ele acha) e a **precisão** (dos que ele
   marcou, quantos eram erro) saem com intervalo de confiança. Dois leitores independentes, com a concordância medida
   (kappa), a mesma lógica dos degraus de revisão. *Proposta de tamanho, a fixar no piloto:* 30 execuções com o rótulo "sim"
   e 30 com "não", por braço. Sem isso não se sabe quanto confiar no número absoluto.
2. **O piloto é o momento de corrigir a regra, e só ele.** No piloto se leem todos os erros marcados e uma amostra dos
   limpos, para achar o que a regra perdeu. Depois o classificador é **congelado por hash**, antes do confirmatório. Ajustar a
   regra depois de ver o resultado seria escolher a medida para dar o resultado (a razão de existir o pré-registro; Nosek et
   al., 2018).
3. **Contar o resíduo da unidade nos dois braços.** Além do padrão-alvo, contam-se os erros da mesma unidade que a regra
   **não** reconhece (a unidade de sandbox inteira, mais ampla que o padrão) e a taxa de **qualquer outro erro**. Se a
   memória empurra o erro para o resíduo, ele **cresce** no braço com memória e o resultado é sinalizado como "deslocamento",
   não como mitigação. É a única forma de ver o caso (c).
4. **Análise de sensibilidade.** O resultado é refeito com uma regra **estrita** e com uma **ampla**. Se as conclusões
   coincidem, a medida é robusta; se não, o resultado é reportado como não robusto.
5. **Números absolutos sempre com intervalo.** O "20 contra 10" nunca aparece sozinho. O veredito se apoia na comparação
   pareada, que usa os inputs em que o resultado **difere** entre os braços.
6. **Convergência qualitativa com o replay de passo (§6, porta zero).** Se a triagem de passo e a execução inteira
   apontarem para lados opostos, é sinal para investigar antes do confirmatório — sem pretensão de prova.
7. **Ler uma execução inteira de cada braço** (§10, passo 14): pega o que nenhuma regra prevê.

**Dois cuidados específicos.**

- **A memória pode fazer o agente evitar a situação** (escrever o código de outro jeito, sem `json`) **e a resposta piorar**:
  sem erro, mas com qualidade pior. Isso é tratado como guarda de dano (bloco 6).
- **O erro só é possível se o agente chega ao passo que o pede.** A taxa **por execução** é a principal (é a do bloco 1 e a
  que o custo acompanha). A taxa **por oportunidade** (execuções que chegaram a um passo que usa o objeto da lição) é
  reportada como conferência. Se a memória faz o agente **falhar antes**, por outro motivo, isso aparece como piora, não
  como mitigação.

**O que isso não resolve.** Um padrão de erro que ninguém previu e que nenhuma amostra lida mostrou; e o julgamento dos
leitores (se os dois concordam mas estão errados do mesmo jeito, o kappa não vê). **Quem são os leitores** é questão técnica:
os agentes de leitura do kit de mineração, ou o Rafael, e quantos casos.

## 2. Os pares: o que se testa, e por que esses

> **Aprovado pelo Rafael em 13/11/2026 (bloco 2 do desenho).**

### 2.1 O que é um par, e por que o teste é por par

Uma memória não "funciona em geral": ela mira um erro de um agente específico, e o efeito depende da frequência desse erro,
do custo do passo e do modelo. Por isso a unidade de teste é uma **comparação-alvo**: *um agente, um erro-alvo e a memória
injetada*. Cada comparação tem a sua própria taxa de erro, o seu próprio tamanho de amostra e o seu próprio veredito.

### 2.2 Como se escolhem os candidatos: três critérios

1. **A memória existe e foi revisada** (degrau 3 do catálogo). Testar uma lição que ninguém conferiu misturaria duas
   perguntas: "a memória mitiga?" e "a lição está certa?".
2. **A memória mira um erro daquele agente.** Uma memória injetada em quem não tem o erro só mede custo e dano.
3. **O erro é frequente e caro o bastante** para o teste ser viável. Sem isso, o experimento gasta tokens sem poder de
   enxergar efeito.

### 2.3 Os candidatos

| # | Agente | Memória injetada | Erro-alvo | Incidência histórica, jul–ago |
|---|---|---|---|---:|
| 1 | **JoogleAnalytics** | o par: memória dos imports + memória do `pandas`, **juntas** | `pandas` | 35,0% (28,4 a 42,1) |
| 2 | **JoogleAnalytics** | o mesmo par | imports (`json`) | 22,4% (17,0 a 29,0) |
| 3 | **ContestacaoCivel** | memória das funções proibidas | funções proibidas | 1,87% (1,66 a 2,12) |

No JoogleAnalytics, a memória do `pandas` só vale junto com a dos imports (campo `vale_junto_com` do catálogo), então se
injeta o par. As comparações 1 e 2 vêm das **mesmas execuções**; o que muda é qual erro se conta. Os números históricos
servem só para **escolher onde olhar**: são da base 3, que termina em agosto, e não são o baseline do experimento.

### 2.4 O baseline é medido no início, não herdado do histórico

**O problema.** O erro pode ter mudado desde agosto: o JoogleAnalytics caiu de 49% para 13% (`pandas`) e de 35% para 1,4%
(`json`) de julho para agosto, e isso pode ser troca de modelo ou de prompt. O experimento precisa da taxa do agente **que vai
ser testado**.

**A solução.** O baseline é o próprio **piloto**: rodar o agente **como está hoje**, sem memória, sobre inputs reais, com um
`n` fixo decidido com o orçamento, e medir a taxa com intervalo de Wilson. É essa taxa que decide a entrada do par, o `n`
necessário do confirmatório e o efeito mínimo `e_min` (recalculado com a taxa de hoje). Para só confirmar que o erro existe,
bastam poucas execuções (com 95% de confiança, 7 para o `pandas`, 12 para o `json` e 159 para as funções proibidas, pelas
taxas históricas).

**O que ficou de fora — duas peças, e por quê.**

1. **A versão de jul–ago do agente** (reconstituir modelo, prompt e código da época). Não decide nenhuma etapa desta fase —
   a memória é injetada no agente de hoje, e a entrada de cada par se decide com a taxa de hoje, medida acima. A pergunta
   diagnóstica que ela responderia ("o histórico se reproduz? a queda de agosto foi a troca de versão?") é da fase 2 e foi
   registrada em [`discussion/open-questions.md`](../discussion/open-questions.md).
2. **"Rodar até sair o erro".** Parar quando o erro aparecer `k` vezes enviesa o estimador e pede a correção da amostragem
   binomial inversa, que este plano não adota. Usa-se `n` fixo, decidido antes, e o intervalo de Wilson — a mesma medida, sem
   regra de parada adaptativa.

**Dois tipos de baseline.** *Por sorteio* (JoogleAnalytics): a taxa de erro de execuções sorteadas da produção. *Por conjunto
gatilho* (ContestacaoCivel): o erro é raro (1,9%), então se parte de inputs que já erraram e se mede a **taxa de reprodução**.

### 2.5 O que fica fora do confirmatório, e por quê

**O que é o confirmatório.** É a parte do experimento cuja hipótese, tamanho e critério são **fixados antes dos dados** (o
pré-registro) e cujo resultado vale como veredito. O que fica fora pode rodar como **exploratório**: procura padrões, não dá
veredito.

| Agente | Por que fora |
|---|---|
| **CalculoTrabalhista** | **Duas razões.** Custo: cada execução gasta cerca de meio milhão de tokens, e os três braços custariam de 135 a 200 milhões. Escassez: só 41 execuções tiveram o erro, e cada input seria repetido 2 ou 3 vezes, o que enfraquece o resultado. A memória dele **se paga** (eficácia mínima de 20%); o problema é rodar o teste. |
| **RoteadorCivel** | **A conta não fecha.** O passo com erro custa 3,5 mil tokens, a memória custa 60 por execução e o erro aparece em 0,5% das execuções: para pagar, a memória precisaria evitar 360% dos erros. É o caso "mitiga, mas não compensa", que pode rodar barato como exploratório (2 a 4 milhões de tokens). |
| **RespostaBacen** | **Não há erro para reduzir** (0 de 76 execuções em jul–ago), então não dá para testar mitigação. Serve à **verificação de dano**: uma memória global injetada onde o erro é raro piora algo? |

### 2.6 O escopo do que se conclui

Cada resultado vale para **aquele agente, aquele modelo, aquela versão do prompt e aquela família de inputs**. Os dois alvos
rodam modelos diferentes (JoogleAnalytics em `gpt-4.1`, ContestacaoCivel em `gpt-5.2`, segundo as execuções cruzadas das
bases 1 e 2). Nada se conclui sobre outros agentes ou outros modelos.

### 2.7 Questões técnicas em aberto (do Rafael, ao executar)

Nenhuma muda o desenho; cada uma precisa de um jeito de contornar: (1) fixar a versão de hoje (o modelo pode mudar por trás
do mesmo nome no gateway); (2) recuperar o input de usuário das execuções históricas (possível, segundo o Rafael); (3) onde
roda e como (aprovações, gateway, orçamento, homologação, bancos locais, caminho das ferramentas); (4) o `n` e o teto de
orçamento do baseline; (5) memória própria da plataforma desligada ou isolada.

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
cinco pares corrigida por Holm (um teste por par, §11). **Depois da decisão de 13/11 (§14) a família tem três pares**
(JoogleAnalytics `pandas`, JoogleAnalytics imports e ContestacaoCivel funções proibidas), e o primeiro limite sobe de 1% para
1,7%: os `n` desta tabela ficam conservadores. As contas são de 12/11/2026 e usam a fórmula de duas proporções
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

### 4.3 Os inputs: com quê se roda

> **Aprovado pelo Rafael em 13/11/2026 (bloco 3 do desenho).**

**O que é um input, e por que tem de ser real.** Um **input** é a mensagem que chega ao agente, como na produção. Num agente
real o erro depende de como o input é: com tarefas inventadas, o erro pode nem aparecer, ou aparecer com outra frequência.
Por isso os inputs são **reais**, recuperados do banco de traces do ambiente, e **ficam dentro do ambiente** (são dados
jurídicos; só saem contagens).

**O problema: o erro precisa aparecer.** Para testar a memória, o erro precisa acontecer nas execuções sem memória. Se
aparece em 35% das execuções, basta sortear inputs. Se aparece em 1,9%, **sorteando** gastaríamos milhares de execuções
para vê-lo (cerca de 3.258 por braço, só para uma comparação; §4.2 e Tabela 4 do relatório da volumetria). Daí os dois
jeitos, um por agente:

| Jeito | Como se monta | Quando se usa | Agente |
|---|---|---|---|
| **Sorteio** | inputs sorteados da produção do papel, **sem olhar** se erraram | o erro é frequente | JoogleAnalytics |
| **Conjunto gatilho** | inputs cuja execução original **teve** o erro | o erro é raro | ContestacaoCivel |

Os dois levam também um **conjunto controle**: inputs sorteados do papel, sem olhar o erro, para medir o **custo de
injetar** a memória onde o erro não acontece, o **dano** e a **incidência de hoje**. (No gatilho, os identificadores das
execuções com o erro vêm da base 3; o input vem do banco de traces.)

**O risco do conjunto gatilho, e a defesa.** Escolher inputs **porque erraram** traz a **regressão à média**: parte deles
erraria de novo só por acaso (se erraram por azar, tendem a errar menos na próxima). Se comparássemos "a execução
original, que errou" com "a nova, com memória", a memória ganharia crédito pelo azar que passou (Barnett et al., 2005). A
defesa: o **braço sem memória é rodado de novo nos mesmos inputs**, e a comparação é entre os dois re-rodados (sem memória
contra com memória), **nunca entre "antes" e "depois"**. A pergunta do piloto (§6) é a **taxa de reprodução**: dado que o
input errou na produção, com que frequência ele erra de novo hoje, sem memória? É ela que vira a "taxa do erro sem
memória" desse par (tabela 4.1). Se for baixa, o par não é viável.

**Regras de higiene dos inputs.**

- **Os inputs do piloto ficam fora do confirmatório.** Usar os mesmos contaminaria o resultado.
- **Sem inputs quase iguais** em braços diferentes, para as repetições serem de fato independentes. A comparação agrupa por
  input (ou por família).
- **Os mesmos inputs rodam em todos os braços** (comparação pareada), e as duas listas ficam congeladas por **hash** antes
  do confirmatório.
- Cada resultado vale para a **família de inputs** que o conjunto representa (§2.6).

**Questões técnicas em aberto (do Rafael, ao executar).** (1) Recuperar o input das execuções históricas no banco de
traces. (2) O mundo mudou desde o input original: um input histórico pode depender de documentos ou dados que a ferramenta
devolvia naquela época e que hoje são diferentes; a saída é "gravar e repetir" as respostas das ferramentas (§3.3).
(3) Como detectar inputs quase duplicados. (4) O que define uma "família" de inputs em cada agente. (5) O tamanho do pool:
o JoogleAnalytics tem 584 execuções históricas na base 3 e o ContestacaoCivel tem 254 com o erro; o par é viável se o pool
tem inputs para fechar `N`.

### 4.4 Quantos inputs, e quantas repetições de cada (K e N)

**Por que repetir o mesmo input.** O agente é estocástico: o mesmo input erra num dia e acerta no outro. Então cada input é
repetido `K` vezes, e há `N` inputs. O número de execuções com o erro por braço é `N × K`, mas as repetições do mesmo input
se parecem, e o ganho de repetir depende de `ρ` (a parte da variação que é do input):

- `ρ` perto de **0**: o erro depende da **sorte da execução**, não do input. Repetir o mesmo input rende tanto quanto trocar
  de input.
- `ρ` perto de **1**: alguns inputs sempre erram e outros nunca. Repetir pouco ajuda, e são precisos muitos inputs
  diferentes.

A relação é `N = n · (1 + (K − 1)·ρ) ÷ K` (Miller, 2024; plano geral §9.3), com `n` o número de execuções por braço que a
estatística pede (bloco 7). Para `n = 116` (com 122, os números sobem cerca de 5%):

| K | N com ρ = 0 | N com ρ = 0,5 |
|---:|---:|---:|
| 1 | 116 | 116 |
| 3 | 39 | 78 |
| 5 | 24 | 70 |

**O caso dos agentes reais.** O Rafael disse que as tarefas desses agentes são geralmente fechadas, quase a mesma tarefa.
Isso sugere um `ρ` baixo, mas é **hipótese**, e o piloto mede. Se `ρ` for alto, a eficácia só vale para o tipo de input que
erra, e o resultado fica restrito a essa família (§13). Inputs quase iguais se comportam como grupos de perguntas
relacionadas (Miller, 2024, §2.2), e a análise agrupa por família (§11).

**`K` e `N` não se decidem agora.** O piloto mede `ρ`, e `K` e `N` saem dele (plano geral §9.3). O critério, segundo Miller,
é que a variação dentro do input, dividida por `K`, seja bem menor que a variação entre inputs.

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

### 4.6 A volumetria medida (base 3, 12/11/2026)

> O método, os intervalos de confiança e o racional de cada tabela estão no [relatório da volumetria](relatorio-volumetria-fase-1.md); o que falta medir, no §9 dele.

**De onde vem.** O script `execucao/volumetria_memorias.py`, rodado na máquina 2, sobre a mineração do sandbox (1.100 erros lidos) e as contagens
(71.894 linhas), com a rodada `observada_c2e5e8b31f297d21`. Nenhum aviso de papel sem correspondente. Só contagens saíram.
Transcrevi as linhas abaixo e conferi a transcrição: em todas, a incidência impressa bate com a divisão das duas
contagens. O arquivo de custo por papel não existe na rodada mais recente, então **os tokens do passo com erro não foram
medidos**; uso a mediana de tokens da execução do papel.

**Os pares, com os dois últimos meses da base (julho e agosto de 2026):**

| Agente · memória | Execuções com o erro (total) | Execuções do papel (total) | Incidência jul–ago | Para ver o erro 1 vez (95%) | Mediana de tokens · passos |
|---|---:|---:|---:|---:|---|
| **JoogleAnalytics · pandas** | 231 | 584 | 35,0% (64 de 183) | 7 execuções | 88 mil · 10 |
| **JoogleAnalytics · imports (`json`)** | 107 | 584 | 22,4% (41 de 183) | 12 | 88 mil · 10 |
| **ContestacaoCivel · funções proibidas** | 254 | 13.454 | 1,9% (251 de 13.405) | 159 | 35 mil · 2 |
| CalculoTrabalhista · imports | 41 | 990 | 2,9% (12 de 412) | 102 | **549 mil** · 12 |
| RoteadorCivel · imports | 241 | 45.271 | 0,5% (167 de 34.978) | 626 | 10 mil · 3 |
| RespostaBacen · funções proibidas | 5 | 3.044 | 0% (0 de 76) | — | 40 mil · 4 |

**Achado 1 — no JoogleAnalytics o erro despencou em agosto.**

| Mês de 2026 | mar | abr | mai | jun | jul | **ago** |
|---|---:|---:|---:|---:|---:|---:|
| pandas | 26% | 41% | 48% | 57% | 49% | **13%** (9 de 70) |
| imports (`json`) | 11% | 9% | 14% | 35% | 35% | **1,4%** (1 de 70) |

A queda de julho para agosto não é sorte (os intervalos de confiança não se tocam). **O porquê é hipótese:** agosto é o
mês da troca de modelo em outros papéis (relatório da base 2), e pode ter mudado o modelo ou o prompt deste papel; a base
2 pode responder, com o modelo de cada execução do JoogleAnalytics em agosto. **A consequência é fato:** a base termina em
agosto e hoje é novembro. O erro pode já ter sumido na versão atual do agente. A porta "o erro ainda existe hoje" do
piloto (§6) é a primeira coisa a medir, antes de qualquer outra.

No sentido contrário, no ContestacaoCivel o erro das funções proibidas **subiu** de julho para agosto (1,4% para 2,1%), e
no RoteadorCivel o dos imports caiu (0,7% para 0,2%).

**Achado 2 — a conta de compensação muda de papel para papel.** O passo perdido custa o que o passo que errou custou:
**medido em 13/11** (mediana de tokens, no [relatório da volumetria](relatorio-volumetria-fase-1.md), Tabela 3). A memória
custa o seu tamanho (hipótese, estimado: 20 tokens a dos imports, 35 o par, 80 a das funções proibidas) em cada passo.

| Agente · memória | Custo de injetar `c` | Economia por erro evitado `s` | Incidência de equilíbrio | Incidência jul–ago | Eficácia mínima para pagar |
|---|---:|---:|---:|---:|---:|
| JoogleAnalytics · par | 360 | 16 mil (8.065 × dois passos) | 2,2% | 35% (13% em agosto) | **6%** (17% com a taxa de agosto) |
| CalculoTrabalhista · imports | 245 | 42 mil | 0,6% | 2,9% | 20% |
| ContestacaoCivel · funções proibidas | 160 | 26 mil | 0,6% | 1,9% | **33%** |
| RoteadorCivel · imports | 60 | 3,5 mil | 1,7% | 0,5% | **não paga** (precisaria de 360%) |

Leitura: no JoogleAnalytics a memória paga com quase qualquer eficácia; no ContestacaoCivel ela precisa evitar um terço dos
erros para empatar (a cauda é longa: com o p90 do passo, 9%); no RoteadorCivel não paga, porque a execução é pequena
(3 passos) e o erro é raro. **O custo do passo agora é medido; seguem hipótese os passos perdidos e o tamanho da memória**,
e o experimento os mede.

**Achado 3 — quanto custa rodar cada par.** Confirmatório no conjunto gatilho, três braços (sem memória, com memória,
placebo), `n` de 82 a 122 execuções por braço (taxa de reprodução de 40%, redução de 50%):

| Agente | Execuções | Tokens (mediana) | Inputs com o erro disponíveis |
|---|---:|---:|---:|
| JoogleAnalytics | 246 a 366 | 22 a 32 milhões | 231 |
| ContestacaoCivel | 246 a 366 | 9 a 13 milhões | 254 |
| RoteadorCivel | 246 a 366 | 2 a 4 milhões | 241 |
| CalculoTrabalhista | 246 a 366 | **135 a 201 milhões** | 41 (cada input repetido 2 a 3 vezes) |

**O que eu recomendo, com esses números:**

1. **JoogleAnalytics (par imports + pandas) e ContestacaoCivel (funções proibidas) são os dois alvos da fase 1.** Há
   inputs suficientes, o custo cabe, e as duas contas de compensação são interessantes e diferentes.
2. **CalculoTrabalhista sai do confirmatório.** Só 41 inputs com o erro e cada execução custa meio milhão de tokens. Fica
   como exploratório pequeno, ou monitorado.
3. **RoteadorCivel entra só se você quiser o caso "mitiga, mas não compensa"**: é o mais barato de rodar e a conta prevê
   que a memória não paga. Não estava na sua lista de agentes.
4. **RespostaBacen** continua como verificação de dano, mas teve só 76 execuções em julho e agosto: confira se o papel
   ainda está ativo.
5. **No JoogleAnalytics, nem é preciso escolher inputs que erraram:** com 13% a 35% de incidência, uma amostra sorteada
   já mostra o erro (7 a 12 execuções para vê-lo uma vez). Isso elimina o risco de regressão à média nesse par.

**O que continua sem medida:** os tokens e a duração do passo com erro (o arquivo de custo não existe na rodada mais
recente); o modelo de cada execução; e a taxa de hoje, que só o piloto dá.

## 5. O que se mede além do erro

> **Aprovado pelo Rafael em 13/11/2026 (bloco 6 do desenho).**

O §1 definiu as **duas medidas principais**: o erro-alvo (sim ou não por execução) e o custo (tokens e segundos). Este bloco
define **tudo o que se mede além delas**, e para que serve. A pergunta é: **como saber que a memória não estragou outra
coisa?** Uma memória que zera o erro mas faz o agente entregar respostas piores, ou travar em outro lugar, é pior que
nenhuma. Tudo o que não for julgamento é calculado por script, sobre o registro da execução (base: §8 do plano geral).

**Grupo 1: o custo em detalhe.**

| O que | Definição | Por quê |
|---|---|---|
| **tokens por execução** | entrada e saída, execução inteira, **mediana, média e p90**, com intervalo por bootstrap | tokens têm cauda longa; a média mente (§1) |
| **tempo por execução** | duração decomposta em modelo, ferramenta e interpretador | a ferramenta real tem latência; reportado, **não é condição** |
| **passos e tamanho da cascata** | número de passos e de erros seguidos | é onde está o ganho por erro evitado |

**Grupo 2: o que pode ter piorado (guardas de dano).**

| O que | Definição | Por quê |
|---|---|---|
| **outros erros** | taxa de qualquer erro fora da unidade, com × sem memória | "mitigou sem criar outro"; também defende o caso (c) do §1.1 |
| **falhas de infraestrutura por braço** | rede, timeout e limite, contados por braço (§8.2) | se o texto maior causa mais timeout, isso é resultado |
| **qualidade da resposta final** | quatro níveis, abaixo | a memória não pode piorar o que o agente entrega |

**Grupo 3: o mecanismo (explica o resultado, não o decide).**

| O que | Definição | Por quê |
|---|---|---|
| **adesão à lição** | quando a memória estava lá e o erro era possível, o código fez o que ela diz? (por AST) | separa "o agente ignorou a memória" de "a memória não funciona". O MERIT chama a fração em que o agente não usa a memória certa de *Ignore Rate* e mediu cerca de 45% nos casos difíceis |
| **replay de passo** | triagem da porta zero (§6.1) | adiar um par antes de gastar o confirmatório; evidência qualitativa do mecanismo |

**Grupo 4: a distribuição (o que a média esconde).**

| O que | Definição | Por quê |
|---|---|---|
| **robustez entre inputs** | fração dos inputs em que a memória melhora, não muda ou piora | uma média boa pode esconder inputs que pioram (no SkillsBench, 16 de 84 tarefas pioraram com skills curadas; resumo da v1) |
| **estabilidade** (`pass^k`, Yao et al., 2024) | fração dos inputs em que todas as `K` repetições passam | métrica do Plano de Trabalho; **secundária, não confirmatória** (decisão 7 do §14) |

**A qualidade da resposta final é o ponto difícil.** Num agente real não há resposta certa conhecida. Quatro níveis, do mais
barato ao mais caro, e **nenhum usa um LLM como juiz**, porque um juiz sem calibração é o risco que o projeto já registrou (o
melhor juiz do TRAIL alcança 11% de acerto conjunto):

1. **Estrutural:** a execução terminou com resposta final, no formato pedido, sem falha silenciosa. Por script.
2. **Presença (determinístico):** os números, datas e identificadores da resposta final aparecem nas observações da mesma
   execução (a medida "groundedness-as-presence" do roadmap da base 1). Por script.
3. **Pareado e cego, em amostra:** especialistas do domínio comparam, **sem saber qual é qual**, as respostas dos dois braços
   para o mesmo input. Amostra pequena por agente (proposta: cerca de 20 pares). **Exploratório, não decide** (decisão 4 do
   §14): uma medida difícil de padronizar não deve decidir o veredito.
4. **Equivalência com a resposta original da produção**, onde existir. Só referência: a execução original pode estar errada.

**O que decide e o que só sinaliza.** Os níveis 1 e 2, por script, entram no veredito. O nível 3 (cego) **sinaliza e dispara
investigação**; ele só pode virar desfecho ("piora") se a regra de decisão — a fração de pares com piora e o critério de
concordância dos especialistas — estiver **fixada no pré-registro, antes dos dados**. Sem regra pré-fixada, uma medida
exploratória não muda o veredito: "se o cego piorar, é piora", decidido depois de olhar o resultado, seria escolher o
critério para dar o desfecho — exatamente o que o pré-registro existe para impedir (§6.3).

**O RespostaBacen como verificação de dano.** Quase não tem o erro (0 de 76), então **não testa mitigação**. Roda a memória
das funções proibidas **só para ver que não piora** (outros erros, custo, qualidade), em outro modelo (o4-mini), o que serve
de checagem de generalidade. Fica **fora do Holm**.

**Como se reporta.** Para cada par, uma tabela única: taxa do erro sem e com memória (Wilson), redução relativa e absoluta
com intervalo, número a tratar (`1 ÷ redução absoluta`), tokens e tempo (mediana, p90, bootstrap), passos, outros erros,
qualidade. **Médias de tokens e tempo nunca aparecem sozinhas.** Os termos (mediana, p90, bootstrap, pareado) estão em
[`conceitos-do-experimento.md`](conceitos-do-experimento.md) §6.

**Compensação.** A compensação em tokens e segundos (`c`, `s`, `π`, §8.2 e §8.3 do plano geral) continua, com o custo do passo
com erro medido (§4.6).

**Questões técnicas em aberto (do Rafael, ao executar):** (1) quem são os especialistas do cego (proposta: 1 a 2 por agente,
cerca de 20 pares cada); (2) como implementar a adesão à lição por AST em cada agente; (3) como separar o tempo em modelo,
ferramenta e interpretador, se o trace não o tem (a base 3 tem só os passos com erro).

## 6. O piloto e o pré-registro

> **Aprovado pelo Rafael em 13/11/2026 (bloco 8 do desenho).**

A sequência é: **porta zero (a triagem mínima, sem injetor) → piloto → portas → decidir `K` e `N` → pré-registro → confirmatório → análise.**

### 6.1 A porta zero: a triagem que decide se o resto existe

Roda **antes de o injetor e a infraestrutura serem construídos** (receita, passo 8 do §10), com o mínimo indispensável: o
agente **na versão atual, sem memória**, sobre os conjuntos gatilho e controle já montados, lido pelo classificador da
mineração reimplementado — que o confirmatório precisa de qualquer forma. Responde, na ordem de custo crescente:

1. **O erro existe hoje?** É a primeira porta da tabela abaixo, e bastam poucas execuções (§2.4).
2. **A taxa de reprodução `p`, em ordem de grandeza**, no conjunto gatilho: afina a linha da tabela 4.1 antes de o piloto
   completo medir o resto.
3. **O replay de passo como triagem.** Em passos em que o erro aconteceu, repete-se **só aquele passo**, com a mesma
   entrada, `K` vezes sem e com memória — uma chamada de LLM por repetição, muito menos que uma execução inteira; no erro do
   sandbox, o erro se lê no código, sem rodar ferramenta. O conceito e os limites estão em
   [`conceitos-do-experimento.md`](conceitos-do-experimento.md) §4. O replay **decide com regra declarada no pré-registro**:
   *sem sinal no par (o erro volta na mesma proporção com e sem memória) → o par é adiado antes do confirmatório.* Ele não
   decide o veredito ("mitiga" ou não) — decide só se vale rodar o instrumento completo, que é onde custo, dano e cascata
   se medem.

Se **nenhum** par passa na porta zero, a fase 1 encerra aqui com "nada testável hoje" — e o custo total foi o da porta,
não o do experimento.

### 6.2 O piloto: mede o terreno, não testa a memória

O piloto roda **só o braço sem memória**, na versão **atual** do agente, e responde seis perguntas (as duas primeiras já
vêm aferidas em ordem de grandeza pela porta zero; o piloto completo as refina com o tamanho planejado):

| O que se mede | Como | Decide |
|---|---|---|
| **o erro ainda existe hoje?** | o conjunto gatilho, sem memória, na versão atual | se não existe, desfecho **"não testável hoje"** (§1) |
| **a taxa de reprodução `p`** | fração das execuções do gatilho que erram de novo | a linha da tabela 4.1 |
| **a incidência de hoje `π`** | fração das execuções do controle com o erro | o `e_min` (§9) e a porta do JoogleAnalytics |
| **o `ρ`** | análise de variância entre e dentro dos inputs (plano geral, §9.3) | `K` e `N` (§4.4) |
| **tokens e tempo por execução**, por papel | mediana, média e p90 | a conta de custo e o orçamento |
| **a taxa de falhas de infraestrutura** | execuções que falham por motivo que não é do agente | quanto repetir fora da nota |

**Tamanho, por par:** 20 inputs do gatilho × 5 repetições mais 20 do controle × 3 repetições = **160 execuções** (480 nos
três pares), a ordem do plano geral, que estima o `ρ` com erro de cerca de ±0,10. Com cerca de 90 mil tokens por execução do
JoogleAnalytics (42 mi ÷ 468), o piloto dele custa cerca de 14 mi de tokens. **O baseline** (§2.4) se mede aqui: a versão
de hoje, com `n` fixo e o intervalo de Wilson.

**Além de medir, o piloto fecha cinco coisas:** (1) o **classificador é corrigido e congelado por hash** (§1.1), só aqui; (2)
o **texto do placebo** (proposta do Claude, aprovada pelo Rafael; §8.1); (3) o **limite da "fração relevante de inputs que
pioram"** (condição 3 do §9), olhando a variação natural entre inputs; (4) o **tamanho da amostra de leitura às cegas** do
classificador (30 + 30 por braço, a fixar); (5) o **`e_min` recalculado** com o `π` medido.

**Portas de decisão** (escritas antes dos dados):

| Porta | Regra | Se falhar |
|---|---|---|
| **o erro ainda existe** *(porta zero)* | o limite inferior do intervalo de `p` é maior que zero | **"não testável hoje"**: a memória fica monitorada e **não foi julgada** |
| **a triagem de passo tem sinal** *(porta zero)* | no replay, a memória reduz a volta do erro (regra fixada no pré-registro, §6.1) | o par é **adiado** antes de gastar o confirmatório |
| **viável** | inputs do gatilho × `K` × `p` ≥ `n` da tabela 4.1 | par monitorado ou exploratório |
| **seguro** | todas as ferramentas classificadas e a saída do §3.3 definida | **não roda** |
| **orçamento** | execuções × tokens médios ≤ o teto fixado com a plataforma | reduz pares ou `K` |
| **entrada do JoogleAnalytics** | taxa de hoje ≥ 25% (§9) | sai do confirmatório |

Se **nenhum** par passar, o resultado da fase 1 é "nada testável hoje". É um resultado legítimo, **não** uma falha do
experimento.

### 6.3 O pré-registro

É um documento escrito **depois do piloto e antes do confirmatório**, para impedir que a medida, a regra ou o critério sejam
ajustados depois de ver o resultado (Nosek et al., 2018).

**O que ele congela, por hash:** os pares que passaram nas portas (e os que saíram, com o motivo); as listas de inputs
(gatilho e controle), que **ficam no ambiente** (só o hash sai); os textos das memórias e dos placebos; o classificador (regra
estrita e ampla); `K`, `N`, o tamanho da amostra e a redução de referência (50%); o `e_min` recalculado e o orçamento; **o
plano de análise inteiro** (pareamento e bootstrap por input, as quatro condições do §9 com o limite de dano, a ordem do
Holm e a forma da correção, A' ou B); e a **regra de parada**: o tamanho é fixo, **não se olha o resultado antes de todas as
execuções terminarem** (olhar no meio e parar quando "dá certo" infla os falsos positivos). **Fora do hash:** o conteúdo
jurídico dos inputs, que não sai do ambiente.

**Depois do congelamento.** Qualquer mudança vira um **desvio declarado**, datado, com o motivo, e aparece no relatório;
nada é reescrito. Tudo o que não estiver no pré-registro (replay, cego, autogerada, adesão) é **exploratório** e não entra no
veredito. O pré-registro precisa do **ok do Rafael** e, para rodar, das aprovações do §3 (onde roda, gateway, orçamento,
homologação), que são do Rafael e do tutor.

**Questões técnicas em aberto (do Rafael, ao executar):** (1) quando a porta zero e o piloto podem rodar (depende da leitura do código, §3.1,
e das aprovações, §3.2); (2) onde o pré-registro é guardado e como o hash sai do ambiente; (3) o `n` e o orçamento do
baseline e do piloto; (4) os comandos literais para o ambiente saem **depois** que os scripts
dos passos 4, 6 e 10 da receita (§10) existirem e forem testados na base 1.

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

### 8.1 Os braços: o que se compara

> **Aprovado pelo Rafael em 13/11/2026 (bloco 4 do desenho).**

Um **braço** é uma maneira de rodar o mesmo agente, com os mesmos inputs, o mesmo modelo e a mesma versão do prompt. **Só
muda o que entra no prompt.** Cada braço responde a uma pergunta diferente; sem eles, "o erro caiu" não diz o que o fez cair.

**Os três braços do veredito** (nos dois alvos):

| Braço | O que o agente recebe | Pergunta que responde |
|---|---|---|
| **sem memória** | o agente como ele é hoje | qual é a taxa do erro sem a memória? É a régua de comparação |
| **com memória** | o agente mais a região `<memory>` com o texto aprovado no degrau 3, **sem reescrita** | a memória reduz o erro? É o tratamento |
| **placebo** | a mesma região `<memory>`, o mesmo invólucro, com texto verdadeiro, do mesmo tamanho e **sem relação com a tarefa** | a redução vem do conteúdo da memória, ou só de ter mais texto no prompt? |

A região `<memory>` é **idêntica em formato** nos dois braços que a têm (o mesmo rótulo, a mesma frase de abertura, o mesmo
formato de itens): qualquer diferença entre eles é de conteúdo, não de forma. A região entra pelo parâmetro de instruções
extras do agente (§7), sem alterar o prompt do repositório, e o injetor registra, em cada execução, quais memórias entraram e
qual a versão do texto.

**Por que o placebo é indispensável.** Acrescentar texto ao prompt já muda o comportamento do modelo, e o erro pode cair por
isso, sem que a lição tenha papel nenhum. Sem o placebo, "a memória mitiga" não se separa de "mexer no prompt mitiga". O
custo é cerca de metade a mais de execuções. **Decidido em 13/11: roda nos dois alvos** (§14).

**Como o placebo é escrito.** Um texto por memória, **do mesmo tamanho (±10%)** do texto correspondente (o custo em tokens e
o efeito de "mais texto" dependem do tamanho); verdadeiro, mas sem relação com a tarefa do agente e sem lição de código;
**congelado por hash** no pré-registro, junto com os textos das memórias.

**O que entra em cada alvo.** No JoogleAnalytics, **as duas memórias juntas** (imports e `pandas`), como uma unidade (§2); o
placebo tem o tamanho do par. No ContestacaoCivel, a memória das funções proibidas; o placebo tem o tamanho dela.

**Os braços fora do veredito.**

| Braço | O que é | Por que fica fora |
|---|---|---|
| **autogerada** | a mesma região, com lições que o **próprio agente escreveu**, sem taxonomia | exploratória, **só no JoogleAnalytics** (erro frequente, braço barato); não entra no Holm, para o veredito ficar limpo (§14) |
| **por ferramenta** (`recall_memory`) | o agente decide se consulta | outra pergunta (recuperação), é do experimento seguinte |
| **no erro** (middleware) | a memória só entra depois do erro | outra pergunta (reincidência), é do experimento seguinte |

A fase 1 pergunta só **"a memória entregue ao agente reduz o erro?"**; como a memória chega é assunto das fases seguintes.

**Qual comparação decide, e qual só descreve.** "Este par mitiga" exige **duas condições ao mesmo tempo**: com memória melhor
que sem memória **e** melhor que o placebo. Quando a afirmação exige as duas, o teste é de **interseção-união**: o `p` do par é
o **maior** dos dois, sem correção entre as partes, e o Holm corrige entre os três pares (§9; a escolha entre as formas A' e
B é do bloco 7). A comparação **placebo contra sem memória** é só descritiva: se o placebo já reduzir o erro, o ganho da
memória sobre ele passa a ser a medida que importa.

**Fecham no piloto:** o texto do placebo de cada alvo (proposta minha, **aprovada pelo Rafael antes do congelamento por hash**)
e o tamanho real do texto da memória, que fixa o do placebo.

### 8.2 A execução: como se roda para a comparação ser justa

> **Aprovado pelo Rafael em 13/11/2026 (bloco 5 do desenho).**

Os blocos anteriores dizem **o que** se compara (pares, inputs, braços). Este diz **como** se roda, para que a diferença
entre os braços seja da memória e não de outra coisa.

**O que fica igual em todos os braços.**

- **O mesmo modelo, a mesma versão do agente e os mesmos parâmetros**; modelo e versão ficam registrados em cada execução. O
  erro já mudou com a troca de modelo em agosto/2026, então um modelo diferente entre braços invalidaria a comparação.
- **Sessão nova a cada execução**, com a memória própria da plataforma (checkpoints, memória nativa do Hermes) **desligada ou
  isolada** (§3.1). Se o agente lembrasse de uma execução anterior, as repetições deixariam de ser independentes.
- **O mesmo input** em todos os braços (pareado, §4.3).

**O que se sorteia.** Os braços de um mesmo input rodam juntos, em **ordem sorteada**. O provedor do modelo muda de
comportamento ao longo do dia e da semana; se um braço rodasse sempre antes, a deriva cairia só nele.

**Ferramentas com efeito colateral.** Rodar o agente real de novo pode expedir ofício, gravar no banco ou enviar mensagem. A
regra (decisão 6 do §14): **se houver homologação, roda-se ao vivo nela; se não, as ferramentas que escrevem usam gravar e
repetir (as respostas vêm do trace original) e só as de leitura rodam ao vivo** (§3.3). Limite: o gravar e repetir falha
quando o agente chama a ferramenta de outro jeito, e é o que a memória pode provocar. Por isso precisa de uma **política para
"não achei a resposta gravada"**, e **se registra quantas vezes isso ocorreu, por braço**: se ocorrer mais num braço, a
comparação fica enviesada e isso se declara.

**Onde entra o replay.** O **replay de passo** virou instrumento de triagem da **porta zero** (§6.1): é barato (um passo é
uma chamada de LLM) e decide, com regra declarada no pré-registro, se o par segue para o confirmatório. O conceito, os
precedentes (DoVer, AgentDebug) e os limites estão em [`conceitos-do-experimento.md`](conceitos-do-experimento.md) §4. O
que decide o veredito é sempre a **execução ao vivo** — única que mede erro, custo e dano juntos — e rodar de novo o mesmo
input sem memória é a base do conjunto gatilho (§4.3). **Congelar também as respostas do LLM não serve**: a memória age
sobre o LLM, e a resposta dele já estaria fixa (`conceitos-do-experimento.md` §4).

**Falhas de infraestrutura** (rede, limite de requisições do gateway, timeout, ferramenta fora do ar) se **separam, se
classificam** (as 8 causas do Eval Engineering) e **se repetem fora da nota**. **Conta-se por braço**: se um braço falha mais,
isso pode ser efeito da memória (texto maior, mais tempo, mais timeout), e então se reporta como resultado. A execução que
falha antes da chance de errar não conta como "sem erro" (quarta forma do §1.1).

**O que é congelado antes do confirmatório** (pré-registro, §6.3): os pares, as listas de inputs (por hash), os textos
das memórias e dos placebos, `K`, `N`, as medidas e os critérios. Os inputs do piloto ficam **fora** do confirmatório.

**Questões técnicas em aberto (do Rafael, ao executar):** (1) há homologação para cada agente; (2) quais ferramentas de cada
agente escrevem e quais só leem; (3) a política para "não achei a resposta gravada"; (4) como desligar ou isolar a memória
própria da plataforma; (5) o `n` e o orçamento do baseline (§2.4); (6) como detectar a deriva do provedor,
para registrá-la.

## 9. Critério de sucesso

> **Aprovado pelo Rafael em 13/11/2026 (bloco 7 do desenho).**

Uma memória "**mitiga**" num agente se as quatro condições valerem:

1. **Eficácia.** A taxa do erro-alvo com a memória é menor que sem ela, com p < 0,05 depois do ajuste de Holm sobre os
   pares (a família tem três pares: os limites são 1,7%, 2,5% e 5%, do menor `p` ao maior), e o intervalo de 95% da redução relativa **não inclui zero**.
2. **Especificidade.** A memória é melhor que o placebo na mesma medida.
3. **Sem dano.** A estrutura da resposta final não piora; a presença não piora; a taxa de outros erros não sobe; o
   resultado do cego, **se a sua regra de decisão foi pré-registrada** (§5), não favorece o braço sem memória; e nenhuma
   fração relevante dos inputs piora (a robustez do §5, com limite fixado no pré-registro).
4. **Robustez.** O resultado vale nas duas metades dos inputs (primeira e segunda metade, ou duas famílias) e, se o
   piloto rodou em dois modelos, nos dois.

Ela "**compensa**" se, além disso, a **incidência de equilíbrio** `c ÷ (c + s)` ficar abaixo da incidência de hoje `π` do
agente, com o limite superior do intervalo ainda abaixo de `π`. A conta é em **tokens**, em **segundos** (reportada, não
condição, porque a velocidade do provedor da plataforma é outra) e em **dinheiro** (tokens × o preço do gateway).

**A régua de eficácia, decidida em 13/11:** além da condição 1 (redução real, com Holm), a redução **estimada** precisa ser
maior que o efeito mínimo que paga o custo, `e_min = c ÷ (π · s)`. Com o custo do passo medido (relatório da volumetria,
Tabela 3): cerca de 6% no JoogleAnalytics e 33% no ContestacaoCivel. O `e_min` é **recalculado no pré-registro** com a taxa de hoje
(`π`) medida no piloto. A versão mais rigorosa, que exige o **limite inferior** do intervalo acima do `e_min`, pede muito
mais amostra e **não foi adotada**; fica como opção se o piloto mostrar amostra sobrando.

**A faixa intermediária tem nome.** Se a redução é real (condições 1 e 2 passam) e a estimativa pontual passa do `e_min`,
mas o intervalo de 95% da eficácia **inclui valores abaixo dele**, o desfecho é **"mitiga, compensação incerta"** (o sétimo
do §1): o par vai para a fase 2 com a ressalva declarada — e, se a amostra permitir, a versão rigorosa da régua fecha a
questão. Sem o sétimo desfecho, essa faixa cairia ora em "mitiga e compensa", ora em "inconclusivo", conforme a vontade do
analista — e a régua deixaria de ser regra.

**Como a correção é feita (decidido em 13/11/2026, bloco 7).** "Mitiga" exige duas comparações por par (contra sem memória e
contra placebo), então o teste é de **interseção-união** (Berger, 1982): o `p` do par é o **maior** dos dois, sem correção
dentro do par, e o **Holm** corrige entre os **três** pares (limites 1,7%, 2,5% e 5%, do menor `p` ao maior, parando no
primeiro que falha; [`literature/holm-1979.md`](literature/holm-1979.md)). É a **opção A'** (a B, com as seis comparações
juntas no Holm, pede cerca de 180 por braço contra cerca de 160, e fica como reserva). **Condição:** os textos de Holm (1979) e
Berger (1982) não foram obtidos; o apoio é de fontes secundárias. **Antes do pré-registro**, o Rafael lê Berger e Hsu (1996,
acesso aberto, [página](https://projecteuclid.org/euclid.ss/1032280304)); se não sustentar a A', troca-se pela B.

**O efeito para o qual se dimensiona.** A amostra é calculada para detectar uma redução de **50%** (a das tabelas do §4),
maior que o `e_min` dos dois alvos (6% e 33%). Se a redução real for menor, o experimento não terá poder, e o resultado
volta como **inconclusivo**, não como "não mitiga".

**O sexto desfecho: inconclusivo.** Um teste que não rejeita **não prova** que a memória não funciona (pode ser amostra
pequena). Por isso **"não mitiga" só se declara quando o intervalo de confiança da redução exclui o `e_min`**. Se o
intervalo ainda inclui efeitos acima do `e_min`, o desfecho é **"inconclusivo: amostra insuficiente"**, e o par pode ser
repetido com mais inputs. Os desfechos do §1 passam a sete (o sétimo é o "mitiga, compensação incerta" da régua acima).

**Porta de entrada do JoogleAnalytics, por orçamento.** Com A' e redução de 50%, o sorteio custa por braço: 156 (taxa de hoje
35%), 194 (30%), 242 (25%), 317 (20%), 517 (13%), isto é, de cerca de 42 a 138 milhões de tokens nos três braços. **Entra se a
taxa de hoje for ≥ 25%** (cerca de 65 milhões de tokens); abaixo disso, sai do confirmatório e fica monitorado, a menos que o
Rafael aceite o orçamento maior. O limite final é fixado no pré-registro, com o orçamento que o Rafael aceitar gastar.

**Fora do Holm** (e do veredito): RespostaBacen, CalculoTrabalhista, RoteadorCivel, a autogerada e o cego. (O replay de
passo não é um braço: é a triagem da porta zero, §6.1.)

**Questões em aberto (do Rafael):** (1) ler Berger e Hsu (1996); (2) o limite da "fração relevante dos inputs que pioram"
(condição 3), a fixar no piloto, olhando a variação natural entre inputs; (3) o orçamento de execuções.

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
| 7 | **O classificador** do erro-alvo reimplementado sobre os registros novos, com segunda implementação (§1.1) — **sem injetor** | Claude | o código testado na base 1 | as duas implementações batem | 2 |
| 8 | **A porta zero** (§6.1): só sem memória, na versão atual, no gatilho e no controle; e o replay de passo no gatilho | Rafael | o erro existe hoje? a taxa de reprodução em ordem de grandeza; o sinal do replay | as portas zero aplicadas; **se nenhum par passa, a fase 1 encerra aqui** | 2 |
| 9 | **O injetor**: a região `<memory>`, o registro, os filtros do catálogo (§7) | Claude escreve e testa; Rafael integra no agente | o injetor testado | uma execução de cada braço lida inteira | 3 |
| 10 | **O piloto completo** (§6.2) | Rafael | incidência de hoje, `ρ`, tokens, tempo; classificador corrigido e congelado por hash | o restante das portas de decisão aplicadas | 2 |
| 11 | **Decidir `K` e `N`** por par (§4.4 e §9.3 do plano geral) e **pré-registrar** | Rafael e Claude | o pré-registro com hash | aprovação do Rafael | 1 |
| 12 | **O confirmatório** (§8) | Rafael | os registros crus + o manifesto | todas as execuções previstas existem | 3–5 |
| 13 | **Análise e auditoria independente** (§11) | Claude escreve; Rafael roda | tabelas e o veredito por par | as duas implementações batem | 3 |
| 14 | **Leitura de uma execução inteira por braço**, e do cego, se houver | Rafael | o relato | — | 1–2 |
| 15 | **Fechamento:** o degrau 4 no catálogo, o relatório, e o que passa para a fase 2 | Rafael e Claude | os documentos | gate do pesquisador | 2 |

Os passos 7–8 são **descartáveis e baratos**: usam só o agente como ele é e o classificador que o confirmatório vai
reusar. O injetor (9) e o resto da infraestrutura só existem **depois** que a porta zero mostra que há o que medir.

**Os comandos literais para o ambiente** (linhas completas, sem variáveis) saem **depois** que os scripts dos passos 4, 6
e 10 existirem e forem testados na base 1; até lá, este documento é o plano, não o roteiro de comandos.

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

## 14. Decisões do Rafael (13/11/2026)

### Revisão de 13/11/2026 (auditoria do desenho)

Depois da aprovação bloco a bloco, o desenho passou por uma auditoria de método experimental (13/11/2026, noite). Os
ajustes estão no texto onde valem; aqui fica o registro:

1. **A fase 1 reenquadrada (§0):** calibração do instrumento experimental + pergunta-gate. A tese do mecanismo (gate,
   esquecimento, destino memória × harness) se decide na fase 2 — a fase 1 não a prova nem no melhor cenário.
2. **Porta zero criada (§6.1, passo 8 da receita):** a triagem mínima — versão atual, sem memória, gatilho e controle,
   com o replay de passo — roda **antes** de o injetor e da infraestrutura serem construídos. Se nenhum par passa, a fase 1
   encerra ali, pelo custo da porta.
3. **Replay de passo reposicionado (§6.1, §8.2):** de braço exploratório solto para **instrumento de triagem da porta
   zero, com regra de decisão declarada no pré-registro** ("sem sinal → o par é adiado"). Instrumento exploratório não
   decide sem regra pré-fixada — o mesmo defeito corrigido no cego.
4. **Baseline B removido (§2.4):** reconstituir a versão de jul–ago não decide nenhuma etapa da fase 1 (a memória é
   injetada no agente de hoje, e a entrada se decide com a taxa de hoje). A pergunta diagnóstica foi para
   [`open-questions.md`](../discussion/open-questions.md), como assunto da fase 2.
5. **"Rodar até k erros" removido (§2.4):** o estimador da binomial inversa não estava conferido em fonte; o baseline usa
   `n` fixo e intervalo de Wilson.
6. **Cego sem poder de veredito improvisado (§5, §9 condição 3):** só decide se a regra (fração de pares com piora,
   concordância dos especialistas) estiver no pré-registro; sem ela, sinaliza e dispara investigação.
7. **Sétimo desfecho (§1, §9):** "mitiga, compensação incerta" — redução real e estimativa acima do `e_min`, com o
   intervalo incluindo eficácias abaixo dele.
8. **Simulação de poder versionada (abaixo, bloco 7):** o script entra no repositório antes do pré-registro; número sem
   script não entra no pré-registro.

Os blocos 1–8 permanecem aprovados; estes ajustes detalham, reordenam ou removem, sem mudar a pergunta, os pares-alvo,
os três braços do veredito nem a correção (A' + Holm).

### O estado da aprovação do desenho, bloco a bloco

As decisões da tabela seguinte foram tomadas em 13/11, mas sem o contexto completo. Por isso o desenho está sendo **reaprovado
um bloco por vez**, com o contexto; cada bloco aprovado entra no texto do plano.

| Bloco | O que decide | Estado |
|---|---|---|
| 1. A pergunta e a medida | o que se mede em cada execução (§1) | **aprovado em 13/11/2026** |
| 1-B. A confiabilidade da medida | como se sabe que o classificador é confiável (§1.1) | **aprovado em 13/11/2026** |
| 2. Os pares | em quais agentes e memórias se testa (§2) | **aprovado em 13/11/2026** |
| 3. Os inputs | de onde vêm (sorteio, gatilho, controle), `K` e `N` (§4.3 e 4.4) | **aprovado em 13/11/2026** |
| 4. Os braços | sem memória, com memória, placebo, autogerada (§8.1) | **aprovado em 13/11/2026** |
| 5. A execução | as regras para a comparação ser justa (§8.2) | **aprovado em 13/11/2026** |
| 6. O que se mede além do erro | dano, estabilidade, qualidade da resposta final (§5) | **aprovado em 13/11/2026** |
| 7. A decisão | `p`, Holm, interseção-união, efeito mínimo (§9) | **aprovado em 13/11/2026** (opção A', condicionada à leitura de Berger e Hsu) |
| 8. O piloto e o pré-registro | portas, o que se congela antes dos dados (§6) | **aprovado em 13/11/2026** |


**Decididas** (o porquê de cada uma está nas seções indicadas e no [relatório da volumetria](relatorio-volumetria-fase-1.md)):

| # | Decisão | O que foi decidido | Por quê (o achado) |
|---|---|---|---|
| 1 | **Alvos** | **JoogleAnalytics** (as memórias do `pandas` e dos imports, **por sorteio**) e **ContestacaoCivel** (funções proibidas, por **conjunto gatilho**). Ficam fora do confirmatório: CalculoTrabalhista, RoteadorCivel e RespostaBacen | JoogleAnalytics: erro em 35% e 22% das execuções, experimento barato, a memória paga com eficácia de 6%. ContestacaoCivel: erro raro (1,9%) mas de alto volume e passo caro (26 mil tokens); precisa de 33% de eficácia; o input é recuperável (resposta do Rafael). CalculoTrabalhista: meio milhão de tokens por execução e só 41 com o erro. RoteadorCivel: a memória não paga (360%). RespostaBacen: 0 de 76 |
| 2 | **Placebo** | roda **nos dois alvos** | sem ele, "mitiga" não se separa de "mexer no prompt"; os custos da Tabela 5 do relatório já incluem esse braço |
| 3 | **Régua de eficácia** | condição 1 (Holm, 5%) **e** redução estimada acima do `e_min` do par (§9); o `e_min` é recalculado com a taxa de hoje | liga a eficácia ao custo sem exigir a amostra da versão mais rigorosa |
| 4 | **Qualidade da resposta final (cego pareado)** | **verificação de dano, exploratória**, amostra pequena; não é condição de sucesso | evita que uma medida difícil de padronizar decida o veredito |
| 5 | **RespostaBacen** | **só verificação de dano**, para ver que a memória não piora | quase não tem erro (0 de 76), então não testa mitigação; roda em outro modelo, o que serve de checagem de generalidade |
| 6 | **Ferramentas com efeito colateral** | **regra:** se houver homologação, rodar ao vivo nela; se não, gravar e repetir as respostas das ferramentas que escrevem e rodar ao vivo só as de leitura | o replay precisa ser repetível sem tocar em sistema real |
| 7 | **Estabilidade** (`pass^k`) | medida **secundária**, não confirmatória | repetir o mesmo input várias vezes custa muito e o §9 já exige robustez entre metades |
| 8 | **Autogerada** | **quarto braço exploratório, só no JoogleAnalytics** (relatório, §10.1) | é onde o erro é frequente e o braço é barato; o veredito da fase 1 fica limpo |

### O contexto de cada decisão

**O experimento, em três linhas.** Um agente, de vez em quando, comete um erro específico (por exemplo, gerar um import que
o sandbox bloqueia). A memória é um texto curto que ensina o agente a evitá-lo. O experimento roda os mesmos inputs sem a
memória e com ela, e mede **se o erro diminui** e **se a memória gasta menos tokens do que economiza**.

1. **Alvos.** Cada execução gasta tokens, e só serve de teste se o erro puder acontecer nela. Há dois jeitos de montar os
   inputs: **sorteio** da produção (funciona quando o erro é frequente) e **conjunto gatilho**, com os inputs que já erraram
   (funciona quando o erro é raro, mas exige recuperar o input original). O JoogleAnalytics erra em 35% e 22% das execuções:
   sorteio, barato. O ContestacaoCivel erra em 1,9%: por sorteio seriam 3.258 execuções por braço, pelo gatilho cerca de 120
   (o input é recuperável, resposta do Rafael). O CalculoTrabalhista fica fora por **custo e escassez** (meio milhão de
   tokens por execução, 41 com o erro), não porque a memória não valha. O RoteadorCivel fica fora porque a memória custa mais
   do que economiza; o RespostaBacen, porque quase não tem o erro. Uma ressalva do gatilho: ele só vale se o mesmo input
   voltar a errar (a taxa de reprodução, uma hipótese de 40% que o piloto mede), e inputs escolhidos por terem errado
   tendem a melhorar sozinhos (regressão à média), por isso o braço sem memória é indispensável.
2. **Placebo.** Se o braço com memória melhorar, pode ser só porque o prompt mudou de tamanho. O placebo é um texto do
   mesmo tamanho, verdadeiro e sem relação com a tarefa: se a memória o vencer, o efeito é da lição. Custa cerca de metade a
   mais de execuções.
3. **Régua.** "O erro diminuiu" pode ser verdade e ainda assim dar prejuízo: a memória do ContestacaoCivel custa 160 tokens por
   execução e, para se pagar, precisa evitar 33% dos erros; se evitasse 5%, com certeza estatística, a redução seria real e a
   memória seria um prejuízo. Por isso a régua exige as duas coisas: redução real (Holm) **e** estimativa acima do `e_min`.
   A versão mais rigorosa (limite inferior do intervalo acima do `e_min`) pede muito mais execuções e ficou como opção.
4. **Cego pareado.** A memória pode evitar o erro de código e piorar o texto da resposta final, que uma contagem de erros não
   vê. Especialistas comparariam pares de respostas, com e sem memória, sem saber qual é qual. É difícil de padronizar, então
   fica como verificação exploratória e não decide o veredito. Os danos que se medem sozinhos (estrutura da resposta, outros
   erros que sobem) continuam na condição 3 do §9.
5. **RespostaBacen.** Quase não tem o erro (0 de 76), então não testa mitigação. Serve a outra pergunta: uma memória
   injetada onde o erro é raro piora algo ou só gasta tokens? E roda em outro modelo (`o4-mini`), o que ajuda a ver se o
   resultado generaliza.
6. **Efeito colateral.** Se uma ferramenta grava ou envia algo, repetir execuções centenas de vezes pode mexer num sistema
   real. Opções: rodar ao vivo numa homologação, gravar as respostas das ferramentas e repeti-las, ou rodar ao vivo só as de
   leitura. A regra escolhida cobre os três casos; a parte técnica (bancos locais, caminho das ferramentas) é do Rafael.
7. **Estabilidade (`pass^k`).** Um agente que erra 1 vez em 10 parece bom na média e falha num caso real. Medir estabilidade é
   repetir o mesmo input `k` vezes e só contar sucesso se todas passarem; multiplica o custo por `k`, então é secundária.
8. **Autogerada.** A memória normal vem do pipeline de mineração e revisão; a autogerada é o agente escrevendo a lição no fim da
   execução. A pergunta é se o pipeline vale o trabalho ou se o agente aprende sozinho. Só no JoogleAnalytics, onde o erro é
   frequente e o braço é barato, e exploratória para não misturar com o veredito.

### O `p`, o limite de 5% e o Holm, em linguagem simples

**O `p`.** Com uma moeda: 10 lançamentos, 9 caras. Se a moeda fosse justa, só 22 das 1.024 sequências possíveis seriam tão
extremas (9 ou mais caras, ou 9 ou mais coroas): 22 ÷ 1.024 ≈ **2%**. Esse é o `p`: a chance de o acaso produzir algo tão
extremo **se não houvesse efeito nenhum**. No experimento, a "moeda justa" é a memória que não faz nada, e o `p` diz com que
frequência o acaso daria uma diferença tão grande entre os braços "com memória" e "sem memória".

**O limite de 5%.** O `p` sozinho não decide nada: é preciso escolher, **antes**, o quão raro é raro o bastante. A convenção é
5%: declaro o efeito real se `p` < 5%, e aceito me enganar 1 vez em 20 quando não há efeito.

**O problema dos três testes.** A fase 1 testa três pares. Se as três memórias não fizerem nada e cada teste usar 5%, a chance
de **pelo menos um** me enganar é `1 − 0,95³` = **14,3%** (1 vez em 7, não 1 em 20). Supõe testes independentes; com
dependência o valor real fica abaixo (Abdi, 2010, §2.1 e §4). Os três bilhetes de loteria têm mais chance de ganhar algo do
que um.

**Dividir o limite (Bonferroni).** Como os riscos de cada teste se somam, mais ou menos, uso 5% ÷ 3 = **1,67%** em cada um:
3 × 1,67% = 5%. (Conferido: 1 − 0,9833³ = 4,9%.) Fica seguro, mas duro para todos.

**O Holm: o "melhor de k tentativas".** O menor `p` dos três é o *melhor de três tentativas*, e entre três é mais fácil
alguém ter sorte. Por isso ele é comparado a um limite mais duro. Depois que ele passa e é declarado real, só dois ficam
em dúvida, e o seguinte é o melhor de duas. O limite de cada passo é 5% ÷ (quantos testes ainda estão em dúvida):

| Quantos restam | Com 5%, o melhor deles me engana em | Limite que traz de volta a 5% | Conferência |
|---:|---:|---:|---|
| 3 | 14,3% | **1,67%** (5% ÷ 3) | 1 − 0,9833³ = 4,9% |
| 2 | 9,8% | **2,5%** (5% ÷ 2) | 1 − 0,975² = 4,9% |
| 1 | 5% | **5%** (5% ÷ 1) | 5% |

Exemplo com `p` = 0,004; 0,021; 0,06 (inventados; o 0,021 vem de 29 contra 15 erros em 131 execuções por braço):

| Ordem | `p` | Limite | `p` ajustado (`(3 − ordem + 1) × p`) | Resultado |
|---:|---:|---:|---:|---|
| 1 | 0,004 | 1,67% | 0,012 | passa |
| 2 | 0,021 | 2,5% | 0,042 | passa |
| 3 | 0,06 | 5% | 0,06 | **barrado** |

**Passar** é declarar o efeito real; **barrar** é não declarar, o que não é o mesmo que "não funciona". O procedimento **para
no primeiro que falha**. Com a regra simples (1,67% para todos), o 0,021 seria barrado.

**O que está e o que não está verificado.** Conferem com Abdi (2010), lido inteiro: a conta dos 14,3%, os limites e a regra de
parar. **Não conferi no texto de Holm (1979)**, que não consegui obter: a prova de que o conjunto fica em 5% e a afirmação de
que vale sem supor nada sobre a dependência. A explicação do "melhor de k" é a usual, não está em Abdi. Ver o fichamento
[`literature/holm-1979.md`](literature/holm-1979.md).

### Decidido (bloco 7): como o placebo entra na correção

Cada par tem duas comparações: memória contra **sem memória** e memória contra **placebo**. A afirmação "este par mitiga"
exige as duas.

- **Opção A', teste de interseção-união por par e Holm entre os pares.** O `p` do par é o **maior** dos dois `p`; cada parte é
  testada sem correção dentro do par, e o Holm corrige só entre os **três** pares (Berger, 1982; **não obtive o texto**,
  apoio em fontes secundárias). A "opção A" anterior (testar o placebo só nos pares aprovados, mantendo a família em três)
  foi **retirada**: o controle do erro nesse caso é um problema de testes em portões (*gatekeeping*) e eu não o verifiquei.
- **Opção B, as seis comparações juntas no Holm.** Limites de 0,83%, 1%, 1,25%, 1,7%, 2,5% e 5%.

**Custo em execuções, por simulação** (13/11/2026; JoogleAnalytics, 35% sem memória, memória a 17,5% (redução de 50%), placebo
sem efeito; teste de duas proporções, primeiro passo do Holm, 200 mil simulações; aproximado):

| Opção | Passar numa comparação, com 131 por braço | Passar nas **duas**, com 131 por braço | Por braço para 80% nas duas |
|---|---:|---:|---:|
| A' (cada parte a 1,67%) | 81% | 69% | cerca de **160** |
| B (cada parte a 0,83%) | 73% | 60% | cerca de **180** |

O poder de 80% do plano valia **para uma comparação**. Para passar **nas duas**, preciso de cerca de 160 por braço (+22%) na
A' e de 180 (+37%) na B. Com a A' e redução de 50%, o `n` por braço sobe com a queda da taxa sem memória: 156 (35%), 194 (30%),
242 (25%), 317 (20%), 517 (13%).

**Reprodutibilidade (decidido na revisão de 13/11, item 8):** o script desta simulação — e o de qualquer refinamento de
poder — entra no repositório **antes do pré-registro**, em `analysis/…/pipeline/execucao/` (fora do hash da rodada), com os
parâmetros no cabeçalho. Número sem script não entra no pré-registro.

**Em aberto, e vai ficando por conta do Rafael, ao executar** (com o desenho aprovado, o que resta são estas questões técnicas e a leitura de Berger e Hsu; a porta do JoogleAnalytics e o texto do placebo já têm regra, nos §9 e §8.1) (questões técnicas; nenhuma muda o desenho acima):

| O que | Onde se fecha |
|---|---|
| Quais ferramentas de cada alvo têm efeito colateral, e se há homologação; como apontar para bancos locais ou trocar o caminho de uma ferramenta | a leitura do código (passo 1 da receita, §10) |
| O que define uma **família de inputs** em cada agente (tipo de processo, conjunto de campos) | a leitura do código; entra no pré-registro |
| **Modelo e versão do prompt de hoje** dos dois alvos | o piloto os registra; o experimento os **fixa** (o prompt do ContestacaoCivel teve quatro versões na base 2) |
| Quem são os especialistas do cego e quantos casos por agente (proposta: 1 a 2 especialistas, cerca de 20 pares por agente) | o Rafael, antes do pré-registro |
| Como a memória entra no prompt (a região `<memory>` ou o equivalente mais simples) | a leitura do código |
| **A porta de entrada do JoogleAnalytics:** a taxa de hoje abaixo da qual o sorteio fica caro demais (435 execuções por braço com 13%, 131 com 35%) e ele sai do confirmatório | definida no pré-registro, com o orçamento de execuções que o Rafael aceitar gastar |

**Dúvidas técnicas de cada etapa da receita (§10)** são tratadas pelo Rafael ao executar. Cada ajuste entra aqui, datado,
com o que mudou e por quê.

## 15. O que este documento reaproveita, e o que muda no plano geral

- **Reaproveitado sem mudança:** as medidas (§8 do plano geral), a estatística (§12), K e N (§9.3), os três níveis de
  replay (§7.1), a região `<memory>` (§6), o catálogo (`nao_vale_em`, `vale_junto_com`), os adendos por unidade.
- **O que a fase 1 muda no plano geral:** os agentes-espelho (a trilha 1) deixam de ser o caminho principal e passam a
  **ensaio e reserva** (construir o executor, o registro, a análise e o injetor, e servir quando um agente real não puder
  rodar); a trilha 2 (agentes reais) passa a ser **a fase 1**. Os experimentos de entrega, origem e conteúdo viram a
  fase 2, e só rodam para os pares em que a fase 1 mostrar que a memória mitiga.
