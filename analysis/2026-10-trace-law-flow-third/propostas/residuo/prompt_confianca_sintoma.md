Você vai testar, com dados, uma tabela de decisão sobre o que sobrou do balde "sintoma não reconhecido" do resíduo da
base 3. A tabela é uma **hipótese**: procure o que a contradiz, não o que a confirma. Rode tudo da raiz do repositório,
com `uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo do repositório.** Você pode
escrever um script de apoio e o relatório, só dentro da pasta de saída (git-ignored):
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/confianca_sintoma/`.

**Entradas (já existem):**
- `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/casos.csv`: os 420 erros do
  resíduo (376 do balde "causa não identificada" + 44 do balde "sintoma não reconhecido"). Tem `unidade`, `role`, `mes`,
  `padrao` (já mascarado), `tok_tot`, `mensagem`, `exec_id`, `agente`, `idx`.
- `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/recorrencia_sintoma.csv`: a
  medição de recorrência por grupo.
- A fonte: `analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet`. A chave entre as duas é
  `(exec_id, agente, role, idx)` = `(cod_idef_exeo, cod_idef_aget, papel, step_pos)`.
- A rodada: `analysis/2026-10-trace-law-flow-third/pipeline/resultados/observada_c2e5e8b31f297d21/`.

**Reuse, não reimplemente** (leia os scripts antes e importe deles):
- `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_recorrencia_sintoma_residuo.py`: `contar(C)` devolve
  os 44 com a coluna `grupo`; `GRUPOS` tem as regras de cada grupo.
- `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_infra_residuo.py`: `funcao_na_linha(msg)` dá o nome da
  função chamada na linha que falhou.
- `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_limites_interpretador_residuo.py`: `versoes(F, papeis)`
  (versões do agente por papel, com rótulos v1, v2…), e `desfecho` e `COLUNAS_FONTE` (como ler o passo seguinte, `next_*` e
  `next2_*`, na fonte).

**A tabela a testar (grupo → decisão proposta):**

| Grupo | Erros | Decisão proposta |
|---|---|---|
| `pdf_layout` | 13 | investigar |
| `dado_tipo_ou_conta` | 7 | fica no resíduo (passa só somando 5 padrões diferentes) |
| `etapa_ja_executada` | 3 | fica no resíduo (passa só somando 3 padrões; custo alto: 300 mil tokens) |
| `sem_nome` | 3 | fica no resíduo (a mensagem não diz a causa) |
| `decodificar_barra` | 8 | fica, em observação (um mês e um papel só) |
| `recusa_llm` | 5 | fica, em observação (já decidido em 11/11) |
| `arquivo_nao_achado` 2, `desempacotar` 2, `planilha_caractere` 1 | 5 | ficam (não passam na régua) |

**Perguntas (responda cada uma com contagens):**

0. **Reprodução.** Reproduza as contagens da tabela (44 erros, por grupo: erros, execuções, meses). Se não baterem, pare e
   diga.
1. **O agrupamento está certo?** Para cada grupo: os padrões (coluna `padrao`, já mascarada) com erros, execuções e meses; a
   função chamada na linha que falhou (por padrão); e a mesma conta para os 3 grupos que passam só somados
   (`dado_tipo_ou_conta`, `etapa_ja_executada`, `sem_nome`). Os padrões dentro do grupo têm a mesma função na linha e o
   mesmo papel? Diga com os números, sem concluir "mesmo mecanismo".
2. **O grupo é maior do que parece?** Aplique a regra de cada grupo aos **420 erros** do `casos.csv` (os dois baldes): há
   erros do mesmo tipo no balde "causa não identificada"? Em quantos erros, execuções e meses? Depois, se não for pesado,
   aplique também aos erros das outras unidades da rodada (carregue a rodada com `carregar_rodada` do
   `especificas/reentrada.py`) e mostre a contagem por unidade e por mês. Se não puder, diga.
3. **`pdf_layout` (o único a investigar).** (a) Por mês, os erros do grupo e a atividade do papel AgenteEstruturador na
   fonte (quantos erros de qualquer tipo ele tem por mês, para saber se ele rodou de maio a agosto: o PDF "acabou" ou o
   papel parou?); (b) as versões do agente nesse papel (rótulos v1, v2…, primeiro e último mês, quantos erros do PDF por
   versão); (c) a distância do passo: o que acontece nos dois passos seguintes (sem passo / mesmo erro de novo / sem erro /
   outro erro); (d) quantas execuções têm 2 erros; (e) a função na linha que falhou.
4. **`decodificar_barra`.** Se a fonte tiver data mais fina que o mês, quantos dias distintos; senão, diga que não tem. As
   versões do agente dos 8 erros; quantos erros desse tipo o mesmo papel tem nos outros meses (qualquer unidade).
5. **`etapa_ja_executada`.** Por que 300 mil tokens em 3 erros: tokens por erro, posição do passo (`idx`) e quantos
   passos a execução tem na fonte; o que o agente faz nos dois passos seguintes; a função na linha.
6. **`dado_tipo_ou_conta` e `sem_nome`.** O papel e a função na linha de cada erro; os dois passos seguintes; para o
   `sem_nome`, as colunas de formato da mensagem (`tem_due_to`, `tem_linha_error`).
7. **`desempacotar`, `arquivo_nao_achado`, `planilha_caractere`.** Só a função na linha e os dois passos seguintes.
8. **Cruzamento.** O papel ContestacaoCivel concentra `decodificar_barra` (8) e `etapa_ja_executada` (3), os dois em
   julho e agosto. Quantos dos 44 são desse papel nesses meses, e quantos dos 420? As versões do agente desse papel em
   julho e agosto.

**Conclusão por linha da tabela.** Para cada linha, uma de três: "a evidência apoia a decisão", "a evidência contradiz", ou
"inconclusiva", com a medida que a sustenta. Não decida nada além disso: a decisão é do pesquisador.

**O que pode sair na resposta:** contagens, nomes de papel, meses, nomes de função ou módulo, a coluna `padrao` (já
mascarada), tipos de erro, rótulos de versão (v1, v2…) e tokens.

**O que não pode sair:** texto de mensagem, trecho de código, identificador de execução, `step_ref` e o código bruto de
versão.

**Entrega.** Grave o relatório completo em `confianca_sintoma/relatorio.md` (na pasta de saída) e responda no chat com o
resumo: uma tabela por pergunta, as conclusões por linha e as limitações (o que você não conseguiu medir e por quê). Não
minere de novo e não toque no `casos.csv`.
