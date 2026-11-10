Você é o leitor de 4 casos do resíduo da base 3, do grupo "infra / LLM" (erros de rede, de API, de política de conteúdo
do LLM e de ferramenta que nenhuma regra conhece; procedimento do resíduo, pergunta R2: de quem é a falha). As
contagens por regra já mostraram que os 54 erros do grupo aconteceram dentro da chamada de uma ferramenta. Faltam duas
dúvidas, que só a leitura resolve. **Não edite nenhum arquivo do repositório** (só grave o arquivo do passo 4), não
instale nem atualize pacotes e use `uv run --no-sync`. Rode tudo **da raiz do repositório**, em Git Bash, depois de
`export PYTHONIOENCODING=utf-8`.

**Passo 1 · Montar os casos.** Rode exatamente:

```
B3=analysis/2026-10-trace-law-flow-third
ME=.github/skills/mineracao-base/scripts/montar_evidencia.py
T=mineracao/residuo/residuo_13b0d02/casos_infra.csv
R="contar_infra_residuo.py --casos $B3/pipeline/resultados/mineracao/residuo/residuo_13b0d02/casos.csv"
uv run --no-sync python $ME $B3 --nome inf_recup --de $T --onde grupo=ferramenta_recuperavel --afirmacao "RecoverableToolError: falha da ferramenta ou argumento errado do agente?" --reproduzir "$R"
uv run --no-sync python $ME $B3 --nome inf_final --de $T --onde grupo=politica_llm --onde funcao_na_linha=final_answer --afirmacao "o final_answer do politica_llm é uma chamada aninhada ao orquestrador?" --reproduzir "$R"
```

O primeiro tem de terminar em `crus conferidos: 5 de 5` e o segundo em `crus conferidos: 1 de 1`. Se não, pare e devolva
só a saída (ou o erro) dos dois comandos.

**Passo 2 · Os casos.** Cada caso é um arquivo `.md` (a janela do erro: passo anterior, passo do erro com o código e a
mensagem, e os dois seguintes), em:
- `analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/inf_recup/derivados/` (5 arquivos);
- `analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/inf_final/derivados/` (1 arquivo).

Se precisar ver mais de um caso, `uv run --no-sync python analysis/2026-10-trace-law-flow-third/pipeline/drill_down.py
caso <exec_id> <papel> <idx>` mostra a mesma janela (o nome do arquivo é `<exec_id>__<papel>__<idx>.md`).

**Passo 3 · Ler.**

*No `inf_recup`:* dos 5 casos, **leia só os 3 cuja mensagem do passo do erro diz "Nenhum documento do tipo inicial
encontrado…"**. Os outros 2 ("Ocorreu um erro ao buscar as informações da pasta do processo… Traceback") já estão
decididos (a ferramenta quebrou por dentro): registre-os como `nao_lido_traceback`. Para cada um dos 3, olhe a chamada à
ferramenta no código do passo do erro (`get_docs_calculo_proprios(...)` ou `get_infos_pasta_calculo_proprios(...)`) e
responda **de onde veio o processo (ou a pasta) que o agente passou**:
- `argumento_ok`: o valor veio de uma variável ou de uma observação anterior (aparece no passo anterior), ou é o processo
  da tarefa; a ferramenta é que não achou o documento;
- `argumento_errado`: o valor foi digitado diferente do que aparece antes, foi inventado, ou é de outro campo;
- `indeterminado`: a janela não mostra de onde o valor veio (diga em uma palavra o que faltou).

*No `inf_final` (1 caso):* a linha que falhou chama o orquestrador dentro do `final_answer`, algo como
`final_answer(orquestrador_papel(...))`?
- `aninhada`: chama;
- `outra`: não chama (diga em uma palavra o que é).

**Passo 4 · Gravar.** Grave `analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/leitura_infra_residuo.csv`
com as colunas `exec_id,role,idx,grupo,resposta,onde_no_trace`: uma linha por caso dos 6 (os 2 do Traceback com
`nao_lido_traceback`). Em `onde_no_trace` vão só nomes de campo (por exemplo `error_code_action`, `prev_observations`).
Não grave recorte de caso em nenhum arquivo.

**Passo 5 · Responder.** Devolva só isto, sem nenhum trecho de código, número de processo, nome ou conteúdo de documento:

```
inf_recup: crus <N> de 5
  <8 primeiros caracteres do exec_id> · Nenhum documento · <argumento_ok | argumento_errado | indeterminado: …> · <onde_no_trace>
  (as 3 linhas)
  <8 primeiros caracteres do exec_id> · Traceback · nao_lido_traceback
  (as 2 linhas)
inf_final: crus <N> de 1
  <8 primeiros caracteres do exec_id> · <aninhada | outra: …> · <onde_no_trace>
```
