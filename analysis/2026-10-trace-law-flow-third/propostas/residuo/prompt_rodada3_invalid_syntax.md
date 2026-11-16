Continue a leitura do `invalid syntax` do balde "causa não identificada" do resíduo da base 3 (as duas rodadas anteriores
estão em `leitura_causa/relatorio_invalid_syntax.md` e `relatorio_invalid_syntax_rodada2.md`). Rode tudo da raiz do
repositório, com `uv run --no-sync`. Não instale nem atualize pacotes. **Não edite nenhum arquivo do repositório**; grave o
que produzir em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/`
(git-ignored). Reaproveite os scripts e as tabelas que você já gerou (`casos_invalid_syntax.csv`,
`invalid_syntax_medidas.csv`, `r2_q*.csv`). É uma leitura de um leitor só; as limitações vão no fim.

**Mesmos limites de saída:** só contagens, categorias, números e os nomes de uma lista fechada (abaixo). **Nunca** texto de
mensagem, trecho de código, uma palavra copiada de um caso, identificador de execução nem `step_ref`; para os casos, só o
número (1 a 75).

**Por que esta rodada.** Na rodada anterior, a categoria `marcador_de_formato` (20 casos) não era o que se esperava: **0**
cercas de código markdown e **0** rótulos do tipo `Thought:`; o marcador estava no **meio** do bloco em 20 de 20 (nunca na
1ª linha); 4 foram classificados como "tag" e **16 ficaram em "outro"**, ou seja, não sabemos o que é. Na categoria
`outra_linguagem` (20), 9 são HTML ou XML, 3 SQL e 8 "outra", e em 0 deles a 1ª linha mostra a linguagem. A regra por traços
da 1ª linha pegou só 2 dos 53 (marcador, outra linguagem e texto ou rótulo). O agente repete o mesmo marcador no passo
seguinte em 13 de 14. **A pergunta desta rodada é: o que é, de fato, o que está no meio do bloco?** Hipóteses, a testar e
não a assumir: **H-a** o agente monta um texto longo (por exemplo um relatório em HTML ou markdown) dentro de um literal de
string e as aspas ou as quebras de linha estragam o literal; **H-b** uma tag ou um trecho de marcação solto no meio do
código, fora de qualquer string; **H-c** outra coisa.

**Perguntas, todas por script e sem ler os códigos.** Use os 53 casos (marcador 20, outra linguagem 20, texto ou rótulo 13)
e, quando pedir, também os 22 restantes (deslize de Python 17, aspas ou fora do ASCII 4, cortado 1) como controle.

1. **A linha que o interpretador aponta.** A mensagem traz o número N da linha. Para a linha N do bloco, só a **classe**:
   começa com `<`; começa com `</`; contém uma tag (`<` ... `>`) no meio; começa com letra; começa com dígito; começa com
   símbolo; vazia. Para as que contêm uma tag, o **nome** da tag, só se estiver nesta lista fechada: `code`, `br`, `p`,
   `div`, `span`, `table`, `tr`, `td`, `li`, `ul`, `h1` a `h6`, `html`, `body`, `a`; senão, `outra_tag`. Conte por categoria.
2. **A linha N está dentro de um literal de string que ficou aberto?** Decida por script (módulo `tokenize` ou contagem de
   aspas e de aspas triplas, declarando o método): `string_aberta_na_linha_N` / `fora_de_string` / `nao_deu_para_decidir`.
   Conte por categoria. Esta é a pergunta que separa **H-a** de **H-b**.
3. **Há um literal longo antes da linha N?** Um literal de texto com 300 caracteres ou mais, ou com aspas triplas, antes da
   linha N: sim ou não, e a distância em linhas entre o fim dele e a linha N (faixas: 0 a 1, 2 a 5, mais de 5, sem
   literal). Conte por categoria.
4. **Onde fica a linha N no bloco:** o total de linhas do bloco e a faixa da linha N (1ª linha, 1º terço, meio, último terço,
   última linha). Conte por categoria.
5. **O bloco tem `final_answer(`?** Antes e depois da linha N. E o texto do bloco contém `<code>` ou `</code>` como texto
   (sim ou não)? Conte por categoria.
6. **Os 13 que repetem o mesmo marcador no passo seguinte:** a linha N do passo seguinte tem a mesma classe da pergunta 1 e o
   mesmo resultado da pergunta 2? (sim ou não, contagem). E o passo seguinte tem a mesma estrutura do bloco (mesmo
   número de linhas, ou diferença de até 10%)?
7. **Os que ainda ficam sem nome:** reclassifique os 16 `marcador` "outro" e as 8 `outra_linguagem` "outra" pelas classes das
   perguntas 1 a 3 (não por leitura) e diga quantos continuam sem classe.
8. **Conclusão por hipótese.** Uma linha para H-a, H-b e H-c: "a medida apoia", "contradiz" ou "inconclusiva", com a contagem
   que sustenta, e uma frase: "o que está no meio do bloco é principalmente …". Diga também se a regra de decisão "a linha N
   está dentro de uma string que ficou aberta" separaria os 53 dos 22 de controle, e com que contagem. Não decida o destino:
   a decisão é do pesquisador.

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio_invalid_syntax_rodada3.md` e responda no chat com uma
tabela por pergunta e as limitações (o que não conseguiu ver e por quê). Não minere de novo e não toque no `casos.csv`.
