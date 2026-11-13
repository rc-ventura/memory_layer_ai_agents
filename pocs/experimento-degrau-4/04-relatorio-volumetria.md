> **Tipo:** Relatório de achados, com o método e o racional · **Fase:** 1 (a memória mitiga o erro?) · **Data:** 13/11/2026 · **Status:** rascunho para discussão

# Relatório — volumetria das memórias por agente, para a fase 1

> Este relatório explica os números que entraram no §4.6 do [plano da fase 1](02-fase-1-mitiga-erro.md):
> de onde vieram, como foram calculados, o que cada tabela diz e o que eu concluí delas. Os conceitos (intervalo de
> confiança, Holm, replay) estão em linguagem simples em [`03-conceitos.md`](03-conceitos.md).
> Cada afirmação vem marcada como **fato** (contado nos dados) ou **hipótese** (suposição minha, a medir).

## 1. Resumo

1. **Dois pares têm erro suficiente para a fase 1:** o JoogleAnalytics, com as memórias do `pandas` e dos imports
   (incidência de 35% e 22% em julho–agosto), e o ContestacaoCivel, com a memória das funções proibidas (1,9%). **Fato.**
2. **No JoogleAnalytics o erro caiu muito em agosto** (do `pandas`: 49% em julho, 13% em agosto). A queda não é sorte.
   A base termina em agosto: o erro pode já ter sumido na versão de hoje do agente. **Fato a queda; hipótese a causa.**
3. **A memória paga com eficácia baixa no JoogleAnalytics** (6% a 22%), precisa de cerca de um terço dos erros evitados
   no ContestacaoCivel (33%, com o custo do passo com erro **medido** em 13/11) e **não paga no RoteadorCivel**
   (precisaria de 360%). **Fato** a conta com o custo medido; **hipótese** os passos perdidos por erro e o tamanho da memória.
4. **O CalculoTrabalhista é caro demais para o confirmatório** (meio milhão de tokens por execução e só 41 execuções com o
   erro). **Fato.**
5. **A unidade do retorno que chega como texto pode baratear a fase 1.** Medido: no ContestacaoCivel o erro aparece em
   10,9% das execuções (cerca de 6 vezes mais que o das funções proibidas), mas a unidade ainda não foi minerada nem
   revisada (§10.2). **Fato** a incidência; ela é do período inteiro, não do mês.
6. **A base que a máquina 2 tem termina em 29/08/2026.** Ela não diz nada sobre a taxa de hoje, e o modelo e a versão do
   prompt dos agentes continuam **não vistos** (§9).

## 2. De onde vêm os dados

