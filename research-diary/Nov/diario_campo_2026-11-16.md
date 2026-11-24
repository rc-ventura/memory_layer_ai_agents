# Diário de Campo — Rafael Coelho Ventura

## Semana de 16/11 a 20/11/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 16/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Segunda de volta ao resíduo da base 3, com dois grupos ainda sem destino. O primeiro é o `invalid syntax`, 75 erros do balde "causa não identificada". É a mensagem do próprio Python, e ela aparece quando o código que o agente manda executar não é Python válido. Nesses casos, o código trazia a tag `<code>` ou `</code>` escrita como texto dentro dele: o agente esquecia de fechar um bloco, abria outro, o harness juntava os dois e o interpretador acusava erro numa linha de texto no meio do código. A biblioteca do agente reproduz esse mecanismo. A leitura dos casos foi feita no ambiente da base em duas etapas; como na segunda ainda não estava claro qual era o marcador de erro, uma terceira etapa foi só para isso. O grupo se dividiu em dois destinos. **17 casos vão para `H_bloco_code`** (harness, bloco mal fechado): o código traz a tag como texto (6 com a tag na própria linha do erro; em 13, a resposta final vem depois da linha que quebra). **Os outros 58 ficam no resíduo**, em duas partes. 22 são erros comuns de código: 17 deslizes de Python que o agente corrige sozinho em 11 casos, 4 com aspas ou caracteres fora do ASCII e 1 código cortado. Os outros 36 são texto ou rótulo, outra linguagem, ou marcador sem a tag. Têm forma reconhecível, mas nenhuma regra os separa sem leitura: a regra de texto solto pega 0 dos 75, a versão relaxada pega 23 (10 deles de outra categoria), a da primeira linha pega 2 dos 53 lidos e a da string aberta pega 1 dos 53 e 1 dos 22. Esses 36 só se reabrem se a extração trouxer a resposta crua do modelo antes do parser.

O segundo grupo é o grupo A: 86 erros de valor numérico que chegou como texto. Depois de três rodadas de leitura no ambiente da base, o critério ficou assim: se o contrato da ferramenta diz texto com clareza e o agente trata como número, é memória; se o contrato promete um tipo e a ferramenta entrega outro, ou se o contrato é ambíguo, é harness. Pelo critério, **49 vão para `H_contrato_ferramenta`** e **37 para `U_tipo_retorno`**. Os 49 vêm de duas ferramentas de correção monetária que declaram `float` e devolvem texto (43 e 6); em 48 deles a variável recebeu direto o retorno da ferramenta. Os 37 são de ferramentas com `Returns: str` ou sem tipo declarado, em que o agente não converteu: 22 de cinco ferramentas, 1 de uma ferramenta de envio de planilha, 6 de três ferramentas que não estavam no levantamento inicial, e 8 em que o valor veio de arquivo ou JSON (5), foi escrito como texto pelo próprio agente (2) ou não deu para ver (1). Antes de fechar, deixei de lado a opção de manter os 49 como memória: a ferramenta contradiz o contrato que o próprio agente lê, e essa pista ficaria só no texto. Como o contrato dessas duas ferramentas não aparece no material que a base 3 exporta, a evidência vem de uma lista fixa com os nomes delas, que precisa ser conferida a cada extração nova. Fiquei com a regra do Ajuste 39 escrita no código: texto numa conta vai para harness quando há evidência de contrato descumprido, e para memória no resto. A regra de cada grupo é aprovada antes de virar código, e foi o que fiz nesse dia.

**Reflexão:** A mensagem do Python não diz quem errou. O mesmo `invalid syntax` pode ser do agente, que esqueceu de fechar um bloco, ou do harness, que colou dois blocos. Só o caso cru separa os dois. No grupo A, a pergunta útil foi quem prometeu o quê: se a ferramenta promete número e entrega texto, o erro não é do agente.

**Decisão/próximo passo:** Decisões de 16/11. (1) `invalid syntax`: 17 para `H_bloco_code` (harness); 58 ficam no resíduo, e os 36 sem forma separável só se reabrem com a resposta crua do modelo. (2) Grupo A: 49 para `H_contrato_ferramenta` e 37 para `U_tipo_retorno`, pelo critério de contrato descumprido. Próximo passo: rodar o Ajuste 39 no ambiente da base.

