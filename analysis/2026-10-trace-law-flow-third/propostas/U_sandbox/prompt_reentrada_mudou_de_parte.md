Investigue, sem alterar nenhum arquivo, por que 5 erros da unidade `U_sandbox` mudaram de parte na re-entrada. Rode
tudo da raiz do repositório, com `uv run --no-sync`. Não instale nem atualize pacotes.

**Contexto.**
- Rodei `analysis/2026-10-trace-law-flow-third/pipeline/especificas/reentrada.py --todas` na rodada
  `analysis/2026-10-trace-law-flow-third/pipeline/resultados/observada_c2e5e8b31f297d21/`.
- O resultado está em `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/reentrada/U_sandbox/delta.csv`.
  Os 5 erros com `situacao == mudou_de_parte` tinham `memoria_id` na foto e agora não têm nenhum.
- A foto é a mineração que fechou o catálogo: `analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/U_sandbox/`.
  Ela contém `erros_lidos.csv` (com `step_ref`, `tipo`, `nome` e `memoria_id`) e `passo1_rodada.json` (com a rodada
  `99e032ad3a8528d8`).
- A regra é o `medir` de `analysis/2026-10-trace-law-flow-third/pipeline/especificas/mineracao_U_sandbox.py`. Ele lê a
  mensagem pela função `extrair`, e só quando o estado da mensagem está em `ESTADOS_INTEGROS`.
- Esse script não muda desde 20/10, antes da foto, e não importa o pipeline.

**O que fazer.**
1. Para os 5, pelo `step_ref`, compare a foto com agora:
   - a foto: o `tipo`, o `nome` e o `memoria_id` do `erros_lidos.csv`;
   - agora: o `tipo`, o `nome` e o estado da mensagem (`err_msg_estado`) na rodada nova. Leia a rodada nova com
     `carregar_rodada` e `ler_agora` do próprio `reentrada.py`, com o módulo dado por `parte_especifica("U_sandbox")`.
2. Diga qual das hipóteses explica cada um dos 5:
   - (a) hoje o estado da mensagem não é íntegro;
   - (b) o texto da mensagem é diferente para o mesmo `step_ref`. Compare só o tamanho e o hash do texto, nunca o texto;
   - (c) a foto foi gravada por outra versão do script. Compare o hash do `mineracao_U_sandbox.py` registrado nos
     arquivos da foto (manifesto da mineração ou `passo1_rodada.json`) com o hash do arquivo atual;
   - (d) outra causa, descrita.
3. Rode a mesma comparação nos 1.095 que ficaram com a mesma parte. Pela contagem por estado e versão, eles servem de
   controle.

**O que pode sair na resposta:** contagens, ids de memória, papel, mês, `tipo`, `nome` (módulo ou função), estado da
mensagem, hashes e tamanhos.

**O que não pode sair:** texto de mensagem, identificador de execução ou `step_ref`.

**Não faça:**
- não minere de novo;
- não grave nada dentro de `resultados/mineracao/U_sandbox/`;
- não edite script nem catálogo.

Responda com uma tabela dos 5 (memória antes, papel, mês, tipo/nome antes → agora, estado agora, hipótese) e com a
conclusão em uma frase.