- **Script:** `analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_memorias.py` (PR #44, com testes).
- **Entradas, na máquina 2:** a tabela de erros da mineração do sandbox (1.100 erros, cada um com a memória, o papel e o
  mês) e as contagens de todas as execuções da base 3 (71.894 linhas, uma por execução, agente e papel). Rodada
  `observada_c2e5e8b31f297d21`.
- **O que saiu da máquina 2:** só contagens, nomes de memória, de papel e meses. Nenhum identificador nem texto de caso.
- **Segunda rodada de medidas (13/11/2026):** o custo do passo com erro (tokens e segundos, por memória e papel; lido do
  perfil `U_sandbox` da mesma rodada) e a incidência de **todas** as unidades por papel (`triagem_por_papel.csv`).
  O script é `execucao/volumetria_custo_passo.py`.
- **Conferência da transcrição:** em todas as linhas usadas aqui, recalculei a incidência dividindo as duas contagens e
  ela bateu com a que o script imprimiu.
- **O período:** de novembro de 2025 a agosto de 2026, a janela da base 3. "Julho–agosto" são os dois últimos meses.
- **Nenhum aviso** de papel sem correspondente nas contagens. O `ContestacaoCivel` aparece nas saídas como
  `ontestacaoCivel` (o nome vem cortado nos dados de erro, como o dossiê do sandbox já registrava); aqui uso o nome inteiro.

## 3. Como calculei — as fórmulas, uma por uma

| Medida | Fórmula | Por quê |
|---|---|---|
| **Incidência** | execuções **distintas** do papel com o erro ÷ execuções do papel, no mesmo período | conta execuções, não erros: uma execução com o erro duas vezes conta uma vez. É a probabilidade de uma execução qualquer do papel ter o erro |
| **Intervalo de confiança de 95%** | o intervalo de **Wilson** para uma proporção | o intervalo "de livro" (`p ± 1,96·√(p(1−p)/n)`) erra quando a proporção é pequena ou há poucas execuções, e pode até dar valores negativos; o de Wilson se comporta bem nesses casos (Bowyer et al., 2025, sobre a aproximação normal em amostras pequenas) |
| **Execuções para ver o erro uma vez (95%)** | o menor `n` tal que `1 − (1 − p)^n ≥ 95%`, isto é, `ln(0,05) ÷ ln(1 − p)`; cerca de `3 ÷ p` | quantas execuções sorteadas são precisas para ter 95% de chance de o erro aparecer ao menos uma vez. A faixa entre parênteses usa os dois limites do intervalo de `p` |
| **Comparar dois meses** | teste de duas proporções (estatística `z`) | diz se a mudança de um mês para o outro é maior do que o acaso explicaria. `|z|` acima de 2 já é difícil de atribuir à sorte; acima de 4, praticamente impossível |
| **Execuções necessárias por braço** | a fórmula de duas proporções, poder de 80%, bilateral, com o limite de 5% dividido por 3 (Holm sobre três pares) | quantas execuções por braço para detectar uma redução relativa do erro. É conservadora, porque ignora o pareamento por input (Miller, 2024) |
| **Compensação** | custo de injetar `c` = tokens da memória × passos da execução; economia `s` = tokens de um passo × passos perdidos por erro; a memória paga se `π · e · s > c`, isto é, se a eficácia `e` passar de `c ÷ (π · s)` | a memória custa leitura em **todo** passo de **toda** execução, e só economiza nas execuções que teriam o erro |

## 4. Tabela 1 — a incidência de cada par

| Agente · memória | Execuções com o erro ÷ execuções do papel (todo o período) | Incidência no período (IC 95%) | Julho–agosto (IC 95%) | Execuções para ver o erro 1 vez, jul–ago (faixa) |
|---|---:|---:|---:|---:|
| **JoogleAnalytics · `pandas`** | 231 ÷ 584 | 39,6% (35,7 a 43,6) | **35,0%** (28,4 a 42,1) | **7** (6 a 9) |
| **JoogleAnalytics · imports (`json`)** | 107 ÷ 584 | 18,3% (15,4 a 21,7) | **22,4%** (17,0 a 29,0) | **12** (9 a 17) |
| **ContestacaoCivel · funções proibidas** | 254 ÷ 13.454 | 1,89% (1,67 a 2,13) | **1,87%** (1,66 a 2,12) | **159** (141 a 180) |
| CalculoTrabalhista · imports | 41 ÷ 990 | 4,1% (3,1 a 5,6) | 2,9% (1,7 a 5,0) | 102 (59 a 178) |
| OBFCivel · funções proibidas | 36 ÷ 5.658 | 0,64% (0,46 a 0,88) | 0,90% (0,65 a 1,24) | 332 (240 a 460) |
| RoteadorCivel · imports | 241 ÷ 45.271 | 0,53% (0,47 a 0,60) | 0,48% (0,41 a 0,56) | 626 (538 a 729) |
| RespostaBacen · funções proibidas | 5 ÷ 3.044 | 0,16% | **0 de 76** | — |

**Como ler.** A incidência é a pergunta "se eu rodar uma execução qualquer deste agente, qual a chance de o erro
acontecer?". O intervalo mostra o quanto ela é precisa: com 584 execuções, o JoogleAnalytics tem um intervalo largo (vários
pontos); com 13 mil, o ContestacaoCivel tem um intervalo estreito. A última coluna traduz a incidência para o que importa
no experimento: **quantas execuções até o erro aparecer**.

**O que ela diz.** O JoogleAnalytics erra muito (o erro aparece em menos de 10 execuções); o ContestacaoCivel erra pouco
em proporção, mas tem muito volume (251 execuções com o erro em dois meses); o RoteadorCivel erra raramente; o
RespostaBacen quase não roda mais (76 execuções em julho–agosto) e não teve o erro.

## 5. Tabela 2 — a série mensal (o erro está mudando?)

| Agente · memória | mar | abr | mai | jun | jul | ago |
|---|---:|---:|---:|---:|---:|---:|
| **JoogleAnalytics · `pandas`** | 26% (19/73) | 41% (47/114) | 48% (42/87) | 57% (59/103) | **49%** (55/113; IC 40 a 58) | **13%** (9/70; IC 7 a 23) |
| **JoogleAnalytics · `json`** | 11% (8/73) | 9% (10/114) | 14% (12/87) | 35% (36/103) | **35%** (40/113) | **1,4%** (1/70; IC 0,3 a 7,7) |
| ContestacaoCivel · funções proibidas | — | — | — | 6,1% (3/49) | 1,4% (68/4.881) | 2,1% (183/8.524) |
| RoteadorCivel · `json` | — | — | 0,3% (3/903) | 0,8% (71/9.334) | 0,7% (132/17.857) | 0,2% (35/17.121) |