**Tags:** residuo, invalid-syntax, grupo-a, contrato-ferramenta, texto-numa-conta

---

## 17/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Rodada do Ajuste 39 no ambiente da base (rodada `c1e1b338fe6b9cd4`). Dos 49 que decidi ontem para o harness, 46 entraram em `H_contrato_ferramenta`; os outros 3 ainda preciso conferir por que não entraram. Os 37 para `U_tipo_retorno` bateram com o previsto, e o resíduo caiu de 420 para 337. O livro-razão dos Ajustes 34 a 40 guarda a regra e a rodada.

O segundo assunto do dia foi o bloco de código mal fechado, que tinha ficado em aberto. Havia três opções. Escolhi a primeira, com a recomendação que fiz: todo erro de sintaxe com a tag `<code>` ou `</code>` no código vai para `H_bloco_code`, nas bases 1 e 3. As outras duas foram recusadas. Uma era mandar os 17 para a memória `U_texto_solto`, mas a orientação "escreva só Python" não resolve um bloco que o harness colou. A outra era mandar só os 17 da base 3 para o harness, o que daria dois destinos ao mesmo erro: na base 1, o mesmo erro (23 casos, de outubro de 2025) já estava como memória.

O motivo para o harness: a regra do harness, aplicada à resposta do modelo, reproduz o código que falhou em 23 de 23 casos. Cada erro vem logo depois de outro erro do protocolo ou do mesmo bloco mal fechado, e o agente repete e não se recupera (17 de 23 na base 1; 13 de 14 na base 3). Pelo critério que fixamos, esse padrão é evidência de falha do harness, e por isso os erros vão para `H_bloco_code`. O custo é aceito: muda número publicado da base 1, com `U_texto_solto` caindo de 33 para 10 e `H_bloco_code` subindo de 33 para 56.

**Reflexão:** A rodada confirmou a conta, mas quem decidiu foi a leitura dos casos. Um bloco mal fechado não é coisa que a memória do agente conserta, porque quem colou o bloco foi o harness.

**Decisão/próximo passo:** (1) Ajuste 39 no ambiente: 46 de 49 para harness, 3 a conferir. (2) Bloco mal fechado: opção 1 aprovada, `H_bloco_code` nas bases 1 e 3. Próximo passo: rodar o Ajuste 40 no ambiente da base.

**Tags:** residuo, ajuste-39, bloco-code, livro-razao

---

## 18/11/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Rodada do Ajuste 40 no ambiente da base (rodada `dbd40c0f4d3604b1`). O resíduo da base 3 fecha em 314 erros, em 92 padrões, 16 deles recorrentes; é 1% dos 30.141 erros da base. Os 314 são 270 de "causa não identificada" e 44 de "sintoma não reconhecido" (este último decidido em 13/11). Dos 270, 215 são os que li hoje e 55 são do `invalid syntax`. Ontem eram 58; a diferença de 3 deve ser dos casos que o Ajuste 40 levou para o harness, e ainda preciso conferir.

Li os 215 em duas leituras completas no ambiente, com um só leitor. Eles se agrupam assim: indexação recusada (34), barra invertida dentro de f-string (38), construtor de DataFrame (19) e outros 124. Depois fiz uma releitura às cegas, com o mesmo modelo, para medir a estabilidade, não para decidir nada: ele repetiu a categoria em 4 de 15 casos da parte A e em 2 de 15 da parte B. Entre as duas leituras, `U_tipo_retorno` caiu de 62 para 1 e `H_contrato_ferramenta` de 23 para 1. A conferência de forma também não bastou. O trecho de evidência costumava ser a primeira linha do código, que não sustenta a categoria; 75 erros foram marcados como "mesma causa" de uma unidade, mas só 11 dos 124 têm unidade candidata; e nenhum dos 38 erros de barra invertida se reproduziu na verificação de sintaxe do Python.

