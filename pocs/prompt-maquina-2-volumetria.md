# Prompt para a máquina 2 — volumetria das memórias por papel e mês

> **Para quê:** saber, para cada memória (as 16 do catálogo do sandbox) e cada papel, **quantas execuções tiveram o erro**
> e quantas execuções o papel teve. É o que decide quantas execuções reais a fase 1 precisa
> ([`plano-fase-1-a-memoria-mitiga-o-erro.md`](plano-fase-1-a-memoria-mitiga-o-erro.md), §4). **Só contagens saem.**
> **Como usar:** cole **tudo abaixo da linha** no agente da máquina 2 (Copilot) e me traga a resposta dele, inteira.

---

Você vai rodar **um script que já existe e já foi testado**, e me devolver a saída. **Não é uma tarefa de análise, de
código ou de interpretação.**

## Regras (valem para tudo)

1. **Não edite nenhum arquivo do repositório**, não crie script e não corrija nada. Se algo falhar, **pare, copie a
   mensagem de erro exatamente como saiu e me devolva**. Não tente consertar.
2. **Não calcule nem interprete números.** Copie a saída do script como ela saiu.
3. **Nada de identificador nem de texto de caso na resposta:** nenhum `exec_id`, nenhum `step_ref`, nenhum trecho de
   código, de mensagem de erro ou de input de usuário. O script só imprime nomes de memória, nomes de papel, meses e
   contagens; se aparecer qualquer outra coisa, **não cole e me avise**.
4. Rode da **raiz do repositório**.

## Passo 1 — trazer só o script, sem trocar de branch

Rode estas duas linhas, uma de cada vez:

```
git fetch origin 2026-11-11-pocs-experimentos-design
git checkout origin/2026-11-11-pocs-experimentos-design -- analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_memorias.py
```

A segunda linha copia **um arquivo só** para a pasta de trabalho; a branch em que você está não muda. Se qualquer das duas
falhar, pare e me devolva a mensagem.

## Passo 2 — rodar

```
uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_memorias.py
```

O script lê dois arquivos nos caminhos padrão:
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/U_sandbox/erros_lidos.csv` e
`analysis/2026-10-trace-law-flow-third/data/base_contagens.parquet`.

- **Se der `não achei erros_lidos`:** procure o arquivo com esta linha e me devolva **os caminhos que achar** (só os
  caminhos, sem abrir o arquivo):
  ```
  git ls-files --others --ignored --exclude-standard -- analysis/2026-10-trace-law-flow-third | findstr erros_lidos
  ```
  Se achar um só, rode de novo acrescentando ` --erros-lidos <o caminho que achou>` ao comando do passo 2. Se não achar
  nenhum, **pare** e me avise: a mineração do sandbox precisa ser rodada antes (não a rode por conta própria).
- **Se der `não achei contagens`:** pare e me avise.

## Passo 3 — o que me devolver

1. A **saída inteira** do comando do passo 2, colada como texto (inclui as linhas `AVISO`, se houver).
2. O conteúdo dos dois arquivos que o script escreveu ao lado do `erros_lidos.csv`:
   `volumetria_memorias_resumo.csv` e `volumetria_memorias_por_mes.csv` (são pequenos, só contagens).
3. O **nome da pasta da rodada mais recente** em `analysis/2026-10-trace-law-flow-third/pipeline/resultados/` (o nome da
   pasta, só isso).
4. **Opcional, se existir:** as linhas dos papéis `ContestacaoCivel`, `RespostaBacen`, `JoogleAnalytics` e
   `CalculoTrabalhista` do arquivo `taxas_custo_por_papel.csv` (dentro de `<rodada>/taxas/`). É a mediana e o p90 de
   tokens por execução, com e sem erro. Se o arquivo não existir, escreva "não existe" e siga.

## O que eu vou fazer com isso

Calcular, para cada par (agente, memória), a incidência de hoje, quantos inputs existem para montar o conjunto de
execuções que erraram e quantas execuções reais cada par exige. Se um `AVISO` disser que um papel dos erros não tem
correspondente nas contagens, isso importa para mim: **não o ignore**.