(Entre parênteses: execuções com o erro ÷ execuções do papel no mês.)

**Como ler.** Cada célula é a incidência daquele mês. A pergunta é se o erro é estável: se mudar muito, a taxa do
experimento (que roda hoje) não será a da tabela.

**O que ela diz — fato:** de julho para agosto, o erro do `pandas` no JoogleAnalytics caiu de 49% para 13% (`z` = 4,9) e o
do `json` de 35% para 1,4% (`z` = 5,4); o do `json` no RoteadorCivel caiu de 0,7% para 0,2% (`z` = 7,3); e o das funções
proibidas no ContestacaoCivel **subiu** de 1,4% para 2,1% (`z` = −3,1). Nenhuma dessas mudanças é sorte.

**Por que pode ter caído — hipótese:** agosto é o mês da troca de modelo em outros papéis (relatório da base 2, §2).
Uma troca de modelo ou de versão do prompt no JoogleAnalytics explicaria a queda. **Não verifiquei**: a base 3 não
exporta o modelo. A base 2 pode responder, e o prompt da §9 pede o modelo de hoje de cada agente.

**A consequência — fato:** a base termina em agosto e estamos em novembro. A taxa de hoje pode ser a de agosto (13%), a de
julho (49%) ou outra. **O piloto da fase 1 mede isso primeiro**, antes de qualquer outra coisa.

## 6. Tabela 3 — a conta de compensação

**O que é:** para cada par, **quanto a memória precisa funcionar para pagar o que ela custa**. A memória custa tokens em
todo passo de toda execução (porque fica no contexto) e só economiza nas execuções em que o erro aconteceria.

**O que mudou em 13/11:** a economia `s` deixou de ser hipótese. Agora é o custo **medido** do passo que errou (mediana
de tokens, nos erros lidos da mineração do sandbox). O custo de injetar `c` e os passos perdidos continuam hipótese.

| Agente · memória | Custo de injetar `c` (tokens por execução, hipótese) | Passo com erro `s` medido: tokens, mediana (p90) | Passos perdidos (hipótese) | Incidência `π` (jul–ago) | Eficácia mínima para pagar `c ÷ (π · s)`, cenário base | Faixa | Antes da medida |
|---|---:|---:|---:|---:|---:|---:|---:|
| JoogleAnalytics · `pandas` (o par) | ~360 | 8.065 (9.971) | 2 | 35% (13% em agosto) | **6%** (17% com a taxa de agosto) | 6% a 22% | 6% |
| CalculoTrabalhista · imports | ~245 | 41.792 (62.190) | 1 | 2,9% | **20%** | 10% a 45% | 19% |
| ContestacaoCivel · funções proibidas | ~160 | 26.246 (99.610) | 1 | 1,9% | **33%** | 16% a 43% | 48% |
| RoteadorCivel · imports | ~60 | 3.477 (4.053) | 1 | 0,5% | **não paga** (precisaria de 360%) | 180% a 810% | 384% |

**Cada coluna:**

- **`c`** = tamanho da memória × mediana de passos da execução do papel. Tamanho da memória (hipótese, estimado pelo
  texto): 20 tokens a dos imports, 35 o par, 80 a das funções proibidas. Passos: a mediana medida (JoogleAnalytics 10,
  ContestacaoCivel 2, CalculoTrabalhista 12, RoteadorCivel 3).
- **`s`** = tokens do passo que errou (**medido**) × passos perdidos por erro. Passos perdidos (hipótese): um por erro,
  porque em 9 de cada 10 erros o agente se corrige no passo seguinte (dossiê do sandbox, item 16); dois no par do
  JoogleAnalytics, porque a linha que falha esquece os dois imports. O que se mediu é só o passo com erro; o passo de
  correção não entrou.
- **Cenários:** otimista = dois passos perdidos; pessimista = um passo perdido e a memória com 25 tokens a mais por passo
  (o invólucro da região `<memory>`).

**O que ela diz — fato, com o custo medido:**

