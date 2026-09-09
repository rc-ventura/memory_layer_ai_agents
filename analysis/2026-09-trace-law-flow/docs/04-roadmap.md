# Roadmap — o que falta

**Atualizado:** 2026-09-08. Consolidação do que ficou em aberto ao longo da análise do primeiro trace.
Prioridades e decisões de escopo confirmadas com o Rafael. Ver também
[`../../../discussion/open-questions.md`](../../../discussion/open-questions.md) para a versão canônica da
discussão de escopo (groundedness determinístico vs. juiz) registrada no nível do projeto, não só desta pasta.

## Urgente — estrutural, não analítico

- [ ] **Criar branch e commitar todo o trabalho.** Hoje tudo (pasta `analysis/` inteira + edições em
  `.gitignore`, `CLAUDE.md`, `README.md`, `papers/reading-queue.md`) está direto no `main`, não versionado.
  Pela convenção do projeto: branch `2026-09-08-<slug>`, depois commit.

## Monitoramento — não é candidato ativo, mas tem gatilho de reabertura

- [ ] **"Resposta sem bloco de código" (Protocolo do harness).** Rebaixado da v1 por ficar concentrado em
  dez/2025 (31/33 casos) e sumir depois (0 em 3.461 steps de mai–ago/2026). Rótulo é `[INATIVO desde
  dez/2025]`, não `[RESOLVIDO]` — não sabemos a causa e não controlamos o harness. **Gatilho de reabertura:**
  ≥2 casos num mês, ou taxa > 1/1k steps (teto do IC95% do regime pós-incidente). Verificar a cada nova
  extração do trace. Ver `02-relatorio-achados.md` §6.

## Fora de escopo / adiado

