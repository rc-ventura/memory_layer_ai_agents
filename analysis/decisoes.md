# Decisões em vigor — o que já foi decidido, para não rediscutir

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](glossario.md).

**Para que serve:** um índice de uma página das decisões que valem para todas as análises — regras de trabalho,
organização do método, destinos decididos para cada achado e as decisões de método por data. O **porquê** de cada uma
está no documento linkado; o **histórico** de cada ajuste, no livro-razão ([`pipeline-entre-bases.md`](pipeline-entre-bases.md)).
O que fazer agora **não** fica aqui: está no roadmap de cada análise (o schema deles em [`plano-atual.md`](plano-atual.md)).

**As referências "4.x"** que aparecem nas decisões são do plano antigo; o de-para para o roadmap de cada item está no fim de [`plano-atual.md`](plano-atual.md).

**Regra:** decisão nova entra no fim da seção da data, com uma linha e o link para o porquê; decisão revogada ganha
"revogada em <data> por <link>", nunca é apagada. Até 06/10/2026 estas decisões estavam no §1 do plano atual
(`git show e0335aa:analysis/plano-atual.md`).

---

**Regras de trabalho:**
- **Uma solução por vez:** contexto, solução, argumento com evidência e tipo da mudança; espera a aprovação; executa,
  verifica na base 1, commita e diz o que o Rafael roda na máquina 2.
- **Regra nova só olhando as duas bases** (livro-razão, Ajuste 7).
- **Leitura por LLM é `[assistido]`** e vale como hipótese; o determinístico é `[conferido]`. Nenhum LLM no caminho da
  classificação.
- **Da máquina 2 só saem** contagens, nomes de papel, ferramenta e modelo, hashes, sim/não, tamanhos, tokens e motivos
  mascarados. Nunca texto de caso nem `exec_id`.

**Organização:**
- Cada análise com método próprio tem o seu conjunto: notebook + racional + relatório + procedimento (protocolo
  `10`–`12`; falhas silenciosas `13`–`15`; candidatas `06`, `07`, `16`). Onde cada mineração está: a tabela de referência em [`roadmap-transversal.md`](roadmap-transversal.md).
- Três notebooks: visível (a esteira), invisível (falhas silenciosas) e consolidação (a triagem final) → `09`, livro-razão
  Ajuste 12.
- As funções de medida ficam no `base_pipeline.py` (ou `analysis/base_utils.py`); o notebook e o `drill_down.py` chamam
  as mesmas.

**Destinos decididos:**

| Achado | Destino | Porquê / onde |
|---|---|---|
| Resposta final fora do envelope (M1), ferramenta que concorre com o `final_answer` (M2) | sinal de harness; a concorrente: **monitorar, não dar como corrigida** (02/10) | `10` §4, `11` §1.3; `analysis/registros/monitoramento.json` |
| "O risco à resposta está na plataforma" ([4]) | hipótese, não achado | `14` §5; 4.1c |
| Resposta vazia aceita (M5), narração executada como código (M6) | achado de harness / plataforma | `10` §4; 4.9 |
| Surtos da base 1 (modo) e da base 2 (modelo) | não-memória; achado para a plataforma | `10`, `11` |
| `U_tipo_retorno`, `U_campo_inexistente` | continuam candidatas: não nascem de falha silenciosa | `13` §8, `14` §4 |
| `U_campo_inexistente` | sinal de harness nas duas bases | livro-razão Ajustes 5 e 13 |
| `json_invalido` do `busca_obf` | dono: o agente (o gesto da `U_repr_colado`); memória **e** sinal de harness; monitorar na base 3 | `13`, `14`; livro-razão Ajuste 12 |
| Família do protocolo, base 1 | fechada | `11` |

**Decisões de método, por data** (o porquê no link):
- **02/10:** ocorrência no balde invisível = a mesma régua do visível (livro-razão Ajuste 12) · erro crítico: investigar
  a chamada que morreu antes de decidir o destino (4.6) · alarme de cobertura mostra a concentração (roadmap #34) ·
  sucesso falso: examinar os 24 candidatos da base 2, em dois eixos (4.1c).
- **05/10, o kit e a investigação:** minerar não é comparar com relatório (a verificação é a auditoria independente em
  paralelo) · nenhuma afirmação sem evidência · sigilo por script (`caso-N`) · a investigação por LLM vem depois do
  determinístico, e o modelo propõe e o script conta · as skills são genéricas → [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md),
  skill `mineracao-base`. Os Ajustes 14–16 do protocolo → livro-razão.
- **05/10, notebook específico:** só com frequência **e** confiança, sem sorteio, reconfirmado a cada partição; a
  aprovação é do Rafael → `16`, `06` §10 peça 6.
- **06/10, a leitura e o gate:** leitura em duas etapas (aberta → gate da lista → fechada em outros casos, ≥ 20) ·
  "os leitores discordam" não é "não há lição" · o gate do pesquisador · dividir a unidade é resultado normal →
  `06` §10, `16`.
- **06/10, monitorar:** determinístico (`analysis/registros/monitoramento.json`, um só para as pastas de todas as bases;
  `monitorar.py` no passo 0 de toda mineração). Em monitoramento: `U_nome_inventado`, `U_campo_inexistente`, a
  ferramenta concorrente do `final_answer` → `16` § O monitoramento.
- **06/10, o kit:** mora no próprio `.claude/`, versionado; cada mineração tem um nome só (`/mineracao-<assunto>`);
  `investigar` e `propor-notebook` são skills de chamada manual; o Copilot lê o mesmo `.claude/`, sem cópia →
  [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md).

---
