Continue a leitura do `invalid syntax` do balde "causa não identificada" do resíduo da base 3 (a que você entregou em
`leitura_causa/relatorio_invalid_syntax.md`). Rode tudo da raiz do repositório, com `uv run --no-sync`. Não instale nem
atualize pacotes. **Não edite nenhum arquivo do repositório**; grave o que produzir em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_c2e5e8b/leitura_causa/`
(git-ignored). Reaproveite os scripts e as tabelas que você já gerou (`casos_invalid_syntax.csv`,
`invalid_syntax_medidas.csv`, `invalid_syntax_categorias.csv`). É uma leitura de um leitor só; as limitações vão no fim.

**Mesmos limites de saída:** só contagens, categorias e números. **Nunca** texto de mensagem, trecho de código, uma
palavra copiada de um caso, identificador de execução nem `step_ref`; para os casos, só o número (1 a 75).

**Por que esta rodada.** A primeira leitura refutou a hipótese de que a regra de "texto solto" deixava passar o texto em
português, e mostrou quatro categorias: outra linguagem (20), marcador de formato (20), deslize de Python (17) e texto ou
rótulo (13), mais 5 pequenas. A proposta é juntar as três primeiras (até 53 erros, 57% dos tokens) numa unidade existente
("o bloco de código contém só Python"), mas faltam três coisas: saber **qual** marcador e **qual** linguagem, conferir as
categorias por um método que não seja a leitura, e medir os falsos positivos de uma regra por traços dentro dos próprios 75.

**Perguntas.**

1. **Cruzamento por script.** As 75: categoria lida × (erro na 1ª linha do bloco: sim ou não; bloco com marcador de
   formato: sim ou não; termina no meio: sim ou não).
2. **Os 20 `marcador_de_formato`:** o tipo do marcador (cerca markdown; rótulo Thought, Observation, Code ou Resposta; tag;
   outro) e onde está (1ª linha, meio, fim do bloco).
3. **Os 20 `outra_linguagem`:** qual linguagem (SQL, JSON, shell, HTML ou XML, tabela markdown, LaTeX, outra) e se a 1ª
   linha do bloco já mostra isso.
4. **"Termina no meio" = 20 contra "código cortado" = 1:** explique a diferença e diga de que categoria são os 20.
5. **REGRA v0, por script e sem ler.** O bloco "não é Python" se a 1ª linha começa com cerca markdown, ou com rótulo (uma ou
   duas palavras seguidas de dois-pontos), ou com palavra SQL (SELECT, INSERT, UPDATE, DELETE, WITH, CREATE). Aplique aos 75
   e diga: dos 53 (marcador, outra linguagem e texto ou rótulo), quantos ela pega; dos 22 restantes (deslize de Python,
   aspas e cortado), quantos ela pega (falso positivo interno).
6. **Os 14 `marcador_de_formato` que repetem a mesma família:** o marcador do passo seguinte é o mesmo? (sim ou não,
   contagem).

**Entrega.** Grave o relatório completo em `leitura_causa/relatorio_invalid_syntax_rodada2.md` e responda no chat com uma
tabela por pergunta e as limitações (o que não conseguiu ver e por quê). Não decida nada: a decisão é do pesquisador. Não
minere de novo e não toque no `casos.csv`.
