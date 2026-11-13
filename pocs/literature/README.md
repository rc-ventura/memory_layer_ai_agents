# literature/ — fichamentos que sustentam o experimento do degrau 4

Fichamentos dos artigos em que o [plano do experimento](../plano-experimento-validacao-memorias.md) se apoia. É o
equivalente, para as POCs, da pasta [`analysis/literature/`](../../analysis/literature/README.md), que sustenta a análise
do trace. A regra é a mesma: **o que o plano afirma com base num artigo tem de passar por um fichamento que diz o que o
artigo de fato diz.**

## Nível de leitura — importante

Na escala de [`papers/reading-queue.md`](../../papers/reading-queue.md):

- **📝** — verificação bibliográfica (título, autores, ano, resultado principal), sem ler o texto.
- **🔎** — texto completo lido por um agente, com extração dirigida por perguntas. Mais forte que 📝 e **não é** ✅.
- **✅** — o Rafael leu.

Todo fichamento desta pasta nasce **🔎, com o ✅ pendente**, e diz isso no topo. Não colapsar em "lido" em nenhum
entregável. Quando o Rafael ler, o fichamento troca a marca e registra o que ele corrigiu.

**Método:** `curl` no PDF, numa pasta isolada fora do repositório, e `pdftotext -layout`; o texto extraído é lido
inteiro, com os apêndices. Autoria, arXiv ID e data são conferidos contra a primeira página do próprio PDF. No
fichamento, o que é derivação ou leitura do agente vai marcado **[derivação minha]** ou **[inferência minha]**, e o que é
do paper traz a página.

## Índice

| Arquivo | Paper | Nível | Para que serve no plano |
|---|---|---|---|
| [`miller-2411.00640.md`](miller-2411.00640.md) | **Miller** — *Adding Error Bars to Evals*, Anthropic (arXiv, 2024) | 🔎, **falta o ✅** | A estatística do plano: decomposição da variância (quantas repetições por tarefa, e por que muitas tarefas), pareamento por tarefa, erro-padrão agrupado e a fórmula de tamanho de amostra (§9 e §12 do plano). |
| [`holm-1979.md`](holm-1979.md) | **Holm** — *A simple sequentially rejective multiple test procedure* (Scandinavian J. of Statistics, 1979) | 📝 do artigo (texto não obtido); fonte secundária lida inteira (Abdi, 2010); **falta o ✅** | A correção para vários pares (§9 e §12 do plano da fase 1): o procedimento, o que a fonte confirma e a opção do placebo que a verificação derrubou. |

## Correções que estes fichamentos produziram no plano

1. **Miller (12/11/2026).** O plano citava o Miller para "o erro-padrão agrupado: tamanho efetivo dividido por
   `1 + (k − 1)·ρ`". A fórmula **não está no paper**: é consequência algébrica da decomposição de variância dele (§3.1).
   E o erro-padrão agrupado do paper (Eq. 4) é para grupos de perguntas **diferentes**; as repetições da mesma tarefa
   são reamostragem, e o paper manda calcular a incerteza sobre a **média por tarefa**, nunca sobre as execuções
   empilhadas. Corrigido no §9.1 e no §12 do plano.
2. **Miller (12/11/2026).** O "3 a 5 repetições por tarefa" do plano **não é um número do paper**: o paper dá o critério
   (`E[σ²]/K ≪ Var(x)`), e o piloto escolhe o `K`. Corrigido na tabela do §0 e no §9.1.
3. **Holm (13/11/2026).** A explicação que eu tinha dado da "opção A" do placebo (testar o placebo só nos pares aprovados,
   com o Holm continuando em três testes e sem custo) **não se sustenta**: a comparação com o placebo é outro conjunto de testes,
   e controlar o erro da família nesse caso é o problema dos portões (*gatekeeping*), que não é trivial. Retirada do
   que ia para o plano; a alternativa é o teste de interseção-união por par, com Holm entre os pares (a confirmar em Berger, 1982).

