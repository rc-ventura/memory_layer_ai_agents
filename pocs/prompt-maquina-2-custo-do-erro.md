# Prompt para a máquina 2 — custo do passo com erro e a incidência de todas as unidades

> **Para quê:** fechar o que a primeira volumetria não mediu: (1) os **tokens e a duração do passo que errou**, por memória
> e papel (é a economia `s` da conta de compensação); (2) a **incidência de todas as unidades da rodada**, mineradas ou não
> (inclui o retorno que chega como texto), lida do `triagem_por_papel.csv` que a rodada já publica, sem precisar de perfil.
> Só contagens, tokens e segundos saem.
> **Como usar:** cole **tudo abaixo da linha** no agente da máquina 2 e traga a resposta inteira.
> **Descartável:** apague este arquivo quando o resultado voltar. Relatório que explica a conta:
> [`relatorio-volumetria-fase-1.md`](relatorio-volumetria-fase-1.md).

---

Você vai rodar **um script que já existe e já foi testado**, e me devolver a saída. **Não é uma tarefa de análise, de código ou de interpretação.** O script de volumetria do sandbox já foi rodado antes; **não o rode de novo**. Este pedido é outro: o custo do passo com erro .

## Regras (valem para tudo)

1. **Não edite nenhum arquivo do repositório**, não crie script e não corrija nada. Se algo falhar, **pare, copie a mensagem de erro exatamente como saiu e me devolva**. Não tente consertar.
2. **Não calcule nem interprete números.** Copie a saída do script como ela saiu.
3. **Nada de identificador nem de texto de caso na resposta:** nenhum `exec_id`, nenhum `step_ref`, nenhum trecho de código, de mensagem de erro ou de input de usuário. O script só imprime nomes de memória, de unidade, de papel, meses, contagens, tokens e segundos. Se aparecer qualquer outra coisa, **não cole e me avise**.
4. Rode da **raiz do repositório**, uma linha de cada vez.

## Passo 1 — trazer só os scripts, sem trocar de branch

```
git fetch origin 2026-11-11-pocs-experimentos-design
git checkout origin/2026-11-11-pocs-experimentos-design -- analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_memorias.py
```

A segunda linha copia **dois arquivos**; a branch em que você está não muda. Se qualquer linha falhar, pare e me devolva a mensagem.

## Passo 2 — o custo do passo com erro, por memória e papel

```
uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py --casos-sandbox
```

O script procura sozinho a rodada mais recente que tem o perfil do sandbox e imprime o nome dela. Se der `nenhuma rodada em resultados/ tem perfis/U_sandbox/casos.csv`: **não gere o perfil.** Me devolva **só os caminhos que achar**:
```
git ls-files --others --ignored --exclude-standard -- analysis/2026-10-trace-law-flow-third | findstr "perfis"
```
Não rode a mineração por conta própria.

## Passo 3 — a incidência de todas as unidades (qualquer uma, minerada ou não)

```
uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py --rodada
```

O script usa a rodada mais recente que tenha o `triagem_por_papel.csv` e imprime o nome dela. Se der `nenhuma rodada em resultados/ tem triagem_por_papel.csv`: **não gere nada.** Me devolva só os nomes das pastas dentro de `analysis/2026-10-trace-law-flow-third/pipeline/resultados` e, para cada uma, os nomes dos arquivos na raiz dela.

## Passo 4 — o que me devolver

1. A **saída inteira** dos comandos dos passos 2 e 3, colada como texto (inclui as linhas `AVISO`, se houver).
2. O conteúdo dos dois arquivos que os scripts escreveram (só números): `custo_do_erro_por_memoria.csv` e `volumetria_por_unidade_e_papel.csv`.
3. Se você consegue ver, **sem abrir nenhum conteúdo de caso**: o **modelo** e a **versão do prompt** que cada um destes quatro papéis usa **hoje** no código do agente (só os nomes, por exemplo `gpt-5.2` e a versão): `ContestacaoCivel`, `RespostaBacen`, `JoogleAnalytics` e `CalculoTrabalhista`. Se não conseguir, escreva "não vi".
4. **A data da execução mais recente** que existe hoje no banco de traces de cada um desses quatro papéis (só a data, e quantas execuções cada um teve nos **últimos 30 dias**). Se não houver acesso, escreva "sem acesso".
