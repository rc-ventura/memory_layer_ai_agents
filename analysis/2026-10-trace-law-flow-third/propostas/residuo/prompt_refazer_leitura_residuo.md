Você vai **refazer**, na **base 3**, a leitura de 215 erros do resíduo (balde `X_causa_nao_identificada`, rodada `dbd40c0f4d3604b1`).
A leitura anterior não passou na conferência: origem, reação e sinais vieram inconsistentes, e por isso ela é refeita do zero. Rode tudo
da raiz do repositório, com `uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo versionado.** Grave tudo em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_dbd40c0/refazer_leitura/` (a `PASTA`).

## As regras que invalidam o trabalho se forem quebradas

1. **Quem classifica é você, lendo cada caso.** Nenhum script pode escolher categoria: nada de regex, dicionário, mapa de família ou
   padrão para categoria, nem preenchimento em lote. Script só prepara os lotes, confere e conta.
2. **Não abra** a pasta `residuo_dbd40c0/fechar_residuo/` nem o `ler_fechar_residuo.py`. Não reaproveite nenhum rótulo antigo.
3. Se não conseguir ler os 215, **pare e diga quantos leu**. Não complete o resto de outro jeito.
4. **Você descreve e conta; quem decide o destino é o pesquisador.** A `unidade_candidata` é uma hipótese.

**Limites de saída (arquivos de resumo e resposta):** só contagens, nomes de papel, de ferramenta, de módulo e de unidade, mês, as
categorias fechadas e a coluna `padrao` do `casos.csv`, já mascarada. **Nunca** texto de mensagem, de código ou de valor, nem
identificador de execução. Lotes e anotações ficam na `PASTA` e não saem do ambiente.

## Etapa 0 · conferir antes de começar

- Casos: `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_dbd40c0/casos.csv`.
- Fonte: `analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet`.
- Família: função `contar` de `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_recorrencia_causa_residuo.py` (importe,
  não reescreva). Junção com a fonte e `passo_seguinte`: função `depois` do mesmo script.
- Colunas da fonte: `error_message`, `error_code_action`, `error_model_output`, `error_observations`, `prev_code_action`,
  `prev_observations`, `next_step_number`, `next_code_action`, `next_model_output`, `next_observations`, `next_error_message`.

**Pare e diga o que faltou** se uma coluna não existir, se algum erro não achar sua linha na fonte, ou se os totais não baterem:

| Parte | Grupo | Famílias | Erros |
|---|---|---|---|
| A | **G1 · indexação recusada** | `indexacao_do_interpretador` | 34 |
| A | **G2 · barra invertida** | `sintaxe_continuacao_barra` e `sintaxe_fstring` | 31 + 7 |
| A | **G3 · construtor de DataFrame** | `dataframe_construtor` | 19 |
| B | **Os demais** | todas as outras, **menos** `sintaxe_invalid_syntax` (55) | 124 |

## Etapa 1 · preparar os lotes (script, sem categoria nenhuma)

Grave `preparar_lotes.py`. Ele numera os casos (`caso_001`...), guarda a chave em `chaves.csv` e escreve `lotes/lote_NN.md`, com **10
casos por lote**, na ordem de grupo. Cada caso traz, inteiros: grupo, família, papel, mês, `passo_seguinte` e as colunas da etapa 0.

Só para o G2, o script acrescenta dois fatos, medidos com `ast.parse` sobre o `error_code_action`:

- `diagnostico_parse`: `reproduz` (mesma mensagem), `outro_erro`, `compila_sem_erro` ou `codigo_ausente`;
- `linha_da_mensagem_no_codigo`: a linha rejeitada que a própria mensagem mostra aparece no código? `sim` ou `nao`.

Registre a versão do Python usada. Quando o parse não reproduzir, **classifique pela linha rejeitada que a mensagem mostra**.

## Etapa 2 · ler, lote por lote

Abra cada lote, leia os 10 casos e só então escreva `anotacoes/lote_NN.csv` à mão. Para cada caso, anote:

- `origem` do valor envolvido. Siga a variável no código do passo, depois no `prev_code_action` e nas observações: `ferramenta:<nome>`,
  `conversao_do_agente`, `literal_do_agente`, `arquivo_ou_json`, `nao_se_aplica`, `nao_deu_para_ver`. **Ferramenta é função do agente
  chamada direto.** Método ou função do Python (`.get`, `sum`, `mean`, `pd.DataFrame`, `from_dict`) não é ferramenta: continue seguindo o
  valor até de onde ele veio.
