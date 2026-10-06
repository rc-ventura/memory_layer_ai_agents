---
name: mineracao-candidata
description: "Minera uma candidata a memória (uma lição/unidade que passou na triagem) de uma base do trace de agentes: a parte genérica para todas as lições (recorrência, sub-unidades, antes, depois, estabilidade, população), a auditoria independente em paralelo, o encontro por script e, pelo funil do procedimento da análise, a parte específica da lição — um notebook determinístico ou a investigação por subagentes. Entrega o arquivo final da memória no esquema da análise (validado), o relatório e o dossiê. Use quando pedirem 'minere a candidata <U_...>', 'minerar a lição <...>', 'rode a mineração da unidade <...>'. Começa pela skill mineracao-base; a investigação usa a mineracao-investigacao com o roteiro candidata."
---

# Mineração de uma candidata a memória

**O método está na análise:** `docs/*procedimento-mineracao-candidatas*.md`, com o porquê no
`docs/*racionais-mineracao-unidades*.md` §9. Esta skill diz como rodar, o que conferir e onde parar. O desenho, com os
diagramas da rodada e do ciclo de vida, está em [`referencias/fluxo.md`](referencias/fluxo.md).

**Entrada:** a lição (`U_...`), passada no pedido, e a pasta da análise.

**Saída:**
- o relatório da parte genérica;
- o dossiê;
- `pipeline/resultados/mineracao/<u>/memoria_<u>_<BASE_ID>.json`, no esquema da análise (`analysis/esquema-memoria.json`),
  aprovado pelo `scripts/validar_memoria.py`.

## 1 · Preparação: a skill `mineracao-base`

O Passo 0 inteiro. Depois:
- **a lição está no `pipeline/resultados/candidatos_memoria.csv`?** Se não, pare: ela não passou na triagem desta
  base;
- **os insumos existem?** Precisam existir `erros_mecanismo.csv` e `resultados/evidencia/silenciosas/ocorrencias.csv`.
  Se faltarem, rode os notebooks da esteira e das falhas silenciosas (ver o `ambiente.md`).

## 2 · Auditor em paralelo (agente `auditor-independente`)

Disparado **da raiz do repositório**. O comando, da pasta da análise:

```
uv run python audit/scripts/audit_recompute6.py --trace <TRACE> --json pipeline/resultados/mineracao/<u>/auditoria_<u>.json --unidade <u>
```

## 3 · A parte genérica

De dentro de `pipeline/`:

```
UNIDADE=<u> uv run jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=-1 --output-dir resultados/mineracao/<u> --output mineracao_generica_<u> mineracao_generica.ipynb
```

A cópia executada (com as saídas) fica junto dos resultados da lição, que são git-ignored; o notebook versionado não
muda. Leia as seções G1–G6 e escreva o relatório da parte genérica no esqueleto da `mineracao-base`. A evidência de cada
achado sai do `montar_evidencia.py`, com `--de mineracao/<u>/casos.csv` e os filtros do achado. Exemplos:
- uma sub-unidade: `--onde role=<papel>`;
- o que vem antes: `--onde "antes=erro antes: a mesma lição"`;
- a lição concentrada num mês: `--onde mes=<mês> --regra semente --n 10`.

Diga sempre as duas limitações do procedimento: a ferramenta do G2 não é a origem do valor, e a parte genérica não
extrai a lição.

## 4 · O encontro

```
uv run python <esta skill>/scripts/comparar_auditoria.py <pasta-da-analise> <u> pipeline/resultados/mineracao/<u>/auditoria_<u>.json
```

Se sair com 1, **pare**: a divergência é o achado.

## 5 · O funil

Leia a tabela entre `<!-- funil` e `<!-- /funil -->` no procedimento da análise. A linha da lição diz a parte
específica:
- **`notebook:<nome>`:** rode `uv run jupyter nbconvert --to notebook --execute --inplace <nome>.ipynb` e leve o
  registro que ele grava para o esquema. Para o notebook que grava `resultados/unidades_memoria.json`:
  ```
  uv run python <esta skill>/scripts/validar_memoria.py <analysis>/esquema-memoria.json --converter resultados/unidades_memoria.json --unidade <u> --base <BASE_ID> --parte-especifica notebook:<nome> --comando "<o comando do notebook>" --saida resultados/mineracao/<u>/memoria_<u>_<BASE_ID>.json
  ```
  Se o registro tiver várias lições, acrescente `--indice <posição da lição>`.
- **`investigação:candidata`:** abra a skill `mineracao-investigacao` com o roteiro `candidata`. A leitura é em duas
  etapas: a aberta (frase livre), **a parada para o pesquisador aprovar a lista** (o primeiro gate, registrado com
  `scripts/registrar_decisao.py --etapa lista`) e a fechada. Ela entrega o dossiê, o arquivo final (rascunho) e o
  `regras.json`.
- **Lição fora da tabela:** **pare** e peça ao pesquisador que a registre no funil.

## 6 · O arquivo final e a entrega

```
uv run python <esta skill>/scripts/validar_memoria.py <analysis>/esquema-memoria.json pipeline/resultados/mineracao/<u>/memoria_<u>_<BASE_ID>.json
```

- **Reprovado:** não entregue. Corrija o que falta e rode de novo.
- **Pendências:** campos novos do esquema ainda não preenchidos vão para as paradas.
- **Para fora:** `versao_para_sair.py` e `varrer_pii.py`, no relatório, no dossiê e no arquivo final.
- **O painel:** rode `uv run python <esta skill>/scripts/valor_da_licao.py <pasta-da-analise> <u>` e atualize as
  colunas Frequência, Confiança, Situação e Decisão da lição na tabela do funil.
- **O gate do pesquisador.** Se a situação tem gate (o painel imprime as opções: "pronta para notebook", "lição existe,
  redação em aberto", "várias causas: investigar a fundo", "certa, mas rara: monitorar"), **pare** e leve ao
  pesquisador o que o roteiro `candidata` pede em "O que o dossiê leva ao gate": a lição principal com a cobertura, os
  leitores lado a lado, o resto e as opções, com a sua recomendação. Registre a resposta com
  `uv run python <esta skill>/scripts/registrar_decisao.py <pasta-da-analise> <u> --etapa situacao --situacao "<situação>" --opcao "<opção>" --porque "<as palavras dele>"`.
  O painel mostra "aguardando" até isso.
- **Na resposta ao pesquisador:**
  - a lição, em uma frase;
  - o escopo;
  - o que é `checado` e o que é `hipotese`;
  - o destino proposto (a decisão é dele);
  - as pendências;
  - os caminhos do relatório, do dossiê e do arquivo final.

## Quando propor um notebook específico

Nunca por conta própria. Só quando a regra de criação do procedimento valer: **frequência** (Pareto das ocorrências ou
presença na maior parte dos meses: `scripts/valor_da_licao.py <pasta> <u>`, que sai com 0 se tem) **e confiança**
(dois leitores às cegas, com pelo menos 20 casos, kappa ≥ 0,6; regras contadas com ≥ 90% e ≤ 10%; laudo do
validador) — no painel, a situação "pronta para notebook", que também passa pelo gate; ou uma decisão do pesquisador. A cada partição nova, reaplique as regras do `regras.json` sem mudança e anote em `confirmacoes`. Aí use a skill `/propor-notebook`.
Ele escreve só em `propostas/<u>/`, e o agente `validador-de-notebook` dá o laudo. A aprovação é do pesquisador.
