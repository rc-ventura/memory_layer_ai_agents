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
  mascarados. Nunca texto de caso nem `exec_id`. **Revogada em 16/10** pela decisão do sigilo, abaixo (só o dado pessoal
  e o conteúdo do cliente não saem).

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
| `U_verificacao_try_nameerror` (o `try/except NameError` que o prompt instrui e o sandbox não captura) | sinal de harness nas bases 2 e 3; a assinatura na linha que falhou decide antes da posição do passo anterior (13/10) | livro-razão Ajuste 17; relatório da base 3 §7.9–7.10 |
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
  aprovação é do Rafael → `16`, `06` §10 peça 6. (Desde 16/10 a parte específica nova é script; a regra é a mesma →
  livro-razão, Ajuste 20.)
- **06/10, a leitura e o gate:** leitura em duas etapas (aberta → gate da lista → fechada em outros casos, ≥ 20) ·
  "os leitores discordam" não é "não há lição" · o gate do pesquisador · dividir a unidade é resultado normal →
  `06` §10, `16`.
- **06/10, monitorar:** determinístico (`analysis/registros/monitoramento.json`, um só para as pastas de todas as bases;
  `monitorar.py` no passo 0 de toda mineração). Em monitoramento: `U_nome_inventado`, `U_campo_inexistente`, a
  ferramenta concorrente do `final_answer` → `16` § O monitoramento.
- **06/10, o kit:** mora no próprio `.claude/`, versionado; cada mineração tem um nome só (`/mineracao-<assunto>`);
  `investigar` e `propor-notebook` (renomeada `propor-script` em 16/10, Ajuste 20) são skills de chamada manual; o Copilot lê o mesmo `.claude/`, sem cópia →
  [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md).
