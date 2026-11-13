> **Tipo:** Relatório de achados, com o método e o racional · **Fase:** 1 (a memória mitiga o erro?) · **Data:** 13/11/2026 · **Status:** rascunho para discussão

# Relatório — volumetria das memórias por agente, para a fase 1

> Este relatório explica os números que entraram no §4.6 do [plano da fase 1](plano-fase-1-a-memoria-mitiga-o-erro.md):
> de onde vieram, como foram calculados, o que cada tabela diz e o que eu concluí delas. Os conceitos (intervalo de
> confiança, Holm, replay) estão em linguagem simples em [`conceitos-do-experimento.md`](conceitos-do-experimento.md).
> Cada afirmação vem marcada como **fato** (contado nos dados) ou **hipótese** (suposição minha, a medir).

## 1. Resumo

1. **Dois pares têm erro suficiente para a fase 1:** o JoogleAnalytics, com as memórias do `pandas` e dos imports
   (incidência de 35% e 22% em julho–agosto), e o ContestacaoCivel, com a memória das funções proibidas (1,9%). **Fato.**
2. **No JoogleAnalytics o erro caiu muito em agosto** (do `pandas`: 49% em julho, 13% em agosto). A queda não é sorte.
   A base termina em agosto: o erro pode já ter sumido na versão de hoje do agente. **Fato a queda; hipótese a causa.**
3. **A memória paga com eficácia baixa no JoogleAnalytics** (6% a 20%), precisa de cerca de metade dos erros evitados no
   ContestacaoCivel, e **não paga no RoteadorCivel**. **Hipótese:** depende do custo do passo com erro, que ainda não foi
   medido; o prompt da §9 o mede.
4. **O CalculoTrabalhista é caro demais para o confirmatório** (meio milhão de tokens por execução e só 41 execuções com o
   erro). **Fato.**
5. **A unidade do retorno que chega como texto pode baratear a fase 1** (o erro aparece com mais frequência no
   ContestacaoCivel), mas ela ainda não foi minerada nem revisada (§10.2).

## 2. De onde vêm os dados

