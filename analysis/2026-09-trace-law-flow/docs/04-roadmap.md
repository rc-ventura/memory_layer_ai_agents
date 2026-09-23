# Roadmap — o que falta

**Atualizado:** 2026-09-23 (datação por `dat_hor_inio_exeo`: auditorias a refazer, errata, item 27). Em 19/09 passou ao formato simples — check + frase +
links; o detalhe mora no doc linkado, não aqui. Versão longa anterior está no histórico git.

Cada item: o que fazer em uma frase + `→` onde está o contexto. Decisões de escopo do projeto:
[`../../../discussion/open-questions.md`](../../../discussion/open-questions.md).

## Agora

- [ ] **Entregar ao tutor o doc de schema + taxonomia de erros** — pedido da reunião de 18/09: onde o erro
  mora no trace (`error` no `ActionStep`), a taxonomia do mais genérico ao mais específico, evidência no
  cru. Serve de base para a query que extrai da base ~1M um dataset só de erros. → [`../../schema-e-taxonomia-de-erros.md`](../../schema-e-taxonomia-de-erros.md)
- [ ] **Relatório de estudo da taxonomia de erros** — logo depois da entrega ao tutor: cada família
  explicada + evidência no cru + `exec_id`s para `drill_down.py`, com o **gráfico-guia "genealogia"**
  (árvore `error` → família → assinatura → submecanismo → unidade de memória → decisão, contagem real por
  nó — **Sankey entregue 21/09 no `09-metodologia-erro-a-memoria.md` §1.1**, gerado por
  `pipeline/genealogia_sankey.py`; falta o aprofundamento família por família) e o teste de cobertura na
  extração ~1M ("Sintoma não reconhecido" do `classify()` = candidato a erro novo). Guideline completo → [`../../schema-e-taxonomia-de-erros.md`](../../schema-e-taxonomia-de-erros.md) §7
- [ ] **Criar branch e commitar o trabalho** — convenção `YYYY-MM-DD-slug`; hoje há edições em `main` sem
  branch (docs 04/05/08, diário).