## Na fila — citados no plano, ainda sem fichamento

Estes artigos sustentam hipóteses ou decisões do plano e ainda não têm fichamento. O nível real de cada um, hoje:

| Paper | O que se sabe | Em que ponto do plano pesa |
|---|---|---|
| **Gloaguen et al. (2026)**, *Evaluating AGENTS.md* (arXiv:2602.11988) | Lido em 12/11 pela página do arXiv por um modelo pequeno (WebFetch), que respondeu a perguntas dirigidas sobre desenho, medidas, estatística e limites. **Não** foi lido pelo método do `pdftotext`, então fica entre 📝 e 🔎. | Hipóteses 1, 2 e 8; o desenho do experimento; a estratificação do §12. **É o primeiro candidato a fichamento.** |
| **SkillsBench (2026)** (arXiv:2602.12670) | Só os resumos da v1 e da v4 (📝). A frase sobre lições autogeradas está no da v1 e não no da v4. | Hipótese 8 (revisada × autogerada). **Ler o método antes de confiar.** |
| **Mishra e Mishra (2026)**, *When Does Memory Help? A Cost-Aware Evaluation of Long-Term Memory in Tool-Using LLM Agents* (arXiv:2609.05441) | Lido em 12/11 pela página do arXiv por um modelo pequeno (definições de utilidade marginal por dólar, taxa de uso da memória e dano; desenho, estatística e limites). **Não** foi lido pelo método do `pdftotext`. | A fase 1 inteira: como medir eficácia e custo de memória em agente que executa tarefas. **Candidato a fichamento, antes de fixar a qualidade da resposta final.** |
| **MemUse** (2026), *Delivered, Not Used: Evaluating Agent Memory at Its Point of Use* (arXiv:2611.01718) | Busca web de 13/11 (📝): 8.000 episódios SWE-bench Verified, três sistemas de memória; resolve rate a **0,4 p.p. do baseline sem memória**; bootstrap pareado por tarefa; juízo de ponto de uso (relevância → uso → efeito). | A adesão à lição do §5 da fase 1 (a mesma separação "chegou × foi usada × teve efeito") e a expectativa para um resultado nulo. **Segundo candidato a fichamento, depois do MERIT.** |
| **VibeMemBench** (2026) (arXiv:2609.23570) | Busca web de 13/11 (📝): memória em tarefas de código em repositórios reais; injeção direta sobe resolução só +1,1 a +4,5 p.p.; 11 de 12 combinações solver × sistema **não batem o baseline sem memória**. | Justifica o braço placebo e a régua econômica (`e_min`): efeito de injeção pequeno é o cenário empírico esperado. |
| **DolphinBench** (2026) (arXiv:2609.24971) | Busca web de 13/11 (📝): cada tarefa só entra no benchmark se passa **com** a história e falha **sem** ela (verificação por oracle); custo e latência reportados junto da acurácia. | O análogo publicado da **taxa de reprodução** do conjunto gatilho (§4.3 e porta zero da fase 1): o erro precisa existir sem memória para o teste valer. |
| **Xiong et al. (2025)**, *How Memory Management Impacts LLM Agents* (arXiv:2505.16067) | Só o resumo (📝). | Memória que propaga erro; o gate; o braço autogerado. |
| **Kapoor et al. (2024)**, *AI Agents That Matter* (arXiv:2407.01502) | Só o resumo (📝). | Ler custo e acerto juntos; a linha de base barata. |
| **Yao et al. (2024)**, *τ-bench* (arXiv:2406.12045) | Só o resumo (📝). | A métrica `pass^k` (estabilidade, §8.4). |
| Os demais do §"Referências" do plano | Verificação bibliográfica por busca (📝), exceto os marcados † | — |

Fichamento só entra aqui quando o artigo for lido pelo método acima.
