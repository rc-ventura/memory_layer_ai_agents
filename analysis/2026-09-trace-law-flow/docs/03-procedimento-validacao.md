# Procedimento de validação — do achado agregado ao caso no trace cru

**Para que serve este documento:** antes de apresentar os achados de
[`02-relatorio-achados.md`](02-relatorio-achados.md) numa reunião — e antes de reusar este mesmo pipeline pra
construir os candidatos reais de memória —, este é o roteiro pra você formar opinião própria sobre cada peça:
o código que gerou os gráficos, e os papers que sustentam a categorização. Nada aqui substitui você ter
revisado; é o caminho mais curto pra revisar direito. Este documento é o "como, com que número" — para o
"por quê" em linguagem acessível (o que é um teste de robustez, por que algo é corrigido vs. retirado), ver
[`01-racionais.md`](01-racionais.md).

O procedimento tem duas frentes independentes — uma mecânica, outra de leitura — e um eixo que atravessa as
duas: **nunca apresentar um número agregado sem saber apontar o caso concreto no trace cru que o sustenta.**

---

## Frente 1 — Auditar o pipeline (não depende de nenhum paper)

Tudo aqui é recomputável. Se o código está certo, os gráficos estão certos — não tem "confiar em mim"
envolvido, só verificação mecânica.

### 1.1 · Abra o notebook de verdade

O ambiente Python do projeto é gerenciado por `uv`, a partir do `pyproject.toml` na raiz do repo (`.venv/`,
git-ignored; `uv.lock` versionado para reprodutibilidade). Substituiu uma versão anterior baseada em
`/tmp/trace_analysis/venv`, que não sobrevive entre sessões (16/09/2026).

```bash
cd /Users/rafaelventura/ICT-ITAU/memory_layer_ai_agents   # raiz do repo, onde está o pyproject.toml
uv sync                                                     # cria/atualiza .venv com pandas/numpy/matplotlib/jupyterlab
uv run python -m ipykernel install --user --name memory-layer-ai-agents \
    --display-name "Python (memory-layer-ai-agents)"        # só na 1ª vez por máquina
uv run jupyter lab analysis/2026-09-trace-law-flow/pipeline/analise_trace_esteira_juridica.ipynb
```

No Jupyter, selecione o kernel **"Python (memory-layer-ai-agents)"** — não "Python (venv)" (kernel legado de
outro projeto, `CrewAI/venv`, sem as libs desta análise; causa o `ModuleNotFoundError: matplotlib` se
selecionado por engano). Para rodar uma célula fora do Jupyter, ad hoc: `uv run python -c "..."` a partir da
raiz do repo já usa o mesmo ambiente.

### 1.2 · Para cada gráfico da seção 8, leia a célula de agregação logo acima

Não a célula de `plt.plot`/`plt.bar` — a célula anterior, onde os dados são filtrados e somados. Confirme que
o número impresso em texto (seções 1–7) bate com a barra/rótulo do gráfico. Esse é o check mais barato: pega
qualquer divergência entre "o que o texto diz" e "o que o gráfico mostra".

### 1.3 · Audite a função `classify()` (seção 2 do notebook)

**A checagem de maior alavancagem.** Toda a taxonomia — os 6 gráficos, a tabela de candidatos, o relatório
inteiro — depende dessa função, que é uma cadeia de `if/elif` procurando substring na mensagem de erro. É
regex simples, com risco real de falso positivo. Pegue ~20 `err_msg` aleatórios de
`resultados/erros_classificados.csv` e veja se você classificaria do mesmo jeito. Qualquer discordância é o
ponto certo pra ajustar antes de reusar o pipeline pra gerar candidatos de verdade — errar aqui contamina tudo
a jusante.

### 1.4 · Recompute um ou dois números por fora do notebook

"Por fora" quer dizer: um caminho de código **diferente** do pipeline — não reusar `classify()`, não usar
pandas do jeito que o notebook usa — só pra provar que o número não é artefato de um bug específico da minha
lógica. Exemplo já feito, com `csv.DictReader` puro (sem pandas, sem JSON schema chique): contar, por *step*,
quantas vezes a string `"Could not index"` aparece dentro do campo `error.message` de cada step. Resultado:
**136 — bateu exato** com o número do relatório, por um código totalmente diferente.

Segundo exemplo, e por que ele vale mais do que parece: `audit/scripts/audit_recompute3.py` recomputa os
tokens por chamada de ferramenta (§3.3) com `csv.DictReader` + `ast` puros, sem pandas e sem o notebook. Ele foi
escrito na auditoria independente de 08/09 e **sempre somou os tokens antes do `try/except` do parse** — a regra
que só virou oficial em 15/09. Rodado hoje contra o notebook corrigido, os três números batem: 27.988, 18.775 e
agregada 22.280. Antes de 15/09 não batiam, e a linha 33 daquele relatório marcou "idênticos ✅" porque comparou
os valores por papel (inclusivos, do script) com o agregado (exclusivo, copiado do notebook) — é exatamente o
tipo de divergência que um recomputo por fora existe pra pegar, e que só pega se os números forem conferidos
**um a um**, não em bloco.

**Armadilha a evitar:** um `grep` cru no arquivo inteiro (sem entrar no JSON) deu **580**, não 136. Isso não é
erro — é porque a mensagem de erro fica ecoada no `model_input_messages` de vários steps seguintes (em média
~4,3× por erro), então contar "onde a string aparece no arquivo" mistura "o erro aconteceu aqui" com "o erro
foi lembrado ali depois". Reforça o achado do §4 do relatório, mas não serve como recomputo do número — pra
recomputar, sempre filtrar pelo campo certo (`error.message` do próprio step), não pelo texto solto.

### 1.5 · Teste de robustez do número mais importante (já feito — e mudou o número)

Os 86,3% (mensagem chegou ao contexto do step seguinte) usavam correspondência de substring cortando os
primeiros 45 caracteres — sensível a como a string é cortada. Rodei três variantes independentes (nenhuma
reusa `classify.py` nem o notebook, código à parte, direto no trace cru):

| Método | "Chegou ao contexto" | "Repetiu igual" |
|---|---:|---:|
| Prefixo (45 primeiros chars) — método original | 86,3% | 13,7% |
| Sufixo (45 últimos chars — o detalhe específico da exceção) | 84,9% | 4,3% |
| **Categoria da taxonomia (`classify()`)** — método correto | — | **11,9%** |
| Mecanismo (unidade da §7 dos racionais) — quarta régua, 15/09/2026 | — | 13,5% |

