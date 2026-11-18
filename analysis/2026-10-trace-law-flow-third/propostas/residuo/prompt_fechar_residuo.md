Você vai ler, na **base 3**, os erros do resíduo (balde `X_causa_nao_identificada`, rodada `dbd40c0f4d3604b1`) que ainda não têm
destino e dizer **o que há dentro deles**. São duas partes: a **Parte A** lê três grupos (91 erros) e a **Parte B** compara os
outros 124 erros com as unidades que já existem. Rode tudo da raiz do repositório, com `uv run --no-sync`. Não instale nem
atualize pacotes. **Não edite nenhum arquivo versionado.** Grave o que produzir, scripts inclusive, em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_dbd40c0/fechar_residuo/`.
É a leitura de um leitor só. **Você descreve e conta; quem decide o destino é o pesquisador.** A `unidade_candidata` da Parte B é
uma hipótese, não uma decisão.

**Limites de saída (valem para os arquivos de resumo e para a resposta):** só contagens, nomes de papel, de ferramenta, de módulo
e de unidade, mês, as categorias fechadas abaixo e a coluna `padrao` do `casos.csv`, que já vem mascarada. **Nunca** o texto de uma
mensagem, de um código ou de um valor, nem identificador de execução. As anotações caso a caso ficam em `casos_lidos.csv`, nessa
pasta, e não saem do ambiente.

## A população

- Casos: `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_dbd40c0/casos.csv`.
- Fonte: `analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet`.
- A família de cada erro vem da função `contar` de
  `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_recorrencia_causa_residuo.py` (importe, não reescreva). A
  junção com a fonte é a da função `depois` desse script (`cod_idef_exeo`, `cod_idef_aget`, `papel`, `step_pos`). Na fonte use
  `error_message`, `error_code_action`, `prev_code_action`, `next_code_action`, `next_error_message` e `next_step_number`.

| Parte | Grupo | Famílias | Erros esperados |
|---|---|---|---|
| A | **G1 · indexação recusada** | `indexacao_do_interpretador` | 34 |
| A | **G2 · barra invertida** | `sintaxe_continuacao_barra` e `sintaxe_fstring` | 31 + 7 |
| A | **G3 · construtor de DataFrame** | `dataframe_construtor` | 19 |
| B | **Os demais** | todas as outras, **menos** `sintaxe_invalid_syntax` (55, já decidida) | 124 |

O balde tem 270 erros: 91 + 124 + 55. **Se algum total não bater, pare e diga qual.** Leia **todos** os 215 casos das duas partes,
não uma amostra.

## Em todo caso das duas partes, anote

- `passo_seguinte` por script: `sem_erro`, `mesma_familia`, `outra_familia` ou `sem_passo` (a mesma definição do script acima).
- `origem` do valor envolvido, procurando a atribuição da variável no código do passo e, se não achar, no `prev_code_action`:
  `ferramenta:<nome>`, `conversao_do_agente` (`json.loads`, `literal_eval`, `str`, `int`...), `literal_do_agente`,
  `arquivo_ou_json`, `nao_se_aplica`, `nao_deu_para_ver`.
- `reacao` no passo seguinte: `converte_o_tipo`, `inspeciona_antes`, `muda_a_chave_ou_o_acesso`, `reescreve_o_trecho`,
  `troca_de_abordagem`, `repete_igual`, `sem_passo`.
- `confianca`: `alta` ou `baixa`.

# Parte A · os três grupos

## G1 · indexação recusada

A mensagem tem a forma "Could not index <valor> with <chave>: <erro>". Anote:

- `valor_indexado`: `texto`, `texto_que_parece_json`, `lista`, `dict`, `numero`, `none`, `dataframe_ou_series`, `objeto`, `outro`.
- `chave_usada`: `inteiro`, `texto`, `slice`, `variavel`, `outro`.
- `erro_final`: o nome da exceção no fim da mensagem (`TypeError`, `KeyError`, `IndexError`, `ValueError`, `outro`).
- `leitura_g1`: `retorno_em_texto_tratado_como_estrutura`, `lista_indexada_com_texto`, `dict_sem_a_chave`,
  `lista_fora_do_tamanho`, `dataframe_acessado_errado`, `none_indexado`, `outra`.

## G2 · barra invertida

Ache a linha e a coluna do erro com `compile()` sobre o `error_code_action` (conte em `nao_reproduz` os casos em que o
`compile` não acusar o mesmo erro). Anote:

- `classe_barra`: `quebra_de_linha_literal_entre_instrucoes` (o `\n` digitado separa comandos, fora de string),
  `aspa_escapada_fora_de_string` (`\"` ou `\'` fora de string), `escape_fora_de_string` (outro `\x` fora de string), `regex`,
  `caminho_de_arquivo`, `barra_de_continuacao_com_algo_depois`, `barra_em_expressao_de_fstring`, `aspas_aninhadas_em_fstring`,
  `outra`.
