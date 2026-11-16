Você vai **ler os 75 erros `invalid syntax`** do balde "causa não identificada" do resíduo da base 3 e entregar medidas por
script, uma categoria fechada por caso e, se a hipótese principal se confirmar, uma regra proposta e contada. Rode tudo da
raiz do repositório, com `uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo do
repositório**; grave o que produzir em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/` (git-ignored).
É uma leitura de um leitor só; as limitações vão no fim.

**Limites de saída (relatório e resposta):** só contagens, nomes de papel, de ferramenta e de módulo, mês, categorias
fechadas e números. **Nunca** o texto de uma mensagem, um trecho de código, uma linha de código, uma palavra de prosa
copiada de um caso, identificador de execução nem `step_ref`. Para os casos, use só o número (1 a 75, na ordem do
`casos.csv`); o arquivo `leitura_causa/casos_invalid_syntax.csv`, com o número, o identificador e as categorias de cada
caso, fica no ambiente.

**O grupo.** 75 erros, 54 execuções, 9 meses (2025-12 a 2026-08), 10 papéis, 3,37 milhões de tokens: o maior do balde, e o
único em que o agente quase não se corrige (33% dos passos seguintes vêm sem erro). Os 75 são `codigo_mal_escrito`; o total
de erros de sintaxe do resíduo é 126 = 75 `invalid syntax` + 32 barra no fim da linha + 12 outra sintaxe + 7 f-string. A
primeira leitura (20 casos, validação 10/10) só deu categorias estruturais genéricas: 29 "linha fragmentada com sintaxe
inconsistente", 11 "rótulo isolado sem expressão válida", 4 operador lógico no fim, 1 marcador de markup; a regra de
forma anterior concordou em 7 de 15.

**Hipótese principal (H1).** A regra `e_texto` do `analysis/2026-10-trace-law-flow-third/pipeline/base_pipeline.py` (por
volta da linha 504) manda para a unidade de "texto solto no código" a linha que (a) começa com `|`, `#`, `**`, `- `,
número seguido de `.` ou `)`, ou tem crase, ou (b) tem **3 palavras ou mais** e pelo menos 15% delas são stopwords do
português (`PT_STOP`). Uma linha de 1 a 2 palavras (um rótulo, como "Resposta:") ou um texto em inglês **não** é pega. Se
boa parte dos 75 for texto ou rótulo que escapa dessa regra, o erro é o mesmo da unidade "texto solto" (o bloco de código
traz texto que não é Python) e a correção é estender a regra, sem unidade nova.

**Outras hipóteses.** H2: marcador de formato dentro do bloco (cerca de código, tag `<code>`, rótulos `Thought:` ou
`Observation:`). H3: código cortado no fim (resposta truncada). H4: deslize real de Python (delimitador não fechado,
dois-pontos faltando, operador ou palavra-chave mal usados). H5: outra linguagem colada (SQL, JSON, shell, LaTeX). H6:
aspas tipográficas ou caractere não ASCII.

**Entradas e o que reaproveitar** (leia os scripts antes e importe deles; não copie):
- `.../mineracao/residuo/residuo_c2e5e8b/casos.csv` (coluna `mensagem` inteira). Chave para a fonte:
  `(exec_id, agente, role, idx)` = `(cod_idef_exeo, cod_idef_aget, papel, step_pos)`.
- A fonte `analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet`: o código do passo que falhou
  é `error_code_action`; o anterior, `prev_code_action`; os seguintes, `next_*` e `next2_*`.
- `pipeline/validacao/contar_recorrencia_causa_residuo.py`: `contar(C)` dá os erros do balde com a coluna `familia`; os 75
  são `familia == "sintaxe_invalid_syntax"`.
- `pipeline/validacao/contar_limites_interpretador_residuo.py`: `ler_fonte(fonte)` e `_chave_casos(linha)`.
- `pipeline/base_pipeline.py`: `e_texto`, `PT_STOP`, `LITERAL_INICIO` e `submecanismo`.

