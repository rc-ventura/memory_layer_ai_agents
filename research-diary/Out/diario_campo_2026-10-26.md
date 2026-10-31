# Diário de Campo — Rafael Coelho Ventura

## Semana de 26/10 a 30/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 26/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Ida à máquina das bases 2 e 3 (fotos `IMG_6036`–`IMG_6058`) para o degrau 2 (conferida) das três memórias do sandbox que vão para o agente:
- **C** — "importe antes de usar: `import json`, `import re`, `import datetime`" (global; 423 erros);
- **C.JoogleAnalytics** — "importe antes de usar: `import pandas as pd`" (só nesse papel; 231 erros);
- **E** — "não chame `repr`, `dir`, `exec`…; não acesse `__name__`…; para inspecionar um valor, use `print(type(x))` e `print(str(x)[:n])`" (global; 317 erros).

Até aqui o degrau 2 delas só tinha rodado com o prompt da base 1, que é de outro período, e confiando na lista de módulos do prompt, que não é a lista do interpretador. Testamos seis hipóteses (dossiê do sandbox §2h, 27):

| # | Hipótese | Resultado | Conclusão |
|---|---|---|---|
| H1 | Com o prompt da base 2 (o mesmo período da base 3) e o ambiente lido do interpretador, as três continuam aprovadas | passam em ambiente, conflito, repetição e recorrência (66 versões de prompt, 18 papéis) | comprovada |
| H2 | O interpretador aceita o que o prompt não lista | o `json` rodou sem erro em 10 papéis, inclusive RoteadorCivel e ContestacaoCivel, cujo prompt não cita `json` | comprovada |
| H3 | No managerAgent o `json` é barrado | a base 3 não tem a lista desse papel e tem 0 erros de `json` nele; a única evidência é a base 1, onde a lista é a padrão do smolagents, sem `json` | sem dado na base 3 |
| H4 | O erro da C é esquecer o import, e não o nome sumir entre passos | 0 de 415 (`json`), 0 de 5 (`re`), 0 de 3 (`datetime`) tinham importado no passo anterior | comprovada (limite: a base 3 só guarda o passo anterior) |
| H5 | O mesmo para o `pandas` no JoogleAnalytics | 0 de 231 importados antes; **mas em 177 de 231 (77%) o passo seguinte importa e dá outro erro** | comprovada para o primeiro erro; o erro seguinte fica para o degrau 3 |
| H6 | A E cobre uma causa só: inspecionar um valor | `__name__` 182, `repr` 98, `dir` 9 e atributos 3 = 292 (92%) de inspeção; `exec`, `__import__`, `bytes`, `open`, `hash` = 25 (8%) de outros usos | comprovada na maior parte |

As amostras de 30 casos por memória para o degrau 3 ficaram prontas na máquina (`drill_down.py tabela` e `montar_evidencia.py --regra semente --n 30`; 30 de 30 crus conferidos nas três).

**Reflexão:**
- O bilhete da C é um **lembrete** ("importe antes de usar"), não reforço do prompt. Ter o `json` na lista do prompt diz que pode, não que tem de importar antes.
- Em três papéis o prompt omite o `json` e o interpretador aceita. Ali o bilhete também diz uma verdade que o prompt esconde.
- O que decide se o bilhete é certo num papel é o interpretador aceitar o módulo, não a lista do prompt.

**Decisão/próximo passo:**
- **A C não vale no managerAgent** (decisão 1). Ali a evidência (base 1) é de um interpretador sem `json`, e na base 3 a C não tem erro nesse papel, então excluir não perde nada que se veja.
- Para registrar isso havia dois jeitos: um campo no esquema da memória ou uma marcação no catálogo. O esquema entra no hash do código da rodada e exigiria rodada nova. **Escolhi o catálogo** (`catalogar_memoria.py --excluir`, campo `nao_vale_em`, Ajuste 30).
- **"Uma causa só" passa nas três** (decisões 2 a 4), por decisão minha com a evidência gravada em `decisoes_degrau2.json`:
  - a C passa sem nota;
  - a C.JoogleAnalytics passa com a nota de que o degrau 3 tem de ver qual é o erro seguinte;
  - a E passa com a nota de que os 8% de outros usos também são funções barradas, para as quais o "não chame" continua certo.
