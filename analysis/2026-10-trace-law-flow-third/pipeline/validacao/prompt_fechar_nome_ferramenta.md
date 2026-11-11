# Prompt temporário: fechar as dúvidas do grupo "nome de ferramenta usado como variável" (resíduo da base 3, b3 #5)

Arquivo provisório. Ele sai do repositório quando o Ajuste 37 for verificado. Para usar: copie o bloco abaixo inteiro
para o agente do ambiente da base e traga de volta só o bloco de resposta.

**Versão 2 (11/11).** A versão 1 pedia o prompt de sistema na base 3, mas a base 3 não exporta o prompt de sistema:
no adaptador, o `sysprompt` fica `nao_exportado`. Por isso, as perguntas sobre o prompt vão para a base 2, que tem o
trace completo, e a base 3 responde só pelo erro, pelo código e pela janela de depois.

O que já foi conferido fora do ambiente, na base 1 (trace completo, 16 papéis com prompt):
- 0 ocorrências da mensagem;
- `final_answer` é declarado em todo prompt; `resposta_final` é declarado no RespostaBacen; `calculo_horas_extras` e
  `calculo_enquadramento` são declarados no CalculoTrabalhista; `exp` não é declarado no JoogleAnalytics (1 execução);
- nenhum prompt atribui `final_answer =`;
- o prompt padrão já traz a regra "não dê a uma variável o mesmo nome de uma ferramenta, por exemplo não chame uma
  variável de 'final_answer'" (11 de 11 execuções do OBFCivel);
- o OBFCivel tem uma ferramenta `get_final_answer_schema` e a instrução de que a resposta final segue esse esquema.

```text
Tarefa: fechar as dúvidas do grupo "nome de ferramenta usado como variável" do resíduo da base 3. Leia o trace da
base 3 (só erros, com a janela de antes e de depois) e o da base 2 (trace completo, com o prompt de sistema). É só
leitura e contagem. Devolva apenas o bloco de resposta do fim.

Regras (obrigatórias):
- Não edite nenhum arquivo do repositório, nem os da lista do hash da base 3 nem o manifesto do kit. Não faça commit.
- Escreva qualquer código auxiliar numa pasta temporária fora do repositório.
- Sigilo (.github/skills/mineracao-base/referencias/sigilo.md): para fora vão só contagens, nomes de papel, nomes de
  ferramenta, meses, versões do agente e hashes curtos. Nada de exec_id, id de agente, mensagem de erro inteira, texto
  de documento ou dado de cliente. Do prompt de sistema, você pode citar no máximo uma linha de instrução genérica, sem
  dado de cliente.
- O erro do grupo é toda mensagem que casa com a regex
  Cannot assign to name '([^']*)': doing this would erase the existing tool
- A base 3 NÃO tem prompt de sistema. Leia o parquet pelo TRACE de
  analysis/2026-10-trace-law-flow-third/pipeline/base_pipeline.py. As colunas estão no contrato de
  analysis/adaptador_trace.py: error_message, error_code_action, prev_code_action, next_code_action, next_error_type,
  next_is_final_answer, next2_*, papel, mes_execucao, cod_vers_aget.
- A base 2 tem trace completo. Leia pelo TRACE de analysis/2026-09-trace-law-flow-second/pipeline/base_pipeline.py.
  Lá o prompt de sistema de um papel é a PRIMEIRA mensagem de model_input_messages do primeiro ActionStep. Use como
  modelo analysis/2026-09-trace-law-flow-second/scripts/contar_ferramentas_prompt_base2.py.

Perguntas, base 3:
B3-1. População. Conte a regex em TODOS os erros da base 3: erros, execuções, meses e (papel, nome). O total bate com
      os 49 do resíduo? Conte também as mensagens com "Cannot assign" que NÃO casam com a regex, e diga a forma delas
      em poucas palavras.
B3-2. A linha que falhou (em error_code_action). Para os erros com nome final_answer ou resposta_final, conte quantos:
      (a) atribuem um dict literal (`= {`); (b) atribuem outra coisa;
      (c) têm `get_final_answer_schema` no mesmo bloco ou em prev_code_action.
B3-3. Versão do agente × erro (OBFCivel). Considere todas as execuções da base 3 com o papel OBFCivel, lembrando que a
      base 3 só tem execuções com algum erro. Por cod_vers_aget: execuções, execuções com o erro, primeiro mês e último
      mês. Também por mês: execuções e execuções com o erro.
B3-4. Recuperação. Para cada um dos erros do grupo, conte no step seguinte:
      (a) não existe; (b) next_error_type preenchido, e de que tipo; (c) sem erro; (d) next_code_action chama `<nome>(`;
      (e) next_is_final_answer verdadeiro.
B3-5. As linhas com a forma `<nome> = <nome>(`: de que nome e de que papel são?

Perguntas, base 2:
B2-1. Conte a regex em todos os erros da base 2: erros, execuções, meses e (papel, nome). Se forem 0, diga isso.
B2-2. Para os papéis OBFCivel, RespostaBacen, CalculoTrabalhista e JoogleAnalytics, por papel: execuções, meses
      cobertos, versões distintas do prompt (sha256, 8 caracteres). Conte também quantas execuções têm no prompt:
      (a) `def <nome>(` para cada um dos nomes final_answer, resposta_final, calculo_horas_extras,
          calculo_enquadramento e exp;
      (b) a regra de não dar a uma variável o nome de uma ferramenta (procure "same name as a tool");
      (c) `get_final_answer_schema`;
      (d) alguma atribuição `final_answer\s*=(?!=)`.
B2-3. Se o smolagents estiver instalado no ambiente, rode
      python -c "import smolagents; from smolagents.local_python_executor import BASE_PYTHON_TOOLS as B; print(smolagents.__version__, 'exp' in B)"
      e devolva a saída. Se não estiver instalado, diga isso.

Resposta (só este bloco, em markdown):
## Grupo nome de ferramenta, fechamento (v2)
B3-1: ... | "Cannot assign" fora da regex: ...
B3-2: tabela nome | dict literal | outra coisa | com get_final_answer_schema
B3-3: tabela versão | execuções | com o erro | primeiro mês | último mês ; tabela mês | execuções | com o erro
B3-4: tabela desfecho | contagem
B3-5: tabela nome | papel | contagem
B2-1: ...
B2-2: tabela papel | execuções | meses | versões | def por nome | regra "same name" | get_final_answer_schema | atribui final_answer
B2-3: saída, ou "não instalado"
Código usado: as funções essenciais que você escreveu (sem dados).
Limitações: o que você não conseguiu medir e por quê.
```
