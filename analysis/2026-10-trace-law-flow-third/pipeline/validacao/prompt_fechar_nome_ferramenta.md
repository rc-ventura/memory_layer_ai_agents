# Prompt temporário: fechar as dúvidas do grupo "nome de ferramenta usado como variável" (resíduo da base 3, b3 #5)

Arquivo provisório. Ele sai do repositório quando o Ajuste 37 for verificado. Para usar: copie o bloco abaixo inteiro
para o agente do ambiente da base e traga de volta só o bloco de resposta. A base 1 já foi conferida fora do ambiente:
o trace inteiro tem 0 ocorrências da mensagem e 0 variantes de "Cannot assign".

```text
Tarefa: fechar as dúvidas do grupo "nome de ferramenta usado como variável" do resíduo da base 3, lendo os traces das
bases 2 e 3. É só leitura e contagem. Devolva apenas o bloco de resposta do fim.

Regras (obrigatórias):
- Não edite nenhum arquivo do repositório, nem os da lista do hash da base 3 nem o manifesto do kit. Não faça commit.
- Escreva qualquer código auxiliar numa pasta temporária fora do repositório.
- Sigilo (.github/skills/mineracao-base/referencias/sigilo.md): para fora vão só contagens, nomes de papel, nomes de
  ferramenta, meses e hashes curtos. Nada de exec_id, id de agente, mensagem de erro inteira, texto de documento ou
  dado de cliente. Do prompt de sistema, você pode citar no máximo uma linha de código ou de instrução genérica, sem
  dado de cliente.
- Localize cada base como manda .github/skills/mineracao-base: o BASE_ID e o TRACE do base_pipeline.py de cada pasta
  de análise. A base 3 é analysis/2026-10-trace-law-flow-third. A base 2 é a pasta cujo BASE_ID é a base 2 neste ambiente.
- O erro do grupo é toda mensagem que casa com a regex
  Cannot assign to name '([^']*)': doing this would erase the existing tool
  O grupo 1 em si está em
  analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/residuo_7f1469/casos_nome_ferramenta.csv
  (49 erros, com as colunas exec_id, agente, role, idx, mes, nome e forma).
- O "prompt de sistema" de um step é a PRIMEIRA mensagem de model_input_messages, como no base_pipeline.py da base 3
  (variável sysp). A "tarefa" é a segunda mensagem.

Perguntas:
P1. População. Conte a regex em TODOS os erros de cada base (2 e 3), não só no resíduo. Para cada base, dê: erros,
    execuções, meses e contagem por (papel, nome). Na base 3, o total bate com os 49? Conte também as mensagens que
    contêm "Cannot assign" e NÃO casam com a regex, e diga a forma delas em poucas palavras.
P2. Ferramenta declarada? Para cada (papel, nome) dos 49, no prompt de sistema do step do erro: existe `def <nome>(`?
    Dê "sim N / não N" por par.
P3. Função embutida do interpretador? Se o smolagents estiver instalado no ambiente, rode
    python -c "import smolagents; from smolagents.local_python_executor import BASE_PYTHON_TOOLS as B; print(smolagents.__version__, [n for n in ['final_answer','resposta_final','calculo_horas_extras','calculo_enquadramento','exp'] if n in B])"
    e devolva a saída. Se não estiver instalado, diga isso.
P4. O prompt induz? Para os papéis OBFCivel e RespostaBacen, conte em quantos dos steps com o erro o prompt de sistema,
    e separadamente a tarefa, contém `final_answer\s*=(?!=)` ou `resposta_final\s*=(?!=)`, ou uma instrução para
    guardar a resposta numa variável com esse nome. Se contém, descreva o tipo em uma frase (por exemplo: "exemplo de
    código que atribui final_answer = {...}"). Se o OBFCivel tiver uma ferramenta própria chamada final_answer além da
    padrão, diga isso.
P5. Versão do prompt × erro (OBFCivel). Considere todas as execuções da base 3 que têm o papel OBFCivel. A base 3 só
    tem execuções com algum erro: declare isso. Para cada mês, dê: execuções, execuções com o erro e o número de
    versões distintas do prompt de sistema (sha256 dos 8 primeiros caracteres). Depois, por versão: execuções,
    execuções com o erro e o mês da primeira e da última aparição.
P6. Recuperação. Para cada um dos 49, olhe o step seguinte do mesmo papel na mesma execução e conte:
    (a) não existe; (b) teve erro, e de que tipo (o nome do erro, não a mensagem); (c) sem erro;
    (d) o código chama a ferramenta com o mesmo nome (`<nome>(`). Conte também quantos dos 49 papéis chegaram a um
    step com is_final_answer.
P7. As 4 linhas da forma "resultado_com_o_nome": de que nome e de que papel são?

Resposta (só este bloco, em markdown):
## Grupo nome de ferramenta, fechamento
P1 base 3: ... | base 2: ... | "Cannot assign" fora da regex: ...
P2: tabela papel | nome | def declarado sim | não
P3: saída do comando, ou "não instalado"
P4: tabela papel | steps | no sistema | na tarefa | tipo da instrução
P5: tabela mês | execuções OBFCivel | com o erro | versões ; tabela versão | execuções | com o erro | primeiro mês | último mês
P6: tabela desfecho | contagem
P7: tabela nome | papel | contagem
Código usado: as funções essenciais que você escreveu (sem dados).
Limitações: o que você não conseguiu medir e por quê.
```
