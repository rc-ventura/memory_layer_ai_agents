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

O venv criado para rodar a análise só tem as bibliotecas de execução (`nbformat`, `nbclient`, `matplotlib`),
não uma interface pra navegar. Para abrir com código, saída e gráfico juntos:

```bash
/tmp/trace_analysis/venv/bin/pip install jupyterlab
/tmp/trace_analysis/venv/bin/jupyter lab pipeline/analise_trace_esteira_juridica.ipynb
```

> Se `/tmp/trace_analysis/venv` não existir mais (`/tmp` não é garantido persistir entre sessões), recrie com:
> `python3 -m venv --system-site-packages /tmp/trace_analysis/venv && /tmp/trace_analysis/venv/bin/pip install nbformat nbclient ipykernel matplotlib jupyterlab`

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
prefixo × sufixo — as réguas convergem. A manchete continua 11,9%; ressalva: 20 dos 58 vêm do laço de dez/2025.

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
| §9 dos racionais, Passo 1 — de qual ferramenta vem cada erro (nº2: 94,8%; nº10: 70%) | a regra de rastreio da variável (AST; comando → step → steps anteriores) | conferência manual de todos os casos fora da dominante + amostra de 4 da dominante (16/09) | ⚠️ **conferido por amostra, não testado por variação** — as atribuições conferem; 5 (nº2) e 1 (nº10) ficam não resolvidos; o veredito da nº2 resiste ao pior caso (ver §1.7) |
| §9 dos racionais, Passo 2 — schema lido da mensagem | o método de leitura do objeto impresso | `ast.literal_eval` × regex tolerante | ✅ **robusto** — 89/89 e 7/7 concordam (ver §1.7) |

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

### 1.7 · Mineração das unidades nº2/nº10 (racionais §9) — como foi rodado, conferido, e onde desviou do pré-registro

Resultados em [`02-relatorio-achados.md`](02-relatorio-achados.md) §6.1; o porquê de cada passo e de cada régua em
[`01-racionais.md`](01-racionais.md) §9. Estado: Passos 1 e 2 de 8.

**Pré-registro.** O método foi commitado antes de rodar (`cb032ad`); o adendo ao Passo 3 (conserto silencioso com
`.get` / `try-except`) também, antes de o Passo 3 rodar (`ae8264b`). As emendas feitas depois de um passo rodar
estão datadas no próprio §9 dos racionais.

**Como reproduzir.** No Jupyter: rodar o notebook até o fim — as células da §11 só dependem da §1 (explosão em
steps), da §2 (`classify()`) e da célula "Do sintoma ao mecanismo". Nesta rodada a §11 foi executada fora do
Jupyter, só com essas células mais as da §11 (`uv run --python 3.13 --with pandas --with numpy --with matplotlib`),
para não regravar os CSVs de `resultados/`. **As saídas da §11 ainda não estão salvas no notebook.**

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
inclusive uma dominante recorrente) — ver `01-racionais.md` §9. As unidades reais seguem iguais: nº2 (a), nº10 (b),
bucket vazio.

**PII.** As células da §11 imprimem só nome de função, contagens, nomes de chave e tipos; chave com cara de dado vira
`<chave-dado>`. Nenhum valor retornado pelas ferramentas sai na tela.

**Ainda não feito:** a verificação por amostragem do Passo 6 (conferir o schema derivado contra o trace cru com
`drill_down.py caso`, 5 casos por unidade) — a conferência acima é da **regra de atribuição**, não do schema final.

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
"Explicação nunca solta no bloco de código": começa logo depois do erro de protocolo do harness de dez/2025.

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
- [ ] Rodei a §11 do notebook (mineração nº2/nº10) no Jupyter e salvei as saídas
