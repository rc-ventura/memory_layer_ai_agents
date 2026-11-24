# Diário de Campo — Rafael Coelho Ventura

## Semana de 09/11 a 13/11/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

*Entradas desta semana reconstruídas a partir dos commits das PRs #43 e #44.*

---

**Contexto da semana, para quem lê de fora.** O projeto analisa milhares de erros que agentes de IA cometeram em tarefas reais (o "trace" — o registro passo a passo de cada execução) para extrair "memórias": lições curtas que, injetadas no agente, evitariam que ele repetisse o erro. Um pipeline determinístico classifica cada erro num destino — vira memória, é problema da infraestrutura, é defeito do ambiente de execução, etc. O que nenhuma regra consegue explicar cai no **resíduo**. Esta semana teve duas frentes: (1) a mineração do resíduo da base 3 — 565 erros inexplicados que fomos tirando do limbo um grupo por vez, escrevendo uma regra nova para cada grupo que entendemos; (2) o desenho do experimento que vai testar, com agentes reais, se uma memória de fato impede o erro — a etapa que tira o projeto do "achamos a lição" para o "a lição funciona".

## 09/11/2026

**Tipo:** implementação — **Sub-atividade:** transversal / 2.2 — **Canal:** pessoal

**Registro objetivo:** Segunda foi dia de fechar pontas e abrir a frente nova. De manhã, limpeza do repositório: apaguei um script de figura que só servira à apresentação para o Itaú, movi 13 scripts de uso único para uma pasta `historico/` (continuam versionados, mas fora do caminho do dia a dia) e fiz merge da PR da semana anterior, que fechava a revisão das memórias do sandbox — a última delas, a memória E ("funções proibidas"), passou no portão de qualidade depois de relidas as 2 discordâncias entre os dois leitores. À tarde, abri a frente da semana: a **mineração do resíduo da base 3**. Criei o instrumento inteiro — a skill `mineracao-residuo` com auditoria independente (um script que relê os dados crus sem usar o pipeline, para conferir se os números batem) e o roteiro de leitura de casos. Também gravei no AGENTS.md a regra do "ambiente da base": o agente que roda onde os dados moram não pode editar os arquivos que definem a versão do pipeline para contornar um erro — toda mudança volta ao repositório no mesmo dia.

**Reflexão:** A regra do ambiente da base parece burocracia, mas é o que mantém a reprodutibilidade: se o agente remoto "consertasse" o pipeline localmente, o hash registrado deixaria de corresponder ao código real e nenhuma rodada seria confiável.

**Tags:** residuo, base-3, mineracao, sandbox, degrau-3, limpeza, reprodutibilidade

## 10/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Primeiro dia de ataque ao resíduo. O resíduo agrupa erros em "padrões" pela mensagem, e o primeiro problema era o próprio agrupador: endereços de memória do tipo `0x7f3a...` mudam a cada execução, então o mesmo erro virava um padrão diferente em cada caso — um `LayoutError` aparecia quebrado em 13 padrões. Escrevi um script de simulação, testei duas correções e apliquei a que funcionou: mascarar o endereço antes de agrupar e cortar o texto do padrão só depois da máscara (antes o corte caía em lugares diferentes conforme o tamanho dos números, e "3 rows" versus "12 rows" viravam padrões separados). Isso foi o **primeiro ajuste da semana**: uma rodada nova do pipeline e os 120 padrões caíram para 111 — menos padrões, mesmos erros, agrupamento mais honesto. À tarde, investiguei o maior grupo do resíduo: 54 erros com cheiro de infraestrutura (conexão, política de conteúdo, ferramenta). Um agente (sem provider definido) leu os 54 casos no ambiente da base e o resultado dividiu o grupo em três destinos. O primeiro fechou ainda no dia: 33 erros eram **conexão perdida dentro de uma chamada a outro modelo de linguagem** — a rede caiu, não é culpa do agente. Escrevi a regra, rodei e o resíduo caiu de 565 para 532.

**Reflexão:** O ajuste da máscara é um bom exemplo de por que o resíduo existe: às vezes o erro inexplicado não é um fenômeno novo, é o instrumento de medida que estava quebrando o fenômeno em pedaços.

