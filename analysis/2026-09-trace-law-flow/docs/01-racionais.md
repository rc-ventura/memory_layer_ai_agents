# Racionais — a lógica por trás da análise, em linguagem simples

**Para que serve este documento:** explicar *por que* a análise foi conduzida nesta ordem e *o que significam*
os conceitos usados — em prosa acessível, para reler antes de explicar a alguém (tutor, reunião) ou para você
mesmo reler depois sem precisar decifrar tabela técnica. Para os números exatos, os scripts e os testes
executados, ver [`03-procedimento-validacao.md`](03-procedimento-validacao.md) — os dois documentos se
complementam: este é o "por quê", aquele é o "como, com que número".

**O que este documento cobre — e o que não cobre.** Têm passo-a-passo próprio: o achado central (§3), o
sucesso verificado por conteúdo (§4), os cinco cortes de custo/eficiência (§5), a assinatura de erro por
papel + duração (§6), a tabela de candidatos a memória (§7), as três etiquetas de um erro — sintoma, mecanismo,
motivo (§8) — além dos conceitos de robustez (§2). A mineração do schema real das unidades nº2/nº10 (o que era a
§9) virou documento próprio: [`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md). **Não têm**
tratamento passo-a-passo próprio, só cobertura conceitual no §1: a recuperação 0/1.550, a reincidência entre
execuções, o teste ToolScan IAN/IAV e os detectores silenciosos (Result-Ignore / RAC / Tool-Skip) — para esses,
o caminho é a célula correspondente do notebook mais o [`02-relatorio-achados.md`](02-relatorio-achados.md).
Essa assimetria foi apontada por auditoria independente em 08/09/2026; o §3 (o mais importante dos que
faltavam) foi escrito em resposta, e o §7 em resposta a uma pergunta em sessão posterior sobre a mesma tabela.

---

## 1 · A lógica geral: do trace cru ao relatório

A pergunta que motivou isto foi: **a taxonomia de erros veio da leitura dos papers, ou veio do trace?** A
resposta certa inverte a ordem que pareceria natural.

1. **Trace cru → primeira exploração direta (v1).** Antes de ler qualquer paper, o JSON do trace foi
   percorrido, os `ActionStep` extraídos, e os 498 erros categorizados por **regex no tipo de exceção Python**
   (`KeyError`, `TypeError`, `SyntaxError`...) — isso é sintoma, não causa, e veio só de olhar o dado. Em
   paralelo, quatro papers (MAST, TRAIL, AgentDebug, ToolScan) foram citados usando **resumos de busca**, sem
   ler o texto completo.

2. **A pergunta "você usou a literatura de verdade?"** — a resposta foi não: era decoração, não fundamentação.
   Uma das citações (a taxonomia do ToolScan) estava literalmente **inventada pelo sumarizador de busca**.

3. **Leitura completa via subagentes.** Quatro subagentes leram os PDFs inteiros (não abstract, não snippet) e
   escreveram fichamentos em [`literature/`](../literature/), cada um respondendo três perguntas dirigidas: qual é
   a taxonomia real de cada paper, meu mapeamento a ela se sustenta ou não, e que análises eu deveria rodar no
   trace que ainda não tinha rodado.

4. **Com esses fichamentos em mãos, a taxonomia foi reconstruída — mas olhando o trace de novo, não copiando
   a literatura.** As mensagens de erro reais foram relidas e reagrupadas por **causa-raiz** (ex.: "retorno é
   dict, agente indexa como lista" em vez de "KeyError"). Essa reclassificação é do trace, feita em cima do
   dado — nenhum dos quatro papers deu essas categorias prontas, porque nenhum deles é sobre esteira jurídica
   em arquitetura CodeAgent.

5. **O que a literatura de fato fez** foi três coisas, nenhuma delas "dar a taxonomia":
   - **Testar o mapeamento contra taxonomias externas** — e a maioria não se sustentou. O achado mais forte do
     relatório é justamente esse: **o MAST não tem nenhum modo de falha para "o código levantou exceção"** —
     os autores põem isso fora do escopo deliberadamente. A família dominante do trace (erro de sintaxe no
     código gerado) cai exatamente na zona que a literatura de multiagente não cobre, porque nos sistemas que
     eles estudaram a ação do agente é *mensagem*, não *código executável*.
   - **Sugerir análises que ainda não tinham sido feitas** — por exemplo, o AgentDebug sugeriu verificar se a
     mensagem de erro chega ao contexto do step seguinte, o que virou o achado central (86,3% / 11,9%). O
     TRAIL sugeriu os detectores de falha silenciosa (Result-Ignore, RAC).
   - **Fornecer princípios de interpretação** — do AgentDebug, focar a causa-raiz e não o sintoma de
     superfície, que é a base da regra de cascata da tabela de candidatos (§7). *Correção 14–15/09/2026:* o
     AgentDebug **não** propõe tipos de memória nem "roteamento" módulo→tipo; os tipos da tabela de candidatos
     vêm de Hu et al. 2025 (arXiv 2512.13564, §4) — ver §7 Passo 3.

6. **Depois veio a rodada de validação**, independente da literatura — testando se cada número dependia de uma
   escolha arbitrária (lista de palavras, inventário de ferramentas, forma de comparar mensagens), comparando
   com a fonte autoritativa dentro do próprio trace quando ela existia. Foi aí que 13,7% virou 11,9%, RAC caiu
   de 461 para 125, e dois detectores foram retirados — o assunto da seção 2.

**Resumo da ordem certa:**

```
trace cru → taxonomia própria (inspeção direta do dado, por causa-raiz)
          → literatura lida de verdade (testa o mapeamento, sugere novas análises, dá framework)
          → análises novas rodadas no trace, motivadas pela literatura
          → validação/robustez de cada número (independente da literatura)
```

A taxonomia é evidência do trace; a literatura é o que permite dizer onde essa taxonomia se encaixa, onde ela
expõe algo que a literatura não previu, e o que ainda falta olhar.

---

## 2 · O que é um teste de robustez

### A ideia, fora do trace

Imagine a pergunta: *"quantas pessoas altas tem nessa sala?"* Para responder, é preciso uma regra para "alto"
— digamos, "mais de 1,75m". Contando: 12 pessoas.

Agora: e se a linha tivesse sido traçada em 1,70m? Ou 1,80m?

- Se der 11, 12, 13 nos três casos → "12" é um fato real sobre a sala. Não importa muito onde exatamente a
  linha foi traçada, a resposta continua parecida. **Robusto.**
- Se der 40 com 1,70m e 2 com 1,80m → o número "12" não estava dizendo nada sobre a sala — estava dizendo onde
  *quem analisou* decidiu cortar. Não existe um corte óbvio de "alto" ali. **Não robusto.**

Um teste de robustez é isso: mudar a regra inventada, refazer a conta, e ver se o resultado continua parecido
ou se voa pra qualquer lugar. No trace, a régua nunca é "altura" — é coisas como "quantos caracteres de uma
mensagem de erro contam como 'a mesma mensagem'" ou "quais palavras contam como 'o agente afirmando sucesso'".

### Por que um achado é RETIRADO, e não só corrigido

Dois desfechos são possíveis quando o teste dá errado, e a diferença importa. O exemplo mais claro foi o
"reasoning-action mismatch" (a ideia de "o agente disse que deu certo, mas o passo falhou").

**A regra original:** procurar, no *thought* do agente, palavras como "sucesso", "concluí", "obtive"... Se
aparecesse uma dessas E o step tivesse dado erro, contava como "o agente se contradisse". Deu 45 casos.

**O teste:** trocar a lista de palavras por uma mais curta e uma mais longa. Deu 0 num extremo e 63 no outro —
já um sinal ruim, como no exemplo da sala.

**A investigação que decide entre "corrigir" e "retirar":** os 45 casos originais foram lidos um por um. E a
descoberta foi pior do que "a lista de palavras era ruim" — **nenhum dos 45 era de fato uma contradição**.
Exemplos reais: um dizia *"...estarei pronto para montar a resposta final"* — futuro, não afirmação de
sucesso. Outro dizia *"Já obtive uma resposta detalhada..."* — isso era **verdade**, o agente realmente tinha
obtido a resposta num passo anterior; o erro aconteceu depois, por outro motivo (uma string mal fechada no
código).

Isso revelou um problema de **lógica**, não de calibração: o *thought* é escrito **antes** do código rodar. O
agente não tem como, no momento em que pensa, já saber que vai dar erro. "O thought parece positivo" e "o step
deu erro" nunca poderiam se contradizer de verdade — são duas coisas em momentos diferentes, sem relação
lógica entre si. Não existe lista de palavras melhor que console isso, porque o problema não é a lista — é que
o detector comparava duas coisas que nunca poderiam estar em contradição.

**A regra prática que sai daqui:**

| Desfecho | O que significa | Exemplo |
|---|---|---|
| **Corrigir** | o fenômeno é real, só foi medido com a régua errada | "agente repete o erro": continua verdade, só a forma de comparar mensagens mudou (13,7% → 11,9%) |
| **Retirar** | ao checar exemplo por exemplo, o fenômeno afirmado nem estava lá | "reasoning-action mismatch": os 45 casos, inspecionados, não eram contradições |

### "Fonte autoritativa dentro do próprio trace" — o que isso quer dizer

Este é um tipo diferente de teste — não é "varia a régua e compara", é "existe algo no próprio dado que já diz
a resposta certa, em vez de eu ter que adivinhar?".

**A analogia:** para saber quem foram os convidados de uma festa, um jeito é ficar na porta observando quem
entra e anotando nomes — um **palpite construído por observação**, sujeito a erro (confundir o garçom com um
convidado, por exemplo). Outro jeito é pegar a **lista de convidados que o anfitrião escreveu** — já existe,
pronta, dentro dos documentos da festa.

**O caso real:** era preciso saber quais nomes de função são ferramentas de verdade que o agente pode chamar.
O primeiro jeito foi "ficar na porta": observar quais funções apareciam sendo chamadas no código gerado, ao
longo de centenas de execuções, e montar uma lista de 43 nomes que pareciam ferramentas.

Só que o trace **já contém a lista oficial**. Cada execução carrega, na primeira mensagem do
`model_input_messages`, o "system prompt" — a instrução que o sistema manda para o modelo antes de ele
começar. Essa instrução **declara literalmente** cada ferramenta disponível, como assinatura de função Python
(`def nome_da_ferramenta(argumentos) -> retorno: ...`). Não é palpite — é o texto de configuração de verdade
usado pelo sistema.

Comparando a lista "observada" (43) com a "declarada" (90), dois problemas apareceram:

1. **Subestimação:** existiam 90 ferramentas de verdade, só 43 tinham sido vistas.
2. **Confusão de categoria, mais grave:** nomes como `grab` e `get_meta` apareciam bastante no código e tinham
   entrado na lista de "ferramentas" — mas não estão declarados no system prompt, porque não são ferramentas
   do sistema. São **funções auxiliares que o próprio agente escreve** dentro do seu código, num passo, e
   reaproveita nos passos seguintes (equivalente a escrever `def grab(doc): ...` no próprio script e chamar
   `grab(x)` mais adiante). O garçom tinha sido contado como convidado.

Quando existe uma fonte assim dentro do próprio dado, ela vale mais que qualquer heurística alternativa — não
é "mais uma opinião a comparar", é o fato contra o qual a opinião deveria ter sido checada desde o início.

---

## 3 · O achado central — passo a passo

Números em [`02-relatorio-achados.md`](02-relatorio-achados.md) §4. Esta seção estava faltando: o resultado
mais importante da análise era o único cuja construção nunca tinha sido destrinchada passo a passo — apontado
por auditoria independente em 08/09/2026.

### Passo 1 — a afirmação precisava de uma prova que ela ainda não tinha

O achado que sustenta a tese é "o agente não aprende com o próprio erro: reincide". Mas medir só *reincidência*
não prova isso. Se o agente errou de novo, existem duas explicações completamente diferentes: **(i)** ele viu a
mensagem de erro e mesmo assim repetiu — aí sim é falha de aprendizado; **(ii)** ele nunca recebeu a mensagem
de erro, e repetiu porque não tinha como saber. A segunda explicação não diz nada sobre memória — diz sobre
encanamento. Sem separar as duas, o achado inteiro fica ambíguo.

### Passo 2 — o que no dado tornava isso verificável

O harness (estilo smolagents) devolve o erro de um step para dentro do contexto do step seguinte. E o trace
guarda, por step, o campo `model_input_messages` — o contexto **exato** que aquele step recebeu. Ou seja: dá
pra checar *textualmente* se a mensagem de erro do step `k` estava no que o agente leu no step `k+1`. Não é
inferência sobre o que o agente "deveria" ter visto; é presença de texto no input registrado.

### Passo 3 — a operação

Para cada step com erro que tem um step seguinte (498 casos): normalizar espaços em branco da mensagem de erro,
pegar os primeiros 45 caracteres, e checar se essa string aparece no dump JSON do `model_input_messages` do
step `k+1`.

### Passo 4 — o primeiro resultado

**430 de 498 (86,3%)** — em 86% das vezes, a mensagem de erro comprovadamente entrou no contexto seguinte. Isso
elimina a explicação (ii) para a grande maioria dos casos: o agente **tinha** a informação.

### Passo 5 — a segunda pergunta, agora que a primeira está respondida

São **duas perguntas diferentes** sobre os mesmos 430 casos (os que comprovadamente leram a mensagem de erro
do step `k`). O "de novo" da primeira pergunta quer dizer "houve erro no `k+1`", **não** "o mesmo erro" — a
questão do "mesmo" é a segunda pergunta.

1. **O step seguinte (`k+1`) também deu erro? — qualquer erro, não importa o tipo.** `76 de 430` (**17,7%**).
   Os outros 354 se recuperaram: leram o erro e o `k+1` saiu limpo.
2. **Desses 76, em quantos o erro do `k+1` era da _mesma causa_ que o do `k`?** Este é o número que sustenta
   "o agente leu e reincidiu no mesmo problema" — e é o que precisou de correção (Passo 6). Resultado:
   **51 (11,9% dos 430)**. Os 25 restantes (`76 − 51`) erraram no `k+1` com causa **diferente** — isso é
   propagação de erro, não reincidência (a distinção e a análise ainda pendente estão em
   [`04-roadmap.md`](04-roadmap.md), seção "Fundamentação emprestada do AgentDebug", item 2).

```
430  leram a mensagem de erro do step k
 ├─ 354            → k+1 saiu limpo (recuperou)
 └─  76  (17,7%)   → k+1 também deu erro
        ├─ 51  (11,9% dos 430)  → mesma mensagem de erro   ← reincidência: o número-manchete
        │                                                    (58 = 13,5% comparando pelo mecanismo, Passo 8)
        └─ 25                    → mensagem diferente       ← propagação
```

O Passo 6 é só sobre o segundo número (o 51): "mesma causa" exige uma régua, e foi ela que precisou ser
acertada.

### Passo 6 — o teste de robustez que corrigiu o segundo número

"Mesma causa" exige uma régua, e a primeira que usei foi comparar os 30 primeiros caracteres das duas
mensagens. Deu 59 (13,7%). Testando com uma régua alternativa igualmente defensável (os 45 últimos caracteres,
onde fica o detalhe específico da exceção), deu 18 (4,3%) — divergência de 3×, sinal de que o número estava
falando da régua, não do agente. Investigando exemplos concretos (§2 acima explica esse caso em detalhe): o
prefixo casava o texto genérico de abertura (`"Code execution failed at line..."`), inflando; o sufixo exigia
igualdade quase byte a byte, perdendo repetições da mesma causa em código diferente. A régua certa não era
nenhuma das duas: era comparar pela **categoria da taxonomia** (`classify()`), o mesmo nível de granularidade
que o resto do relatório usa. Resultado corrigido: **51 (11,9%)**.

### Passo 7 — por que um número precisou de correção e o outro não

O "chegou ao contexto" (86,3%) é robusto: prefixo dá 86,3%, sufixo dá 84,9% — convergem. O "repetiu igual"
não era: 13,7% vs 4,3%. A diferença é que o primeiro pergunta "esse texto está presente?" (pouca ambiguidade)
e o segundo pergunta "essas duas coisas são a mesma?" (definição inteiramente arbitrária até você fixá-la).

### Passo 8 — o mesmo teste, um nível abaixo: por mecanismo (15/09/2026)

A régua do Passo 6 (`classify()`) compara **mensagens de erro**. A §7 mostrou que mensagens iguais podem vir de
mecanismos diferentes — então refiz a pergunta "é o mesmo erro?" comparando o **mecanismo** (a unidade da §7) do
step `k` com o do `k+1`. Resultado: **58 de 430 (13,5%)**, contra 51 (11,9%) por mensagem. Das 76 vezes em que o
agente errou de novo, as duas réguas concordam em 65 e discordam em 11 — conferidas caso a caso com
`drill_down.py`:

- **9 pares com mensagem diferente e o mesmo mecanismo** (contam por mecanismo, não por mensagem). Caso típico,
  execução `cd794f02…` (`ConversationAgent`): no step 2 o agente indexa por posição o dict das ferramentas de
  documento (`docs[0][0]` → "Retorno é dict"); no step 3 corrige, mas desce um nível demais e itera um único
  documento como se fosse lista (→ "Objeto sem o atributo esperado"). Duas mensagens, a mesma confusão sobre o
  formato do retorno.
- **2 pares com a mesma mensagem e mecanismos diferentes** (contam por mensagem, não por mecanismo). Execução
  `95344639…` (`RespostaBacen`): no step 1 o agente pede um campo que não existe (`informacoes_evidencias`; o
  retorno oferece `dados_evidencias`); no step 2 a ferramenta devolve um **texto de erro** e o agente o indexa
  como dict. As duas quebras aparecem como "Could not index", mas são lições diferentes.

**Ressalva que vai junto:** 20 dos 58 vêm de "Explicação nunca solta no bloco de código", quase todos do
incidente de dez/2025 — é o laço da execução `2a407143…` (10 erros seguidos, descrito em
`03-procedimento-validacao.md`). O mesmo laço também pesa na régua por mensagem.

**Decisão:** o número-manchete continua 11,9% (a régua já testada, usada no relatório); 13,5% entra como quarta
régua do teste de robustez. As duas contam a mesma história — o agente lê o erro e repete — e a régua por
mecanismo deixa o achado um pouco mais forte, não mais fraco.

### O que isso prova — e o que não prova

**Prova:** o feedback dentro da trajetória existe, é lido, e não basta. Em 11,9% dos casos onde o agente
comprovadamente leu o erro, ele caiu na mesma categoria de novo (13,5% comparando pelo mecanismo, Passo 8). Junto
com a reincidência entre execuções (o mecanismo "texto longo dentro de literal" aparece nos 9 meses com dado da
amostra), é o caso empírico direto para memória externa persistente.

**Não prova:** que o agente é incapaz de aprender. O que está medido é a insuficiência do mecanismo de feedback
atual (devolver o texto do erro no contexto seguinte), não um limite do modelo. É exatamente por isso que o
achado sustenta "precisa de um mecanismo de memória", e não "precisa de um modelo melhor".

---

## 4 · Sucesso verificado por conteúdo — passo a passo

Esta seção reconstrói o racional de uma análise específica (documentada com números em
[`02-relatorio-achados.md`](02-relatorio-achados.md) §3.1), porque a lógica não ficou clara na primeira explicação.

### A pergunta que a análise tenta responder

Até aqui, o achado "erro é custo, não falha" vinha de uma checagem **mecânica**: em algum momento a função
`final_answer(...)` foi chamada? Isso não confirma que o **conteúdo** daquela resposta era bom — só que a
função rodou. Um cético perguntaria: *"tá, ele chamou `final_answer`, mas será que a resposta que saiu dali
prestava, ou ele só colou qualquer coisa lá pra não travar?"* A análise tenta fechar essa lacuna: pegar só as
execuções que **de fato tiveram resposta boa** e ver quantas, mesmo assim, tiveram erro pelo caminho.

### Passo 1 — por que não dava pra usar o campo "status" do banco

A tentação óbvia seria usar o campo de status do banco pra separar sucesso de fracasso. Mas esse campo já
tinha se mostrado não confiável: a maioria das execuções não tem status de "concluída" persistido, mas 100%
das memórias delas contêm um `final_answer` de verdade lá dentro. O campo do banco não bate com o que
realmente aconteceu no agente — usar ele seria usar uma régua já sabidamente quebrada.

### Passo 2 — como achar uma régua melhor, sem inventar uma

Era preciso separar "resposta boa" de "resposta ruim" olhando o **texto da resposta**, não um campo de banco.
A tentação seria inventar uma lista de palavras que soam a "não consegui responder" — mas listas de palavras
inventadas já tinham se mostrado frágeis (foi o que derrubou o "reasoning-action mismatch", seção 2). Em vez
de inventar, a pergunta certa é a mesma da seção 2: **o próprio sistema já diz, nas instruções que manda pro
agente, qual frase usar quando ele não acha a resposta?**

Achou-se: o system prompt instrui literalmente — *"Ausência de base ou dúvida: responder 'Não encontrado na
base' OU 'Informação insuficiente na base'"*. Não é uma frase inventada; é o protocolo que o próprio sistema
define para "não consegui responder". Essas duas frases exatas viraram o critério.

### Passo 3 — o que foi medido

Para cada execução: (1) o texto que o agente realmente devolveu como resposta final contém uma das duas
frases de "não achei"? Se sim → resposta **degenerada**; se não → **conteúdo**. (2) Em qualquer lugar da
execução inteira, aconteceu algum erro? Depois, cruzar as duas.

### Passo 4 — o achado

834 de 840 execuções (99,3%) tiveram resposta de conteúdo. Dentro delas, **310 (37,2%) tiveram pelo menos um
erro pelo caminho** e mesmo assim a resposta final não foi um "não encontrado" — foi uma resposta de verdade.
Essa proporção (37,2%) é quase idêntica à taxa de erro do dataset inteiro (37,3%): se o erro estivesse
causando respostas ruins, seria esperado ver **menos** erro no grupo "resposta boa" do que no geral — e não é
isso que aparece. O custo confirma o padrão já visto: quem teve erro gastou o triplo de tokens, mesmo dentro
do grupo cuja resposta se confirmou boa.

### A conclusão, e onde ela para

O padrão "erro é custo, não causa de fracasso" sobrevive a um teste mais rigoroso — que olha o conteúdo da
resposta, não só se a função rodou. Isso é evidência real, mais forte que a anterior, porque responde à
objeção óbvia que alguém faria numa reunião.

Mas a conclusão prova **menos do que parece à primeira vista**. O detector de "degenerada" só pega as duas
frases exatas — não pega um pedido de esclarecimento (ex.: *"Por favor, especifique um valor de filtro..."*),
que fica contado como "sucesso" sem realmente ser uma resposta final. Os 99,3% provavelmente estão inflados
por isso. E mais fundamental: o teste só checa se a resposta **existe e não é uma recusa** — não checa se ela
está **factualmente certa** (se os números, datas e nomes de processo citados vêm mesmo dos documentos, ou se
foram inventados). Essa é a pergunta de *groundedness*, ainda em aberto — o próximo passo de maior valor
listado no relatório.

---

## 5 · Cinco cortes de custo e eficiência — passo a passo

Números completos em [`02-relatorio-achados.md`](02-relatorio-achados.md) §3.2–3.6. Aqui, a cadeia mecânica
completa de cada uma: que dado exato entrou, que operação foi aplicada, que resultado saiu, por que essa
operação e não outra — pra dar pra criticar ou refinar qualquer elo, não só concordar ou discordar da
conclusão final.

### 3.2 · Razão input/output por step

**Passo 1 — a lacuna.** Já tínhamos *descrito em palavras* dois mecanismos: "string não fechada" acontece
quando o agente gera texto longo; "retorno é dict" acontece ao processar uma entrada grande. Descrição em
palavras não é prova — pode ser uma história bonita sem sustentação no dado. Precisava de um número que
pudesse confirmar ou desmentir.

**Passo 2 — o dado disponível.** Cada `ActionStep` do trace já registra `token_usage.input_tokens` e
`token_usage.output_tokens` separadamente — não é preciso inventar nada, o dado já existia, só nunca tinha
sido cruzado dessa forma.

**Passo 3 — a operação.** Para cada step, dividir `tok_in / tok_out` (excluindo os casos raros de
`tok_out = 0`, que dariam divisão por zero). Agrupar esses valores pela assinatura de erro (a taxonomia já
validada em §2 deste documento) e tirar a **mediana** de cada grupo — mediana, não média, porque já sabíamos
de outras análises que a distribuição de tokens tem cauda longa (§3.4 abaixo) e média seria puxada por
outliers.

**Passo 4 — o resultado bruto.** Mediana geral dos steps OK: 33,5. "String não fechada": 17,5 (menos da
metade). "Retorno é dict": 58,9 (quase o dobro).

**Passo 5 — a leitura.** Um step que trava processando um payload grande recebe muito `tok_in` e mal chega a
escrever antes de quebrar → razão alta. Um step que trava NO MEIO de escrever um relatório longo já consumiu
muito `tok_out` antes da falha → razão baixa. Os dois extremos da distribuição geral batem exatamente com a
hipótese original — ela deixa de ser história e vira número.

**Passo 6 — o uso prático.** Além de confirmar, isso vira sinal operacional: um step com razão anormalmente
alta logo após uma chamada de ferramenta pesada é candidato a esse erro específico — detectável **antes** da
exceção acontecer, só observando o padrão de consumo de tokens.

### 3.3 · Tokens por chamada de ferramenta declarada

**Passo 1 — a lacuna.** Taxa de erro (§2.1) mede comportamento errado. Um papel pode nunca errar e ainda
assim ser caro pra produzir uma unidade de trabalho real — essa pergunta é logicamente independente da taxa
de erro, e nunca tinha sido feita.

**Passo 2 — definir "unidade de trabalho real".** Não é "um step" (um step pode ser só formatação, sem
chamar nada). É uma chamada a uma ferramenta **declarada** no system prompt — a mesma lista autoritativa de
90 nomes já usada e validada no teste de inventário (§2 acima). Reusar essa lista, em vez de reconstruir uma
nova, é deliberado: evita reintroduzir o erro de confundir função auxiliar do agente com ferramenta real.

**Passo 3 — a operação, sempre por papel.**

1. **Por step, duas quantidades.** `tokens(step)` = `tok_in` + `tok_out` daquela chamada de LLM (o total do
   step — mesma unidade "tokens" de §3.4/§3.6, dominada pelo contexto re-enviado). `n_calls(step)` = nº de nós
   `ast.Call` no `code_action` (via `ast.parse`) cujo nome está na lista autoritativa de 90 ferramentas
   declaradas — chamada a função auxiliar do próprio agente (`grab`, `get_meta`) ou indexação de dict **não**
   contam.
2. **Agrupar os steps por papel** — pelo `cod_idef_aget` da execução a que cada step pertence.
3. **Por papel, somar as duas colunas** sobre *todos* os steps daquele papel: `Σtok(papel)` e `Σcham(papel)`.
   *Todos* mesmo — inclusive os steps cujo código não parseia, que entram com `n_calls = 0` (Ressalva 2).
4. **Uma divisão por papel:** `métrica(papel) = Σtok(papel) / Σcham(papel)`. Sai **um número para cada papel**
   (Passo 4) — **não** uma divisão única do dataset inteiro. (A divisão global, `Σtok(tudo) / Σcham(tudo)`, é
   outra coisa — a "razão agregada" do Passo 5.)

**Ressalva 1.** Steps sem nenhuma chamada de ferramenta (`n_calls = 0` — raciocínio puro, formatação) entram no
numerador mas não no denominador. É proposital — o número cobra o overhead de contexto/raciocínio às chamadas
("quantos tokens custa produzir uma invocação de ferramenta real deste papel") — mas infla o valor; a versão
estrita (só steps com `n_calls ≥ 1`) daria menos.

**Ressalva 2 — o que acontece quando o código nem parseia (regra oficial fixada em 15/09/2026).** É um terceiro
caso, diferente do de cima: o `code_action` tem erro de sintaxe e `ast.parse()` levanta exceção **antes** de
contar qualquer chamada — não é raro, é a família de erro mais comum deste trace inteiro (`SyntaxError`, string
não fechada, §2). Chamamos esses de **steps não parseáveis**: o texto que o agente emitiu não é uma árvore
sintática válida, então não há como percorrer o código e contar invocações nele. Um step **parseável** é o caso
normal — `ast.parse()` devolve a árvore, o `ast.walk()` conta as chamadas cujo nome está entre as 90
ferramentas declaradas.

> **Regra oficial:** o step **sempre** entra no numerador (os tokens que ele queimou são custo real do papel) e
> contribui **zero** para o denominador (não dá pra contar chamadas numa árvore que não existe). Em código:
> `except Exception: n_calls = 0`, com a soma de tokens fora do `try`.

Três razões, em ordem de peso:

1. **Consistência com a Ressalva 1.** Um step de raciocínio puro já entra no numerador com `n_calls = 0` — o
   overhead é cobrado das chamadas reais, de propósito. Um step que não parseia está exatamente na mesma
   situação do denominador (zero chamadas confirmadas); descartá-lo seria aplicar *duas* regras diferentes ao
   mesmo caso, e era essa a inconsistência que o notebook carregava (a conta por papel descartava, a conta por
   execução da mesma célula já somava).
2. **É o que a métrica pergunta.** "Quanto custa a este papel produzir uma chamada de ferramenta real" inclui o
   que ele gastou tentando e não conseguindo: o papel queimou os tokens, o trabalho não saiu. Descartar mede
   outra coisa — o custo dos steps bem-comportados.
3. **O descarte enviesa justamente onde dói — e isso é medido, não suposto.** Varrendo o trace cru por fora do
   notebook: **224 dos 5.781 steps (3,9%) não parseiam**, e eles queimaram **5,50M tokens** (3,9% do
   numerador). O número que decide a questão: **224 de 224 — 100% — têm o campo `error` preenchido no próprio
   step**. Ou seja, a regra antiga não descartava uma amostra neutra de steps difíceis de contar; ela
   descartava **exclusivamente falhas**. Uma métrica de custo que remove só os steps que deram errado responde
   "quanto custa este papel quando dá certo", que é a pergunta oposta à desta análise.

**O preço da escolha, declarado:** o número fica **maior**. A versão estrita (só steps com `n_calls ≥ 1` no
numerador) daria menos. É o mesmo viés já assumido na Ressalva 1, agora aplicado de forma consistente aos dois
casos de denominador-zero — não uma correção de erro, uma escolha de escopo entre duas contas defensáveis.

**O que isso mudou.** Só os 7 papéis que têm steps não parseáveis; os outros 9 ficam idênticos ao dígito:

| Papel | steps não parseáveis | tokens neles | exclusiva | **oficial** | Δ |
|---|---:|---:|---:|---:|---:|
| managerAgent | 141 | 2.889.647 | 17.592 | **18.775** | +6,7% |
| ConversationAgent | 72 | 2.540.262 | 27.062 | **27.988** | +3,4% |
| CadastroCivel | 5 | 26.162 | 3.249 | **3.618** | +11,3% |
| RespostaBacen | 1 | 17.295 | 7.929 | **8.004** | +1,0% |
| RoteadorCivel | 3 | 13.004 | 6.120 | **6.220** | +1,6% |
| CadastroTrabalhista | 1 | 10.445 | 5.446 | **5.589** | +2,6% |
| WorkflowManager | 1 | 5.565 | 6.661 | **6.678** | +0,3% |

Razão agregada: 21.420 → **22.280**. Não mudaram: `CalculoCivel` (141.673) e
`CalculoTrabalhista` (50.624) — o código deles parseia; a mediana por execução (12.192), que já era inclusiva; e
portanto os múltiplos **11,6×** e **4,2×** e o destaque laranja do gráfico 8.9 (`ConversationAgent` já estava
acima de 2× a mediana antes e depois).

**Nota de auditoria.** Essa divergência aparecia como dois números na §3.3 (27.988/18.775 no relatório ×
27.062/17.592 no notebook) e foi diagnosticada como *duas contas sem rótulo*, não erro de digitação. A origem
está na auditoria independente de 08/09, que usou **dois** scripts com réguas diferentes sem notar:
`audit_recompute3.py` soma os tokens **antes** do `try/except` do parse (inclusiva) e produziu os valores por
papel; `audit_recompute4.py`, réplica fiel da célula da época, descartava o step do agregado por papel mas
mantinha os tokens dele no agregado por execução — replicou a inconsistência da célula e por isso acertou
21.420 e 12.192 simultaneamente. A linha 33 do relatório de auditoria marcou "idênticos ✅" juntando os dois,
embora o log do primeiro script já imprimisse `22,280 (esperado 21.420)`. Com a regra unificada, notebook e
auditoria convergem nos três valores — ver nota **N1** em `../audit/2026-09-08-auditoria-independente.md`.

**Passo 4 — o resultado.** `CalculoCivel`: 141.673 tokens por chamada de ferramenta. `CalculoTrabalhista`:
50.624. O múltiplo que dá escala a esses números é sempre contra a **mediana, entre execuções, da razão
tokens/chamada** — o `12.192` do Passo 5, que é uma razão, **não** o custo de uma execução inteira (esse é da
ordem de dezenas de milhares de tokens — ver §3.5): `CalculoCivel` gasta **11,6×** mais tokens por chamada que
a execução mediana; `CalculoTrabalhista`, **4,2×**. Cruzando com a taxa de erro já conhecida:
`CalculoTrabalhista` tinha taxa de erro normal (9%) — a ineficiência por chamada é um problema que a taxa de
erro sozinha nunca revelaria.

**Passo 5 — a correção de rótulo, achada ao revisar antes de publicar.** O primeiro número que calculei
("mediana geral: 21.420" — **22.280** desde que a Ressalva 2 fixou a regra de contagem) estava **mal nomeado**
— não era mediana, era razão agregada (soma de tudo / soma
de tudo, dominada pelos papéis de maior volume). Recalculei a mediana de verdade (das razões por execução,
uma de cada vez, depois tirando o valor central): 12.192 — continua sendo **tokens por chamada**, não tokens
por execução. As duas medidas são legítimas — divergem porque o
custo é concentrado numa cauda (§3.4) — mas chamar a agregada de "mediana" seria erro de rótulo, não de
cálculo. Corrigido em todos os três documentos.

### 3.4 · Concentração de custo (Pareto)

**Passo 1 — a lacuna.** Já tínhamos citado "a execução mais cara consumiu 5,9M tokens" como curiosidade
solta, sem responder se é exceção rara ou se o sistema inteiro se comporta assim.

**Passo 2 — a operação.** Pegar as 840 execuções, cada uma já com seu total de tokens somado (dado que já
existia). Ordenar do mais caro pro mais barato. Para cada fatia do topo (1%, 5%, 10%, 20%, 50% das execuções,
por contagem), somar os tokens dessa fatia e dividir pelo total do sistema — uma soma acumulada normalizada,
sem nenhuma escolha de corte ou classificação envolvida.

**Passo 3 — o resultado.** 1% das execuções (8 de 840) = 16,8% do gasto total. 10% (84 execuções) = 54,6%.
50% (420 execuções) = 89,8%.

**Passo 4 — por que não precisou de teste de robustez.** Diferente das outras análises desta seção, aqui não
existe corte arbitrário: é soma acumulada sobre a lista inteira ordenada, o resultado não depende de nenhuma
escolha minha — só reordena e soma. Não há régua pra variar.

**Passo 5 — a leitura.** 10% das execuções carregam mais da metade do custo do sistema inteiro. Otimizar o
caso médio rende pouco comparado a mirar o perfil dessa cauda.

### 3.5 · Desperdício em percentual vs. em volume absoluto

**Passo 1 — a lacuna.** Taxa de erro (§2.1) e tokens/chamada (§3.3) são as duas **razões**. Razão esconde
escala: um papel pode ter razão "boa" e ainda ser, em números absolutos, o maior poço de desperdício do
sistema, se processar um volume grande o bastante.

**Passo 2 — a operação.** Por papel: somar tokens de todos os steps (`tok_total`) e somar tokens só dos steps
com erro (`tok_erro`). Dividir `tok_erro / tok_total` dá o percentual; `tok_erro` sozinho dá o volume absoluto.
Filtrar papéis com `tok_total >= 50.000` pra excluir ruído de papéis com volume irrelevante — essa é a única
escolha embutida, e foi testada (ver abaixo).

**O que conta como "uma execução", e por que o corte é 50.000.** Uma execução = uma linha do CSV = um
atendimento completo da esteira a **um** pedido do usuário, da pergunta que entra até o `final_answer` que sai
— dura minutos. Os 9 meses (nov/2025–ago/2026) são só a janela em que as 1.000 execuções foram coletadas, não
a duração de uma. Dentro de **uma** execução atuam vários papéis: o `managerAgent` orquestra, delega ao
`ConversationAgent`, que aciona agentes de domínio (`CalculoCivel`, `CadastroTrabalhista`…). O "custo de uma
execução" é a soma dos tokens (entrada + saída, todos os steps) de **todos esses papéis juntos, dentro daquela
execução**. A mediana desse custo, entre as 840 execuções, fica na casa das **dezenas de milhares** de tokens
(`02-relatorio-achados.md` §3: 48 mil nas execuções sem erro; §3.6: mediana mensal de 54–95 mil).

Esse é um recorte **diferente** do `tok_total` do filtro — e confundir os dois é o que torna o "50.000" opaco:

| Soma | Junta o quê | Ordem de grandeza |
|---|---|---|
| **custo de uma execução** | todos os papéis, **dentro de 1 execução** (1 pedido) | ~dezenas de milhares (~50 mil) |
| **`tok_total` de um papel** (o do filtro) | um só papel, **somando as 1.000 execuções / 9 meses** | `ConversationAgent` 76,8M · `CalculoCivel` 7,9M · papel raro < 10 mil |

O corte de 50.000 toma emprestado o número "uma execução típica" (~50 mil) e o usa como **piso** sobre o
`tok_total` do papel: se um papel, somando os 9 meses inteiros, gastou menos do que uma única execução típica
custa, ele é marginal demais pra entrar num ranking de desperdício — o "% desperdiçado" dele sairia de uma
base minúscula (tirar percentual de 2 jogadas de moeda). É um piso de relevância, redondo e aproximado de
propósito; o que o sustenta não é o valor exato, e sim o teste do Passo 4 (10k / 50k / 100k não mexem nos
primeiros colocados).

**Passo 3 — o resultado, dois rankings.** Por percentual: `CalculoCivel` lidera (25,0%). Por volume absoluto:
`ConversationAgent` lidera (7,5M tokens, quase 4× o desperdício absoluto de `CalculoCivel`), apesar de um
percentual "saudável" (9,8%) — só porque processa um volume total muito maior (76,8M contra 7,9M).

**Passo 4 — teste de robustez do corte de 50.000.** Recalculei com cortes de 10.000, 50.000 e 100.000. Os
cinco primeiros colocados por percentual são idênticos nos cortes de 10k e 50k; no corte de 100k, dois papéis
de volume muito pequeno (`JoogleAnalytics`, `ontestacaoCivel`) saem da lista — comportamento esperado do
próprio corte, não instabilidade do achado. **Robusto.**

**Passo 5 — a leitura.** Os dois rankings não concordam de propósito, e essa discordância é o achado: "qual é
a prioridade" depende de o critério ser corrigir o comportamento mais quebrado (`CalculoCivel`) ou economizar
o máximo em termos absolutos (`ConversationAgent`).

### 3.6 · Evolução mensal da eficiência

**Passo 1 — a hipótese que este teste tenta derrubar.** Se o custo por execução estivesse caindo mês a mês só
por ajuste orgânico da equipe — sem nenhum mecanismo de memória — isso enfraqueceria a tese: bastaria esperar
o sistema melhorar sozinho.

**Passo 2 — a operação.** Agrupar as 840 execuções por `mes` (campo já derivado de `anomesdia` desde a seção
1), tirar mediana de `tok_tot` por mês. Sem corte, sem classificação — é agrupamento e mediana direto.

**Passo 3 — o resultado.** dez/2025 (n=208): mediana 54.086. Os meses seguintes não caem — abr/2026 (n=65)
chega a 94.585, quase o dobro. jun/2026 (n=268, a maior amostra do dataset): 75.430, ainda acima de dezembro.

**Passo 4 — a ressalva de amostra, não de escolha.** jan/2026 (n=7) e mar/2026 (n=9) foram excluídos da
leitura por amostra pequena demais — isso não é um corte que precise de teste de robustez (não é uma escolha
que poderia mudar a conclusão se variada), é simplesmente reconhecer que 7 pontos não sustentam uma mediana
confiável, o mesmo princípio do corte de amostra usado em §2.3 e §6 abaixo.

**Passo 5 — a leitura.** Não há tendência de queda nos meses com amostra confiável. Ausência de melhora
orgânica ao longo de 9 meses é o que sustenta a necessidade de um mecanismo ativo — se bastasse esperar, o
padrão apareceria aqui, e não aparece.

**Ressalva — o que "a mediana subiu" não diz sozinho.** Mediana mais alta em 2026 não distingue "o mesmo
trabalho ficou mais caro" de "a carga mudou" (mais casos pesados, agente/rota nova — o status 34 só aparece a
partir de abr/2026). A conclusão que se sustenta aqui é a **ausência de queda**; atribuir a subida a regressão
de eficiência exige decompor cada mês em erro × baseline limpo × comprimento de trajetória —
[`04-roadmap.md`](04-roadmap.md) item 9.

---

## 6 · Erro por papel e por duração — passo a passo, respondendo "temos o tipo de erro por agente?"

Números completos em [`02-relatorio-achados.md`](02-relatorio-achados.md) §2.2–2.3.

### 2.2 · Mecanismo de erro por papel (refeito por mecanismo em 15/09/2026)

**Passo 1 — a pergunta literal.** Dado um papel (`CalculoCivel`, `CadastroTrabalhista`...), sabemos que TIPO
de erro ele comete, especificamente, ou só sabemos a taxa geral dele?

**Passo 2 — a primeira tentativa, e por que ela engana.** O caminho óbvio é cruzar papel × família de erro em
**contagem bruta** (quantos erros de cada tipo, por papel). Mas os papéis têm volumes muito diferentes —
`ConversationAgent` tem 2.478 steps, `CadastroTrabalhista` tem 51. Num cruzamento bruto, um papel pequeno
nunca aparece perto do topo de nada, mesmo que seja *inteiramente* dominado por um único tipo de erro — a
contagem absoluta dele é sempre pequena demais pra competir com os papéis grandes.

**Passo 3 — a correção.** Normalizar por **linha**: para cada papel, dividir a contagem de cada família pelo
total de erros DAQUELE papel — perguntar "dos erros deste papel, que fração é de cada tipo?", não "dos erros
do dataset inteiro, quantos vieram deste papel?". São perguntas matematicamente diferentes, e só a primeira
revela assinatura característica.

**Passo 4 — a operação exata.** `pd.crosstab(papel, mecanismo)` sobre os 498 erros (o mecanismo é a unidade da
§7, atribuída na célula "Do sintoma ao mecanismo" do notebook); dividir cada linha pela soma daquela linha;
multiplicar por 100. Manter só papéis com volume mínimo (`role_vol >= 5`) pra não exibir percentual de amostra
ínfima. *Até 14/09 a coluna era a assinatura (a mensagem de erro); trocou porque a pergunta aqui é "que lição
escrever para este papel", e a mensagem engana nisso — ver Passo 8.*

**Passo 5 — o resultado.** `CadastroTrabalhista`: 94% dos erros são "ferramentas só aceitam argumento nomeado"
(n=18). `CalculoCivel`: 76% são "retorno pode chegar como string" (n=17). `managerAgent`: 62% são "texto longo
nunca dentro de literal de string" (n=180). `ConversationAgent`: 43% "retorno das ferramentas de documento é
dict" e 29% "texto longo em literal". `RespostaBacen` não tem dominante: campo inexistente e retorno como string
empatam em 33%, e 29% é protocolo do harness.

**Passo 6 — teste de robustez do corte `role_vol >= 5`.** Recalculei com cortes de 3, 10 e 15, por mensagem (até
14/09) e por mecanismo (15/09): os papéis que aparecem em mais de um corte têm exatamente o mesmo mecanismo
dominante e o mesmo percentual em todos. **Robusto** — com uma honestidade a registrar: o corte só decide *quais
papéis aparecem*; o % dentro de um papel nunca dependeu dele. O teste confirma que nada quebra, mas não é um
teste forte.

**Passo 7 — a leitura.** No dataset inteiro, "argumento nomeado" é só 7% de todos os erros — parece secundário.
Mas dentro de `CadastroTrabalhista` especificamente, é quase o problema inteiro. A mesma causa pode ser
"pequena" no agregado e "dominante" num recorte — e o recorte que importa pra decidir onde escrever memória é o
papel, não o dataset inteiro.

**Passo 8 — o que a troca de régua mudou, conferido no trace cru.** Dois papéis tinham a causa errada quando a
coluna era a mensagem de erro:

- **`CalculoCivel`** — o percentual é o mesmo (76%), a causa não. Por mensagem, aparecia como "Retorno é dict".
  No `drill_down.py caso` da execução `42891135…`: a ferramenta `calculo_correcoes_monetarias` devolve o
  resultado como **texto JSON**; o agente faz `corr_mon["valor_corrigido"]` e quebra; no step seguinte ele mesmo
  corrige com `isinstance(corr_mon, str)` + `json.loads`. A lição existe dentro da execução — e se perde na
  próxima.
- **`RespostaBacen`** — por mensagem, 62% "Retorno é dict"; por mecanismo, dois erros diferentes. Um deles,
  execução `1be966e7…`: a ferramenta `validar_quebra_sigilo` devolve `{'vazamento_sigilo': …, 'justificativa':
  …}`, e o agente pede `quebra_sigilo`. No step seguinte ele escreve o mapeamento `vazamento_sigilo →
  quebra_sigilo` num comentário. É um fato sobre a ferramenta que caberia numa unidade de memória factual.

### 2.3 · Duração por família de erro

**Passo 1 — a lacuna.** Todo "custo" medido até esse ponto era em tokens. Tokens e tempo não são a mesma
coisa — uma chamada pode ser barata em tokens e cara em segundos (ex.: espera de timeout numa infraestrutura
lenta). Isso é uma pergunta nova, não uma repetição da anterior.

**Passo 2 — a operação.** Cada `ActionStep` já tem `timing.duration` (dado que já existia, nunca cruzado com
família de erro antes). Agrupar por assinatura, tirar mediana e contar `n` de cada grupo.

**Passo 3 — o primeiro resultado (antes do teste).** "Falha do LLM interno": mediana 115,2s, `n=6`. Todas as
outras famílias ficavam entre 3s e 16s — uma diferença de ordem de grandeza que parecia um achado forte.

**Passo 4 — por que esse número precisava de teste antes de virar fato.** `n=6` é uma amostra pequena, e uma
mediana de 6 pontos é sensível a cada ponto individual — o teste certo é checar se o padrão sobrevive a exigir
mais amostra.

**Passo 5 — o teste.** Recalcular a mesma tabela com corte mínimo de amostra `n >= 3, 10, 20, 50` — a mesma
lógica de "varia a régua e compara" usada em toda a §2 deste documento, agora aplicada a um corte de tamanho
de amostra em vez de um corte de similaridade de texto.

**Passo 6 — o que o teste revelou.** Com `n >= 10`, "Falha do LLM interno" **desaparece da tabela** — os 6
pontos não sobrevivem ao corte. Olhando os valores brutos por trás daquela mediana:
`6,8s, 8,9s, 62,2s, 168,1s, 205,7s, 818,7s` — uma dispersão de quase 3 ordens de magnitude (de 7 segundos a 14
minutos). Uma mediana calculada sobre pontos tão dispersos não descreve um comportamento estável; descreve o
acaso de quais 6 execuções entraram na amostra. Rodando o mesmo teste, apareceu outra família igualmente rara
(`Módulo usado sem import`, também `n=6`, mediana 65s) que a primeira versão nem tinha citado — sinal de que
eu tinha olhado só o extremo mais chamativo (115s), não toda a distribuição.

**Passo 7 — a correção.** Refeita a tabela só com famílias de amostra confiável (`n >= 20`): "string não
fechada" (n=159) é 15,3s de mediana, quase o dobro de "retorno é dict" (n=136, 7,7s) — essa diferença, sim,
sobrevive a qualquer corte razoável. A hipótese sobre erro de infra ser caro em tempo mesmo barato em token
continua plausível, mas virou hipótese explícita a testar com mais dados — não número publicado como fato.
Corrigido nos três documentos.

### Por que só 2.2, 2.3 e 3.5 precisaram de teste, entre os oito achados desta rodada

O critério é sempre o mesmo (§2 acima): só precisa de teste quem embute uma escolha de corte ou heurística que
poderia mudar a conclusão se variada. `3.1` já usava fonte autoritativa. `3.2` (razão in/out), `3.4` (Pareto) e
`3.6` (evolução mensal) são contagem/razão direta, sem corte de classificação — não há régua pra variar. `3.3`
reusa o inventário de ferramentas já validado. `2.2` e `3.5` tinham corte de volume mínimo; `2.3` tinha corte
de tamanho de amostra por família — os três testados, dois confirmados robustos, um corrigido.

---

## 7 · Os candidatos a unidade de memória — passo a passo

Números completos em [`02-relatorio-achados.md`](02-relatorio-achados.md) §6. Código no notebook: a célula "Do
sintoma ao mecanismo" (logo após `classify()`, na §2 — submecanismo, cascata, ocorrência; usada também em §2.2,
§3, §5, §6, §8.4, §8.5 e §8.8), e na §9 as células 9.2 (triagem, tabelas, CSV) e 9.3 (gráfico). **Refeito do zero em
15/09/2026**, reexecutando o notebook inteiro duas vezes: as saídas da §9 saíram idênticas nas duas execuções e
os outros quatro CSVs (`erros_classificados`, `execucoes`, `payoff_assinaturas`, `reincidencia`) saíram
byte-idênticos à versão anterior — só a tabela de candidatos mudou. A versão anterior (7 candidatos, tipos por
analogia aos módulos do AgentDebug) fica no histórico do git.

**Passo 1 — a lacuna: assinatura não é unidade de memória.** A §2 do relatório classifica os 498 erros por regex
sobre a mensagem da exceção — isso é o **sintoma**. Uma unidade de memória é outra coisa: **um conteúdo,
escrevível numa frase, que evitaria o erro na próxima execução**. Os dois não coincidem 1:1. Exemplo concreto: a
assinatura "Falha ao indexar o retorno (Could not index)" (136 erros) junta três conteúdos diferentes — 89 são de
fato um dict indexado por posição (`r[0]` em `{'result': [[...]]}`), 37 são uma **string** indexada por chave, e
10 são um campo que não existe no dict (`r['quebra_sigilo']`). Uma memória por assinatura ensinaria a coisa
errada para 47 desses 136 erros.

**Passo 2 — do sintoma ao submecanismo: uma regra determinística por erro.** A função `submecanismo()` olha duas
coisas que estão no próprio trace: o texto da exceção e, nos erros de parsing, **a linha de código que o parser
rejeitou**. Sem LLM, regras em ordem:

- **Erros de parsing.** A linha rejeitada abre uma string (`final_answer("...`, `x = """...`, chave de dict
  entre aspas) ou o erro é `unterminated` / `never closed` / `forgot a comma` → *texto dentro de literal*. A linha
  é texto em português ou markdown (começa com `|`, `#`, `**`, `- `, `1)`; tem crase; ou ≥15% das palavras são
  stopwords do português) → *texto solto no código*. Contém "truncado" → *retorno impresso colado de volta*.
  Nenhuma das anteriores → *erro de sintaxe Python pontual*.
- **Erros de execução.** `KeyError: 0` num dict → *dict indexado por posição*; `string indices must be integers`
  → *string tratada como dict*; `KeyError: 'campo'` → *campo inexistente*; `'list' object is not an iterator` →
  *`next()` sobre gerador*; `variable X is not defined` → *módulo sem import* (se X é `json`, `datetime`...) ou
  *nome não definido*; builtin proibido ou `Import of` → *inventário do sandbox*; `AgentGenerationError`/422 →
  *infra*.

Cada submecanismo aponta para uma **unidade** (um conteúdo). O CSV `triagem_assinaturas.csv` mostra, para cada
assinatura da §2, em quantas unidades ela se divide e quanto cai na dominante.

**Passo 3 — o tipo de cada unidade: a régua é Hu et al. 2025, não o AgentDebug.** O tipo vem da **função do
conteúdo**, na taxonomia do survey *Memory in the Age of AI Agents* (Hu, Liu et al., arXiv 2512.13564, §4 —
trechos conferidos no PDF em 15/09/2026). O survey separa a memória por função, cada uma respondendo uma
pergunta (p. 31): *factual* — *"What does the agent know?"*; *experiential* — *"How does the agent improve?"*.
Duas subcategorias cobrem tudo o que este trace produz:

- **factual · ambiente** (§4.1.2, p. 36): *"entities and states external to the user, encompassing long
  documents, codebases, tools, and interaction traces"*. Critério prático: o conteúdo é **um fato sobre
  ferramentas, sandbox ou documentos, checável contra o próprio sistema** — o schema de retorno, a assinatura da
  ferramenta, a lista de imports.
- **experiencial · estratégia** (§4.2.2, *Insights*, p. 40): *"distilling discrete pieces of knowledge, such as
  granular decision rules and reflective heuristics, from past trajectories"*. Critério prático: o conteúdo é
  **uma regra de como agir**, destilada da falha, que não é fato do ambiente — "montar relatório em variáveis
  antes de `final_answer`".
- **não-memória · harness/infra**: quem falhou foi o parser do harness ou o LLM upstream. O agente não tem o que
  aprender; vira política operacional (retry) ou gatilho de monitoramento. Fica fora da taxonomia do survey, que
  classifica memória *do agente*.

O que ficou de fora do survey, e por quê: *case-based* (§4.2.1) é uma forma de guardar exemplos — qualquer
unidade pode carregar o trace que a originou, não é um tipo de triagem; *skill-based* (§4.2.3) é memória
executável (uma função ou API nova), o que muda o harness — direção v2; *working memory* (§4.3) vale dentro de um
episódio, e as unidades aqui são entre execuções por construção.

**Passo 4 — ocorrência, não erro: a cascata.** Contar erros infla as unidades que o agente repete em sequência:
numa execução de dez/2025 o `managerAgent` errou 10 steps seguidos escrevendo explicação em prosa no lugar do
código. A regra: erros em steps **consecutivos** do mesmo papel na mesma execução formam uma **cascata**; dentro
dela, a mesma unidade repetida conta **uma ocorrência**. Resultado: 498 erros → 437 ocorrências. O princípio de
focar a causa-raiz e não o sintoma de superfície é do AgentDebug (arXiv 2509.25370, p. 2 e p. 8, confirmado por
ablação); **a operacionalização por cascata é nossa**, não do paper.

**Passo 5 — a triagem: três perguntas, na mesma ordem para todas as unidades.**

1. **É memória do agente?** Tipo `não-memória` → fica fora do agente (continua na tabela porque vira política
   operacional).
2. **Tem conteúdo único?** O resíduo de erros pontuais (parêntese trocado, comparação com `None`, argumento errado
   em `final_answer`) não tem uma frase que evite os 9 casos → fora.
3. **Volta em execuções diferentes?** Memória entre execuções só se justifica se o problema recorre: **≥3
   execuções e ≥2 meses** com ocorrência. Abaixo disso → fora.

O que passa nas três é **candidato**. Sensibilidade: com ≥5 execuções e ≥3 meses, só uma unidade muda de lado
("Após step com erro, o que ele definiria não existe") — marcada **limítrofe** na tabela e no gráfico.

**Passo 6 — o antigo Passo 4, respondido com número.** A versão anterior dizia que cinco assinaturas ficaram de
fora por serem "sacos-de-gato" de várias causas — e já avisava que isso era leitura de padrão, não critério
documentado. Medido erro por erro, **nenhuma das cinco era multi-causa**:

| Assinatura excluída antes | Erros | Para onde foram os erros | Leitura |
|---|---:|---|---|
| Sintaxe inválida (prosa vazando no código) | 39 | 28 explicação solta · 7 texto em literal · 3 pontuais · 1 retorno colado | 72% numa unidade; parecia heterogênea porque 67% dos erros vêm logo depois de outro erro do mesmo papel — quase sempre repetição do mesmo |
| Tipo diferente do esperado | 22 | 13 `next()` sobre gerador · 6 retorno como string · 3 pontuais | 59% numa causa única que ainda não tinha nome |
| Texto do documento colado em literal | 20 | 19 texto em literal · 1 retorno colado | mesma causa do candidato "relatório em literal", com outra mensagem de exceção |
| Objeto sem o atributo esperado | 8 | 7 dict iterado como lista · 1 retorno como string | mesma causa do contrato de retorno das ferramentas de documento |
| Módulo usado sem import | 6 | 6 inventário do sandbox | já estava no *conteúdo* do candidato "Inventário do sandbox", só não era contada |

Três eram a mesma causa de um candidato existente, escrita com outra exceção; duas escondiam uma causa nova. O
critério "causa única, conteúdo numa frase" continua certo — o erro era aplicá-lo à assinatura em vez de a cada
erro.

**Passo 7 — o resultado.** 14 unidades: **10 candidatas** (5 factual · ambiente, 5 experiencial · estratégia),
2 não-memória e 2 fora. As candidatas cobrem 447 dos 498 erros (90%) e 92% dos tokens gastos em steps com erro.
O que mudou em relação à tabela anterior de 7 linhas:

- **Três candidatas novas com peso real**: "Retorno pode chegar como string" (47 erros, 36 execuções, 7 meses,
  7 papéis — a 3ª maior em tokens, 2,11M), "`next()` sobre expressão geradora falha no sandbox" (13 erros) e
  "Campo inexistente no retorno estruturado" (10 erros, `quebra_sigilo` 7×, 8 deles no `RespostaBacen`). Mais
  duas menores: "Explicação nunca solta no bloco de código" e "Nome usado sem ter sido definido".
- **O contrato de retorno encolheu e mudou de escopo**: 136 → 96 erros, e **os 96 são todos do
  `ConversationAgent`**. O que parecia o mesmo erro em `CalculoCivel` e `RespostaBacen` é outro mecanismo (string
  indexada por chave; campo inexistente).
- **Contagens que subiram por coerência com o próprio conteúdo**: "Inventário do sandbox" 11 → 17 (o conteúdo já
  citava `json` e `openpyxl`, mas só uma assinatura era contada); a política de retry 6 → 7 (o conteúdo já citava
  422, mas o HTTP 422 não entrava).
- **"Variável não existe após erro" se dividiu**: 5 casos em que o step anterior falhou (a unidade limítrofe) e
  5 nomes nunca definidos (`Observation`, `result`, funções auxiliares).
- **Ressalva sobre "Explicação nunca solta no bloco de código"**: 26 dos seus 33 erros (92% dos tokens) são de
  dez/2025, e 7 das 12 ocorrências vêm logo depois do erro de protocolo do harness daquele incidente — é, em boa
  parte, a reação do agente ao incidente. Ela passa na triagem pelas 4 ocorrências próprias de abr–jun/2026, mas
  o volume grande é resíduo.

**Passo 8 — o gráfico.** Uma barra por unidade, agrupadas pela decisão (candidatas / não-memória / fora) e
ordenadas por tokens dentro de cada grupo. Cor pelo tipo — factual = azul, estratégia = laranja, não-memória =
verde — e cinza neutro para "fora", que não é série. As três cores são os slots 1–3 da paleta categórica em
ordem fixa, validados com `validate_palette.js` (skill dataviz): passa em tudo; o aviso de contraste do verde é
coberto pelo rótulo direto em cada barra. O rótulo mostra tokens e **ocorrências**, não erros, porque ocorrência
é a evidência que a triagem usa.

**Passo 9 — a leitura.** As duas maiores unidades — "Texto longo nunca dentro de literal de string" e "Retorno das
ferramentas de documento é dict" — somam 57% dos erros e 50% dos tokens. Continuam sendo a aposta mais forte, com
números menores que os 59%/59% da tabela anterior. O tipo não é cosmético: uma unidade *factual · ambiente* pode
ser minerada do próprio trace e checada contra o sistema (o schema real sai dos erros); uma unidade *experiencial
· estratégia* precisa ser escrita como regra e só se valida vendo se o erro para de voltar. As duas linhas de
não-memória (retry e protocolo do harness) seguem fora do agente pelo mesmo motivo de antes: nenhuma seria
escrita como "o agente deveria saber X".

**Ressalva de método (substitui a ressalva anterior).** Tudo aqui é classificado pelo que o trace **mostra** — a
mensagem de exceção e a linha que falhou —, não pelo raciocínio do agente. O AgentDebug classifica de outro jeito:
lê o *thought* e decide em qual módulo cognitivo o erro nasceu (Detector Prompt, Fig. 14, p. 19). Não fizemos
isso. Por isso a triagem responde **"que conteúdo evitaria este erro"**, e não **"em que parte do raciocínio ele
nasceu"**. Duas consequências: (a) só entram erros que levantaram exceção — erros silenciosos (código que roda e
entrega errado) ficam de fora por construção (ver §5 do relatório); (b) a regra de cascata olha só o step
imediatamente anterior, então uma variável definida num step que falhou dois steps antes aparece como "nome
nunca definido", não como "estado perdido após erro".