- `reacao`, lendo o `next_code_action`: `converte_o_tipo`, `inspeciona_antes`, `muda_a_chave_ou_o_acesso`, `reescreve_o_trecho`,
  `troca_de_abordagem`, `repete_igual`, `sem_passo`. **`sem_passo` só quando `passo_seguinte` for `sem_passo`.** Um passo seguinte sem erro
  tem reação: leia o que mudou. Em erro de sintaxe, `converte_o_tipo` não se aplica.
- `confianca`: `alta` ou `baixa`.
- `evidencia_campo` (`mensagem`, `codigo`, `anterior`, `observacoes`, `seguinte`, `saida_seguinte`) e `evidencia_trecho`: um trecho **copiado
  literalmente** desse campo, de 10 a 200 caracteres, que sustenta a categoria principal.
- `justificativa`: uma frase sua sobre este caso.

**G1:** `valor_indexado` (`texto`, `texto_que_parece_json`, `lista`, `dict`, `numero`, `none`, `dataframe_ou_series`, `objeto`, `outro`);
`chave_usada` (`inteiro`, `texto`, `slice`, `variavel`, `outro`); `erro_final` (`TypeError`, `KeyError`, `IndexError`, `ValueError`, `outro`);
`leitura_g1` (`retorno_em_texto_tratado_como_estrutura`, `lista_indexada_com_texto`, `dict_sem_a_chave`, `lista_fora_do_tamanho`,
`dataframe_acessado_errado`, `none_indexado`, `outra`).

**G2:** `classe_barra` (`quebra_de_linha_literal_entre_instrucoes`, `aspa_escapada_fora_de_string`, `escape_fora_de_string`, `regex`,
`caminho_de_arquivo`, `barra_de_continuacao_com_algo_depois`, `barra_em_expressao_de_fstring`, `aspas_aninhadas_em_fstring`, `outra`);
`bloco_escapado` (`quase_todas`, `algumas`, `nenhuma`); `bloco_em_uma_linha` (`sim`, `nao`); `repete_a_classe` (`sim`, `nao`, `sem_erro`,
`sem_passo`). Use `outra` só com a `justificativa` dizendo o que é.

**G3:** `argumento` (`variavel`, `literal_texto`, `literal_numero`, `chamada_de_funcao`, `outro`); `tipo_provavel` (`texto`,
`texto_que_parece_json`, `numero`, `none`, `dict_de_escalares`, `nao_deu_para_ver`); `como_soube` (`atribuicao`, `observacao`, `saida_do_modelo`,
`correcao_seguinte`, `nao_soube`); `correcao` (`envolve_em_lista_ou_dict`, `desserializa`, `passa_index`, `monta_de_outro_jeito`, `outra`).

**Parte B:** antes de ler, veja `UNI`, `SUB2UNI` e `submecanismo` em `analysis/2026-10-trace-law-flow-third/pipeline/base_pipeline.py`. Anote:

- `unidade_candidata`: `U_arg_nomeado`, `U_campo_inexistente`, `U_codigo_lento`, `U_contrato_dict`, `U_estado_perdido`,
  `U_ferramenta_nao_declarada`, `U_next_gerador`, `U_nome_ferramenta_como_variavel`, `U_nome_inventado`, `U_repr_colado`, `U_resultado_bruto`,
  `U_sandbox`, `U_texto_literal`, `U_texto_solto`, `U_tipo_retorno`, `U_verificacao_existencia`, `H_bloco_code`, `H_contrato_ferramenta`,
  `H_infra_llm`, `H_timeout_ferramenta`, `C_limite_passos` ou `nenhuma`. **Na dúvida, `nenhuma`.** A mensagem sozinha não basta.
  `U_tipo_retorno` exige ver que o valor **veio do retorno de uma ferramenta** e chegou num tipo diferente do que o agente tratou.
- `por_que_nao_casou`: `mesma_causa_com_outra_redacao`, `mesma_causa_sem_sinal_no_trace`, `mecanismo_diferente`, `erro_comum_de_codigo`,
  `erro_interno_da_ferramenta`.
