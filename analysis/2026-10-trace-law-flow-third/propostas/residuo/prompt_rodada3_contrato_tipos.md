Continue a análise do contrato das ferramentas do grupo A (valor em texto) que você entregou em
`leitura_causa/relatorio_contrato.md` e `relatorio_contrato_rodada2.md`. Rode tudo da raiz do repositório, com
`uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo do repositório**; grave o que produzir em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/`
(git-ignored), o relatório em `relatorio_contrato_rodada3.md`. É uma leitura de um leitor só; as limitações vão no fim.

**Mesmos limites de saída:** só contagens, nomes de ferramenta, de papel e de tipo, mês e categorias. **Nunca** o texto de um
prompt, de uma descrição de ferramenta, de uma mensagem ou de um código, nem um valor retornado, nem identificador de
execução.

**Por que esta checagem.** Na rodada anterior, para a `calcular_correcao_monetaria` (43 erros) e mais três ferramentas
(7 erros) o seu script classificou a assinatura como "outro" e a documentação como "não declara". Mas o `smolagents` aceita
estes tipos de retorno na assinatura `def nome(...) -> X:`: `string`, `boolean`, `integer`, `number`, `image`, `audio`,
`array`, `object`, `any`, `null`. Um retorno `string` cairia em "outro" no seu script (que só tinha `object`, `str`,
`float_ou_int` e `dict`), e nesse caso o contrato **diz** que a ferramenta devolve texto. Precisamos do tipo exato para saber
se o contrato é claro (o agente foi avisado e errou: memória de reforço) ou se falta informação (o agente não tinha como
saber: memória de fato do ambiente, com uma pista de harness mais forte).

**Perguntas.** Para as 11 ferramentas do grupo A (`calcular_correcao_monetaria`, `calculadora_de_pedido`,
`validador_calculo`, `indice_correcao_monetaria`, `metadados_processo`, `corrigir_e_salvar`, `calculo_horas_extras`,
`envia_excel_para_usuario`, `corrigir_pela_selic_ajustada`, `calculo_vale_alimentacao_refeicao`, `gera_boxplot_calculo`), em
cada prompt distinto do papel CalculoTrabalhista na base 2 (e na base 1, se ela estiver no ambiente):

1. **O tipo exato na assinatura** `def nome(...) -> X:`, da lista fechada: `string`, `boolean`, `integer`, `number`,
   `image`, `audio`, `array`, `object`, `any`, `null`, ou `outro` (e, se `outro`, diga só de que forma é, sem copiar o
   texto: por exemplo "tipo composto", "sem anotação de retorno").
2. **A linha de retorno da descrição:** a descrição tem uma linha "Returns:", "Retorna" ou "Retorno"? E, se tem, qual tipo
   ela diz: `str`, `numero`, `dict`, `lista`, `nao_diz`.
3. **O vocabulário da descrição:** o texto que descreve o que a ferramenta faz chama o resultado de "valor" ou de "número"
   (sim ou não)? E existe uma contradição entre a assinatura e a linha de retorno (por exemplo, assinatura `number` e
   retorno `str`, ou o contrário)? (`coerente` / `contradiz` / `nao_se_aplica`).
4. **As ferramentas ausentes do prompt da base 2:** `corrigir_e_salvar`, `corrigir_pela_selic_ajustada` e
   `gera_boxplot_calculo` não estão no prompt do papel nesta base. Existe no prompt uma ferramenta de **nome parecido** que
   as substitua (só o nome)? Em que meses aparecem no trace como chamada?
5. **A troca entre junho e agosto:** a `calcular_correcao_monetaria` entra e a `indice_correcao_monetaria` sai. Para as
   duas: o tipo da assinatura (pergunta 1) e a linha de retorno (pergunta 2) são iguais ou diferentes?

**Entrega.** Uma tabela com uma linha por ferramenta e por base, com as colunas: ferramenta, base, está no prompt (sim ou
não), tipo na assinatura, linha de retorno (sim ou não e tipo), vocabulário (valor/número), coerência. Grave o relatório em
`leitura_causa/relatorio_contrato_rodada3.md` e responda no chat com a tabela e as limitações (o que não conseguiu ver e por
quê). Não decida nada: a decisão é do pesquisador. Não minere de novo e não toque no `casos.csv`.