**Por que os 215 ficaram no resíduo, grupo a grupo.** Os 215 são o que sobrou do balde de 376 depois de tirar o grupo A (86) e o `invalid syntax` (75), decididos em 16/11. Cada parte ficou por um motivo diferente. O grupo B (barra escrita literalmente pelo agente, concentrada no papel de contestação em julho e agosto) ficou como hipótese em 14/11, porque é volume de um papel novo e o prompt desse papel ainda não tinha sido lido; depois apareceram 38 casos de barra dentro de f-string, mas nenhum se reproduziu com a verificação de sintaxe do Python. O grupo C, o de maior custo (3,37 milhões de tokens, 54 execuções, 9 meses, com o agente se corrigindo em só 33% dos casos), teve uma primeira leitura só com categorias genéricas, e a hipótese de texto em inglês deixado passar pela regra de texto não ganhou sinal suficiente. D e E não se confirmaram ou ficaram inconclusivos, e as sacolas e os casos de um mês têm volume baixo e nenhum mecanismo visível. A leitura de 18/11 não separou nada porque o sinal que testei, a exceção final `AgentExecutionError`, estava em todos os 270 erros do resíduo: cobertura de 100%, precisão entre 1,1% e 7%. Um sinal que aparece em tudo não decide nada. Por isso o critério que fixamos antes de ver os resultados manda ficar no resíduo.

**Por que as leituras não ficaram estáveis.** A releitura às cegas, com o mesmo modelo, repetiu a categoria em 6 de 30 casos (4 de 15 na parte A, 2 de 15 na parte B). Entre as duas leituras, `U_tipo_retorno` foi de 62 para 1 e `H_contrato_ferramenta` de 23 para 1: o leitor não encontra um mecanismo fixo e cria categorias novas a cada leitura. As evidências citadas costumam ser a primeira linha do código, que não é a causa; só 11 dos 124 "outros" têm unidade candidata; e os 75 marcados como "mesma causa" não se confirmaram. Não há um segundo leitor independente para esse conjunto, então não temos medida de concordância entre leitores. A hipótese que me parece mais provável, e que ainda não está verificada, é que a causa esteja antes da última linha: no passo em que o agente montou o código ou no que a ferramenta devolveu. Para confirmar, é preciso olhar o passo anterior de cada caso. Uma ressalva de números: o grupo B aparece com 36 casos em 14/11 e 38 de barra em 18/11; a contagem foi refeita sobre outra rodada, então não é o mesmo conjunto.

**Reflexão:** Este foi o dia em que mais precisei aceitar "não há regra para isso". Fechar o resíduo sem regra nova só vale porque o critério foi fixado antes de ver o resultado. Se eu escolhesse uma categoria depois dos números, estaria empurrando o resíduo para baixo sem explicar nada.

**Decisão/próximo passo:** Os 215 ficam no resíduo, cada um com o motivo registrado, porque nenhuma categoria teve sinal observável por script. Hipóteses abertas, não achados: (1) "lista fora do tamanho": 22 casos na primeira leitura e 18 na segunda, em 6 meses ou mais, o padrão mais estável; (2) "Número inválido: deve conter n dígitos": 23 erros, 19 execuções, um mês, em que a primeira leitura culpou a ferramenta e a segunda o agente (20 de 23); só uma leitura humana desses casos separa as duas. Reabro se algum método passar na releitura às cegas e der sinal que separe um subgrupo. Próximo passo: integrar a PR #43 à `main`.

**Tags:** residuo, base-3, fechamento, bloco-code, causa-nao-identificada, criterio-previo

---

## 19/11/2026

**Tipo:** implementação — **Sub-atividade:** transversal / 2.2 — **Canal:** pessoal

**Registro objetivo:** A PR #43 foi integrada à `main` (merge `c9fcf31`). Ela traz a skill de mineração do resíduo, a auditoria independente, o roteiro de leitura de casos, as regras dos Ajustes 34 a 40, o livro-razão e os registros de decisões de 11/11 a 18/11. Os itens 5 do roadmap da base 3 e 8 do roadmap transversal já tinham sido marcados como fechados no commit de 18/11 (`d57792b`); a PR apenas levou essa mudança para a `main`.

**Reflexão:** O resíduo começou a mineração em 565 erros e fechou a semana em 314. Os 215 que sobram são a parte do que ainda não conseguimos explicar, e isso precisa ficar visível no registro, não escondido num balde.

**Decisão/próximo passo:** Nenhuma. A PR #44 segue aberta, sem alteração nesta semana.

**Tags:** residuo, pr-43, merge, roadmap

---

## 20/11/2026

**Tipo:** observação livre — **Sub-atividade:** transversal — **Canal:** pessoal