- [ ] **Refazer as auditorias independentes das pastas de evidência §11** — em 23/09 o `mes` passou a vir de
`dat_hor_inio_exeo` (não de `anomesdia`) e as regras de escolha de casos, que ordenam por (mês, exec_id, idx),
trocaram casos em 8 das 10 pastas `11.x` (na 11.9 só mudam as contagens por mês; a 11.6 não é afetada). As pastas foram regeneradas e conferem contra o cru, mas **os
`relatorio_independente.md` de cada pasta e os `relatorio_meta_11.1-11.8.md` / `relatorio_meta_11.1-11.10.md`
auditaram a amostra antiga e estão desatualizados** — não citar como verificação da amostra atual até refazer.
Os `audit/scripts/audit_recompute*.py` já leem o mês real; as saídas e os valores "esperados" neles (ex.: "26/33
em dez/2025") são da datação antiga → `03-procedimento-validacao.md` §1.12
- [x] **Errata das afirmações datadas pelo lote** — feita em 23/09: 69 trechos recalculados com o mês real;
o que mudou de conclusão (incidente em out/2025; leitura de estabilidade do schema na 07 §11.5) está listado em
→ `03-procedimento-validacao.md` §1.12

## Próximos — em ordem de valor

| # | Item | Contexto |
|---|---|---|
| 1 | **Dataset de erros da base completa (~1M) via query** — montar a query com o tutor a partir do doc de schema (catch-all = `error` presente → `error.type` → `error.message`), replicar a §11 do notebook na base nova (teste de replicação das unidades nº2/nº10), confirmar semântica dos status 1/2/3/34 com a esteira | `../../schema-e-taxonomia-de-erros.md` · `open-questions.md` ("Second trace extraction") · `05-schema.md` §Aberto |
| 2 | **Groundedness-como-presença (determinístico)** — tokens tipados (CNJ, CPF, data, valor) do `final_answer` checados contra observações anteriores; ordenar a fila pelo crosstab erro×resposta-entregue (310 execs); é o mesmo mecanismo do *Output-Fabrication* do item 13 | `01-racionais.md` §4 · `02-relatorio-achados.md` §3.1 |
| 3 | **Detectores nos steps sem erro (91,4% nunca olhados)** — proxy determinístico primeiro: padrões de validação no `code_action` (`assert`, `if not`, `len(`, `try/except`) | `../literature/agentdebug-2509.25370.md` |
| 4 | **Instruction Non-compliance** — erro nº1 do TRAIL (35,5%), nunca levanta exceção; detector por regra explícita do system prompt | `../literature/trail-2505.08638.md` §4 (#4) |
| 5 | **Resolver Tool-Skip de vez** — nunca convergiu (14/8/10); extrair inventário de ferramentas **por papel**, não união | `02-relatorio-achados.md` §7 · passa a viver no notebook do item 26 |
| 6 | **Reasoning-action mismatch (determinístico)** — thought anuncia X (regex) × `code_action` chama Y (AST), no mesmo step; é o *Tool Selection Errors* do TRAIL | `trail-2505.08638.md` §4 (#2) · passa a viver no notebook do item 26 |
| 7 | **Erro estrutural de argumento de tool** — chamada real (AST) × assinatura declarada no system prompt; "camada 1.5", não cobre erro de valor | `05-schema.md` §ActionStep |
| 8 | **Decompor custo por chamada de ferramenta** — contexto re-enviado × trajetória longa. Antes: ler os ~10 JSONs mais caros (estrutura, não conteúdo — PII) | `01-racionais.md` §3.3–3.4 |
| 9 | **Decompor a subida mensal de tokens** — erro × baseline limpo × trajetória, por mês; resolve a ressalva do §3.6 | `01-racionais.md` §3.6 |
| 10 | **PlanningStep — eval plano×execução** (só `RespostaBacen`/`CalculoTrabalhista`) + gráfico `err_type` (`AgentExecutionError` × `AgentParsingError`, por mês/papel — a coluna já existe, custo zero) | `05-schema.md` §PlanningStep · `08-*.md` |
| 11 | **Gold-standard anotado por especialistas** — pré-requisito para confiar em qualquer juiz LLM | `open-questions.md` ("gold-standard") |
| 12 | **9 detectores TRAIL restantes** — ranqueados por custo no fichamento §4 | `trail-2505.08638.md` §4 · passa a viver no notebook do item 26 |
| 13 | **5 detectores ToolScan/ToolFailBench** — já desenhados no fichamento; Output-Fabrication primeiro (≈ item 2) | `../literature/tool-use-errors.md` §"Tradução para o paradigma CodeAgent" · passa a viver no notebook do item 26 |
| 14 | **Curva de erro por maturidade da ferramenta** — inventário por execução (não colapsado), "nascimento" de cada tool via `anomesdia` × `cod_vers_aget`, taxa de erro × tempo de exposição. **Resgatado de commit órfão `d7e4173` (nunca mergeado — branch `claude/analise-erros-novas-ferramentas-wofgw6`)**; bloqueado em confirmar se `cod_vers_aget` reflete mudança de toolset | `open-questions.md` (blind spot de falha silenciosa) · `05-schema.md` §Aberto |
| 15 | **Evidência por análise para §1–§10 do notebook** — mesmo padrão da §11 (pasta de evidência por análise); começar pelo achado central 86,3%/11,9% | `03-procedimento-validacao.md` ("Evidência por análise") |
| 16 | **Detector de anomalia de ambiente** — retorno que contradiz a forma histórica estável da ferramenta = mudança de API; testar primeiro na segunda extração | `06-racionais-mineracao-unidades-n2-n10.md` §9 |
| 17 | **Análise funda: de onde vem o conhecimento do schema da nº2** — "sabia e errou a profundidade" × "nunca viu"; não bloqueia a memória | `03-procedimento-validacao.md` §1.9 |
| 18 | **Construir os candidatos de memória de verdade (camada 2)** — `description`/`impact`/`correction_guidance` derivados por método (LLM + validação de amostra), não à mão; sequenciar para quando começar a construção | `01-racionais.md` §8 |
| 19 | **`memory_payload` em `unidades_memoria.json`** — gerar sub-objeto (`description`, `correction_guidance`, `scope`) em `registro_final`, só nas unidades com `destino` ≠ harness | `06-racionais-mineracao-unidades-n2-n10.md` §9 |
| 20 | **Promover MAST e ToolScan/ToolFailBench de 🔎 para ✅** (leitura própria) — AgentDebug ✅ 09/09, TRAIL ✅ 15/09 | `../literature/README.md` · `papers/reading-queue.md` |
| 21 | **Reenquadrar o §8.8 como "papel → taxonomia de erros" (descritivo puro)** — hoje o gráfico funde duas camadas: descrição (que tipos de erro cada papel comete) e decisão de memória (cinza "candidata/não vira memória" importa a triagem do §9 para um gráfico que deveria ser só descritivo). Refazer como papel × unidade de lição, sem terminologia de memória/candidata — harness/resíduo viram só mais categorias ("outras" neutro). A decisão de candidatura fica toda no §9. **E a terminologia "unidade/candidata" precisa ser revista** — o que confunde é chamar de "unidade de memória" um agrupamento que inclui erros que nunca viram memória. Extensão possível: hoje `triagem()` decide por unidade **global** (conta execs/meses da unidade inteira); candidatura por (papel × unidade) seria análise nova | `analise_trace_esteira_juridica.ipynb` §8.8/§9.3 · `base_pipeline.py` `triagem` |
| 22 | **Eixo de severidade (`impact`) na triagem — aberto: decidir o desenho antes de implementar** — motivação já registrada no fichamento TRAIL: sem severidade, 223 `SyntaxError` baratos e recuperáveis pesam o mesmo que uma alucinação de número de processo; Fig. 6 do TRAIL: Hallucinations 89% HIGH × Output Generation só 12% HIGH; ~79% dos HIGH são invisíveis a exceção. O destino é uma coluna `impact` na triagem e dois rankings lado a lado (frequência × tokens × gravidade), no espírito do §3.5. **Mas não é simples: quem anota e com que rubrica exige análise própria (Rafael, 21/09)** — o TRAIL usou 4 anotadores humanos (~2h/trace, sem κ formal, só taxa de revisão ~5%) e o melhor LLM-as-judge do paper acerta 11% conjunta; a rubrica HIGH/MEDIUM/LOW em si não está no paper. Caminhos a comparar: (a) rubrica determinística consultando o trace (resposta final degenerada via `medir_sucesso`/`DEGENERADO`; erro cruzou para saída externa; só custou token); (b) anotação humana em amostra → casa com o item 11 (gold-standard). Se optar por (a), entra como heurística nova na escada de validação: robustez antes de virar ranking. Relacionado: o item 18 já menciona `impact` como campo do candidato de memória — alinhar os dois | `../literature/trail-2505.08638.md` §"O schema é reusável no nosso trace?" + §2 "Onde dói mais: impacto" · `01-racionais.md` §3.5/§8 · item 11 · item 18 |
| 23 | **Refinar o split de `nome_nao_definido`: separar "inventado" de "definido-mas-expirado-entre-steps"** — auditoria no cru (21/09, motivada pela aresta cruzada do Sankey "Função bloqueada → `nome_nunca_definido`") mostrou que os 2 erros não são nomes inventados: o agente definiu o helper (`get_metadado`, `filtrar_principais`) num step sem erro e o sandbox "esqueceu" a definição — padrão consistente: **def de função só vale para o mesmo bloco ou o imediatamente seguinte; variáveis persistem**. Execs `26e300f1` (nov/25) e `43701975` (mai/26); ambas se recuperaram redefinindo (o agente escreve "# Redefinindo a função auxiliar"). Ajuste: terceiro ramo no split — "o nome tem `def` num `code_action` anterior sem erro?" — mais linha no `SUB2UNI`/`UNI`. **Checar:** se mover os 2 erros, `U_nome_inventado` fica com 3 — confirmar que ainda bate `MIN_EXECS`/`MIN_MESES`. Nuance: "defs não persistem entre steps" é **propriedade do harness**, não padrão de erro — pode virar candidato factual/ambiental por justificativa própria (verificável contra o executor da esteira), sem depender da régua de recorrência. Re-verificar na extração ~1M (item 1) | `base_pipeline.py` `submecanismo`/`montar_unidades` · `09-metodologia-erro-a-memoria.md` §1.1 · item 1 |
| 24 | **Explodir `txt_vrvl_locl` — medir o contrato real na população** — hoje o contrato de retorno é *inferido* (mensagem de erro + drill-down de caso); o `locals()` final por papel guarda o **retorno real das ferramentas** → vira estatística ("das N execuções que chamaram `extrair_evidencias`, o retorno tinha chaves X/Y/Z em n%") e permite cruzar o campo pedido no erro com as chaves presentes. **Caveat estrutural:** é o estado *final* do papel, não o estado no step do erro — responde bem "qual é o contrato real", mal "o que o agente enxergava no step n". Granularidade nova (por papel×exec, não por step) → passada própria, notebook com range §12.x; extrai tipo/forma/chaves, **nunca valores** (é a coluna mais densa em PII). Roda já na base 1 — não depende da extração ~1M | `../../schema-e-taxonomia-de-erros.md` §5 · item 1 |
| 25 | **Medir `cod_vers_aget` — versão do agente como dimensão registrada** — hoje ninguém lê; extrair versão por execução (uma coluna, custo zero) e reportar a distribuição papel × versão, sem cruzar nada ainda. Habilita a pergunta futura "o mesmo papel em versões diferentes erra diferente?" e **destrava o item 14**, que está bloqueado exatamente em confirmar se `cod_vers_aget` reflete mudança de toolset. Mesma classe de pendência que a semântica dos status 1/2/3/34: confirmar com a esteira o que a coluna registra | `05-schema.md` §Aberto · item 14 · `open-questions.md` |
| 26 | **Separar falhas silenciosas em notebook próprio — decisão de Rafael, 22/09.** O notebook da esteira (`analise_trace_esteira_juridica.ipynb`) fica só com erro **visível por exceção** (§1–§6, §8–§10); o §7 de hoje (Result-Ignore/RAC/Tool-Skip + a nota do detector Reasoning-action-mismatch retirado) migra por completo pra um notebook novo, dedicado a construir detectores determinísticos de erro **invisível** com o mesmo rigor de uma passada própria (não é só mudar de arquivo — é reconstruir, testar robustez, documentar). Motivo do corte: método diferente do resto do notebook da esteira (mesma lógica que já separou a mineração das unidades nº2/nº10 em `mineracao_unidades_n2_n10.ipynb`), e Rafael quer investir tempo/rigor real nisso, não só adicionar células. **Numeração:** §11.x é da mineração, §12.x já está reservado pro item 24 (`txt_vrvl_locl`) — este notebook novo toma **§13.x**. Par de docs novo: `10-racionais-falhas-silenciosas.md` / `11-relatorio-falhas-silenciosas.md` (`08-*.md` está reservado pro item 10; `09-*.md` já existe). **O menu de detectores a construir lá é o que os itens 5, 6, 12 e 13 já apontavam** — os 5 do ToolScan/ToolFailBench (tabela "modo de falha → análogo em CodeAgent → detector executável" + "Ordem de execução recomendada") e os 9 do TRAIL (tabela "análises executáveis", ranqueadas por impacto×facilidade) — esses 4 itens passam a alimentar este notebook, não o atual. **Pré-requisito já feito (22/09):** as primitivas que o §7 usava soltas em células — `bykey` (construído na célula 31, do §6, e usado de carona pelo §7: dependência escondida que quebraria o notebook novo), o inventário `INV` e o percurso do AST — subiram para `analysis/base_utils.py` (raiz, importável por qualquer análise), junto com o mecanismo genérico "entidade tipada sem suporte" que os itens 2, 13 e o IAV-b vão usar; reproduz os números do §7 exatamente. As células do notebook atual ainda não foram trocadas — isso acontece junto com a extração. Pendente: decidir o ponto de corte exato antes de mover código (Rafael, 22/09) | `../literature/tool-use-errors.md` §"Tradução para o paradigma CodeAgent" · `trail-2505.08638.md` §4 · `analise_trace_esteira_juridica.ipynb` §7 (células a extrair) · itens 5, 6, 12, 13 |
| 27 | **Confirmar com a esteira o que é `anomesdia` e como cada extração escolheu suas linhas** — hipótese: data de corte da democratização da base (1 valor por mês, sempre posterior à execução). A base 2 (lote de ago/2026) é **independente** da base 1: 0 `exec_id` em comum (`checklist.py` §6, 23/09) e execuções de 9 meses reais (dez/2025–ago/2026, 88% em jun–ago) — a triagem canônica (≥2 meses) funciona nela, sem regime especial. Falta saber o critério de seleção das 1.000 linhas de cada extração (aleatório? filtro por status?) | `05-schema.md` §Datas e §Aberto 9 · `03-procedimento-validacao.md` §1.12 |
| 28 | **Corrigir "CalculoCivel é o pior por %" (§3.5)** — com o corte de 50 mil tokens, `JoogleAnalytics` (28,0%) e `OficiosResposta` (26,3%) ficam acima do `CalculoCivel` (25,0%); os dois têm 10–15 steps. O texto só vale "entre os papéis com volume relevante" — explicitar isso ou criar um piso de amostra no ranking por % (achado em 23/09, quando o print fixo do notebook virou valor calculado) | `01-racionais.md` §3.5 Passo 3 e 5 · `02-relatorio-achados.md` §3.5 |
| 29 | **Aplicar o procedimento do resíduo ao padrão dos parênteses** — `SyntaxError: closing parenthesis <q> does not match opening parenthesis <q>` está em "revisar — prioridade" na base 1 (3 execuções, 2 meses). Rodar a base 2 com o pipeline novo antes, para escolher as regras pelos padrões que se repetem nas duas bases (inclui o argumento nomeado inexistente no `final_answer`, 1 caso na base 1) | `03-procedimento-validacao.md` Frente 3 · `drill_down.py padrao` |

## Monitoramento — gatilho de reabertura

- [x] **"Resposta sem bloco de código" (Protocolo do harness)** — inativo só *dentro da base 1* (1.000
  registros, nov/2025–ago/2026): não assumir resolvido nem inativo, como este item já avisava. **Gatilho
  disparado em 22/09/2026**: rodando o mesmo pipeline numa segunda base (ago/2026, 1.000 registros), o erro
  reapareceu bem acima do limiar (≥2 casos/mês ou taxa > 1/1k steps) — ver diário de campo, entrada
  22/09/2026. Rótulo `[INATIVO]` removido do código (`base_pipeline.py`) e da documentação (`02-relatorio-
  achados.md` §6, `schema-e-taxonomia-de-erros.md`, `genealogia_sankey.py`) por estar desatualizado.
  **Pendente:** reclassificar formalmente (tipo/decisão) esta unidade quando a base 2 for integrada ao
  pipeline (item 1) — hoje ela segue com `tipo=NAO` porque a integração ainda não aconteceu, não porque o
  achado tenha sido revalidado. → `02-relatorio-achados.md` §6

## Fora de escopo / adiado

- ~~Groundedness semântico (juiz)~~ — fora do v1 determinístico; v2 ou disciplina de agent-evals. → `open-questions.md`
- **Replay contrafactual** (teste de suficiência da memória) — depende de rodar a esteira; combinar com o
  time junto com a divergência de documentação. → `06-*.md` §9 Passo 7
- **Análise funda `extrair_evidencias`** — checada e descartada 17/09 (8 execuções, sem campo mensurável);
  registro de que foi investigada. → `03-procedimento-validacao.md` §1.10

## Fechado

- [x] Mineração das unidades nº2/nº10 — Passos 1–8, verificação humana Passo 6, destino da nº10 = `harness`
  (9/21 = 43% payloads inválidos), divergências de documentação levadas à plataforma. → `06-*.md` · `07-*.md` · `03-*.md` §1.7–1.11
- [x] Auditoria independente das 10 pastas de evidência §11 + meta-relatório 11.1–11.10 (18/09) + decisão
  `avulso/`. → `pipeline/resultados/evidencia/relatorio_meta_11.1-11.10.md`
- [x] Auditoria independente do pipeline respondida (S1–S6). → `../audit/2026-09-08-auditoria-independente.md` §6
- [x] Gráficos dos 8 achados novos (6 construídos, 2 deliberadamente não). → `02-relatorio-achados.md`
- [x] Resíduo do Passo 5 (`AttributeError`, cobertura nº2: 89/91→91/91) + `correction_guidance`
  simplificada. → `06-*.md` §9 · `03-*.md` §1.9
- [x] Doc "metodologia" — entregue em duas camadas (21/09): o **método genérico** (pré-artigo, cinco elos
  com racionais e fundamentação) em `discussion/hipoteses/trace-error-taxonomy-methodology/general-error-taxonomy-methodology.md`;
  a **instanciação** (cadeia visual, dois eixos, cardinalidades, exemplo "Could not index", mapa
  elo→gráfico) em `09-metodologia-erro-a-memoria.md` — movido para o `docs/` da análise em 21/09 (decisão
  do Rafael: a análise é dona dos seus resultados). O que segue faltando é a figura da **genealogia por
  nó** (contagem real por aresta) — continua no item "Relatório de estudo" acima; a versão do doc genérico
  é esquemática (contagem por nível, não por nó).
- [x] Fichamentos promovidos: AgentDebug ✅ (09/09), TRAIL ✅ (15/09). → `../literature/README.md`

## Conceitos e apresentação — onde moram agora

- **Camadas de "causa" (0/1/2)** → `01-racionais.md` §8
- **Fundamentação emprestada do AgentDebug** → `../literature/agentdebug-2509.25370.md`; a política "uma
  unidade por cascata, na raiz" → `01-racionais.md` §7 + `../../../discussion/knowledge-as-infra-architecture-hypothesis.md` §C
- **Propagação 1,8× / propagação crítica 0/1.550 / 99,3%** → `02-relatorio-achados.md` · `03-*.md` §1.6
- **Análises de cascata propostas** (coeficiente estratificado, iniciador×seguidor, custo por cascata,
  posição normalizada) — seguem abertas, dentro do item 1 quando a base completa chegar.
- **Censo `"Thought:"` por papel + `PlanningStep`** → `05-schema.md`
- **`error.type` como eixo nativo (err_type)** → `05-schema.md` §ActionStep · `08-*.md`
