# Racionais — a lógica da análise da base 3, em linguagem simples

> Códigos de unidade (`U_…`, `H_…`, `C_…`, `X_…`) e demais siglas: [glossário](../../glossario.md). Aqui cada código
> aparece junto do nome da lição.

**Para que serve este documento:** explicar *por que* a base 3 é analisada do jeito que é, e o que cada conceito quer
dizer — para reler antes de apresentar ao tutor. Os números estão em [`02-relatorio-achados.md`](02-relatorio-achados.md);
como cada um foi conferido e como reproduzir, em [`03-procedimento-validacao.md`](03-procedimento-validacao.md); o que
falta, em [`04-roadmap.md`](04-roadmap.md). O método é o mesmo das bases 1 e 2 — a genealogia família → assinatura →
mecanismo → unidade → destino, toda por regra fixa, sem LLM no caminho
([metodologia](../../2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md)).

---

## 1 · O que a base 3 é — e por que muda a análise

As bases 1 e 2 chegaram como **trace completo**: cada execução com a memória inteira de cada papel (todos os passos,
com e sem erro, o system prompt, a resposta final). A base 3 é a base atual do projeto, a fonte de verdade, mas chega
de outro jeito: um parquet produzido pela query `ICTI_crossmemory_query_mineracao_erros` no Athena, com **uma linha por
passo com erro** (ActionStep) e, em colunas, uma janela em volta dele — o passo anterior, os dois seguintes, os custos
e um sinal de recuperação. São 31.421 linhas: 30.141 erros estruturados e 1.280 suspeitas.

Isso muda três coisas:

1. **Não há denominador.** Os passos sem erro e as execuções sem erro não estão no arquivo. Dá para contar erros,
   execuções com erro, meses e papéis; não dá para calcular taxa (erros por passo, por execução, por papel).
2. **O contexto é uma janela, não o histórico.** Do passo anterior vêm o código, as observações e o tipo do erro; do
   resto da execução, nada. O system prompt e o modelo não vêm.
3. **Os textos vêm cortados.** A mensagem de erro é cortada em 20.000 caracteres, o código em 12.000, as observações
   em 20.000. Em erros de traceback longo, o final da mensagem — às vezes a parte que diz a causa — some.

Por isso o pipeline da base 3 não é o `carregar_base()` das bases 1 e 2. Ele é o **modo observado**
(`mineracao_observada.py`): reaplica exatamente as mesmas regras de classificação, mas só onde o dado é suficiente
para a regra decidir.

## 2 · As mesmas regras, aplicadas só onde decidem

Cada regra do método precisa de certos insumos. Exemplos:

- reconhecer o sintoma (família e assinatura) precisa da mensagem de erro inteira;
- separar "nome de um passo que falhou" de "nome nunca definido" precisa saber se o passo anterior teve erro;
- "texto longo dentro de literal de string" × "retorno colado de volta no código" precisa do código e do histórico
  de chaves vistas antes.

O modo observado olha, erro a erro, se esses insumos estão na janela. Se estão, aplica a regra de sempre e o erro cai
numa unidade — é um **mecanismo observável**. Se não estão, o erro fica **pendente**, com o motivo escrito
(`mensagem_limitada_ou_ausente`, `predecessor_nao_identificado_sql`…). Nenhuma regra nova foi criada para a base 3, e
as regras foram comparadas por estrutura de código com as da base 2: são iguais (ver o procedimento, §2).

## 3 · Pendente não é resíduo

Nas bases 1 e 2, o erro que nenhuma regra explica vai para o **resíduo** (`X_causa_nao_identificada`,
`X_sintoma_nao_reconhecido`) — é trabalho de taxonomia. Na base 3 existe um terceiro estado, o **pendente**: a regra
existe, mas o dado não chegou. Misturar os dois inflaria o resíduo com erros que a taxonomia já sabe explicar e
esconderia a limitação da extração. Por isso:

- o pendente fica **sem unidade** e aparece na cobertura com o motivo e o custo em tokens;
- o resíduo continua sendo só o que a regra viu e não explicou;
- o alarme de cobertura (resíduo acima de 5% dos erros) é calculado sobre o resíduo, não sobre os pendentes.

## 4 · A triagem: a mesma régua, sobre o que é observável

A triagem é a de sempre: uma unidade vira **candidata a memória** quando aparece em pelo menos 3 execuções e em pelo
menos 2 meses (recorrência), e quando o tipo dela é de lição do agente (factual ou estratégia). Plataforma e infra
vão para **não-memória**; o limite de passos vai para **investigar — crítico**; o resíduo vai para **revisar**. Uma
régua mais estrita (5 execuções, 3 meses) roda junto, para mostrar quais candidatas são limítrofes.

