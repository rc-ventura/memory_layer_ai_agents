Você é o leitor de **todos** os erros do grupo "infra / LLM" do resíduo da base 3 (erros de rede, de API, de recusa do
LLM e de ferramenta que nenhuma regra conhece; procedimento do resíduo, pergunta R2: de quem é a falha). As contagens já
mostraram que os erros do grupo aconteceram dentro da chamada de uma ferramenta, e uma primeira leitura fechou 6 casos.
Agora a leitura é de todos, em categorias fechadas, para decidir o destino de cada grupo. **Não edite nenhum arquivo do
repositório** (só grave o arquivo do passo 4), não instale nem atualize pacotes e use `uv run --no-sync`. Rode tudo **da
raiz do repositório**, em Git Bash, depois de `export PYTHONIOENCODING=utf-8`.

**Passo 1 · Uma contagem antes de ler (sem caso).** Rode exatamente:

```
B3=analysis/2026-10-trace-law-flow-third
C=$B3/pipeline/resultados/mineracao/residuo/residuo_13b0d02/casos.csv
uv run --no-sync python -c "
import pandas as pd, re
C = pd.read_csv('$C'); m = C.mensagem.fillna('').astype(str)
b = m[m.str.contains(r'\bBadRequestError\b|ContentPolicyViolation')]
print('BadRequestError/ContentPolicyViolation:', len(b))
for nome, rx in [('content_policy', r'(?i)content.?policy|content_filter|ResponsibleAI'),
                 ('contexto', r'(?i)context.?length|maximum context|too many tokens|max_tokens'),
                 ('parametro', r'(?i)invalid.?(param|request|value)|unsupported')]:
    print(' ', nome, int(b.str.contains(rx).sum()))
"
```

Ele imprime só contagens. Guarde a saída para o passo 5.

**Passo 2 · Montar os casos (todos).** Rode exatamente:

```
ME=.github/skills/mineracao-base/scripts/montar_evidencia.py
T=mineracao/residuo/residuo_13b0d02/casos_infra.csv
R="contar_infra_residuo.py --casos $C"
for g in rede_api politica_llm ferramenta_recuperavel ferramenta_conteudo; do
  uv run --no-sync python $ME $B3 --nome infra_todos_$g --de $T --onde grupo=$g --n 100 \
    --afirmacao "grupo $g do resíduo: de quem é a falha e o que o agente fez depois" --reproduzir "$R"
done
```

Cada um termina em `crus conferidos: N de N` (o N é o tamanho do grupo). Se algum não fechar, pare e devolva só a saída
(ou o erro) dos quatro comandos.

**Passo 3 · Ler.** Cada caso é um `.md` em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/infra_todos_<grupo>/derivados/` (a janela do erro:
o passo anterior, o passo do erro com o código e a mensagem, e os dois seguintes). Para **cada caso**, responda duas
colunas: `resposta` (a pergunta do grupo) e `depois` (a mesma para todos).

*`resposta`, por grupo:*
- **`rede_api`** — o que a chamada que falhou estava chamando?
  - `llm`: um modelo (o código ou a mensagem mostram chamada a orquestrador, subagente, modelo, completions);
  - `api_interna`: um serviço que não é modelo (busca de documento, pasta, sistema do processo);
  - `indeterminado:<uma palavra>`.
- **`politica_llm`** — por que o provedor recusou?
  - `politica_conteudo`: a mensagem fala em política de conteúdo, filtro de conteúdo ou conteúdo bloqueado;
  - `contexto_grande`: tamanho de contexto ou de tokens;
  - `parametro_invalido`: parâmetro ou requisição inválida;
  - `outra:<uma palavra>`.
  Some a isso, depois de `;`, se a linha que falhou chama o orquestrador ou um subagente: `;aninhada` ou `;direta`
  (ex.: `politica_conteudo;aninhada`).
- **`ferramenta_recuperavel`** e **`ferramenta_conteudo`** — o argumento que o agente passou à ferramenta:
  - `argumento_ok`: veio de uma variável, de uma observação anterior ou da tarefa; a ferramenta é que falhou;
  - `argumento_errado`: digitado diferente do que aparece antes, inventado ou de outro campo;
  - `indeterminado:<uma palavra>`;
  - (só no `ferramenta_recuperavel`) `traceback`: a mensagem mostra a ferramenta quebrando por dentro (Traceback).

*`depois` (todos os casos), nos dois passos seguintes:*
- `repetiu_igual`: chamou a mesma ferramenta com o mesmo argumento e falhou de novo;
- `repetiu_e_deu_certo`: chamou de novo (igual ou quase) e funcionou;
- `mudou_caminho`: outra ferramenta, outro argumento ou outra abordagem;
- `encerrou`: deu `final_answer` ou a execução acabou;
- `indeterminado:<uma palavra>`.

**Passo 4 · Gravar.** Grave
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/leitura_infra_residuo_todos.csv` com as colunas
`exec_id,role,idx,grupo,resposta,depois,onde_no_trace`: uma linha por caso, de todos os grupos. Em `onde_no_trace` vão só
nomes de campo (por exemplo `error_code_action`, `error_model_output`, `prev_observations`). **Não grave recorte de caso,
URL, número de processo, nome nem conteúdo de documento em nenhum arquivo.**

**Passo 5 · Contar e responder.** Rode exatamente:

```
uv run --no-sync python -c "
import pandas as pd
L = pd.read_csv('$B3/pipeline/resultados/evidencia/leitura_infra_residuo_todos.csv')
print('casos lidos:', len(L), '| execuções:', L.exec_id.nunique())
for g, d in L.groupby('grupo'):
    print(f'\n== {g}: {len(d)} casos, {d.exec_id.nunique()} execuções')
    print('  resposta:', d.resposta.value_counts().to_dict())
    print('  depois:  ', d.depois.value_counts().to_dict())
    print('  papéis:  ', d.role.value_counts().to_dict())
"
```

Devolva **só** isto, sem nenhum trecho de código, identificador, URL, número de processo, nome ou conteúdo de documento:
1. a saída do passo 1;
2. a última linha de cada um dos quatro comandos do passo 2 (`crus conferidos: N de N`);
3. a saída do passo 5;
4. em no máximo três linhas, o que você achou estranho (uma categoria que não serviu, um caso que não coube), em
   palavras gerais.
