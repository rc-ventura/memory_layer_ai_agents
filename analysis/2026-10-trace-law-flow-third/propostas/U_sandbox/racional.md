# Racional da lição — o inventário do sandbox (`U_sandbox`)

> Códigos e siglas: [glossário](../../../glossario.md). O porquê de cada passo, para toda lição:
> [`07`](../../docs/07-racionais-mineracao-candidatas.md). Os comandos: [`06`](../../docs/06-procedimento-mineracao-candidatas.md).
> Aqui fica só o que é desta lição, na ordem dos passos do `07`.

**Status:** proposta · **Escrito em:** 16/10/2026 · **Hash:** o do commit que traz este arquivo, registrado antes de o
script rodar na base 3 (a ordem do pré-registro).

## A lição

O agente escreve código que o interpretador do sandbox recusa: chama uma função proibida (`repr`, `eval`, `globals`,
`dir`), importa um módulo fora da lista autorizada (`ast`), usa um módulo sem importar (`json`, `datetime`) ou um
módulo que não existe no ambiente (`openpyxl`). É uma lição **factual sobre o ambiente**: o conteúdo da memória é a
lista do que pode e do que não pode.

**A hipótese que o script testa:** a lição sai da própria mensagem de erro. O interpretador escreve o nome do que
recusou e, no import, a lista dos imports autorizados; não é preciso ler o caso.

**De onde veio a regra.** Base 1, pela porta da query (16/10/2026): 17 erros em `U_sandbox`, **17 com nome (100%)**:
`modulo_sem_import` (datetime 3, json 3), `funcao_proibida` (repr 3, globals 2, dir 1, eval 1), `modulo_ausente`
(openpyxl 1), `atributo_dunder` (`__name__` 1), `import_bloqueado` (autojson 1, ast 1). Duas listas de imports
autorizados distintas (uma com `pandas` e `json`, outra sem), o que sugere que a lista depende do papel. Os padrões são
os da regra de classificação do `base_pipeline.py` (a assinatura e a sub-unidade); nada novo.

## Passo 1 · A população, em prosa (para a auditoria)

Na rodada: os erros classificados em `U_sandbox` (sub-unidades `inventario_sandbox` e `modulo_sem_import`), o
`casos.csv` do perfil. Os pendentes não entram.

Na auditoria, sem importar o pipeline: o passo é um erro estruturado (o tipo do erro preenchido) e a mensagem tem
- `Forbidden function evaluation: '<nome>'` com `<nome>` uma função embutida do Python (um nome que não é embutido é
  "nome não definido", outra lição); ou
- `Import of` / `Import from`, `ModuleNotFound` ou `Forbidden` (qualquer outro); ou
- ``The variable `<nome>` is not defined`` com `<nome>` em `json`, `pd`, `np`, `re`, `os`, `math`, `datetime`;

e não tem nenhum dos sinais que o pipeline decide antes (resposta sem bloco de código — `regex pattern`; falha do LLM —
`AgentGenerationError`, `internally hosted`, `Error code: 422`, `UnprocessableEntity`; timeout de ferramenta —
`excedeu o timeout`, `TimeoutError`; sintaxe, `Could not index`, `has no attribute`, `JSONDecode`, argumento
posicional, `object is not an iterator`, limite de passos, tempo do interpretador).

**Emenda 3, de 19/10 (consequência do Ajuste 21, decidido pelo Rafael):** sai também da população a introspecção que
verifica uma variável e guarda a criação dela: a função proibida é `globals`, `locals` ou `vars`; a linha que falhou
verifica um nome — direto (`'x' in globals()`, `'x' not in globals()`, `globals().get('x')`) ou por uma função escrita pelo
agente que recebe o nome entre aspas (`f('x')`) e, na mesma linha, cria `x`; e esse nome recebe, no código do passo ou na
própria linha, o resultado de uma chamada de função que não é `globals`/`locals`/`vars` (`x = ferramenta(...)`). Esses
erros vão para `U_verificacao_existencia` (sinal de harness). Regras do passo 4 e limiares não mudam. A emenda foi
escrita depois da primeira mineração na base 3 e do teste da regra (b) nela (dossiê, foto `IMG_5900`): é descritiva.