Duas diferenças da base 3:

- **"Candidato observado", não "candidato".** A recorrência é medida só nos erros observáveis. Uma unidade que não
  passa na régua tem **recorrência não demonstrada** — pode existir nos pendentes. O caso mais claro é o
  `U_contrato_dict` (retorno das ferramentas de documento é dict): na base 1, o corte de 20.000 caracteres apaga 81 dos
  96 erros dele; na base 3 sobram 2. Não é ausência do padrão, é a mensagem cortada.
- **Nenhum destino é herdado.** Nas bases 1 e 2 a mineração decidiu, por exemplo, que o `U_campo_inexistente` (campo
  inexistente no retorno) se conserta no harness. Essa decisão vale para a base em que foi tomada. Na base 3 toda
  candidata começa com o destino em aberto, e o destino sai da mineração dela.

## 5 · Execução, ocorrência e componente

- **Execução** = execução + agente (a mesma execução pode ter mais de um agente).
- **Mês** = o mês em que a execução começou (`dat_hor_inio_exeo`), não a partição do lote (`anomesdia`).
- **Componente** = uma sequência de erros seguidos do mesmo papel, ligados pela janela (o anterior de um é o erro de
  trás). É o "episódio" do guia da query e a "cascata" das bases 1 e 2. Como a janela não traz a chamada nem o
  histórico, a componente é **condicional**: um vínculo que a janela não confirma divide o que seria um episódio só.
  Por isso as contagens de ocorrência da base 3 não são contagens exatas de episódios.

## 6 · O que a base 3 não responde (e por quê)

- **Taxas** de erro (por passo, execução, papel, versão): sem denominador.
- **Falhas silenciosas** (a ferramenta devolve erro como texto, sem erro estruturado): a regex de suspeita da query não
  reconhece o padrão; na base 1 ela pega 0 das 119 falhas silenciosas. As 1.280 suspeitas ficam separadas, fora da
  taxonomia.
- **Sucesso da execução** por conteúdo: a resposta final não vem.
- **Protocolo do system prompt** (ferramentas declaradas, modo de resposta): o prompt não vem.

Cada uma dessas lacunas está medida no procedimento (§4) e vira item do pedido da próxima versão da query
([roadmap](04-roadmap.md)).

## 7 · O teto de economia e o teste de compensação da memória

**A pergunta de fundo.** Criar uma memória compensa? Uma lição injetada no contexto **custa tokens em todo passo em que é
injetada**; ela só vale a pena se evitar mais tokens em erro do que custa. Esta seção fixa o enquadramento — **hipótese,
não resultado** — para que o número de hoje sirva de linha de base quando houver uma memória para testar.

**O teto de economia.** É a soma dos tokens dos passos com erro das unidades **candidatas** (as que passaram na régua de
recorrência), por papel e no total: o que se gastou em passos que falharam por um erro que uma lição poderia evitar. Na
rodada `609c…` (fonte v2, contagens do pedido A):

| Pré-destino do erro (§8) | Tokens (mi) | % do gasto total (3.729,3 mi) | Quem resolve |
|---|---:|---:|---|
| Candidatas a memória | 387,0 | **10,4%** | memória (hipótese) |
| Sinal de harness (`try/except NameError`) | 112,0 | 3,0% | prompt/harness |
| Harness / infra (não-memória) | 64,2 | 1,7% | plataforma |
| Resíduo | 21,9 | 0,6% | taxonomia (investigar) |
| Crítico e sem recorrência | 2,5 | 0,1% | — |
| Pendente (falta dado na extração) | 5,1 | 0,1% | — |
| **Todos os erros estruturados** | **592,9** | **15,9%** | |

