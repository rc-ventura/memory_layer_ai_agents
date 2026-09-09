# literature/ — fichamentos que sustentam a análise do trace

Duas camadas:

1. **Quatro fichamentos de leitura completa** (MAST, TRAIL, AgentDebug, ToolScan) — taxonomia de erro de
   agentes, lidos em **texto completo** (apêndices incluídos) por subagentes em 08/09/2026, para ancorar a
   categorização dos erros do trace da esteira jurídica. Nível 🔎, **exceto `agentdebug-2509.25370.md` →
   ✅ (Rafael leu, 09/09/2026)**.
2. **Quatro fichamentos breves** (seção própria abaixo) — adicionados em 09/09/2026 a partir de busca web,
   para dar contexto ao *próximo passo* (escalar a análise, construir unidades de memória). **Tier mais
   fraco:** bibliografia conferida só por busca web, resumo do abstract, texto não lido.

## Nível de leitura — importante

Na escala de [`papers/reading-queue.md`](../../../papers/reading-queue.md), estes fichamentos são **🔎**: texto
completo lido por um agente, com extração dirigida por perguntas. Isso é mais forte que 📝 (verificação
bibliográfica) e **não é** ✅ (Rafael leu). Não colapsar em "lido" em nenhum entregável.

**Exceção (09/09/2026):** `agentdebug-2509.25370.md` está em **✅** — Rafael leu via discussão dirigida em
sessão. MAST, TRAIL e ToolScan seguem 🔎.

Toda a bibliografia foi conferida contra o próprio PDF — autoria, arXiv ID, data e venue. Método: `curl` no PDF +
`pdftotext -layout` (`WebFetch` em `arxiv.org` está bloqueado neste ambiente).

## Índice

| Arquivo | Paper | Para que serve nesta análise |
|---|---|---|
| [`mast-2503.13657.md`](mast-2503.13657.md) | **MAST** — Cemri et al., UC Berkeley, NeurIPS 2025 D&B | Os 14 modos de falha. Mostra que o MAST **não tem modo para "o código levantou exceção"** — a família dominante do trace cai fora do escopo dele por construção. |
| [`trail-2505.08638.md`](trail-2505.08638.md) | **TRAIL** — Patronus AI | Mede o **ponto cego**: ≥59% dos erros não levantam exceção. Traz o schema de anotação reusável e as 11 análises executáveis para abrir esse ponto cego. |
| [`agentdebug-2509.25370.md`](agentdebug-2509.25370.md) | **AgentDebug** — arXiv:2509.25370 | O **roteador módulo→tipo de memória** e a política de escrita "uma unidade por cascata, na raiz". O paper metodologicamente mais próximo da tese — mas **não** é precedente de memória persistente. |
| [`tool-use-errors.md`](tool-use-errors.md) | **ToolScan/SpecTool** (Salesforce, ICLR 2025 WS) + **ToolFailBench** (ICML 2026 WS) | Os 7 erros de tool-use e os 4 modos silenciosos. Contém a **tabela de detectores executáveis** traduzidos para o paradigma CodeAgent. |

## Fichamentos breves — leitura de contexto (tier abaixo)

Adicionados 09/09/2026. **Não são 📝 nem 🔎:** a bibliografia (arXiv ID, título, data, autoria) foi conferida
contra páginas de resultado de busca web — **não contra o PDF primário** — e o resumo vem do abstract + páginas
de listagem, **sem leitura de texto completo**. Cada um resolve um item do [`docs/04-roadmap.md`](../docs/04-roadmap.md),
não a análise já feita. Antes de citar qualquer estatística destes em entregável, conferir no PDF.

| Arquivo | Fonte | Para que serve |
|---|---|---|
| [`insights-generator-2605.21347.md`](insights-generator-2605.21347.md) | **Insights Generator** — Scale AI, arXiv:2605.21347 | O **blueprint para escalar esta análise**: par Scout (propõe modo de falha numa amostra) + Investigator (valida no corpus inteiro com estatística) → relatório de insights. É a versão automatizável do que foi feito à mão nas 1.000 execuções. |
| [`silent-failures-2606.14589.md`](silent-failures-2606.14589.md) | **When Errors Become Narratives** — Wei Wu, arXiv:2606.14589 | Único outro estudo de taxonomia de causa-raiz por **trace longitudinal de um sistema de produção**. Dá vocabulário ao ponto cego do relatório: classes C (*error swallowing*), D (*chained hallucination*), E (*forensic blind spot*). |
| [`contrastive-trajectory-mining.md`](contrastive-trajectory-mining.md) | **CONTRAMEM** (arXiv:2608.22533) + **Self-Consolidation** (arXiv:2602.01966) | A ponte trace → unidade de memória: o par (execução ok / execução com o mesmo erro) na mesma classe de caso é onde está o sinal. Sustenta olhar as execuções sem erro (roadmap item 2) e a "curadoria localizada, não append-only". |
| [`failure-attribution-2505.00212.md`](failure-attribution-2505.00212.md) | **Who&When** — Zhang et al., ICML 2025 | Mede que um LLM acha o **passo decisivo** de uma falha com ~14% de acerto → argumento a favor dos detectores determinísticos por regra (roadmap itens 1, 4, 6). Traz o eixo "agente responsável × passo decisivo". Inclui PrefixGuard (trace → sinal de aviso online) como relacionado. |

## Correções que estes fichamentos produziram no relatório

1. A taxonomia do ToolScan citada na v1 do relatório **fora inventada pelo sumarizador de busca** — nenhum dos
   sete nomes aparece no paper. Corrigido em `tool-use-errors.md` §"ToolScan — status da verificação".
2. A afirmação "suposição sobre dados ≡ erros de argumento do ToolScan" **não se sustenta** — testada nos dados e
   refutada (1 caso de IAN, zero de IAV).
3. O mapeamento ao MAST era estruturalmente inválido: MAST rotula por *trace* como diagnóstico de causa-raiz; a
   análise do trace rotula por *step* como sintoma. Percentuais não são comparáveis.