- **Script:** `analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_memorias.py` (PR #44, com testes).
- **Entradas, na máquina 2:** a tabela de erros da mineração do sandbox (1.100 erros, cada um com a memória, o papel e o
  mês) e as contagens de todas as execuções da base 3 (71.894 linhas, uma por execução, agente e papel). Rodada
  `observada_c2e5e8b31f297d21`.
- **O que saiu da máquina 2:** só contagens, nomes de memória, de papel e meses. Nenhum identificador nem texto de caso.
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

## 6. Tabela 3 — a conta de compensação (a "tabela 2" do resumo anterior)

No resumo que eu te mandei antes, a segunda tabela era esta. Aqui ela ganha número próprio, as colunas explicadas e os
cenários.

**O que é:** para cada par, **quanto a memória precisa funcionar para pagar o que ela custa**. A memória custa tokens em
todo passo de toda execução (porque fica no contexto) e só economiza nas execuções em que o erro aconteceria.

| Agente · memória | Custo de injetar `c` (tokens por execução) | Economia por erro evitado `s` | Incidência `π` (jul–ago) | Eficácia mínima para pagar `c ÷ (π · s)` — cenário base | Faixa (otimista a pessimista) |
|---|---:|---:|---:|---:|---:|
| JoogleAnalytics · par | ~360 | ~17 mil (2 passos) | 35% (13% em agosto) | **6%** (16% com a taxa de agosto) | 6% a 20% |
| CalculoTrabalhista · imports | ~245 | ~45 mil (1 passo) | 2,9% | **19%** | 9% a 42% |
| ContestacaoCivel · funções proibidas | ~160 | ~18 mil (1 passo) | 1,9% | **48%** | 24% a 64% |
| RoteadorCivel · imports | ~60 | ~3 mil (1 passo) | 0,5% | **não paga** (precisaria de 384%) | 192% a 864% |

**Cada coluna:**

- **`c`** = tamanho da memória × mediana de passos da execução do papel. Tamanho da memória (hipótese, estimado pelo
  texto): 20 tokens a dos imports, 35 o par, 80 a das funções proibidas. Passos: a mediana medida (JoogleAnalytics 10,
  ContestacaoCivel 2, CalculoTrabalhista 12, RoteadorCivel 3).
- **`s`** = tokens de um passo × passos perdidos por erro. **Hipótese:** um passo custa a mediana de tokens da execução
  dividida pela mediana de passos (88 mil ÷ 10 no JoogleAnalytics). Passos perdidos: um por erro, porque em 9 de cada 10
  erros o agente se corrige no passo seguinte (dossiê do sandbox, item 16); dois no par do JoogleAnalytics, porque a
  linha que falha esquece os dois imports.
- **Cenários:** otimista = dois passos perdidos; pessimista = um passo perdido e a memória com 25 tokens a mais (o
  invólucro da região `<memory>`).

**O que ela diz:** a conta depende de três coisas, e o RoteadorCivel mostra todas: execução pequena (passo barato), erro
raro e memória lida em todo passo. Onde o erro é frequente (JoogleAnalytics), quase qualquer efeito paga; onde é raro e
o passo é barato (RoteadorCivel), nenhum efeito paga.

**O que falta para virar fato:** o custo **real** do passo que errou. A primeira volumetria não o mediu (o arquivo de custo
por papel não existe na rodada mais recente). O prompt da §9 mede os tokens e a duração do próprio passo com erro, e a
tabela é refeita com eles.

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

| O que falta | Por que importa | Como fechar |
|---|---|---|
| tokens e duração do **passo com erro**, por memória e papel | é a economia `s` da Tabela 3, hoje uma hipótese | o [prompt da máquina 2](prompt-maquina-2-custo-do-erro.md), passo 2 |
| a volumetria da unidade do **retorno que chega como texto** | decide se vale incluí-la (§10.2) | o mesmo prompt, passo 3 |
| o **modelo e a versão do prompt de hoje** de cada agente | explicaria a queda de agosto | o mesmo prompt, item 3 (ou a sua leitura do código) |
| **a taxa de hoje** | a base termina em agosto | o mesmo prompt, item 4 (as execuções dos últimos 30 dias); e, de vez, o piloto da fase 1 |
| se o **input de usuário** das execuções com erro pode ser recuperado | sem ele não há conjunto gatilho | sua leitura do código e do banco de traces (§3.1 do plano da fase 1) |

O script novo é `execucao/volumetria_custo_passo.py` (com 3 testes), e lê a tabela de casos que a rodada já guarda (`perfis/<unidade>/casos.csv`, que tem os tokens e a duração de cada passo com erro).

## 10. As duas perguntas que você fez

### 10.1 Vale testar a memória autogerada já na fase 1?

**A pergunta da fase 1 é "a memória mitiga o erro, e a que custo?".** A autogerada pergunta outra coisa: "a taxonomia vale
como produtora de memória, ou o agente aprende sozinho?". As duas importam, mas não devem se misturar no veredito.

**O que eu recomendo:** incluir a autogerada **como um quarto braço, exploratório, só no JoogleAnalytics**.

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

**Sua intuição está certa num ponto:** no ContestacaoCivel, esse erro deve aparecer com mais frequência que o das funções
proibidas. **Estimativa (hipótese):** com 2.385 erros em 13.454 execuções do papel, a incidência é no máximo 17,7% (se cada
erro estivesse numa execução diferente); com a média de 1,5 erro por execução da unidade, seria cerca de 12%. Seria **cerca
de 6 vezes mais frequente** que o das funções proibidas (1,9%), e o experimento precisaria de **cerca de 7 vezes menos
execuções** sorteadas (cerca de 475 por braço, contra 3.258). E como cada erro custa o dobro em tokens, a conta de compensação ficaria mais fácil.

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
- **A Tabela 3 depende de duas hipóteses** (custo do passo e tamanho da memória). O prompt da §9 fecha a primeira; a
  segunda se mede contando os tokens do texto injetado.
- **A Tabela 4 é conservadora:** a fórmula ignora que os braços rodam os mesmos inputs. Com os dados do piloto, a fórmula
  pareada do Miller dá um número menor.
- **"Inputs disponíveis" supõe que o input de cada execução com erro pode ser recuperado.** Não está confirmado.
- **Os números da §10.2 são estimativa**, a confirmar pelo passo 3 do prompt.