**Emenda 2, de 16/10, depois da primeira rodada na base 3** (`observada_e3ebc8274dcf108c`): a lista acima não tinha os
três primeiros sinais (bloco de código, falha do LLM, timeout de ferramenta), que o pipeline decide antes do sandbox
(o timeout desde o Ajuste 4 do livro-razão). Na base 3, **1 erro de 3.653** tinha a função proibida e o timeout de
ferramenta na mesma mensagem: o pipeline o pôs no timeout, e a auditoria, no sandbox. O encontro divergiu só por ele
(`passo7_divergencia.csv`). A emenda corrige a definição da auditoria; a população da mineração (a da rodada), as
regras do passo 4 e os limiares não mudam. Decisão do Rafael.

## Passo 4 · A regra específica: o nome recusado de cada erro

Sobre o último trecho da mensagem (depois do último `due to:`, porque o começo repete a linha de código do agente, que
pode ter as mesmas palavras), na ordem; vale a primeira que casar:

| Tipo | Padrão na mensagem | O nome extraído |
|---|---|---|
| `funcao_proibida` | `Forbidden function evaluation: '<nome>'` | a função |
| `import_bloqueado` | `Import of <módulo> is not allowed` ou `Import from <módulo> is not allowed` | o módulo |
| `modulo_ausente` | `No module named '<módulo>'` | o módulo |
| `atributo_dunder` | `Forbidden access to dunder attribute: <nome>` | o atributo |
| `modulo_sem_import` | ``The variable `<nome>` is not defined`` | o módulo |
| `sem_nome` | nenhuma das anteriores | — |

A mensagem é a do passo com erro, inteira (a v2 não tem corte); com estado não íntegro, conta como `sem_nome`.

**As listas de imports autorizados:** quando a mensagem tem `Authorized imports are: [...]`, os nomes entre os
colchetes, em ordem alfabética, viram uma lista; listas iguais contam como uma.

**Tabelas:** uma linha por erro (`exec_id`, `step_ref`, papel, mês, tipo, nome); o inventário por tipo e nome (erros,
execuções, papéis, meses); nome × papel; nome × mês; cada lista autorizada distinta com os papéis e os meses.

## Passo 5 · A confiança: cobertura ≥ 95%

Erros com nome ÷ erros da população; o `sem_nome` contado pela primeira palavra do trecho. **Abaixo de 95%,** a hipótese
"a lição sai da mensagem" não vale: o arquivo final não é gravado e a lição volta à investigação.

## Passo 6 · Os números para o destino

1. A lista autorizada é uma só, em todos os papéis e meses? (sim → é configuração fixa do ambiente, e cabe perguntar se
   o lugar dela é o prompt do harness)
2. O mesmo nome reaparece na mesma execução e papel depois do primeiro erro? (sim → o agente não aprende sozinho
   dentro da execução)

## Passo 7 · O que o encontro compara

A população, a cobertura, o inventário por tipo e nome e as listas autorizadas.

## Passo 8 · O arquivo final

| Campo | Como é montado | Origem |
|---|---|---|
| `category` | "Inventário do sandbox (factual · ambiente)" | checado |
| `scope` | `role: null` (o sandbox é um ambiente só); com mais de uma lista autorizada, a guidance as separa | checado |
| `location` | até 10 casos, o primeiro de cada papel na ordem (papel, mês, `step_ref`), com `exec_id`, `step_ref`, `fonte_id`, `rodada_id` | checado |
| `evidence` | 3 casos: o primeiro de cada um dos três tipos mais frequentes, com tipo e nome | checado |
| `description` | frase montada das contagens: quantos erros, de que tipos, em quantos papéis | checado |
| `correction_guidance` | montada da tabela, sem texto livre: "Não chame: …; não importe: …; importe antes de usar: …; não existe no ambiente: …; não acesse: …; imports autorizados: …" — todos os nomes vistos, por ordem de erros; com mais de uma lista autorizada, uma por grupo de papéis | checado |
| `occurrences` | erros, ocorrências, execuções e meses do perfil da rodada | checado |
| `status` | `derived-and-checked` se a cobertura passa e o encontro fecha | checado |
| `validation` | cobertura, encontro, listas autorizadas, os números do passo 6; `destino: "em aberto"` até o Rafael decidir | checado / pendente |
| `impact` | `null` | pendente |

