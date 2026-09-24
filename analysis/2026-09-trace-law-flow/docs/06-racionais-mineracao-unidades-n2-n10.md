# Racionais da mineração das unidades nº2/nº10 — continuação de `01-racionais.md`

**Para que serve este documento:** o mesmo de [`01-racionais.md`](01-racionais.md) — explicar *por que* a
análise foi conduzida assim, em prosa acessível — mas só para a segunda análise desta pasta: a mineração do
schema real das unidades de memória nº2 e nº10. Foi separada do documento principal em 18/09/2026 porque virou
uma análise própria (pré-registrada, com evidência por caso e produto final em `unidades_memoria.json`), não só
mais uma seção.

**Pré-requisitos, todos no documento principal:** a tabela de candidatos de onde esta análise parte
([`01-racionais.md`](01-racionais.md) §7), o que é um teste de robustez e a regra corrigir × retirar (lá, §2), o
schema do registro de unidade (lá, §8) e o detector `DEGENERADO` (lá, §4 Passo 2).

**Numeração preservada.** O corpo abaixo continua sendo a "§9 dos racionais", e o notebook companheiro
([`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb)) continua numerado "§11.x" —
assim as referências já escritas (`03-procedimento-validacao.md`, `04-roadmap.md`, `discussion/`, pastas
`../pipeline/resultados/evidencia/11.*`) seguem apontando para o lugar certo.

---

## 9 · Minerar as unidades nº2/nº10 — o schema real a partir do próprio trace, passo a passo

Números em [`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.1; como foi rodado, conferido e onde desviou
do pré-registro em [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.7; código no notebook [`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb), §11.

> **Em linguagem simples, antes do racional técnico.** Esta seção investiga dois erros que o agente comete ao ler a
> resposta de uma ferramenta. **nº2:** o agente chama `get_available_documents` (busca documentos) e trata a
> resposta errado — tenta `r[0]` quando o certo é `r['result'][0]`. **nº10:** o agente chama `validar_quebra_sigilo`
> e pede o campo `quebra_sigilo`, mas a ferramenta devolve o campo com outro nome: `vazamento_sigilo`.
>
> A pergunta é: dá para transformar cada um desses erros numa **memória** — uma frase certa, derivada do próprio log,
> que a próxima execução já recebe pronta, em vez de o agente ter que descobrir de novo?
>
> Os oito passos abaixo são o caminho até essa frase, cada um respondendo uma pergunta: o erro realmente vem de uma
> ferramenta só, ou de várias misturadas (Passo 1)? o que a ferramenta devolve de verdade (Passo 2)? o agente já
> tinha essa informação no prompt (addendum ao Passo 2)? o que o próprio agente fez para se corrigir (Passo 3)? isso
> é sempre igual, ou muda com o tempo (Passo 4)? dá para confiar no resultado (Passo 5)? isso bate com o log bruto,
> conferido à mão (Passo 6)? e, por fim, qual é a frase final (Passos 7–8)?
>
> O que vem a seguir é o racional técnico completo — cada decisão, cada régua e por que ela foi escolhida assim.
> Quem só quer o resultado pode ir direto a `07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

**Por que esta análise.** A tabela de candidatos (`01-racionais.md` §7) tem, para cada unidade, um "conteúdo proposto" escrito à
mão a partir de alguns casos lidos. Nas unidades *factual · ambiente* esse conteúdo é um fato sobre uma
ferramenta — e fato sobre ferramenta dá pra derivar do próprio trace e checar contra ele, sem LLM. As duas
escolhidas são as que carregam o schema de retorno de uma ferramenta: **nº2** ("Retorno das ferramentas de
documento é dict", submecanismos `dict_indexado_por_posicao` e `dict_iterado_como_lista`) e **nº10** ("Campo
inexistente no retorno estruturado", submecanismo `campo_inexistente_no_retorno`). A meta é trocar o texto
escrito à mão por conteúdo derivado e checado, no schema do `01-racionais.md` §8. A análise estava "adiada, não é prioridade" em
`04-roadmap.md` desde 08/09; foi reaberta em 16/09 para rodar **antes** da segunda extração, de modo que a base
nova sirva de teste de replicação do próprio schema minerado (ver
[`../../../discussion/open-questions.md`](../../../discussion/open-questions.md), item "Second trace extraction").

**Por que pré-registrado.** Os oito passos e as réguas de decisão foram escritos e commitados antes de olhar o
dado. O motivo é o mesmo de todo teste de robustez desta análise (`01-racionais.md` §2): se a régua é escolhida depois de ver o
resultado, fica impossível saber se o número fala do dado ou da régua. Regras acrescentadas depois de algum passo
rodar ficam marcadas com data e com a indicação de que não mudaram o resultado já obtido.

**Evidência de cada passo.** Cada análise desta mineração tem uma pasta com os casos escolhidos por regra, o trace cru de cada um e uma visão derivada que só espelha o cru — como é montada, gerada e lida está em `03-procedimento-validacao.md`, "Evidência por análise".

**Passo 1 — "ferramenta não é unidade": testar a premissa antes de escrever a lição.** O `01-racionais.md` §7 Passo 1 já provou,
um nível acima, que agrupar por sintoma esconde causas diferentes: a mensagem "Could not index" sozinha
misturava três problemas (89 dict-como-lista, 37 string-como-dict, 10 campo inexistente) até a régua virar
"submecanismo". O mesmo risco existe um nível abaixo, ainda não testado: um submecanismo pode misturar
**ferramentas** diferentes que quebram do mesmo jeito. Pista concreta, não confirmada:
`02-relatorio-achados.md` (linha 400) descreve a nº2 no plural — "**ferramentas** retornam
`{'result': [[...]]}`" — sugerindo que mais de uma ferramenta do `ConversationAgent` pode compartilhar esse
contrato quebrado, sem que isso já tenha sido contado.

Por que importa de verdade: se a nº2 for, na real, duas ferramentas — uma que devolve `{'result': [...]}` e
outra que devolve `{'conteudo': [...]}` —, uma lição única ("acesse sempre `r['result'][0]`") **acerta** para a
dominante e **atrapalha ativamente** a outra, porque a chave certa é diferente. Memória confiante e errada numa
fração dos casos é pior do que nenhuma memória.

**Operação:** para cada erro das duas unidades, olhar o `code_action` daquele step (já disponível em `RAW`) e
identificar qual função produziu o objeto que quebrou — o código de verdade, não a mensagem de erro. Na prática: a
mensagem traz o comando que falhou e o que foi pedido (`KeyError: 0`, `KeyError: 'quebra_sigilo'`,
`has no attribute get`); acha-se no comando, por AST, o nó que pediu exatamente isso, e segue-se a variável até a
chamada que a criou — no próprio comando, antes dele no mesmo step, ou em steps anteriores do mesmo papel, porque o
namespace Python persiste entre steps. Quando a variável não tem origem rastreável (ex.: o erro acontece dentro de
uma função auxiliar que o próprio agente escreveu), o caso fica **não resolvido** — nunca atribuído por palpite.
Contar, por unidade, quantos erros e quantas ocorrências vêm de cada função: erro é o que a regra lê; ocorrência
(cascata deduplicada, `01-racionais.md` §7 Passo 4) é o que a triagem de recorrência conta — por isso os dois níveis são reportados.

**Decisão:** ≥90% das ocorrências da mesma função → confirma "uma coisa só", sigo com essa confiança. Uma
segunda função com peso ≥10% → a unidade se divide, uma lição por ferramenta, não uma lição genérica.
**Expectativa declarada antes de rodar** (previsão a testar, não a resposta): provável "uma coisa só", já que a
unidade inteira é 100% `ConversationAgent` e `get_available_documents` sozinha já domina o trace inteiro (730
chamadas, `02-relatorio-achados.md` linha 48) — mas quem decide é a contagem, não essa expectativa.

**Por que a regra dos 10% é frágil com amostra pequena — e por que o destino não depende dela.** A régua tem duas
metades: **(a)** a função dominante cobre ≥90% dos casos → "uma ferramenta só"; **(b)** uma segunda função cobre
≥10% → a unidade se divide. Percentual sobre amostra pequena vira com um caso só: numa unidade de 10 erros, **um
único caso vale 10%** e já dispara (b); com 11 erros, o mesmo caso valeria 9,1% e não dispararia. Foi o que
aconteceu na nº10 (números em `07-relatorio-mineracao-unidades-n2-n10.md` §6.1). Dois fatos tiram o peso dessa fragilidade: se a
dominante fica longe de 90%, (a) falha de qualquer jeito, então a unidade não é "uma ferramenta só"
independentemente de (b); e uma função de 1 caso nunca passa na triagem de recorrência (≥3 execuções e ≥2 meses),
então disparar (b) com um caso só não transforma esse caso em memória. Por isso (a) e (b) descrevem a **forma** da
unidade, e o **destino** de cada pedaço é decidido pela triagem — abaixo.

**Emenda à régua (16/09/2026, decidida depois do Passo 1 rodar, sem mudar o resultado dele): o destino de cada
sub-unidade.** O pré-registro dizia como dividir a unidade, mas não o que fazer com cada pedaço, nem com o caso em
que nem (a) nem (b) se cumprem — **(c)**: dominante abaixo de 90% e o resto espalhado em funções abaixo de 10% cada.
Uma primeira versão da emenda mandava a unidade (c) inteira para um bucket; um teste com dados sintéticos mostrou o
problema — uma dominante de 70%, recorrente, viraria candidata numa unidade (b) e ficaria sem memória numa unidade
(c), só porque o resto estava mais espalhado. A regra ficou uniforme, igual para (a), (b) e (c), aplicada a cada
sub-unidade `(unidade, função)`, nesta ordem:

1. **Passa na triagem de recorrência → candidata.** Mesma régua do `01-racionais.md` §7, pelo mesmo motivo: memória entre execuções
   só se justifica se o problema volta. Vale para a dominante e para qualquer outra função que passe (ex.: 60/40,
   as duas recorrentes → duas candidatas).
2. **Não passa, e cobre ≥10% das ocorrências da unidade → documentada e monitorada.** Não é descarte: ficar fora
   por falta de recorrência numa amostra de 1.000 linhas, com provável `LIMIT` (`04-roadmap.md` item 3), não prova
   que o problema não recorre. Mesma lógica do protocolo do harness (`02-relatorio-achados.md` §6):
   dormente, com gatilho de reabertura explícito — **na segunda extração, reaplicar a triagem a cada
   `(unidade, papel, função)`; se passar em ≥3 execuções e ≥2 meses, na base nova ou nas duas somadas depois do
   dedup por `cod_idef_exeo`, vira candidata.** É o caso frágil: a dominante vira memória, as funções de 1 caso
   ficam monitoradas. **Confirmação empírica do próprio design (22/09/2026):** é exatamente o que aconteceu com
   o protocolo do harness — dormente na base 1, gatilho disparado ao rodar a base 2 (diário de campo,
   22/09/2026; `04-roadmap.md` §Monitoramento) — evidência de que a política "monitorada, não deletada" tem
   trabalho real a fazer, não é só formalismo.
3. **Não passa, e cobre menos de 10% → bucket de consulta.** Uma fatia pequena de uma unidade não justifica gatilho
   próprio, mas também não some: fica listada caso a caso, sem memória, para abrir com
   `drill_down.py caso <exec_id> <role>` — mesma ideia do balde "Sintoma não reconhecido" da `classify()`.

A fatia é medida em **ocorrências**, o mesmo nível que a triagem conta. Casos **não resolvidos** (sem função
atribuída) não entram nessa escada — não há função para triar: ficam documentados, com a atribuição a refazer.
Implementado no notebook §11.1 (coluna `destino` e tabela `BUCKET_CONSULTA`).

**Passo 2 — extrair o schema real da própria mensagem de erro, e reforçar com o `thought` (só por presença de
texto, nunca por interpretação).** O formato do smolagents (`Could not index {valor} with {chave}`) embute o
valor retornado de verdade — já confirmado no exemplo documentado (`1be966e7…`, step 7:
`{'vazamento_sigilo': 'NAO', 'justificativa': '...'}` pedindo `'quebra_sigilo'`). **Operação:** regex pra
separar `{valor}` de `{chave}`; `ast.literal_eval(valor)` primeiro (nunca `eval` — não executa nada); se falhar
(valor truncado, aspas quebradas — risco real na nº2, que pode carregar texto de documento), cair pra um regex
tolerante que só puxa as chaves de topo (`r"'(\w+)':"`), sem tentar reconstruir o objeto inteiro. **Teste de
robustez embutido** (mesmo espírito do prefixo-vs-sufixo do `01-racionais.md` §3 Passo 6): rodar os dois métodos nas mesmas
ocorrências e comparar quantos casos cada um resolve e se as chaves batem — divergência grande é sinal de regra
errada, não de dado ruim.

**O reforço do `thought`, e onde a linha determinístico/não-determinístico passa exatamente.** O `thought`
daquele mesmo step pode confirmar, **por presença literal de texto**, se o agente já "esperava" aquela chave ou
ferramenta antes do código quebrar — mesmo mecanismo do detector determinístico do item 6 do roadmap (regex no
`thought` vs. AST no `code_action`, sem juiz). Isso **entra** como evidência extra pro `description`. O que
**não entra** aqui: interpretar *por que* o agente achou que a chave era aquela (alucinou? confundiu com outra
ferramenta?) — isso exige julgamento sobre texto livre, não é achar uma string, e cai fora da escada de degraus
inteira (ver Passo 7).

**O que exatamente a mensagem mostra, e o que se tira dela.** O objeto impresso é o que foi **indexado**, não
necessariamente o retorno inteiro da ferramenta: se o agente já tinha descido um nível (pegou um documento de
dentro da lista e o indexou como se fosse lista), o que aparece é esse pedaço. Por isso cada objeto lido é
descrito pela sua **forma** (chaves e tipos), e a leitura de cada caso diz em que nível da estrutura ele está —
não se soma cegamente tudo num schema só. Uma lista pode ter elementos de tipos diferentes, e por isso a forma
descreve **todos** os tipos presentes, não só o do primeiro elemento; um dicionário de contagens por valor é
resumido como `{<campo>: {<valor>: int}}`, porque as chaves dele são dado, não schema. **Só estrutura sai deste passo** — nomes de chave e
tipos, nunca valores: o objeto de uma ferramenta de documento pode trazer texto de peça, nome e número de processo.
Pelo mesmo motivo, uma chave com cara de dado (sequência longa de dígitos, texto livre) é mascarada como
`<chave-dado>`. A checagem de sanidade embutida é barata e diz se a leitura faz sentido: a chave que o agente pediu
**não** pode existir no objeto lido — se existisse, não teria havido erro.

**Addendum ao Passo 2 (16/09/2026, pré-registrado antes de rodar): a informação já estava no prompt?** O `thought`
diz o que o agente pensou; o system prompt (`sysprompt`, já extraído em `RAW` — a primeira mensagem do contexto,
onde as ferramentas são declaradas) diz o que ele **recebeu**. São fontes diferentes e a pergunta é diferente:
não "o agente esperava essa chave" (Passo 2), mas "essa chave já estava disponível pra ele checar, antes de
escrever o código". Isso importa direto para o Passo 7 — se a chave certa já está descrita no prompt e o agente
mesmo assim erra, a lacuna não é de informação ausente (que memória resolveria de cara); se não está, é.
**Operação:** para cada erro, checar por presença literal de texto (regex, sem interpretação) se o `sysprompt`
daquele step contém (a) a(s) chave(s) reais do schema minerado no Passo 2 e (b) a chave errada que o agente usou.
Reporta-se a contagem, não se decide nada a partir dela — é insumo para a leitura do Passo 7, não um novo critério
de status. A presença é medida em três formas, da mais frouxa à mais estrita — palavra solta, entre aspas, e **como
chave de JSON** (`'chave':`) —, porque um nome pode aparecer no prompt como prosa ou como valor de exemplo sem estar
declarado como chave; só a forma estrita responde a pergunta, e a distância entre as três mostra quanto as frouxas
enganariam. E como uma chave pode estar declarada para **outra** ferramenta, registra-se também se ela aparece
dentro do bloco `def ferramenta(...)` da própria ferramenta (acrescentado ao rodar, não pré-registrado): é o que
separa "o prompt fala desta chave" de "o prompt diz que esta ferramenta devolve esta chave".

**Passo 3 — cruzar com a autocorreção do próprio agente.** Reaproveita o que já está calculado em `01-racionais.md` §3 (430/498
leram o erro no contexto seguinte). Para as ocorrências de nº2/nº10 especificamente, pegar o `code_action` do
step seguinte na mesma execução e checar se ele acessa a mesma variável com uma chave/índice diferente do que
falhou. Isso dá uma **segunda fonte independente** da chave certa — o `1be966e7…` já documenta isso: o próprio
agente escreve o mapeamento `vazamento_sigilo → quebra_sigilo` num comentário no step seguinte. Onde essa
correção existe, ela confirma (ou contradiz) o que o Passo 2 extraiu da mensagem de erro — uma terceira fonte
determinística, independente das duas primeiras.

**Adendo pré-execução ao Passo 3 (16/09/2026, registrado antes de rodar): nem todo conserto confirma a chave
certa.** Em Python há dois jeitos de ler um campo de dicionário: `quebra["quebra_sigilo"]` **quebra**
(`KeyError`) se a chave não existe — é o que aparece no trace; `quebra.get("quebra_sigilo", "NÃO")` **não
quebra** — se a chave não existe, devolve em silêncio o valor padrão (`"NÃO"`). Um agente pode "consertar" o
erro trocando o primeiro pelo segundo: o código passa a rodar, mas ele não aprendeu a chave certa, só calou o
erro. Neste caso concreto seria pior que o erro — como `quebra_sigilo` nunca existe, a leitura sempre devolveria
`"NÃO"`, e o agente afirmaria "não houve quebra de sigilo" qualquer que fosse a resposta da ferramenta em
`vazamento_sigilo`: erro silencioso numa resposta regulatória. **É um risco a vigiar, não algo já observado no
trace.**

**O padrão é escolha do agente, não `"NÃO"` (emenda de 16/09/2026, antes de rodar).** O exemplo usa `"NÃO"`, mas o
segundo parâmetro de `chave.get("campo", segundo_parametro)` é o que o agente quiser — `None`, `""`, `0`, `[]`,
`"SIM"`, outra variável — e é **ele** que decide qual erro silencioso acontece: `"NÃO"` afirma ausência de quebra,
`"SIM"` afirmaria o contrário, `None` empurra o vazio pra frente (e pode ou não quebrar mais adiante). Por isso o
tipo 2 abaixo registra também **o segundo parâmetro**: o literal, quando é uma constante curta; o tipo do nó
(`Name`, `Call`…), quando não é; ou "sem padrão" (equivale a `None`).

Regra — o conserto no step seguinte é classificado em três tipos:

1. **Troca de chave** — a mesma variável passa a ser lida por uma chave/índice diferente (ex.:
   `["vazamento_sigilo"]`, `["result"][0]`), com ou sem `.get` → conta como confirmação (ou contradição) do
   Passo 2.
2. **Conserto silencioso** — a mesma chave errada continua, mas protegida por `.get(...)` (com ou sem padrão) ou
   por um `try/except` que engole o erro → **não** confirma nada; contado à parte, como sinal suspeito, com o
   segundo parâmetro registrado.
3. **Sem conserto comparável** — o step seguinte não lê mais a variável, ou o agente mudou de estratégia → sem
   evidência para aquele caso (ausência, não contradição).

**O que a regra não previu, e por que foi tratado assim (16/09/2026, ao rodar).** A pergunta do Passo 3 é "o que o
agente fez com o **objeto** que quebrou" — e o nome da variável nem sempre continua apontando para esse objeto:

- **Reatribuição.** Se o step seguinte faz `docs = docs['result'][0]` e depois lê `docs[0]`, esse segundo acesso é
  sobre outro objeto; contá-lo como "repetiu o erro" confundiria nome com objeto. Só contam as leituras antes da
  reatribuição e as do lado direito dela. Reatribuir **chamando a mesma ferramenta de novo** não corta: o objeto é
  novo, mas o schema é o mesmo, e a pergunta continua válida.
- **Guarda de tipo.** `docs['result'][0] if 'result' in docs else docs[0]` troca para a chave certa e mantém a antiga
  num ramo condicionado ao tipo da própria variável. Conta como troca de chave — o caminho que roda é o novo —, mas
  marcada à parte, porque a guarda é informação: o agente corrige sem confiar que a forma do retorno é estável.
- **Nível da comparação.** A chave nova é comparada com o schema da **ferramenta** inteira, não só do pedaço que
  quebrou: o agente pode corrigir lendo outro nível do mesmo retorno (ex.: quebrou num item de metadado, corrigiu
  lendo o documento).

**Evidência caso a caso — por que cinco logs, e como foram escolhidos (16/09/2026, depois do Passo 3; não
pré-registrado).** O addendum ao Passo 2 mostrou que, nos 7 erros de `validar_quebra_sigilo`, o agente pediu
`quebra_sigilo` e o bloco da ferramenta no prompt declara `quebra_sigilo`. Daí sai uma afirmação forte: **o prompt
ensina um contrato errado, o agente segue o prompt, e a falha é da documentação da ferramenta, não do agente.** Forte
porque muda o destino da unidade (conserto na origem, harness, em vez de memória) e porque aponta um defeito na
plataforma de outro time. Dois números que coincidem não bastam para isso: não mostram que a chave veio do prompt, nem
como o agente chegou na certa. Quem mostra é o log — o texto que o agente recebeu, o código que ele escreveu, o que a
ferramenta devolveu e o que ele fez depois. O caminho, passo a passo:

1. **Separar duas afirmações antes de procurar evidência.** "O prompt declara um contrato explícito diferente do real"
   (`validar_quebra_sigilo` e `extrair_evidencias`: um JSON com outras chaves) não é a mesma afirmação que "o prompt
   descreve o retorno de modo incompleto" (`get_available_documents`: "uma lista de documentos e um resumo", sem o
   envelope `result`). A primeira se verifica lendo o bloco da ferramenta; a segunda depende de como o agente
   interpreta uma frase. Cada uma recebe os seus logs e a sua conclusão, e é esperado que terminem com força diferente.
2. **Ler o que o prompt diz, não só se a chave aparece.** O addendum conta presença de chave, e presença não diz o que
   o prompt afirma sobre ela. Por isso a §11.3 passou a imprimir o texto literal com que o bloco descreve o retorno, e
   `drill_down.py ferramenta <nome>` lista todas as variantes da declaração no trace inteiro: se o texto tivesse mudado
   ao longo dos meses, a afirmação valeria só para uma parte do período.
3. **Escolher os casos por regra, não a dedo.** Para cada ferramenta, o primeiro caso em ordem cronológica de cada
   desfecho de correção do Passo 3 (troca sem guarda, troca com guarda de tipo, conserto com `.get`), no máximo dois
   por ferramenta. Escolher "os mais claros" produziria exatamente a evidência que se quer ver. Os desfechos sem
   conserto ficam de fora porque a pergunta inclui como o agente descobre e corrige.
4. **Fazer as mesmas quatro perguntas a cada log.** (a) O que o bloco da ferramenta declara? (b) Que linha quebrou, e
   que objeto a mensagem imprime? (c) A chave real já estava no contexto do agente antes do erro — no prompt ou num
   `print` anterior — ou aparece pela primeira vez depois? (d) O que o `thought` e o código do step seguinte fazem? A
   (c) é a que separa "não tinha a informação" de "tinha e errou mesmo assim", e é por ela que as duas afirmações do
   item 1 terminam diferentes.
5. **Dizer o que um log prova e o que não prova.** Um log mostra a sequência: o prompt diz X, o agente escreve X, a
   ferramenta devolve Y, o agente lê Y e troca. Não prova que o prompt **causou** o erro — `quebra_sigilo` é também o
   nome óbvio para o campo, e o log não mostra qual das duas menções do prompt (o bloco da ferramenta ou o modelo do
   JSON final) o agente seguiu. Causa só se testa mudando a documentação, ou injetando a memória, e medindo de novo: o
   replay contrafactual do Passo 7.
6. **Separar o que vai para o documento do que fica local.** Os trechos citados em `03` são redigidos (valores
   trocados pelo tipo, números e nomes de variável com número mascarados). O texto cru — o system prompt inteiro que o
   agente recebeu e as mensagens que ele leu antes de corrigir — sai em JSON por `drill_down.py evidencia`, em
   `resultados/` (git-ignored), para quem precisar conferir a fonte.

Os cinco logs e as conferências de apoio estão em [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.8;
o que eles sustentam, em [`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md) §6.1.

**Monitoramento além do Passo 3 (candidato a detector — registrado, não rodado).** O Passo 3 só olha o step
seguinte a um erro. Mas, com o schema real da ferramenta em mãos (Passo 2), o mesmo padrão vira um detector de
falha silenciosa para o trace inteiro, inclusive em steps que nunca levantaram exceção: toda leitura
`x.get("campo", padrão)` em que `x` vem de uma ferramenta de schema conhecido (atribuição do Passo 1) e `"campo"`
**não existe** nesse schema devolve sempre o padrão — erro sem exceção, invisível hoje (o ponto cego registrado em
`../../../discussion/open-questions.md`). Determinístico: AST + o schema minerado. Entra como candidato ao lado dos
detectores silenciosos do roadmap (itens 2 e 13), não como parte deste pré-registro.

**Passo 4 — checar estabilidade entre ocorrências e ao longo do tempo, por ferramenta — e o subproduto que isso
gera de graça.** As chaves reais são as mesmas nas N ocorrências, nos M meses cobertos? **Se sim** → fato
estável, memória factual de alta confiança. **Se não** (ex.: um mês mostra schema diferente) → não forço uma
linha única; reporto "schema mudou em `<mês>`". **Subproduto, não escopo original deste passo:** esse mesmo
teste de estabilidade, rodado uma vez pra minerar a unidade, produz de graça um **detector reaproveitável** —
quando um schema historicamente estável quebra de repente, isso é sinal determinístico de **anomalia de
ambiente** (a API da ferramenta mudou), não de comportamento do agente. É exatamente a distinção que
[`../../../discussion/open-questions.md`](../../../discussion/open-questions.md) já registra em aberto
("Should the deterministic anomaly filter... distinguish agent-behavior anomalies from environment/
infrastructure anomalies"), hoje sem proxy proposto. Não é escopo desta mineração construir o filtro inteiro —
mas o subproduto fica registrado como candidato a bloco de construção reutilizável pra aquele item.

**Passo 5 — regra de decisão do que vira `status: derived-and-checked` vs. resíduo (pergunta diferente do Passo
1).** O Passo 1 pergunta "estou agrupando a coisa certa?" (correção de **escopo**). Este passo pergunta "eu
consegui *ler* o dado direito o suficiente pra confiar no que extraí?" (confiabilidade de **extração**) — são
perguntas independentes: mesmo com o Passo 1 respondido "é uma ferramenta só", a extração ainda pode falhar
caso a caso (mensagem truncada, aspas quebradas). **Regra:** ≥90% das ocorrências parseadas com sucesso no
Passo 2 **e** nenhuma contradição de schema entre elas no Passo 4 → `status: derived-and-checked`. Abaixo
disso, ou com contradição → `status: "parcial"`, cobertura exata reportada, resíduo sempre explicitado — nunca
escondido, mesmo princípio já aplicado no roadmap ("não forçar camada 2 no resíduo").

**Emenda ao Passo 5 (17/09/2026, depois da verificação humana do Passo 6 achar o caso `3f44a68b…`): confirmação
indireta por `AttributeError`.** Duas leituras não esgotam o que a mensagem pode provar. Quando o erro é "dict
iterado como lista" (`for d in objeto`, depois `.get()` numa das chaves — que vira uma string sem método `.get`), o
smolagents formata como `Object <chave> has no attribute get`: não imprime o objeto inteiro, só a chave em que a
iteração parou. Isso não é o mesmo nível de evidência do Passo 2 (não dá pra derivar a forma toda) — mas é
evidência: se essa chave já é conhecida do schema, derivado de **outros** erros da mesma ferramenta, ela confirma
(ou contradiria) o mesmo fato. **Regra, geral desde o início — não escrita para os 2 casos que a motivaram:** para
qualquer erro do tipo `AttributeError` numa ferramenta com schema já derivado, extrair a chave da mensagem e checar
se ela está no schema; se sim, conta como "lido ou confirmado" na cobertura do Passo 5, ao lado da leitura direta
(reportado à parte, para não inflar silenciosamente o número); a leitura estrita (só objeto lido de fato) continua
reportada, sem essa confirmação. **Por que não é circular:** o schema contra o qual se confere vem sempre de
**outros** erros (os 89 lidos diretamente), nunca do próprio caso sendo confirmado — não tem como o método
"confirmar" uma chave errada que ele mesmo inventou. **Efeito nos dois casos que motivaram a emenda:** cobertura por
erro da nº2 sobe de 89/91 para 91/91; por ocorrência já era 100% (os dois estavam em execuções com outro erro lido);
o status não muda. Números em `07-relatorio-mineracao-unidades-n2-n10.md` §6.1; código e verificação em
`03-procedimento-validacao.md` §1.9.

**Passo 6 — verificação humana por amostragem, antes de aceitar o candidato final.** Abrir manualmente uma
amostra pequena (5 por unidade, incluindo ao menos 1 caso do resíduo não-parseado do Passo 5) via
`drill_down.py caso()` e conferir se o schema derivado bate com o trace cru — mesma disciplina do item 12 do
roadmap ("rodar, triangular com `drill_down.py` contra casos concretos antes de reportar"). Esta verificação
não é opcional mesmo se o Passo 5 der 100% de cobertura sem contradição: cobertura alta garante que o método
foi **consistente**, não que ele está **certo** — é possível estar consistentemente enganado (ex.: o regex do
Passo 2 sempre pegando a chave errada de um jeito sistemático).

**Passo 7 — o que este método produz é causa raiz, mas de um nível específico; o que ele não produz, e por
quê.** O schema real da ferramenta (degrau 2 · descrição) e a instrução de ação (degrau 3 · correção) são
causa raiz **da falha de execução**: o `KeyError` aconteceu porque faltava uma informação verificável (a chave
certa), e essa informação, uma vez presente, fecha exatamente esse buraco. Isso não é definição nova para este
passo — é a mesma que o pipeline usa desde a v2, já registrada na "Ressalva de método" do `01-racionais.md` §7: *"Tudo aqui é
classificado pelo que o trace **mostra** — a mensagem de exceção e a linha que falhou —, não pelo raciocínio
do agente."* O AgentDebug, quando lê o *thought* pra decidir em qual módulo cognitivo o erro nasceu, responde
uma pergunta diferente e mais funda — **por que** o agente escreveu aquele código (alucinou o schema? nunca
leu a declaração da ferramenta? ruído de sampling?). Essa pergunta não é degrau 2 nem degrau 3 desta escada:
cai nos módulos `memory`/`reflection` do AgentDebug, já registrados em `04-roadmap.md` (sub-achado do item 10)
como **fora de alcance sem LLM** — não é um gap novo desta análise.

**Degrau 2 → degrau 3: o mesmo fato, dois modos gramaticais.** Não são dois achados diferentes. Degrau 2
narra o que aconteceu, modo indicativo, uso forense: "a ferramenta X devolve `{chaves reais}`; o agente pediu
`{chave errada}`". Degrau 3 reformula a mesma informação como instrução de ação futura, modo imperativo — é o
payload que vai pro contexto do agente: "ao ler o retorno de X, use `{chave real}`, não `{chave errada}`". Uma
vez que os Passos 2–4 derivam o schema real e o padrão de acesso errado, ir de degrau 2 pra degrau 3 é reescrita
quase mecânica, não pede dado novo — por isso os dois entram juntos no schema final (`01-racionais.md` §8).

**O que fica genuinamente de fora, sem correção proposta aqui.** A causa cognitiva (por que o agente errou, não
só o que ele errou) exigiria uma de duas alavancas que o projeto já decidiu não usar em v1: mudança de
harness/prompt (`../../../discussion/open-questions.md`, item "Update Engine as candidate to propose harness
changes in v2" — adiado pro v2) ou treino/ajuste do modelo (fora de escopo do projeto inteiro,
`scope-and-terminology-decisions.md#1`, mecanismo não-paramétrico). A memória factual não resolve isso porque
não é esse o tipo de buraco que ela tapa. O teste que decide se ela é suficiente já está definido na
arquitetura: replay contrafactual — "`M` voltou a ocorrer em `R` depois da escrita?" Se a reincidência cair
depois da correção injetada, era buraco de informação; se persistir mesmo com o fato disponível no contexto, é
sinal de que o problema é de harness, não de memória — dado empírico barato pra decidir se escala pro v2, não
palpite.

**Passo 8 — o schema final de saída.** "Unidade", pra fins deste schema, é a granularidade que sobra depois do
Passo 1 — pode ser a linha original de `candidatos_memoria.csv` (se confirmado "uma ferramenta só") ou uma
sub-unidade por ferramenta (se o Passo 1 dividir). Cada campo do schema de `01-racionais.md` §8 tem uma origem específica, sem
mistério:

| Campo | Origem |
|---|---|
| `category` | a unidade em si — produção própria do projeto (`01-racionais.md` §7) |
| `location`, `evidence`, `impact` | **TRAIL** (Apêndice A.11 — anotação por span) |
| `description`, `correction_guidance` | **AgentDebug** (Stage 1/2 — descrição do caso e diretiva corretiva) |
| `occurrences`, `status`, `validation` | produção própria do projeto — a disciplina "derivado-e-checado vs. hipótese" (Commit Gate), não vem de nenhum paper |
| `scope` (papel/ferramenta) | produção própria do projeto — achado empírico de `02-relatorio-achados.md` §6 ("a chave de recuperação da unidade deve ser (papel, unidade), não global") |
| `validation.destino` | **campo novo, sub-produto da análise funda de 17/09 (§9, "Análise funda da nº10")** — `"memória"` \| `"harness"` \| `"em aberto"`. Existia como texto solto no código antes de 17/09 (`registro_final`); formalizado aqui depois que a nº10 foi o primeiro registro a receber um valor de verdade, não a frase genérica. Ver a nota abaixo sobre por que este campo importa pro v2. |

**Por que `validation.destino` importa além desta análise (17/09/2026).** Até 16/09 o schema tratava toda
unidade como candidata a memória — "harness" era só o oposto informal ("não é memória"). A nº10 é o primeiro caso
em que esse rótulo foi **decidido por regra pré-registrada e evidência medida** (`07-relatorio-mineracao-unidades-n2-n10.md` §6.2), não
por impressão: o prompt declara o mesmo nome de campo para o retorno da ferramenta e para a saída final, o agente
confunde os dois, e isso mede-se direto no payload entregue, sem precisar do replay contrafactual que o Passo 7
(acima) previa como o teste "de verdade". Ou seja: **existe hoje um caminho mais barato que o replay para produzir
o sinal harness × memória** — comparar o contrato declarado no prompt com o schema real e com o que foi
efetivamente entregue. Isso conecta direto com o "Update Engine" hipotetizado para o v2 do mecanismo de memória
(`../../../discussion/knowledge-as-infra-architecture-hypothesis.md`, componente C, "v2 harness-change loop") — nota
cruzada lá.

**`location`/`evidence` são lista, não exemplo único.** A unidade só virou candidata por ter recorrência (≥3
execuções/≥2 meses) — a evidência tem que carregar essa recorrência, não um caso isolado escolhido a dedo.
Proposta: `location` = lista de `{exec_id, role, step}` (capada em ~10 amostras + contagem total para unidades
grandes, como as 96 da nº2); `evidence` = 2–3 excertos representativos, **redigidos** (só chaves de topo, nunca
o conteúdo de string dentro delas — mesma regra de PII já usada pelo `drill_down.py`, crítica aqui porque a nº2
vem de ferramentas de documento).

**`scope: {role, tool}` como campo de primeira classe, não enterrado dentro de `location`.** É o que decide de
qual "prateleira" de memória o agente vai puxar depois — batendo direto com o `ACL(μ, uid)` ainda em aberto na
arquitetura (`../../../discussion/open-questions.md`).

**`impact`: `null` nesta rodada — decisão explícita, não omissão.** O `impact` do TRAIL é atribuído por
anotador (humano ou juiz lendo o span), não por fórmula — "usar a metodologia do TRAIL" de verdade significaria
rodar um juiz, o que este passo (determinístico, sem LLM) não faz. Preencher com uma proxy inventada agora
(ex.: frequência ou custo em tokens) repetiria o erro que o próprio `impact` existe pra evitar — `01-racionais.md`
`01-racionais.md` §8 já avisa que confundir frequência com gravidade é exatamente essa armadilha. Fica `null`, pendente do item
11 (gold-standard + juiz calibrado).

### Execução dos Passos 4 a 8 (17/09/2026) — como cada um foi feito, e o que o pré-registro não fixava

Números em `07-relatorio-mineracao-unidades-n2-n10.md` §6.1; conferência em `03-procedimento-validacao.md` §1.9; código no notebook,
§11.5–§11.8; evidência em `resultados/evidencia/11.5_…` a `11.8_…`. Os passos rodam só nas **sub-unidades candidatas**
do Passo 1 — `(ConversationAgent, get_available_documents)` na nº2 e `(RespostaBacen, validar_quebra_sigilo)` na nº10.
As sub-unidades de 1 caso ficam como estavam (documentar e monitorar). Cada decisão abaixo que não estava escrita
antes de rodar está marcada como tal.

**Passo 4 — o schema é o mesmo em todos os meses?**

1. **Separar os níveis antes de comparar.** O objeto que a mensagem imprime às vezes é o retorno inteiro
   (`{result: …}`) e às vezes um documento de dentro dele (`{hashDocumento, metadado, tipoExtracaoOcr}`). Comparar os
   dois chamaria de "mudança de schema" o que é só outro nível da mesma estrutura. O nível é dado pelas chaves de topo
   do objeto lido. *(Não fixado no pré-registro.)*
2. **Comparar cada forma com a mais comum do seu nível**, e não com a do primeiro mês: a mais comum é a melhor
   estimativa do fato estável, e o primeiro mês pode ser justamente o ponto fora. *(Não fixado.)*
3. **Dizer o que é "contradição".** O Passo 5 exige "nenhuma contradição de schema", sem definir o termo. Definição
   adotada: **contradição** é faltar uma chave da forma comum ou um tipo mudar — o que tornaria falso o conteúdo da
   memória. **Campos a mais** — a forma comum inteira está lá, mais alguma chave de tipo simples — é registrado, mas não
   contradiz: a memória usa as chaves da forma comum, e uma chave extra nula não as torna falsas. **Esta definição foi
   escrita depois de o Passo 2 já ter mostrado um retorno com dois campos a mais** (`iuDocsId`, `iuDocsTenantId`,
   nulos), então não é cega. Por isso a leitura estrita — qualquer diferença conta — é calculada ao lado e levada ao
   Passo 5.
4. **Só os meses com erro são observados.** Um mês sem erro não diz nada sobre o schema: a ferramenta pode ter
   devolvido qualquer coisa sem que ninguém a indexasse errado.
5. **O subproduto fica registrado, não construído.** O detector de anomalia de ambiente (schema estável que quebra de
   repente) continua como bloco para o item "Should the deterministic anomaly filter…" de `open-questions.md` —
   pendência no roadmap.

**Passo 5 — status.** A régua é a pré-registrada (≥90% das ocorrências com objeto lido e nenhuma contradição). Falta
dizer quando uma **ocorrência** conta como lida, já que uma ocorrência pode ter vários erros: conta se **pelo menos um**
dos seus erros teve o objeto lido — um objeto lido basta para saber o que a ferramenta devolveu naquela cascata.
*(Não fixado.)* O status sai nas duas leituras do Passo 4; a adotada é a que não trata campos a mais como contradição,
e a estrita fica ao lado, com o mesmo destaque. O resíduo (erros sem objeto lido) é listado caso a caso, com o motivo,
e cada caso vai para a pasta de evidência.

**Passo 6 — amostra para conferir contra o trace cru.**

1. **Sortear, e com semente.** O pré-registro dizia "5 por unidade, incluindo ao menos 1 do resíduo", sem dizer como
   escolher. Sorteio, para que a amostra não seja escolhida; semente fixa (`random.Random(20260917)`, a data da
   rodada), para que seja a mesma em qualquer execução. Na nº10 não há resíduo, então a exigência de 1 caso do resíduo
   não se aplica. *(Não fixado.)*
2. **Três fontes por caso, e só duas independentes.** (1) O objeto que a mensagem de erro imprime tem a forma comum?
   É o mesmo leitor do Passo 2 aplicado de novo — mede consistência, não acerto, e é justamente o risco que o Passo 6
   existe para cobrir. (2) As chaves do schema aparecem no **log de `print`** que o agente recebeu? É outro texto,
   produzido por outro caminho (o `print` do agente, não o formatador de erro do smolagents). (3) O conserto do
   Passo 3 lê uma chave do schema? É o código que o próprio agente escreveu depois.
3. **A verificação humana continua sendo o Passo 6.** O pré-registro diz "verificação humana", e uma leitura feita
   por agente — mesmo abrindo o cru — não é isso. A tabela do notebook e a pasta `11.7_amostra_passo6/` existem para
   deixar essa verificação curta: cada caso tem o cru e uma visão que aponta onde olhar. Enquanto ela não for feita, o
   registro diz "verificação humana: pendente".

**Passo 7 — `description` e `correction_guidance` por molde, não por redação livre.** O §9 já dizia que ir do degrau
2 ao 3 é "reescrita quase mecânica". O molde fixo preenche: a forma comum (Passo 4), o pedido mais comum do agente
(Passo 2), o acesso certo e a cláusula sobre o prompt (11.3). Redação livre — de pessoa ou de LLM — seria texto sem
validação, exatamente o que a disciplina "derivado e checado" evita. Dois pontos do molde:

- **O acesso certo vem do código que funcionou.** A primeira versão usava só a chave nova do Passo 3 e escreveu
  "use `r['result']`" — que não resolve, porque os documentos estão em `r['result'][0]`. Agora o acesso é a cadeia
  completa de índices que o próprio agente escreveu na variável que quebrou, contada só nos consertos de troca de chave
  cujo step seguinte roda sem erro; vale a mais comum que começa pela chave nova. *(Corrigido ao rodar.)*
- **A cláusula sobre o prompt sai do 11.3.** Se o bloco da ferramenta declara a chave errada em todos os prompts, a
  `description` diz isso e a `correction_guidance` avisa que o prompt diz outra coisa; se o bloco não declara nenhuma
  chave do retorno, a `description` diz isso.

**Passo 8 — o registro.** Campos do §9 acima, com três escolhas de preenchimento:

- **`location` alterna os meses** (o primeiro caso de cada mês, depois o segundo de cada mês…, até 10). A unidade é
  candidata por recorrer entre meses; dez casos do mês com mais erros esconderiam isso. *(Não fixado.)*
- **`evidence` são os 3 primeiros de `location`** — portanto de 3 meses diferentes —, só com estrutura: pedido e forma
  do objeto indexado. *(Não fixado.)*
- **O registro não decide o destino da nº10.** Quando a correção contradiz o system prompt, `validation.destino` diz
  isso e deixa a decisão memória × harness em aberto. O registro também guarda o conteúdo que foi escrito à mão na `01-racionais.md` §7
  (`conteudo_escrito_a_mao_que_este_registro_substitui`), para a comparação ficar visível.

**Ressalva final, residual — não é a lacuna do Passo 7, é outra.** Este método só cobre erros que já bateram em
alguma regra de `submecanismo()`. Uma falha silenciosa nova, do mesmo tipo de problema (schema de retorno
errado) mas sem exceção e sem match em nenhum detector existente, não aparece em nada disto — mesmo ponto cego
já registrado em `../../../discussion/open-questions.md` (item "Second trace extraction").

### Análise funda da nº10 — as leituras do retorno de `validar_quebra_sigilo` (pré-registro, 17/09/2026)

> **Em linguagem simples, antes do racional técnico.** Os oito passos acima acharam os **erros**: 7 vezes o agente
> pediu a chave `quebra_sigilo`, a ferramenta não tem esse campo, o programa quebrou e o agente se corrigiu. Erro
> que quebra é erro barato — alguém vê, o agente tenta de novo, custa tokens.
>
> Esta análise pergunta a outra metade: **e quando não quebra?** O mesmo pedido errado pode passar em silêncio —
> `r.get("quebra_sigilo", "")` devolve string vazia sem reclamar, um `try/except` engole a exceção, um
> `if "quebra_sigilo" in r` simplesmente não entra. Nesses casos o agente segue em frente achando que leu o campo, e
> pode escrever no JSON final de uma resposta ao Bacen um campo de sigilo vazio, ou com um valor-padrão que ele
> mesmo escolheu.
>
> Se isso acontecer ao menos uma vez, o achado muda de natureza: deixa de ser **custo** (retry, tokens) e vira
> **risco** (resposta errada, sem ninguém perceber). É essa diferença que decide o destino da nº10 — memória, ou
> ticket pro time da plataforma.

**Por que esta análise, e por que agora.** É o ataque direto à ressalva do parágrafo anterior: o método dos oito
passos só enxerga erro que já bateu em alguma regra de `submecanismo()`, e uma leitura errada que **não** levanta
exceção não aparece em lugar nenhum. Aqui a ressalva vira pergunta mensurável, para uma ferramenta só — a única em
que o prompt declara o contrato errado nos dois lugares (bloco da ferramenta e molde do JSON final, 135/135 steps),
inclusive na grafia do valor (`"NÃO"` declarado × `'NAO'` devolvido). Ela precisa rodar **antes** da decisão sobre a
nº10, porque é ela que diz se o prompt errado custa retry ou produz resposta errada.

**O universo.** As execuções cujo system prompt declara `validar_quebra_sigilo` — hoje 26 execuções e 135 steps pela
contagem de `drill_down.py ferramenta validar_quebra_sigilo`, a reconferir no notebook. Dentro delas, cada
`x = validar_quebra_sigilo(...)` achado por AST no `code_action` de cada step. Execução que declara a ferramenta e
nunca a chama é contada à parte ("declarada, nunca chamada") e fica **fora** da classificação de leitura — não há
retorno para ler. Determinístico, sem LLM, como todo o §11.

**O que conta como leitura do retorno.** Mesma regra do Passo 3, já implementada em `acessos()` na §11.0: a partir da
variável que recebeu a chamada, contam as leituras dela no mesmo step e nos steps seguintes do mesmo papel — o
namespace Python persiste entre steps. Se o código reatribui a variável a outra coisa, contam só as leituras
anteriores à reatribuição e as do lado direito dela; depois disso a variável já não é o retorno da ferramenta.
Reatribuir chamando a **mesma** ferramenta não corta.

**As cinco classes — a unidade de classificação é a leitura, não a execução.**

| Classe | O que é | Como é reconhecida no código | O que significa |
|---|---|---|---|
| **(a) chave real** | lê o campo que existe | chave lida ∈ chaves reais derivadas no Passo 2 (`vazamento_sigilo`, `justificativa`) | correto |
| **(b) chave declarada, com erro** | `r['quebra_sigilo']` sem proteção | chave ∈ declaradas-só-no-prompt **e** o erro daquele step pede exatamente essa chave | visível: custa retry |
| **(c) chave declarada, sem erro** | `.get(chave, padrão)`, dentro de `try/except` que pega tudo, ou em ramo guardado por `in` | chave declarada-só-no-prompt **e** o step não tem erro pedindo essa chave | **silenciosa** — o alvo desta análise |
| **(d) objeto inteiro repassado** | `{"quebra_sigilo": quebra}`, `json.dumps(quebra)` — o dict inteiro vai adiante | a variável aparece sem subscrito dentro de uma estrutura que segue para o JSON final | depende de quem consome |
| **(e) chamado, nunca lido** | chamou e não usou o retorno | nenhum acesso à variável | sem efeito |

A fronteira (b)/(c) é decidida pelo **erro do step**, não pela forma do acesso: mesma chave errada, o que muda é se
levantou exceção. Isso reaproveita a leitura de erro já validada nos Passos 1–2, em vez de criar régua nova. Os
sinais `protegido` / `padrão` / `guardado` que `acessos()` já devolve entram como **motivo** do silêncio na tabela de
(c) — é o que explica *por que* não quebrou.

**A régua da grafia do valor — separada das chaves.** Um acesso pode acertar a chave e ainda assim comparar com o
literal errado. Conta como **grafia divergente** a comparação (`==`, `!=`, `in [...]`) entre uma variável derivada do
retorno e um literal de string que (i) não está entre os valores observados no trace para aquele campo e (ii) vira um
valor observado depois de normalizar caixa e acento. Hoje o valor observado é `'NAO'` nos 6 casos negativos vistos, e
o prompt declara `"NÃO"` — comparação que é falsa sem levantar exceção nenhuma. A referência é o conjunto de valores
**observados no trace**, não o que o prompt diz.

**Rótulo da execução.** Cada leitura tem sua classe; a execução recebe a classe mais severa presente, na ordem
**(c) > (d) > (b) > (a) > (e)**. O rótulo serve para dirigir a atenção humana, não para dizer o desfecho: o desfecho
de (c), (d) e grafia é decidido caso a caso no passo seguinte.

**Consequência — só para (c), (d) e grafia.** Para cada caso dessas classes, seguir se o valor lido chega ao
`final_answer` / JSON final daquele papel, e com que **categoria** de valor (vazio, literal-padrão curto, `SIM`,
`NAO`). O valor de verdade só é afirmável quando o trace mostra: houve `print` do objeto, ou houve erro que revelou a
estrutura. Sem isso, o caso é **candidato**, não confirmado — e o relatório usa essas duas palavras, sem misturar.

**O que será reportado.** (1) tabela por classe, com leituras e execuções; (2) tabela de grafia; (3) a lista completa
dos casos (c), (d) e grafia, com `exec_id`, papel, `idx` e o que foi lido; (4) a separação candidato × confirmado;
(5) a contagem "declarada no prompt, nunca chamada". Implementação numa **§11.9** do notebook, no mesmo molde das
outras (título · o que faz · como ler · célula curta), reaproveitando `indexar_steps`, `acessos`, `resolve` e
`registrar_evidencia` da §11.0.

**Evidência.** Pasta `resultados/evidencia/11.9_leituras_quebra_sigilo/`, mesmo padrão das outras (`casos.csv`,
`leia-me.md`, `crus/`, `derivados/`). Aqui entram **todos** os casos de (c), de (d) e de grafia — não uma amostra,
porque são poucos e são exatamente o que sustenta o achado — mais o primeiro caso de cada outra classe, para
comparação. Cada caso de (c) e de grafia é **aberto no cru antes de ser reportado**, com a disciplina do Passo 6.

**A decisão que esta análise alimenta — fixada antes de ver o número.**

- **≥1 caso confirmado** de (c) ou de grafia cujo valor chega ao `final_answer` → o prompt errado produz resposta
  errada, não só retry: a nº10 é tratada como **harness, com urgência**, e `impact` deixa de ser `null`.
- **Só candidatos, nenhum confirmado** → reportar como risco não confirmado; a nº10 continua em aberto e a pendência
  passa a ser abrir esses casos na esteira real (replay), não no log.
- **Nenhum caso** → o achado fecha como **custo**, e a nº10 pode seguir como memória.

**As três escolhas que foram do Rafael (17/09/2026), não minhas.** Ficam nomeadas porque mudam a conclusão, não só
a implementação: **(1)** o limiar que manda a nº10 pro harness é **um caso confirmado** chegando ao `final_answer` —
não se aplica aqui a triagem de recorrência (≥3 execuções, ≥2 meses) que vale para memória, porque risco regulatório
não precisa recorrer para existir; **(2)** o escopo é **só `validar_quebra_sigilo`** — `get_available_documents` e
`extrair_evidencias` sofrem do mesmo tipo de leitura silenciosa, mas nenhuma delas trava a decisão da nº10 e ficam no
roadmap; **(3)** a análise **segue o valor até o `final_answer`**, e não para na leitura — sem isso nenhum caso seria
confirmado e a decisão sairia sem prova. As demais réguas desta subseção não foram escolha de ocasião: saem de
disciplinas já fixadas no `01-racionais.md` §2 e no §9 deste documento (referência vem do trace e não do prompt; candidato e confirmado não se
misturam; hipótese não confirmada vira resultado escrito).

**Limites, declarados antes de rodar.** São 26 execuções numa base com `LIMIT` provável — é contagem de casos, não
taxa. Só `RespostaBacen`. O valor que a ferramenta devolveu só é visível quando o agente imprimiu ou quando houve
erro; sem isso, (c) mostra que o campo **pode** estar errado, não que está. E a hipótese que motivou a pergunta
(`dbc472b0…`, `.get("quebra_sigilo", "")`, vista na §11.5 revertida em 16/09) é **hipótese a testar**: se ela não se
confirmar, isso também é resultado, e fica escrito como resultado.

**PII.** Nada de texto de documento na tela: a análise reporta contagens, nomes de chave e categorias de valor.
Literais de valor só saem quando curtos e sem dígitos longos, pela régua de `chave_segura()`/`segundo_parametro()` já
em uso. É a lição dos dois incidentes de 16–17/09 (`03-procedimento-validacao.md` §1.7 e §1.9).

### Execução da análise funda (17/09/2026) — o que apareceu, contado do começo

Números completos em `07-relatorio-mineracao-unidades-n2-n10.md` §6.2; conferência, com a retratação descrita abaixo, em
`03-procedimento-validacao.md` §1.10.

#### A virada: existe uma medida direta, e o pré-registro não a tinha previsto

O pré-registro mandava **ler o código** do agente e classificar as leituras do retorno. É uma medida indireta: do
código eu infiro o valor. No meio da execução apareceu uma medida melhor, que estava no trace o tempo todo e que eu
não tinha visto — **o payload que a esteira entregou**.

Quando o agente chama a ferramenta que submete a resposta, o `action_output` daquele step guarda o `request`
inteiro: um objeto de quatro campos (`id_reclamacao`, `resposta_orgao`, `resposta_cliente`, `quebra_sigilo`). O campo
`quebra_sigilo` entregue está ali, literal. Não é inferência — é o que saiu.

Essa medida **desmentiu a primeira versão desta análise**, e a retratação está registrada em
`03-procedimento-validacao.md` §1.10. Vale a mesma regra do `01-racionais.md` §2: achado errado é **retirado por escrito**, com o que
o derrubou.

#### A medida direta: o que foi entregue no campo de sigilo

Das 26 execuções que declaram a ferramenta, **21 chegaram a entregar** um payload com o campo `quebra_sigilo`
(5 nunca entregaram o campo). Nessas 21:

| o que foi entregue no campo | execuções | meses |
|---|---|---|
| `'NAO'` ou `'SIM'` — o valor esperado | **12** | 4 |
| **o objeto inteiro da ferramenta** (`{justificativa, vazamento_sigilo}`) | **7** | 2 |
| um **texto de 203 caracteres** (não é `SIM`/`NAO`) | **1** | 1 |
| **string vazia** (`''`) | **1** | 1 |

**9 das 21 entregas — 43% — puseram no campo de sigilo algo que não é `SIM` nem `NAO`.** Em cinco meses diferentes
(dez/2025, jan–mar/2026, jun/2026). Nenhuma delas levantou exceção; nenhuma aparece em qualquer contagem de erro do
pipeline, porque não há erro nenhum a contar.

#### Os três jeitos de errar o mesmo campo

1. **O objeto inteiro no lugar do valor (7 execuções).** O código é literalmente
   `"quebra_sigilo": quebra_sigilo_obj` — o dicionário devolvido pela ferramenta vai inteiro para o campo que
   deveria conter `SIM` ou `NAO`. É a classe (d) do pré-registro, que eu tinha classificado como "depende de quem
   consome". Não depende: o consumidor recebeu um dicionário onde esperava duas letras.
   Por que o agente faz isso tem uma explicação direta no prompt: **o campo do JSON de saída e o campo do retorno da
   ferramenta têm o mesmo nome, `quebra_sigilo`**. O prompt declara os dois assim. Ao ver `quebra_sigilo` dos dois
   lados, passar o objeto de um para o outro é a leitura mais natural da instrução.
2. **O texto longo (1 execução).** Mesma confusão, um passo adiante: em vez do objeto, foi o texto da
   justificativa.
3. **O campo vazio (1 execução).** É o caso `dbc472b0…`, de dez/2025 — o único em que a leitura silenciosa do
   pré-registro aconteceu em forma pura:

   ```python
   quebra_saida = quebra.get('quebra_sigilo', '')      # a chave não existe → devolve ''
   json_resposta = { …, 'quebra_sigilo': quebra_saida }
   final_answer(json_resposta)
   ```

   A chave pedida é a do prompt, não existe no retorno, e o `.get` com padrão `''` devolve string vazia sem
   reclamar. O payload saiu com o campo de quebra de sigilo em branco. **É exatamente a hipótese que a §11.5
   revertida em 16/09 tinha levantado** — agora confirmada, e confirmada pela via forte: não pelo formato do código,
   mas pelo que foi entregue.

#### O erro que a leitura estática me fez cometer

A primeira versão desta análise apontou `8dd410c8…` como o caso confirmado: o agente teria trocado
`r["quebra_sigilo"]` por `r.get("quebra_sigilo")` e entregue `None`. **Estava errado**, e o payload entregue
mostrou: aquela execução entregou `'NAO'`, o valor certo.

A causa do meu erro é instrutiva. O código de verdade era:

```python
'quebra_sigilo': new_quebra.get('vazamento_sigilo', new_quebra.get('quebra_sigilo'))
```

Uma **cadeia**: pede primeiro a chave certa; a chave errada é só o plano B, e o plano B nunca roda, porque o
primeiro `.get` acerta. Meu classificador andava pela árvore sintática e via os dois `.get` como duas leituras
independentes — contava o plano B como se fosse a leitura que valeu.

Esse mesmo padrão de cadeia aparece em três execuções (`8dd410c8…`, `6b8e118d…`, `e2d4f9ea…`), e as três entregaram o
valor certo. Numa quarta (`21a4fa6c…`) a cadeia está invertida — chave errada primeiro, chave certa como plano B — e
mesmo assim entrega certo, porque o plano B salva.

Duas lições ficam registradas:

- **`.get` aninhado é uma cadeia, não duas leituras.** A régua de classificação precisa avaliar a cadeia inteira: se
  qualquer chave dela existir, a leitura resolve. A §11.9 implementa assim.
- **Leitura de código é proxy; payload entregue é fato.** Onde o trace guardar o resultado, a medida direta manda.
  Passa a valer para as próximas análises deste tipo.

#### O acento existe, mas está escondido atrás do erro de chave

A outra metade da pergunta era a grafia: o prompt declara `"SIM"`/`"NÃO"`, a ferramenta devolve `'SIM'` e `'NAO'`
(sem acento). Comparar `== "NÃO"` é sempre falso, e falso sem levantar exceção.

Há **duas comparações divergentes, em duas execuções** — e as duas estão **na mesma linha em que o step falhou**: a
linha é `if r["quebra_sigilo"] == "NÃO":`, a indexação errada estoura primeiro, e a comparação nunca chega a ser
avaliada.

> O erro da chave **blinda** o erro do acento. Enquanto a chave estiver errada, o acento nunca se manifesta.

Daí a consequência prática: **corrigir só a chave torna o erro de grafia ativo — e ele é silencioso.** Os dois têm
que ser corrigidos juntos. (Numa execução o agente escreveu sozinho `in ["NAO", "Nao", "NÃO", "Não"]`, cobrindo as
quatro grafias: de novo, inconsistência, não incapacidade.)

#### O que estes números decidem

A regra de decisão estava fixada antes de rodar: **um caso confirmado de campo errado chegando à resposta final
basta** para tratar a nº10 como problema de harness. Não há um caso — há **nove**, medidos no payload entregue, em
três meses.

1. A nº10 **deixa de ser candidata a memória** e passa a `harness`. O prompt declara o contrato errado em dois
   lugares e usa **o mesmo nome** para o campo de saída e para o campo do retorno; memória aqui seria remendo sobre
   instrução ambígua.
2. O `impact`, até aqui `null`, ganha conteúdo medido: **9 de 21 respostas entregues (43%) com o campo regulatório
   de quebra de sigilo inválido**, sem nenhum erro registrado. Não é custo de retry.
3. Nasce um método reaproveitável, mais valioso que a nº10 em si: **comparar o que o agente entregou com o schema
   que a ferramenta devolve** encontra falha que nenhum detector de exceção acha. Virou item de roadmap para as
   demais ferramentas de contrato conhecido.

#### As outras duas ferramentas com documentação divergente — por que uma foi mais longe e a outra não (17/09/2026)

O escopo original (Escolha 2 do Rafael, acima) era só `validar_quebra_sigilo`. Depois que a medida direta apareceu
— comparar o valor entregue com o schema real — ficou barato demais checar rapidamente as outras duas ferramentas
com o mesmo tipo de divergência de documentação (`03-procedimento-validacao.md` §1.8): o motivo original do recorte
(nenhuma delas travava a decisão da nº10) continua verdadeiro, mas não é mais motivo para não olhar, já que olhar
não custa quase nada.

**`get_available_documents` (nº2) — achado real, mas travado no limite de PII.** É a ferramenta mais chamada do
trace (730 vezes). Vasculhando o mesmo padrão — `.get(chave, sem_padrão)` sobre o retorno — apareceram **2 execuções**
com a mesma forma do bug da nº10:

```python
docs_by_protocolo = get_available_documents(...)
documents = docs_by_protocolo.get('documents')   # 'documents' não é chave real — só 'result' é
```

`'documents'` e `'summary'` não são chaves do schema derivado no Passo 2 (só `result` é). Sem segundo argumento,
o `.get` devolve `None` em silêncio, e esse `None` segue como argumento de outra chamada de ferramenta
(`answer_question_using_documents(documents=None, …)`). O step terminou sem erro e marcado como final.

Aqui a análise para onde a da nº10 conseguiu ir além: `validar_quebra_sigilo` tem um campo de saída único e
nomeado (`quebra_sigilo`) que aparece **estruturado** no `action_output` — dava para comparar o valor sem ler texto.
`get_available_documents` alimenta uma resposta em **texto livre**; para dizer se a resposta saiu errada eu
precisaria ler esse texto e compará-lo com o conteúdo real dos documentos — exatamente o tipo de leitura de conteúdo
que a regra de PII da sessão proíbe (`03-procedimento-validacao.md` §1.9, incidente de 17/09). O detector de resposta
degenerada que já existe no pipeline (`DEGENERADO`, definida no setup §0 deste notebook) não acusou nada nos dois casos — o que não prova
que a resposta saiu certa, só que não saiu obviamente vazia.

**Fica como candidato, não confirmado**, com o limite declarado: mesma forma de bug da nº10, consequência não
verificável sem violar a disciplina de PII. Registrado em `07-relatorio-mineracao-unidades-n2-n10.md` §6.2 e no roadmap, sem bloquear
nada — a nº2 já está `derived-and-checked` e não muda de status por isso.

**`extrair_evidencias` — verificada e descartada, não esquecida.** Só **8 execuções** declaram a ferramenta no
prompt, com **1 erro conhecido** no total (`03-procedimento-validacao.md` §1.8, Log 3). Duas razões descartam o
mesmo aprofundamento: a amostra é pequena demais para qualquer contagem valer como achado, e o retorno dela não
alimenta um campo único e nomeado como `quebra_sigilo` — o conteúdo se espalha dentro do texto da resposta, então a
mesma medida direta (comparar payload estruturado) não se aplica sem reintroduzir leitura de texto livre. Fica
registrada como investigada, com o motivo de não ter avançado escrito — não como pendência esquecida.

### Análise funda da nº2 — leituras silenciosas de `get_available_documents` (17/09/2026)

**Por que esta análise, e por que não é cega como a da nº10.** A tabela de destino/impact (`01-racionais.md` §8) só existe para a
nº10; a nº2 continuava com `analise_funda: "pendente"` desde a padronização de schema desta sessão. Diferente da
nº10, este pré-registro **não parte de zero**: uma sessão anterior, fora do notebook e sem pré-registro (pasta
`resultados/evidencia/11.10_leituras_get_available_documents/`, gerada por um agente, não pelo pipeline), já tinha
olhado 3 casos a dedo e relatado "2 confirmados" — leitura silenciosa (`.get("documents")`/`.get("summary")` sem
plano B) que faz o `final_answer` afirmar ausência de documentos que existiam de verdade no retorno da ferramenta.
Essa exploração motivou a pergunta, mas **contamina** a cegueira do pré-registro — por isso o que segue separa
explicitamente o que já era conhecido (o mecanismo, a existência de pelo menos 1 caso) do que é genuinamente novo
e cego (a contagem exaustiva no universo completo, e o cruzamento com um detector já validado, nenhum dos dois
feito antes).

**O que ficou fixado antes de rodar.**

1. **Universo.** Toda `(exec_id, role)` cujo system prompt declara `get_available_documents`, e dentro dela toda
   chamada `var = get_available_documents(...)` achada por AST (`chamadas_de`) — não só os steps que já erraram.
2. **Rastreio entre steps.** A partir do step da chamada, percorrer os steps seguintes do mesmo papel aplicando
   `acessos()` (já usada e validada no Passo 3 da mineração original) a cada um, até uma reatribuição de `var` que
   não seja "chamar `get_available_documents` de novo" — mesmo critério de corte já usado dentro de um único step,
   agora entre steps.
3. **Classificação de cada leitura.** `real` se a chave é `result` (o único nível de topo que interessa aqui — as
   chaves por documento, já derivadas no Passo 2, não entram nesta contagem, que é sobre o envelope); senão
   `errada`. Dentro de `errada`: **guardada** (dentro de um ramo condicionado a checar a própria chave/tipo antes —
   inclui os 17 casos já documentados de guarda de tipo, e é dead code sempre que a condição nunca é satisfeita
   pelo schema real, como `'documents' in retorno`) e **protegida** (dentro de `try/except`) ficam de fora da
   contagem de "silenciosa" — não é que rodaram sem consequência, é que a análise desta rodada não decide o que
   acontece dentro delas (ver "o que fica de fora", abaixo). O que sobra, sem guarda e sem proteção, se divide em
   **visível** (o step tem erro — deveria coincidir com os 91 já conhecidos, é o teste de consistência do método)
   e **silenciosa** (o step não tem erro — o alvo desta análise).
4. **O teste de consistência antes de contar qualquer coisa nova.** As leituras classificadas "visível" precisam
   bater com o conjunto já conhecido dos 91 erros da nº2 (`ATRIB`, `unidade == "U_contrato_dict"`) — se não
   baterem, o método tem um bug, não um achado. Só depois desse teste passar os números novos contam.
5. **O sinal de dano, sem inventar lista de palavras.** Para cada leitura silenciosa, checar se a resposta **real**
   entregue (a do `managerAgent`, não a saída intermediária do `ConversationAgent` que a pasta exploratória tinha
   lido) bate o detector `DEGENERADO` (`n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente`) — o único
   detector de resposta ruim já validado no pipeline, porque vem do texto literal do próprio system prompt
   (`01-racionais.md` §4 Passo 2), não de uma lista inventada. **Decisão fixada antes de rodar:** se `DEGENERADO`
   não bater em nenhum caso, a análise não eleva `impact` nem muda `destino` — só registra `analise_funda`, porque
   inventar uma lista de palavras nova sobre a saída do `ConversationAgent` (o que a pasta exploratória tinha
   feito) repetiria o erro que derrubou o "reasoning-action mismatch" (`01-racionais.md` §2).
6. **O que fica de fora, declarado antes de rodar.** Leituras guardadas por uma condição que a chave real nunca
   satisfaz (`'documents' in retorno`, sempre falso) não são "sem consequência" — ao contrário, o `if` nunca entra
   e o ramo verdadeiro (que usaria os documentos reais) nunca roda, então os documentos são **descartados por
   inteiro**, incondicionalmente, toda vez que esse padrão de código aparece. Isso é um mecanismo distinto do
   ".get sem plano B" (aqui não sobra um valor errado, sobra ausência total) e pré-registrar uma régua para ele
   exigiria antes decidir, caso a caso, se a condição de guarda é satisfazível pelo schema real — trabalho que
   não estava pronto a tempo desta rodada. Fica registrado como achado à parte, não quantificado exaustivamente
   (`04-roadmap.md`), não misturado ao número de "silenciosas" desta análise.

**Execução e resultado — o mecanismo ".get sem plano B".** 635 papéis declaram `get_available_documents`; 597
leituras rastreadas no universo completo. Teste de consistência: das leituras sem guarda/proteção com o step em
erro, 93 batem com os 91 erros já conhecidos (a pequena folga vem de mais de uma leitura por erro em alguns steps
— esperado, não é uma divergência). **4 ocorrências silenciosas confirmadas** (uma por execução: `175cd9f2…`,
`26e300f1…`, `910fde1e…`, `a47d6e3b…`), em 3 meses (2025-11 ×2, 2026-03, 2026-06). Restou também, sem ser contada
como silenciosa nem como achado (resíduo explicitado, não escondido, `04-roadmap.md`), **8 leituras** sem
guarda/proteção, com erro no step, que não batem os 91 já conhecidos.

**O sinal de dano, com três checagens independentes, não só `DEGENERADO`.** As 4 execuções chegam a um
`final_answer` real do `managerAgent` (a execução não trava). Três checagens estruturais na resposta real, nenhuma
lendo conteúdo de documento: (1) `DEGENERADO` (recusa explícita, do texto do próprio system prompt); (2) presença
literal de `None`/`null` (o valor que um `.get` sem plano B devolve, se vazar pro texto); (3) um regex frouxo pra
"parece um dict/objeto Python impresso" (o mesmo mecanismo que a nº10 achou na classe "objeto inteiro repassado",
`07-relatorio-mineracao-unidades-n2-n10.md` §6.2 — cobre o caso de vazar a estrutura toda, não só `None`). **Nenhuma das 4 bate nenhuma das três.**

**Execução e resultado — o segundo mecanismo, "guarda sobre chave fantasma", quantificado (não deixado de fora).**
O item 6 acima só registrava a *decisão* de não misturar este mecanismo ao número de "silenciosas"; ele foi, à
parte, contado exaustivamente com a mesma disciplina: um detector de AST específico (`'chave' in retorno` cuja
`chave` não existe no schema real) rodado no mesmo universo de 635 papéis. **Resultado: 1 ocorrência no trace
inteiro** — exatamente o caso `15f6ad52…` que a pasta exploratória tinha chamado de "achado mais forte" — em 1
execução, 1 mês, e as mesmas três checagens (`DEGENERADO`, `None`/`null`, dict impresso) não batem nela também.
Abaixo do piso de recorrência que qualquer candidata a memória exige (≥3 execuções e ≥2 meses, `01-racionais.md` §7 Passo 5): fica
documentado como mecanismo confirmado e raro, não vira unidade própria.

**A retratação, por escrito.** A pasta exploratória anterior chamava 2 dos 3 casos que olhou de "confirmado: chega
a `final_answer` errado", e citava o caso do segundo mecanismo como o "achado mais forte" sem contar quantas vezes
ele acontece. Com o universo completo e as três checagens (não uma lista de palavras nova sobre a saída
intermediária do `ConversationAgent`, que era o método da pasta anterior), **nenhuma das 5 ocorrências reais
(4 + 1) bate nenhum sinal de resposta ruim/corrompida que o pipeline já confia**. Segue a mesma regra do `01-racionais.md` §2:
**corrigir** quando o fenômeno é real e só a régua era fraca — aqui os dois mecanismos são reais, agora contados
exaustivamente em vez de 3 casos a dedo —, mas o **dano à resposta entregue**, tal como a pasta anterior afirmou,
não se sustenta e é retirado. Conferência completa em [`03-procedimento-validacao.md`](03-procedimento-validacao.md)
§1.11; evidência reconciliada (mesma pasta, conteúdo substituído) em
`resultados/evidencia/11.10_leituras_get_available_documents/`; código no notebook [`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb), §11.10.

**O que isso muda para a nº2.** `status` continua `derived-and-checked` (não depende desta análise) e `destino`
continua `memória` (o prompt segue incompleto, não contraditório — nada aqui muda essa leitura). O que muda é
`validation.analise_funda`, que sai de `"pendente"` para o resultado acima — e a `description`/`correction_guidance`
ganham um fato a mais, ainda não incorporado ao texto: existe, além dos 91 erros que quebram, um número pequeno mas
real de leituras que não quebram e ainda assim perdem os documentos — argumento a favor de também levar o envelope
`result` não documentado ao time da plataforma (mesma recomendação já feita para a nº10), não só escrever a memória.

---

## Onde ver os números e o código

Este documento explica a lógica; [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.7–§1.11 tem
como cada passo foi rodado, conferido e onde desviou do pré-registro. Código no notebook
[`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb); números em
[`07-relatorio-mineracao-unidades-n2-n10.md`](07-relatorio-mineracao-unidades-n2-n10.md); evidência caso a caso em
`../pipeline/resultados/evidencia/11.*` (git-ignored, com PII).
