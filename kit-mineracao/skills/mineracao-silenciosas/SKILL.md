---
name: mineracao-silenciosas
description: "Minera as falhas silenciosas (o balde invisível: a ferramenta falhou e o step não levantou exceção) de uma base do trace de agentes, do zero, a partir das tabelas que o notebook e o drill_down produzem para essa base: funil, ferramentas, grupos do motivo e seus donos, o que vem depois, candidatos a sucesso falso, detectores e ocorrências. Não compara com relatório publicado: a verificação é uma auditoria independente rodando em paralelo, cujas medidas são confrontadas com as tabelas por script. Entrega os achados da base e as paradas (o que precisa de leitura de caso). Use quando pedirem 'minere as falhas silenciosas', 'rode as silenciosas na base <X>', 'mineração do balde invisível'. Começa pela skill mineracao-base; as paradas seguem para a skill mineracao-investigacao."
---

# Mineração das falhas silenciosas

**O que é minerar aqui:** ler as tabelas que o pipeline produziu para esta base, seguindo os passos do procedimento da
análise, e dizer o que elas mostram. Não há número "certo" para bater: os números **são** o resultado. O que garante
que eles estão certos é:
- **uma segunda implementação** (a auditoria independente) chegando nos mesmos números;
- **as conferências internas**, que valem em qualquer base.

**O método está na análise, não aqui.** O passo a passo é `docs/*procedimento-falhas-silenciosas*.md`, e o porquê
de cada medida é `docs/*racionais-falhas-silenciosas*.md`. Esta skill diz de onde ler, o que verificar e onde parar.
Se o procedimento e esta skill discordarem, vale o procedimento: registre a discordância.

## 1 · Preparação: a skill `mineracao-base`

O Passo 0 inteiro. Guarde o `BASE_ID`, a pasta da análise e o `TRACE`. Se a preparação parou, esta skill também para.

## 2 · Disparar a auditoria em paralelo (agente `auditor-independente`)

Logo depois da preparação, sem esperar a mineração, entregue ao `auditor-independente` este comando, para rodar da
pasta da análise:

```
uv run python audit/scripts/audit_recompute9.py --base <BASE_ID> --trace <TRACE> --json pipeline/resultados/auditoria_silenciosas_<BASE_ID>.json
```

- Ele recalcula as medidas direto do trace, sem usar o pipeline, e grava o JSON.
- Ele precisa do `pipeline/resultados/erros_mecanismo.csv`, que é o balde visível, gerado pelo notebook da esteira.
  Se o arquivo não existir, rode antes, de dentro de `pipeline/`:
  `uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 analise_trace_esteira_juridica.ipynb`.
- Sem subagentes no ambiente: rode o comando você mesmo, antes do passo 3, e não leia a saída dele até o passo 5.

## 3 · Garantir as tabelas da mineração

As tabelas de entrada, todas em `pipeline/resultados/` e todas da mesma base:

| Tabela | Quem produz |
|---|---|
| `evidencia/silenciosas/casos.csv` (uma linha por falha silenciosa) | `uv run python drill_down.py silenciosas` |
| `evidencia/silenciosas/ocorrencias.csv` (a saída para a consolidação) | o notebook `falhas_silenciosas.ipynb` |
| as saídas das seções do notebook `falhas_silenciosas.ipynb` | o próprio notebook |

Se alguma falta, ou é mais antiga que o trace ou que o `base_pipeline.py`, gere de novo, de dentro de `pipeline/`:

```
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 falhas_silenciosas.ipynb
uv run python drill_down.py silenciosas
```

Para conferir as datas: `uv run python -c "import os,base_pipeline as b;[print(round(os.path.getmtime(p)),p) for p in (b.TRACE,'base_pipeline.py','resultados/evidencia/silenciosas/casos.csv','resultados/evidencia/silenciosas/ocorrencias.csv')]"`.

## 4 · Minerar: ler as tabelas, passo a passo do procedimento — cada achado com a evidência

Para cada passo, escreva no relatório **o que a tabela mostra**, em contagens e proporções, e **a evidência**: a regra 0
da `mineracao-base` e o `evidencia.md` dela. Não use números de outra base como referência.

A evidência crua de cada achado sai do `montar_evidencia.py` da `mineracao-base`, chamado como abaixo. Nos comandos,
`ME` é `uv run python <skill mineracao-base>/scripts/montar_evidencia.py <pasta-da-analise>`, e `T` é a tabela
`evidencia/silenciosas/casos.csv`. Cada chamada escreve um `bloco.md`. Leve-o ao relatório com `cat`.