**Emenda de 16/10 (depois do primeiro ensaio na base 1, antes de qualquer rodada na base 3).** Duas mudanças na linha
`correction_guidance` do passo 8, nenhuma em regra, limiar ou população:
1. o rótulo "não acesse" (o tipo `atributo_dunder`, que já estava no passo 4);
2. "com mais de uma lista autorizada, uma por grupo de papéis", que repete o que a linha `scope` já dizia.

**A base de confirmação é a base 3.** A regra foi escrita olhando a base 1 (ver "De onde veio a regra"), então o ensaio
na base 1 confere o **código** (o script faz o que o racional diz), não a **hipótese** (a lição sai da mensagem). Quem
confirma a hipótese é a primeira rodada na base 3, depois do commit desta emenda. O hash do pré-registro fica
registrado no funil do procedimento `06`.

**Emenda 4, de 19/10 (decisões do Rafael: a lição dividida e os destinos; `decisoes.md`, 19/10).** O passo 8 monta
**uma memória por parte**, e o encontro (passo 7) compara também os erros de cada parte. A parte de cada erro sai do
tipo e do nome do passo 4: **C** = `modulo_sem_import` (global, destino memória); **E** = `funcao_proibida` ou
`atributo_dunder` (global, destino **em aberto**: em investigação, dossiê §2c); **B** = `import_bloqueado` ou
`modulo_ausente` de uma ferramenta — o framework (`smolagents`, `mcp`, `mcp_client`), os nomes `tools`, `tool_usage`,
`tool_functions`, `python_interpreter`, ou um nome que começa por `get_` (uma memória por papel, destino memória);
**D** = os outros imports (uma memória por papel, destino memória, com a lista autorizada do papel no mês mais recente).
A lista de B foi escrita **olhando a base 3** (rodada `85706f1e`, dossiê §2b): é descritiva, não pré-registrada. Regras
do passo 4, população e limiar não mudam. A memória fechada (destino memória, derived-and-checked) entra no catálogo
`analysis/registros/memorias.json` (Ajuste 22).

**O arquivo final de cada parte (emenda 4, complemento de 19/10, depois da revalidação 4).** Em toda lista de nomes
abaixo, a ordem é **por erros, e no empate a alfabética**. Nenhum texto livre: as frases são moldes fixos.

| Campo | Como é montado na memória da parte |
|---|---|
| `category` | "Inventário do sandbox · <rótulo da parte> (factual · ambiente)", com os rótulos C "módulo usado sem import", B "ferramenta importada como módulo", D "import fora da lista autorizada", E "funções e atributos proibidos" |
| `scope` | `role: null` em C e E; `role: <papel>` em B e D; `tool: null` |
| `location` | os erros da parte; em C e E, o primeiro de cada papel na ordem (papel, mês, `step_ref`), até 10; em B e D (um papel só), os 10 primeiros na ordem (mês, `step_ref`) |
| `evidence` | o primeiro caso (papel, mês, `step_ref`) de cada um dos 3 nomes com mais erros na parte |
| `description` | "<n> erros em <k> papel(éis), parte <P> do inventário do sandbox (<rótulo>): <nome> <erros>, …." (com ponto final, como os moldes da `correction_guidance`; revalidação 5) |
| `correction_guidance` | C: "Importe antes de usar: <nomes>." · B: "As ferramentas já estão no escopo como funções: chame-as direto, sem import. Não importe: <nomes>." (bloqueado e ausente juntos: uma ferramenta não se importa, exista ou não o módulo) · D: "Não importe: <bloqueados>; Não existe no ambiente: <ausentes>; imports autorizados neste papel: <lista>." (a lista do papel no mês mais recente em que aparece; empate entre listas do mesmo mês: a com mais erros, e então a alfabética) · E: "Não chame: <funções>; Não acesse: <atributos>." — cada pedaço só se tiver nome |
| `occurrences` | erros, execuções e meses da parte; `ocorrencias` = erros (a ocorrência condicional é da unidade inteira, no perfil da rodada) |
| `status` | `derived-and-checked` se a cobertura passa e o encontro (com as partes) fecha; senão `parcial` |
| `validation` | a parte (código, rótulo, escopo), cobertura, encontro, as listas autorizadas da parte, os números do passo 6 com os erros que repetem o nome na parte, `destino` (C, B, D: "memória"; E: "em aberto") e onde foi decidido |
| `impact` | `null` |

