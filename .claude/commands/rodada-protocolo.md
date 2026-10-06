---
description: "Minera o protocolo do harness (resposta sem bloco de código) de uma base do trace, do zero, com a auditoria independente em paralelo (kit de mineração)"
argument-hint: "<pasta da análise, ex.: analysis/<pasta-datada>>"
---

Minere o protocolo do harness da base na pasta de análise `$ARGUMENTS` (se vier vazia, use a pasta corrente).

1. Skill `mineracao-base`: o Passo 0 inteiro. Se ele parar, pare e me diga por quê.
2. Skill `mineracao-protocolo`:
   - dispare o `auditor-independente` em paralelo (`audit_recompute10.py --json`);
   - gere as tabelas com `drill_down.py protocolo`;
   - minere passo a passo do procedimento, com a evidência de cada achado;
   - faça o encontro auditoria × tabelas.
3. Relatório no esqueleto da `mineracao-base`, com a evidência de cada achado. Versão que sai pelo
   `versao_para_sair.py`, com o `varrer_pii.py` limpo.

Na resposta, traga só:
- os achados principais desta base (incidente ou fundo, a camada, o M1), em contagens;
- o resultado do encontro auditoria × tabelas e das conferências internas;
- as paradas (cobertura, fronteira de chamada, P1, P2), com a pasta de evidência de cada uma;
- o caminho do relatório completo.

Não leia casos nesta rodada; eu escolho o que vai para a `mineracao-investigacao`.
