# literature/ — fichamentos que sustentam a análise do trace

Quatro papers de taxonomia de erro de agentes, lidos em **texto completo** (apêndices incluídos) por subagentes
em 08/09/2026, para ancorar a categorização dos erros do trace da esteira jurídica.

## Nível de leitura — importante

Na escala de [`papers/reading-queue.md`](../../../papers/reading-queue.md), estes fichamentos são **🔎**: texto
completo lido por um agente, com extração dirigida por perguntas. Isso é mais forte que 📝 (verificação
bibliográfica) e **não é** ✅ (Rafael leu). Não colapsar em "lido" em nenhum entregável.

Toda a bibliografia foi conferida contra o próprio PDF — autoria, arXiv ID, data e venue. Método: `curl` no PDF +
`pdftotext -layout` (`WebFetch` em `arxiv.org` está bloqueado neste ambiente).

## Índice

| Arquivo | Paper | Para que serve nesta análise |
|---|---|---|
| [`mast-2503.13657.md`](mast-2503.13657.md) | **MAST** — Cemri et al., UC Berkeley, NeurIPS 2025 D&B | Os 14 modos de falha. Mostra que o MAST **não tem modo para "o código levantou exceção"** — a família dominante do trace cai fora do escopo dele por construção. |
| [`trail-2505.08638.md`](trail-2505.08638.md) | **TRAIL** — Patronus AI | Mede o **ponto cego**: ≥59% dos erros não levantam exceção. Traz o schema de anotação reusável e as 11 análises executáveis para abrir esse ponto cego. |
| [`agentdebug-2509.25370.md`](agentdebug-2509.25370.md) | **AgentDebug** — arXiv:2509.25370 | O **roteador módulo→tipo de memória** e a política de escrita "uma unidade por cascata, na raiz". O paper metodologicamente mais próximo da tese — mas **não** é precedente de memória persistente. |
| [`tool-use-errors.md`](tool-use-errors.md) | **ToolScan/SpecTool** (Salesforce, ICLR 2025 WS) + **ToolFailBench** (ICML 2026 WS) | Os 7 erros de tool-use e os 4 modos silenciosos. Contém a **tabela de detectores executáveis** traduzidos para o paradigma CodeAgent. |

## Correções que estes fichamentos produziram no relatório

1. A taxonomia do ToolScan citada na v1 do relatório **fora inventada pelo sumarizador de busca** — nenhum dos
   sete nomes aparece no paper. Corrigido em `tool-use-errors.md` §"ToolScan — status da verificação".
2. A afirmação "suposição sobre dados ≡ erros de argumento do ToolScan" **não se sustenta** — testada nos dados e
   refutada (1 caso de IAN, zero de IAV).
3. O mapeamento ao MAST era estruturalmente inválido: MAST rotula por *trace* como diagnóstico de causa-raiz; a
   análise do trace rotula por *step* como sintoma. Percentuais não são comparáveis.