**Parte 0 · Reprodução.** Reproduza 75 erros, 54 execuções, 9 meses e 10 papéis. Se não baterem, pare e diga.

**Parte 1 · Medidas por script, nos 75, sem ler.** A mensagem traz a linha que o interpretador apontou (o formato é
"Code parsing failed on line N … Error: invalid syntax"); o bloco de código é o `error_code_action`. Para cada erro, calcule:
- a posição: o número da linha do erro e o total de linhas do bloco (a 1ª linha? a última?);
- na linha que falhou: número de palavras, fração de letras, se tem caractere não ASCII, se é um rótulo (uma ou duas
  palavras seguidas de dois-pontos), se parece inglês (stopwords em inglês) ou português (`PT_STOP`), e se **passaria em
  `e_texto`** (sim/não);
- no bloco: tamanho em caracteres, se tem cerca de código ou tag `<code>`/`</code>`, e se **termina no meio** (o último
  caractere é `(`, `[`, `{`, `,`, `\` ou um operador, ou os delimitadores terminam desbalanceados);
- no histórico: se a mesma execução (exec_id + agente) já teve erro da mesma família antes (laço de repetição) e o desfecho
  do passo seguinte (sem erro / mesma família / outra família).

Mostre as contagens de cada traço por papel e por mês. E diga quantos dos 75 passariam em `e_texto` se o limite fosse
relaxado (aceitar rótulo de 1 palavra seguido de dois-pontos e texto em inglês).

**Parte 2 · A leitura.** Leia os 75 (se não der, 40, estratificados por mês, escolhendo pelo `idx` crescente dentro de
cada mês, e diga qual escolheu). Dê **uma** categoria por caso:
- `texto_ou_rotulo_no_lugar_de_codigo` (prosa, em português ou inglês, ou um rótulo solto na linha que falhou);
- `marcador_de_formato`;
- `codigo_cortado_no_fim`;
- `deslize_de_python` (código que é Python de verdade, com um erro de escrita);
- `outra_linguagem`;
- `aspas_ou_caractere_nao_ascii`;
- `outra: <até 8 palavras, sem texto de caso>` ou `nao_deu_para_ver`.

Dê também a confiança (alta, média ou baixa). Para os casos de `texto_ou_rotulo_no_lugar_de_codigo`, diga de onde vem o texto:
`explicacao_do_proprio_agente`, `texto_colado_de_retorno_de_ferramenta` ou `nao_deu_para_ver`. Depois, **sem olhar as suas
primeiras respostas**, reclassifique 15 casos sorteados (semente 7) e diga a concordância. É uma concordância do mesmo
leitor consigo mesmo: não substitui um segundo leitor, e o relatório deve dizer isso.

**Parte 3 · A regra (só se H1 se confirmar, isto é, se `texto_ou_rotulo_no_lugar_de_codigo` for pelo menos um terço dos
casos lidos).** Proponha uma regra determinística (traços, ou uma expressão regular) que pegue o que escapa da `e_texto` e
**conte-a**:
- nos 75;
- nos outros 51 erros de sintaxe do resíduo (barra 32, outra sintaxe 12, f-string 7), para ver se a regra rouba o que é de
  outro grupo;
- nos erros que hoje já caem em "texto solto no código" e "texto em literal" (a regra não pode tirar o que é deles);
- em **código válido**: nos blocos que rodaram sem erro (por exemplo, o passo anterior ao erro, `prev_code_action`, quando
  ele não é um erro), quantas linhas a regra marcaria como texto. Esses são os falsos positivos, e é o número que decide
  se a regra serve.

**Parte 4 · Custo e conclusão.** Tokens por categoria (soma) e o desfecho do passo seguinte por categoria. Uma linha por
hipótese (H1 a H6): "a leitura apoia", "contradiz" ou "inconclusiva", com a contagem que sustenta. E uma frase: "o `invalid
syntax` é principalmente …". Não decida o destino: a decisão é do pesquisador.

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio_invalid_syntax.md` e responda no chat com uma tabela por
parte e as limitações (o que não conseguiu ver e por quê). Não minere de novo e não toque no `casos.csv`.
