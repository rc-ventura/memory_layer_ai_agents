# Auditorias — o que já foi auditado, por quem, e em que estado

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Para que serve:** responder "isso já foi auditado?" sem abrir cada relatório. Uma linha por auditoria e uma por
script de recomputação. Quando uma auditoria nova chegar: o relatório entra aqui com o estado **aberta**, as
ressalvas viram item no [`../../plano-atual.md`](../../plano-atual.md), e a resposta do autor entra no próprio
relatório como **Parte II**. Só então o estado vira **fechada**.

**Regras que valem para todas:**

- **Reexecutar não é verificar.** Rodar as funções do pipeline de novo prova reprodutibilidade. Verificação é uma
  segunda implementação a partir da prosa dos racionais, comparada número a número — o padrão dos
  `audit_recompute*.py` (`csv` + `json` + `ast`, sem pandas, sem importar o `base_pipeline`). Só a abertura do
  arquivo vem de fora: `analysis/leitor_trace.py` (`abrir_trace`), que entrega as linhas no formato do
  `csv.DictReader` a partir de CSV (puro, `.xz`, `.gz`) ou de um único parquet (plano-atual §4.10).
- **Uma checagem que diverge sempre é consertada**, nunca convivida: ensina a ignorar a próxima divergência.
- **Saídas** (`scripts/audit_out*.txt`) são git-ignored: podem ter trechos do trace. Os relatórios são manuscritos e
  versionados.
- **Base 2:** auditada por fotos da máquina de compliance. Só contagens saem de lá — o `audit_recompute9` aceita
  `--base base2 --trace …` para rodar lá. Todos os scripts aceitam `--trace <arquivo>` (CSV ou parquet); os números
  esperados embutidos nos scripts 1–8 são os da base 1. O `audit_recompute9` aceita qualquer `--base`: numa base sem números embutidos,
  imprime tudo como "a conferir" e, com `--json <arquivo>`, grava as medidas. É assim que o kit de mineração o usa,
  em paralelo à mineração, para confrontar com as tabelas (`kit-mineracao/`, skill `mineracao-silenciosas`).

## Relatórios

| Data | Relatório | Objeto | Estado | Onde estão as respostas |
|---|---|---|---|---|
| 08/09 | [`2026-09-08-auditoria-independente.md`](2026-09-08-auditoria-independente.md) | cadeia de evidência do notebook da esteira (base 1) | fechada · parcialmente desatualizada desde 23/09 (mês do lote → mês da execução; banner no topo) | `../docs/03-procedimento-validacao.md` §1.12 |
| 16/09 | [`2026-09-16-auditoria-independente.md`](2026-09-16-auditoria-independente.md) | auditoria #2: mecanismo, triagem, unidades (após 15/09) | fechada · parcialmente desatualizada desde 23/09 (banner no topo) | idem; roadmap |
| 02/10 | [`2026-10-02-auditoria-branch-2026-09-28-mineracao-base2.md`](2026-10-02-auditoria-branch-2026-09-28-mineracao-base2.md) | PR #29 (branch `2026-09-28-mineracao-base2`, 43 commits): Ajustes 5–10, família Protocolo do harness, balde invisível | **fechada nas duas bases** (Parte II, 02/10; base 2 em II.7) | Parte II do próprio relatório; Ajuste 11 no livro-razão |

## Scripts de recomputação independente

| Script | Cobre | Estado na base 1 |
|---|---|---|
| `scripts/audit_recompute.py` | números-chave do relatório (fase 1) | auditoria de 08/09 |
| `scripts/audit_recompute2.py` | contexto, candidatos, detectores (fase 2) | idem |
| `scripts/audit_recompute3.py` | durações, razões in/out, eficiência, papel × assinatura (fase 3) | idem |
| `scripts/audit_recompute4.py` | réplica do §3.3, ferramentas posicionais, CSVs derivados, integridade do notebook (fase 4) | idem |
| `scripts/audit_recompute5.py` | nível base (assinatura/erro/execução) após 15/09 (fase 5) | auditoria de 16/09 |
| `scripts/audit_recompute6.py` | **balde visível**: submecanismo erro a erro, cascatas, unidades, cobertura, papel × unidade, ressalva E, tokens/chamada, régua | **0 divergências (A–G)** em 02/10 — E corrigida para o mês da execução |
| `scripts/audit_recompute7.py` | evidência 11.9 (leituras de `validar_quebra_sigilo`) | auditoria de 16/09 |
| `scripts/audit_recompute8.py` | evidência 11.10 (leituras de `get_available_documents`) | auditoria de 16/09 |
| `scripts/audit_recompute9.py` | **balde invisível**: funil, grupos do motivo (+ disparos por regra), [2], [3], [4] (Ajuste 11), forma do `busca_obf`, sondas da consolidação, **G: a `U_repr_colado` consolidada** (Ajuste 12; base 1 12 · 12 · 4 · 2) | **0 divergências** nas duas bases em 02/10 (base 2 na máquina 2: `--base base2 --trace <.csv>`); com o bloco G (04/10): base 1 0 divergências, base 2 a rodar |

Para conferir tudo de novo na base 1 (de `analysis/2026-09-trace-law-flow/`):

```
python audit/scripts/audit_recompute6.py > audit/scripts/audit_out6.txt
python audit/scripts/audit_recompute9.py > audit/scripts/audit_out9.txt
grep -c DIVERGE audit/scripts/audit_out6.txt audit/scripts/audit_out9.txt   # esperado: 0 e 0
```