- **O JoogleAnalytics e o RoteadorCivel não mudaram de resposta.** O passo do JoogleAnalytics custa 8 a 9 mil tokens, bem
  perto da hipótese de 8,8 mil; a memória paga com eficácia de 6%. O do RoteadorCivel custa 3,5 mil: a memória não paga.
- **O ContestacaoCivel ficou mais fácil:** o passo com erro custa 26 mil tokens (a hipótese era 18 mil), e a eficácia
  mínima caiu de 48% para 33%. A cauda é longa: o p90 é de 100 mil tokens, quase quatro vezes a mediana; com ele a
  eficácia mínima seria de 9%. A mediana é a conta conservadora.
- **A duração tem cauda ainda maior no ContestacaoCivel:** mediana de 31 segundos, p90 de 618 (mais de 10 minutos). Nos
  outros pares o passo com erro dura de 3 a 8 segundos de mediana, então a latência quase não pesa lá.
- **O CalculoTrabalhista continua caro demais** para o confirmatório (o passo com erro custa 42 mil tokens e só há 41
  execuções com o erro).

**A mesma tabela, para todas as memórias do sandbox** (tokens do passo com erro, mediana; só as com mais de 40 erros):
imports do RoteadorCivel 3.477; imports do JoogleAnalytics (`json`) 9.223; `pandas` do JoogleAnalytics 8.065; imports do
CalculoTrabalhista 41.792; funções proibidas do ContestacaoCivel 26.246; funções proibidas do OBFCivel 13.395. O arquivo
completo, com os p90 e os segundos, fica na máquina 2 (`custo_do_erro_por_memoria.csv`).

## 7. Tabela 4 — quantas execuções o experimento precisa

Se os inputs forem **sorteados** da produção, a taxa sem memória é a própria incidência. Execuções por braço para detectar
a redução, poder de 80%, limite de 5% dividido por 3 (Holm sobre três pares):

| Taxa do erro sem memória | redução de 50% | redução de 70% | Onde se aplica |
|---:|---:|---:|---|
| 35% | 131 | 60 | JoogleAnalytics · `pandas`, se a taxa de julho valer hoje |
| 22% | 238 | 107 | JoogleAnalytics · `json` |
| 13% | 435 | 195 | JoogleAnalytics · `pandas`, se a taxa de agosto valer hoje |
| 1,9% | 3.258 | 1.443 | ContestacaoCivel, sorteando |
| 0,5% | 12.515 | 5.536 | RoteadorCivel, sorteando |

**O que ela diz:**

- No **JoogleAnalytics**, sortear inputs funciona se a taxa de hoje estiver perto da de julho (131 execuções por braço).
  Com a taxa de agosto, o número triplica.
- No **ContestacaoCivel**, sortear não funciona (3 mil por braço). É preciso o **conjunto gatilho**: os inputs que erraram
  na produção (há 251 em julho–agosto). Nesse conjunto a taxa sem memória é a **taxa de reprodução**, que o piloto mede;
  com 40%, são cerca de 120 execuções por braço (tabela 4.1 do plano da fase 1).

## 8. Tabela 5 — quanto custa rodar cada par

Três braços (sem memória, com memória, placebo), na mediana de tokens por execução do papel.

| Agente | Desenho | Execuções | Tokens | Inputs com o erro disponíveis |
|---|---|---:|---:|---:|
| JoogleAnalytics | sorteio, taxa de julho (131 por braço) | 393 | ~35 milhões | 231 |
| JoogleAnalytics | sorteio, taxa de agosto (435 por braço) | 1.305 | ~115 milhões | 231 |
| ContestacaoCivel | conjunto gatilho, reprodução de 40% (82 a 122 por braço) | 246 a 366 | ~9 a 13 milhões | 254 |
| RoteadorCivel | conjunto gatilho (82 a 122 por braço) | 246 a 366 | ~2 a 4 milhões | 241 |
| CalculoTrabalhista | conjunto gatilho (82 a 122 por braço) | 246 a 366 | **~135 a 201 milhões** | 41 (cada input repetido 2 a 3 vezes) |

A mediana subestima o custo, porque execuções com erro são mais longas; o teto real é maior.

## 9. O que não foi medido, e como fechar