Estas regras foram escritas depois do ensaio na base 1 e da rodada `85706f1e` da base 3: são descritivas (não mudam
população, regras do passo 4 nem limiar).

**Emenda 5, de 19/10 (consequência do Ajuste 23, decidido pelo Rafael; descritiva, escrita depois dos testes da parte E
na base 3):** a emenda 3 passa a valer também quando a função proibida é `eval` — a linha que falhou verifica um nome
(por uma função escrita pelo agente que recebe o nome entre aspas e, na mesma linha, cria a variável) e o nome recebe o
resultado de uma chamada que não é `globals`/`locals`/`vars`/`eval`. Esses erros vão para `U_verificacao_existencia`.
O `eval(texto)` que converte texto fica na parte E. Regras do passo 4, partes e limiar não mudam.
**Como o código aplica (revalidação 6, para a prosa dizer o mesmo que o código e a auditoria):** (i) "função que recebe
o nome entre aspas" é qualquer chamada `f('x')` na linha com `x` criado na mesma linha, escrita pelo agente ou não; (ii)
com `eval`, valem também as formas diretas da emenda 3 (`'x' in globals()`, `globals().get('x')`), se a linha as tiver;
(iii) a criação por `eval(...)` não conta como "chamada" em nenhum dos casos, nem nos de `globals`/`locals`/`vars`
(criar a variável lendo-a de novo não é chamar uma ferramenta). Na base 1, 0 erros caem nesses pontos; na base 3, a
rodada nova os mostra.

**Emenda 6, de 19/10 (decisão do Rafael, depois da investigação da parte E, dossiê §2c):** o destino da parte **E**
passa de "em aberto" a **memória** (global), e a `correction_guidance` dela ganha, depois de "Não chame: …; Não acesse: ….",
o complemento fixo "Para inspecionar um valor, use print(type(x)) e print(str(x)[:n]); para ler JSON, use json.loads."
(o jeito permitido de fazer o que a depuração e a conversão de texto faziam). Regras, partes e limiar não mudam.

**Emenda 7, de 20/10 (consequência do Ajuste 26, decidido pelo Rafael; descritiva, escrita depois do teste na base 2,
dossiê §2h, foto `IMG_5968`):** sai também da população o import de uma ferramenta que o prompt **cita e não declara**:
no último trecho da mensagem (depois do último `due to:`), o nome de `Import of X is not allowed`, `Import from X is not
allowed` ou `No module named 'X'`, pela raiz antes do primeiro ponto, está na lista do pipeline das ferramentas citadas e
não declaradas — hoje só `get_document_text` (o prompt do OBFCivel a cita e não a declara em 63 de 63 execuções na base 2
e 11 de 11 na base 1). Esses erros vão para `U_ferramenta_nao_declarada` (sinal de harness). A parte **B** fica com os
nomes do framework (`python_interpreter`, `tools`, `tool_usage`, `tool_functions`, `smolagents`, `mcp`, `mcp_client`) e
os outros `get_*`. Regras do passo 4, partes e limiar não mudam. Na base 1, 0 erros caem aqui; na base 3, o esperado é
**167** (todos no OBFCivel): o sandbox 1.401 → 1.234 e a B.OBFCivel 211 → 44.

**Emenda 8, de 20/10 (consequência do Ajuste 27, decidido pelo Rafael; descritiva, escrita depois da medição na base 3,
dossiê §2h, 7–8, fotos `IMG_5976`–`IMG_5978`):** sai também da população, **no papel cujo prompt manda verificar se a
variável existe** (a lista do pipeline; hoje só o ContestacaoCivel, que chega ao trace como `ontestacaoCivel`), toda
verificação de existência com a função proibida `globals`, `locals` ou `vars`: a linha que falhou tem `in globals()` /
`in locals()` / `in vars()` ou `globals().get(` (e o mesmo com `locals`/`vars`), crie a variável ou não, com nome entre
aspas ou não. Esses erros vão para `U_verificacao_existencia`. Nos outros papéis vale só a emenda 3 (verifica e cria por
uma chamada). `dir` e `eval` não entram aqui (o `eval` segue a emenda 5). Regras do passo 4, partes e limiar não mudam. Na
base 1, 0 erros caem aqui (o único do papel já sai pela emenda 3); na base 3, o esperado é **135** (jul–ago/26; `globals`
125, `locals` 10), parte no sandbox e parte hoje pendente por código cortado — o sandbox somado aos pendentes de
verificação cai 135.