---

## 8 · Do sintoma à correção — o que este pipeline, o TRAIL e o AgentDebug realmente entregam

Registrado em 15/09/2026, consolidado depois de três rodadas de correção na mesma sessão — a versão final desta
seção, checada contra citação real dos dois PDFs (não só dos fichamentos). Um erro passa por três degraus, e
cada um responde uma pergunta diferente:

**A analogia médica, na forma final.** "Tenho gripe" é saber que há um problema. Febre e dor no corpo são o
**sintoma** — o que o corpo emite sem precisar interpretar nada. Examinar e concluir "é uma amigdalite, a
garganta está inflamada porque X" é o **diagnóstico** — tem uma forma curta, reaproveitável, pra contar casos
("amigdalite") e uma forma longa, específica daquele paciente ("inflamação bacteriana na amígdala direita,
provável foco em Y"). A receita — "tome amoxicilina por 7 dias" — é a **correção**: não descreve o problema, diz
o que fazer diferente.

| Degrau | Pergunta | Exemplo real — `RespostaBacen`, execução `1be966e7…`, step 7 | Como se obtém neste pipeline |
|---|---|---|---|
| **1 · Sintoma** | O que o Python reclamou? | `"Could not index … KeyError: 'quebra_sigilo'"` | regex na mensagem crua (`classify()`, §2 do notebook) |
| **2 · Diagnóstico — rótulo** | Que *tipo* de erro é esse (reaproveitável, dá pra contar)? | "Campo inexistente no retorno estruturado" | regra fixa sobre a mensagem + linha rejeitada, sem LLM (`submecanismo()`, §7) |
| **2 · Diagnóstico — descrição** | O que aconteceu, *neste caso específico*? | a ferramenta `validar_quebra_sigilo` devolve `vazamento_sigilo`; o agente pediu `quebra_sigilo` | hoje: hipótese escrita à mão por unidade (§7, "conteúdo proposto"); "de verdade" ainda não construído (`04-roadmap.md`) |
| **3 · Correção** | O que o agente deveria fazer diferente da próxima vez? | "ao ler o retorno de `validar_quebra_sigilo`, usar a chave `vazamento_sigilo`, não `quebra_sigilo`" | **não temos ainda** — é o que a unidade de memória precisa virar |

**As duas lentes, antes de comparar campo a campo (adicionado 16/09/2026, a pedido do Rafael).** A tabela campo a
campo abaixo compara o que cada *schema de saída* carrega — é uma comparação de **produto**. Antes dela, uma
distinção mais estrutural, de **método**, que a comparação de campos não mostra por si só:

- **AgentDebug analisa em nível de módulo cognitivo, com busca dirigida a um alvo causal.** A taxonomia nasce de
  impor uma arquitetura modular ao próprio agente (tags `<memory>/<reflection>/<plan>/<action>` forçadas no
  prompt, Fig. 17–19) — cada erro é rotulado pelo módulo interno em que nasceu. E o objetivo não é catalogar todo
  erro; é achar **um** passo — o *critical error*, "the earliest step whose correction directly prevents the
  final failure" (§3.2, já citado acima) — porque o racional do paper inteiro é que a propagação de erro é o
  que mais compromete a confiabilidade do agente (Key Insight, verbatim, já citado no fichamento: *"Error
  propagation is the primary bottleneck in LLM agent reliability. Early mistakes rarely remain confined;
  instead, they cascade into subsequent steps..."*). Método: acha a raiz de uma cascata, não o inventário dela.
- **TRAIL analisa em nível de sistema/observabilidade, com cobertura exaustiva.** O trace já chega estruturado
  como spans OpenTelemetry/OpenInference — uma chamada de LLM ou de ferramenta por span (fichamento
  `trail-2505.08638.md`, "O schema é reusável..."). A tarefa não busca uma raiz causal única: é produzir, para
  **cada** span do trace inteiro, `category`+`location`+`evidence`+`description`+`impact` — um LLM-as-judge
  que audita exaustivamente, sem hierarquia entre os erros achados além da escala de impacto. Método: cataloga
  tudo que já aconteceu num trace já estruturado, não busca a causa de um fracasso.

São lentes diferentes, e ambas fazem sentido pro projeto, sem que uma precise vencer a outra: o TRAIL responde
**"quanto do que aconteceu no trace estamos vendo"** (cobertura, ponto cego — §4 do fichamento, os 59% de erros
estruturalmente invisíveis à nossa `classify()`); o AgentDebug responde **"qual passo, corrigido, teria evitado
a cascata"** (causa raiz, e daí a política de escrita "uma unidade de memória por cascata, na raiz" — §7 acima).
A comparação campo a campo que segue é sobre o produto de cada método, não substitui esta distinção de método.

**Onde TRAIL e AgentDebug entram — os dois cobrem o degrau 2, cada um com um campo a mais que o outro não tem:**

| Campo | TRAIL (Apêndice A.11, por span) | AgentDebug (Stage 1, por módulo/passo) | AgentDebug (Stage 2, por trajetória) |
|---|---|---|---|
| Rótulo reaproveitável | `category` (tipo-folha da taxonomia) | `error_type` | `error_type` (repetido, do passo crítico) |
| Descrição específica do caso | `description` — verbatim, sempre causal: *"The agent's thought said: 'I'll now call search_agent...' However, the 'Code:' generated printed the task through the interpreter instead"* | `reasoning` — mas verbatim é *"Explanation of why THIS IS AN ERROR based on the definition"*, justifica a classificação, não diagnostica o caso | `root_cause` — verbatim: *"Concise description of the fundamental problem"* |
| Severidade | `impact` ∈ {HIGH, MEDIUM, LOW} | **não tem** | **não tem** (`cascading_effects[].impact` é texto livre por passo seguinte afetado, não uma escala — nem `confidence: 0.0–1.0`, que é confiança na classificação, não gravidade da consequência) |
| Correção prescritiva | **não tem campo dedicado** — o único "should have" achado está num exemplo ilustrativo do prompt (não nos 7 exemplos reais do dataset), inconsistente com a própria instrução do campo | **não tem** — Stage 1 só classifica | `correction_guidance` — verbatim: *"Actionable advice for the agent to avoid the same mistake"* |

Ou seja: **os dois papers ficam no degrau 2** (rótulo + descrição do caso) — nenhum "é" o mecanismo e o outro "é"
o motivo, como uma versão anterior desta seção chegou a dizer (corrigido depois de checar contra os PDFs). O que
muda entre eles é qual peça extra cada um carrega: **o TRAIL tem `impact` (severidade) e o AgentDebug não; o
AgentDebug tem `correction_guidance` (degrau 3) no Stage 2, e o TRAIL não tem equivalente.**

**Para que serve `impact`, concretamente.** É a gravidade da consequência, não a frequência do erro — a
distinção que falta neste pipeline hoje. No TRAIL: 304 erros HIGH (36,1%), 363 MEDIUM (43,2%), 174 LOW (20,7%) —
mas a distribuição por família inverte a intuição de "erro que aparece mais é mais grave": `Hallucinations` é
89% HIGH, `Output Generation` (a família que a nossa esteira mais vê via exceção) é só 12% HIGH e 44% LOW. Sem um
campo assim, 223 `SyntaxError` baratos e recuperáveis pesam, na nossa priorização hoje, o mesmo que uma
alucinação de número de processo — que é rara mas cara. É exatamente o "o que mais falta" já registrado no
fichamento do TRAIL (`../literature/trail-2505.08638.md`, "O schema é reusável no nosso trace?").

**Por que isso importa pra frente, não só pra fechar a discussão de hoje.** As duas estruturas, somadas, dão um
schema melhor do que qualquer uma sozinha pro que falta na §7: `category`/rótulo já temos (a unidade); `location`
já temos (`exec_id`, `role`, `step`); `evidence` temos parcialmente (`err_msg`, falta pra erros sem exceção);
`description` (degrau 2, caso específico) é hoje escrita à mão, sem método; `impact` não temos; `correction_
guidance` (degrau 3) não temos, e é ele que **é** a unidade de memória, não um campo a mais — o candidato de
memória de verdade é o `correction_guidance` de cada unidade, validado, não a unidade em si. Isso vira o schema
proposto pra fase "Construir os candidatos de memória de verdade" (`04-roadmap.md`).

**Onde cada degrau é usado neste pipeline hoje:**

- **Sintoma** — inventário e custo, onde "qual erro" não muda a resposta: distribuição geral (8.1), duração por
  família (§2.3), forma da chamada (§3.2). Os gráficos que nem usam etiqueta (8.3, 8.6, 8.7, 8.9 a 8.12) não
  mudam.
- **Diagnóstico — rótulo** — repetição e lição: mecanismo por papel (§2.2 e 8.8), custo por mecanismo (§3 e 8.5),
  reincidência dentro da execução (§3, Passo 8), reincidência mês a mês (§6 do notebook e 8.4), a triagem de
  candidatos (§7).
- **Diagnóstico — descrição** e **Correção** — não entram em gráfico ainda. Decidem *onde* vai o conserto
  (documentação da ferramenta, memória, ou mudança no ambiente) e *o que* a lição diz. Fase seguinte, com juiz
  LLM validado contra anotação humana (`04-roadmap.md`).

**Nota de vocabulário.** Em `04-roadmap.md` a mesma escada tem outra numeração: "camada 0" é a exceção crua
(sintoma), "camada 1" é o diagnóstico-rótulo (`classify()` e, desde 15/09, o `submecanismo()` mais fino — teto
do v1 determinístico), "camada 2" cobre diagnóstico-descrição e correção juntos — ainda não decidido lá se
precisam de dois passos de LLM separados ou um só.

**Sintoma não foi um passo errado — é outro degrau de dado, válido por si.** A sequência desta sessão (agrupar
por sintoma → achar o limite → reagrupar por mecanismo → achar mais uma camada no mecanismo) pode ser lida como
"o sintoma estava errado". Não estava. `classify()` é determinístico, auditável, cobre 497 dos 498 erros, e
responde de verdade as perguntas pra que foi usado: quantos erros, quantos tokens, qual duração (8.1, §2.3,
§3.2 — nenhuma mudou hoje). O que mudou foi a pergunta, não a validade do corte anterior: "quantos erros
existem" e "qual lição escrever" pedem granularidades diferentes, e dá pra medir exatamente onde isso muda a
resposta (§2.2 — dois papéis com a causa trocada; §3 Passo 8 — 11,9% vs. 13,5%; §7 Passo 4 — cinco assinaturas
"sem causa única" que na verdade tinham uma). **O achado metodológico da sessão é esse: a granularidade certa
depende da pergunta, e descobrir isso é ciência incremental normal, não correção de erro.** Os gráficos por
sintoma continuam publicados, corretos e citáveis como estão. O ajuste ainda pendente (`04-roadmap.md`, "grupo
1") é só de rótulo: dar às 4 categorias da `classify()` que hoje afirmam uma causa só parcialmente verdadeira um
nome que descreva 100% do que está dentro — não trocar o corte por sintoma pelo corte por mecanismo no relatório
inteiro.

---

## A continuação: mineração das unidades nº2/nº10

A análise que era a §9 deste documento — a mineração do schema real das unidades nº2 ("Retorno das ferramentas
de documento é dict") e nº10 ("Campo inexistente no retorno estruturado") — virou documento próprio em
18/09/2026: [`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md). Separada porque é uma
análise distinta, não mais uma seção: pré-registrada (réguas fixadas antes de olhar o dado), com evidência por
caso em `../pipeline/resultados/evidencia/11.*` e produto final (`unidades_memoria.json`). A numeração "§9" foi
preservada lá — referências a "§9 dos racionais" seguem valendo, agora naquele arquivo. Os números dela estão em
[`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) e o pipeline no notebook
[`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb).

---

## Onde ver os números e o código de cada teste

Este documento explica a lógica; [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.5–1.6 tem a
tabela completa de sete testes, o resultado de cada um, e como reproduzir cada script.