| O que faltava | Estado (13/11/2026) | Como fechar o que resta |
|---|---|---|
| tokens e duração do **passo com erro**, por memória e papel | **medido** (Tabela 3) | — |
| a volumetria da unidade do **retorno que chega como texto** | **medida**, do período inteiro (§10.2) | a série mês a mês só sai se a unidade ganhar perfil: `executar.py analisar --perfil-investigacao U_tipo_retorno` e `volumetria_custo_passo.py --casos-unidade` |
| o **modelo e a versão do prompt de hoje** de cada agente | **parcial**: o agente da máquina 2 triangulou, por `exec_id`, as execuções da base 3 que também estão nas bases 1 e 2 (ver abaixo). É o passado, não o de hoje | a sua leitura do código dos agentes |
| **a taxa de hoje** | **não responde**: o banco de traces da máquina 2 termina em 29/08/2026 (a execução mais recente de cada papel é de 27 a 29/08) | o piloto da fase 1 |
| se o **input de usuário** das execuções com erro pode ser recuperado | **sim** (resposta do Rafael, 13/11/2026); falta só conferir por papel | a leitura do código e do banco de traces (§3.1 do plano da fase 1) |

**Modelo e versão do prompt, nas execuções das bases 1 e 2 que também estão na base 3** (junção por `exec_id`; só os nomes e as contagens):

| Papel | Execuções trianguladas (base 1 · base 2) | Modelo | Versões do prompt |
|---|---|---|---|
| ContestacaoCivel | 3 · 224 | `gpt-5.2-2025-12-11` (uma variante com sufixo `-gs` em 22) | **quatro** na base 2: 152, 51, 20 e 1 execuções |
| RespostaBacen | 24 · 56 | `azure/o4-mini-2025-04-16` (alguns sem registro) | uma só |
| JoogleAnalytics | 1 · 10 | `gpt-4.1-2025-04-14` (2 sem registro) | uma só |
| CalculoTrabalhista | 8 · 12 | `gpt-4.1-2025-04-14` (alguns sem registro) | uma só |

**O que isso diz e o que não diz.** **Fato:** o ContestacaoCivel teve quatro versões de prompt na base 2, então o prompt
desse agente muda; o experimento precisa **fixar e registrar** o modelo e a versão do prompt. **Não diz nada sobre a queda de
agosto no JoogleAnalytics:** só 11 execuções dele foram trianguladas, todas com o mesmo modelo e o mesmo prompt, e isso não
cobre julho nem agosto. **Hipótese minha:** o mesmo código de versão (`b0f37eea`) aparece em três agentes diferentes, o que
sugere que ele identifica um prompt-base compartilhado e não o prompt do agente; a leitura do código confirma ou não. Nada
disso é "de hoje".

**Execuções nos "últimos 30 dias" do banco da máquina 2** (a contagem é relativa ao fim da base, em agosto, e não a hoje):
ContestacaoCivel 8.880 (a última em 29/08), RespostaBacen 72 (27/08), JoogleAnalytics 75 (29/08), CalculoTrabalhista 360
(28/08). Isso confere com a Tabela 2 (agosto, JoogleAnalytics: 70 execuções).

**Para repetir as duas medidas** (da raiz, na máquina da base; o primeiro comando só é preciso se o perfil do sandbox ainda não existir):

```
uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py analisar --perfil U_sandbox
uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py --casos-sandbox
uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py --rodada
```

Sem valor, `--casos-sandbox` e `--rodada` procuram a rodada mais recente que tenha o arquivo e imprimem o nome dela.

## 10. As duas perguntas que você fez

### 10.1 Vale testar a memória autogerada já na fase 1?

**A pergunta da fase 1 é "a memória mitiga o erro, e a que custo?".** A autogerada pergunta outra coisa: "a taxonomia vale
como produtora de memória, ou o agente aprende sozinho?". As duas importam, mas não devem se misturar no veredito.

**Decidido em 13/11/2026 (Rafael):** incluir a autogerada **como um quarto braço, exploratório, só no JoogleAnalytics**.

- **Por que lá:** é o par em que o erro aparece mais (mais lições geradas no piloto) e o mais barato de testar com sorteio.
  O braço a mais custa cerca de 131 execuções e ~12 milhões de tokens, mais uma chamada de LLM por execução com erro do
  piloto para gerar as lições.
- **Por que exploratório:** a hipótese de que a memória revisada vale mais que a autogerada se apoia num artigo cujo método
  eu ainda não li (SkillsBench). E o veredito da fase 1 (a memória revisada mitiga?) fica limpo, com a mesma família de
  comparações.
- **Por que não no ContestacaoCivel:** lá o erro é raro (1,9%), o piloto produziria poucas lições, e cada braço a mais
  custa caro em execuções.
