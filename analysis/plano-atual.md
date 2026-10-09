# Plano atual — o schema dos roadmaps

> **Códigos e siglas:** [glossário](glossario.md).

**Atualizado:** 09/10/2026 · **Branch:** `2026-10-09-roadmaps-schema`.

**Para que serve este arquivo:** desde 09/10/2026 ele **não é mais uma lista do que fazer**. É o **schema** que todo
roadmap de análise segue, o mapa de onde cada roadmap está e o de-para do plano antigo. O que fazer agora, em cada
análise, fica no roadmap da própria pasta; o que vale para todas fica em dois arquivos próprios. Assim, o backlog tem
um lugar só por assunto e diminui à medida que os itens são marcados.

O plano antes desta mudança (298 linhas, com decisões, o feito, a fila e o backlog): `git show e0335aa:analysis/plano-atual.md`.

---

## 1. Onde está cada coisa

| O quê | Arquivo |
|---|---|
| Roadmap da base 1 (trace cru, out/2025–ago/2026) | [`2026-09-trace-law-flow/docs/04-roadmap.md`](2026-09-trace-law-flow/docs/04-roadmap.md) — cite `b1 #N` |
| Roadmap da base 2 (lote de ago/2026) | [`2026-09-trace-law-flow-second/docs/04-roadmap.md`](2026-09-trace-law-flow-second/docs/04-roadmap.md) — `b2 #N`; índice em [`2026-09-trace-law-flow-second/README.md`](2026-09-trace-law-flow-second/README.md) |
| Roadmap da base 3 (só os erros, em parquet — a base atual) | [`2026-10-trace-law-flow-third/docs/04-roadmap.md`](2026-10-trace-law-flow-third/docs/04-roadmap.md) — `b3 #N` |
| Roadmap do que atravessa as bases (método, kit, skills, plataforma) | [`roadmap-transversal.md`](roadmap-transversal.md) — `transversal #N` |
| Decisões em vigor (para não rediscutir) | [`decisoes.md`](decisoes.md) |
| Histórico de cada ajuste do método e de cada etapa | [`pipeline-entre-bases.md`](pipeline-entre-bases.md) (o livro-razão) |
| Registros lidos por script (monitoramento, esquema da memória) | [`registros/`](registros/README.md) |
| O que cada código e sigla quer dizer | [`glossario.md`](glossario.md) |

**O que não entra num roadmap:** o **porquê** (os `docs/NN-racionais-*.md` de cada análise), os **números** (os
relatórios) e o **histórico** (o livro-razão). Um roadmap diz o que fazer e o que foi feito, com o link para onde está o
resto.

---

## 2. O schema

Todo roadmap fica em `<pasta da análise>/docs/04-roadmap.md` e tem estas seções, nesta ordem.

```markdown
# Roadmap — <o backlog numerado de ...>

> **Códigos e siglas:** [glossário](...). O schema deste roadmap: [plano-atual.md](...).
> **Numeração:** os números são desta pasta e estáveis; de fora, cite como `bN #N`.

**Atualizado:** AAAA-MM-DD · **Branch:** `AAAA-MM-DD-slug`.

## Backlog
- [ ] **#N** o que fazer, em uma frase → onde está o contexto (link)
- [ ] **#N** item feito só em parte: a parte feita escrita no texto, e `[ ]`

## Monitoramento            (opcional — gatilhos de reabertura)
- [ ] **<o que se monitora>** — regra · dono · ação → link

## Fora de escopo / adiado  (opcional)
- o item e o porquê de não fazer agora

## Fechado
- [x] **#N** o que foi feito → o commit ou o documento (a prova)
```

**Regras:**

1. **Checkbox.** Feito, marca `[x]`; não feito, fica `[ ]`. Nada de `~~riscado~~`, "feito em…" no meio do backlog nem
   "→ plano-atual 4.x".
2. **Marcar `[x]` exige prova** — um commit, um ajuste do livro-razão ou um documento — escrita na própria linha. Sem
   prova, o item continua `[ ]`.
3. **O item marcado desce para "Fechado"**, com o **mesmo número e o texto original**; o backlog fica só com o que falta.
   Em dúvida, o item fica no backlog, com uma nota.
4. **Os números são estáveis:** nunca se renumera nem se apaga. Item novo entra no fim e ganha o próximo número. Os
   números são **por pasta**; fora do arquivo, cite com o prefixo (`b1 #24`, `b2 #3`, `b3 #9`, `transversal #1`). Um
   "roadmap #N" sem prefixo, nos documentos de antes de 09/10/2026, é o da base 1.
