Continue a leitura do balde "causa não identificada" do resíduo da base 3 (a que você acabou de entregar em
`leitura_causa/relatorio.md`). Rode tudo da raiz do repositório, com `uv run --no-sync`. Não instale nem atualize pacotes.
**Mesmos limites:** só contagens, nomes de papel, mês, função ou ferramenta e categorias; nada de texto de mensagem,
trecho de código, conteúdo de variável, identificador de execução ou `step_ref`. **Não edite nenhum arquivo do
repositório**; grave o que produzir em `leitura_causa/` (git-ignored). Reaproveite os scripts e os casos lidos que você já
tem; é uma leitura de um leitor só, e as limitações vão no fim.

**1 · Grupo A (os 86 erros de valor que é texto).**
- (a) Para os 79 de `retorno_de_ferramenta`: o nome da ferramenta e a contagem.
- (b) O formato do valor (`com_simbolo_de_moeda`, `decimal_com_ponto`, `decimal_com_virgula`, `outro`) **por ferramenta**:
  cada ferramenta devolve sempre o mesmo formato ou mistura?
- (c) A por mês (jan, mar, jul, ago), por formato e por ferramenta: o formato ou a ferramenta mudou em agosto?
- (d) Classifique os 18 "outra" do passo seguinte em até 5 categorias fechadas que você propuser, com a contagem de cada
  uma.

**2 · Grupo B (a barra invertida, os 44).**
- (a) Por mês (jan a ago): os erros de B no papel ContestacaoCivel (`ontestacaoCivel` no dado) e os ActionSteps do papel
  no mês (as contagens que você já usou), e a taxa de B sobre os ActionSteps do mês.
- (b) A classe da barra (`sequencia_de_escape_digitada`, `regex`, `caminho_de_arquivo`) por mês, julho contra agosto.
- (c) Nos 11 de "sequência de escape digitada", só a **forma** (por exemplo, "\n" literal dentro de aspas simples, ou barra
  no fim da linha seguida de espaço), sem mostrar o texto.

**3 · Grupo C (os 75 `invalid syntax`).** A regra de forma concordou em só 7 de 15, e 45 dos 75 ficaram em "outra". Faça a
leitura aberta que faltou:
- (a) Leia 20 casos da categoria "outra" (escolha pelo `idx` crescente). Para cada um, **uma frase de até 8 palavras** sobre
  o que está errado na linha, sem código nem texto do caso.
- (b) A partir das frases, proponha até 6 categorias fechadas, reclassifique os 45 por regra (script seu) e valide em 10
  outros casos lidos, dizendo a concordância.
- (c) Por categoria, o desfecho do passo seguinte (sem erro, a mesma família, outra família).

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio_continuacao.md` e responda no chat com uma tabela por
pergunta e as limitações (o que não conseguiu ver e por quê). Não decida nada: a decisão é do pesquisador. Não minere de
novo e não toque no `casos.csv`.