- **O ganho:** se a autogerada empatar com a revisada no JoogleAnalytics, você sabe cedo que a pergunta "vale a pena a
  taxonomia como produtora de memória?" é séria, antes de investir na fase 2.

### 10.2 Vale minerar a unidade do retorno que chega como texto?

**O que já se sabe — fato, do relatório da base 3:** é a maior unidade em tokens (207 milhões), com 5.319 erros em 3.480
execuções, 17 papéis, 10 meses; o ContestacaoCivel tem 2.385 desses erros (45%); cada erro custa cerca de 39 mil tokens (o
dobro da média); o pico foi em agosto (2.664 erros).

**Medido em 13/11 — fato (período inteiro, não o mês a mês):** a incidência da unidade por papel.

| Papel | Erros | Execuções com a unidade | Execuções do papel | Incidência | Execuções até ver o erro (95%) | Tokens do passo com erro (média) |
|---|---:|---:|---:|---:|---:|---:|
| ContestacaoCivel | 2.385 | 1.465 | 13.454 | **10,9%** | 26 | 57.920 |
| RespostaBacen | 889 | 730 | 3.044 | 24,0% | 11 | 11.922 |
| CalculoTrabalhista | 680 | 499 | 990 | 50,4% | 5 | 50.564 |
| OBFCivel | 638 | 443 | 5.658 | 7,8% | 37 | 14.844 |
| JoogleAnalytics | 576 | 224 | 584 | 38,4% | 7 | 12.545 |

**O que isso muda.** A estimativa que eu tinha dado (cerca de 12% no ContestacaoCivel) se confirmou: 10,9%. É **cerca de 6
vezes** a incidência das funções proibidas (1,9%), e ver o erro leva 26 execuções, contra cerca de 160. Para o experimento
sorteado, isso é perto de 7 vezes menos execuções. E o passo com erro custa o dobro (a média é de 58 mil tokens contra 26 mil
de mediana nas funções proibidas; atenção: uma é média e a outra mediana). O RespostaBacen, que ficou de fora da fase 1 por
quase não rodar mais, tem 24% de incidência nessa unidade, mas só 72 execuções no último mês da base.

**O que o número não é.** A contagem vem da regra automática que agrupa os erros, não de uma lição conferida: pode misturar
causas. E é do período inteiro: o pico foi em agosto (2.664 erros), então a taxa recente do ContestacaoCivel pode ser maior.

**O que pesa contra, agora:**

1. **Ela não passou pelos degraus 1 a 3.** Não há texto de memória, nem leitura de casos, nem gate. Testar uma lição não
   revisada mistura duas perguntas: "a memória mitiga?" e "esta lição está certa?". Um resultado negativo não diria qual
   das duas falhou.
2. **O destino não foi decidido.** A causa conhecida é o retorno da ferramenta da petição inicial chegando como texto JSON
   (relatório da base 3). O conserto pode ser na ferramenta (sinal de harness), não na memória.
3. **O tempo.** O sandbox levou cerca de três semanas, da mineração (19/10) ao degrau 3 (09/11).

**O que eu recomendo:**

- **Agora:** medir a volumetria dela (passo 3 do prompt), para trocar a estimativa por fato.
- **Em paralelo à fase 1:** começar a mineração (degrau 1 é trabalho de script) e decidir o destino. Se ela chegar ao
  degrau 3 a tempo, entra como **fase 1b** no ContestacaoCivel, onde deve ser mais barata de testar que a memória das
  funções proibidas.
- **Não trocar** os pares da fase 1 por ela: a fase 1 começa com as memórias já revisadas.

## 11. Limites deste relatório

- **A base termina em agosto de 2026.** Toda incidência é histórica; a de hoje só o piloto mede.
- **A Tabela 3 ainda depende de duas hipóteses:** os passos perdidos por erro e o tamanho da memória. O custo do passo com
  erro agora é medido, mas só o do passo que errou, sem o passo de correção. O tamanho da memória se mede contando os
  tokens do texto injetado.
- **A Tabela 4 é conservadora:** a fórmula ignora que os braços rodam os mesmos inputs. Com os dados do piloto, a fórmula
  pareada do Miller dá um número menor.
- **"Inputs disponíveis" supõe que o input de cada execução com erro pode ser recuperado.** Não está confirmado.
- **Os números da §10.2 são medidos, mas do período inteiro e por regra automática**, não por lição conferida.
- **A média e a mediana não se comparam:** a Tabela 3 usa a mediana do passo com erro; a §10.2, a média (é o que a tabela da
  rodada guarda).
