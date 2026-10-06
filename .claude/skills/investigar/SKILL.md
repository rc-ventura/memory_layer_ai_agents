---
name: investigar
description: "Investigação de uma parada de uma rodada de mineração do trace, até o dossiê de decisão (kit de mineração)"
argument-hint: "<mineração> <pergunta do roteiro, ex.: silenciosas S2> [pasta da análise]"
disable-model-invocation: true
---

Investigue a parada indicada no pedido (`$ARGUMENTS`) com a skill `mineracao-investigacao`.

- Comece pelo relatório mais recente desta mineração em `pipeline/resultados/`, na pasta de análise indicada (ou na
  corrente).
- Siga os passos da skill na ordem: hipóteses antes de ler, amostra por regra, leitura com o `investigador`, segundo
  leitor às cegas com o `segundo-leitor`, regra contada com o `testar_regra.py`, dossiê e `varrer_pii.py`.

Na resposta, traga:
- a pergunta;
- as hipóteses;
- as contagens: leitura `[assistido]`, concordância, regra `[conferido]`;
- as opções e a sua recomendação, com a confiança;
- o caminho do dossiê completo, em que cada número tem o comando e cada categoria tem os casos crus que a sustentam.

Não altere o pipeline; a decisão é minha.