**Registro objetivo:** Sexta sem commit no repositório, e a PR #44 não teve alteração nesta semana. Aproveitei o dia para reler o resumo de trabalho do desenho da fase 1 (o arquivo `resumo-design-fase-1-rascunho.md`, que está em Downloads) e fazer a síntese dele abaixo, para ter o experimento inteiro num lugar só. É um rascunho de notas minhas, validado em conversa em 14/11, e não é documento oficial.

**Síntese do desenho da fase 1.** A pergunta tem duas partes: a memória que já temos mitiga o erro que ela descreve quando é injetada num agente real, e a que custo? A primeira parte se mede pela eficácia (a redução relativa da taxa de erro); a segunda, pelo custo líquido em tokens. Uma régua calculada, `e_min = c / (π·s)`, liga as duas: a memória só se paga se evitar pelo menos essa fração dos erros, sendo `c` o custo da injeção, `π` a taxa de erro de hoje e `s` o custo do passo que erra. O desenho parte de seis premissas. O agente de hoje não é o de agosto (o erro de `pandas` caiu de 49% para 13% de julho para agosto), então todos os números da régua são re-medidos. O agente é estocástico, então cada input roda `K` vezes. O erro tem mecanismo, o que cria um gatilho: inputs que já erraram têm mais chance de errar de novo. Quem define o erro também o mede, então a regra precisa de guardas. A observação é a execução inteira, não o passo, porque os passos não são independentes. E "compensa" é conta de população, o que exige uma amostra sorteada da produção além do gatilho. Os braços são: sem memória (referência), placebo (texto verdadeiro, do mesmo tamanho e sem relação com a tarefa, para separar "a lição funciona" de "prompt maior"), com memória (a lição revisada) e autogerada (ensaio da fase 2, fora do veredito). As medidas são a taxa de erro por braço, a eficácia, o custo líquido e o tempo, que só descreve e não entra como critério. As guardas contra o erro que apenas migra para um padrão vizinho, o dano em outros erros, a perda de oportunidade e a leitura humana cega ao braço.

**Etapas e estado.** A volumetria já está feita sobre a base 3 e não é recalculada. Ela deu o `π` histórico e o custo do passo com erro, e triou os pares: entram JoogleAnalytics (`pandas` e imports) e ContestacaoCivel (funções proibidas); fica como candidata ContestacaoCivel com retorno como texto; ficam fora RoteadorCivel, porque a conta não fecha, e CalculoTrabalhista, que passa na viabilidade e é reprovado no orçamento; RespostaBacen fica só para verificação de dano. Depois vem a sonda (estágio 0), que roda inputs do gatilho sem memória para perguntar se o erro ainda existe; ela trabalha em lotes, e cada lote limpo só aperta um teto para `p`. Se o teto ficar baixo demais, o par fecha como "não testável hoje". O piloto (estágio 1) remede `π`, `p` e `ρ` (o quanto o resultado depende do input, que decide quantos inputs e quantas repetições rodar), mede o `s` de hoje, valida o classificador contra rótulos humanos e escreve os placebos. O pré-registro congela tudo por hash antes de qualquer dado do confirmatório. O confirmatório (estágio 2) roda os três braços intercalados em ordem sorteada, com rótulos cegos ao braço, eficácia pareada por input, correção de Holm e as guardas, e termina em um dos sete desfechos por par.

**Pendências.** Ainda estão em aberto: como a memória entra na plataforma (formato e posição, que só se fecham com a leitura do framework); se o trace é capturado localmente ou lido do banco de dev; se as ferramentas leem ou escrevem, o que decide se repetir uma execução tem efeito colateral; fixar a versão do modelo; e garantir que cada repetição roda em sessão nova. Tudo roda dentro do ambiente da empresa, e só saem contagens e hashes. Na literatura, Miller tem fichamento feito, mas falta minha leitura; Berger & Hsu precisa ser lido antes do pré-registro; o orçamento de execuções ainda depende da aceitação do Rafael, e o limite de "fração de inputs que pioram" deve ser fixado no piloto.

**Decisão/próximo passo:** Nenhuma decisão nova. O próximo passo do experimento continua o piloto e o pré-registro, como ficou registrado em 13/11.

**Tags:** sem-atividade, degrau-4, fase-1, resumo-desenho

---