- Com isso, as três completam o degrau 2, gravado no catálogo (`--registrar`).
- **O degrau 3 sem esperar a cota de IA da máquina**, que só voltaria em 30/10:
  - (1) regras contadas sobre a população inteira de cada memória, que só imprimem números e categorias;
  - (2) 10 casos por memória, mascarados e trazidos por foto. No mascaramento, todo texto entre aspas, comentário e número vira `<texto>`, `# <comentário>` e `<n>`. Só saem o código e as mensagens de erro, sem a saída do modelo nem as observações, e a saída passa pelo varredor de dado pessoal antes de ser impressa;
  - (3) os dois leitores automáticos na máquina, quando houver cota.
- Um agente (sem provider definido) escreveu o script (`pipeline/validacao/degrau3_sandbox.py`). O teste na base 1, no formato da base 3, pegou dois defeitos antes de qualquer coisa sair:
  - a instrução que falhou pode ter várias linhas;
  - um texto entre aspas triplas que abre e não fecha no trecho deixava passar o conteúdo (apareceram uma tabela em markdown e um código de documento).
- Os dois defeitos foram corrigidos. Como proteção a mais, toda linha que ainda pareça texto corrido é omitida.

**Tags:** base-3, base-2, sandbox, degrau-2, degrau-3, memoria-global, nao-vale-em, ajuste-30, managerAgent, json, pandas, uma-causa-so, sigilo, mascaramento, sub-2.2, sub-2.5

### 26/10/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 / 3.6 — **Canal:** pessoal

**Registro objetivo:** Ajustes nas figuras da base 3, depois de ver o painel e o relatório na máquina 2 por foto (`IMG_6063`–`IMG_6066`).

1. **A genealogia virou duas figuras.** A genealogia de cinco colunas juntava duas análises diferentes:
   - **o censo do sintoma** (família → assinatura), que é uma árvore e virou barras;
   - **a genealogia da decisão** (assinatura → mecanismo → unidade → destino), um Sankey com recorte por unidade.

   No recorte de uma unidade há um destino só, então a cor do destino deixava tudo de uma cor. A figura passou a ser pintada pela **família do erro**, a mesma cor do censo, e o destino ficou escrito na última coluna. No `U_sandbox` da base 1, os 16 erros são todos da família "Ambiente & sandbox".

   Depois pedi também a figura inteira pintada pelo **destino**, numa figura separada (`genealogia_decisao.png` e `genealogia_decisao_destino.png`). Cada figura tem uma variável só na cor. As duas paletas reusam o azul e o laranja com sentidos diferentes, por isso nunca aparecem na mesma figura.
2. **A cobertura das regras virou duas barras.** A figura de um motivo por barra confundia: eram nove barras, a maior com 87%. Agora há só cobertos (a regra tem evidência para decidir: 29.392 de 30.141, 97,5%) e pendentes (falta dado na extração: 749). Os maiores motivos dos pendentes ficam em texto embaixo, e a lista inteira continua na tabela do painel.
3. **A recuperação da população ficou só com os papéis com erro.** A barra das execuções repetia o funil (28,4% de 71.881 execuções tiveram erro) e saiu; o número foi para o título. O limite de passos era preto e se confundia com o verde-escuro de "um erro"; passou a vermelho, da família de "terminou no erro".
4. **O estudo de caso do sandbox ganhou figuras:** dos 3.653 erros de 16/10 aos 1.100 de agora, degrau por degrau, e os 1.100 por grupo de memória (rosca e barras). Saem lidas do catálogo, e o script confere que os grupos fecham em 1.100.
5. **O fluxo de branches e PRs foi para o `AGENTS.md`**, para o Copilot da máquina 2 ler também:
   - sincronizar por merge, nunca por rebase, depois que a branch está no `origin`;
   - PR empilhada contra a branch de base;
   - PR mergeada não recebe mais nada.

   Ali ficou também a regra do hash do código da rodada da base 3: o que não mexer para a rodada atual continuar valendo.

**Reflexão:** As figuras saem lidas da rodada ou do catálogo, sem rodada nova. O que muda é a leitura, não os números. Ler "seguiu sem erro até o fim" como "entregou a resposta final" continua sendo uma leitura que não vale.

**Tags:** base-3, genealogia, censo, sankey, painel, cobertura, recuperacao, limite-de-passos, figuras, estudo-de-caso, sandbox, agents-md, fluxo-de-pr, hash-da-rodada, sub-2.2, sub-3.6, transversal