**Tags:** residuo, mascara, padroes, infra, conexao-perdida, agrupamento

## 11/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** O dia mais produtivo da semana — três grupos do resíduo fechados. Continuando o grupo de infra de ontem: 16 erros eram **ferramentas que falharam saindo do próprio contrato** (a ferramenta quebrou de um jeito que a documentação dela não prevê) — virou destino de infra/contrato, e o resíduo foi para 516. Sobraram 5 erros que pareciam "recusa do modelo por política de conteúdo"; a contagem mostrou que não era recusa coisa nenhuma — era **estouro do limite de tokens de entrada** (285 mil contra o teto de 272 mil) que a biblioteca rotula errado como política de conteúdo. Como o volume é baixo, esse padrão ficou "em observação" — um estado que renomeei hoje (antes se chamava "cobertura"): o erro continua no resíduo, é contado a cada rodada com o motivo escrito, e volta à fila se crescer. O terceiro grupo foi o mais interessante: 49 erros de **"Cannot assign to name"** — o agente tentava guardar um valor numa variável com o mesmo nome de uma ferramenta (`final_answer = {...}`), e o interpretador barrava para não apagar a ferramenta. Só acontece na base 3 — zero casos nas outras duas. Fui checar: o prompt padrão do framework **já proíbe** isso explicitamente ("não nomeie variável com nome de ferramenta"). Ou seja: o harness faz tudo certo — avisa, protege, explica — e o agente erra mesmo assim. Decisão: é erro do agente, destino "memória de reforço" (repetir a regra que ele ignorou), com alarme se o erro triplicar. Resíduo: **467 erros**.

**Reflexão:** O caso do nome de ferramenta é a essência do que o projeto procura: um erro que a instrução já cobre e o agente comete mesmo assim é o candidato perfeito para memória — mas reforço, não lição nova, porque a lição já existe e não bastou.

**Tags:** residuo, contrato-ferramenta, recusa-falsa, estouro-de-tokens, nome-de-ferramenta, memoria-de-reforco, em-observacao

## 12/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Dois assuntos grandes. O primeiro: 49 erros de sintaxe que é **Python válido mas que o interpretador do agente não implementa** — desempacotar dicionário com `{**x}`, o operador morsa `:=`, `global`, `nonlocal`, `raise` sozinho. Testei num sandbox local contra três versões da biblioteca: o interpretador recusa todos, do começo ao fim, e o prompt nunca avisa. O lado bom: o agente desiste da construção sozinho no passo seguinte em 46 de 47 casos. Isso virou mais uma regra — esses erros agora alimentam o inventário do sandbox (a lista de coisas que o ambiente não deixa fazer, que é material para memória), e a lição ganhou os consertos que eu testei de verdade. O segundo assunto é de método: criei o mecanismo de **re-entrada** — quando uma rodada nova do pipeline muda quais erros pertencem a uma memória já minerada, a memória volta à investigação. O script compara a "foto" tirada na época da mineração com o estado atual. Já na estreia ele achou um bug em si mesmo: 5 falsos positivos de "mudou de parte" que eram só `NaN != NaN` (vazio comparado com vazio contava como diferença). Corrigi. No fim do dia, medi o que sobrou do balde "sintoma não reconhecido" (44 erros em 9 grupos) para decidir o que valia investigar.

**Reflexão:** A re-entrada fecha um buraco do método: até aqui, uma memória minerada era tratada como terminada para sempre, mas o pipeline evolui — uma regra nova pode mudar a população de erros que a memória cobre, e ninguém perceberia. Agora o próprio sistema avisa.

**Tags:** residuo, sandbox, sintaxe-nao-suportada, re-entrada, metodo, nan, sintoma-nao-reconhecido

### 12/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.3 / 3.6 — **Canal:** pessoal

