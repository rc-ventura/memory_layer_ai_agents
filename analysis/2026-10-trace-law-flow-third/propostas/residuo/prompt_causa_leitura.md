Você vai **testar, com dados e com leitura de casos, uma tabela de decisão** sobre o balde "causa não identificada" do
resíduo da base 3 (376 erros). A tabela é uma **hipótese**: procure o que a contradiz, não o que a confirma. Rode tudo da
raiz do repositório, com `uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo do
repositório.** Você pode escrever um script de apoio e os arquivos da leitura, só dentro de
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/`
(git-ignored).

**Entradas e o que reaproveitar** (leia os scripts antes e importe deles; não copie):
- `.../mineracao/residuo/residuo_c2e5e8b/casos.csv`: os 420 erros do resíduo (a coluna `mensagem` tem a mensagem inteira).
  Chave para a fonte: `(exec_id, agente, role, idx)` = `(cod_idef_exeo, cod_idef_aget, papel, step_pos)`.
- A fonte: `analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet` (só linhas de erro). As colunas
  de código são `prev_code_action`, `error_code_action` (o que falhou), `next_code_action` e `next2_code_action`.
- As contagens: `analysis/2026-10-trace-law-flow-third/data/base_contagens.parquet` (o denominador: execuções e
  ActionSteps; descubra as colunas, e veja em `pipeline/execucao/taxas.py` como a junção com a fonte é conferida).
- `pipeline/validacao/contar_recorrencia_causa_residuo.py`: `contar(C)` dá os erros do balde com a coluna `familia`.
- `pipeline/validacao/contar_recorrencia_sintoma_residuo.py`: `contar(C)` dá os 44 do balde do sintoma com a coluna
  `grupo` (o `decodificar_barra` é o grupo que importa aqui).
- `pipeline/validacao/contar_limites_interpretador_residuo.py`: `ler_fonte(fonte)` e `_chave_casos(linha)`.
- `pipeline/validacao/contar_infra_residuo.py`: `funcao_na_linha(msg)`.
- Contexto já medido: agosto teve mais execuções e uma taxa de erro por ActionStep bem maior que julho (6,7% → 15,7%,
  `02-relatorio-achados.md` §5); as rajadas de agosto podem ser em parte volume.

**A tabela a testar (grupo → decisão proposta):**

| Grupo | Erros | Decisão proposta |
|---|---|---|
| **A** · valor numérico que é texto: `round_ou_formato_em_texto` (45, todos CalculoTrabalhista) + `soma_ou_concatenacao_entre_tipos` do CalculoTrabalhista (41 de 52) | ~86 | investigar |
| **B** · barra invertida no código: `sintaxe_continuacao_barra` (32) + a parte de `sintaxe_fstring` com barra + `decodificar_barra` do balde do sintoma (8) | ~45 | investigar |
| **C** · `sintaxe_invalid_syntax` | 75 | investigar |
| **D** · `dataframe_construtor` (JoogleAnalytics) | 19 | investigar |
| **E** · `objeto_nao_chamavel` | 7 | checar se é nome de ferramenta usado como variável (a unidade do Ajuste 37) |
| ficam no resíduo | 99 | `indexacao_do_interpretador` 34 (15 padrões), `tipo_outro` 16 (9 padrões), `pandas_outro` 11, `sintaxe_outra` 12, `data_ou_hora` 9, `json_nao_serializavel` 6, `comparacao_entre_tipos` 5, o resto da soma entre tipos |
| em observação (um mês só) | 43 | `numero_invalido_da_ferramenta` 23, `json_ausente_no_retorno` 13, `indice_de_lista_com_texto` 7 |

**Perguntas (responda cada uma com contagens; numere os casos lidos de 1 em diante por pergunta e use só o número):**

0. **Reprodução.** Reproduza erros, execuções e meses de cada família da tabela. Se não baterem, pare e diga.
1. **Rajada ou volume?** Para os papéis CalculoTrabalhista, ContestacaoCivel (`ontestacaoCivel` no dado), JoogleAnalytics e
   OBFCivel, por mês (jan a ago): as execuções ou ActionSteps do papel (contagens), os erros do papel, e os erros dos
   grupos A, B, C e D. Diga se a concentração de agosto dos grupos A e B é proporcional ao volume do papel em agosto ou
   maior (a taxa do grupo sobre os ActionSteps do papel-mês, agosto contra os outros meses).
