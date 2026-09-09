> **Fichamento breve — tier abaixo dos quatro 🔎 desta pasta.** Bibliografia (ID, título, data, autoria) conferida por busca web em 2026-09-09, **não contra o PDF primário**. Resumo derivado do abstract, da página HTML do arXiv e do post do Scale Labs — **texto completo não lido** (nem por agente). Estatísticas abaixo são "conforme reportado na busca", não citação verificada. `Lido por Rafael: não`.

# Insights Generator — Systematic Corpus-Level Trace Diagnostics for LLM Agents

- **Autores:** Akshay Manglik, Apaar Shanker, Kaustubh Deshpande, Jason Qin, Yash Maurya, Veronica Chatrath, Vijay S. Kalmath, Levi Lentz, Yuan (Emily) Xue — Scale AI
- **Ano:** 2026
- **Venue:** arXiv:2605.21347 (v3); há post correspondente no blog do Scale Labs
- **Link:** <https://arxiv.org/abs/2605.21347>
- **Tags:** trace-mining, corpus-level, failure-mode-analysis, multi-agent-diagnosis, hypothesis-testing

## O que é

O paper metodologicamente mais próximo do que esta análise fez: parte de um **corpus** de traces de execução (não de um caso isolado) e produz um **relatório de insights com evidência**. Problema declarado: hoje o diagnóstico é manual — o praticante inspeciona um punhado de traces, forma hipóteses ad-hoc e itera — o que (a) perde padrões que só aparecem na população e (b) não escala para corpora de produção onde cada trace tem dezenas de milhares de tokens.

Arquitetura: sistema **multi-agente** com dois papéis —
- **Scout** — lê amostras pequenas de traces e propõe hipóteses candidatas de modo de falha;
- **Investigator** — pega cada hipótese e a **valida contra o corpus inteiro, com evidência estatística**.

Resultado reportado: especialistas humanos usando os relatórios do IG melhoram o desempenho do scaffold em **+30,4 pontos percentuais** sobre o baseline; agentes de código que consomem os insights do IG mostram ganho consistente.

## Relevância para o projeto

1. **É o blueprint para escalar esta análise.** A taxonomia do trace da esteira jurídica foi construída à mão a partir de ~1.000 execuções. O par Scout/Investigator é a versão automatizável do que foi feito manualmente: propor um modo de falha a partir de uma amostra, depois testá-lo determinística/estatisticamente no corpus todo. O `04-roadmap.md` (itens 1–6) é exatamente uma fila de hipóteses aguardando esse teste.
2. **Separar hipótese de validação** é a mesma disciplina do "teste de robustez" já descrita em `01-racionais.md`. O IG a formaliza como arquitetura.
3. **Ressalva:** o IG usa LLM tanto no Scout quanto no Investigator; esta análise manteve o v1 determinístico de propósito. Adotar a *forma* (propor → validar no corpus), não necessariamente o *mecanismo* (dois agentes LLM).

## Relacionados (não buscados a fundo)

- **Diagnosing with Insights / AGENTSCOPE** — arXiv:2609.02371 (Tsinghua + Microsoft Research + UIUC, set/2026). Abordagem neuro-simbólica: abstrai a trajetória em representação estruturada + "invariantes neurais" + raciocínio guiado por LLM para localizar passo e tipo da falha; reporta superar o SOTA em Who&When.
- **AgentRx: Diagnosing AI Agent Failures from Execution Trajectories** — arXiv:2602.02475 (Microsoft Research).

---
Adição nova — ainda não dobrada em nenhum relatório de `literature-review/`.
