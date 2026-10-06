---
description: "Minera uma candidata a memória (uma lição da triagem) de uma base do trace: parte genérica, auditor em paralelo, funil para a parte específica e o arquivo final no esquema da memória (kit de mineração)"
argument-hint: "<unidade, ex.: U_...> [pasta da análise]"
---

Minere a candidata `{{argumentos}}` com a skill `mineracao-candidata` (a pasta da análise vem no argumento, ou é a
corrente).

1. **Preparação** (`mineracao-base`) e conferência de que a lição está no `candidatos_memoria.csv`. Se não estiver,
   pare.
2. **Parte genérica:**
   - dispare o `auditor-independente` em paralelo (`audit_recompute6 --json --unidade`), da raiz do repositório;
   - rode o `mineracao_generica.ipynb` com `UNIDADE=<u>`;
   - faça o encontro;
   - escreva o relatório da parte genérica, com evidência por achado.
3. **Funil:** pela tabela do procedimento.
   - Com notebook específico, rode-o e converta o registro.
   - Com investigação, use a `mineracao-investigacao` com o roteiro `candidata`, com dois leitores às cegas e regras
     contadas.
4. **Arquivo final:** `memoria_<u>_<BASE_ID>.json`, aprovado pelo `validar_memoria.py`. A versão que sai passa pelo
   `varrer_pii.py`.

Na resposta, traga:
- a lição em uma frase;
- o escopo;
- o que é `checado` e o que é `hipotese`;
- o destino proposto;
- as pendências;
- os caminhos dos arquivos.

A decisão de destino é minha.