O "chegou ao contexto" é robusto: os dois métodos convergem em ~85–86%. O "repetiu" **não era robusto**: caiu
de 13,7% pra 4,3% trocando prefixo por sufixo. Investigando exemplos concretos (com `drill_down.py`), a causa
ficou clara — prefixo estava pegando o texto genérico de abertura da exceção ("Code execution failed at
line..."), não o erro específico; sufixo era rigoroso demais e perdia repetições da mesma causa em código
diferente. O teste certo é comparar pela **categoria da taxonomia**, que é o nível de granularidade que o
resto do relatório usa — deu **11,9% (51 casos)**, e foi o número que corrigiu o relatório e o notebook
(commit desta correção: seção 5 do notebook, `same_sig` via `classify()`).

**Quarta régua, 15/09/2026 — por mecanismo.** Depois que a triagem de candidatos passou a atribuir um mecanismo a
cada erro ([`01-racionais.md`](01-racionais.md) §7), a mesma pergunta foi refeita um nível abaixo: `same_mec` na
seção 5 do notebook. Deu **58 (13,5%)**. As duas réguas concordam em 65 das 76 repetições; as 11 divergências
foram abertas com `drill_down.py caso`: 9 são mensagens diferentes para a mesma confusão (ex.: `docs[0][0]` e
depois iterar um documento como lista, execução `cd794f02…`), 2 são a mesma mensagem para lições diferentes
(campo inexistente e depois texto de erro indexado, execução `95344639…`). Não é a divergência de 3× do
prefixo × sufixo — as réguas convergem. A manchete continua 11,9%; ressalva: 20 dos 58 vêm do laço de out/2025.

**A lição pra qualquer novo número que você for defender:** teste sempre com pelo menos duas heurísticas de
correspondência diferentes antes de reportar como firme. Se divergirem muito, investigue exemplos concretos
(`drill_down.py caso`) até entender por quê — normalmente aponta pro método errado, não pro dado errado.

### 1.6 · Quais achados precisam de teste de robustez — e quais não

**O critério:** um teste de robustez só é necessário onde o número depende de uma **escolha arbitrária de
quem analisou**. Onde é contagem direta, não há o que variar — é robusto por construção.

**Robustos por construção (não precisam de teste):** tokens por execução (146k vs 48k), 0 de 1.550
trajetórias terminando em erro, coeficiente de propagação 1,8×, taxa de erro por papel, reincidência por mês,
contagens de steps/execuções/tokens. Nenhum embute uma decisão de "o que conta como igual".

**Dependentes de escolha (precisam de teste):** o quadro abaixo é o estado atual.

| Achado | Escolha arbitrária embutida | Teste | Veredicto |
|---|---|---|---|
| "Mensagem chegou ao contexto" — 86,3% | como comparar duas mensagens | prefixo vs sufixo | ✅ **robusto** (86,3% vs 84,9%) |
| "Repetiu o mesmo erro" — 11,9% | idem | 3 heurísticas + mecanismo (15/09) | ⚠️ **corrigido** de 13,7% → 11,9% (ver §1.5); por mecanismo 13,5% — ✅ converge |
| `classify()` — base de toda a taxonomia | ordem das condições `if/elif` | ambiguidade de regras | ✅ **robusto, e a ordem é o mecanismo** (ver abaixo) |
| Reasoning-action mismatch — 45 steps | a lista de palavras de "sucesso" | 3 listas de tamanhos diferentes | ❌ **NÃO robusto — não apresentar** (ver abaixo) |
| Tool-Skip — 14 execuções | minha lista de 43 ferramentas | comparação com o system prompt | ❌ **inventário errado — refazer** (ver abaixo) |
| Result-Ignore — 103 | definição de "ignorado" | 3 variações + troca de inventário | ✅ **robusto** (ver abaixo) |
| RAC — 125 (era 461) | definição de "redundante" + inventário | 3 variações + troca de inventário | ⚠️ **corrigido** de 461 → 125 (ver abaixo) |
| §2.2 mecanismo por papel (94%/76%/62%; por mensagem, até 14/09, era 94%/76%/56%) | corte `role_vol >= 5` | cortes de 3, 5, 10, 15 | ✅ **robusto** — idêntico em todos (o corte só escolhe quais papéis aparecem) |
| §2.3 duração "Falha do LLM interno" — 115s | corte de amostra mínima por família | `n >= 3, 10, 20, 50` | ❌ **NÃO robusto — retirado como número, virou hipótese** (só 6 pontos, variância de 3 ordens de magnitude) |
| §3.5 desperdício % por papel | corte `tok_total >= 50.000` | cortes de 10k, 50k, 100k | ✅ **robusto** — ranking idêntico |
| §3.3 tokens por chamada, por papel | o que fazer com o step cujo código **não parseia** (sem árvore, sem como contar chamadas) | as duas contagens defensáveis: descartar o step inteiro × somar os tokens dele com `n_calls = 0` | ⚠️ **escolha fixada em 15/09** — contar os tokens. Inclusiva: 27.988 / 18.775 / agregada 22.280; exclusiva: 27.062 / 17.592 / 21.420. ✅ **robusto no que a seção conclui**: ranking, os múltiplos 11,6× e 4,2×, a mediana (12.192) e o destaque laranja do 8.9 são idênticos nas duas. Racional em [`01-racionais.md`](01-racionais.md) §3.3, Ressalva 2 |
| §7 dos racionais — candidatos a memória | limiar de recorrência (≥3 execuções e ≥2 meses) | ≥5 execuções e ≥3 meses | ✅ **robusto** — só 1 das 10 candidatas muda de lado (marcada limítrofe) |
| `submecanismo()` — base das análises por mecanismo | ordem das regras e o limiar de 15% de stopwords | 6 casos abertos com `drill_down.py` (15/09) | ⚠️ **conferido por amostra, não testado por variação** — os 6 casos batem; variar as regras ainda não foi feito |
| §9 de `06-racionais-mineracao-unidades-n2-n10.md`, Passo 1 — de qual ferramenta vem cada erro (nº2: 94,8%; nº10: 70%) | a regra de rastreio da variável (AST; comando → step → steps anteriores) | conferência manual de todos os casos fora da dominante + amostra de 4 da dominante (16/09) | ⚠️ **conferido por amostra, não testado por variação** — as atribuições conferem; 5 (nº2) e 1 (nº10) ficam não resolvidos; o veredito da nº2 resiste ao pior caso (ver §1.7) |
| §9 de `06-racionais-mineracao-unidades-n2-n10.md`, Passo 2 — schema lido da mensagem | o método de leitura do objeto impresso | `ast.literal_eval` × regex tolerante | ✅ **robusto** — 89/89 e 7/7 concordam (ver §1.7); a descrição da forma foi **corrigida** (listas mistas) |
| §9 de `06-racionais-mineracao-unidades-n2-n10.md`, addendum ao Passo 2 — a chave está no system prompt | a forma de presença de texto | palavra solta × entre aspas × como chave (`'chave':`) | ❌ **formas frouxas não robustas** — `result` e `justificativa` aparecem só como prosa/valor; reportada a forma estrita (ver §1.7) |
| §9 de `06-racionais-mineracao-unidades-n2-n10.md`, Passo 3 — tipo do conserto no step seguinte | o que conta como "o mesmo objeto" | abertura dos casos que contrariavam o esperado (19 "repetiu" sem erro seguinte) | ⚠️ **corrigido** — reatribuição e guarda de tipo; 1 caso não inspecionado (ver §1.7) |

### O método por trás de cada teste — o racional

Cada linha da tabela acima seguiu a mesma receita, com quatro passos:

1. **Nomear a escolha arbitrária.** Toda vez que uma análise usa uma regra que eu inventei — uma janela de
   texto (primeiros/últimos N caracteres), uma lista de palavras-chave, uma lista de nomes conhecidos, um
   critério de inclusão/exclusão — essa regra é uma decisão minha, não um fato do trace. O primeiro passo é
   identificar exatamente qual escolha está embutida no número.
2. **Construir pelo menos uma alternativa igualmente defensável.** Não uma alternativa qualquer — uma que um
   revisor cético proporia com a mesma razoabilidade. Ex.: se comparo mensagens pelo prefixo, a alternativa
   óbvia é comparar pelo sufixo (o detalhe específico costuma ficar no fim, não no início). Se uso uma lista
   de palavras de 8 termos, as alternativas óbvias são uma lista mais estrita e uma mais ampla.
3. **Recalcular a MESMA métrica com a alternativa**, em código à parte (não editando a análise original) —
   assim dá pra comparar os dois números lado a lado sem um contaminar o outro.
4. **Decidir pelo resultado, nunca pela média:**
   - Os números **convergem** (variam pouco, tipicamente <5 pontos percentuais) → o achado fala sobre o
     trace, é **robusto**, reporta como está.
   - Os números **divergem muito** → o achado estava falando sobre a minha escolha, não sobre o agente.
     Não fazer média nem escolher "o do meio" — **investigar exemplos concretos** (`drill_down.py caso`) até
     entender por que divergem. Normalmente isso revela qual das duas heurísticas (às vezes nenhuma) mede o
     conceito certo, e às vezes revela um terceiro método mais correto que nenhuma das duas alternativas
     originais (foi o caso do 86,3%/11,9% — nem prefixo nem sufixo eram certos; a `classify()` era).

**Uma variação do mesmo método**, usada no inventário de ferramentas: em vez de comparar duas heurísticas
inventadas, procurei se existia uma **fonte autoritativa dentro do próprio trace** (o system prompt declara as
ferramentas) e comparei minha lista observada contra ela. Sempre que uma lista feita à mão puder ser checada
contra algo que o próprio dado declara, isso vale mais que qualquer heurística alternativa — não é "mais uma
opinião", é o padrão-ouro.

**Como cada execução foi feita, em concreto:** todo teste rodou como script Python isolado, lendo o
`.csv.xz` direto via `csv.DictReader` + `json.loads` — nunca reaproveitando `classify()` do notebook nem
`pandas` da análise original. Isso importa porque um teste que reusa o mesmo código da análise não é
independente: replicaria um eventual bug em vez de expô-lo.

#### Teste da `classify()` — a ordem importa, mas é ela que faz o trabalho

73% das mensagens casam com **mais de uma** regra, então o rótulo depende da ordem. Isso parece frágil, mas
olhando as combinações fica claro que é intencional:

| Combinação | n | Regra vencedora |
|---|---:|---|
| String não fechada + SyntaxError genérico | 159 | a específica |
| Retorno é dict + KeyError | 98 | a específica |
| Retorno é dict + TypeError | 38 | a específica |
| Argumento posicional + ValueError | 35 | a específica |

Uma string não fechada **é** um `SyntaxError`; um "Could not index" **é** levantado como `KeyError`. A ordem
coloca a causa específica antes do tipo genérico de exceção — **é exatamente isso que converte sintoma em
causa-raiz.** Se você inverter a ordem, reproduz a taxonomia da v1 (KeyError 98, ValueError 37 — os números
batem exatamente). Robusto, e vale saber explicar isso se perguntarem na reunião.

#### Teste do reasoning-action mismatch — reprovado, e o problema não era só a lista

**O que se afirmava:** "o *thought* afirma sucesso e o step falhou — 45 steps (9,0% dos steps com erro)",
apresentado como detecção do FM-2.6 do MAST (descompasso entre raciocínio e ação).

**A escolha arbitrária:** quais palavras contam como "afirmar sucesso". Escolhi 8 termos a dedo
(`sucesso|concluí|apliquei|foi aplicad|funcionou|pronto|obtive|com êxito`), sem critério principiado.

**O teste — variar a lista:**

| Lista | Resultado |
|---|---:|
| Estrita (3 termos inequívocos) | **0 steps (0%)** |
| Original (8 termos) | 45 steps (9,0%) |
| Ampla (14 termos) | 63 steps (12,7%) |

O número percorre todo o intervalo plausível — de "não existe" a "1 em cada 8 erros" — só mexendo na lista.

**Inspecionando os 45 casos, todos são falso positivo**, em três padrões:

1. **Verbo no futuro, planejando** — não afirma sucesso nenhum:
   *"...validarei confidencialidade e estarei **pronto** para montar a resposta final"*
2. **Descrição correta de um step ANTERIOR que de fato deu certo:**
   *"Já **obtive** uma resposta extremamente detalhada do ConversationAgent..."* — e aí o código *deste* step
   quebra por outro motivo (string mal fechada). Não há contradição.
3. **A palavra estava dentro do texto escrito para o usuário**, não numa afirmação sobre a execução:
   `final_answer({ "Cadastro realizado com sucesso! ...` — o regex lia o `model_output`, que inclui o bloco de
   código, e casou com uma palavra dentro de uma *string*.

É por isso que a lista estrita deu zero: em 498 steps com erro, o agente **nunca** usa linguagem inequívoca de
sucesso sobre um passo que falhou.

**O erro conceitual, mais grave que o da lista:** o *thought* é escrito **antes** do código executar. O agente
não tem como saber, no momento em que pensa, que o código vai falhar. Logo "thought afirma sucesso + step deu
erro" não é contradição — o thought descreve os steps anteriores (que deram certo) e o código deste step falha
depois. O detector comparava duas coisas que não têm por que se contradizer. Um FM-2.6 de verdade exigiria
comparar o thought com a **ação do mesmo step** (o thought diz que vai chamar X e o código chama Y) ou com a
**observação** (o thought afirma um valor que a observação não contém).

**Lição generalizável:** detector baseado em "o texto contém a palavra X" funciona para coisas **estruturais**
(a mensagem contém `SyntaxError`?) e falha para coisas **semânticas** (o agente está afirmando sucesso?).
Sempre que o detector tentar capturar intenção ou significado, keyword matching gera falso positivo em volume —
ali é caso de anotação de amostra ou juiz LLM, não de regex.

#### Teste do inventário de ferramentas — meu inventário estava errado nas duas direções

O `model_input_messages[0]` (system prompt) **declara as ferramentas** como assinaturas `def nome(...)` — é a
fonte autoritativa, e eu nunca a tinha usado. Comparando:

- **90 ferramentas declaradas** no system prompt (união de todos os papéis), contra as 43 que eu tinha
  observado. E a lista é **por papel**: `ConversationAgent` recebe 9, `managerAgent` recebe 3.
- Nomes muito chamados que **não são ferramentas**: `grab` (135×), `get_meta` (100×), `pick_docs`,
  `filtrar_principais`. São **funções auxiliares que o próprio agente define** num step e reutiliza nos
  seguintes (o namespace Python persiste entre steps). Eu as tinha contado como ferramentas autorizadas.

Consequência: o número de Tool-Skip (14 execuções) é não confiável e precisa ser refeito com a lista
declarada por papel. A conclusão de "zero nomes de função alucinados" continua de pé, mas por outro motivo do
que eu havia dito — os nomes desconhecidos são auto-definidos pelo agente, não inventados.

**Regra geral que sai daqui:** sempre que uma análise depender de uma lista feita à mão (ferramentas,
palavras-chave, categorias), procure primeiro a **fonte autoritativa dentro do próprio dado** — aqui, o
system prompt. Lista construída por observação é hipótese, não inventário.

> ⚠️ **Detalhe de implementação que quase repetiu o erro:** o system prompt é a **primeira mensagem** de
> `model_input_messages`. Extrair `def nome(...)` do contexto *inteiro* devolve 152 nomes — contaminado com as
> funções que o próprio agente define ao longo da conversa. Lendo só `model_input_messages[0]`: **90**.

#### Teste do Result-Ignore — aprovado, e o refinamento fortalece o achado

Definição original: retorno de ferramenta atribuído a uma variável que nunca reaparece em código posterior da
mesma trajetória. Variações testadas:

| Variação | Resultado |
|---|---:|
| Definição original | 103 de 3.053 (3,4%) |
| Excluindo ferramentas de efeito colateral (`envia_excel_para_usuario`, `contact_user`…) | **103** (idêntico) |
| Trocando inventário observado (43) pelo declarado (90) | **103** (idêntico) |
| Restrito a chamadas caras (subagente, `answer_question_using_documents`) | 96 de 1.358 (7,1%) |

Insensível a todas as variações → **robusto**. E a última linha é um achado novo: **96 dos 103 casos são
chamadas caras**. O desperdício não está espalhado, está concentrado exatamente onde custa dinheiro — o que
torna esse detector o mais acionável dos silenciosos.

#### Teste do RAC — reprovado na forma original, corrigido para 125

| Variação | Resultado |
|---|---:|
| Original (inventário observado, incluindo `final_answer`) | 461 |
| Só repetições entre steps (não dentro do mesmo step) | 434 |
| Excluindo `final_answer` | 266 |
| **Inventário declarado + excluindo `final_answer`** | **125** |

Amplitude de 3,7× conforme a escolha. A causa principal é a mesma do teste de inventário: `grab` (135×) e
`get_meta` (100×) estavam contados como ferramentas, mas são **funções auxiliares que o próprio agente
define** — chamar a própria função auxiliar várias vezes é programação normal, não redundância de ferramenta.
Somado a isso, `final_answer` repetido pode ser comportamento do harness, não do agente.

**125 é o número conservador** (inventário declarado, sem `final_answer`) e é o que ficou no notebook e no
relatório. Continua sendo um indício útil, mas deve ser apresentado com a definição explícita ao lado.

### 1.7 · Mineração das unidades nº2/nº10 (`06-racionais-mineracao-unidades-n2-n10.md` §9) — como foi rodado, conferido, e onde desviou do pré-registro

Resultados em [`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.1; o porquê de cada passo e de cada régua em
[`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9. Estado: os 8 passos rodados, mais o addendum ao Passo 2; saídas salvas no
notebook. Esta seção cobre os Passos 1–3; os cinco logs do system prompt estão na §1.8; os Passos 4–8, na §1.9. A
evidência de cada análise (pastas com o trace cru) está descrita em "Evidência por análise", no eixo comum de
triangulação, abaixo.

**Pré-registro.** O método foi commitado antes de rodar (`cb032ad`); o adendo ao Passo 3 (conserto silencioso com
`.get` / `try-except`) também, antes de o Passo 3 rodar (`ae8264b`), e a checagem do system prompt, antes de rodar
(`2a07d6e`). As emendas feitas depois de um passo rodar estão datadas no próprio §9 de `06-racionais-mineracao-unidades-n2-n10.md`.

**Como reproduzir.** No Jupyter: rodar o notebook `pipeline/mineracao_unidades_n2_n10.ipynb` até o fim — as
células da §11 só dependem do setup §0 (que reconstrói `RAW`, `EU`, `UNI`, `S` a partir do trace). Na linha de
comando, a partir da raiz do repo:
`uv run jupyter nbconvert --to notebook --execute --inplace analysis/2026-09-trace-law-flow/pipeline/mineracao_unidades_n2_n10.ipynb`
(regrava os CSVs de `resultados/`, que são determinísticos e git-ignored).

**Sanidade do ambiente.** Com pandas 3.0.5, as células reproduziram os números já publicados das duas unidades (nº2:
96 erros / 87 ocorrências; nº10: 10 / 10), e a chave `(exec_id, role, idx)` é única em `RAW` — é por ela que a
atribuição acha o código de cada step.

**Desvios do pré-registro — os três, com o efeito de cada um.**

1. **O texto do Passo 1 dizia "96 (nº2) e 10 (nº10) ocorrências"** — são 96 **erros**; a nº2 tem 87 ocorrências.
   Rodado nos dois níveis; o veredito é o mesmo. O texto dos racionais foi corrigido; a versão original está no
   commit `cb032ad`.
2. **O parser da mensagem foi corrigido depois da primeira rodada**, em dois formatos que ele não lia:
   `KeyError: 'x'. Maybe you meant one of these indexes instead: [...]` (a regex capturava a frase inteira, não só a
   chave) e o erro de colunas do pandas (`are in the [columns]`). Os limiares não mudaram. Efeito só na nº10 —
   antes: `validar_quebra_sigilo` 7, `get_available_documents` 1, não resolvido 2; depois: 7, 1,
   `extrair_evidencias` 1, não resolvido 1. Veredito "divide" nas duas rodadas.
3. **A regra de destino de cada sub-unidade foi acrescentada depois do Passo 1** (candidata / documentar e monitorar
   / bucket de consulta). Não muda nenhum resultado atual; foi testada com dados sintéticos (abaixo).

**Conferência manual da atribuição (Passo 1).** Abertos um a um, com o comando que falhou e o nó que pediu (strings
longas e sequências de ≥5 dígitos mascaradas): todos os casos fora da função dominante (5 da nº2), os 10 da nº10, e
uma amostra de 4 atribuições "em step anterior" da nº2 — nas 4, a linha achada no step anterior é a chamada
`docs = get_available_documents(...)` (ou `docs_info = ...`). O que a conferência mostrou:

- **nº10:** as 7 atribuições a `validar_quebra_sigilo` conferem — a variável indexada é `quebra`,
  `validacao_sigilo`, `sigilo_val`, `quebra_obj` ou `valid_quebra`, e em todas a origem é essa chamada. A de
  `extrair_evidencias` é a execução `95344639…`, já descrita em `01-racionais.md` §3 Passo 8; a de
  `get_available_documents` indexa um item de metadado (`doc['metadado'][0]`).
- **nº2:** os 5 fora da dominante são "dict iterado como lista" com o `.get` falhando dentro de função auxiliar ou
  `lambda` escrita pelo agente. Em 2 deles o único `.get` casado no comando é de um dicionário do próprio agente
  (`prioridade`, `priority`), não o objeto que falhou — por isso ficam **não resolvidos**, em vez de atribuídos a
  algo errado. 1 é atribuído à função auxiliar `meta_map`. Pior caso (os 5 contra a dominante): 91/96 = 94,8%,
  acima dos 90%.

**Teste de robustez do Passo 2 — dois métodos de leitura.** `ast.literal_eval` × regex tolerante sobre o mesmo
objeto impresso: resolvem e concordam (chaves de topo contidas no regex, e mesma 1ª chave) em **89/89** (nº2) e
**7/7** (nº10). Checagem de sanidade: a chave pedida existe no objeto lido em **0/88** e **0/7** — como tem de ser,
é o erro. Os 3 objetos de nível de documento da nº2 foram cruzados com o pedido: `[0]` em 2, fatia em 1.

**Teste sintético da regra de destino.** Duas unidades inventadas, rodadas pela mesma célula: (i) dominante com
70,6% (12 casos, 5 execuções, 3 meses) e cinco funções de 5,9% cada → veredito (c); a dominante sai **candidata** e
as cinco vão para o **bucket de consulta**; (ii) divisão 60/40 com as duas funções recorrentes → veredito (b), **duas
candidatas**. Foi este teste que mostrou o defeito da primeira versão da emenda (a unidade (c) inteira no bucket,
inclusive uma dominante recorrente) — ver `06-racionais-mineracao-unidades-n2-n10.md` §9. As unidades reais seguem iguais: nº2 (a), nº10 (b),
bucket vazio.

**Correção da leitura do Passo 2 (16/09, depois de publicada).** A função `forma` descrevia só o **primeiro**
elemento de listas com elementos de tipos diferentes. `result` tem dois — a lista de documentos e um resumo de
contagens por campo — e o segundo não aparecia. Achado ao rodar a checagem do system prompt: a primeira versão dela
descia em todos os níveis do objeto e trouxe chaves que não estavam no schema publicado; um mapa de caminhos (só
estrutura) mostrou a posição 1 de `result` nos 86 retornos inteiros, sempre depois da lista de documentos. Corrigido:
listas mistas descrevem todos os tipos; dicionário de contagem vira `{<campo>: {<valor>: int}}`; campos de registros
mostram a forma de cada valor (a forma de `metadado` passou a aparecer nos 86, não só em 3). O teste de robustez
(89/89, 7/7) não muda — ele compara chaves de topo.

**Incidente de PII na primeira versão da checagem do system prompt.** Ao descer em todos os níveis, ela imprimiu na
saída da sessão chaves que eram **dado**: valores categóricos (tipos de peça, UFs, canais) e hashes de documento de 32
caracteres. Nomes, CPF/CNPJ e números de processo não saíram — a máscara de sequências de ≥5 dígitos segurou. Nada
disso foi para documento nem para o notebook. Corrigido: as chaves reais vêm só do schema do Passo 2, e a `forma`
mascara chave com cara de dado (hex longo, código em maiúsculas, ≥5 dígitos). Nome de variável também pode embutir
identificador (um agente nomeou uma variável com um número longo): a célula do Passo 3 não imprime nomes de variável.

**Teste de robustez da checagem do system prompt — três formas de presença.** Palavra solta, entre aspas e como chave
de JSON (`'chave':`) divergem exatamente onde deviam: `result` aparece 91/91 como palavra (prosa dos exemplos
genéricos do smolagents) e 0/91 como chave; `justificativa` aparece 7/7 entre aspas (como valor, em
`"motivo": "justificativa"`) e 0/7 como chave; `quebra_sigilo`, `hashDocumento` e `tipoExtracaoOcr` batem nas três. A
forma reportada no relatório é a estrita. **Extensão não pré-registrada**, motivada pelas janelas de contexto
(redigidas) que mostraram onde cada chave fica no prompt: se a chave está declarada dentro do bloco
`def ferramenta(...)` — o que separa "o prompt declara esta chave para esta ferramenta" de "a chave aparece no prompt".
**Segunda extensão (16/09, na reorganização da §11):** a célula também imprime o texto literal com que o bloco
descreve o retorno (a seção `Outputs:`, ou as frases da descrição que falam em "return"). Presença de chave não diz
**o que** o prompt afirma; o texto diz, e é o que separa "prompt errado" de "prompt omisso" (§1.8). O bloco é o mesmo
em todos os steps com erro de cada ferramenta (1 variante nos erros).

**Passo 3 — o que o pré-registro não previu, e como foi tratado.** (i) **Reatribuição:** a primeira rodada contou 19
"repetiu o acesso errado" na nº2 — e nos 19 o step seguinte **não** teve erro, o que não combina com repetição. Abertos
com as linhas redigidas: o agente reatribui a variável (`docs = docs['result'][0]`) e depois lê `docs[0]`, que já é
outro objeto. Regra: só contam as leituras antes da reatribuição e as do lado direito dela. A primeira versão dessa
regra também cortava quando o agente chamava **a mesma ferramenta** de novo com o mesmo nome — o que escondeu o
conserto silencioso da nº10 (virou "não lê mais a variável"); corrigido: reatribuir com a mesma ferramenta não corta.
(ii) **Guarda de tipo:** com a regra (i), 18 casos ainda tinham o acesso antigo, 0 com erro no step seguinte — 17
dentro de um ramo guardado pelo tipo da própria variável (`x['result'][0] if 'result' in x else x[0]`), contados como
troca de chave marcada "com guarda de tipo"; 1 sem guarda, não inspecionado. (iii) A chave nova é comparada com o
schema da **ferramenta** (todas as sub-unidades dela), não do pedaço indexado: o caso de metadado da nº10 indexava um
item `{nomeMetadado, valorMetadado}` e corrigiu lendo `hashDocumento` no documento. (iv) O `.get` da nº10 foi aberto:
o segundo parâmetro é `<var>.get('vazamento_sigilo')`.

**Rodada no Jupyter (16/09).** Rodado no kernel "Python (memory-layer-ai-agents)" até a §11.2, sem erro: as saídas das
§1–§10 reproduzem as já publicadas (na célula do achado central o Jupyter só juntou duas saídas de texto numa; no
gráfico 8.10 a imagem foi redesenhada, com o mesmo texto). A saída salva da §11.2 foi limpa, porque era do código
anterior à correção acima.

**Reorganização da §11 e rodada completa (16/09, depois).** As células da §11 misturavam as regras (o racional) com a
análise, e a 11.1 tinha ~10 mil caracteres de código antes da tabela. Reorganizadas sem mudar o método: as funções
foram para uma célula própria (11.0, sem saída), e cada passo virou título + o que faz + como ler + uma célula curta
que só mostra as tabelas. **Teste de equivalência:** as quatro tabelas que os passos produzem (`ATRIB`, `SCHEMA`,
`CHAVES_REAIS`, `AUTOCORR`) foram geradas com o código antigo e com o novo sobre o mesmo trace, e são idênticas
(`DataFrame.equals`). Notebook executado inteiro com `nbconvert`, sem erro; o texto de todas as saídas das §1–§10 é
idêntico ao já salvo, e essas células foram mantidas como estavam (para não regravar a imagem do gráfico 8.10). **As
saídas das §11.1–§11.4 estão salvas no notebook.**

**PII.** As células da §11 imprimem só nome de função, contagens, nomes de chave e tipos, o segundo parâmetro do
`.get` como estrutura, e o texto do bloco em que a ferramenta é declarada no prompt (documentação da ferramenta);
chave com cara de dado vira `<chave-dado>`. Nenhum valor retornado pelas ferramentas sai na tela; conferido nas
saídas salvas: nenhuma sequência de ≥5 dígitos, hex ≥16 ou `exec_id`. Os JSONs de `drill_down.py evidencia` (§1.8)
são o oposto — texto cru, com PII — e ficam em `resultados/`, git-ignored. **Incidente (16/09):** ao abrir o caso
`c67b0502…` para escolher trechos, um print exploratório com redação insuficiente mostrou na saída da sessão texto de
`final_answer` (nome de parte, CNPJ parcial). Nada foi para documento, notebook ou arquivo versionado; os trechos da
§1.8 foram redigidos à mão.

**Ainda não feito (Passos 1–3):** o 1 caso de "repetiu sem guarda" da nº2. A amostra do Passo 6 está na §1.9.

### 1.8 · Cinco logs — o prompt declara um contrato, a ferramenta devolve outro, o agente descobre e corrige

Sustenta a leitura do system prompt de [`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.1. Por que logs, como
foram escolhidos e o que eles podem provar: [`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9, "Evidência caso a caso". Não é
pré-registrado e não substitui o Passo 6.

**Regra de escolha.** Para cada ferramenta com erro atribuído no Passo 1, o primeiro caso na ordem (mês, `exec_id`,
`idx`) de cada desfecho de **correção** do Passo 3 que aparece nela — troca de chave sem guarda, troca com guarda de
tipo, conserto com `.get` —, no máximo dois por ferramenta. `extrair_evidencias` só tem um caso. Desde 17/09 a regra
roda no próprio notebook (§11.4), que grava os cinco casos em `resultados/evidencia/11.4_conserto/casos.csv` — os mesmos
cinco escolhidos em 16/09.

**Como abrir cada caso com o texto cru.** Os trechos abaixo são redigidos (valores trocados por `<str>` / `{…}`,
números e nomes de variável com número mascarados). O texto inteiro está na pasta de evidência da §11.4
(**git-ignored, com PII — não versionar**; estrutura em "Evidência por análise", abaixo):

```bash
cd analysis/2026-09-trace-law-flow/pipeline
uv run python drill_down.py evidencia 11.4_conserto            # grava crus/ e as visões dos cinco logs
uv run python drill_down.py ferramenta validar_quebra_sigilo   # todas as variantes da declaração, no trace inteiro
```

| Log | Trace cru | Visão do caso (`derivados/`) |
|---|---|---|
| 1 | `crus/d3d64194-ca05-4c53-9041-f398fb723baf.json` | `d3d64194_RespostaBacen_idx1.json` |
| 2 | `crus/21a4fa6c-0421-429c-8824-e668bdef11eb.json` | `21a4fa6c_RespostaBacen_idx2.json` |
| 3 | `crus/95344639-1610-4920-a362-68bfb88709cf.json` | `95344639_RespostaBacen_idx0.json` |
| 4 | `crus/1eed2931-0b7f-a2ab-ed5b-c88e867b0e2e.json` | `1eed2931_ConversationAgent_idx1.json` |
| 5 | `crus/c67b0502-e24a-3ca1-1f3a-bd2ffde18b0c.json` | `c67b0502_ConversationAgent_idx6.json` |

Na visão de cada caso, `trechos_do_cru` traz, nesta ordem e cada um com o caminho no cru: o bloco da ferramenta no
system prompt enviado ao agente e as outras linhas do prompt que a citam; a última chamada da ferramenta antes do erro,
quando foi em outro step; o `thought`, o código, as observações e a mensagem de erro do step do erro; as mensagens que o
agente leu antes do step seguinte; e o `thought`, o código e o erro do step seguinte. `calculados` traz a chave pedida,
as chaves do objeto e em que mensagens do contexto as chaves aparecem, antes e depois do erro. `idx` é a posição do
ActionStep no papel, a partir de 0 (a coluna do notebook); o `step_number` do smolagents recomeça a cada turno da
conversa e não serve de referência. *(Em 16/09 estes JSONs eram gravados soltos por `drill_down.py evidencia <exec_id>
<role> <idx> <ferramenta>`, com o prompt e os steps no mesmo arquivo; substituídos em 17/09 pela pasta com cru e visão
separados.)*

**O que o prompt declara** — texto literal do bloco `def ferramenta(...)` (documentação da ferramenta, não dado de
caso), contra o retorno real do Passo 2:

| Ferramenta | O prompt diz que devolve | Devolve de verdade | Declaração no trace (`drill_down.py ferramenta`) |
|---|---|---|---|
| `validar_quebra_sigilo` | `json com a validação de quebra de sigilo no formato: {"quebra_sigilo": "SIM" ou "NÃO", "motivo": "justificativa"}` | `{vazamento_sigilo: str, justificativa: str}` | 2 variantes, que só diferem na quebra de linha — 135 steps, 26 execuções, dez/2025–jun/2026 |
| `extrair_evidencias` | `json com as informações extraídas das evidências, no seguinte formato: {"informacoes_evidencias": [<lista de informações extraídas de cada evidência>]}` | `{dados_evidencias: [{4 campos}]}` | 1 variante — 38 steps, 8 execuções, mar–jun/2026 |
| `get_available_documents` | `-> object`; *"This is a tool that returns a list of documents and a summary of the kinds of documents from a list of dominios […]"* — nenhuma chave | `{result: [[{documento}], {<campo>: {<valor>: int}}]}` | 5 variantes — 2.478 steps, 635 execuções, out/2025–ago/2026; nenhuma cita `result` (as de out–nov/2025 dizem só *"returns documents"*) |

Fora do bloco, o prompt do `RespostaBacen` repete a chave no **modelo do JSON final** que o agente deve entregar —
`"quebra_sigilo": "<saída da tool validar_quebra_sigilo>"` — e, no prompt do log 3, a ferramenta seguinte é declarada
como `def draft_resposta(reclamacao: string, assunto: string, informacoes_evidencias: array)`.

#### Log 1 — `validar_quebra_sigilo`, troca de chave · `d3d64194…` · `RespostaBacen` · jan/2026 · idx 1 → 2

- **O erro (idx 1).** O agente encadeia as ferramentas na ordem que o prompt manda, imprime o retorno
  (`print(quebra)`) e monta o JSON final lendo a chave declarada: `"quebra_sigilo": quebra["quebra_sigilo"]`.
  Mensagem: `Could not index {'vazamento_sigilo': 'NAO', 'justificativa': <str>} with 'quebra_sigilo': KeyError: 'quebra_sigilo'`.
- **Onde a chave real aparece.** Nem no prompt nem em nenhuma mensagem do contexto do idx 1. No contexto do idx 2, em
  duas mensagens, ambas resposta do step que falhou: o log do `print(quebra)` e a mensagem de erro.
- **O conserto (idx 2).** *thought:* "Houve um erro ao montar o JSON final porque a chave retornada pela validação de
  sigilo é 'vazamento_sigilo' e não 'quebra_sigilo'. Vou ajustar o mapeamento e gerar o JSON final corretamente."
  Código: `"quebra_sigilo": quebra["vazamento_sigilo"]` — mantém o nome de campo que o modelo do JSON final pede e lê a
  chave real. Sem erro; `final_answer`.

#### Log 2 — `validar_quebra_sigilo`, conserto que aceita os dois contratos · `21a4fa6c…` · `RespostaBacen` · fev/2026 · idx 2 → 3

- **O erro (idx 2).** O agente copia do prompt a chave **e** o valor: `if validacao_sigilo["quebra_sigilo"] == "NÃO":`.
  Mensagem: `Could not index {'vazamento_sigilo': 'NAO', 'justificativa': <str>} with 'quebra_sigilo': KeyError: 'quebra_sigilo'`.
- **Onde a chave real aparece.** Ausente do contexto do idx 2; no do idx 3, no log do `print(validacao_sigilo)` e na
  mensagem de erro.
- **O conserto (idx 3).** *thought:* "A ferramenta validar_quebra_sigilo retornou a chave "vazamento_sigilo" em vez de
  "quebra_sigilo". Vou ajustar o código para usar essa chave corretamente e seguir o fluxo de validação e consolidação
  da resposta." Código: `quebra = validacao_sigilo.get("quebra_sigilo", validacao_sigilo.get("vazamento_sigilo"))` e
  `if quebra in ["NÃO", "NAO", "Não", "Nao"]:` — código que funciona com o contrato do prompt e com o real, na chave e
  na grafia do valor. Sem erro. É o "conserto silencioso" benigno do Passo 3.
- **O que o log mostra além da chave.** O prompt declara `"NÃO"`; a ferramenta devolveu `'NAO'`. Com a chave certa e o
  valor do prompt, `== "NÃO"` seria falso sem exceção nenhuma.

#### Log 3 — `extrair_evidencias`, troca de chave · `95344639…` · `RespostaBacen` · mar/2026 · idx 0 → 1

- **O erro (idx 0).** `draft_resposta(..., informacoes_evidencias=info_evidencias["informacoes_evidencias"])` — o
  nome do argumento e a chave são os dois que o prompt declara. Mensagem: `Could not index {'dados_evidencias': [{…}]}
  with 'informacoes_evidencias': KeyError: 'informacoes_evidencias'. Maybe you meant one of these indexes instead:
  ['dados_evidencias']`.
- **Onde a chave real aparece.** Ausente do contexto do idx 0; no do idx 1, no log do `print(info_evidencias)` e na
  mensagem de erro, que aqui ainda sugere a chave.
- **O conserto (idx 1).** *thought:* "The return from extrair_evidencias uses the key 'dados_evidencias' instead of
  'informacoes_evidencias'. I will correct that and proceed with draft_resposta, resposta_orgao_regulador and
  validar_quebra_sigilo, then assemble the final JSON." Código: `informacoes_evidencias=info_evidencias["dados_evidencias"]`.
  O idx 1 erra de novo, por outro motivo: a ferramenta seguinte devolve um texto de erro de validação e o agente o
  indexa como dict (o caso já descrito em `01-racionais.md` §3 Passo 8).

#### Log 4 — `get_available_documents`, troca de chave · `1eed2931…` · `ConversationAgent` · dez/2025 · idx 1 → 2

- **Antes do erro (idx 0).** `documentos = get_available_documents(filter_field_name="cod_rfrc_arqu_juri",
  filter_field_value=<pasta>, domains=["civelingestao"])` e `print(documentos)`.
- **O erro (idx 1).** *thought:* "Já obtive a lista completa dos documentos vinculados à pasta <n> […]". Código:
  `for doc in documentos[0]`. Mensagem: `Could not index {'result': [[{…}], {…}]} with '0': KeyError: 0`.
- **Onde a chave real aparece.** **Já estava no contexto do idx 1**: o log do `print(documentos)` do idx 0 começa com
  `{'result': [[{'hashDocumento': …`. O `thought` fala em "lista completa dos documentos" e o código indexa `[0]` —
  compatível com a descrição do prompt (uma lista cujo primeiro elemento são os documentos), mas o log não mostra de
  onde veio a suposição. No idx 2, `result` aparece de novo, no log e na mensagem de erro.
- **O conserto (idx 2).** *thought:* "O erro ocorreu porque documentos['result'] é uma lista de listas, portanto
  preciso acessar a camada correta antes de iterar. A lista completa dos documentos está em
  'documentos['result'][0]'." Código: `for doc in documentos['result'][0]`. Sem erro.

#### Log 5 — `get_available_documents`, troca com guarda de tipo · `c67b0502…` · `ConversationAgent` · dez/2025 · idx 6 → 7

- **Antes do erro.** Conversa de vários turnos. No idx 4 o agente chama `get_available_documents(...)` de novo e
  imprime o retorno; `{'result': …` está no contexto do idx 6 em três mensagens, todas logs de `print`.
- **O erro (idx 6).** `all_docs_<n> = docs_info_<n>[0]`. Mensagem: `Could not index {'result': [[{…}], {…}]} with '0': KeyError: 0`.
- **O conserto (idx 7).** *thought:* "A variável de resposta da ferramenta tem um aninhamento adicional (lista dentro de
  lista). Preciso acessar corretamente a lista de documentos […] Acessarei docs_info_<n>['result'][0] para obter a
  lista correta dos documentos." Código: `all_docs_<n> = docs_info_<n>['result'][0] if isinstance(docs_info_<n>, dict)
  else docs_info_<n>[0]` — lê a chave real e mantém o acesso antigo num ramo, caso o retorno venha como lista. Sem erro.

**O que os cinco logs sustentam, e o que não.**

- **Logs 1–3 (`validar_quebra_sigilo`, `extrair_evidencias`) — a forma forte.** O prompt declara um contrato
  explícito; o agente escreve exatamente esse contrato (chave, nome de argumento, grafia do valor); a ferramenta
  devolve outro. A chave real não está no prompt nem no contexto antes do erro, aparece pela primeira vez na resposta
  do step que falhou (log do `print` do mesmo step e mensagem de erro, que imprime o objeto), e o `thought` do conserto
  nomeia a troca nos três.
- **Logs 4–5 (`get_available_documents`) — a forma fraca.** O prompt não declara chave errada: descreve o retorno como
  "uma lista de documentos e um resumo" e omite o envelope `{'result': …}`. O `[0]` do agente é compatível com essa
  descrição, mas nos dois logs o retorno impresso, com `result`, **já estava no contexto antes do erro**. O prompt
  omisso é causa plausível, não a única: o agente tinha a estrutura na frente e errou mesmo assim.
- **Descobrir e corrigir.** Nos cinco, o agente descobre pela resposta do step que falhou e o `thought` do conserto
  descreve a estrutura real. Dois dos cinco consertos se protegem dos dois contratos (log 2: `.get` com a chave real de
  padrão e a lista de grafias; log 5: guarda de tipo).
- **Sequência, não causa.** Os logs mostram prompt → código → retorno → troca. Não provam que a documentação certa
  evitaria o erro; isso só o replay contrafactual testa (`06-racionais-mineracao-unidades-n2-n10.md` §9 Passo 7).

**Conferências de apoio, fora dos logs (16/09).** (i) Declaração de cada ferramenta no trace inteiro:
`drill_down.py ferramenta <nome>` — números da tabela acima. (ii) Modelo do JSON final com
`"quebra_sigilo": "<saída da tool validar_quebra_sigilo>"` (regex `"quebra_sigilo":\s*"<sa[íi]da da tool
validar_quebra_sigilo>"` no system prompt): **7/7** steps com erro e **135/135** steps que declaram a ferramenta.
(iii) Valor de `vazamento_sigilo` no objeto impresso pelas 7 mensagens de erro (`ast.literal_eval`): `'NAO'` em 6,
`'SIM'` em 1 — nunca `'NÃO'`; o código que quebrou compara com o literal `"NÃO"` ou `"SIM"` (regex
`==\s*["'](NÃO|SIM)["']`) em **3/7**. (ii) e (iii) foram contados por script de sessão, não versionado — as regras
estão aqui para refazer.

### 1.9 · Passos 4 a 8 (`06-racionais-mineracao-unidades-n2-n10.md` §9) — como foi rodado, conferido, e onde desviou do pré-registro (17/09/2026)

Resultados em [`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.1; o porquê de cada decisão em
[`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9, "Execução dos Passos 4 a 8"; código no notebook `mineracao_unidades_n2_n10.ipynb`, §11.5–§11.8; evidência nas
pastas `11.5_estabilidade/` a `11.8_registro_final/` (ver "Evidência por análise", abaixo).

**Como reproduzir.** Rodar o notebook inteiro (comando na §1.7) e, em `pipeline/`, `uv run python drill_down.py
evidencia` para gravar os crus e as visões por caso.

**Rodada (17/09).** Notebook executado inteiro com `nbconvert`, sem erro. O texto das saídas das §1–§10 é idêntico ao já
salvo (células mantidas como estavam). As tabelas das §11.1–§11.4 não mudaram: as células só ganharam, no fim, a
gravação da pasta de evidência. O `drill_down.py evidencia` foi rodado duas vezes — antes e depois da execução final do
notebook — com o mesmo resultado nas 8 pastas.

**Desvios e decisões não pré-registradas — com o efeito de cada uma.**

1. **Passo 4 — níveis.** Formas comparadas só dentro do mesmo nível (chaves de topo do objeto). Sem isso, os 3
   documentos indexados como lista da nº2 contariam como "schema diferente" do retorno inteiro.
2. **Passo 4 — referência.** Cada forma comparada com a mais comum do nível, não com a do primeiro mês. Sem efeito
   aqui: nos três níveis, a forma do primeiro mês é a mais comum.
3. **Passo 4 — "contradição".** Definida como faltar chave da forma comum ou um tipo mudar; campos a mais, de tipo
   simples, não contam. **Escrita depois de o Passo 2 já ter mostrado o caso com `iuDocsId`/`iuDocsTenantId`.** Efeito:
   decide o status da nº2 — `derived-and-checked` na leitura adotada, `parcial` na estrita. As duas são reportadas lado
   a lado no notebook, no relatório e no registro (`validation.passo5_cobertura`).
4. **Passo 5 — ocorrência lida.** Conta como lida se pelo menos um dos seus erros teve o objeto lido. Efeito nenhum
   hoje: os 2 erros do resíduo estão em ocorrências com outro erro lido (86/86 por ocorrência; 89/91 por erro).
5. **Passo 6 — sorteio.** `random.Random(20260917)`: 1 do resíduo quando há, o resto entre os lidos. Na nº10 não há
   resíduo, então o "ao menos 1 do resíduo" não se aplica.
6. **Passo 7 — acesso certo.** A primeira rodada do molde escreveu `use r['result']` (só a chave nova do Passo 3), que
   não resolve. Corrigido para a cadeia completa de índices que o agente escreveu nos consertos sem erro no step
   seguinte: `r['result'][0]` em 59/72 na nº2, `r['vazamento_sigilo']` em 6/6 na nº10.
7. **Passo 8 — `location` e `evidence`.** `location` alterna os meses (até 10); `evidence` são os 3 primeiros, de 3
   meses diferentes.

**Conferência do Passo 4.** A variante com campos a mais foi lida no cru (`11.5_estabilidade/crus/`, jul/2026), com
`ast.literal_eval` sobre a mensagem de erro e só contagens na tela: `result` tem 2 posições (lista e dict); os 18
documentos de `result[0]` têm as 3 chaves da forma comum, os 18 têm `iuDocsId` e `iuDocsTenantId`, nulos em todos, e
nenhum tem outra chave; os `metadado` de todos têm `nomeMetadado`/`valorMetadado`. Os 3 objetos de nível de documento são os mesmos 3 já cruzados na §1.7
(pedido `[0]` em 2 e fatia em 1).

**Conferência do Passo 5 — o resíduo.** Os 2 erros abertos no cru (`11.6_status/crus/`), extraindo só o padrão da
mensagem: os dois são `Object hashDocumento has no attribute get`, e nenhum traz `Could not index` — não há objeto na
mensagem para ler. Confirma o motivo registrado.

**Conferência do Passo 6 — a amostra, pelo agente.** Três fontes por caso, calculadas no notebook (§11.7) e
recontadas por fora, direto dos arquivos crus da pasta `11.7_amostra_passo6/`, só com contagens:

- **(1) objeto da mensagem de erro:** as chaves do schema estão no objeto em 9/9 casos lidos (6/6 chaves na nº2, 2/2
  na nº10). É o mesmo texto que o Passo 2 leu — consistência, não prova.
- **(2) log de `print`:** as chaves estão em 10/10 — incluindo o caso do resíduo. **Um tropeço na recontagem, registrado
  porque ensina onde olhar:** a primeira recontagem procurou o log só nas mensagens depois da última resposta do agente
  e deu 0/6 nos 5 casos da nº2. Refeita no contexto inteiro do step seguinte, o log com as 6 chaves está na mensagem 4,
  **antes** da resposta do agente que falhou (mensagem 5; 8 no resíduo): na nº2 o agente imprimiu o retorno num step
  anterior e errou depois. Na nº10 o log vem depois da última resposta — é o `print` do próprio step que falhou. Mesmo
  padrão dos logs 4–5 e 1–3 da §1.8.
- **(3) conserto:** lê chave do schema em 4/4 casos lidos da nº2 (`result`) e 5/5 da nº10 (4 trocas para
  `vazamento_sigilo` e 1 `.get` com ela de padrão).

**Verificação humana do Passo 6 — feita (17/09).** O pré-registro pede verificação humana; a leitura da tabela acima
(automática, por agente) não substituía isso. Feita em duas partes: (1) o caso `3f44a68b…` (o resíduo), guiado
célula a célula com [`pipeline/indice_evidencia.ipynb`](../pipeline/indice_evidencia.ipynb) — notebook genérico que
lista os casos, lista os blocos de um caso sem mostrar texto, mostra o texto de um bloco escolhido, e busca o mesmo
caminho direto no cru, sem depender do código que gerou o derivado (nunca salvar esse notebook com saídas rodadas —
ele imprime texto cru); (2) os 10 casos da amostra, checagem independente do Rafael, registrada em
[`resultados/evidencia/11.7_amostra_passo6/relatorio_independente.md`](../pipeline/resultados/evidencia/11.7_amostra_passo6/relatorio_independente.md)
(git-ignored, com PII — não versionar), lendo os crus direto e cruzando prompt declarado × código do agente × retorno
real, mais uma varredura pelos 10 casos atrás do erro de `draft_resposta`/assunto inválido.

**Incidente de PII nº3 (17/09) — reincidência do mesmo problema, barrada antes do commit.** O `indice_evidencia.ipynb`
voltou a ser salvo **com saídas rodadas**: 7 saídas, ~245 mil caracteres de trace cru, com números de processo. A
advertência escrita dentro do próprio notebook não evitou — quem roda o notebook para validar naturalmente salva o
arquivo depois. O aviso é lembrete, não controle. Nada vazou (o arquivo ainda era *untracked*); as saídas foram
limpas e o arquivo ficou com 0 saídas. **Controle que passa a valer:** antes de qualquer commit que toque um `.ipynb`,
varrer as saídas de todos os notebooks atrás de corridas de ≥5 dígitos e conferir o contexto de cada uma. A varredura
que pegou este caso também passou pelo `analise_trace_esteira_juridica.ipynb` — ali as 301 ocorrências são contagens
de token e durações, nenhuma é identificador. Reforça a regra de sempre: o notebook do índice existe para ser rodado
**localmente**, e sai do repositório sempre vazio.

**Resultado: confirma os achados nos 10/10 casos, sem divergência.**

- **`validar_quebra_sigilo` (5/5 da amostra):** o bloco da ferramenta no prompt é idêntico nos cinco; o agente lê a
  chave que o prompt declara (`quebra_sigilo`, de formas diferentes — `quebra["quebra_sigilo"]`,
  `valid_quebra["quebra_sigilo"]`, dentro de um `if` em um caso); o retorno real traz `vazamento_sigilo`/`justificativa`
  nos cinco. Em 4/5 o step seguinte já corrige para `vazamento_sigilo`; no quinto (`21a4fa6c…`) a quebra acontece
  dentro do próprio `if`, antes de haver step de correção — consistente com o que já tínhamos.
- **`get_available_documents` (5/5 da amostra, incluindo o resíduo):** o prompt não fixa uma estrutura de saída; o
  agente assume um nível de indexação (`docs[0]`, ou — no resíduo — `docs["result"][0][0]`) que não bate com o
  retorno real (`{'result': [[...]]}`). Mesma leitura já documentada: aqui é lacuna de informação, não contrato
  errado.
- **Achado adicional, não generalizável (1/10 — `9be7b413…`):** antes do erro de `validar_quebra_sigilo`, a mesma
  execução tem `extrair_evidencias` e `draft_resposta` chamados com `assunto="dcr-discorda_de_juros"`, rejeitado —
  a ferramenta só aceita `['cartoes_demais', 'roteiro_generico', 'discorda_juros', 'discorda_debito']`. **Conferido
  no cru, com uma correção de precisão:** a chamada a `draft_resposta` não levanta exceção — devolve uma string de
  erro (`"Error calling tool 'draft_resposta': Assunto não previsto..."`) como se fosse a resposta; o erro que de
  fato interrompe o step é a linha **seguinte**, que tenta indexar essa string como se fosse o dict de resposta
  esperado. É o mesmo mecanismo já catalogado como "Retorno pode chegar como string" (nº3, `U_tipo_retorno`) — não é
  um fenômeno novo, só não tínhamos essa execução específica como exemplo. Ausente nos outros 9 casos; não afeta
  nenhum número já publicado.

**Conclusão do Passo 6:** as duas fontes (nossa leitura automática + a verificação independente) concordam nos 10
casos. Nada a corrigir nos achados de `07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

**Achado da verificação humana — o caso resíduo `3f44a68b…` revela um segundo sentido de erro na nº2.** Lendo o
`model_output` do próprio step que quebrou (não o conserto seguinte): o `thought` diz *"A variável `docs` é um
dicionário com chave 'result'. Vou extrair a lista de documentos a partir de `docs['result'][0][0]`..."*, e o código
é `docs_list = docs["result"][0][0]`. Pelo schema já minerado no Passo 2, `docs['result'][0]` **já é** a lista inteira
de documentos — `docs['result'][0][0]` pega só o primeiro documento (um dicionário), e o `for d in docs_list`
seguinte percorre as **chaves** desse dicionário (`hashDocumento`, `metadado`, `tipoExtracaoOcr`...) como se fossem
itens de uma lista. É por isso que a mensagem de erro é `Object hashDocumento has no attribute get` — `hashDocumento`
é literalmente uma chave de dicionário virando `d`. Confirmado lendo o `code_action` e a `mensagem de erro` do mesmo
step, direto no cru (mesmo caminho bruto, campos diferentes).

No step seguinte (o conserto), o `thought` **não** já sabia a profundidade certa: *"O erro indica que `docs_list` não
é uma lista de dicts, mas sim um dict... Vou inspecionar o tipo/estrutura de `docs['result'][0]`... Vou imprimir tipos
e chaves para localizar a lista"* — e o código roda `print(type(res), len(res))`, `print("tipo res[0]:", type(res[0]))`
etc. antes de continuar. Ou seja: o agente sabia que `result` existia (não é falta de informação nesse sentido), mas
não sabia — nem depois de errar — quantos níveis de profundidade tinha, e teve que investigar em tempo de execução.

**O que isso muda.** É o mesmo padrão "desce um nível demais" já documentado em `01-racionais.md` §3 Passo 8 (3 dos 91
erros da nº2), só que este caso tem mensagem `AttributeError`, não `KeyError`/"Could not index" — por isso caiu no
resíduo do Passo 5 em vez de ser lido pelo Passo 2. A `correction_guidance` da nº2 (`07-relatorio-mineracao-unidades-n2-n10.md` §6.1)
foi simplificada por causa disso: em vez de contrastar com **um** erro específico ("use `r['result'][0]`, não
`r[0]`"), agora só afirma o caminho certo ("use `r['result'][0]`") — cobre tanto o erro de menos (dominante, 88/91)
quanto este de mais, sem escolher um dos dois pra citar.

**Checagem: existe algum canal com o schema da ferramenta além do texto do prompt? (17/09, a pedido do Rafael.)** As
ferramentas vêm de um MCP — cabia perguntar se o agente recebe, além do texto renderizado no prompt (o que
`bloco_da_ferramenta()` já lê), algum schema estruturado (JSON Schema, campo `tools=[...]` da API) que a nossa leitura
estivesse deixando de fora. Checado direto na estrutura do cru, campo por campo, no caso `cbc5d62d…`:

| Campo | O que tem |
|---|---|
| `step["tool_calls"]` | só `python_interpreter` (o meta-tool de execução de código do CodeAgent) |
| `model_output_message["tool_calls"]` | `None` |
| `model_output_message["raw"]` | a resposta crua da API (formato OpenAI: `choices`, `model`, `usage`) — sem `tools` nem schema de ferramenta |
| mensagem de sistema (`msgs[0]`) | `tool_calls: None`, `raw: None` |

**Resultado: não existe.** O smolagents (CodeAgent) não usa function-calling nativo da API pras ferramentas de
negócio — só `python_interpreter` é uma "tool" no sentido da API; as demais são chamadas de dentro do código Python
que o agente escreve, e a única forma como ele sabe que existem é o texto do prompt. O que a gente já lê **é o
total** do que o trace guarda sobre a ferramenta — nenhuma informação mais completa está sendo perdida na leitura.

**Ressalva que fica fora do alcance do trace.** O MCP original provavelmente tem um schema mais rico (JSON Schema,
tipos, campos obrigatórios) — o smolagents converte isso pra texto **antes** do que é gravado no trace, e esse passo
de conversão não é visível aqui. Se a pergunta for "a conversão perdeu informação que o MCP original tinha", isso não
dá pra responder só com o trace — é pergunta pro time da plataforma (Fase 3 do plano de pendências).

**O que fica em aberto, registrado, não bloqueante.** "De onde vem o conhecimento do schema, e o agente sabe ou erra
ao aplicar" é uma pergunta de pesquisa legítima — mas não é necessária pra escrever a memória (o schema certo já está
derivado e validado, Passos 1–8, e confirmado que não há canal mais rico sendo perdido). Viraria uma análise nova,
pré-registrada (mesmo motivo do revert de 16/09: pergunta nascida do resultado, precisa de regra escrita antes de
rodar em escala). Registrada em `04-roadmap.md`.

Casos conferidos até aqui: `3f44a68b…` (acima). **Ainda faltam:** os outros 9 casos de `11.7_amostra_passo6/casos.csv`
— anotar aqui, por caso, se bateu ou não.

**Emenda ao Passo 2/5 (17/09) — o resíduo fecha, sem reclassificar nada.** Discussão com o Rafael sobre o caso
`3f44a68b…`: ele já estava classificado como `U_contrato_dict`/nº2 desde o Passo 1 (`submecanismo="dict_iterado_como_lista"`
→ mesma `unidade` dos outros 89, mesma `funcao_origem="get_available_documents"` — conferido direto em `ATRIB`). O
que separava esses 2 casos dos outros 89 não era classificação, era um degrau mais estreito, técnico: o Passo 2
(§11.2) só sabe ler mensagens no formato `Could not index {objeto} with '{chave}'`; a mensagem desses 2 é
`Object hashDocumento has no attribute get` — formato diferente, a regex não reconhece, o objeto nunca é impresso
inteiro.

1. **Confirmação de que os 2 casos do resíduo são o mesmo mecanismo.** Abertos os dois no cru: `3f44a68b…`
   (`docs_list = docs["result"][0][0]`) e `aa3de754…` (`all_docs = docs["result"][0][0]`) — **código idêntico**, mesma
   mensagem de erro. `docs['result'][0]` já é a lista inteira (Passo 2); `[0][0]` pega só o primeiro documento, e
   `for d in docs_list` percorre as chaves dele (`hashDocumento`, `metadado`, `tipoExtracaoOcr`) como se fossem itens.
2. **A regra nova, geral.** `MSG_ATTR = re.compile(r"Object (.+?) has no attribute \w+")` (notebook §11.0). Quando o
   Passo 2 não acha `Could not index` mas acha esse padrão, guarda a chave revelada (`chave_confirmada`) — sem tentar
   reconstruir a forma inteira, só isso. No Passo 5, uma ocorrência conta como coberta se teve **ou** um objeto lido
   direto **ou** uma `chave_confirmada` que já pertence ao schema derivado dos **outros** erros da mesma ferramenta
   (nunca do próprio caso — não tem como confirmar uma chave inventada por ele mesmo). Regra aplicada a qualquer
   `AttributeError` de qualquer ferramenta candidata, não só a estes 2 — testado contra `validar_quebra_sigilo`
   também (nenhum efeito lá, ela não tem erro desse tipo).
3. **Efeito, conferido no notebook re-executado (nbconvert, sem erro; §1–§10 idênticas ao HEAD).**

   | | Antes (16/09) | Depois (17/09) |
   |---|---|---|
   | Erros lidos ou confirmados (nº2) | 89/91 | **91/91** |
   | Ocorrências lidas/confirmadas (nº2) | 86/86 (100%) | 86/86 (100%) — **sem mudança**, os 2 já estavam em ocorrências com outro erro lido |
   | `RESIDUO` (tabela) | 2 linhas | **0 linhas** |
   | `status` / `status na leitura estrita` (nº2) | `derived-and-checked` / `parcial` | **iguais** — o "parcial" da leitura estrita é por causa dos "campos a mais" do Passo 4, não do resíduo |

   O status final **não mudou** — só a contabilidade de erro-a-erro e o resíduo, que agora reflete corretamente que
   não sobrou nada sem explicação.
4. **`amostra_passo6()` não muda.** Ela sorteia com base em `literal_ok` (objeto lido direto), não na nova
   `confirmado` — por isso `3f44a68b…` continua saindo como "resíduo do Passo 5" na amostra do Passo 6 (§1.8 acima):
   são perguntas diferentes (o Passo 6 testa se o schema bate com o cru; esta emenda testa se há evidência suficiente
   pra contar a cobertura do Passo 5).
5. **Pastas de evidência regeradas do zero** (`rm -rf resultados/evidencia && ...`, depois `drill_down.py evidencia`)
   pra não deixar arquivo órfão de antes da emenda; `11.6_status/` ficou com 0 casos (esperado — sem resíduo, nada
   pra abrir). `drill_down.py` corrigido para criar `crus/` mesmo quando uma pasta não tem nenhum caso.

**Auditoria independente da pasta vazia (17/09, Rafael).** Com `11.6_status/` sem `casos.csv`, ficou a dúvida: a
pasta vazia é o resultado esperado, ou um artefato de geração quebrado? Checagem registrada em
`resultados/evidencia/11.6_status/relatorio_independente.md` (git-ignored): a ausência de `casos.csv`/`crus`/`derivados`
bate com o texto acima (resíduo real = 0, nada a materializar ali) — **confirmado, não é lacuna acidental**. A
auditoria também apontou uma lacuna real, à parte: dos 2 casos do antigo resíduo, só `3f44a68b…` continuava
materializado em algum lugar (`11.7_amostra_passo6/`, por também ser a amostra do Passo 6); `aa3de754…` só existia
como texto nos docs, sem cru salvo. **Corrigido:** `python drill_down.py evidencia aa3de754-7bc2-4119-c6e1-409586496e3e
ConversationAgent 2 get_available_documents` → `resultados/evidencia/avulso/` (11/11 trechos conferidos contra o
cru). Os dois casos históricos do resíduo agora reabrem em: `3f44a68b…` em `11.7_amostra_passo6/`, `aa3de754…` em
`avulso/`.

**Sensibilidade.** Leitura estrita do Passo 4 (qualquer diferença de forma conta): a nº2 fica `parcial`; a nº10 não
muda. Nenhum outro resultado depende de decisão tomada depois de ver o dado.

**PII.** As saídas das §11.5–§11.8 imprimem estrutura, contagens e **prefixos de 8 caracteres de `exec_id`** (§11.7 e
§11.8) — identificador de execução, não dado de caso; conferido: nenhum `exec_id` inteiro, nenhuma outra sequência de
≥5 dígitos, nenhum hex ≥16. Os registros completos (`resultados/unidades_memoria.json`) têm `exec_id` inteiro e só
estrutura. **Incidente (17/09):** ao ler os crus da amostra, uma redação improvisada (troca de literais de string por
regex) falhou com aspas dentro do texto e mostrou na saída da sessão trechos de justificativa e o nome de uma cliente.
Nada foi para arquivo, notebook ou documento. A recontagem seguinte imprimiu só contagens e nomes de chave extraídos por
regex — é o único jeito de ler o cru na sessão daqui em diante.

### 1.10 · Análise funda de `validar_quebra_sigilo` — execução, retratação e conferência (17/09/2026)

Pré-registro em [`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9; resultado narrado, com a história caso a caso, na mesma
seção, "Execução da análise funda" em diante; números em [`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.2.
Evidência em `resultados/evidencia/11.9_leituras_quebra_sigilo/` (ver "Evidência por análise", abaixo).

**Como reproduzir.** `uv run python drill_down.py evidencia 11.9_leituras_quebra_sigilo` depois de rodar a §11.9 do
notebook. Nesta sessão o resultado abaixo foi obtido por um protótipo fora do notebook, testado célula a célula
contra o trace; a formalização como §11.9 do notebook está pendente (`04-roadmap.md`).

**Retratação — registrada por escrito, com o que a derrubou (mesma regra do §2).**

A primeira rodada desta análise seguia o pré-registro à risca: ler o código, classificar cada leitura em uma das
cinco classes, seguir a variável até o `final_answer`. Ela apontou `8dd410c8…` como o caso confirmado — o agente
teria trocado `r["quebra_sigilo"]` por `r.get("quebra_sigilo")` no step final e entregado `None`.

**Estava errado.** Rafael perguntou, no checkpoint, "o que você mediu no `final_answer` — algum campo vazio ou
inventado?" — a pergunta certa, porque a resposta revelou que eu tinha inferido o valor do código, nunca olhado o
valor de verdade. Fui buscá-lo: o `action_output` do step de submissão guarda o `request` inteiro, estruturado —
inclusive o campo `quebra_sigilo` como foi entregue. Em `8dd410c8…` o valor entregue era `'NAO'`, o correto.

**A causa do erro.** O código real da leitura "silenciosa" era uma cadeia:

```python
new_quebra.get('vazamento_sigilo', new_quebra.get('quebra_sigilo'))
```

Pede a chave **certa** primeiro; a errada é só o plano B, e o plano B nunca roda porque o primeiro `.get` acerta. O
classificador do protótipo andava pela árvore sintática (AST) e via os dois `.get` como duas leituras independentes
— contava o plano B como leitura que valeu, sem checar se ele chegou a ser avaliado.

**A correção.** A régua de leitura passou a considerar `.get` aninhado como uma cadeia só: resolve pela primeira
chave que existir no schema real; só conta como leitura da chave errada quando ela é a **única** no `.get`, ou
quando é a **primeira** de uma cadeia cujo resultado nunca é sobrescrito por uma chave real depois. Reaplicada a
todos os 7 casos de leitura silenciosa candidata, restaram os corretos.

**A medida que substituiu a régua de código: o payload entregue.** Em vez de inferir o valor pelo caminho do código,
a análise passou a medir **o que o `action_output` de cada step final guarda como `request.quebra_sigilo`** — fato,
não inferência. Das 26 execuções que declaram a ferramenta, 21 entregaram um payload com o campo; 9 dessas 21 (43%)
trazem algo que não é `SIM`/`NAO` — números completos em `07-relatorio-mineracao-unidades-n2-n10.md` §6.2.

**Por que a medida direta é mais forte, e passa a valer daqui pra frente.** Ler código é inferência sobre o que
*deveria* acontecer; ler o `action_output` é observação do que *aconteceu*. Onde o trace guarda o resultado de fato
(como aqui, via o `request` estruturado), a medida direta substitui a leitura de código como fonte primária — a
leitura de código continua útil para explicar o **porquê** (a cadeia de `.get`, o nome duplicado no prompt), não
para decidir o **o quê**. Registrado como norma para as próximas análises deste tipo, não só como correção pontual.

**Conferência dos 5 casos fora do padrão (7+1+1, agrupados por forma).** Os 7 casos de "objeto inteiro no lugar do
valor" e o caso de "campo vazio" (`dbc472b0…`) foram conferidos contra o cru, estrutura apenas: o `action_output` de
cada step final tem `request.quebra_sigilo` do tipo e forma reportados na tabela de §6.2; nenhum dos 9 tem
`SIM`/`NAO` no campo. O caso de "texto de 203 caracteres" foi conferido pelo comprimento e pela ausência de match
com `SIM`/`NAO`/`NAO ` normalizados — sem ler o conteúdo do texto.

**A grafia — conferência de alcance.** As duas comparações divergentes (`== "NÃO"`) foram checadas contra a linha em
que cada step falhou (extraída da própria mensagem de erro, `FALHOU` no notebook): as duas comparações estão na
mesma linha da falha de chave — nunca avaliadas. Achado negativo, mas checado, não presumido.

**O achado candidato em `get_available_documents` — por que fica travado no limite de PII.** Achadas 2 execuções com
a mesma forma (`.get('documents')`/`.get('summary')`, chaves inexistentes no schema real, sem plano B), conferidas
estruturalmente: o valor resultante (`None`) segue como argumento de outra chamada de ferramenta dentro do mesmo
step, sem erro. Para confirmar se a resposta final saiu errada seria preciso ler o texto da resposta e compará-lo
com o conteúdo real dos documentos — violaria a regra de PII em vigor desde os incidentes de 16–17/09 (acima). Fica
travado como candidato por desenho, não por preguiça de investigar: o mesmo limite que protege PII aqui é o que
impede confirmar. `extrair_evidencias` foi checada (8 execuções, 1 erro conhecido) e descartada por amostra — não
há campo único mensurável no payload, e 8 casos não sustentam contagem nenhuma.

**PII desta análise.** Todas as inspeções usaram `action_output.request.quebra_sigilo`/`documents`/`summary` só como
**tipo e forma** (string curta, dict com quais chaves, comprimento de texto) — nunca o conteúdo de `resposta_orgao`,
`resposta_cliente` ou da justificativa. Nenhum texto de caso apareceu na tela nesta análise.

**Formalização como §11.9 do notebook (17/09) — um segundo bug achado ao portar.** Ao mover o protótipo pras funções
de §11.0 (`classificar_campo_final`, `payload_entregue_qs`, `comparacoes_grafia_qs`) e rodar dentro do pipeline
oficial, o detector de grafia (comparações `== "NÃO"`) apareceu com 3 execuções em vez de 2 — uma a mais que o já
registrado. Aberto o caso extra (`8dd410c8…`): a comparação divergente não tinha nada a ver com `quebra_sigilo` —
era sobre uma variável (`new_validade`) de outro campo qualquer, que por acaso está num step de uma execução que
também chama `validar_quebra_sigilo`. O detector original olhava qualquer comparação de string no step, sem checar
se a variável comparada vinha de fato do retorno da ferramenta. **Corrigido:** `comparacoes_grafia_qs` agora exige
que o lado comparado se resolva (`base_deriva_de`, um nível de indireção) até uma variável que recebeu a chamada de
`validar_quebra_sigilo` naquele papel — mesma disciplina de proveniência usada em `classificar_campo_final`.
Reconferido: os 5 casos de grafia voltam a bater com o já publicado (2 execuções, `06-racionais-mineracao-unidades-n2-n10.md` §9). Números
decisivos — **9/21 (43%), 5 meses, `destino: harness`** — não mudaram: o bug estava isolado no detector de grafia,
que é achado à parte, não usado no cálculo do impact. `resultados/unidades_memoria.json` regravado automaticamente
pela própria célula (não editado à mão). Evidência: `resultados/evidencia/11.9_leituras_quebra_sigilo/` — 13 casos,
122/122 trechos conferidos contra o cru (`drill_down.py evidencia 11.9_leituras_quebra_sigilo`).

### 1.11 · Análise funda de `get_available_documents` (nº2) — de exploração avulsa a célula do notebook, com
retratação (17/09/2026)

Pré-registro e racional completos em [`01-racionais.md`](01-racionais.md), "Análise funda da nº2"; resultado em
[`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.3; código no notebook `mineracao_unidades_n2_n10.ipynb`, §11.10.

**Ponto de partida — o que já existia e por que não bastava.** Uma sessão anterior no mesmo dia tinha gerado a
pasta `resultados/evidencia/11.10_leituras_get_available_documents/` **fora do notebook, sem pré-registro**: 3
casos escolhidos por inspeção, 2 chamados de "confirmado: chega a `final_answer` errado" usando uma lista de
palavras inventada ("não encontr...", "ausente", "inacessível"...) aplicada à saída do `ConversationAgent`. Antes
de aceitar isso como resultado, três problemas foram encontrados ao tentar reproduzir/formalizar:

1. **A lista de marcadores era inventada**, não derivada do system prompt (diferente de `DEGENERADO`, que vem de
   uma frase literal que o próprio prompt instrui usar). É exatamente a categoria de proxy que `01-racionais.md`
   §2 já mostrou frágil (o "reasoning-action mismatch" foi retirado pelo mesmo motivo).
2. **O nível errado do trace.** Os marcadores foram checados na saída **intermediária** do `ConversationAgent`,
   não na resposta **real** que o `managerAgent` entrega — conferido diretamente: `DEGENERADO` (o detector já
   validado) **não bate** na resposta real do `managerAgent` para nenhum dos 3 casos daquela pasta.
3. **Os caminhos citados no `leia-me.md` daquela pasta não existiam** (`resultados/evidencia/get_available_documents_silent/traces/...`,
   `manifest.csv`) — os arquivos reais estavam em outro lugar (`resultados/evidencia/avulso/`), sinal de que a
   evidência não passou pelo padrão `registrar_evidencia`/`drill_down.py evidencia` do resto do pipeline.

**O que foi refeito.** Uma célula nova (§11.10) generaliza o Passo 1 da mineração original (`acessos()`,
`chamadas_de()`, o critério de reatribuição entre steps) para o **universo completo** de chamadas a
`get_available_documents` — não só os 91 erros já conhecidos —, separando leituras guardadas (dead code quando a
condição nunca é satisfeita pelo schema real) e protegidas por `try/except` das leituras sem proteção nenhuma, e
cruzando estas últimas, quando o step não tem erro, com `DEGENERADO` na resposta real do `managerAgent`.

**Teste de consistência (condição para confiar no resto).** As leituras erradas-e-desprotegidas com erro no step
precisam reconciliar com os 91 já conhecidos da nº2 (`ATRIB`). Bateram: 93 de 597 leituras rastreadas, contra 91
erros conhecidos — a diferença de 2 é mais de uma leitura por step em alguns dos erros já contados, não
divergência. Sem esse teste passar, os números novos não seriam publicáveis.

**Por que `DEGENERADO` sozinho não bastava (achado em sessão de revisão, 17/09).** `DEGENERADO` só pega **recusa
explícita** — a frase que o system prompt manda usar quando não acha nada. Mas um `.get(chave_errada)` sem plano B
devolve `None` **em silêncio**, e nada garante que isso vire uma recusa explícita: pode virar um `None`/`null`
literal no texto final, ou o dict/objeto inteiro sendo repassado adiante e acabando impresso (o mesmo mecanismo já
visto na nº10, classe "objeto inteiro repassado", §6.2) — nenhum dos dois soa como "não encontrado". Por isso a
célula final roda **três checagens independentes** na resposta real do `managerAgent`, não uma: `DEGENERADO`,
presença literal de `None`/`null`, e um regex frouxo para "parece um dict impresso". Conferido manualmente antes de
formalizar (fora do notebook, lendo os 4 crus dos casos confirmados): nenhum dos três sinais aparece em nenhum dos
4 — confirma que a checagem ampliada não muda o resultado desta rodada, só o torna mais defensável.

**Resultado, e o que ele retrata.** 4 ocorrências do mecanismo ".get sem plano B" no universo completo (não
amostra), 0/4 em qualquer das três checagens. **A frase "confirmado: chega a `final_answer` errado" da pasta
exploratória é retirada** — o mecanismo (leitura silenciosa que descarta documentos reais) é real e agora contado
de forma exaustiva; o dano à resposta entregue, como tinha sido afirmado, não se sustenta contra nenhum sinal já
validado ou estrutural. Mesma disciplina de retratação do §2 de `01-racionais.md`: separar "corrigir" (o mecanismo
continua verdadeiro, só a régua mudou) de "retirar" (a afirmação específica de dano não estava lá).

**O segundo mecanismo — quantificado, não deixado como menção solta.** Um dos 3 casos originais (`15f6ad52…`) não
é do tipo ".get sem plano B" — é uma guarda (`if 'documents' in retorno`) cuja condição a chave real (`result`)
nunca satisfaz, então o ramo que usaria os documentos reais nunca roda e eles são descartados por inteiro. Uma
primeira versão deste documento deixou isso como "lead, não quantificado" — o Rafael apontou que isso não deveria
entrar no racional como se fosse parte da análise sem ter sido de fato rodado. Corrigido: um segundo detector de
AST (`'chave' in retorno` com `chave` fora do schema real) rodado no mesmo universo de 635 papéis achou **1
ocorrência no trace inteiro** — o próprio `15f6ad52…`, nenhuma outra — abaixo do piso de recorrência de qualquer
candidata a memória (≥3 execuções e ≥2 meses, §7 Passo 5). Fecha como mecanismo confirmado e raro, não como lead
pendente.

**Evidência reconciliada.** A pasta `resultados/evidencia/11.10_leituras_get_available_documents/` foi **regravada
pela própria célula** (`registrar_evidencia`) e por `drill_down.py evidencia 11.10_leituras_get_available_documents`
— 9 casos, 8 crus (9,7 MB), 64/64 trechos conferidos contra o cru. O conteúdo da pasta exploratória anterior
(incluindo o `leia-me.md` com os caminhos inconsistentes) foi substituído; os arquivos com o nome de padrão antigo
(`<exec>_<role>.json`, sem prefixo de UUID completo) que não correspondiam a nenhum caso do `casos.csv` foram
removidos.

**PII.** Toda a análise usa estrutura (chave lida, forma da proteção, se bateu ou não um regex já validado) —
nenhum texto de documento ou de resposta apareceu na tela desta sessão.

### 1.12 · Três relógios — que data o `mes` do pipeline carrega (23/09/2026)

**A pergunta.** Toda análise por mês (triagem "≥2 meses", séries mensais, datação de incidentes) depende de a
data de cada execução estar certa. Até 23/09 ela vinha de `anomesdia`. Esse campo é a data da execução?

**O método: três relógios de fontes independentes, por execução.**

1. `anomesdia`: coluna da tabela (quem grava não está documentado);
2. `dat_hor_inio_exeo`: coluna da tabela, "data/hora de início";
3. `timing.start_time` de cada step: gravado **pelo runtime do agente**, durante a execução, dentro de
   `txt_etap_memo`.

Se (2) e (3) concordam e (1) diverge, (1) não é a data da execução. O teste não passa por nenhum código de
classificação: só lê duas colunas e um campo do JSON.

**Evidência.** `uv run python drill_down.py relogios` → `resultados/evidencia/A3_relogios/` (git-ignored):
`derivados/relogios.csv` (as 1.000 execuções com as três datas), `derivados/cruzamento.csv` (lote × mês real),
`derivados/h_bloco_code.csv` e `crus/` para uma regra de escolha escrita antes de olhar os casos: as 3 de maior
defasagem, a 1ª com defasagem > 30 dias em cada lote, 1 controle com defasagem < 1 dia, e a 1ª execução
`H_bloco_code` de out/2025 (empate → ordem de `exec_id`).

**Resultado.** (2) = (3) em 840/840 (mesmo mês e mesma semana; diferença máx. 0,26 h). (1) só bate com o mês
real em 35,8% das 840 execuções com memória (41,4% nas 1.000 linhas: as 160 sem memória são quase todas
recentes); defasagem mediana de 46 dias, máx. 230; **0** execuções começam depois de (1). Semântica e decisão:
`05-schema.md` §Datas; `01-racionais.md` §1.

**Conferir sem confiar no pipeline.** Abrir um `crus/<exec_id>.json`, ler `anomesdia` e `dat_hor_inio_exeo`,
pegar qualquer `timing.start_time` de um step e converter (`date -u -r <epoch>`). As duas últimas batem; a
primeira vem semanas ou meses depois. No controle, as três batem.

**O que não prova.** O que `anomesdia` é exatamente — só quem mantém a tabela confirma (`05-schema.md` §Aberto 9).

**Consequência para as pastas de evidência da §11.** As regras de escolha de casos ordenam por (mês, exec_id,
idx). Com o `mes` real, os casos escolhidos mudaram em 8 das 10 pastas `11.x` (a 11.9 manteve os casos, mas suas contagens por mês mudam; a 11.6 não tem casos); as pastas foram regeneradas
(`casos.csv` pelo notebook, `crus/` e visões por `drill_down.py evidencia`) e conferem contra o cru, mas **os
`relatorio_independente.md` e os `relatorio_meta_*.md` auditaram a amostra antiga** — estão desatualizados até
serem refeitos (`04-roadmap.md`).

**Errata aplicada nos docs (23/09/2026).** 69 trechos em `01`, `02`, `03`, `05`, `06`, `07`, `09`,
`schema-e-taxonomia-de-erros.md` e nos comentários de `base_pipeline.py`, todos recalculados com o `mes` real.
O que muda de conclusão, e não só de número:

- **Incidente do harness:** foi em **out/2025** (24 dos 33 casos, 59,0/1k steps), não em dez/2025. Some a partir
  de **mar/2026**, não de mai/2026. O limiar de reabertura quase não muda (teto do IC95% ≤ 0,99/1k com 0 casos
  em 3.037 steps; antes ≤ 0,87/1k em 3.461). O laço de 10 erros do `managerAgent` (`2a407143…`) e a concentração
  de "Explicação solta" (25/33 erros, 90% dos tokens) também são de out/2025.
- **Custo mensal:** a série ganha out/2025 e fev/2026. A conclusão "sem tendência de queda" **se mantém**: base
  nov/2025–jan/2026 em 39–50 mil, 2026 acima dela. out/2025 (88 mil) é o mês do incidente e fica fora da base.
- **Estabilidade do schema de `get_available_documents` (07 §11.5):** o único retorno com campos a mais é de
  jul/2026, o último mês com erro nesse nível e sozinho nele. A leitura anterior ("variação entre execuções, não
  mudança no tempo") dependia de o caso cair num mês com outros 3, o que só acontecia na datação por lote. **Não se
  sustenta mais**, e o 07 agora diz que o dado não separa as duas hipóteses.
- **Colunas `meses`** (triagem, sub-unidades, assinaturas) sobem, porque um lote juntava vários meses. As decisões da
  triagem, inclusive a sensibilidade ≥5/≥3, são idênticas.
- **Datas de casos citados** (logs 1–3 da §1.8, exemplos do 09, entregas não conformes da 11.9): passam ao mês
  real; as não conformes da 11.9 ficam em 5 meses, não 3.
- **Cobertura:** out/2025–ago/2026 (11 meses), não nov/2025–ago/2026.

O teste sintético da §1.7 (unidades inventadas, "3 meses") e as datas que não vêm do trace (datas de auditoria,
de trabalho, do diário) não mudam.

### 1.13 · O resíduo da taxonomia na base 1 (23/09/2026)

**A pergunta.** O que cai nos dois baldes de resíduo — os erros que nenhuma regra de causa reconheceu — e o que
cada caso pode significar? O racional dos baldes e das classes está em `01-racionais.md` §7 Passo 2 ("Os dois
baldes de resíduo").

**O método.** Todos os erros das unidades `X_causa_nao_identificada` e `X_sintoma_nao_reconhecido`, sem amostra.
Para cada um: a classe (o submecanismo), a assinatura do `classify()`, o `error.type`, a classe da exceção e a
frase da exceção **mascarada** — texto entre aspas → `<q>`, entre crases → `<id>`, números → `<n>` —, porque os
valores entre aspas podem ser dados do caso. Nos erros de sintaxe a frase não entra (a mensagem traz a linha de
código rejeitada).

**Evidência.** `uv run python drill_down.py residuo` (depois do notebook) → `resultados/evidencia/A5_residuo/`
(git-ignored): `casos.csv`, `derivados/residuo.csv` e os 9 crus.

**Resultado — 9 erros, 3 classes:**

| Classe | n | Casos (exec · papel · mês) | Exceção e frase mascarada | Leitura |
|---|---:|---|---|---|
| **Código Python mal escrito** | 4 | `456d8bf5`, `a80a9074` (managerAgent, out/2025) · `a47d6e3b` (ConversationAgent, mar/2026) · `b8a32b7b` (ConversationAgent, fev/2026) | `SyntaxError` ×3, `IndentationError` ×1 | código mal formado; nada em comum entre os casos além da classe |
| **Erro conhecido, causa sem regra** | 4 | `6dde0bab` (ConversationAgent, dez/2025) · `ab45d27a` (managerAgent, mar/2026) · `87e8f3f4` (managerAgent, nov/2025) · `f82e081a` (ConversationAgent, mai/2026) | `TypeError`: `<q> not supported between instances of <q> and <q>` · `TypeError`: `unsupported operand type(s) for \|: <q> and <q>` · `ValueError`: `dictionary update sequence element #<n> has length <n>; <n> is required` · `TypeError`: `FinalAnswerTool.forward() got an unexpected keyword argument <q>` | dois tipos: operação ou comparação entre tipos errados (vizinho de "retorno pode chegar como string"), e **argumento nomeado que não existe no `final_answer`** — um erro de contrato de chamada (o IAN do ToolScan), não um acaso |
| **Erro que a taxonomia não conhece** | 1 | `c4611fe3` (ConversationAgent, dez/2025) | `InterpreterError`: `NoneType is not supported.` | limitação do interpretador do smolagents; nenhuma regra de sintoma nem de causa a conhece |

**Conferir no cru.** `uv run python drill_down.py caso <exec_id> <role>`, ou em `A5_residuo/crus/<exec_id>.json`:
`txt_etap_memo` → papel → o `idx`-ésimo `ActionStep` → `error.message`.

**Recorrência por padrão** (a regra da triagem para o resíduo, `01-racionais.md` §7 Passo 5; tabela no notebook
9.2 e em `resultados/residuo_padroes.csv`). Os 9 erros formam **7 padrões**; um só se repete:

| Padrão | Erros | Execuções | Meses | Passa (≥3 exec., ≥2 meses)? |
|---|---:|---:|---:|---|
| `SyntaxError: closing parenthesis <q> does not match opening parenthesis <q>` | 3 | 3 | 2 (out/2025, mar/2026) | **sim** |
| os outros 6 padrões (um por linha da tabela acima) | 1 cada | 1 | 1 | não |

**O que isso mostra.** Na base 1 o resíduo é pequeno (9 de 498 erros, 1,8%) e só 1 é erro desconhecido. Contado pela
unidade, a "causa não identificada" pareceria recorrente (8 execuções, 6 meses), mas são 8 erros diferentes; contado
por padrão, aparece **o único que volta de fato**: parênteses que fecham com um tipo diferente do que abriram, em 3
execuções. Por isso a unidade sai **revisar — prioridade**, e o "sintoma não reconhecido" **revisar — baixa
prioridade**. É candidato a regra de causa nova, não memória ainda. Na base 2 (25 erros de sintoma não reconhecido), a
mesma tabela diz se são um erro novo que se repete ou vários soltos.

---

## Frente 2 — Verificar a literatura (aqui sim precisa da sua leitura)

Nem todo achado depende de paper. Separe antes de investir tempo:

| Não depende de nenhum paper (só do trace) | Depende de como um paper foi lido |
|---|---|
| Taxonomia por causa-raiz, custo em tokens, funil de propagação, mapa de calor de reincidência, taxa por papel — **§2 a §6 do relatório, os 6 gráficos** | O "ponto cego" de 59% (§5) — número do *dataset do TRAIL*, não do nosso trace |
| | "MAST não tem modo de falha para exceção" (§7) — depende do escopo lido corretamente |
| | A correção da citação do ToolScan (§7) — depende da extração certa dos 7 tipos |
| | Tipos da tabela de candidatos (§6 do relatório / §9 do notebook) — **a que mais importa**, molda o desenho dos candidatos reais. Desde 15/09/2026 vêm de Hu et al. 2025 (§4.1.2 e §4.2.2), não de um mapeamento módulo→tipo do AgentDebug |

Dado que este pipeline vai virar a base dos candidatos de memória de verdade, a prioridade de leitura segue o
critério que o projeto já usa em [`papers/reading-queue.md`](../../../papers/reading-queue.md): o que alimenta uma
decisão de arquitetura em uso agora vem antes do que só refina um componente.

| Ordem | Paper | Por que essa prioridade | O que checar especificamente |
|---|---|---|---|
| 1 | **AgentDebug** — arXiv:2509.25370 | A taxonomia de 5 módulos é a base da política de escrita por cascata e do schema de candidato a memória (`01-racionais.md` §8) — vale conferir a fonte primária antes de decidir arquitetura em cima dela | A seção da taxonomia (17 tipos / 5 módulos, Tabela 2); conferir que o paper **não** propõe tipos de memória nem roteamento módulo→tipo (overclaim já corrigido 14/09, checar que a leitura própria confirma) |
| 2 | **TRAIL** — arXiv:2505.08638 | Sustenta os números do "ponto cego" que quantificam quanto do relatório é "o que vemos" vs "o que não vemos" | As tabelas de distribuição por categoria; o split SWE-Bench (arquitetura igual à nossa) |
| 3 | **MAST** — arXiv:2503.13657 | Checagem pontual, rápida | O trecho do §4, p. 7, que põe explicitamente falhas de limitação de modelo fora do escopo |
| 4 | **ToolScan** — arXiv:2411.13547 | Menor prioridade — entra no relatório pra *refutar* uma afirmação errada da v1, não pra fundamentar algo novo | Os 7 tipos (IAC/IAV/IAN/IAT/RAC/IFN/IFE) contra o que está em [`literature/tool-use-errors.md`](../literature/tool-use-errors.md) |

**Como ler sem reler cada paper do zero:** os fichamentos em [`literature/`](../literature/) têm citações verbatim
com página/seção marcadas. A forma rápida de gerar confiança real é abrir o PDF direto na página citada e
confirmar que a citação existe e está no contexto certo — mais rápido que leitura corrida e ainda pega o erro
que mais importa (citação fora de contexto).

Os PDFs ficaram em `/tmp/trace_analysis/*.pdf` (não garantido persistir). Se precisar rebaixar:

```bash
curl -sL --max-time 60 -o agentdebug.pdf https://arxiv.org/pdf/2509.25370
curl -sL --max-time 60 -o trail.pdf      https://arxiv.org/pdf/2505.08638
curl -sL --max-time 60 -o mast.pdf       https://arxiv.org/pdf/2503.13657
curl -sL --max-time 60 -o toolscan.pdf   https://arxiv.org/pdf/2411.13547
```

Não commitar os PDFs no repo — manter como cópia de leitura local, fora do git.

Marque o progresso de leitura na `reading-queue.md` com a mesma régua que o projeto já usa: 📝 (verificado
bibliograficamente) < 🔎 (texto completo lido por agente — nível atual dos quatro fichamentos) < ✅ (lido por
você). Promova pra ✅ conforme for lendo de fato.

---

## O eixo comum: triangulação — do gráfico ao caso no trace cru

### Por que nenhum dos dois extremos basta sozinho

O **trace cru** é um CSV de 875 MB onde cada linha carrega um JSON aninhado — às vezes 27 MB numa única célula.
Não dá pra abrir "no olho": não carrega num Excel, não dá pra ler uma linha inteira sem ferramenta.

O **CSV limpo** (`resultados/erros_classificados.csv`) tem uma linha por erro, com `err_msg` cortado em 400
caracteres. Ótimo pra contar e agregar — é onde você sustenta "tive 98 KeyError" — mas corta fora o resto da
história: o *thought* do agente antes do erro, o código completo, a observação recebida depois.

A prática certa é sempre em duas etapas:

1. **Comece no agregado** (CSV limpo ou tabelas do notebook) para achar quantos, qual proporção, quais
   execuções.
2. **Escolha 2–3 `exec_id` concretos** representativos do padrão e **volte ao trace cru filtrado só naquela
   execução** — aí sim vale olhar, porque é um caso, não 1.000.

É o mesmo padrão que TRAIL e AgentDebug usam pra anotar seus datasets: exemplo por exemplo, nunca o dataset
inteiro de uma vez.

### A ferramenta: [`drill_down.py`](../pipeline/drill_down.py)

Comandos, sempre a partir da pasta `pipeline/` (o caminho do trace dentro do script é relativo a ela):

```bash
cd analysis/2026-09-trace-law-flow/pipeline

# 1a) do achado agregado, listar exec_id candidatos pra uma MENSAGEM de erro (etiqueta 1, sintoma)
python3 drill_down.py listar "Falha ao indexar o retorno (Could not index)"

# 1b) ou pra um MECANISMO (etiqueta 2) — lê resultados/erros_mecanismo.csv; rode o notebook antes
python3 drill_down.py mecanismo "Retorno pode chegar como string"

# 2) escolher um e ver a história completa daquela execução
python3 drill_down.py caso <exec_id> <role>
```

O nome tem que bater exatamente com o que aparece no gráfico/tabela — a assinatura para `listar`, o mecanismo
(nome da unidade, igual ao da §6 do relatório) para `mecanismo`. Mesmo texto do notebook e do relatório, de
propósito: permite ir do gráfico até o caso sem traduzir nada. Nome errado em `mecanismo` imprime a lista dos
disponíveis. *(Até 15/09 esta seção mandava rodar a partir da pasta da análise, com um venv em `/tmp`; o caminho
do trace no script só resolve a partir de `pipeline/`.)*

**Cuidado com a saída:** o script imprime nome de pasta/processo em claro. Não exportar/printar fora do
terminal local; para a reunião, copiar só o trecho relevante já revisado para o slide, nunca o terminal
inteiro sem checar antes.

### Evidência por análise — o trace cru primeiro, o derivado só espelha (17/09/2026)

Toda afirmação da mineração nº2/nº10 vem de código, e código pode errar de um jeito consistente: o mesmo leitor
aplicado a 91 erros dá o mesmo número 91 vezes, certo ou não. Por isso cada afirmação tem de poder ser levada ao trace
cru por uma pessoa, sem depender do código que a produziu. Até 16/09 isso existia só para os cinco logs da §1.8, numa
pasta solta. Agora vale para cada análise da §11 do notebook `mineracao_unidades_n2_n10.ipynb`, sempre do mesmo jeito:

1. **Uma pasta por análise**, com o número da seção do notebook — quem lê a análise acha a evidência pelo mesmo
   número. Cada notebook de análise é dono de um intervalo de seções (este, §11.x; o próximo passe, §12.x) —
   número nunca reutilizado, pasta nunca renomeada.
2. **Os casos saem de uma regra escrita**, não da escolha de quem argumenta. A regra fica no notebook e no `leia-me.md`
   da pasta (ex.: "o primeiro caso de cada mês em cada nível, mais todos os que diferem"). Escolher "os mais claros"
   fabrica a evidência que se quer ver.
3. **O cru é a fonte e vai inteiro.** `crus/<exec_id>.json` é a linha do trace sem nenhuma alteração — só o campo
   `txt_etap_memo` é desserializado, para dar para ler e apontar caminhos dentro dele. A linha inteira, e não só o step
   do erro, porque recortar já seria decidir o que o leitor vê.
4. **O derivado espelha o cru e diz de onde tirou cada coisa.** `derivados/<exec>_<role>_idx<n>.json` é a visão de um
   caso para leitura humana: só trechos copiados do cru, cada um com o caminho onde está (`cru`) e, quando é pedaço de
   um texto, o recorte (`caracteres`) ou o intervalo de mensagens (`mensagens`). O comando confere cada trecho contra o
   cru ao gravar e aborta se algum divergir. O que é calculado — a chave pedida, as chaves do objeto, onde elas
   aparecem no contexto — fica separado em `calculados`, com a regra. As tabelas da análise vão em `derivados/*.csv`,
   uma linha por erro, com `exec_id`/`role`/`idx` para voltar ao cru.
5. **O texto cru nunca passa pela saída do notebook.** O notebook decide os casos e grava só estrutura (`casos.csv`,
   tabelas, `leia-me.md`); quem grava os crus e as visões é o `drill_down.py`. O notebook versionado continua sem dado
   de caso.
6. **Ordem de leitura:** o derivado para ver o argumento; o cru para conferir. Se divergirem, vale o cru.
7. **Só os casos escolhidos têm cru.** Uma linha crua tem mediana de 358 KB (máximo 28 MB), e as 97 execuções da §11
   somam 155 MB; por isso cada pasta guarda de 2 a 12 casos, e as tabelas derivadas apontam para o resto, que se abre com
   `drill_down.py caso`.

**Como gerar** (a partir de `pipeline/`, depois de rodar o notebook):

```bash
uv run python drill_down.py evidencia                  # todas as pastas que têm casos.csv
uv run python drill_down.py evidencia 11.4_conserto    # uma pasta
uv run python drill_down.py evidencia <exec_id> <role> <idx> <ferramenta>   # um caso avulso → evidencia/avulso/
```

**As pastas da §11 (17/09).** Todos os trechos das visões conferidos contra o cru (641/641). Conferência independente
do comando: os 59 arquivos crus foram relidos contra o `.csv.xz` original, coluna a coluna (`txt_etap_memo` comparado
depois de `json.loads`), e são idênticos à linha do trace em 59/59.

| Pasta | Seção | O que sustenta | Regra de escolha | Casos | Cru |
|---|---|---|---|---:|---:|
| `11.1_origem_do_erro` | §11.1 | de qual função vem cada erro | todos fora da função dominante + o 1º de cada `via` da dominante | 12 | 32,9 MB |
| `11.2_schema_real` | §11.2 | a forma do objeto que a mensagem imprime | o 1º de cada forma distinta | 10 | 13,7 MB |
| `11.3_prompt_declara` | §11.3 | o que o system prompt declara para cada ferramenta | o 1º erro de cada ferramenta com schema lido | 3 | 1,6 MB |
| `11.4_conserto` | §11.4 | o que o agente fez depois (os cinco logs da §1.8) | por ferramenta, o 1º de cada desfecho de correção | 5 | 8,0 MB |
| `11.5_estabilidade` | §11.5 | o schema é o mesmo em todos os meses | o 1º de cada mês em cada nível + todos os que diferem | 11 | 8,3 MB |
| `11.6_status` | §11.6 | cobertura e resíduo | todos os erros do resíduo | 2 | 2,0 MB |
| `11.7_amostra_passo6` | §11.7 | a amostra do Passo 6 | sorteio com semente `20260917`, 5 por candidata | 10 | 9,1 MB |
| `11.8_registro_final` | §11.8 | os casos citados em `evidence` dos registros | os 3 primeiros de `location` de cada registro | 6 | 3,6 MB |

"1º" = primeiro na ordem (mês, `exec_id`, `idx`). Tudo em `pipeline/resultados/evidencia/`, git-ignored, **com PII** nos
crus e nas visões — não versionar, e redigir antes de citar em documento. As análises §1–§10 ainda não têm pastas assim
(pendência no `04-roadmap.md`).

### Exemplo já testado — a prova em texto corrido do achado central

Rodando `caso` na execução com 10 repetições consecutivas citada no relatório
(`2a407143-c37d-687f-4b4a-45f8dc413734`, papel `managerAgent`), a sequência real é:

- **Step 2** — o agente responde em texto puro (tabela markdown), sem bloco de código → erro "sem bloco de
  código".
- **Step 3** — o *thought* diz literalmente: *"Ocorreu um erro porque a resposta anterior não estava dentro
  de um bloco `<code>`"*. Ele diagnostica o próprio erro corretamente. Ao tentar corrigir, escreve uma frase
  de narração *antes* da tag `<code>`, e isso quebra de novo → erro de sintaxe.
- **Step 4** — o *thought* diz de novo: *"O erro foi causado por um texto explicativo dentro do bloco
  `<code>`"*. Diagnostica corretamente outra vez — e comete a mesma categoria de erro outra vez.

Isso é o §4 do relatório ("o agente lê o erro e reincide") capturado com as palavras do próprio agente. Numa
reunião, isso vale mais que qualquer barra de gráfico: mostra que o problema não é falta de informação (o
agente sabe o que errou), é a ausência de um mecanismo que traduza esse diagnóstico em comportamento
diferente — o argumento direto para memória procedural.

Por mecanismo ([`01-racionais.md`](01-racionais.md) §7), esses 10 erros seguidos são a maior cascata da unidade
"Explicação nunca solta no bloco de código": começa logo depois do erro de protocolo do harness de out/2025.

### Exemplos já testados (15/09/2026) — quando a mensagem engana e o mecanismo acerta

Abertos com `drill_down.py caso` para conferir a troca de régua de mensagem para mecanismo:

- **`CalculoCivel`, execução `42891135…`** — mensagem "Retorno é dict"; mecanismo "retorno pode chegar como
  string". No step 2 a ferramenta `calculo_correcoes_monetarias` imprime o resultado como texto JSON; no step 3 o
  agente faz `corr_mon["valor_corrigido"]` e quebra (`string indices must be integers`); no step 4 corrige com
  `isinstance(corr_mon, str)` + `json.loads`.
- **`RespostaBacen`, execução `1be966e7…`** — mensagem "Retorno é dict"; mecanismo "campo inexistente no retorno".
  No step 7 `validar_quebra_sigilo` devolve `{'vazamento_sigilo': …}` e o agente pede `quebra["quebra_sigilo"]`;
  no step 8 escreve o mapeamento `vazamento_sigilo → quebra_sigilo`. Esse caso mostra as três etiquetas de um
  erro de uma vez (sintoma, mecanismo e motivo — ver [`01-racionais.md`](01-racionais.md) §8).
- **`ConversationAgent`, execução `008d142f…`** — `docs_civel[0]` sobre `{'result': [[...]]}` (dict por posição),
  corrigido no step seguinte para `docs_civel['result'][0]`.
- **`ConversationAgent`, execução `0adcc967…`** — `next(m['valorMetadado'] for m in ...)` dentro de uma list
  comprehension quebra com `'list' object is not an iterator`; no step seguinte o agente troca por uma função
  auxiliar com `for`.
- Os dois pares em que mensagem e mecanismo discordam no §5 do notebook (`cd794f02…` e `95344639…`) estão
  descritos em [`01-racionais.md`](01-racionais.md) §3 Passo 8.

### Formato recomendado por achado, na apresentação

Para cada achado importante: **o gráfico agregado primeiro** (o "quantos"), seguido de **um `caso` real**
como o acima (o "como, na prática"). Um exemplo bom por achado é suficiente — não empilhar vários.

---

## Checklist pré-reunião

- [ ] Abri o notebook em Jupyter e rodei célula a célula pelo menos uma vez
- [ ] Conferi os 6 gráficos da seção 8 contra a célula de agregação correspondente
- [ ] Auditei ~20 mensagens de erro reais contra a função `classify()`
- [ ] Recomputei por fora pelo menos um número (ex.: % por família)
- [x] Rodei o teste de robustez do achado 86,3%/11,9% — três heurísticas, corrigiu o número de 13,7% pra 11,9%
- [ ] Li o trecho da taxonomia do AgentDebug (5 módulos) e conferi que o paper não propõe roteamento módulo → tipo de memória (é a nossa correção de 14/09, não uma citação do paper)
- [ ] Conferi as tabelas de distribuição do TRAIL que sustentam o "ponto cego"
- [ ] Conferi a citação do MAST (§4, p. 7) no contexto original
- [ ] Escolhi 1 caso concreto (via `drill_down.py caso`) para cada achado que vou apresentar
- [ ] Revisei a saída de cada `caso` antes de copiar qualquer trecho para o slide (PII)
- [x] Rodei a §11 do notebook `mineracao_unidades_n2_n10.ipynb` (mineração nº2/nº10) e salvei as saídas — 16/09, `nbconvert` (§1.7)
- [ ] Li os cinco logs da §1.8 e abri pelo menos um caso de `resultados/evidencia/11.4_conserto/` (PII — só local)
- [x] Fiz a verificação humana do Passo 6 — os 10 casos de `resultados/evidencia/11.7_amostra_passo6/` (§1.9, 17/09) — confirma os achados, 1 nota adicional não generalizável
- [ ] Decidi o destino da nº10 (memória × não-memória · harness) — `07-relatorio-mineracao-unidades-n2-n10.md` §6.1