## 27/10/2026

**Tipo:** observação livre — **Sub-atividade:** transversal — **Canal:** pessoal

**Registro objetivo:** Dia de organização.
- **Diário de campo de 20/10 a 23/10:** o kit de mineração, os quatro degraus de validação, o sandbox dividido em partes A a E e os destinos decididos.
- **A lista de decisões por data (`decisoes.md`) voltou à ordem cronológica.** Sete entradas estavam no fim do arquivo, fora da seção da data delas (cinco de 20/10, uma de 16/10 e as duas de 23/10), e foram para o fim da seção certa. As decisões revistas ganharam marca de revisão: a (8) de 21/10, revista em 22/10; o degrau 3 de 22/10, revisto em 26/10; a barra das execuções da recuperação, que saiu em 26/10. A cor da genealogia era de 26/10, não de 23/10, e virou entrada própria.
- **A regra de conflito no `decisoes.md`, no `AGENTS.md`, estava errada.** Dizia "mais recente em cima", mas a regra do arquivo é "no fim da seção da data".
- A PR da recuperação e da genealogia (#41) foi para o `main`.

**Tags:** diario-de-campo, decisoes, ordem-cronologica, agents-md, organizacao, transversal

## 28/10/2026

**Tipo:** implementação — **Sub-atividade:** 3.6 / 2.5 — **Canal:** pessoal

**Registro objetivo:**
- **Nova figura de taxa por papel na base 3, `papel_volume_execucao`.** É o mesmo desenho da figura por passo (`papel_volume`), mas conta **execuções**: à direita ficam os papéis que rodam em mais execuções; acima, os que têm pelo menos um erro estruturado em mais delas. A pergunta é "em quantas das vezes que o papel rodou houve erro". A tabela de agregação do papel ganhou a coluna `execucoes_com_erro`, com teste.
- **Síntese mensal de outubro**, semanas 1 a 3.
- **Abri o `b3 #58`, uma suspeita de viés de seleção na base 3.** A query `ICTI_crossmemory_query_mineracao_erros` tem um filtro de tamanho que soma o comprimento de três textos da execução. No SQL, `length(NULL)` é nulo e a soma inteira vira nula, então a execução com um desses textos ausente (por exemplo, sem resposta final gravada) não passa no filtro e sai da base.
- **O que a v2 da extração resolveu e o que não:** ela tirou o corte de 20.000 caracteres da mensagem de erro (1.009 erros afetados), mas **não mudou quais execuções entram**. São as mesmas 31.421 linhas e as mesmas 20.986 chaves da v1. São dois limites diferentes, e só o primeiro acabou.

**Reflexão:**
- O #58 é hipótese, não fato. A evidência é indireta:
  - o comportamento do SQL com nulo;
  - o teste na base 1 (`validacao/porta_query_v1.py`): se o texto vazio virasse nulo, sobrariam 100 de 1.000 execuções;
  - na base 3, 20.971 de 20.986 execuções com erro (99,9%) têm resposta final gravada, contra 34 de 318 (10,7%) na base 1.
- Sem a tabela de origem (e sem acesso ao Athena) não dá para fechar.
- Se for verdade, a base 3 sub-representa as execuções que não terminam. As contagens do pedido A foram pedidas "com o mesmo recorte", então o viés valeria também para o denominador das taxas.

**Tags:** base-3, taxa-por-papel, taxa-por-execucao, execucoes-com-erro, figuras-taxas, vies-de-selecao, query, filtro-de-tamanho, extracao-v2, sintese-mensal, sub-3.6, sub-2.5

## 29/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.6 — **Canal:** pessoal

**Registro objetivo:** Duas decisões de vocabulário, enquanto montava os slides da apresentação ao tutor:
1. **Pré-destino × destino.** Pré-destino é o que a triagem entrega antes da investigação: candidata a memória (com o tipo da lição), harness/infra, resíduo, crítico, sem recorrência. Destino é só a decisão depois da investigação, minha, com evidência. Os gráficos de volume (`destinos`, `unidades_destino_tipo` e a genealogia pelo destino) mostram pré-destino; o rótulo é de quem apresenta, e o arquivo e o código não mudam. O pipeline não muda: o destino já fica "em aberto" até a mineração, e os arquivos do pipeline estão no hash da rodada. Ficou no glossário (§9), nos racionais da base 3 (§8) e em `decisoes.md`.
2. **Os nomes dos degraus nos slides: minerada, conferida, revisada, validada.** "Memória candidata" fica só como saída da triagem. Antes, "candidata" servia para duas coisas: a unidade que passa na triagem e o degrau 1. Os documentos ainda dizem "candidata" no degrau 1; a troca vale para os slides.

Também registrei o #58 no roadmap (o que a v2 resolveu e o que não, a evidência, o que fica exposto, como fechar e a ressalva enquanto isso) e documentei no `README.md` a geração do relatório mensal pela skill.

**Reflexão:** Chamar de "destino" o que a triagem entrega fazia parecer decidido o que ainda é hipótese. Na base 3, em 29/10, só há destino decidido para o sandbox e para duas unidades de harness com evidência própria. As decisões das bases 1 e 2 são evidência prévia, não herdada (Ajuste 7).

**Tags:** pre-destino, destino, triagem, degraus, minerada, conferida, revisada, validada, terminologia, slides, base-3, relatorio-mensal, sub-2.2, sub-2.6

## 30/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.6 — **Canal:** pessoal

**Registro objetivo:**
- **Diagramas da apresentação ao tutor, em draw.io** (fonte e imagem em `docs/sources/`): anatomia do trace; o erro estruturado; como o erro é descrito; por que classificar o erro; como os erros viram lição; o degrau 4; o mapa geral da investigação.
- **Duas decisões de método e vocabulário:**
  1. **A quinta checagem do degrau 2 ("uma causa só") é decisão do pesquisador, confirmada no degrau 3.** Nenhum script de mineração grava o campo `causas`, então a checagem sai "não verificável" e eu decido com a evidência registrada. Fazer o script que minera gravar as causas seria circular: a checagem só confirmaria que ele concorda consigo mesmo. A confirmação independente é a leitura do degrau 3, que registra causa e lição por caso. Quando a checagem for automatizada, as causas serão registradas na granularidade da lição da memória: causas com a mesma lição levam o mesmo rótulo e não reprovam. Assim o `conferir_memorias.py`, que falha com mais de uma causa distinta, passa a concordar com o doc 17, que define a falha por lições diferentes (roadmap `#59`).
  2. **"Lição" é o termo, nos dois níveis.** A lição é o que o agente deveria fazer diferente: um fato a lembrar ou um hábito a mudar.
     - A **lição da unidade** é a ideia geral proposta na classificação, uma por unidade, ainda hipótese.
     - A **lição da memória** é a instrução específica de uma parte, com escopo e destino (o `correction_guidance`). Uma unidade pode gerar várias.

     A quinta checagem passa a ser "é uma lição só?". Nada muda no código nem no esquema (glossário §10).

**Tags:** apresentacao, drawio, diagramas, degrau-2, degrau-3, uma-causa-so, licao, terminologia, b3-59, sub-2.2, sub-2.6

### 30/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Rodei na máquina 2 o degrau 3 sem cota de IA para as três memórias que vão para o agente: as regras contadas na população inteira e os 10 primeiros casos da amostra de cada uma, mascarados e trazidos por foto (`IMG_6115`–`IMG_6138`). As populações bateram (423, 231 e 317 erros), o varredor saiu limpo e nada foi bloqueado. A leitura dos 30 casos foi feita por um agente (sem provider definido), não por mim.

*As regras na população:*

| Memória | O passo seguinte | O erro depois do import (ou onde está a chamada) |
|---|---|---|
| C (423) | importa e segue sem erro 333; importa e erra 61; não importa e segue 22; não importa e erra 7 | ferramenta chamada com argumento posicional 33; `JSONDecodeError` 25; outros 3 |
| C.JoogleAnalytics (231) | importa e erra 177; importa e segue 54 | **`json` não definido 99**; argumento posicional 53; `JSONDecodeError` 12; "o objeto JSON deve ser texto, não módulo" 7; outros 6 |
| E (317) | — | **dentro de `print(...)` 222 (70%)**; numa atribuição 28; numa condição 23; outra 44 |

*Os 10 casos de cada uma:*
- **C:** 10 de 10 esqueceram o import; o nome é usado direto na instrução e nenhum passo anterior importou. São `json` 9 (5 no RoteadorCivel, dentro de `json.dumps(...)` passado a uma ferramenta; 3 no JoogleAnalytics, com o `pandas` já importado; 1 no CadastroTrabalhista) e `re` 1 (OBFCivel). No passo seguinte, 7 importam e seguem sem erro, 2 esbarram no argumento posicional e 1 reescreve a chamada sem `json`.
- **E:** 10 de 10 inspecionam um valor, com `type(x).__name__` 5 e `repr(x)` 5. São 7 no ContestacaoCivel, 2 no OBFCivel e 1 no AgenteEstruturador. Os 10 se corrigem sozinhos no passo seguinte: tiram a chamada ou a trocam por `str` ou `isinstance`.
- **C.JoogleAnalytics:** a mesma linha nos 10 casos, `pd.DataFrame(json.loads(run_query(...)))`, sem importar **nem `pandas` nem `json`**. O erro é o do `pd` porque ele vem primeiro na linha. No passo seguinte, 5 importam só o `pandas` e caem no `json` não definido; 3 importam os dois e esbarram no argumento posicional (os três usam `run_query(query)`); 2 importam os dois e seguem sem erro (os dois usam `run_query(query=...)`).

*A contagem que fechou a dúvida* (fotos `IMG_6139`–`IMG_6141`): pedi uma regra a mais, os outros nomes do inventário usados na instrução que falhou. Na C.JoogleAnalytics, o `json` está na linha em **231 de 231** erros: sem import no passo nem no anterior em 225, importado antes em 6.

**Reflexão:**
- As três causas se confirmam. O erro que vem depois do import é quase todo de **outra lição**, a ferramenta chamada com argumento posicional (`U_arg_nomeado`); não é falha do bilhete.
- **O achado da semana:** no JoogleAnalytics o agente esquece **dois** imports na mesma linha. Isso explica os 77% da H5: o maior grupo depois do import (99) é o segundo import esquecido.
- O 225 é teto e o 99 é piso. A base 3 só guarda o passo anterior, e um import mais antigo pode continuar valendo. A própria C mostra isso: 100 linhas usam `pd` sem import no passo nem no anterior, e mesmo assim o erro foi o `json`.
- Limites da leitura:
  - 10 casos por memória, um leitor só, código mascarado;
  - a regra de onde está a chamada da E põe em "outra" as chamadas dentro de um `try`, porque o interpretador aponta a linha do `try:` (3 dos 10 casos);
  - os 7 "não módulo" não apareceram nos casos.

**Decisão/próximo passo:**
- O bilhete "import pandas as pd" corrige só o primeiro dos dois erros; o segundo é o da C, que vale no papel. Havia duas escolhas: (a) pôr os dois imports no bilhete, o que pediria mudar o script da mineração e minerar de novo para repetir o que a C já diz; (b) deixar o texto e escrever a dependência. **Escolhi (b).**
- O `catalogar_memoria.py` ganhou `--junto-com` (Ajuste 31, kit 0.14.0), que grava `vale_junto_com` na entrada da C.JoogleAnalytics. O catálogo avisa (`ALARME`) se a C deixar de chegar ao JoogleAnalytics: se for excluída do papel, ficar monitorada ou sumir do catálogo.

**Tags:** base-3, sandbox, degrau-3, json, pandas, joogleanalytics, dois-imports, vale-junto-com, ajuste-31, catalogo, argumento-posicional, inspecao, mascaramento, sub-2.2, sub-2.5

## 31/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Reabri e fechei a parte F do sandbox, que tinha ficado para depois em 21/10 ("volta quando a maior parte das memórias estiver no degrau 3"). A F é o que sobrou no sandbox de `globals`, `eval`, `locals` e `vars` depois dos Ajustes 21 e 27: 37 erros (`globals` 18, `eval` 14, `locals` 4, `vars` 1), com destino em aberto. O texto que o script montava era só "Não chame: …". Rodei na máquina 2 a contagem e 10 casos mascarados (fotos `IMG_6142`–`IMG_6151`); a leitura dos casos foi feita por um agente (sem provider definido).

*A contagem:*
- **Por nome e uso:**
  - `eval`: `eval(...)` 9, o nome não aparece na instrução 5;
  - `globals`: o nome não aparece (função auxiliar?) 7, outro uso 6, verificação de existência (`in`) 3, leitura com valor padrão (`.get`) 2;
  - `locals`: verificação de existência 4;
  - `vars`: outro uso 1.
- **Por papel:** ContestacaoCivel 25. Fora dele, 12 erros em 9 papéis: as 9 verificações já anotadas no `#54` e mais 3.
- **Passo seguinte:** sem erro 26 de 37.

*Os 10 casos:*

| Leitura | Casos |
|---|---|
| Verificação de existência: `"x" in globals()`, `"x" in locals()`, listar quais nomes existem, uma função auxiliar que olha `globals()`, `eval` do nome com `except NameError` | 5 |
| Cria se não existe (`globals().setdefault(...)`) | 1 |
| `eval` de um texto, para ler o texto como dado | 1 |
| Não dá para ver para quê (`g = globals()`, `globals_dict = globals()`, `locals` dentro de uma lista) | 3 |

Também tirei do repositório o esqueleto e os scripts que geravam a apresentação (`apresentacao-esqueleto.md`, `gerar_apresentacao.py`, `comparar_apresentacao.py`; cerca de 2.000 linhas) e o `python-pptx`. Nada mais os citava, e não havia testes. O painel "erros por mês × taxa por passo", que só esse gerador desenhava, virou figura própria (`execucao/figura_erros_mes.py`), fora do hash do código da rodada. Ela lê as taxas só se o hash bater com o manifesto.

**Reflexão:**
- A F é, na maior parte, a mesma lição do `#51`: verificar se uma variável existe com um nome que o sandbox barra.
- A regra de uso não separa o `eval` de um nome (para verificar) do `eval` de um texto. Quantos dos 14 são de texto ela não diz; nos casos lidos, foi 1 em 10.
- Os 25 do ContestacaoCivel estão no papel cujo prompt manda verificar. Nos casos lidos, a forma é a da instrução, escrita de jeitos que a regra do Ajuste 21 não reconhece. É hipótese, não verificada na população, que sejam o mesmo sinal de harness da verificação de existência.
- **O contraste com o prompt**, a minha pergunta do dia. Uma memória do `#51` ("use `try/except Exception` ou `x = None` e depois `if x is None`; nunca `globals()` nem `except NameError`"):
  - não contrasta com a versão antiga do prompt do ContestacaoCivel (jun–ago), que manda verificar sem dizer como: ali ela completa o prompt;
  - **contrasta com a versão nova** (só agosto), que manda usar `try/except NameError`, o jeito que o sandbox não captura. Na base 2, 97 de 97 erros com o prompt novo; na base 3, os 5.762 erros desse padrão.
- Ali o conserto é no prompt, e a checagem de conflito do degrau 2 reprovaria a memória, como reprovou a E com o `globals`. Nos outros papéis o prompt não manda verificar, então não há contraste.

**Decisão/próximo passo:**
- **A F vai inteira para o `#51`** ("como verificar se uma variável existe, no sandbox"), sem regra nem rodada nova. No `#51`, a parte do ContestacaoCivel deve sair como harness, e a memória vale para os papéis sem a instrução. Na F são 12 erros, que ainda precisam passar na régua de recorrência.
- Recusei:
  - dividir a F agora: os 25 do ContestacaoCivel iriam para harness, o que pediria um ajuste de regra e rodada nova para uma decisão que o `#51` toma com a unidade inteira;
  - manter a F como "Não chame: …": contrasta com o prompt e não diz como verificar.
- **Os dois leitores ficam na máquina, na segunda (02/11), quando a cota volta.** Ler daqui perderia a saída do modelo e as observações, que ficam na máquina pela regra de sigilo. Para estas três memórias a perda seria pequena, porque a causa aparece no código, mas o caso inteiro é o certo para o degrau 3.
- O roteiro está em `propostas/U_sandbox/degrau3_leitores.md`: as hipóteses escritas antes de ler, a lista de categorias a aprovar (`causa`, `tambem_json`, `conserto`, `licao_livre`), a leitura fechada direto (a lição já está fixada nos degraus 1 e 2), os textos para o Copilot (o segundo leitor num chat novo, às cegas) e os comandos de concordância.
- Depois disso, falta gravar o degrau 3 no catálogo (ainda sem comando), e o sandbox fecha.

**Tags:** base-3, sandbox, parte-f, globals, eval, locals, verificacao-existencia, contestacaocivel, conflito-com-prompt, harness, b3-51, degrau-3, leitores, sigilo, apresentacao, figura-erros-mes, sub-2.2, sub-2.5
