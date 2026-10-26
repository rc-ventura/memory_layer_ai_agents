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
- **19/10, o script do inventário do sandbox está aprovado** (cobertura 99,86% na base 3, encontro 61/61, validador aprovado):
  sai de `propostas/U_sandbox/` para `pipeline/especificas/mineracao_U_sandbox.py`. A divisão da lição em partes e os destinos
  seguem em aberto → [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md).
- **19/10, a lição do sandbox é dividida por papel e por causa** (decisão do Rafael): a evidência é contada —
  `globals` 2.347 de 2.352 no `ContestacaoCivel`, `get_document_text` 167 de 167 no `OBFCivel`, `pd` 231 de 233 no
  `JoogleAnalytics`, contra `json` em 10 papéis e 10 meses. O racional ganha as partes e o script monta uma memória por parte
  (nova validação). O destino da parte do `globals` (harness) segue como hipótese → [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md).
- **19/10, a validação de uma memória tem quatro degraus** (decisão do Rafael): candidata (a mineração) → conferida
  (cinco checagens determinísticas: ambiente, conflito com o prompt, repete o prompt, recorrência, uma causa só) →
  revisada (leitura de casos com dois leitores e o gate) → validada (o experimento). Num documento à parte do
  procedimento → [`17`](2026-09-trace-law-flow/docs/17-validacao-memorias.md); livro-razão, Ajuste 24. As 14 do sandbox estão
  no degrau 1 (`b3 #50`).
- **19/10, o piloto do sandbox está fechado** (`b3 #12`): na rodada `aedb9b5db70d6c92` da base 3, 14 memórias (C e E
  globais, B e D por papel) com destino memória e derived-and-checked, registradas no catálogo `registros/memorias.json`
  (transcritas das fotos e conferidas contra o inventário: 43 nomes, 1.396 erros). 6 delas têm 1 a 3 erros; a régua
  de memória rara fica para depois, se o Rafael quiser → [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md) §2d.
- **19/10, a parte E do sandbox vira memória global** (decisão do Rafael, depois da investigação, dossiê §2c): o que
  sobra depois do Ajuste 23 (depuração com `repr`/`.__name__`, outras funções proibidas, a verificação com valor padrão
  que a regra (b) deixou no sandbox) é hábito do agente, sem instrução no prompt. A guidance ganha o jeito permitido
  ("print(type(x))", "str(x)[:n]", "json.loads"); emenda 6 do racional.
- **19/10, o script do sandbox dividido em partes está aprovado** (decisão do Rafael): a emenda 4 (C, B, D, E; uma
  memória por parte; o catálogo), validada pelo `validador-de-script` na revalidação 5 (110 de 110 medidas iguais) →
  [laudo](2026-10-trace-law-flow-third/propostas/U_sandbox/validacao.md). A primeira rodada na base 3 tem de ser
  posterior ao commit `ef36e2c`.
- **19/10, o Ajuste 23 (decisão do Rafael):** o `eval` usado numa função auxiliar que verifica se a variável existe e,
  se não existe, a cria chamando uma ferramenta (`if not _exists('x'): x = ferramenta(...)`) sai de `U_sandbox` e entra em
  `U_verificacao_existencia` (harness), pela mesma regra do Ajuste 21. O `eval(texto)` para converter texto em objeto
  (os 3 dos outros papéis e 6 do ContestacaoCivel) fica no sandbox. Evidência: base 3, 40 de 46 `eval` do ContestacaoCivel
  com a função auxiliar definida no código do passo; nenhum prompt menciona `eval` (base 2) →
  [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md) §2c; livro-razão, Ajuste 23.
- **19/10, o catálogo das memórias fechadas** (decisão do Rafael): `analysis/registros/memorias.json`, uma entrada por
  memória com destino memória e status derived-and-checked (só conteúdo técnico e o hash do arquivo final, sem os
  casos); montado no passo 9 do `minerar.py` e registrado com `catalogar_memoria.py --registrar`. Uma lição pode ter
  várias memórias (esquema 0.3) → livro-razão, Ajuste 22.
