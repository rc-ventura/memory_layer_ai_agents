# Racionais das falhas silenciosas — o balde invisível

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Para que serve este documento:** o mesmo papel do [`01-racionais.md`](01-racionais.md), só para o erro que **não**
vira exceção. Explica **por que** a fonte de erros não pode ser só a exceção, **como** o funil separa os dois baldes e
**o que** cada medida do balde invisível quer dizer. Os números por base estão em
[`14-relatorio-falhas-silenciosas.md`](14-relatorio-falhas-silenciosas.md); o roteiro para repetir numa base nova, em
[`15-procedimento-falhas-silenciosas.md`](15-procedimento-falhas-silenciosas.md). O código é o notebook
[`../pipeline/falhas_silenciosas.ipynb`](../pipeline/falhas_silenciosas.ipynb) e o `drill_down.py silenciosas`, que
chamam as mesmas funções do `base_pipeline.py`. A história, na ordem em que aconteceu, fica no livro-razão
([`../../pipeline-entre-bases.md`](../../pipeline-entre-bases.md), Etapa 10c).

**Por que um conjunto próprio (decisão do Rafael, 22/09; nomes e desenho em 01/10).** É um método diferente do resto do
notebook da esteira — a entrada não é a mensagem de uma exceção, é o texto que a ferramenta devolveu e o código que a
chamou. Roadmap item 26; `../../plano-atual.md` §1.

---

## 1 · O ponto cego

A taxonomia da esteira parte de `ActionStep.error`: só entra o erro que levantou exceção. Isso deixa de fora, por
construção:

- **a falha de ferramenta devolvida como texto.** O wrapper da ferramenta captura a falha e devolve
  `"Error calling tool '<nome>': <motivo>"` como **valor**; o Python segue, o step fica com `error: null`, e para o
  pipeline o step foi "ok". O caso que disparou a medida: no erro crítico da base 2, a calculadora devolveu
  `'DEFAULT'` como resultado, o contrato declarava `dict`, e a falha só aparecia na observação
  ([`11-relatorio-protocolo-harness.md`](11-relatorio-protocolo-harness.md) §2.5);
- **o comportamento errado que não quebra nada** — retorno de ferramenta ignorado, chamada repetida, ferramenta que
  devia ser chamada e não foi. Pelas categorias do TRAIL classificadas por visibilidade a exceção (mapeamento nosso),
  ≥59% dos erros caem em tipos que a exceção não mostra.

Nas duas bases, **~90% das falhas de ferramenta são silenciosas** (93% e 87%). Um método de memória que só lê a exceção
aprende com a menor parte das falhas.

## 2 · O funil e os dois baldes

Um funil de detecção único olha cada step uma vez e o põe num balde só:

| Regra (por step) | Balde |
|---|---|
| tem exceção (`error` não nulo) — inclusive quando a mensagem é `Error calling tool` | **visível** (notebook da esteira) |
| sem exceção, com `Error calling tool '<nome>'` na observação ou no `action_output` | **invisível** (este conjunto) |
| nenhum dos dois | ok |

Sem sobra e sem sobreposição: a §13.1 do notebook confere que nenhum step está nos dois baldes. As falhas de ferramenta
"com exceção" (9 na base 1, 20 na base 2) ficam só no visível.

**Mesmo catálogo, regras de entrada próprias.** Cada balde é classificado à parte. O visível lê a classe e a mensagem
da exceção (família → assinatura → mecanismo). O invisível lê o **motivo** que a ferramenta escreveu (§3) e a **forma**
do código que a chamou (§5). Do mecanismo para baixo, o catálogo é um só — unidade, lição e destino (`UNI`,
`SUB2UNI`) —, e é isso que permite consolidar: a mesma unidade pode ter ocorrências nos dois canais.

**A consolidação junta ocorrências, não totais.** Uma execução pode ter a mesma unidade nos dois baldes; somar
"execuções do visível + execuções do invisível" contaria essa execução duas vezes. Por isso cada balde entrega uma
tabela de ocorrências no mesmo formato (`exec_id`, papel, `idx`, mês, unidade, canal), e a triagem final conta sobre a
união (`consolidacao_unidades.ipynb`, plano 4.2b).

## 3 · O motivo: seis grupos e o dono

