# Racionais do resíduo — o que sobra quando nenhuma regra reconhece o erro

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`/`X_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Para que serve este documento:** o mesmo papel do [`01-racionais.md`](01-racionais.md), só para o **resíduo**: os
erros que as regras determinísticas não explicam. Ele explica por que há dois baldes, como um erro do resíduo é
agrupado num **padrão**, por que a recorrência é contada pelo padrão, e o que reduz o resíduo. O roteiro para minerar o
resíduo numa base está em [`19-procedimento-residuo.md`](19-procedimento-residuo.md). Os casos de cada base estão em:
- base 1: [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.13;
- base 2: o mesmo doc, §1.16;
- base 3: [`../../2026-10-trace-law-flow-third/docs/02-relatorio-achados.md`](../../2026-10-trace-law-flow-third/docs/02-relatorio-achados.md) §5.

A história de cada regra que tirou erros do resíduo está no livro-razão
([`../../pipeline-entre-bases.md`](../../pipeline-entre-bases.md), Ajustes 1–4 e 8).

**De onde veio o texto (09/11/2026).** As §1 a §3 saíram do `01` §7 (Passo 2, "Os dois baldes de resíduo"; Passo 5,
item 2). O `01` guarda um resumo curto e o ponteiro para cá. As §4 e §5 juntam o que o livro-razão §4 aprendeu com a
base 2 (itens 2 a 5). É o passo "antes da skill" do roadmap transversal #8.

---

## 1 · Os dois baldes

Duas funções leem a mesma mensagem de erro, com papéis diferentes:
- o `classify()` dá o **sintoma** (família e assinatura, §2 do relatório). Ele não decide nada: descreve;
- o `submecanismo()` dá a **causa**, e é ela que leva o erro a uma unidade.

Cada uma tem a sua sobra, e cair em cada sobra diz uma coisa diferente:

| Balde | Classe (submecanismo) | Quando cai | O que pode significar |
|---|---|---|---|
| **Causa não identificada** (`X_causa_nao_identificada`) | **Código Python mal escrito** (`codigo_mal_escrito`) | erro de sintaxe ou de indentação em que a linha rejeitada não é texto colado, literal de texto nem retorno colado | código mal formado de verdade (parêntese, indentação, operador): ruído, até se provar que se repete |
| | **Erro conhecido, causa sem regra** (`causa_sem_regra`) | o `classify()` reconhece o sintoma, mas nenhuma regra de causa casa. Inclui o "Could not index" fora dos três padrões | o sintoma tem nome e a causa não: **candidato a regra nova** se recorrer (ex.: o argumento nomeado que não existe no `final_answer`, que virou regra em 25/09/2026 ao reaparecer na base 2) |
| **Sintoma não reconhecido** (`X_sintoma_nao_reconhecido`) | **Erro que a taxonomia não conhece** (`sintoma_nao_reconhecido`) | nem o `classify()` nem o `submecanismo()` reconhecem a mensagem | **erro novo**: um tipo que a taxonomia nunca viu, uma versão nova da esteira ou do smolagents, ou algo que não é erro de código (ex.: `AgentMaxStepsError`, exaustão de iterações). É o sinal de cobertura: onde ele cresce, as regras não alcançam |

As duas leituras se combinam **num ponto só**, o `montar_unidades()`, e **só para o resíduo**:

| O sintoma foi reconhecido? (`classify()`) | A causa foi identificada? (`submecanismo()`) | Vai para |
|---|---|---|
| sim | sim | uma unidade normal (ex.: `U_contrato_dict`) |
| sim | não | **Causa não identificada**: classe *Código Python mal escrito* (erro de sintaxe) ou *Erro conhecido, causa sem regra* |
| não | não | **Sintoma não reconhecido**: classe *Erro que a taxonomia não conhece* |
| não | sim | uma unidade normal; só a coluna de família fica "Sintoma não reconhecido" (raro; 0 casos na base 1) |

**Não há sobreposição.** Cada erro vai para exatamente uma unidade, e nunca está nos dois baldes. "Sintoma não
reconhecido" aparece em dois lugares: como **família** (a coluna do `classify()`) e como **unidade**. Os dois quase
sempre coincidem (base 1: 1 = 1) e só divergem na última linha da tabela.

**Esta é a única exceção à regra "o sintoma não decide".** O `submecanismo()` continua sem ler o `classify()`. Quem usa
a família é o `montar_unidades()`, e só para separar os dois baldes, que nunca viram memória. Nenhuma candidata
depende disso. Isso foi testado: as candidatas da base 1, e o sinal de harness, saem idênticas com ou sem a separação.

O nome "causa não identificada" diz o que aconteceu com a regra, não com o erro: **não quer dizer que o erro
aconteceu uma vez só**. Até 23/09/2026 o balde se chamava "erros pontuais", nome que sugeria isso sem que a regra
conferisse.

## 2 · O padrão: a impressão digital de um erro do resíduo

A unidade de resíduo junta, por construção, erros diferentes: é o que sobrou. Para contar se **um** erro volta, cada
erro ganha um **padrão** (`padrao_residuo()`, no `base_pipeline.py`):
- **fora da sintaxe:** a classe da exceção mais a frase mascarada. O texto entre aspas vira `<q>`, o texto entre crases
  vira `<id>` e os números viram `<n>`. Os valores entre aspas podem ser dados do caso, e a máscara também serve ao
  sigilo;
- **na sintaxe** (`codigo_mal_escrito`): a classe mais o motivo do parser (a linha `Error:`, ou, no formato novo, o
  trecho depois de `due to: …Error:`), sem a posição. Só a classe juntaria códigos quebrados de jeitos diferentes
  (Ajuste 2.1);
- **sem nome de exceção na mensagem:** a chave vira `sem impressão digital: <err_type>`, e **não conta como padrão
  recorrente**. Na base 2, o antigo `?` juntava tempo do interpretador e limite de passos, e passava na recorrência
  sem ser um padrão (Ajuste 8).

**A máscara é uma aproximação declarada, e falha nos dois sentidos** (livro-razão §4, item 2):
- **união excessiva:** a classe sozinha, ou o `?`, junta erros diferentes;
- **divisão excessiva:** a máscara só troca o que está entre aspas. Assim `Import from get_document_text …` e
  `Import from typing …` viram dois padrões, e `FinalAnswerTool` e `FinalAnswerToolOrHumanAssistance` não se juntam.

Por isso a tabela por padrão fica visível para conferência humana antes de se escrever a regra:
- base 1: notebook 9.2 e `resultados/residuo_padroes.csv`;
- base 3: `especificas/residuo.py`.

E o primeiro passo da leitura de casos é sempre **conferir o agrupamento** (procedimento, passo 3).

## 3 · Recorrência pelo padrão, não pela unidade

O resíduo **nunca é candidato**. Sem regra de causa não há frase que evite os casos, e portanto não há lição
escrevível. A triagem manda os dois baldes para **revisar**, a fila de trabalho da taxonomia, e aplica o mesmo teste de
recorrência das candidatas (≥3 execuções e ≥2 meses), só que **por padrão**. Que a unidade "recorra" só diria que
existe resíduo em vários meses.

- Algum padrão passa → **revisar — prioridade**.
- Nenhum passa → **revisar — baixa prioridade**. O balde continua na lista, porque é sinal de cobertura.
- **Alarme de cobertura:** se o "Sintoma não reconhecido" passar de 5% de todos os erros da base
  (`ALARME_COBERTURA`), o balde sobe para prioridade mesmo sem padrão recorrente: a taxonomia não cobre aquela base. A
  coluna "motivo (resíduo)" da triagem diz por que ele subiu.

"Revisar" não é "não-memória". Na não-memória a causa é conhecida e a correção vive fora do agente. No resíduo a
causa não é conhecida.

**Duas lições da base 2 sobre esta régua** (livro-razão §4, itens 3 e 4):
- **o alarme pode estar certo e o número enganar.** Os 5,2% de sintoma não reconhecido eram 64% um único padrão (o
  Timeout: 16 erros, 15 execuções, 1 mês, 1 papel). Sem ele, eram 1,9%. Antes de ler o alarme como "a taxonomia não
  cobre", olhe o Pareto dos padrões;
- **a régua de recorrência é da memória do agente, não do incidente de plataforma.** Um incidente reprova por ter um
  mês só. A saída é dar a ele uma regra (uma unidade `H_*`, que a `triagem()` manda direto para não-memória), não mexer
  no limiar.

## 4 · Pendente não é resíduo (a partir da base 3)

Na base 3 há um terceiro estado, o **pendente**: a regra existe, mas o dado não chegou na extração. Ele fica **sem
unidade**, aparece na cobertura com o motivo e o custo em tokens, e **não entra no resíduo nem no alarme**. Misturar os
dois inflaria o resíduo com erros que a taxonomia já sabe explicar, e esconderia a limitação da extração
([`../../2026-10-trace-law-flow-third/docs/01-racionais.md`](../../2026-10-trace-law-flow-third/docs/01-racionais.md) §3).
A mineração do resíduo **não lê os pendentes**.

## 5 · A mesma chave pode esconder mecanismos diferentes

O padrão priorizado da base 1 (`SyntaxError: closing parenthesis <q> does not match opening parenthesis <q>`, 3
execuções, 2 meses) é o mesmo motivo que a base 2 traz nos 7 erros do `RoteadorCivel`. Mas os mecanismos são outros:
- no cru da base 1 são **2 erros de digitação e 1 texto longo dentro de uma chamada**;
- na base 2 é **retorno colado**.

Por isso a regra "o mesmo padrão em outra base sobe de prioridade" confere o **mecanismo**, não só a chave
(livro-razão §4, item 5; `b1 #33`). Um padrão que aparece em duas bases só conta como "o mesmo" depois de lido nas
duas.

## 6 · O que reduz o resíduo

**Uma regra determinística nova, nunca uma leitura.** Cada padrão do resíduo termina de três jeitos:
- **vira regra:** estende a regra de uma unidade que já existe (a regra só não reconhecia esta forma da mensagem) ou
  cria uma unidade nova (`U_*` se a falha é do agente, `H_*` se é do harness, da infra ou de um limite do LLM). A regra
  vai no `submecanismo()`, e também no `classify()` quando o balde era "Sintoma não reconhecido". A mesma regra é
  reescrita à parte na auditoria nº 6;
- **é descartado com motivo escrito:** quando o agrupamento era falso, ou quando os casos não têm nada em comum além
  da classe;
- **fica como cobertura:** os padrões de uma ocorrência só. Não há trabalho agora; o padrão volta se reaparecer em
  outra base com o mesmo mecanismo.

Uma regra nova muda o número de alguma unidade já publicada, e por isso **é um Ajuste**: evidência, aprovação do
pesquisador, rodada nas bases, registro no livro-razão. A leitura de casos (do pesquisador ou dos leitores do kit,
`[assistido]`) só propõe a regra. Quem conta é o script, na população inteira.

**A meta não é zerar o resíduo.** O resíduo pequeno é a medida de que a taxonomia cobre a base. O trabalho vai para os
padrões que passam na recorrência e para os que mais custam em tokens. Um resíduo que cresce numa base nova é a
notícia a dar, e não um defeito a esconder.