- **19/10, os destinos das partes do sandbox depois do Ajuste 21 (decisão do Rafael):** C (módulo usado sem import,
  656) → **memória global**; B (ferramenta importada como módulo, 212, `OBFCivel`) → **memória do papel `OBFCivel`**;
  D (import fora da lista autorizada, 40) → **memória por papel** (cada papel com a sua lista). A parte E (funções e
  atributos proibidos, 523, concentrada no `ContestacaoCivel`) **fica em investigação antes de virar memória**: se vem
  do prompt desse papel, como a verificação de existência, é sinal de harness → testes `contar_proibidas_linha.py`
  (base 3) e `contar_proibidas_prompt_base2.py` (base 2); [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md), §2c.
- **19/10, o Ajuste 21 (decisões do Rafael):** (1) a introspecção proibida (`globals`/`locals`/`vars`) usada para
  verificar a existência de uma variável **e que guarda a criação dessa variável por uma chamada** ("se `x` não existe,
  `x = ferramenta(...)`" — o comportamento que a instrução do prompt pede) sai de `U_sandbox` e entra na unidade do
  `try/except`; a leitura com valor padrão (`globals().get('x', padrão)`, espontânea) fica no sandbox — **regra (b),
  condicionada a um teste na base 3**; se o teste não separar, vale a regra só pela linha (a), com as exceções
  registradas; (2) a unidade passa a `U_verificacao_existencia`; (3) o ajuste vale nas três bases; (4) o monitoramento
  (`b3 #28`) é registrado junto, com os dois sintomas; (5) o aviso à plataforma continua adiado (`transversal #7`) →
  [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md); base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #46.
- **20/10, a unidade do sandbox fecha no degrau 3** (decisão do Rafael): as memórias que passam no degrau 2 e vão para
  injeção passam também pela leitura de casos com dois leitores e o gate (degrau 3, skill `mineracao-investigacao`);
  só o degrau 4 (o experimento) fica para as POCs → [`17`](2026-09-trace-law-flow/docs/17-validacao-memorias.md); base 3,
  [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #50.
- **20/10, o degrau 2 lê os nomes de um campo estruturado** (decisão do Rafael): `validation.nomes` no arquivo final
  (esquema 0.4; `importar`, `usar`, `nao_importar`, `nao_usar`), gravado pelo script específico da mesma tabela que gera
  a guidance, e copiado no catálogo; a lista autorizada de cada papel vem do prompt; a instrução do prompt que induz um
  nome (a verificação de existência) fica no item do `monitoramento.json`; as 14 do sandbox ganham o campo transcrito da
  `description`, marcado, até a próxima mineração → livro-razão, [Ajuste 25](pipeline-entre-bases.md#ajuste-25--o-degrau-2-por-script-e-o-esquema-04-20102026).
- **20/10, o `get_document_text` do OBFCivel é sinal de harness, não memória** (decisão do Rafael): nas 63 execuções do
  papel na base 2 (abr–ago/26, as 4 versões do prompt) e nas 11 da base 1, o prompt cita a função e não a declara como
  ferramenta — o erro vem do prompt, e a memória atual ("chame-as direto") mandaria chamar algo que o prompt não declara
  (se a função existe no executor não foi testado: na base 1 o agente nunca a chama direto; o teste da chamada direta e
  da declaração em outros papéis vai à base 2; hipótese do Rafael: a ferramenta mudou de nome e o prompt não). O import
  de `get_document_text` sai da unidade do sandbox por regra (Ajuste 26, a escrever); o resto da parte B segue memória do
  OBFCivel → [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md) §2h; base 3,
  [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #49 (fechado) e #50.
- **20/10, a verificação com valor padrão do ContestacaoCivel é sinal de harness** (decisão do Rafael, por coerência com o
  Ajuste 21): `if 'x' not in globals(): x = '…'` (≈ 124 `globals` + 10 `locals` na base 3, jul–ago/26) é a instrução
  "verifique se a variável existe" cumprida sem caminho dado — o prompt deixa o como em aberto, o agente tenta e o sandbox
  barra. Sai do sandbox por regra (extensão da regra (b) do Ajuste 21, só no papel com a instrução; as ≈ 9 verificações
  espontâneas dos outros papéis ficam), na mesma rodada do Ajuste 26; a memória E deixa `globals`/`locals`/`vars`/`eval`.
  A causa por erro é inferida (a base 3 não guarda o prompt), como no Ajuste 21. A ideia de uma memória "como verificar no
  sandbox" fica como candidata própria → [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md) §2h;
  base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #50 e #51.
  **Complemento (20/10, depois da medição — `contar_introspeccao_linha.py` parte E, fotos `IMG_5976`–`IMG_5978`):** a forma
  do código não separa o ContestacaoCivel dos outros papéis (fora dele aparecem as mesmas formas), e ele tem as quatro
  (cria com valor fixo 52, leitura com valor padrão 14, sem nome entre aspas 33, verifica e não cria 36). Decisão do Rafael:
  **a regra é pelo papel** — toda verificação com `globals`/`locals`/`vars` que a regra (b) deixa no sandbox, **no
  ContestacaoCivel**, vai para `U_verificacao_existencia` (135 na base 3); os 9 dos outros papéis ficam no sandbox, porque
  o prompt desses papéis não tem a instrução (base 2, todos os papéis; base 1) — inferência, sem o prompt na base 3; por
  que esses agentes verificam sem instrução não se sabe ("hábito" seria interpretação). Aceito sem investigar agora porque
  são 9 erros e não viram memória injetada; a investigação de alguns casos fica no `b3 #54`. A regra é o Ajuste 27
  ([livro-razão](pipeline-entre-bases.md)), emenda 8 do racional do sandbox.
- **20/10, as 10 memórias de "import fora da lista" são monitoradas, não injetadas** (decisão do Rafael): a lista de imports
  autorizados já está no prompt de todos os papéis (bases 1 e 2) e as 10 falham em "repete o prompt" no degrau 2; são 40
  erros na base 3 (0,13%), de 1 a 14 por papel. Ficam no inventário do sandbox (os erros não mudam de unidade) e entram no
  monitoramento num **tipo novo, "memória de reforço (repete o prompt)"**, distinto de *sinal de harness* e de *memória rara*
  — as 5 que também falham na régua entram neste tipo, não no de memória rara. Injetar o que o prompt já diz testa outra
  pergunta (o reforço funciona?), documentada como experimento próprio (EX-8 do
  [blueprint](../pocs/blueprint-m1-pocs-minimos.md), com a literatura) → [glossário](glossario.md) (tipos de
  monitoramento); base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #50.
- **20/10, o script do sandbox com as emendas 7, 8 e 9 está aprovado** (decisão do Rafael): revalidação 7 do
  `validador-de-script` aprovada — 189 de 189 medidas iguais no ensaio da base 1, encontro com a auditoria 31/31, 7
  memórias no esquema 0.4; cada emenda no mesmo commit do código que a aplica (`c832da3`, `cc27360`). Condição: a
  primeira rodada na base 3 com um HEAD que contenha essas emendas. As três observações do laudo para a base 3: conferir o
  esperado da emenda 8 (135); a ordem das raízes no `nomes` da B; o `destino_decidido_em` pelo título da entrada (feito)
  → [laudo](2026-10-trace-law-flow-third/propostas/U_sandbox/validacao.md), "Revalidação 7".
- **21/10, o gráfico do custo da execução (com × sem erro) mostra valores reais, não razões** (decisão do Rafael, ao
  tentar ler o gráfico para a apresentação): a versão de 15/10 normalizava as barras (sem erro = 1×), o que escondia os
  números de que o "4,3×" e o "1,3×" saem e usava duas escalas diferentes; a leitura natural "1,3× = 30% a mais de passos"
  estava errada — são medianas inteiras, 4 passos contra 3 (um passo a mais). Agora cada painel tem as duas barras em
  unidades reais (tokens, 43.774 contra 10.074; passos inteiros, 4 contra 3), a razão escrita ao lado da barra, a média e o
  n de cada grupo; a estatística da barra continua a mediana (a decisão de 15/10 se mantém) → `figuras_taxas.custo_execucao`,
  teste `test_custo_execucao_em_valores_reais`; falta rodar na máquina da base 3 (`executar.py taxas`).
- **21/10, entra o gráfico de erros e taxa por papel e mês (`taxas_papel_mes.png`; roadmap b3 #37, o papel fixo)** (Rafael, ao escrever o slide da escala: o gráfico por papel não mostra quanto cada papel erra por mês, e o mapa papel × unidade agrupa por unidade). Duas faixas lado a lado, contagem de erros e taxa do próprio papel no mês (erros ÷ passos do papel naquele mês), com a fatia dos erros e a fatia dos passos no rótulo de cada papel — "concentrado" só vale para o papel com mais erros do que passos. Régua de cor linear, não log. Entram também os papéis que erram mais de 2× a taxa global com poucos erros (o AnaliseProcessual não some em "demais"). **Junto, `taxas_papel_entrada.png`:** em que mês cada papel aparece (execuções por papel e mês) e a participação dele nos passos do mês (o mix), com a moldura no primeiro mês — a data de entrada que a taxa mensal não dava. Só código e teste; falta rodar na máquina 2.
- **21/10, o "`json` sem import" do RoteadorCivel é memória, não harness** (decisão do Rafael): na base 3, o import de
  `json` funciona no papel (218 de 241 erros corrigidos no passo seguinte importando; 129 imports rodaram; 0 "Import of
  json is not allowed"), inclusive com o prompt sem `json` na lista; o erro começa em mai/26, quando o `json` sai da lista,
  mas com volume pequeno antes e queda em ago/26 ainda sem ele — a lista não explica o erro. A C global fica como está. A
  divergência entre a lista do prompt e a do interpretador fica como fato a avisar à plataforma → dossiê do sandbox §2h,
  16–17.
- **21/10, o degrau 2 confere o ambiente pelo que o interpretador aceita, não pela lista do prompt** (confirmado na base 2,
  foto `IMG_6014`: 520 de 520 imports de `json` rodam em 808 execuções cujo prompt não o lista; com a base 1, 531 de 531):
  na mesma execução, o prompt não lista o `json` e o `import json` roda (base 1: 11 de 11 passos, em 3 papéis);
  o prompt anuncia um ambiente que não é o real, e o agente segue o real. A checagem de ambiente do `conferir_memorias.py`
  passa a ler a lista do interpretador (mensagem "Authorized imports are: [...]") onde ela existe; a do prompt fica para a
  checagem de conflito. No smolagents, o `CodeAgent` aceita um interpretador pronto (`executor=`), e só o criado por ele
  recebe a lista do agente (`agents.py`, l. 1515 e 1585, v1.26.0; reproduzido com um modelo falso,
  `testar_sandbox_executor_proprio.py`) — o mecanismo da plataforma é hipótese → dossiê do sandbox §2h, 18–21; feito no
  Ajuste 28 (as decisões 1–3 abaixo); aviso à plataforma, [transversal](roadmap-transversal.md) #7.
- **21/10, as 8 decisões do fechamento do sandbox** (decisões do Rafael, uma por vez; plano do fechamento): (1) o que o
  agente pode importar vem da **mensagem de erro do interpretador e dos imports que rodaram sem erro**; sem nenhum dos dois,
  do prompt, com aviso; (2) com mais de uma lista no papel, o módulo tem de estar **em todas** (a reprovação mostra a
  versão e os meses); (3) as funções do Python que uma memória manda usar se conferem por uma **lista testada no
  interpretador**, na mesma mudança (fecha o `b3 #55`); (4) a checagem "uma causa só" sem a classificação de uso é
  **decidida pelo pesquisador, memória por memória, com motivo** ("decidido pelo pesquisador", nunca "passa"; a
  classificação automática vira item do kit); (5) a E fica **liberada da regra da repetição**: o prompt cita `print`, mas
  não avisa sobre `repr`/`dir`/`exec` — alarme falso (registrada em `registros/decisoes_degrau2.json`); (6) a
  **C.CalculoTrabalhista é memória rara** (2 erros, 1 mês): guardada, monitorada, não injetada; (7) a **parte F fica para
  depois**: o sandbox não fecha sem ela, e ela volta quando a maior parte das memórias estiver no degrau 3; (8) o degrau 3
  lê casos **na base 1** para as memórias que têm casos nela e **na base 2** para as que não têm ou têm pouco → Ajuste 28
  (1–5); dossiê do sandbox §2h, 22.
- **22/10, as 3 questões que o degrau 2 novo abriu no sandbox** (decisões do Rafael, uma por vez): (1) a C global no
  managerAgent — na base 1 o interpretador do papel mostra uma lista sem `json` e nenhum `import json` rodou — **espera a
  base 3** (o ambiente pela tabela da mineração): sem lista do papel lá, volta para decisão; lista sem `json`, a regra da
  mineração (global = módulos em todas as listas) já resolve; lista com `json`, vale a base 3; (2) a regra de citação do
  degrau 2 **exige a forma do Python** (`nome(` sem espaço, `from nome import`): a prosa do prompt do OBFCivel contava
  como citação de `tools` (Ajuste 28; só o conflito da B.OBFCivel muda); (3) a **B.OBFCivel é memória de reforço**, como
  as D: o prompt do OBFCivel já diz que as ferramentas são funções para chamar direto ("these tools are basically Python
  functions which you can call with code", 4 de 4 versões na base 1) e não libera `tools`/`python_interpreter`/
  `smolagents` — guardada, monitorada, não injetada. As memórias injetadas (e o degrau 3) ficam três: **C, E e
  C.JoogleAnalytics** → dossiê do sandbox §2h, 22.
- **22/10, a memória não injetada fica marcada e vigiada no catálogo** (aprovado pelo Rafael; o desenho de 20/10 no `16`,
  "Dois níveis"): rara → alarme quando passa na régua; reforço → alarme quando triplica; a marcação passa de uma mineração
  para a outra. Aplicado nas 13 não injetadas do sandbox — reforço: as 10 D e a B.OBFCivel; rara: a B.RespostaBacen e a
  C.CalculoTrabalhista → Ajuste 29; dossiê do sandbox §2h, 25.
- **22/10, o degrau 3 do sandbox lê casos de todas as bases, com prioridade para a base 3** (revisão da decisão 8 de
  21/10, decisão do Rafael): a base 1 tem 6, 5 e 0 casos da C, da E e da C.JoogleAnalytics, e a base 2 parece pequena; a
  base 3 tem 423, 317 e 231. Na base 3, até 30 casos por memória, cada um com o passo do erro e os vizinhos (n-1, n+1,
  n+2), sem o prompt, lidos na máquina pela skill de investigação; nas bases 1 e 2, todos os casos que houver, com o trace
  inteiro (pegam o "importou antes e o nome sumiu" que a janela da base 3 pode não mostrar). Para ler a base 3, a pasta
  dela ganha um `drill_down.py` (tabela, caso, evidencia: o contrato do kit) → dossiê do sandbox §2h, 26.
- **26/10, a cobertura das regras vira duas barras** (decisão do Rafael, ao ver o painel da base 3 na máquina 2, foto
  IMG_6063): a figura de um motivo por barra confundia (nove barras, a maior com 87% dos erros, e os pendentes espalhados
  em quatro). Agora: cobertos (a regra tem a evidência para decidir; na base 3, 29.392 de 30.141, 97,5%) e pendentes
  (falta dado na extração; 749), com os maiores motivos dos pendentes em texto embaixo da barra; a lista inteira continua
  na tabela do painel. Lido da rodada, sem rodada nova → `execucao/painel.py` (`figura_cobertura`).
- **26/10, a memória C do sandbox exclui o managerAgent** (decisão do Rafael, depois da ida à máquina de 26/10): na base
  1, a lista do interpretador do managerAgent é a padrão do smolagents, sem `json`, e nenhum `import json` rodou ali; a
  base 3 não tem lista dele e tem 0 erros da C nesse papel (1 execução com algum erro no período). Excluir não perde nada
  que se veja e evita o único risco que a evidência aponta. Nos outros papéis a C fica: o interpretador aceita `json` em
  todos os vistos, e o bilhete é um lembrete, com a mesma causa (esquecimento) onde o prompt lista o `json` e onde o omite.
  Para valer, a memória precisa de um alcance "global, exceto papéis": feito no catálogo (`nao_vale_em`, Ajuste 30, o
  jeito B, escolhido pelo Rafael em 26/10 — sem mexer no esquema, para não exigir rodada nova) → dossiê do sandbox §2h, 27–28.
- **26/10, "uma causa só" passa nas três memórias do sandbox que vão para o agente** (decisões do Rafael, uma por vez):
  a **C** (esquecimento; 0 de 423 importados antes, import nunca barrado); a **C.JoogleAnalytics** (esquecimento, 0 de 231;
  nota: em 77% o passo seguinte dá outro erro — o degrau 3 anota qual); a **E** (inspeção, 92% dos 317; nota: os 8% de outros
  usos são funções barradas, o "não chame" continua certo). Gravadas em `registros/decisoes_degrau2.json` pelo
  `conferir_memorias.py --decidir` → dossiê do sandbox §2h, 27.
- **23/10, a recuperação depois do erro é contada por trajetória, não por erro, e entra no relatório** (decisão do
  Rafael, ao pedir um sinal de recuperação do sistema inteiro na base 3, que é censo dos erros): o gráfico "o que vem
  depois do erro" da parte 1 conta por erro (uma cascata de 5 erros entra 4 vezes como "errou de novo") e só vê o passo
  seguinte; fica como está, para a pergunta "que erro prende o agente". O novo conta cada papel numa execução uma vez,
  do primeiro erro até o fim do papel: um erro só, cascata, recaída (os três seguidos de nenhum erro estruturado até o
  fim), terminou no erro, limite de passos, indeterminado. Dois gráficos na parte 2: a população (execuções, com o
  denominador das contagens, e papéis com erro) e um por papel. **Por que dá sem o trace completo:** a base 3 tem todos
  os erros de cada papel (a junção confere chave a chave), e as sequências saem dos vizinhos da query (o seguinte errou ou
  não), conferidos par a par. **A numeração não serve de posição:** na base 1, o `step_number` difere da posição do
  ActionStep no papel em 1.749 de 5.781 passos (30,3%) e recomeça em 491 de 1.550 papéis (nova chamada). **Teste com
  resposta conhecida na base 1:** 354 de 354 trajetórias na mesma categoria pelo trace completo e só pelos erros. Lido
  das contagens e da fonte, sem rodada nova → `execucao/recuperacao.py`, `figuras_taxas.recuperacao_*`,
  `validacao/conferir_recuperacao_base1.py`, teste `test_recuperacao_base3`; base 3, roadmap #56; falta rodar na
  máquina 2.
- **23/10, a genealogia vira duas figuras, e a da decisão começa na assinatura** (decisão do Rafael): família e
  assinatura (o sintoma) e mecanismo, unidade e destino (a decisão) são análises diferentes e não ficam numa figura só.
  **Por que a assinatura entra na decisão e a família não**, medido nas arestas (ensaio da base 1, 20/10): família →
  assinatura é uma árvore (nenhuma assinatura em duas famílias) e vai para um censo em barras; assinatura → mecanismo
  diverge e converge (11 de 21 assinaturas se abrem em mais de uma causa, 10 de 21 causas recebem mais de uma assinatura)
  — é a única passagem com cruzamento, e sem ela o Sankey da decisão seria uma árvore; mecanismo → unidade só converge
  (por construção: o dicionário causa → unidade); unidade → destino segue reto (D4 de 16/10, uma coluna só). O erro
  estruturado é o evento que flui pela figura; a assinatura é o rótulo do sintoma dele. **O recorte por unidade**
  (`execucao/figuras_genealogia.py --unidade U_sandbox`, fora do `executar.py` porque ele entra no hash de código) é exato porque cada causa vai para uma unidade só; o script recusa se
  isso deixar de valer. **A cor das duas figuras é a família do erro** (a do censo, 10 cores da paleta, a fita mantém a cor do começo ao fim); o
  destino fica escrito na última coluna. Pintar pelo destino foi testado e descartado (Rafael, 23/10): no recorte de uma
  unidade, que tem um destino só, tudo saía de uma cor; a família mostra de que tipo de erro vem o que termina em cada
  decisão (no `U_sandbox` da base 1, os 16 erros são todos de Ambiente & sandbox). A versão de 22/10 (decisão = mecanismo → unidade, sem a assinatura) foi revertida → painel,
  `execucao/figuras_genealogia.py`, teste `test_genealogia_figuras_base3`; base 3, roadmap #57; falta rodar na máquina 2.
- **20/10, as memórias C e E do sandbox se dividem pelo ambiente** (decisão do Rafael, no fechamento do sandbox): (1)
  **C** — uma memória global só leva os módulos que estão em todas as listas autorizadas vistas; os outros (o `pd`, por
  exemplo) viram memória do papel (`U_sandbox.C.<papel>`), com o import escrito, e "não está na lista autorizada deste
  papel" onde o módulo não está; (2) **E** — sai do texto `globals`, `locals`, `vars` e `eval` (o "não chame `globals`"
  brigava com o prompt do ContestacaoCivel: o degrau 2 reprovou a E no conflito, §2g–§2h); os erros desses nomes que
  sobram no sandbox depois dos Ajustes 21, 23 e 27 vão para uma parte própria, **F**, com destino em aberto — a
  população da memória "como verificar no sandbox" (`b3 #51`); E fica com a depuração → racional do sandbox, emenda 9;
  dossiê §2h, 9.
- **20/10, a memória E perde a dica "para ler JSON, use json.loads"** (decisão do Rafael, na etapa 5 do fechamento do
  sandbox): a E é global, e o `json` não está na lista autorizada de quatro papéis no prompt da base 1 (OBFCivel,
  RoteadorCivel, managerAgent, ContestacaoCivel) — o degrau 2 do ensaio reprovou a E no ambiente por isso. A dica servia
  ao `eval(texto)`, que foi para a parte F, e a ≈ 5 `__import__('json').loads` do ContestacaoCivel. Fica "Para inspecionar
  um valor, use print(type(x)) e print(str(x)[:n])." (testado no interpretador: funciona); pode voltar se o `json` for
  confirmado em todas as listas → racional do sandbox, emenda 9; dossiê §2h, 9.
- **20/10, o monitoramento tem dois níveis** (decisão do Rafael): monitoram-se sempre erros, contados no recorte da
  **unidade** (a tabela do pipeline; `monitorar.py` e `monitoramento.json`, no passo 0 — os sinais de harness) ou no
  recorte de uma **memória** (unidade × parte × papel; o resultado da mineração e o catálogo; `catalogar_memoria.py`, no
  passo 9, compara com a contagem anterior — as memórias raras e as de reforço). O `monitorar.py` não muda: o pipeline não
  etiqueta a parte, e um item no recorte da memória contaria a unidade inteira ou pararia o passo 0 das outras bases. O
  alarme de uma memória só dispara quando a unidade dela é minerada de novo → [`16`](2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md)
  ("O monitoramento", "Dois níveis"); [glossário](glossario.md) (tipos de monitoramento).
- **20/10, a régua de memória rara se aplica; sobra uma** (decisão do Rafael, fecha o `b3 #48`): das 6 memórias do
  sandbox que falham na recorrência, as 5 de "import fora da lista" já são *memória de reforço* (decisão 3); a
  `U_sandbox.B.RespostaBacen` (1 erro, jan/26) fica **monitorada como memória rara**, não injetada, no nível da memória
  (catálogo). Achado no caminho: `python_interpreter` é ferramenta-base do smolagents só para o `ToolCallingAgent` (o
  `CodeAgent` não a recebe — por isso nunca está no prompt), mas o `CodeAgent` registra cada passo de código como uma
  chamada de ferramenta `python_interpreter`, que volta ao modelo no histórico ("Calling tools: … 'python_interpreter'
  …"; `agents.py` e `memory.py`, smolagents 1.26.0). Hipótese: o agente vê o nome no histórico e tenta importá-lo (34 erros
  no OBFCivel e 1 no RespostaBacen, na base 3). O texto das memórias B com nomes do framework muda no script específico:
  não "chame-as direto", e sim "não importe `python_interpreter`/`tools`/`smolagents`: o seu código já roda no
  interpretador" → [dossiê](2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md) §2h; base 3,
  [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #48 (fechado) e #50.
- **20/10, o `monitorar.py` ler a base 3 é item próprio, fora do fechamento do sandbox** (decisão do Rafael): o passo 0
  segue "não conferido" na base 3 (as tabelas dela têm outro formato); o sandbox fecha com os itens registrados, e a
  recontagem automática na base 3 vem com o item do kit → base 3, [roadmap](2026-10-trace-law-flow-third/docs/04-roadmap.md) #52.
- **16/10, a parte específica da mineração é um script, não um notebook:** em `pipeline/especificas/`, com teste na suíte,
  lendo a rodada conferida pelo código do pipeline e com manifesto próprio; fora do hash do código da rodada. A skill
  passa a `propor-script` e o agente a `validador-de-script`. Os notebooks da base 1 continuam como legado → livro-razão,
  [Ajuste 20](pipeline-entre-bases.md#ajuste-20--a-parte-específica-da-mineração-passa-a-ser-um-script-não-um-notebook); `16`, "Como o script roda".

---
