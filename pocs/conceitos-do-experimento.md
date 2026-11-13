> **Tipo:** Conceitos para entender o experimento, sem jargão · **Status:** rascunho · **Data:** 12/11/2026

# Conceitos do experimento, em linguagem simples

Este texto explica, em ordem, as ideias que o [plano da fase 1](plano-fase-1-a-memoria-mitiga-o-erro.md) usa. Os números
dos exemplos são contas minhas de 12/11/2026, e os valores de cada agente real só saem das contagens da máquina 2.

## 1. O experimento ideal, em um comando

Imagine que tudo já está pronto. Você escreve um arquivo de configuração e roda **um comando**:

```
rodar_experimento --config experimento.yaml
```

O arquivo diz: **quais inputs reais** (a lista congelada), **quais braços** (sem memória, com memória, placebo) e
**quantas repetições `K`** de cada input. O programa faz, sozinho:

1. Para cada input, em ordem sorteada, roda o agente em dev com cada braço, `K` vezes.
2. **A cada passo do agente**, olha o que aconteceu e anota: houve erro? Qual? (o classificador do pipeline, sem LLM).
3. Grava **uma linha por execução**: input, braço, repetição, modelo, versão, e a lista de tudo que aconteceu (abaixo).
4. No fim, calcula as tabelas do §6 e escreve o relatório.

**O que cada linha registra:** os erros de **todas** as unidades (qual unidade, em qual passo, a mensagem), se o erro-alvo
aconteceu, o número de passos, os tokens de entrada e de saída, o tempo (modelo, ferramenta, interpretador), se terminou
com resposta final, a resposta final, e se a memória estava presente e foi seguida. Nada precisa ser decidido durante a
execução: **o experimento só observa**, e a decisão vem na análise.

Por isso você não precisa "ficar de olho" quando erra. O registro já diz **qual erro foi**. Se aparecer um erro que não
é o X, ele fica anotado como outro erro e entra na conta de "criou outro erro".

## 2. Quantas execuções para o erro X aparecer

Se o erro acontece em uma fração `p` das execuções, ele aparece em média a cada `1/p` execuções. Para ter **confiança** de
vê-lo, é preciso mais:

| `p` (taxa do erro) | em média | ver pelo menos 1 vez (95% de chance) | ver pelo menos 10 vezes (95%) |
|---:|---:|---:|---:|
| 50% | 2 | 5 | 28 |
| 20% | 5 | 14 | 76 |
| 10% | 10 | 29 | 154 |
| 5% | 20 | 59 | 311 |
| 2% | 50 | 149 | 782 |
| 1% | 100 | 299 | 1.568 |
| 0,5% | 200 | 598 | 3.138 |

Regra de bolso: para ver o erro **ao menos uma vez**, rode cerca de `3 ÷ p` execuções.

**A pergunta que importa para nós não é "o erro aparece?" e sim "quantas vezes ele precisa aparecer para eu poder
comparar?"**. Para detectar uma redução de 50%, são de 23 a 900 execuções **com o erro** por braço, conforme a taxa
(tabela do §4.1 do plano da fase 1). Por isso a fase 1 usa inputs que **já errou** na produção: se o erro tem taxa de 40%
nesses inputs, são 82 execuções por braço, e não milhares.

**De onde vem o `p` real de cada agente:** da contagem na máquina 2 (§8).

## 3. Por que "não errou com a memória" não prova nada

O agente erra por **sorte também**. Se sem memória ele erra 50% das vezes, em **uma** execução com memória ele não erra
com 50% de chance, **mesmo que a memória não faça nada**. Uma execução sem erro não diz se foi a memória ou a sorte.

Quantas execuções seguidas sem erro acontecem **por acaso**, sem memória nenhuma, conforme a taxa de erro `p0`:

| `p0` | 1 execução | 3 | 5 | 10 |
|---:|---:|---:|---:|---:|
| 80% | 20% | 0,8% | ~0% | ~0% |
| 50% | 50% | 12,5% | 3,1% | 0,1% |
| 30% | 70% | 34% | 17% | 2,8% |
| 10% | 90% | 73% | 59% | 35% |

Com taxa de erro de 10%, **dez** execuções sem erro seguidas ainda acontecem por acaso em 35% das vezes. A resposta
sempre é comparar **taxas**, em muitas execuções, sob as mesmas condições, com o braço sem memória rodando junto
(mesmo dia, mesma versão, ordem sorteada). Só uma **diferença entre taxas** é evidência. Isso é o **braço de controle**.

