---
description: "Propõe um notebook específico para uma lição que cumpriu a regra de criação do procedimento de mineração de candidatas (kit de mineração)"
argument-hint: "<unidade, ex.: U_...> [pasta da análise]"
---

Proponha um notebook específico para a lição `{{argumentos}}`, seguindo o procedimento da análise
(`docs/*procedimento-mineracao-candidatas*.md`, § "O ciclo de vida da parte específica").

1. **Confira a regra de criação antes de qualquer coisa.**
   - (a) As regras do `resultados/mineracao/<u>/regras.json` foram aplicadas **sem mudança** numa segunda base, com
     concordância ≥ 90%, "pega a mais" ≤ 10% e kappa ≥ 0,6 nas duas. Ou:
   - (b) Há uma decisão minha registrada no `plano-atual.md`.

   Se nenhuma vale, **pare** e diga qual critério falta, com os números.
2. **Escreva só em `propostas/<u>/`:**
   - `racional.md` primeiro, com a lição, as regras em prosa, de onde cada uma veio, o que o notebook mede e não mede,
     o status "proposta" e a data e o hash do arquivo;
   - depois o notebook `mineracao_<u>.ipynb`, só com as regras do racional, sem saídas.

   Não mexa em `docs/`, `pipeline/` nem na tabela do funil.
3. **Peça a validação** ao agente `validador-de-notebook`, disparado da raiz do repositório.

Na resposta, traga o critério que valeu, os arquivos da proposta e o veredito do laudo. A aprovação é minha.
