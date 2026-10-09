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