- **15/10, gráficos de volume e de taxa não separam destino:** nos gráficos de volume, taxa e custo, **erro é erro** — sem
  linha, marcador ou cor por destino (memória, sinal de harness, infra). O destino de cada erro depende da classificação,
  que muda a cada investigação; um gráfico de volume que dependesse dela teria de ser refeito a cada sinal novo. A
  separação por destino mora nos gráficos de destino (a fatia do orçamento de cada papel por destino; as unidades por
  destino e tipo de memória). A taxa de erro por mês e por papel é, portanto, a taxa de **todos** os erros estruturados →
  base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #36.
  **Aplicação à parte 1 do relatório (15/10, #40):** os gráficos por unidade (tokens por unidade, frequência × custo, papel × unidade,
  concentração por papel) trazem **todas** as unidades, sem cor, agrupamento nem texto de destino; só o gráfico de destinos (e o
  orçamento por papel, nas taxas) separam por destino.
  Sem exceção no gráfico de tokens por unidade; a cor desses gráficos é a **família** do erro, com legenda; o destino e o tipo da
  memória (factual · ambiente × experiencial · estratégia, Hu et al. 2025) ficam no gráfico de unidades por destino (#38), que
  entra na parte 1 (#40, gráfico 12).
- **15/10, a linha de base da economia da memória é congelada num registro versionado:** o "antes" do teste de compensação
  (teto de economia por papel e unidade, passos por papel, hashes da fonte, das contagens e da rodada; só números, nenhum
  identificador) fica num arquivo em [`registros/`](registros/README.md), no estilo do `monitoramento.json`, e não só na pasta
  de resultados (fora do git, e que pode ser refeita com outro código) → [racionais da base 3 §7](2026-10-trace-law-flow-third/docs/01-racionais.md#7--o-teto-de-economia-e-o-teste-de-compensação-da-memória),
  [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #39. O arquivo só é criado depois da tabela de tokens por unidade
  e papel (#36, gráfico 9).
- **15/10, a rodada da base 3 passa a guardar os tokens e os erros por unidade × papel, de todas as unidades:** hoje só as
  unidades de memória têm essa abertura por papel, e por isso o gráfico das taxas que divide o orçamento de cada papel por destino
  e o de papel × unidade do painel saem incompletos. Aprovada pelo Rafael (opção A): tabela nova na rodada
  (`consolidacao_unidade_papel_tokens.csv`), com os pendentes como "sem unidade"; os números que já existem não mudam
  (conferido por teste e por hash) e a rodada ganha um identificador novo. **Só entra no código quando a auditoria dos gráficos
  fechar** → [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #36 (gráfico 9) e #40 (gráfico 4); destrava #39.
- **15/10, cada gráfico do relatório tem um insight único:** se dois gráficos contam a mesma história a partir da mesma tabela,
  corta-se um e o que ele tinha de único passa para o outro. Aplicação: o gráfico de papéis das candidatas (um papel por barra)
  foi cortado da parte 1; o total por papel passa para a margem do mapa papel × unidade e as cores vivas por papel, para a
  concentração por candidata; e o gráfico de erros por unidade e mês (contagem) foi cortado da parte 1, virando o painel da esquerda do
  gráfico de taxa por unidade e mês da parte 2 → base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #40, gráficos 4, 7, 8 e 9.
- **16/10, as seis escolhas dos gráficos da base 3** (o porquê de cada uma e o que se perde: [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md),
  Plano de evolução, Etapa 1; #41):
  - **taxa de erro por mês: nenhuma faixa de incerteza nem cor** — o título se apoia em meses grandes e o painel de cima já mostra
    o tamanho de cada mês; uma faixa "de livro" seria estreita demais (os erros vêm em sequência na mesma execução) e poluiria;
    só uma frase no "Como ler" sobre o mês pequeno;
  - **taxa por unidade e mês em % dos passos do sistema, com 2 casas** (uma unidade só no relatório); **um mês com menos de 1.000
    passos no sistema** mostra os números mas fica cinza e fora da régua de cor (nenhum erro sai da conta);
  - **prioridade em dois painéis, um insight por painel:** para reduzir erros (todos os tokens em erro) e para memória (o teto: só
    as candidatas);
  - **genealogia: unidade e destino numa coluna só** (são 1 para 1; as arestas gravadas continuam com as cinco colunas); a cauda
    **não** é agrupada (a decisão de 24/09 continua; rever com a foto);
  - **"o que vem depois do erro" de todas as unidades,** por uma tabela só de contagem na rodada (`consolidacao_depois_unidade.csv`),
    com **a unidade do erro seguinte** quando o vínculo está confirmado (a matriz de transição: sequência, não causa); e o
    **perfil sob demanda de qualquer unidade** (`--perfil-investigacao`), marcado como "investigação — não é candidatura", para os
    roteiros de protocolo, crítico, resíduo e timeout;
  - **sem índice de Gini** na concentração de custo.
- **16/10, o arquivo final da memória na base 3 aponta o caso por hash** (esquema 0.2): `step_ref` + `fonte_id` + `rodada_id`
  no lugar de `idx` (a base 3 não tem `idx`). Assim o arquivo sai inteiro, sem a troca por `caso-N`. O `exec_id` vai junto
  (decisão seguinte). Os arquivos 0.1 da base 1 continuam
  válidos → livro-razão, [Ajuste 19](pipeline-entre-bases.md#ajuste-19--o-arquivo-final-da-memória-aponta-o-caso-por-hash-na-base-3-esquema-02); base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #44.
- **16/10, o sigilo protege só o dado pessoal e o conteúdo do cliente** (decisão do Rafael, opção 1 entre "liberar o
  técnico" e "liberar tudo"): saem o `exec_id`, o `step_ref`, a mensagem de erro, o código do agente, nomes de variável,
  chamadas de ferramenta e o texto do prompt; não saem nome de pessoa, CPF, CNPJ, número de processo, e-mail, o
  documento, a pergunta do usuário, a resposta entregue a ele e os valores do caso. O `varrer_pii.py` continua
  obrigatório antes de algo sair (sem procurar mais o identificador); a troca por `caso-N` fica opcional. Revoga o
  "nunca texto de caso nem `exec_id`" das regras de trabalho. O arquivo final da memória leva o `exec_id` ao lado do
  `step_ref` → [sigilo](../.claude/skills/mineracao-base/referencias/sigilo.md).
- **16/10, o inventário do sandbox ganha script específico por decisão do Rafael** (a porta da regra de criação que
  dispensa os dois leitores): a lição sai da mensagem de erro, e a confiança é a cobertura da regra, **≥ 95%**, escrita
  antes de rodar → base 3, [`propostas/U_sandbox/racional.md`](2026-10-trace-law-flow-third/propostas/U_sandbox/racional.md),
  [`07`](2026-10-trace-law-flow-third/docs/07-racionais-mineracao-candidatas.md).
- **16/10, a parte específica da mineração é um script, não um notebook:** em `pipeline/especificas/`, com teste na suíte,
  lendo a rodada conferida pelo código do pipeline e com manifesto próprio; fora do hash do código da rodada. A skill
  passa a `propor-script` e o agente a `validador-de-script`. Os notebooks da base 1 continuam como legado → livro-razão,
  [Ajuste 20](pipeline-entre-bases.md#ajuste-20--a-parte-específica-da-mineração-passa-a-ser-um-script-não-um-notebook); `16`, "Como o script roda".

---
