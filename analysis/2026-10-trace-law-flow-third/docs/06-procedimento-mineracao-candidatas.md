# Procedimento — minerar uma candidata a memória na base 3

> Códigos e siglas: [glossário](../../glossario.md). **O porquê de cada passo:**
> [`07-racionais-mineracao-candidatas.md`](07-racionais-mineracao-candidatas.md). **O que é de cada lição** (a regra,
> os limiares): `propostas/<u>/racional.md`. A origem do método, na base 1:
> [`16`](../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md).

**Atualizado:** 16/10/2026 · **Branch:** `2026-10-16-base3-comparar-rodadas`.

**Dois jeitos de rodar, o mesmo resultado:**
- **pela skill** `/mineracao-candidata <u>`: ela roda os passos abaixo na ordem, para onde eles param e organiza a
  entrega;
- **à mão:** os comandos abaixo, um por passo, na ordem. Cada passo lê o que o anterior gravou e para com saída 1 e o
  motivo numa linha.

Tudo roda da raiz do repositório, no ambiente onde está a base. Para ensaiar com a base 1, ver o §3. Os scripts das skills que o comando chama (`monitorar.py`, `validar_memoria.py`, `varrer_pii.py`) são
procurados em `.claude/skills/` e, se não estiverem lá, em `.github/skills/` (o Copilot, no ambiente da base) e em
`.copilot/skills/`.

## 1 · O que muda na base 3

| | Base 1 | Base 3 |
|---|---|---|
| Parte genérica | `mineracao_generica.ipynb` | já está na rodada: `perfis/<u>/`, gravada pelo `executar.py analisar` |
| Auditoria independente | `audit_recompute6.py` | `audit/scripts/audit_candidata_base3.py`: recalcula a lição direto do parquet, sem importar o pipeline |
| Parte específica | notebook (legado) ou investigação | **script** `mineracao_<u>.py` (Ajuste 20): em `propostas/<u>/` até a aprovação, depois em `pipeline/especificas/`; ou investigação |
| Localizador no arquivo final | `exec_id` + `idx` | `step_ref` + `fonte_id` + `rodada_id` (esquema 0.2, Ajuste 19) |

## 2 · O passo a passo

Abreviação: `M="uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/minerar.py <u> --rodada <rodada_id>"`.
Os passos gravam em `pipeline/resultados/mineracao/<u>/` (ou em `--saida <pasta>`).

| Passo | Comando | O que faz | Para se |
|---|---|---|---|
| 1 · Conferir a rodada | `$M --passo 1` | rodada concluída, todo artefato no hash do manifesto, a lição candidata com perfil gravado | rodada incompleta, artefato fora do manifesto, lição fora da triagem ou sem perfil (`executar.py analisar --perfil <u>`) |
| 2 · Monitoramento | `$M --passo 2` | roda o `monitorar.py` da skill `mineracao-base` | um alerta (a lição volta ao pesquisador) |
| 3 · Parte genérica | `$M --passo 3` | lê o perfil da rodada (recorrência, sub-unidades, antes, depois, estabilidade, população) | — |
| 4 · Parte específica | `$M --passo 4` | roda o script da lição (`script:` no funil) e grava as tabelas dele | a linha do funil é `investigação:` (segue a investigação, `16`) |
| 5 · Confiança | `$M --passo 5` | a cobertura da regra, contra o limiar do racional da lição | abaixo do limiar (tabelas gravadas, arquivo final não) |
| 6 · Destino | `$M --passo 6` | os números que o racional da lição pede para a decisão memória × harness | — |
| 7 · Auditoria e encontro | `$M --passo 7` | roda `audit/scripts/audit_candidata_base3.py` e compara medida a medida com os passos 3–5 | qualquer medida diferente (a divergência é o achado) |
| 8 · Arquivo final | `$M --passo 8` | monta `memoria_<u>_<BASE_ID>.json` e o valida com o `validar_memoria.py` | reprovado |
| 9 · Saída | `$M --passo 9` | manifesto da mineração, relatório completo (fica), versão que sai (varrida) e o resumo | o varredor acha algo |

**Todos de uma vez:** `$M` (sem `--passo`) roda de 1 a 9 e para no primeiro problema. É o que a skill chama.

**A auditoria, sozinha** (o passo 7 a chama; à mão, para refazer só ela):

```bash
uv run python analysis/2026-10-trace-law-flow-third/audit/scripts/audit_candidata_base3.py <u> --fonte <parquet> --json <arquivo>
```

**O resumo** (fim do passo 9) cabe numa foto: cada passo com ok ou o motivo da parada, a confiança, o encontro e as
tabelas principais da lição, só com contagens e nomes (papel, mês, módulo, função). É dele que saem
o dossiê e as decisões do pesquisador (`07`, "O gate").

## 3 · Como ensaiar aqui (base 1 pela porta da query)

```bash
uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/rodada_base1.py --saida <pasta>
uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/minerar.py <u> --rodada <pasta>/rodada --fonte <pasta>/fonte_base1_v1.parquet --saida <outra pasta>
```

O padrão de `--saida` é `pipeline/resultados/ensaio_base1/`. O primeiro gera uma rodada da base 1 no formato da base 3 (a mesma porta do `comparar_base1.py`), com o perfil de
todas as candidatas. O segundo é o mesmo comando da base real.

## 4 · O funil — a parte específica de cada lição

<!-- funil: a skill mineracao-candidata e o minerar.py leem esta tabela. Uma linha por lição; parte específica = script:<arquivo em pipeline/especificas/> | investigação:<roteiro do kit> -->

| Lição | Parte específica | Estágio | Desde | Frequência | Confiança | Situação | Decisão |
|---|---|---|---|---|---|---|---|
| `U_sandbox` | `script:mineracao_U_sandbox` | 3 · script | 16/10/2026 (racional: `9640b13`, emendas `aa99b8f`, `fd93e93`) | — (o comando calcula) | cobertura 99,86% (base 3) | script aprovado (19/10) | dividir em partes: em aberto (dossiê) |
| `U_tipo_retorno` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | espera o contrato da ferramenta (pedido C) | — |
| `U_arg_nomeado` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | próxima candidata a script | — |
| `U_campo_inexistente` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | espera o contrato da ferramenta (pedido C) | — |
| `U_estado_perdido` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | precisa de leitura de caso | — |
| `U_texto_solto` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | precisa de leitura de caso | — |
| `U_repr_colado` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | precisa de leitura de caso | — |
| `U_nome_inventado` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | em monitoramento (`monitoramento.json`) | — |
| `U_texto_literal` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | precisa de leitura de caso | — |
| `U_next_gerador` | `investigação:candidata` | 1 · investigação | 16/10/2026 | — | não avaliada | próxima candidata a script | — |

<!-- /funil -->

## 5 · O que sai do ambiente da base

O de sempre ([sigilo](../../../.claude/skills/mineracao-base/referencias/sigilo.md)): contagens, nomes de papel,
ferramenta, unidade, módulo e função, meses, hashes e o identificador de execução. O arquivo final da memória sai
inteiro. O relatório completo, com a evidência, fica.
