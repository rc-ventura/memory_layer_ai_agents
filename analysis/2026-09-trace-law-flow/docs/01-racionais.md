# Racionais — a lógica por trás da análise, em linguagem simples

**Para que serve este documento:** explicar *por que* a análise foi conduzida nesta ordem e *o que significam*
os conceitos usados — em prosa acessível, para reler antes de explicar a alguém (tutor, reunião) ou para você
mesmo reler depois sem precisar decifrar tabela técnica. Para os números exatos, os scripts e os testes
executados, ver [`03-procedimento-validacao.md`](03-procedimento-validacao.md) — os dois documentos se
complementam: este é o "por quê", aquele é o "como, com que número".

**O que este documento cobre — e o que não cobre.** Têm passo-a-passo próprio: o achado central (§3), o
sucesso verificado por conteúdo (§4), os cinco cortes de custo/eficiência (§5) e a assinatura de erro por
papel + duração (§6), além dos conceitos de robustez (§2). **Não têm** tratamento passo-a-passo próprio, só
cobertura conceitual no §1: a recuperação 0/1.550, a reincidência entre execuções, o teste ToolScan IAN/IAV,
os detectores silenciosos (Result-Ignore / RAC / Tool-Skip) e a tabela de candidatos — para esses, o caminho
é a célula correspondente do notebook mais o [`02-relatorio-achados.md`](02-relatorio-achados.md). Essa
assimetria foi apontada por auditoria independente em 08/09/2026; o §3 (o mais importante dos que faltavam)
foi escrito em resposta.

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
   - **Fornecer um framework de interpretação** — a ideia do AgentDebug de que "o módulo que produziu o erro
     roteia o tipo de memória" (procedural vs. semântica vs. experiencial) é o que organiza a tabela de
     candidatos no relatório.

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
        ├─ 51  (11,9% dos 430)  → mesma causa      ← reincidência: o número-manchete
        └─ 25                    → causa diferente   ← propagação
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

### O que isso prova — e o que não prova

**Prova:** o feedback dentro da trajetória existe, é lido, e não basta. Em 11,9% dos casos onde o agente
comprovadamente leu o erro, ele caiu na mesma categoria de novo. Junto com a reincidência entre execuções
(mesma assinatura reaparecendo por 8-9 meses), é o caso empírico direto para memória externa persistente.

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
4. **Uma divisão por papel:** `métrica(papel) = Σtok(papel) / Σcham(papel)`. Sai **um número para cada papel**
   (Passo 4) — **não** uma divisão única do dataset inteiro. (A divisão global, `Σtok(tudo) / Σcham(tudo)`, é
   outra coisa — a "razão agregada" do Passo 5.)

**Ressalva.** Steps sem nenhuma chamada de ferramenta (`n_calls = 0` — raciocínio puro, formatação) entram no
numerador mas não no denominador. É proposital — o número cobra o overhead de contexto/raciocínio às chamadas
("quantos tokens custa produzir uma invocação de ferramenta real deste papel") — mas infla o valor; a versão
estrita (só steps com `n_calls ≥ 1`) daria menos.

**Passo 4 — o resultado.** `CalculoCivel`: 141.673 tokens por chamada de ferramenta. `CalculoTrabalhista`:
50.624. O múltiplo que dá escala a esses números é sempre contra a **mediana, entre execuções, da razão
tokens/chamada** — o `12.192` do Passo 5, que é uma razão, **não** o custo de uma execução inteira (esse é da
ordem de dezenas de milhares de tokens — ver §3.5): `CalculoCivel` gasta **11,6×** mais tokens por chamada que
a execução mediana; `CalculoTrabalhista`, **4,2×**. Cruzando com a taxa de erro já conhecida:
`CalculoTrabalhista` tinha taxa de erro normal (9%) — a ineficiência por chamada é um problema que a taxa de
erro sozinha nunca revelaria.

**Passo 5 — a correção de rótulo, achada ao revisar antes de publicar.** O primeiro número que calculei
("mediana geral: 21.420") estava **mal nomeado** — não era mediana, era razão agregada (soma de tudo / soma
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

### 2.2 · Assinatura de erro por papel

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

**Passo 4 — a operação exata.** `pd.crosstab(papel, assinatura)` sobre os 498 erros já classificados (mesma
taxonomia de §2 acima); dividir cada linha pela soma daquela linha; multiplicar por 100. Manter só papéis com
volume mínimo (`role_vol >= 5`) pra não exibir percentual de amostra ínfima.

**Passo 5 — o resultado.** `CadastroTrabalhista`: 94% dos erros são "argumento posicional" (n=18).
`CalculoCivel`: 76% são "retorno é dict" (n=17). `managerAgent`: 56% são "string não fechada" (n=180, mais
concentrado que a média geral de 45% pra essa causa).

**Passo 6 — teste de robustez do corte `role_vol >= 5`.** Recalculei com cortes de 3, 10 e 15. Os cinco
papéis mais concentrados (`managerAgent`, `ConversationAgent`, `CalculoCivel`, `CadastroTrabalhista`,
`RespostaBacen`) aparecem idênticos, com os mesmos percentuais, em todos os quatro cortes testados. **Robusto.**

**Passo 7 — a leitura.** No dataset inteiro, "argumento posicional" é só 7% de todos os erros — parece
secundário. Mas dentro de `CadastroTrabalhista` especificamente, é quase o problema inteiro. A mesma causa
pode ser "pequena" no agregado e "dominante" num recorte — e o recorte que importa pra decidir onde escrever
memória é o papel, não o dataset inteiro.

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

## Onde ver os números e o código de cada teste

Este documento explica a lógica; [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.5–1.6 tem a
tabela completa de sete testes, o resultado de cada um, e como reproduzir cada script.