- `dono`: `agente`, `ferramenta_ou_harness`, `nao_deu_para_ver`.
- Só em `numero_invalido_da_ferramenta`, `quem_errou`: `agente_passou_valor_errado`, `ferramenta_recusou_valor_valido`, `nao_deu_para_ver`.

## Etapa 3 · conferir a leitura (script; corrija relendo o caso, nunca o script)

Grave `conferir_leitura.py`. Ele sai com 1 e lista os `caso_NNN` se falhar qualquer item:

1. os 215 casos anotados, sem repetir, e todo valor dentro da lista fechada;
2. `evidencia_trecho` existe literalmente no `evidencia_campo` daquele caso;
3. `reacao` é `sem_passo` **se e somente se** `passo_seguinte` é `sem_passo`; `repete_a_classe` é `sem_erro` **se e somente se** `passo_seguinte`
   é `sem_erro`, e `sem_passo` idem;
4. todo `ferramenta:<nome>` aparece no código como chamada sem ponto antes e não é função embutida do Python;
5. `U_tipo_retorno` só com `origem` `ferramenta:<nome>`; `tipo_provavel` diferente de `nao_deu_para_ver` só com `como_soube` diferente de `nao_soube`;
6. nenhuma `justificativa` repetida em mais de 3 casos.

## Etapa 4 · medir os sinais

Grave `sinais.py`. Para cada categoria com **3 erros ou mais** (`leitura_g1`, `classe_barra`, `tipo_provavel` e cada `unidade_candidata` diferente de
`nenhuma`), procure um **sinal observável por script** na mensagem ou no código: tente ao menos a família, a exceção final e uma marca no código.
Aplique o sinal aos **270** erros do balde e informe: `erros_da_categoria`, `pega_dentro`, `pega_fora`, `cobertura` (dentro ÷ categoria),
`precisao` (dentro ÷ tudo o que pegou) e `atinge_80` (cobertura de 80% ou mais). Sinal com `pega_dentro` 0 está errado: corrija ou escreva `sem_sinal`.

## Etapa 5 · a entrega

Grave `refazer_leitura.md` na `PASTA` e passe o varredor. Só mostre o conteúdo se sair limpo:

```
uv run --no-sync python .github/skills/mineracao-base/scripts/varrer_pii.py analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_dbd40c0/refazer_leitura/refazer_leitura.md
```

Mostre, com **tabelas estreitas** (no máximo 7 colunas e nomes curtos), nesta ordem:

1. totais (34, 38, 19, 124), versão do Python, resultado do `conferir_leitura.py` e `diagnostico_parse` e `linha_da_mensagem_no_codigo` do G2;
2. **Parte A**, por categoria principal de cada grupo: erros, execuções, meses, papéis, `sem_erro`, `mesma_familia`, `outra_familia`;
3. **Parte A**, `origem` e `reacao` por grupo e os traços do G2;
4. **Parte B**, erros, execuções e meses por `unidade_candidata`, por `por_que_nao_casou`, por `dono` e por `quem_errou`;
5. **Parte B**, uma linha por padrão com **2 erros ou mais**: `padrao` (até 60 caracteres), erros, execuções, meses, unidade mais frequente e em quantos
   erros, `sem_erro`. Os padrões de 1 erro entram somados por família e unidade;
6. os sinais: categoria, erros, dentro, fora, cobertura, precisão;
7. quantos casos ficaram com `confianca` `baixa` em cada parte e as limitações.

Termine com a frase: **"Abra uma conversa nova para a etapa 6."**

## Etapa 6 · releitura às cegas (só em conversa nova)

Nesta etapa **não abra** a pasta `anotacoes/` nem o `refazer_leitura.md`. Em cada parte, ordene os casos pelo SHA-256 de `exec_id + agente + idx`, pegue os 15
primeiros, leia nos lotes só esses casos e anote a categoria principal em `releitura/parte_A.csv` e `releitura/parte_B.csv`. Depois grave
`comparar_releitura.py`, que compara com as anotações, e mostre só: **x de 15 na Parte A, y de 15 na Parte B** e as categorias que mudaram, em contagens.
É o mesmo modelo relendo, não um segundo leitor: diga isso na resposta.