5. **Cada item cabe numa frase** e aponta para onde está o contexto. O detalhe mora no documento linkado.
6. **Um item mora num roadmap só.** Se vale para mais de uma base, vai para o `transversal`, e as bases apontam para ele.
7. **Atualize o cabeçalho** (data e branch) a cada mudança, e os links ao mover um arquivo.

**Para uma análise nova** (uma base 4, por exemplo): crie a pasta `AAAA-MM-trace-law-flow-<slug>/docs/`, copie o bloco
acima para `04-roadmap.md`, escreva um `README.md` com o que é a análise e onde estão os seus documentos, e acrescente a
linha na tabela do §1 deste arquivo.

---

## 3. De-para — onde foi cada item do plano antigo (de 06/10/2026)

**§1, o que vale (decisões):** todo o §1 → [`decisoes.md`](decisoes.md).

**§3, em discussão:** 1 (sucesso falso, 4.1c) → `transversal #1`; 2 (aviso à plataforma, 4.9) → `transversal #7`; 3 (sucesso
em três níveis, 4.5) → `transversal #2`; 4 (4.4 e 4.3) → `transversal #3` e `#4`.

**§4, a fila:**

| Item antigo | Onde está agora |
|---|---|
| 4.14, passo 1 (validar o kit na base 2) | `b2 #1` (preparar), `b2 #2` (monitoramento), `b2 #4` (silenciosas e protocolo) |
| 4.14, passo 2 (`U_texto_literal` na base 1) | `b1 #43` |
| 4.14, passos 3, 4 e 5 (skills de resíduo, erro crítico e apresentação) | `transversal #8`, `#9`, `#10` |
| 4.11 (`U_nome_inventado`) | `b2 #3` |
| 4.1b (sucessos falsos de plataforma, base 1) | `b1 #42` |
| 4.1c, 4.5, 4.4, 4.3, 4.6, 4.8, 4.9 | `transversal #1`, `#2`, `#3`, `#4`, `#5`, `#6`, `#7` |
| "Onde cada mineração está, em documentos" (tabela) | `transversal`, seção Referência |

**§5, o backlog:** as linhas que já eram "(roadmap #N)" continuam no roadmap da base 1 com o mesmo número. Os que não
tinham número: relatório de estudo da taxonomia → `b1 #40`; refazer as auditorias §11 → `b1 #41`; o alarme de cobertura →
`b1 #34`; o resíduo dos parênteses e os achados laterais → `b1 #29` e `#35`; intake da base 3 → `b3 #21` (feito);
detectores de comportamento → `transversal #11`; OBFCivel jul 30 × 180 s e o falso negativo do AgenteProcuracoes → `b2 #12` e `b2 #11`; o escopo de memória → `transversal #12`; o
racional do resíduo e do erro crítico → `transversal #8` e `#9`.

**§2, o feito:**

| Item antigo | Onde está agora |
|---|---|
| Docs do protocolo, `metadados_steps.py`, `drill_down.py critico`, S2/S2b, 4.2, 4.0, Ajuste 11, `audit_recompute9`, auditoria de 02/10, 4.2b-0, 4.2b, 4.2c | `b1 #44`–`#55` |
| S1, 4.1 (S2 na base 2), 4.2a, 4.1b/4.7 (base 2), 4.2d, Ajuste 13 | `b2 #5`–`#10` |
| 4.10 (parquet), 4.12 (o kit), 4.13 (Ajustes 14–16), monitoramento e kit no `.claude/`, racional dos hábitos, PR #29/#30, auditoria e blueprint, o plano limpo | `transversal #13`–`#20` (o 4.10 também em `b3 #21`) |