2. **Grupo A, o mesmo problema?** (a) As execuções (exec_id + agente) que têm erro das duas famílias (round/formato e
   soma) e, nelas, qual vem primeiro. (b) Para os 45 + 41, no código que falhou, de onde vem o valor que é texto:
   `retorno_de_ferramenta` (resultado de uma chamada de ferramenta), `lido_de_arquivo_ou_json`, `escrito_pelo_agente`,
   `nao_deu_para_ver`; e o nome da ferramenta quando for retorno de ferramenta. (c) O formato do valor, só a classe:
   `decimal_com_virgula`, `decimal_com_ponto`, `com_simbolo_de_moeda`, `outro`, `nao_deu_para_ver`. (d) O que o agente
   faz no passo seguinte para corrigir: `converte_o_texto` (float, replace…), `refaz_o_calculo_sem_o_valor`, `outra`.
3. **Grupo B, é uma coisa só?** (a) Por papel e mês, os erros de cada uma das três pontas (barra no fim da linha, f-string
   com barra, `decodificar_barra`) e quantas execuções têm mais de uma ponta. (b) Leia os casos da barra no fim da linha
   (até 12, escolha pelo `idx` crescente) e os 8 do `decodificar_barra` e classifique a barra: `caminho_de_arquivo`,
   `sequencia_de_escape_digitada` (um `\n` ou `\t` literal), `regex`, `latex_ou_formula`, `texto_com_barra_juridica`,
   `outra`, `nao_deu_para_ver`; e se o texto com a barra está num literal do passo ou vem de variável.
4. **Grupo C, o que está errado na linha?** Para os 75 erros, classifique a **forma** da linha que falhou (a linha que o
   interpretador aponta, no código de `error_code_action`), nunca o conteúdo: `prosa_sem_codigo`,
   `cerca_markdown_ou_tag`, `delimitador_nao_fechado`, `palavra_chave_mal_usada`, `aspas_tipograficas_ou_nao_ascii`,
   `string_multilinha_quebrada`, `outra`. Faça por regra (script seu) e valide lendo 15 casos, dizendo a concordância.
   Por categoria, o desfecho do passo seguinte (sem erro / a mesma família / outra família).
5. **Grupo D.** O que é passado a `pd.DataFrame(...)` nos 19: `string`, `dict_de_escalares`, `lista_vazia`,
   `variavel_de_passo_anterior`, `outra`, `nao_deu_para_ver`; e o que o agente muda no passo seguinte.
6. **Grupo E.** Nos 7: o nome chamado; se esse nome foi atribuído como variável no próprio passo ou no passo anterior
   (`prev_code_action`); se é o nome de uma ferramenta (um nome chamado como função simples em outros passos da fonte).
   Diga: `nome_de_ferramenta_sobrescrito`, `variavel_propria` ou `nao_deu_para_ver`.
7. **Conclusão por linha da tabela.** Para cada linha (A, B, C, D, E, "ficam", "em observação"): "a leitura apoia a
   decisão", "contradiz" ou "inconclusiva", com a medida que a sustenta. Diga também se algum dos que "ficam" ou estão
   "em observação" deveria subir, e por quê (com contagem).

**O que pode sair na resposta:** contagens, nomes de papel, meses, nomes de função ou de ferramenta, a coluna `padrao` (já
mascarada), as categorias acima e o número do caso lido.

**O que não pode sair:** texto de mensagem, trecho de código, conteúdo de variável ou de célula, identificador de
execução e `step_ref`.

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio.md` e responda no chat com: uma tabela por pergunta, a
tabela de conclusão por linha e as limitações (o que não conseguiu ver e por quê; é uma leitura de um leitor só). Não
decida nada além da conclusão por linha: a decisão é do pesquisador. Não minere de novo e não toque no `casos.csv`.
