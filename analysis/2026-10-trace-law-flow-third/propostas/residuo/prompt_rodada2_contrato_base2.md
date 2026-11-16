Continue a análise do contrato das ferramentas do grupo A (valor em texto) que você entregou em
`leitura_causa/relatorio_contrato.md`, e a replicação do `invalid syntax` na base 2. Rode tudo da raiz do repositório, com
`uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo do repositório**; grave o que produzir em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/`
(git-ignored), o relatório em `relatorio_contrato_rodada2.md`. É uma leitura de um leitor só; as limitações vão no fim.

**Mesmos limites de saída:** só contagens, nomes de papel, de ferramenta e de módulo, mês, categorias e números. **Nunca**
o texto de um prompt, de uma descrição de ferramenta, de uma mensagem ou de um código, nem um valor retornado por
ferramenta, nem identificador de execução.

**Por que esta rodada.** A decisão sobre o destino do grupo A (memória ou harness) está fraca em quatro pontos: o formato
do retorno da `calcular_correcao_monetaria` não bate entre a base 2 ("string com ponto" em 16 de 16 chamadas) e a base 3
(23 de 43 erros com símbolo de moeda); não sabemos se a mistura de formatos é por chamada ou por campo; a base 3 não tem a
taxa de erro por chamada; e o agente disse "sem mudança em agosto" só pela declaração `Returns:`, enquanto o hash do bloco
de ferramentas mudou (fev para jun, jun para ago).

**Perguntas.**

1. **Formato do retorno de `calcular_correcao_monetaria`** (base 2, chamadas bem-sucedidas). Classifique cada retorno por
   regras que você declara, **nesta ordem**: (i) tem "R$"; (ii) vírgula como separador decimal; (iii) ponto de milhar e
   vírgula decimal; (iv) só dígitos e um ponto decimal; (v) dict ou lista; (vi) número (int ou float, não texto); (vii)
   outra. Conte cada uma por mês. Diga a ordem exata das regras e se uma mesma chamada cairia em mais de uma.
2. **Estabilidade.** Para `calculadora_de_pedido`, `validador_calculo` e `metadados_processo`, a mesma classificação por
   mês; se o retorno é um texto com estrutura, diga só se a **estrutura** é igual ou varia entre as chamadas.
3. **Taxa de erro por chamada.** Para cada ferramenta do grupo A, por mês: quantas chamadas há na base 2 e em quantas o
   passo seguinte do mesmo papel e da mesma execução tem um erro de "valor em texto numa conta" (mensagens com
   "unsupported operand" e `'str'`, "can only concatenate str", "__round__", "Unknown format code" e `'str'`). Dê a taxa.
4. **O que o agente faz com o retorno**, nas chamadas sem erro, no passo seguinte: converte (float, int, replace), usa
   direto numa conta, só imprime ou repassa a outra ferramenta. Contagem por ferramenta.
5. **Mudança do bloco de ferramentas** entre os meses da base 2 (jan e fev, jun, ago): quais ferramentas foram
   acrescentadas ou removidas (só os nomes) e, para as 11 do grupo A, se a descrição mudou (sim ou não, sem texto).
6. **Cobertura.** Quais meses a base 2 tem para qualquer papel e quantas execuções por mês. Março e julho existem?
7. **Replicação do `invalid syntax` na base 2** (erros "Code parsing failed ... invalid syntax"): quantos há, por papel e
   mês. Para o código executado, a 1ª linha do bloco: começa com cerca markdown (três crases), com rótulo (uma ou duas
   palavras e dois-pontos), com palavra SQL (SELECT, INSERT, UPDATE, DELETE, WITH, CREATE) ou com Python? O trace guarda a
   resposta crua do modelo, antes de o parser extrair o `<code>`? Se sim, nesses erros a resposta crua traz o marcador
   **dentro** do `<code>`? (contagem). Se não guarda, diga qual coluna tem o código extraído.

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio_contrato_rodada2.md` e responda no chat com uma tabela
por pergunta e as limitações (o que não conseguiu ver e por quê). Não decida nada: a decisão é do pesquisador. Não minere
de novo e não toque no `casos.csv`.
