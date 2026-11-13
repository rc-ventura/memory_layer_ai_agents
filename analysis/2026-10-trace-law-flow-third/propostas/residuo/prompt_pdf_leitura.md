Você vai **ler 13 casos** do grupo `pdf_layout` do resíduo da base 3 e entregar um relatório com categorias fechadas e
contagens. O objetivo é decidir o destino do grupo (memória, harness, falha silenciosa ou fica no resíduo), e para isso
preciso de três respostas. Rode tudo da raiz do repositório, com `uv run --no-sync`. Não instale nem atualize pacotes.
**Não edite nenhum arquivo do repositório.** Você pode escrever um script de apoio e os arquivos da leitura, só dentro de
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_pdf/` (git-ignored).

**O grupo.** São 13 erros do balde "sintoma não reconhecido": o `LayoutError` do gerador de PDF (uma linha de tabela maior
que a página), vindo de duas ferramentas: `orquestrador_eletronico` (8) e `orquestrador_papel` (5), de um papel só
(AgenteEstruturador), de fevereiro a abril. Já medimos o que dá para medir sem ler:
- em 9 dos 13 o agente chama a ferramenta de novo (7 no passo seguinte, 2 no depois) e o erro não se repete no passo
  seguinte; em 4 ele encurta o código e em 3 muda outra coisa; em 0 divide o conteúdo em várias chamadas;
- em 4 dos 13 o agente chama `final_answer` no passo seguinte e nunca mais chama a ferramenta (1 do eletronico, 3 do
  papel);
- no `orquestrador_papel` o maior texto literal do código que falhou é pequeno (mediana 74 caracteres): o conteúdo grande
  chega por variável.

**Entradas e o que reaproveitar** (leia os scripts antes e importe deles; não copie):
- `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/casos.csv` (a coluna
  `mensagem` tem a mensagem inteira, com números).
- A fonte: `analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet`. Chave entre as duas:
  `(exec_id, agente, role, idx)` = `(cod_idef_exeo, cod_idef_aget, papel, step_pos)`. As colunas de código são
  `prev_code_action` (passo anterior), `error_code_action` (o que falhou), `next_code_action` e `next2_code_action` (os
  dois seguintes).
- `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_recorrencia_sintoma_residuo.py`: `contar(C)` devolve os
  44 com a coluna `grupo`; o grupo é `pdf_layout`.
- `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_limites_interpretador_residuo.py`: `ler_fonte(fonte)`
  e `_chave_casos(linha)`.
- `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_infra_residuo.py`: `funcao_na_linha(msg)` (a
  ferramenta).
- `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/pdf_medidas.csv`: a medida
  anterior (só números, mesma ordem dos 13).

**Numere os casos de 1 a 13** (ordem do `casos.csv`) e use só esse número no relatório. O arquivo com o número, o
identificador da execução e as categorias de cada caso fica em `leitura_pdf/casos_lidos.csv`, dentro do ambiente.

**Leia cada caso e classifique** nas categorias abaixo (use "outra: <até 8 palavras, sem texto de caso>" se nenhuma
servir, e "nao_deu_para_ver" se o código não permitir dizer). Dê também a confiança de cada classificação (alta, média ou
baixa).

**Pergunta 1 · O que há na linha grande demais?** (código que falhou, mais o passo anterior se precisar)
- (a) *Origem do conteúdo passado à ferramenta:* `texto_escrito_no_proprio_passo` (literal no código) ·
  `montado_no_proprio_passo` (f-string, `join`, laço sobre variáveis, no mesmo código) ·
  `variavel_de_passo_anterior` (o argumento é uma variável que não é definida nesse código).
- (b) *Tipo de conteúdo:* `campo_de_texto_longo` · `lista_ou_tabela_com_muitas_linhas` · `varios_campos_juntos` ·
  `nao_deu_para_ver`.
- (c) *Números na mensagem*, se ela trouxer: linhas e colunas da tabela, altura da linha ou célula mais alta, altura
  disponível da página. Só os números, nunca o texto da célula.

**Pergunta 2 · O que o agente muda nos 9 em que a ferramenta volta?** (compare o código que falhou com o do passo em que
a ferramenta volta: o seguinte, ou o depois dele nos 2 que passaram por um passo no meio)
`encurtou_o_texto` (mesma estrutura, texto menor) · `truncou_com_fatia` (corta com `[:n]` ou parecido) ·
`removeu_campo_ou_coluna` · `dividiu_em_varias_linhas_ou_tabelas` · `trocou_o_formato` (tabela por parágrafo ou lista) ·
`mudou_outra_coisa_sem_relacao_com_o_tamanho`. Diga também se o passo intermediário (nos 2) faz alguma coisa relacionada
ao tamanho (por exemplo, medir o conteúdo) ou nenhuma.

**Pergunta 3 · O que dizem os 4 `final_answer`?** (o código do passo seguinte) Para cada um:
- (a) `afirma_que_gerou_o_documento` · `admite_que_nao_gerou` · `nao_menciona_o_documento`;
- (b) se a resposta traz um caminho, um nome de arquivo ou um link de documento (sim/não), sem dizer qual;
- (c) se o passo anterior ao que falhou já tinha chamado uma das duas ferramentas com sucesso (sim/não).

**Depois das três perguntas, preencha esta tabela de hipóteses.** Para cada linha diga "a leitura apoia", "contradiz" ou
"inconclusiva", com a contagem que sustenta:

| Hipótese de destino | O que a apoiaria |
|---|---|
| harness: a ferramenta devia partir a linha ou tratar o erro | o conteúdo vem de variável (não escrito pelo agente), e o agente não mede o tamanho antes |
| memória: o agente devia evitar | o conteúdo é texto que o agente escreve e poderia encurtar antes de chamar |
| falha silenciosa | o `final_answer` dos 4 afirma que o documento foi gerado, ou nem menciona a falha |
| só desistência (memória de recuperação) | o `final_answer` dos 4 admite que não gerou |

**O que pode sair na resposta:** o número do caso (1 a 13), as categorias, as contagens, os números da mensagem (linhas,
colunas, alturas), nomes de ferramenta, mês, papel e confiança.

**O que não pode sair:** texto de mensagem, trecho de código, conteúdo de célula, texto de `final_answer`, identificador
de execução e `step_ref`.

**Entrega.** Grave o relatório completo em `leitura_pdf/relatorio.md` e responda no chat com: (1) uma tabela por pergunta;
(2) a tabela de casos (número, ferramenta, mês, categorias, confiança); (3) a tabela de hipóteses; (4) as limitações (o
que você não conseguiu ver e por quê; é uma leitura de um leitor só, sem segundo leitor). Não decida o destino: a decisão é
do pesquisador. Não minere de novo e não toque no `casos.csv`.