- ~~**Groundedness semântico** (o juiz que confirma se a citação está CERTA, não só se aparece)~~ —
  fora de escopo do v1. Exige LLM-as-judge ou humano — não-determinístico, incompatível com o princípio já
  documentado de que o v1 inteiro é regra fixa e auditável (ver
  [`../../../discussion/open-questions.md`](../../../discussion/open-questions.md), item "Which parameters...
  should become adaptive"). Pertence a observabilidade/agent-evals como disciplina própria, ou a um v2 que
  relaxe a restrição de determinismo.
- **Minerar o candidato 1 automaticamente** (schema de retorno sem LLM) — adiado, não é prioridade agora.

## Analítico — em aberto, em ordem de valor

| # | Item | O que falta, em uma frase |
|---|---|---|
| 1 | **Groundedness-como-presença (determinístico)** | Extrair tokens tipados (CNJ, CPF/CNPJ, data, valor) do `final_answer` e checar se o texto aparece literalmente em alguma observação anterior — regex puro, zero LLM. **Reclassificado de "fora de escopo" pra ativo em 2026-09-08**: é proxy (presença ≠ correção), mas é determinístico, cabe no pipeline "por hora" tanto quanto os 8 achados de hoje. |
| 2 | **Rodar detectores nas execuções sem erro — versão determinística primeiro** | 91,4% dos steps (5.283 de 5.781) nunca foram olhados semanticamente. Antes de cogitar juiz LLM, tentar o proxy determinístico já esboçado durante a leitura do AgentDebug: contar `code_action` com padrão de validação (`assert`, `if not`, `len(`, `is None`, `try/except` com recuperação) vs. steps que só consomem sem checar. Juiz LLM/anotação manual só se o proxy não bastar. |
| 3 | **Segunda extração sem `LIMIT`** | O trace tem exatamente 1.000 linhas (provável `LIMIT`) — amostra, não população. Confirmar também com o time da esteira o que os status 1/2/3/34 realmente significam (hoje inferido por correlação). |
| 4 | **Instruction Non-compliance** | Nossa taxonomia inteira é baseada em exceção; o TRAIL mostra que, na arquitetura idêntica à nossa, esse é o erro nº 1 (35,5%) e nunca levanta exceção. Escrever um detector determinístico por regra explícita do system prompt. |
| 5 | **Resolver Tool-Skip de vez** | Nunca convergiu: deu 14 / 8 / 10 execuções em três rodadas, dependendo do inventário de ferramentas usado. Corrigir extraindo o inventário **por papel**, não a união de todos; depois testar robustez como os outros seis achados desta sessão. |
| 6 | **Reasoning-action mismatch — versão determinística primeiro** | A versão por palavra-chave foi retirada por estar conceitualmente errada (comparava thought pré-execução com erro pós-execução) — isso não muda. Mas existe uma versão determinística diferente, já esboçada: comparar o nome de agente/ferramenta que o *thought* anuncia (regex) contra o que o `code_action` de fato chama (AST), no mesmo step — divergência = candidato, sem juiz. Só tentar juiz LLM/anotação manual se essa comparação estrutural não capturar o fenômeno. |

## Fundamentação emprestada do AgentDebug (arXiv:2509.25370)

Três achados do paper que embasam decisões acima. **Todos são sobre os benchmarks do AgentDebug**
(ALFWorld/WebShop/GAIA — espaço de ação fechado, reward automático, single-agent), **não medidos neste
trace** — entram como justificativa atribuída, com a ressalva de domínio. Registro completo e caveats em
[`../literature/agentdebug-2509.25370.md`](../literature/agentdebug-2509.25370.md).

1. **"Focar em causa-raiz, não em consertar todo erro de superfície, é o que dá ganho"** (ablação, §1,
   verbatim: *"focusing on root-cause errors, rather than attempting to fix every surface-level mistake, is
   key to efficient debugging and meaningful performance gains"*). Ressalva: ablação no benchmark deles.
   **Sustenta** a política de escrita **"uma unidade de memória por cascata, na raiz"** — não uma por step
   com erro (≈498 steps com erro → ~150–250 raízes de cascata, menos após dedup por assinatura). Ver
   [`../../../discussion/knowledge-as-infra-architecture-hypothesis.md`](../../../discussion/knowledge-as-infra-architecture-hypothesis.md)
   §C.

2. **"Error propagation is the primary bottleneck… early mistakes cascade"** (insight central, §2.1).
   Ressalva: afirmação do paper, **ilustrada não medida** — o AgentDebug não tem métrica de propagação (só
   a Figura 8, ilustrativa). **Sustenta** priorizar as análises de cascata abaixo (candidatas a entrar na
   tabela analítica acima), além do coeficiente básico `1,8×` já computado (`03-procedimento-validacao.md`
   §1.6):
   - **Coeficiente de propagação estratificado** — `P(erro em k+1 | erro em k)` vs.
     `P(erro em k+1 | sem erro em k)`, por papel e por tipo de erro.
   - **Iniciador vs. seguidor** — distribuição de `first_err_type` vs. `err_type` em todos os steps: se
     diferem, alguns tipos iniciam a cascata e outros só a seguem.
   - **Custo por cascata** — `sum(tokens | step ≥ first_err_step)` vs. `sum(tokens | step < first_err_step)`:
     decompõe o "~3× mais tokens" em quanto vem da cascata vs. do erro isolado.
   - **Posição normalizada** — `SyntaxError` concentra cedo (agente formatando), `KeyError`/`TypeError`
     concentram tarde (agente manipulando dados): separa erro de forma de erro de conteúdo por posição.

3. **Detecção de erro crítico: 45% de acerto de passo / 24,3% no critério estrito** (passo + módulo + tipo),
   com dependência de **ordem de magnitude** no modelo analista (GPT-4.1 ~32% estrito vs. modelos menores
   ~2% — Tabela 1 e Figura 7b). Ressalva: usar a Tabela 1 — o box "Findings" do paper reporta 50,0/42,5,
   que não bate com a própria tabela nem com a Figura 7b; citar sempre os dois valores (passo e estrito).
   **Sustenta** o princípio já aplicado nos itens 1, 4 e 6: um LLM pedido para localizar o step / classificar
   a causa é **gerador de candidatos, não rotulador** — o backbone tem de ser determinístico (tipo de
   exceção, AST do `code_action`, presença de texto no `model_input_messages`), com juiz LLM só onde o
   determinístico comprovadamente não captura o fenômeno. Ver `03-procedimento-validacao.md` Frente 2.

## Fechado nesta sessão

- [x] **Auditoria independente respondida** — 6 discrepâncias (S1–S6) verificadas uma a uma contra o dado
  (não contra o texto do parecer) e corrigidas; S3 mostrou-se pior que o relatado (1 linha errada **+ 2
  famílias omitidas**). O gap de bijeção também foi fechado: o achado central ganhou passo-a-passo próprio
  (`01-racionais.md` §3) e o documento ganhou nota declarando o que cobre. O item que a auditoria não
  conseguiu verificar (`.gitignore` vs. raw CSV) foi verificado — está limpo. Ver
  [`../audit/2026-09-08-auditoria-independente.md`](../audit/2026-09-08-auditoria-independente.md) §6.

- [x] **Gráficos para os 8 achados novos** — 6 construídos (Pareto, assinatura por papel, tokens/chamada,
  ranking duplo, evolução mensal, funil de sucesso verificado), 2 avaliados e deliberadamente não construídos
  (3.2 e 2.3 — poucos pontos / achado principal retirado no teste de robustez). Três bugs achados e corrigidos
  ao conferir visualmente (rótulos sobrepostos, percentual com base errada, legenda truncada).

## Fora da análise do trace em si

- **Promover os fichamentos de 🔎 pra ✅** — [x] **`AgentDebug` promovido a ✅ em 09/09/2026** (leitura dirigida
  em sessão — taxonomia, 5 módulos, Stages 1–3, erro crítico, re-rollout, o que adotar/não adotar). Faltam
  **MAST, TRAIL e ToolScan** — ainda lidos só por subagente.
- **A reunião de apresentação ainda não aconteceu** — toda a sessão até aqui foi preparação.
- **Construir os candidatos de memória de verdade**, reusando este pipeline — ainda não começado.