**Seu exemplo (1.000 execuções sem memória erram 10%; 1.000 com memória erram 1 vez):**

| | erros | taxa | intervalo de confiança de 95% (Wilson) |
|---|---:|---:|---|
| sem memória | 100 | 10% | de 8,3% a 12,0% |
| com memória | 1 | 0,1% | de 0,02% a 0,56% |

Os dois intervalos **não se tocam**: a diferença não é sorte. A redução é de cerca de **9,9 pontos percentuais**
(intervalo de 8,0 a 11,8). O que cada leitor entende melhor é o **"número a tratar"**: `1 ÷ 0,099 ≈ 10`, isto é, a
cada 10 execuções com a memória, **evita-se um erro**.

**E se o resultado fosse zero erros em 1.000?** Não se diz "a taxa é zero", e sim que com 95% de confiança ela é **menor
que cerca de 0,3%** (a **regra dos três**: o limite superior é `3 ÷ n`).

## 4. Replay: o que é, e se dá para congelar

Pensando só no essencial, "refazer" uma execução pode significar quatro coisas diferentes:

| Tipo | O que se congela | O que ainda varia | Serve para testar a memória? |
|---|---|---|---|
| **Rodar de novo** | só o input | o modelo (mesmo com temperatura zero não é idêntico, Atil et al., 2024), as ferramentas, o estado do caso | sim, mas é ruidoso e custa uma execução inteira |
| **Congelar o mundo** (gravar e repetir as ferramentas) | o input **e as respostas das ferramentas** | só o modelo | sim, e sem efeito colateral |
| **Congelar o modelo também** (repetir as respostas gravadas do LLM) | tudo | nada | **não**: a memória age sobre o LLM, e a resposta dele já está fixa. Só serve para testar o código em volta |
| **Replay de passo** (a "bifurcação") | tudo **até o passo t**: o que o modelo viu naquele passo | só a resposta do modelo no passo t | **sim, e é o mais barato** |

**O replay de passo é o que importa para você.** O trace guarda, em cada passo, a **entrada exata** que o modelo recebeu
(as mensagens). Então dá para: pegar um passo em que o erro aconteceu, **repetir só aquele passo** com a mesma entrada,
**sem** memória `K` vezes e **com** memória `K` vezes, e ver em quantas de cada o erro volta. Um passo é uma chamada de LLM,
bem menos que uma execução inteira. O método tem nome na literatura: DoVer e AgentDebug intervêm no passo da falha e
continuam dali (Ma et al., 2025; Zhu et al., 2025).

**É possível congelar? Sim, com duas ressalvas.**

- O trace **completo** é necessário. A base 3 tem só os passos com erro e uma janela curta, sem o prompt de sistema; o
  trace completo está no banco de traces do ambiente (a base 2 o tem).
- Depois do passo `t`, o mundo muda: o replay de passo mede **a probabilidade do erro naquele passo**, e não o efeito na
  cascata, nos tokens e no tempo. Para isso há a execução inteira.

**Uma vantagem do replay de passo para este erro:** o "erro do sandbox" (usar `json` sem importar; chamar uma função
barrada) aparece **no código que o modelo escreve**, então se detecta lendo o código, sem rodar ferramenta nenhuma. É
preciso **conferir** que essa leitura estática dá o mesmo rótulo que o classificador teve na execução real (ver §5).

**Resposta ao seu cenário** ("errou, injetamos a memória, e o erro não apareceu"): uma amostra sem erro não prova nada
(§3). No replay de passo a pergunta é "em quantas das `K` repetições o erro volta?". Se sem memória volta em 5 de 10 e
com memória em 1 de 10, isso já é uma diferença; com 2 de 10 e 1 de 10, é sorte.

**Rodar de novo é a base do experimento; replay de passo é a triagem barata.** O plano geral usa os três níveis (§7.1).

## 5. Como saber se a medida do erro é confiável

O classificador é um programa determinístico, mas ele pode **errar o rótulo**. Três conferências simples, antes de confiar:

1. **Nos erros conhecidos:** em passos que erraram na produção, o classificador, aplicado ao que foi reproduzido, dá o
   mesmo rótulo? (sensibilidade).
2. **Nos passos limpos:** ele **não** dá o rótulo onde não houve erro? (falsos positivos).
3. **Leitura humana de uma amostra:** você lê, por exemplo, 30 casos de cada braço sem saber qual braço é, e o rótulo
   do programa é comparado com o seu. A concordância (o kappa) entre dois leitores é a mesma lógica que o projeto já usa
   nos degraus de revisão.