**Emenda 9, de 20/10 (decisões do Rafael no fechamento do sandbox, `decisoes.md` 20/10: 1, 4, 5 e 6; o degrau 2 da
validação, dossiê §2g–§2h).** O passo 8 muda nas partes C, B e E, ganha a parte **F**, e toda parte grava
`validation.nomes` (esquema 0.4). Moldes fixos, ordem por erros e no empate a alfabética, como na emenda 4.
- **C se divide.** O módulo de um `modulo_sem_import` é o nome lido, com os apelidos `pd` → `pandas` e `np` → `numpy`.
  **C** (global) fica com os módulos que estão em **todas** as listas autorizadas distintas da população (a tabela
  `imports_autorizados`); sem nenhuma lista vista, todos ficam em C. Os outros vão para **Cp** (rótulo "módulo usado sem
  import, por papel"; uma memória por papel, id `U_sandbox.C.<papel>`, destino memória). Molde do import: `import <m>`,
  e com apelido `import <m> as <apelido>`. C: "Importe antes de usar: <imports>." Cp: "Importe antes de usar: <imports>."
  com os módulos que estão na lista do papel (a do mês mais recente, como em D) ou quando o papel não tem lista vista;
  e "Não está na lista autorizada deste papel: <módulos>." com os que a lista vista do papel não tem — cada pedaço só se
  tiver nome, separados por "; ".
- **B, o texto:** "As ferramentas são só as funções declaradas no prompt: chame-as direto, sem import. Não importe:
  <nomes>." e, se a parte tem nomes do framework (`smolagents`, `mcp`, `mcp_client`, `tools`, `tool_usage`,
  `tool_functions`, `python_interpreter`, pela raiz), " <esses nomes>: são do framework, e o seu código já roda no
  interpretador." (decisão 4: o `python_interpreter` vem do framework; não se afirma mais que a ferramenta existe).
- **E perde quatro nomes:** `funcao_proibida` com `globals`, `locals`, `vars` ou `eval` vai para a parte **F**
  (rótulo "introspecção fora da verificação instruída"; global; destino **em aberto** — a memória "como verificar no
  sandbox", `b3 #51`); molde: "Não chame: <funções>.". E fica com as outras funções proibidas e os atributos dunder,
  com o molde da emenda 6 (decisão 5: o "não chame `globals`" brigava com o prompt do ContestacaoCivel). O complemento
  fixo da emenda 6 perde "; para ler JSON, use json.loads" e fica "Para inspecionar um valor, use print(type(x)) e
  print(str(x)[:n])." (decisão do Rafael, 20/10, depois do degrau 2 no ensaio da base 1: o `json` não está na lista
  autorizada de quatro papéis no prompt da base 1 — OBFCivel, RoteadorCivel, managerAgent, ContestacaoCivel — e a E é
  global; a frase servia ao `eval(texto)`, que foi para F, e a ≈ 5 `__import__('json')` do ContestacaoCivel).
- **`validation.nomes`** (decisão 6): C e Cp — `importar` os módulos que o texto manda importar, `nao_importar` os que
  não estão na lista do papel; B e D — `nao_importar` os nomes (B pela raiz); E — `nao_usar` as funções e os atributos,
  `usar` `print`, `type`, `str` (o complemento fixo); F — `nao_usar` as funções. As listas que não se
  aplicam ficam vazias.
- **`destino_decidido_em`:** onde cada destino foi decidido (`decisoes.md`, com a data e a decisão).
População, regras do passo 4 e limiar não mudam. Os números de cada parte saem da rodada nova da base 3; o encontro
(passo 7) compara as partes novas com a auditoria, que divide C e E pela mesma prosa.

## O que não mede

- Se o agente se recuperou depois do erro (é o "depois" da parte genérica).
- Se a memória reduz os erros: é o teste de compensação (`b3 #39`), depois de haver memória.
- O que não gerou erro: a lista autorizada só aparece nos erros de import.