**Registro objetivo:** Em paralelo, abri a segunda frente da semana (PR #44): o desenho do **experimento do degrau 4** — a etapa em que paramos de só extrair memórias e passamos a testar se elas funcionam. Comecei documentando o SDK interno de memória da plataforma (transcrição anonimizada em `pocs/sdk-memory-docs/`) e analisando o que ele resolve e o que não resolve contra o nosso mecanismo — virou até uma pergunta nova nas open questions ("por que não usar o SDK interno?"). Depois escrevi o plano do experimento: para qualquer memória que chegou ao degrau 3 (revisada), medir se injetá-la reduz o erro e se compensa o custo em tokens. O desenho tem seis braços de comparação — sem memória, memória injetada de três jeitos diferentes, placebo e memória autogerada — e a fase 1 responde a pergunta mais simples e mais importante: **a memória mitiga o erro?**, rodando agentes reais com inputs reais.

**Tags:** pocs, degrau-4, experimento, sdk-memoria, fase-1, bracos, desenho

## 13/11/2026

**Tipo:** achado — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Fechei o balde "sintoma não reconhecido". Dos 44 erros que sobravam, decidi que só um grupo valia investigação: 13 erros de geração de PDF (o documento vinha com uma linha de tabela mais alta que a página). Li os 13 casos no ambiente e o resultado foi instrutivo: em 6 deles o agente simplesmente **abandona a ferramenta** e segue sem o documento; em 4 ele responde ao usuário logo depois do erro — candidato a falha silenciosa, o pior tipo, porque ninguém fica sabendo que o PDF não saiu. Decisão: o grupo fica no resíduo com uma **pista de harness** registrada (a ferramenta devia quebrar a linha sozinha, é culpa dela, não do agente), e nenhum dos 44 vira regra nova — o balde está fechado. Isso liberou o segundo balde, o maior: "causa não identificada", 376 erros. Medi a recorrência em 19 famílias de mensagem e a primeira leitura já apontou pistas que atravessam famílias: número escrito como texto concentrado num papel só, barra invertida escrita literalmente pelo agente num período específico (jul/ago), e 75 erros de `invalid syntax` que precisam de leitura.

**Reflexão:** O caso do PDF é o achado mais valioso do dia, apesar de não virar regra: mostrou que "o erro não se repete no passo seguinte" não significa "o agente corrigiu" — às vezes ele só desistiu, e a desistência é invisível. Essa distinção (corrigiu × contornou × largou) vai importar na hora de medir se as memórias funcionam.

**Tags:** residuo, pdf, falha-silenciosa, pista-de-harness, causa-nao-identificada, recorrencia, corrigiu-vs-desistiu

### 13/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.3 / 3.6 — **Canal:** pessoal

**Registro objetivo:** O experimento avançou de plano para desenho aprovado. Medimos a **volumetria** na base 3: quantas execuções têm o erro que cada memória cobre, por papel e por mês — é o número que decide se o experimento é viável (um erro raro demais não dá para medir efeito). O script ficou genérico: mede qualquer memória, minerada ou não, e acha sozinho qual rodada do pipeline tem os dados. Também medimos o custo de um passo com erro em tokens e duração — é o que a memória precisa economizar para "pagar" sua injeção. À tarde, a **fase 1 foi aprovada bloco a bloco** (8 blocos de desenho + 1 extra), mas não sem antes passar por uma revisão dura de uma auditoria do desenho: entrou "porta zero" antes do injetor (prova de que o ambiente está limpo), o replay virou etapa de triagem, trocamos "rodar até dar K erros" por amostra de tamanho fixo com intervalo de confiança, e o avaliador cego perdeu poder de veredito sem regra pré-registrada — tudo para o experimento não poder se enganar. Na literatura, entraram na fila MemUse, VibeMemBench e DolphinBench; o Miller já está fichado (por um agente — minha leitura ainda pendente). Terminei organizando `pocs/`: os 8 documentos soltos viraram uma pasta própria do experimento, numerada e com índice.

**Decisão/próximo passo:** Desenho da fase 1 aprovado. Próximo passo: piloto e pré-registro, antes de rodar com agentes reais.

**Tags:** pocs, degrau-4, fase-1, volumetria, custo-do-erro, desenho-aprovado, auditoria, literatura, pre-registro
