# Base 2 — trace cru, lote de ago/2026 (1.000 registros), a segunda amostra

> **Códigos e siglas:** [glossário](../glossario.md). O schema dos roadmaps: [`../plano-atual.md`](../plano-atual.md).

**O que esta pasta é.** A base 2 é uma amostra independente da base 1 (0 execuções em comum), com o trace cru, rodada
no ambiente de compliance — o pipeline e os dados dela ficam lá, e não saem de lá. Esta pasta guarda só a
**documentação** da base 2: o [roadmap](docs/04-roadmap.md) e este índice. Até 09/10/2026 a base 2 não tinha pasta aqui,
e o que é dela estava espalhado pelos documentos da base 1 e pelo livro-razão.

**A base 2 não tem racionais nem procedimento próprios**, de propósito: o método é o mesmo da base 1, e os racionais e
procedimentos são **por método** (valem para as duas bases). O que é próprio da base 2 são os **resultados**, a
**auditoria** e o **como foi rodada**. Onde estão, hoje:

| O que | Onde está | Observação |
|---|---|---|
| **Relatório — protocolo do harness** | [`11`](../2026-09-trace-law-flow/docs/11-relatorio-protocolo-harness.md) §2 (a base 2, em andamento até 02/10) e §3 (comparação entre bases) | Base 1 e base 2 no mesmo documento |
| **Relatório — falhas silenciosas** | [`14`](../2026-09-trace-law-flow/docs/14-relatorio-falhas-silenciosas.md) (por ferramenta, motivos, candidatos a sucesso falso) | Mistura as duas bases |
| **Relatório — o que a base 2 trouxe à taxonomia** | livro-razão [`pipeline-entre-bases.md`](../pipeline-entre-bases.md): Etapas 3 (causa não identificada), 4 (timeout), 5 (a chave `?`), 5b (AgenteProcuracoes), 10b (`H_bloco_code`), 10c (falhas silenciosas), 10d (rodada 2 e finalização), 6 (alarme de cobertura), 7 (comparação entre bases); Ajustes 3, 4, 13 | O histórico de cada ajuste e a verificação |
| **Racionais** (protocolo, silenciosas, candidatas) | [`10`](../2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md), [`13`](../2026-09-trace-law-flow/docs/13-racionais-falhas-silenciosas.md), [`06`](../2026-09-trace-law-flow/docs/06-racionais-mineracao-unidades-n2-n10.md) | Por método, não por base |
| **Procedimento** | [`12`](../2026-09-trace-law-flow/docs/12-procedimento-protocolo-harness.md), [`15`](../2026-09-trace-law-flow/docs/15-procedimento-falhas-silenciosas.md), [`16`](../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md) | Por método, não por base |
| **Como foi rodada** (replicar os ajustes na pasta `-second`, reexecutar os notebooks no terminal) | livro-razão, Etapas 10b–10d | |
| **Auditoria** | [`../2026-09-trace-law-flow/audit/2026-10-02-auditoria-branch-2026-09-28-mineracao-base2.md`](../2026-09-trace-law-flow/audit/2026-10-02-auditoria-branch-2026-09-28-mineracao-base2.md) | Fechada, com Parte II |
| **Monitoramento** | [`../registros/monitoramento.json`](../registros/monitoramento.json); e a seção Monitoramento do [roadmap da base 1](../2026-09-trace-law-flow/docs/04-roadmap.md) (gatilho do timeout acionado na base 2; o protocolo revalidado) | |
| **Diário** | `research-diary/summarization/Set/sintese_2026-09.md` e `Out/` | |

**Itens do [roadmap da base 1](../2026-09-trace-law-flow/docs/04-roadmap.md) que dizem respeito à base 2** (ficam lá,
com o número deles, porque o código e os docs os citam): `b1 #29`–`#34` (o resíduo, o timeout, o `Import from`, o `?`,
o cruzamento de padrões, o alarme de cobertura), `b1 #36` e `b1 #39` (os erros críticos).

**Numeração:** os números do roadmap desta pasta são desta pasta; de fora, cite como `b2 #N`.

**Próximo passo possível, não feito:** reunir num `relatorio-base2.md` as seções acima, **copiando** (sem mover) e
com link para a origem. Fica aberto até o Rafael decidir.
