> **Fichamento breve — tier abaixo dos quatro 🔎 desta pasta.** Bibliografia do paper principal conferida (proceedings.mlr.press/v267 + arXiv + repo `ag2ai`); resumo por busca web, **texto completo não lido**. Estatísticas "conforme reportado". `Lido por Rafael: não`.

# Which Agent Causes Task Failures and When? — On Automated Failure Attribution of LLM Multi-Agent Systems (Who&When)

- **Autores:** Shaokun Zhang, Ming Yin, Jieyu Zhang, Jiale Liu, Zhiguang Han, Jingyang Zhang, Beibin Li, Chi Wang, Huazheng Wang, Yiran Chen, Qingyun Wu (Penn State + Duke + …)
- **Ano:** 2025 · **Venue:** ICML 2025 (Spotlight) · **arXiv:** 2505.00212 · **Repo:** github.com/ag2ai/Agents_Failure_Attribution
- **Link:** <https://arxiv.org/abs/2505.00212>
- **Tags:** failure-attribution, decisive-step, who-and-when, llm-as-judge-limits, benchmark

## O que é

Formaliza a tarefa de **atribuição automática de falha**: dado o log de um sistema multi-agente que falhou, apontar (a) o agente responsável e (b) o **passo decisivo** onde a falha se determinou. Dataset **Who&When**: logs de falha de 127 sistemas multi-agente, com anotação fina ligando cada falha a um agente e a um passo. Três métodos: *all-at-once* (mostra o log inteiro e pergunta direto), *step-by-step* (incremental) e híbrido.

**Resultado que importa:** o melhor método acerta **53,5%** o agente responsável, mas só **14,2%** o passo decisivo. Modelos de raciocínio SOTA (o1, R1) não chegam a utilidade prática. Follow-up **Who&When Pro** (arXiv:2607.09996): 12.326 trajetórias, 26 benchmarks — atribuição de trajetória completa supera a incremental.

## Relevância para o projeto

1. **Argumento a favor da abordagem determinística.** O relatório rotula por **step-como-sintoma**. Este paper mede que pedir a um LLM para achar o passo decisivo num trace é ~14% confiável. Isso sustenta a decisão (roadmap itens 1, 4, 6) de escrever detectores determinísticos por regra em vez de juiz LLM para localização de passo.
2. **Vocabulário "agente responsável × passo decisivo"** é o eixo que falta na taxonomia atual, que é por causa-raiz de trace (como MAST) e por step isolado — não por *qual* handoff entre papéis determinou o resultado.

## Relacionados (não buscados a fundo)

- **PrefixGuard — From LLM-Agent Traces to Online Failure-Warning Monitors** — arXiv:2605.06455 (Huang et al.). Aprende, sobre **prefixos** de trace, um sinal binário de aviso precoce de falha, para intervir no meio da execução. É a forma *preditiva* do "trace → sinal" — relevante para um eventual monitor online (v2), não para o v1 determinístico pós-hoc.
- **AGENTSCOPE / Diagnosing with Insights** — arXiv:2609.02371 (neuro-simbólico; reporta superar Who&When).
- **Attributing Failures via Spectrum Analysis** — arXiv:2509.13782.
- **When Only the Final Text Survives: Implicit Execution Tracing for Multi-Agent Attribution** — arXiv:2603.17445.

---
Adição nova.
