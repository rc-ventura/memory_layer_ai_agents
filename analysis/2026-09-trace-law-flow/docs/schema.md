# Schema do trace cru — esteira de agentes do fluxo jurídico

**Arquivo:** `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` (14,2 MB comprimido). **git-ignored** — contém PII (nomes
de clientes, nºs de processo, trechos de documentos em claro); ver `.gitignore` da raiz (`*.csv.xz`, `*.csv`) e
o desta pasta. Nunca versionar sem anonimização.

**Cobertura:** 1.000 execuções, nov/2025–ago/2026 · 5.781 steps · 142,6M tokens. **Provável `LIMIT 1000`** na
query de origem — amostra, não população (`04-roadmap.md` item 3).

## Granularidade

1 linha do CSV = **1 execução** de agente. Os steps daquela execução vivem no JSON aninhado da coluna
`txt_etap_memo` (células chegam a dezenas de MB).

## Colunas (11)

| # | Coluna | Conteúdo | Fonte |
|---|---|---|---|
| 0 | `cod_idef_aget` | id numérico do agente (tipo/papel) | dado |
| 1 | `cod_idef_exeo` | id da execução | dado |
| 2 | `cod_idef_stat_exeo_aget` | código de status da execução (ver §Status) | dado; semântica **inferida** |
| 3 | `cod_idef_cvsa_asnc` | id de conversa / fluxo assíncrono | nome **inferido** da abreviação |
| 4 | `dat_hor_encm_exeo` | data/hora de encerramento — **só preenchida para status 3 e 34** | dado |
| 5 | `txt_etap_memo` | JSON das etapas: `model_output` (thought), `code_action`, `observations`, `tool_calls`, `model_input_messages`, e a chamada `final_answer()` | dado |
| 6 | `txt_vrvl_locl` | "variável local" — provável namespace Python persistido entre steps | nome **inferido** |
| 7 | `txt_rspa_fina` | texto da resposta final (coluna dedicada) — **vazia para status 1** | dado |
| 8 | `dat_hor_inio_exeo` | data/hora de início | dado |
| 9 | `cod_vers_aget` | versão do agente | dado |
| 10 | `anomesdia` | AAAAMMDD (int) | dado |

⚠️ Nomes das colunas 3 e 6 são leitura da abreviação, não confirmados com a esteira.

## `cod_idef_stat_exeo_aget` (o campo "status")

Medido direto do CSV em 2026-09-10 (`lzma.open` + `csv.reader`, `field_size_limit` alto). **Nunca null** —
sempre um de 4 valores.

| status | execuções | % | tem `dat_hor_encm_exeo`? | tem `txt_rspa_fina`? |
|---|---:|---:|---|---|
| **1** | 872 | 87,2% | não (0/872) | não (0/872) |
| **3** | 68 | 6,8% | sim (68/68) | sim (63/68) |
| **2** | 51 | 5,1% | não (0/51) | parcial (29/51) |
| **34** | 9 | 0,9% | sim (9/9) | sim (9/9) |

Cortes adicionais:

- **status 1 = default dos agentes de maior volume.** `cod_idef_aget` 1 (714 exec) e 2 (100 exec) são 100%
  status 1. Os agentes de domínio (ids 67, 133, 168, 496…) concentram 2/3/34.
- **status 34 só aparece a partir de abr/2026** (0 em nov–dez/2025) — possivelmente código adicionado depois.
- status 1 domina todos os meses.

### Por que o status não serve como rótulo de sucesso/fracasso

Para os 87% em status 1, a plataforma não persiste nem encerramento nem resposta final — **mesmo o agente
tendo chamado `final_answer()` dentro de `txt_etap_memo`**. As únicas 77 execuções (7,7%) com sinal de "fechou"
estão em status 3/34. Por isso a análise (`02-relatorio-achados.md` §3.1 / §4) construiu um check de sucesso
**por conteúdo** (procura `final_answer` no JSON + duas frases de recusa), não pelo status.

**Precisão:** `01-racionais.md` §4 Passo 1 diz "100% das memórias contêm `final_answer`" — vale para o **JSON
`txt_etap_memo`** (~840 de 1.000). A **coluna `txt_rspa_fina`** é outro campo e está vazia em 87%. São duas
coisas distintas.

## Aberto — perguntas para o time da esteira (`04-roadmap.md` item 3)

1. O que é cada código? status 1 = "em andamento" / "não rastreado até o fim" / "sucesso não persistido"?
2. Por que status 1 nunca tem `dat_hor_encm_exeo` / `txt_rspa_fina` se houve `final_answer()`? Quem escreve
   essas colunas, e quando?
3. 3 e 34 são os "encerrados" — 3 = sucesso, 34 = erro? Outra distinção?
4. status 2 (sem encerramento, resposta parcial) — o que é?
5. status 34 só desde abr/2026 — código novo? o que era antes?
6. O status depende do *tipo* de agente (`cod_idef_aget` 1 e 2 são sempre status 1)?
7. A extração de 1.000 linhas filtra por status?
8. Confirmar os nomes das colunas 3 (`cod_idef_cvsa_asnc`) e 6 (`txt_vrvl_locl`).

---
Extração e cross-tabs: `lzma.open` + `csv.reader`, 2026-09-10. A semântica dos códigos de status e os nomes
das colunas 3/6 são **inferência** — confirmar com a esteira antes de citar como fato.