| Passo | O que registrar | Reproduzir | Evidência crua (montar) |
|---|---|---|---|
| **1 · Funil e escala** | falhas de ferramenta com exceção × silenciosas, a proporção e a sobreposição entre os baldes (tem de ser 0; se não for, **pare**) | `uv run python drill_down.py silenciosas` + notebook §funil | `ME --nome silenciosas_funil_<BASE_ID> --de T` (o 1º de cada mês) |
| **2 · Por ferramenta** | onde as silenciosas se concentram (topo e fração) | `uv run python drill_down.py silenciosas` [1] | `ME --nome silenciosas_ferramenta_<BASE_ID> --de T --onde ferramenta=<a do topo>` |
| **3 · Grupos do motivo** | contagem por grupo e a fração de `nao_reconhecido`. **Parada S3** se ele não estiver vazio | `uv run python drill_down.py silenciosas --motivos` | `ME --nome silenciosas_nao_reconhecido_<BASE_ID> --de T --onde grupo=nao_reconhecido` |
| **4 · Dono dos grupos a conferir** | a forma do argumento por ferramenta. **Parada S1** se a forma não decide | `uv run python drill_down.py silenciosas --forma <ferramenta>` | `ME --nome silenciosas_dono_<grupo>_<BASE_ID> --de T --onde grupo=<grupo> --onde ferramenta=<ferramenta>` |
| **5 · O que vem depois** | a distribuição do que vem depois e a fração de erros de contrato precedidos, contra o limiar do procedimento | `uv run python drill_down.py silenciosas` [2] e [3] | — (número agregado: reproduzir + derivada) |
| **6 · Candidatos a sucesso falso** | o teto por grupo (candidatos / falhas reais). **Parada S2** se houver candidatos | `uv run python drill_down.py silenciosas` [4] | `ME --nome silenciosas_sucesso_falso_<BASE_ID> --de T --onde sucesso_falso_candidato=True --por grupo` |
| **7 · Detectores** | os números da seção do notebook; o inventário declarado × as ferramentas chamadas | notebook §detectores | — (agregado) |
| **8 · Consolidação** | as unidades que o canal silencioso alimenta, o que muda na triagem, os steps nos dois canais (tem de dar 0) | `uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 consolidacao_unidades.ipynb` | `ME --nome silenciosas_unidade_<unidade>_<BASE_ID> --de evidencia/silenciosas/ocorrencias.csv --onde unidade=<unidade>`, uma por unidade |

Em todo comando do `ME`, passe `--afirmacao "<a frase do achado>"` e `--reproduzir "<o comando da coluna Reproduzir>"`.
O bloco do relatório sai com a afirmação, o comando, a tabela derivada com o filtro e os casos crus.

As perguntas S1, S2 e S3 estão no roteiro `silenciosas` da skill `mineracao-investigacao`. Aqui se registra que a
parada existe, as contagens que a motivam e a pasta de evidência que a investigação vai usar.

## 5 · O encontro: auditoria × tabelas

Quando o auditor terminar:

```
uv run python <esta skill>/scripts/comparar_auditoria.py <pasta-da-analise> pipeline/resultados/auditoria_silenciosas_<BASE_ID>.json
```

- **Saiu com 0:** as duas implementações chegaram nos mesmos números e as conferências internas passaram. Os achados do
  passo 4 estão verificados. No relatório, a verificação leva os dois comandos (o do auditor e este) e o caminho do
  JSON.
- **Saiu com 1:** **pare**. Registre cada linha DIVERGE ou FALHA no relatório e não tire conclusão das medidas que
  divergem. A divergência é o achado, e quem decide o que fazer é o pesquisador. Não edite a auditoria, o pipeline
  nem as tabelas.

## 6 · Saída

- **Relatório:** `pipeline/resultados/relatorio_silenciosas_<BASE_ID>_<AAAA-MM-DD>.md`, no esqueleto da
  `mineracao-base`. Leva os achados por passo, cada um com a evidência; o encontro; as conferências internas; e as
  paradas, cada uma com a pasta de evidência montada.
- **Sigilo:** o relatório completo fica no ambiente. Para sair, use `versao_para_sair.py` e depois `varrer_pii.py` no
  `_saida.md`.
- **Para o pesquisador:** os achados principais em poucas linhas, o resultado do encontro e as paradas, com a pergunta
  do roteiro que cada uma abre. Para investigar uma delas, use a skill `mineracao-investigacao`.
