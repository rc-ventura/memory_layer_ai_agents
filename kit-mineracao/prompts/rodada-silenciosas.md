---
description: "Minera as falhas silenciosas de uma base do trace, do zero, com a auditoria independente em paralelo (kit de mineração)"
argument-hint: "<pasta da análise, ex.: analysis/<pasta-datada>>"
---

Minere as falhas silenciosas da base na pasta de análise `{{argumentos}}` (se vier vazia, use a pasta corrente).

1. Skill `mineracao-base`: o Passo 0 inteiro. Se ele parar, pare e me diga por quê.
2. Skill `mineracao-silenciosas`:
   - dispare o `auditor-independente` em paralelo;
   - garanta as tabelas;
   - leia-as passo a passo do procedimento;
   - faça o encontro auditoria × tabelas.
3. Relatório no esqueleto da `mineracao-base`, com a evidência de cada achado (comando, tabela, casos crus montados pelo
   `montar_evidencia.py`). Versão que sai pelo `versao_para_sair.py`, com o `varrer_pii.py` limpo.

Na resposta, traga só:
- os achados principais desta base, em contagens;
- o resultado do encontro auditoria × tabelas e das conferências internas;
- as paradas, com a pergunta do roteiro que cada uma abre e a pasta de evidência de cada uma;
- o caminho do relatório completo.

Não investigue as paradas nesta rodada; eu escolho qual vai para a `mineracao-investigacao`.
