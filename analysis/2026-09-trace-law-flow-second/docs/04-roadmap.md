# Roadmap — o backlog numerado da base 2

> **Códigos e siglas:** [glossário](../../glossario.md). O schema deste roadmap (o mesmo de todos): [`../../plano-atual.md`](../../plano-atual.md).
> **Numeração:** os números são desta pasta e estáveis; de fora, cite como `b2 #N`. Índice do que existe da base 2:
> [README](../README.md).

**Atualizado:** 09/10/2026 · **Branch:** `2026-10-09-roadmaps-schema`. Até 06/10/2026 estes itens eram o §4.14, o §4.11 e
linhas do §2 do plano atual (`git show e0335aa:analysis/plano-atual.md`).

## Backlog

**A validar o kit na base 2** (plano antigo 4.14, passo 1) — o ambiente de compliance; o Rafael roda e traz contagens. O
prompt que existia para isso foi apagado e **não será recuperado** (decisão de 09/10): se for preciso, escreve-se outro
a partir destes itens.

- [ ] **#1 · Preparar a pasta `-second`.** Replicar o que o livro-razão pede: o parquet (`uv sync`, que traz o
  `pyarrow`; `analysis/leitor_trace.py`; as trocas de leitura no `base_pipeline.py`, `checklist.py` e `drill_down.py`;
  o `.gitignore`) e os Ajustes 13–16, com `TRACE` e `BASE_ID` restaurados. **Reexecutar os notebooks no terminal** (a
  pendência do antigo 4.2a). Conferir que o Copilot acha o kit no `.claude/` (`/mineracao-candidata` aparece no `/`) e
  apagar as cópias antigas das skills em `.github/`. Os registros agora estão em `analysis/registros/`.
- [ ] **#2 · O monitoramento primeiro** (`monitorar.py`). Esperado: a `U_nome_inventado` com alerta (118 erros); o
  `U_campo_inexistente` com alerta de crescimento (38 ≥ 3 × 10); a ferramenta concorrente do `final_answer` sem alerta.
- [ ] **#3 · `U_nome_inventado` — a maior candidata da base 2** (plano antigo 4.11). **Contexto:** 118 erros na base 2 (5
  na base 1). A contagem da rodada 2 mostra 101 num papel, num mês e num modelo: parece incidente, e os 17 espalhados
  sustentam a candidatura (livro-razão Etapa 10d). Na base 1, a unidade junta duas lições (dossiê em
  `resultados/mineracao/U_nome_inventado/`). **O que fazer:** `/mineracao-candidata U_nome_inventado` no ambiente da
  base 2, com as regras da base 1 sem mudança; conferir se o ContestacaoCivel já usava o mesmo modelo antes de agosto
  sem o erro (`drill_down.py protocolo` [8]). **Tipo:** medição; pode virar Ajuste (separar o mês na triagem, ou
  dividir a unidade).
- [ ] **#4 · As minerações de silenciosas e de protocolo, no método novo de leitura.** Comparar com o publicado (`14`,
  `11`, as 8 candidatas) **aqui, fora do kit**.

- [ ] **#11 · Falso negativo do AgenteProcuracoes** (Etapa 5b, achado 5; 1 execução). A busca com nome + CPF achou
  procurações, e a resposta final foi "não localizei procurações concluídas", dada "pelos trechos visíveis na
  observação". Em aberto: se o que achou não eram concluídas, a resposta está certa; se eram, o erro custou uma resposta
  errada. → livro-razão Etapa 5b
- [ ] **#12 · A lição candidata "uma ferramenta pesada por step"** (Etapa 5b, achado 1: OBFCivel jul, limite de 30 s, três
  ferramentas pesadas no mesmo bloco; RespostaOficios mar, 30 s). Sem regra: 2 casos, 1 confirmado, e contar ferramentas
  não diz quais são pesadas. Espera a medida e a base 3. → livro-razão Etapa 5b

## Monitoramento

Os gatilhos da base 2 estão na seção Monitoramento do [roadmap da base 1](../../2026-09-trace-law-flow/docs/04-roadmap.md)
e em [`registros/monitoramento.json`](../../registros/monitoramento.json); não se duplicam aqui. Em aberto lá: o
gatilho do timeout de ferramenta (acionado na base 2) pede um ticket à plataforma.

## Fora de escopo / adiado

## Fechado

Cada linha: o que foi feito → o commit ou o documento (a prova).

- [x] **#5 · S1 — a leitura do erro crítico da base 2** → `0d71323`; `11` §2.5, `10` §4.
- [x] **#6 · S2 fechado na base 2** (antigo 4.1) → registro de 01/10; livro-razão Etapa 10c.
- [x] **#7 · A base 2 rodada no ambiente de compliance** (antigo 4.2a) → relatório de 02/10; livro-razão Etapa 10c.
  A pendência (reexecutar os notebooks no terminal) é o #1.
- [x] **#8 · Os sucessos falsos de plataforma e a leitura assistida** (antigos 4.1b, base 2, e 4.7 / D2): nenhum
  sucesso falso confirmado nos 24 candidatos — a resposta final declara a falha; RespostaBacen M1 3, M2 1 → relatório
  de 02/10 e a segunda rodada de 05/10; `14` §5, `11` §2.6, `10` §4.
- [x] **#9 · A base 2, rodada 2: a base 2 finalizada** (antigo 4.2d) → registro de 05/10; livro-razão Etapa 10d, `14` §5.
- [x] **#13 · O relatório da base 2 reunido num documento só**, copiando as seções dos docs `11`, `14` e do livro-razão,
  com a origem em cada linha (nada foi movido) → [`02-relatorio-base2.md`](02-relatorio-base2.md) (09/10).
- [x] **#10 · O campo inexistente da base 2 também é sinal de harness** (Ajuste 13) → registro de 05/10; livro-razão.
