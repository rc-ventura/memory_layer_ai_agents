---
name: rodada-candidata
description: "Minera uma candidata a memória (uma lição da triagem) de uma base do trace: parte genérica, auditor em paralelo, funil para a parte específica e o arquivo final no esquema da memória (kit de mineração)"
argument-hint: "<unidade, ex.: U_...> [pasta da análise]"
disable-model-invocation: true
---

Minere a candidata indicada no pedido (`$ARGUMENTS`) com a skill `mineracao-candidata` (a pasta da análise vem no argumento, ou é a
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
   - Com investigação, use a `mineracao-investigacao` com o roteiro `candidata`: leitura aberta pelos dois leitores,
     **pare para eu aprovar a lista**, depois a leitura fechada às cegas e as regras contadas.
4. **Painel e gate:** rode o `valor_da_licao.py` com a lição. Se a situação tem gate, **pare** e me traga a lição
   principal com a cobertura, os leitores lado a lado, o resto e as opções.
5. **Arquivo final:** `memoria_<u>_<BASE_ID>.json`, aprovado pelo `validar_memoria.py`. A versão que sai passa pelo
   `varrer_pii.py`.

Na resposta, traga:
- a lição em uma frase;
- o escopo;
- o que é `checado` e o que é `hipotese`;
- o destino proposto;
- as pendências;
- os caminhos dos arquivos.

A decisão de destino é minha.