- `bloco_escapado`: a proporção das aspas do bloco que vêm depois de uma barra: `quase_todas` (90% ou mais), `algumas`, `nenhuma`.
- `bloco_em_uma_linha`: o bloco inteiro está numa única linha física? `sim` ou `nao`.
- `repete_a_classe`: o passo seguinte tem a mesma `classe_barra`? `sim`, `nao` ou `sem_erro`.

## G3 · construtor de DataFrame

- `argumento`: `variavel`, `literal_texto`, `literal_numero`, `chamada_de_funcao`, `outro`.
- `tipo_provavel`: `texto`, `texto_que_parece_json`, `numero`, `none`, `dict_de_escalares`, `nao_deu_para_ver` (diga como
  soube; se for só pelo passo seguinte, marque `confianca` `baixa`).
- `correcao`: `envolve_em_lista_ou_dict`, `desserializa`, `passa_index`, `monta_de_outro_jeito`, `outra`.

# Parte B · os 124 erros contra as unidades que já existem

**A pergunta:** cada erro é um mecanismo que o pipeline já conhece, com outra redação, ou é outra coisa? Um erro pode pertencer a
uma unidade existente mesmo aparecendo em um mês só. Antes de ler, leia o que cada unidade significa em `UNI` e `SUB2UNI` e as
regras em `submecanismo`, no `analysis/2026-10-trace-law-flow-third/pipeline/base_pipeline.py`. Anote em cada erro:

- `unidade_candidata`: uma destas ou `nenhuma`: `U_arg_nomeado`, `U_campo_inexistente`, `U_codigo_lento`, `U_contrato_dict`,
  `U_estado_perdido`, `U_ferramenta_nao_declarada`, `U_next_gerador`, `U_nome_ferramenta_como_variavel`, `U_nome_inventado`,
  `U_repr_colado`, `U_resultado_bruto`, `U_sandbox`, `U_texto_literal`, `U_texto_solto`, `U_tipo_retorno`,
  `U_verificacao_existencia`, `H_bloco_code`, `H_contrato_ferramenta`, `H_infra_llm`, `H_timeout_ferramenta`, `C_limite_passos`.
- `por_que_nao_casou`: `mesma_causa_com_outra_redacao` (a regra da unidade não conhece este texto),
  `mesma_causa_sem_sinal_no_trace` (parece a unidade, mas nada observável confirma), `mecanismo_diferente`,
  `erro_comum_de_codigo`, `erro_interno_da_ferramenta`.
- `dono`: `agente`, `ferramenta_ou_harness`, `nao_deu_para_ver`.

Marque `unidade_candidata` só com evidência no caso. Na dúvida, use `nenhuma`.

# Nas duas partes · o sinal que uma regra poderia usar

Para cada categoria com **3 erros ou mais** (`leitura_g1`, `classe_barra`, `tipo_provavel` e, na Parte B, cada
`unidade_candidata` diferente de `nenhuma`), diga se existe um **sinal observável por script** na mensagem ou no código do passo e
**meça**: quantos erros da categoria o sinal pega e quantos erros **de fora da categoria**, nos 270 do balde, ele pega também. Se não
houver sinal, escreva `sem_sinal`. Descreva o sinal pelo tipo (por exemplo, "exceção final da mensagem"), sem copiar texto de caso.

# Qualidade

Em cada parte, ordene os casos pelo SHA-256 de `exec_id + agente + idx`, releia às cegas os 15 primeiros e informe quantos deram a
mesma categoria principal (`leitura_g1`, `classe_barra` ou `tipo_provavel` na Parte A; `unidade_candidata` na Parte B). Isso é o mesmo
leitor relendo, não um segundo leitor: diga isso no relatório.

# A entrega

Grave `fechar_residuo.md` nessa pasta, passe o varredor nele e só mostre o conteúdo se ele sair limpo:

```
uv run --no-sync python .github/skills/mineracao-base/scripts/varrer_pii.py analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_dbd40c0/fechar_residuo/fechar_residuo.md
```

Mostre o conteúdo na resposta, com tabelas curtas, nesta ordem:

1. os totais conferidos (34, 38, 19, 124) e o `nao_reproduz` do G2;
2. **Parte A**, para cada grupo, uma tabela por categoria principal: erros, execuções, meses, papéis, `sem_erro`, `mesma_familia`,
   `outra_familia`;
3. **Parte A**, `origem` por grupo (com as ferramentas e quantos erros cada uma tem), `reacao` por grupo e os traços do G2
   (`bloco_escapado`, `bloco_em_uma_linha`, `repete_a_classe`);
4. **Parte B**, o resumo: erros, execuções e meses por `unidade_candidata`, por `por_que_nao_casou` e por `dono`;
5. **Parte B**, uma linha por padrão, dos maiores para os menores: `padrao` (até 90 caracteres), família, erros, execuções, meses,
   papéis, `unidade_candidata` mais frequente (e em quantos erros do padrão), `por_que_nao_casou` mais frequente, `dono`, `sem_erro`;
6. a tabela dos sinais das duas partes: categoria, sinal, pega na categoria, pega fora dela;
7. as releituras (x de 15 em cada parte), quantos casos ficaram com `confianca` `baixa` e as limitações.