**Dois cuidados que enganam:**

- **A memória pode fazer o agente evitar a situação** (escrever o código de outro jeito, sem `json`) **e a resposta piorar**.
  Sem erro, mas com qualidade pior. Por isso a qualidade da resposta é uma guarda (plano da fase 1, §5).
- **O erro só é possível se o agente chega ao passo que precisa dele.** Se numa execução ele falha antes por outro motivo,
  o erro X não podia acontecer. A taxa certa é **por oportunidade** (execuções que chegaram a um passo que usa o objeto da
  lição), não por execução. É o que o replay de passo dá de graça: cada contexto congelado é uma oportunidade.

## 6. O que se coleta no fim

Para cada par (agente, memória), uma tabela com **esta forma**:

| Medida | Como se escreve | Por quê |
|---|---|---|
| taxa do erro, sem e com memória | proporção com intervalo de confiança (Wilson, §3) | a pergunta central |
| redução relativa e absoluta | com intervalo de confiança | "quanto"; a absoluta vira "erros evitados por 1.000 execuções" |
| número a tratar | `1 ÷ redução absoluta` | a leitura mais direta |
| tokens e tempo por execução | **mediana**, p90 e intervalo por bootstrap | custo e tempo têm cauda longa: a média mente |
| passos por execução | mediana e média | eficiência |
| outros erros | taxa, com × sem memória | "não criou outro" |
| qualidade da resposta | estrutural, presença e leitura cega | guarda |

**O que é o quê, sem mistério:**

- **Média e mediana.** A média soma tudo e divide; a mediana é o valor do meio. Para tokens e tempo, algumas execuções
  enormes puxam a média; a mediana mostra o caso típico. Reportam-se as duas.
- **Erro-padrão.** O quanto a média (ou a taxa) mudaria se você repetisse o experimento inteiro. Para uma taxa `p` em
  `n` execuções, é `√(p·(1−p)/n)` (Miller, 2024, Eq. 2). Quanto maior `n`, menor.
- **Intervalo de confiança de 95%.** A faixa em que a verdade provavelmente está. Se o intervalo da **diferença** não
  inclui zero, a diferença não é sorte.
- **Bootstrap.** Sortear, com reposição, as próprias execuções muitas vezes e ver quanto o resultado varia. Dá o
  intervalo sem fórmula, e funciona para a mediana.
- **Pareado.** Comparar o mesmo input nos dois braços, em vez de dois grupos diferentes. Tira a variação "este input é
  difícil" da comparação (Miller, 2024, §4.2).

## 7. O que é Holm

> **Atualização de 13/11/2026.** Na fase 1 a família tem **três pares** (não cinco). A explicação mais simples, com a moeda, o
> `p` e a ideia do "melhor de k tentativas", está no §14 do [plano da fase 1](plano-fase-1-a-memoria-mitiga-o-erro.md); a
> verificação contra a fonte, em [`literature/holm-1979.md`](literature/holm-1979.md). O texto abaixo vale como visão geral.

O problema: se você faz **vários testes** (cinco pares de agente e memória), a chance de um deles dar "significativo" **só
por sorte** sobe. Com cinco testes e limite de 5% em cada, a chance de pelo menos um falso positivo passa de 20%.

**Holm** (1979) é uma regra para corrigir isso e manter em 5% a chance de **algum** falso positivo na família inteira.
Funciona assim:

1. Ordene os valores de `p` do menor para o maior.
2. Compare o menor com `5% ÷ 5 = 1%`; o seguinte com `5% ÷ 4 = 1,25%`; depois `5% ÷ 3`, `5% ÷ 2` e `5% ÷ 1`.
3. Vá subindo enquanto cada `p` for **menor** que o seu limite. No primeiro que **não** for, pare: esse e os maiores não
   são significativos.

Exemplo com cinco pares, `p` = 0,004; 0,011; 0,03; 0,04; 0,20.

| ordem | `p` | limite | resultado |
|---:|---:|---:|---|
| 1 | 0,004 | 0,0100 | significativo |
| 2 | 0,011 | 0,0125 | significativo |
| 3 | 0,030 | 0,0167 | **não**: para aqui |
| 4–5 | 0,04; 0,20 | — | não |

Dois dos cinco pares passam. A correção mais simples, a de Bonferroni, usaria 1% para todos e só deixaria passar o
primeiro. **Holm nunca é menos potente que Bonferroni**, e vale sem supor nada sobre a relação entre os testes. Por isso o
plano o usa.

## 8. A volumetria: o que já existe, e o que pedir à máquina 2