`motivo_da_falha()` lê o texto depois de `Error calling tool '<nome>':` e o põe num grupo, por palavras-chave, na ordem
(a primeira que casa decide):

| Grupo | Exemplo de motivo | É falha real? | Dono |
|---|---|---|---|
| `sem_resultado` | "não foram encontrados…", "No text … found" | não — "não encontrei" é a resposta certa | ninguém |
| `fora_da_cobertura` | "Assunto não previsto…", "Coeficiente não encontrado" | não — o pedido está fora do que a ferramenta cobre | negócio |
| `argumento_do_agente` | "necessário passar", "validation error for call", "Query falhou" | sim | o agente — candidato a memória que a taxonomia não vê |
| `plataforma` | "internally hosted model failed", "Failed to fetch", "Wrong credentials", "object has no attribute" | sim | plataforma / ferramenta |
| `json_invalido` | "Expecting property name enclosed in double quotes" | sim | a conferir em cada base (§5) |
| `nao_reconhecido` | o que nenhuma regra pegou | sim (por cautela) | cobertura — escrever regra |

**Regras escritas olhando as duas bases.** As mensagens são escritas pelo dev de cada ferramenta; uma regra escrita
com uma base só vira regra daquela base (Ajuste 7). Cada regra em `MOTIVO_REGRAS` anota a base de origem (`b1`, `b2`).
Uma base nova traz ferramentas novas: o que não casar cai em `nao_reconhecido` e se lê como cobertura, igual ao resíduo
do balde visível.

**Dono = quem precisa mudar para a falha não acontecer.** Não é culpa. O rótulo do grupo é **genérico**: o
`json_invalido` fica "a conferir" mesmo onde já foi conferido, porque em outra base o JSON quebrado pode vir de dentro
da ferramenta (decisão do Rafael, 01/10).

## 4 · O que cada medida pergunta

- **[1] por ferramenta** — onde a falha silenciosa se concentra. Percentual alto com poucas chamadas é indício.
- **[2] o que vem depois** — o 1º erro com exceção do mesmo papel em até 3 steps. Se "(nenhum erro)" domina, a falha
  passa sem rastro no balde visível: a taxonomia nunca a veria por tabela.
- **[3] contrato de retorno precedido** — quanto de `U_tipo_retorno`, `U_contrato_dict` e `U_campo_inexistente` vem logo
  depois de uma falha silenciosa. Pergunta se essas memórias são, na verdade, efeito da plataforma (a ferramenta
  devolveu texto onde o contrato prometia `dict`). Se fossem, a lição estaria no lugar errado.
- **[4] candidato a sucesso falso** — numa falha **real**, o papel entregou `final_answer` — no próprio step da falha
  ou depois, **na mesma chamada do papel** — sem nenhuma chamada sem falha da mesma ferramenta no meio. É **teto**: a
  resposta pode não depender daquele dado. Só a leitura do caso confirma. *Ajuste 11 (02/10):* a regra antiga olhava
  só o 1º final **estritamente depois** e em **qualquer chamada**. Com isso, deixava fora a falha mais direta (a
  ferramenta falha e o mesmo bloco entrega o `final_answer`) e aceitava um final que respondia a outra tarefa. Isso
  violava o próprio "teto" (livro-razão, Ajuste 11).

Três níveis que [4] separa e as métricas de sucesso confundem: o step não teve exceção ≠ a ferramenta funcionou ≠ a
tarefa foi concluída (plano S5).

## 5 · A forma do argumento — e o gesto do `repr_colado`

O grupo diz **o que** a ferramenta reclamou; não diz **quem** causou. Para o `json_invalido`, a pergunta é: o JSON
quebrado foi montado pelo agente ou gerado dentro da ferramenta? `forma_argumento()` responde lendo **só o tipo** de como
o 1º argumento foi passado no código do step:

| Forma | Leitura |
|---|---|
| `json.dumps(...)`, ou a variável que outra ferramenta devolveu | o agente passou o dado certo → o problema vem da ferramenta |
| `str(...)`, dict ou string montados à mão | o agente montou o argumento → é dele |
| … **colado de um retorno impresso** | o agente colou o print de um retorno em vez de passar a variável |

"Colado" usa o mesmo critério do `repr_colado` no `submecanismo()`: ≥2 pares `"chave": "texto"` no literal e ≥2 dessas
chaves já impressas como chave numa observação anterior do mesmo papel.