**Por que é um teto, e não uma previsão** (cada item torna o número real menor):
1. supõe que a memória evita **todos** os erros das candidatas (eficácia de 100%);
2. **não desconta o custo da injeção** da própria memória;
3. candidata é "recorrente o suficiente para minerar", não memória aprovada — algumas terão destino harness;
4. mede o passo que falhou, **não a recuperação** que vem depois (roadmap #15);
5. mistura papéis: a economia real depende de **em quais passos** a memória é injetada.

**O orçamento de injeção** é o teto dividido pelos passos onde a memória entraria — o tamanho máximo que a memória pode ter
para empatar com 100% de eficácia. Com todas as candidatas e injeção em todos os passos do sistema: 387,0 mi ÷ 283.925 passos
= **≈ 1.363 tokens por passo** (10,4% dos 13.135 tokens de um passo médio); uma unidade só, `U_tipo_retorno`: 207,0 mi ÷
283.925 = ≈ 729 tokens por passo. Injetar só nos papéis onde a unidade ocorre **aumenta** o orçamento por passo (o
denominador é o dos passos do papel). Com eficácia *e* menor que 100%, o ponto de equilíbrio é
**tamanho da memória < e × orçamento de injeção**.

**O teste de compensação (quando existir uma memória).** Com a rodada de hoje como **linha de base congelada** (fonte, contagens
e rodada com hash; os números ficam num **registro versionado** em `analysis/registros/`, e não só na pasta de resultados, que está fora
do git e pode ser refeita com outro código — decisão de 15/10, [`decisoes.md`](../../decisoes.md)), mede-se depois da injeção, nos mesmos papéis e unidades: (1) a **economia medida** = tokens em erro da
base − tokens em erro depois; (2) o **custo da injeção** = tokens injetados × passos em que entraram; (3) a memória
**compensa** se economia medida − custo da injeção > 0; (4) a **eficácia** = economia medida ÷ teto. A comparação é por
**taxa e por papel**, nunca por total: o gráfico mensal de custo mostrou que a mistura de papéis muda o custo por execução
sem mudar a eficiência de nenhum deles ([roadmap](04-roadmap.md) #36, gráfico 6; #37).

## 8 · Pré-destino e destino (29/10/2026)

**O problema.** Os gráficos de volume (`destinos`, `unidades_destino_tipo` e a genealogia pelo destino) mostram, para cada
erro, a decisão da triagem da unidade dele: candidata a memória, sinal de harness, harness / infra, crítico, resíduo ou
sem recorrência. Isso é um **encaminhamento antes da investigação**, e a palavra "destino" no título sugere que a
investigação já aconteceu para todas as unidades. Não aconteceu: no kit, só o `U_sandbox` a completou.

**A definição.**
- **Pré-destino** é o que a triagem entrega, por regra: para as unidades candidatas, "memória candidata" com o tipo da lição
  (`UNI[u][1]`: factual · ambiente ou experiencial · estratégia); para as famílias de plataforma, "harness / infra"
  (não-memória, por taxonomia); e "resíduo", "crítico" e "sem recorrência". É provisório.
- **Destino** é só a decisão depois da investigação, do pesquisador, com evidência: memória catalogada (com o degrau),
  harness registrado, monitorada ou em aberto.

**O que o pipeline já faz.** O código não define destino antes da mineração: `destino_mineracao(u)` devolve "em aberto" para
a unidade que não foi minerada nesta base, e a coluna `destino_proposto` da triagem só lê esse registro. O que os gráficos
chamam de destino é a **decisão da triagem**, isto é, o pré-destino. Por isso não há mudança de pipeline: os nomes
(`destino_proposto`, `DESTINO_MINERACAO`, a coluna "destino" da genealogia) ficam como estão, e `base_pipeline.py`,
`mineracao_observada.py` e `genealogia_sankey.py` entram no hash de código da rodada. O rótulo que aparece no gráfico é
escolha de quem apresenta.

**O sinal de harness é híbrido.** A triagem só o emite quando uma mineração anterior já decidiu "harness" para a unidade
nesta base (`_decisao`, em `mineracao_observada.py`). Ele pertence ao pré-destino, mas já carrega uma decisão
pós-investigação. Mantê-lo fora das candidatas tem uma razão funcional: o teto de economia (§7) não conta como memória o
que já se decidiu ser harness.

**O pré-destino é provisório, e a mineração o corrige.** O `U_sandbox` entrou como candidata com 3.653 erros; depois da
mineração, os erros de verificação de existência e de ferramenta não declarada foram para unidades de harness, e a unidade
ficou com 1.401 erros, dividida em partes com destinos diferentes (dossiê do sandbox, §1 e §2d). É o resultado correto da
mineração, não uma falha do pré-destino.

**O estado do destino na base 3, em 29/10/2026** (registro `DESTINO_MINERACAO` e catálogo `registros/memorias.json`):
- **destino decidido nesta base:** o `U_sandbox` (pelo kit, por parte: 13 memórias no degrau 1 e 3 no degrau 2 no
  catálogo) e as duas unidades de harness com evidência própria da base 3, `U_verificacao_existencia` e
  `U_ferramenta_nao_declarada`;
- **decisão de outra base, não herdada** (Ajuste 7): `U_contrato_dict` (memória, base 1) e `U_campo_inexistente` (harness,
  bases 1 e 2). São evidência prévia, não destino desta base;
- **as demais unidades:** só pré-destino.

Como apresentar: os gráficos de volume dizem "pré-destino"; "destino" só se usa para o que passou pela investigação.