Olhei a pasta da base 3. **A maior parte já existe**, e o que falta é pouco:

| O que preciso | Onde já está | Estado |
|---|---|---|
| execuções do papel, por mês (**o denominador**) | `taxas_por_papel_mes.csv`, gerado por `executar.py taxas` ou `relatorio` (uma linha por papel e mês: execuções, passos, erros) | já gerado em 15/10 na rodada `609c…`; a versão por papel e mês é de 21/10 e **precisa ser rodada de novo** |
| tokens e passos por execução, por papel, com e sem erro | `taxas_custo_por_papel.csv` (mediana, média e p90) | já gerado |
| erros de cada **memória** por papel e mês | a tabela `erros_lidos` da mineração do sandbox (uma linha por erro, com a memória, o papel e o mês) | existe no ambiente; **falta a contagem por memória × papel × mês** |

**O que falta é uma conta pequena:** para cada (memória, papel, mês), quantas **execuções distintas** tiveram o erro,
dividido pelas execuções do papel naquele mês. Com ela, a incidência `π` de cada par e o número de inputs disponíveis para
o conjunto gatilho saem de imediato.

**Duas formas de pedir, e eu recomendo a primeira:**

1. **Um script curto** (cerca de 20 linhas, só pandas), que lê esses dois arquivos e escreve **uma tabela só de
   contagens**. É determinístico, repete o resultado e não passa por um LLM.
2. **Um prompt** para o agente da máquina 2 fazer a mesma conta. Funciona, mas pode variar de uma vez para a outra.

Para eu escrever a linha de comando completa, preciso do **nome da pasta da rodada** (a última, onde está o
`manifesto.json`) e de **onde está a tabela `erros_lidos`**. Não vou inventar.

## 9. Os artigos citados: o que são e o que levamos

Nenhum foi lido por você. O nível de cada um está na última coluna (📝 resumo, 🔎 texto completo por um agente).

| Artigo | O que é | O que levamos | Nível |
|---|---|---|---|
| **Miller (2024)** — *Adding Error Bars to Evals* | estatística de avaliação de LLMs | erro-padrão, intervalo, pareamento, quantas repetições (§3 do plano geral) | 🔎 ([fichamento](literature/miller-2411.00640.md)) |
| **Holm (1979)** | regra para vários testes | o §7 acima | 📝 só referência |
| **Barnett et al. (2005)** — regressão à média | selecionar casos extremos engana: eles tendem ao meio sozinhos | o braço sem memória rodado de novo nos mesmos inputs | 📝 |
| **Bowyer et al. (2025)** — *Don't use the CLT…* | com poucas centenas de casos, a fórmula normal subestima a incerteza | usar intervalos exatos ou bayesianos em amostras pequenas | 📝 |
| **Atil et al. (2024)** — não determinismo | mesmo com temperatura zero o LLM varia entre execuções | repetir cada input `K` vezes | 📝 |
| **Mishra e Mishra (2026)** — MERIT | como medir memória em agente que executa tarefas: utilidade por dólar, taxa de uso da memória, dano | quase toda a lista de medidas | 📝 (página do arXiv, por um modelo pequeno) |
| **Gloaguen et al. (2026)** — *Evaluating AGENTS.md* | sem contexto × gerado por LLM × escrito por humano; sucesso, passos e custo | o desenho dos braços | 📝🔎 (página do arXiv) |
| **SkillsBench (2026)** | lições curadas ajudam; as autogeradas não; algumas tarefas pioram | medir a **robustez entre inputs** | 📝 (resumos) |
| **Ma et al. (2025)** — DoVer · **Zhu et al. (2025)** — AgentDebug | intervir no passo da falha e continuar dali | o replay de passo (§4) | 📝 |
| **Guo et al. (2024)** — StableToolBench | repetir avaliações sem depender de ferramenta real (cache e simulador) | congelar o mundo (§4) | 📝 |
| **Xiong et al. (2025)** · **Yuan et al. (2026)** | memória com erro se propaga; separar "não chegou" de "o agente ignorou" | o braço de dano; a taxa de uso da memória | 📝 |
| **Kapoor et al. (2024)** · **Erol et al. (2025)** · **Yao et al. (2024)** | custo e acerto juntos; custo por acerto; `pass^k` | a compensação e a estabilidade | 📝 |

Os fichamentos completos que faltam, **em ordem de prioridade**: MERIT, Gloaguen e SkillsBench (os que sustentam as
medidas e as hipóteses). A fila está em [`literature/README.md`](literature/README.md).
