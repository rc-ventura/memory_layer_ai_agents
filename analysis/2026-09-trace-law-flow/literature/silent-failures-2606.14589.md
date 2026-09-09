> **Fichamento breve — tier abaixo dos quatro 🔎 desta pasta.** Bibliografia conferida por busca web + `WebFetch` do abstract em 2026-09-09, **não contra o PDF completo**. Texto completo não lido. Estatísticas "conforme reportado". `Lido por Rafael: não`.

# When Errors Become Narratives — A Longitudinal Taxonomy of Silent Failures in a Production LLM Agent Runtime

- **Autor:** Wei Wu
- **Ano:** 2026 (submetido 12/06/2026)
- **Venue:** arXiv:2606.14589
- **Link:** <https://arxiv.org/abs/2606.14589>
- **Tags:** silent-failure, production, longitudinal, root-cause, error-swallowing, observability-gap

## O que é

Estudo **longitudinal de 8 semanas** de um agente assistente pessoal em produção contínua desde março/2026. 22 incidentes com postmortem de causa-raiz completo, num sistema com 40 jobs agendados, 8 provedores de LLM, proxy de tool-governance, memória de knowledge-base, 4.286 testes unitários e 827 checks de governança.

**Taxonomia de 5 classes, orientada a mecanismo:**
- **(A) Environment & platform quirks** — anomalias de nível de sistema.
- **(B) Design-assumption mismatches** — desalinhamento entre o que a arquitetura assume e a realidade.
- **(C) Error swallowing & dilution** — o sinal de erro é suprimido ou atenuado no caminho.
- **(D) Chained hallucination & fabrication** — o LLM transforma o erro num relato "fluente e plausível" (a classe mais perigosa).
- **(E) Operational omission & forensic blind spots** — não há log/monitor onde a falha aconteceu.

**Achados reportados:** ~70% das falhas silenciosas foram pegas por **observação humana da view do usuário**, não por teste ou auditoria automática. Auditorias funcionam como "motor de regressão, não de predição" (~87% de bloqueio de regressão; ~0% de prevenção ex-ante). As falhas mais longas ocorrem "nas costuras entre componentes, onde nenhum teste roda".

## Relevância para o projeto

1. **Nomeia o ponto cego do relatório.** `02-relatorio-achados.md` §6 mede que ≥59% dos erros do trace não levantam exceção. As classes **C** (error swallowing) e **E** (forensic blind spot) são exatamente esse fenômeno, com vocabulário de causa. A classe **D** é a versão agentiva do risco de groundedness — o erro vira texto convincente na `final_answer`.
2. **Precedente metodológico direto.** É o único outro estudo que faz taxonomia de causa-raiz a partir de trace longitudinal de **um** sistema de produção real (aqui: 1.000 execuções, nov/2025–ago/2026). Método comparável (postmortem incidente a incidente), escala menor.
3. **"Costuras entre componentes"** aponta o próximo lugar a olhar na esteira: handoffs entre papéis/subagentes, onde nenhum detector determinístico atual roda.

---
Adição nova.
