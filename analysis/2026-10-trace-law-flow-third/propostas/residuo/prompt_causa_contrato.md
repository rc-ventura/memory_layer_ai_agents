Você vai levantar, na **base 2** (que tem o trace inteiro e o prompt de sistema; a base 3 não tem prompt), o que falta para
decidir o destino de dois grupos do resíduo da base 3. Rode tudo da raiz do repositório, com `uv run --no-sync`. Não
instale nem atualize pacotes. **Não edite nenhum arquivo do repositório**; grave o que produzir em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/` (git-ignored).
É uma leitura de um leitor só; as limitações vão no fim.

**Limites de saída (valem para o relatório e para a resposta):** só contagens, nomes de papel, de ferramenta e de módulo,
mês, categorias fechadas e hashes. **Nunca** o texto de um prompt, de uma descrição de ferramenta, de uma mensagem ou de um
código; nem identificador de execução. Onde o pedido disser "diga só a categoria", é só a categoria.

**Onde ler.** O trace da base 2 é o `TRACE` do `analysis/2026-09-trace-law-flow-second/pipeline/base_pipeline.py`. Para ler o
prompt por papel, veja como o `_prompt` e o `medir_prompt` de
`analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_limites_interpretador_residuo.py` fazem (`ler_trace`, a
coluna `txt_etap_memo`) e reaproveite. Os nomes de papel podem estar cortados no dado (`ontestacaoCivel`): procure por
`estacaoCivel` e por `CalculoTrabalhista`. Se um papel ou uma ferramenta não existir na base 2, diga isso e siga.

**A base 1 já foi lida (por mim, localmente):** os 3 prompts distintos do CalculoTrabalhista dela têm as ferramentas
`validador_calculo`, `calculadora_de_pedido`, `indice_correcao_monetaria`, `metadados_processo` e
`calculo_horas_extras`; **não têm** `calcular_correcao_monetaria` nem `corrigir_e_salvar`. Se a base 1 também estiver
no ambiente, repita a pergunta 1 nela, para as ferramentas que existirem, e diga se bate com a base 2; senão, só a
base 2. O que decide é a base 2 (ou a 1) ter as ferramentas do grupo A, principalmente a de 43 erros: se uma não existir
em nenhuma das duas, diga qual.

**Contexto já medido na base 3** (rodada `c2e5e8b31f297d21`, só linhas de erro):

- **Grupo A** · 86 erros do papel CalculoTrabalhista em que um valor que é **texto** entra numa conta ou num `round`/formato.
  Em 79 o valor vem do retorno de uma ferramenta; o agente converte o texto no passo seguinte em 68. Erros por ferramenta:
  `calcular_correcao_monetaria` 43 (0 em jan, 2 em mar, 8 em jul, 33 em ago), `calculadora_de_pedido` 7,
  `validador_calculo` 7, `indice_correcao_monetaria` 6 (só em jan), `metadados_processo` 5, `corrigir_e_salvar` 4,
  `calculo_horas_extras` 2, e 1 cada de `envia_excel_para_usuario`, `corrigir_pela_selic_ajustada`,
  `calculo_vale_alimentacao_refeicao`, `gera_boxplot_calculo`. A taxa de erro do grupo em agosto é 3,3 vezes a dos outros
  meses.
- **Grupo B** · 44 erros de barra invertida no código, 40 deles do ContestacaoCivel. O papel só tem ActionSteps a partir de
  junho (196), 8.205 em julho e 22.501 em agosto; a taxa de B é 0,158% em julho e 0,120% em agosto. Das 40: 27 são
  sequência de escape digitada (`\n`), 7 regex (só em agosto) e 6 caminho de arquivo.
- O que a base 1 (local) já mostrou, em **três níveis que não são a mesma coisa**: (1) a **assinatura** das ferramentas é
  `-> object` em todas (stub do framework: não diz que é texto); (2) a **documentação** (`Returns:`) de `validador_calculo`
  e de `calculadora_de_pedido` diz `str`; (3) o **aviso** (uma frase no prompt, fora das definições de ferramenta, do
  tipo "o retorno desta ferramenta é texto, não esqueça") **não existe**: os 3 prompts distintos do papel são o prompt padrão
  do framework (em inglês; a regra 4 fala em geral de "output format unpredictable", sem citar ferramenta) mais as
  definições, sem nenhuma instrução específica do papel. Além disso, a descrição de `calculadora_de_pedido` fala em
  "retornando o valor calculado e o racional" e o seu `Returns:` fala em "texto com a validação do cálculo": confirme se
  essa incoerência existe na base 2.

**Pergunta 1 · O que o agente vê sobre o retorno (grupo A).** São três níveis diferentes; não os misture. No prompt do
CalculoTrabalhista da base 2, para cada uma das 11 ferramentas acima:
- (a) a ferramenta está no prompt? (sim/não)
- **nível 1, a assinatura** (`def nome(...) -> X`): o tipo que ela declara para o retorno (`object`, `str`, `float_ou_int`,
  `dict`, `outro`);
- **nível 2, a documentação** (o `Returns:` da descrição): o tipo (`str`, `float_ou_int`, `dict`, `list`, `nao_declara`,
  `outro`); se diz o formato do valor (`declara_formato` / `nao_declara_formato`, sem dizer qual); e se a descrição do que
  a ferramenta faz e o `Returns:` são coerentes entre si (`coerente` / `incoerente` / `nao_deu_para_ver`);
- **nível 3, o aviso:** existe, **fora das definições de ferramenta**, uma frase que diga ao agente que o retorno das
  ferramentas (ou o desta) é texto, que o formato é imprevisível ou que ele deve converter antes de calcular? Responda
  `aviso_sobre_esta_ferramenta`, `aviso_geral_sobre_retorno` ou `nenhum`, e conte quantos prompts do papel têm cada um.
  Diga também se o prompt tem alguma instrução **específica do papel** além do prompt padrão do framework (sim/não) e se
  a regra geral sobre "formato de saída imprevisível" do framework está lá (sim/não).

**Pergunta 2 · O contrato mudou ao longo do tempo?** Para o CalculoTrabalhista na base 2, por mês: quantos prompts
distintos há (por hash do bloco de descrição das ferramentas, não do prompt inteiro) e, para as ferramentas do grupo A, em
quantos meses a declaração de retorno (`Returns:`) é diferente. Se a base 2 cobrir os mesmos meses da base 3 (jan a ago),
diga quais meses ela cobre.

**Pergunta 3 · A ferramenta devolve sempre a mesma forma? (se a ferramenta existir na base 2)** Para
`calcular_correcao_monetaria`, `calculadora_de_pedido` e `validador_calculo`, por mês: o número de chamadas, o número de
chamadas com erro e a **forma** do retorno nas chamadas bem-sucedidas: `str_com_moeda`, `str_com_ponto`, `str_com_virgula`,
`dict`, `numero`, `outra`. Dentro de um retorno que seja um dict ou um JSON em texto, diga só se **os campos numéricos** têm
a mesma forma entre chamadas (`estavel` / `varia`), sem os nomes dos campos.

**Pergunta 4 · O prompt do ContestacaoCivel induz a barra? (grupo B)** No prompt do ContestacaoCivel da base 2:
- (a) quantos exemplos de código do prompt contêm uma barra invertida dentro de um literal (`\n`, `\t`, regex, caminho), por
  tipo;
- (b) o prompt instrui como escrever texto longo ou com quebras de linha dentro do código (aspas triplas, `\n`, outra
  forma)? `instrui_aspas_triplas` / `instrui_barra_n` / `nao_instrui` / `nao_deu_para_ver`;
- (c) o prompt menciona regex ou cadeias brutas (`r"..."`)? sim/não, e quantos exemplos.

**Conclusão por grupo.** Para o grupo A, uma de: "há aviso (nível 3) e o agente erra mesmo assim (memória de reforço)", "a documentação declara
`str` (nível 2) mas não há aviso (nível 3): a informação existe só como documentação", "a documentação não declara ou é
incoerente com a ferramenta (a documentação induz: harness)", "a ferramenta devolve formas diferentes entre chamadas
(contrato da ferramenta)", ou "inconclusiva", com a contagem que sustenta; diga se o 3,3 vezes de
agosto bate com alguma mudança de prompt ou de forma de retorno. Para o grupo B: "o prompt induz", "o prompt não induz" ou
"inconclusiva". Não decida nada além disso: a decisão é do pesquisador.

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio_contrato.md` e responda no chat com uma tabela por
pergunta e as limitações (o que não conseguiu ver e por quê). Não minere de novo e não toque no `casos.csv`.