**O achado (01/10, duas bases).** O `json_invalido` do `busca_obf` é inteiro o gesto colado (base 1: 6/6; base 2:
86/86). O `RoteadorCivel` recebe o dict do `puxa_doc_decisao` e, ao chamar o `busca_obf`, cola o print. É o mesmo gesto
da unidade `U_repr_colado` (Ajuste 2.2) — muda só **onde** ele aparece:

| | Visível (`U_repr_colado`) | Invisível (`json_invalido`) |
|---|---|---|
| O que quebra | a colagem fica com um colchete trocado → `SyntaxError` | a colagem é Python válido dentro de `str()` → aspas simples → o `json.loads` da ferramenta falha |
| Quem via | a taxonomia | ninguém |

O contrato declara `textos_decisoes (str)`: "… em JSON formatado como string". O texto pede JSON; o tipo `(str)` convida
ao `str(...)`. Por isso o destino é duplo: **memória** (a lição do `repr_colado` estendida — use a variável, converta com
`json.dumps`, nunca cole o print nem use `str()`) e **aviso à plataforma** (o passe dict → string JSON entre duas
ferramentas da mesma esteira). A unidade passa a contar os dois canais na consolidação (decisão do Rafael, 01/10;
plano 4.2b).

## 6 · Os detectores de comportamento (migrados da esteira)

A §13.7 do notebook reúne os detectores determinísticos (AST) que moravam no §7 do notebook da esteira até 01/10, com o
mesmo código e os mesmos números. Eles não dependem do texto `Error calling tool`:

1. **Result-Ignore** — retorno de ferramenta atribuído a uma variável que nunca é lida depois. **Robusto** (o número não
   se move ao trocar o inventário nem ao excluir ferramentas de efeito colateral).
2. **RAC** — chamada idêntica repetida na trajetória, em steps sem erro. **Sensível à definição** (varia ~3,7× com o
   inventário e com contar ou não o `final_answer`); o número publicado é o conservador.
3. **Reasoning-action mismatch** — **retirado**: o *thought* é escrito antes do código executar, não há contradição a
   detectar. O número só aparece para registro.
4. **Tool-Skip** — execução chega a `final_answer` sem chamar ferramenta declarada. **Provisório**: depende do
   inventário (deu 14, 8 e 10); inventário por papel é o roadmap item 5.
5. **Ferramentas chamadas × declaradas** — a diferença são funções auxiliares que o próprio agente define.

Inventário: o que o system prompt **declara** (`def nome(...)`), não o que aparece nas chamadas
(`inventario_ferramentas()`, `analysis/base_utils.py`). Testes de robustez:
[`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.6.

## 7 · Limites

- **Só a forma `Error calling tool`.** Ferramentas que devolvem falha com outro texto, e resultados vazios ou errados
  sem mensagem, não entram no balde invisível. Os detectores da §6 cobrem uma parte desse resto, não tudo.
- **Grupos por palavra-chave.** Uma regra pode errar de grupo numa ferramenta nova; o `nao_reconhecido` e a conferência
  nas duas bases são a proteção.
- **A forma lê só o código do step da falha**, por regex, e só o 1º argumento. É contagem de forma, não leitura de caso.
- **[4] é teto — e frouxo.** Candidato a sucesso falso não é sucesso falso confirmado. Na leitura de 6 casos da base 2
  (02/10), nenhum era: em 3, a resposta veio de outra fonte; nos 3 do `json_invalido`, ela **declara a falha**. A
  "falha declarada" é uma terceira categoria que o [4] não separa (plano 4.1c e S5). A fronteira de chamada vem dos `TaskStep`
  do papel; o resto das ferramentas ainda mistura as chamadas (plano S4).
- **A ocorrência do balde invisível é uma falha (uma linha por step × ferramenta), não uma cascata.** Para consolidar
  com o visível (ocorrência = cascata × unidade), a regra precisa ser escolhida na 4.2b. Base 1: 120 falhas em 119
  steps, 100 sequências de steps consecutivos; no `json_invalido`, 6 = 6 (`audit_recompute9`, sonda F).
- **Groundedness da resposta final** (o valor no `final_answer` tem suporte nas observações?) — o erro de maior impacto
  no TRAIL — ainda não é medido aqui ([`02-relatorio-achados.md`](02-relatorio-achados.md) §5).
