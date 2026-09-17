# Diário de Campo — Rafael Coelho Ventura

## Semana de 14/09 a 18/09/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 14/09/2026

**Tipo:** achado — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Ao revisar com um agente (sem provider definido) a tabela de 7 candidatos a unidade de memória do notebook de análise de trace (`analysis/2026-09-trace-law-flow/`), questionou a afirmação de que a tabela e os 4 `tipo` (semântica/procedural/experiencial-procedural/harness) estavam "fundamentados no AgentDebug". O agente abriu o PDF original do paper (arXiv 2509.25370, 32 páginas — a nota de leitura só citava seção, não página) e buscou o texto completo por "rout"/"memory type"/"semantic memory"/"procedural memory": zero ocorrências. Confirmado que o AgentDebug propõe uma taxonomia de 5 módulos diagnósticos (memory/reflection/planning/action/system, Tabela 2, p. 14) e o princípio de escrita por causa-raiz (p. 2 e p. 8), mas **não** propõe tipos de memória nem fala em "roteamento" — os 4 `tipo` da tabela são analogia própria do projeto, não citação do paper. Corrigido em três arquivos: célula 9 do notebook, `01-racionais.md` §7 Passo 2, `02-relatorio-achados.md` §6.

**Reflexão:** Na sequência, comparou a taxonomia do AgentDebug com a do TRAIL (arXiv 2505.08638) para entender se são redundantes ou complementares. Concluiu que olham eixos diferentes: AgentDebug classifica por **em que módulo cognitivo do agente** o erro nasceu (processo interno, exige tags `<memory>/<reflection>/<plan>/<action>`, prescreve correção via `correction_guidance`); TRAIL classifica por **que tipo de erro é** (fenômeno observável por span do trace, sem exigir tags internas, mede gravidade via `impact` HIGH/MEDIUM/LOW, cobre coordenação multiagente — que o AgentDebug estruturalmente não cobre). São complementares: AgentDebug dá a forma da unidade de memória (causa + correção), TRAIL mede o que ainda não é visto — 59% dos tipos de erro do TRAIL são estruturalmente invisíveis à classificação por exceção Python que o pipeline usa hoje, e o paper fornece um menu de 11 detectores determinísticos ranqueados por custo×impacto, dos quais só 2–3 estão hoje no roadmap (`04-roadmap.md`). Ficou claro também que só o AgentDebug foi "promovido" de leitura 🔎 (por subagente) para ✅ (leitura dirigida) — o TRAIL segue em 🔎, e o próprio overclaim corrigido hoje é um caso de estudo direto de por que essa promoção importa antes de uma nota virar citação formal numa seção de "fundamentação emprestada" (`papers/reading-queue.md`: nota existente ≠ lido).

**Decisão/próximo passo:** Vai ler o TRAIL agora, com atenção, para promovê-lo de 🔎 a ✅ como foi feito com o AgentDebug em 09/09. Ficou pendente de decisão (não executado ainda): creditar o TRAIL no item 6 do roadmap (hoje sem atribuição, apesar de descrever o mecanismo de *Tool Selection Errors* do TRAIL) e avaliar se adiciona o detector "Resource Abuse" (custo trivial, reaproveita código já existente) como item novo na tabela analítica do roadmap.

**Tags:** achado, agentdebug, trail, overclaim, citacao, verificacao-de-fonte, taxonomia-de-erro, modulo-vs-fenomeno, complementaridade, ponto-cego, roadmap, fichamento, promocao-de-leitura, fundamentacao-emprestada, reading-queue, sub-2.1, sub-2.2

## 15/09/2026

**Tipo:** achado — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Confirmado que a esteira de fluxo jurídico permite, sim, uma análise de reasoning nos moldes da taxonomia de eixo cognitivo do AgentDebug. Dois agentes — Cálculo Cível Trabalhista e Agente Bacen — possuem uma etapa `planningStep` ausente nos demais fluxos analisados. Essa etapa expõe a tag `<plan>`, além de `thought` e `observation`, o que torna possível desenhar um novo eval de consistência: comparar o que foi decidido no plano contra se cada etapa desse plano foi de fato executada.

**Reflexão:** É o primeiro caso concreto na base de um agente com estrutura suficiente para aplicar a classificação por módulo cognitivo do AgentDebug (`<plan>`/`<action>`/etc.) em vez de só a classificação por fenômeno observável do TRAIL — os dois agentes com `planningStep` viram candidatos naturais para pilotar esse eval de aderência plano→execução antes de tentar generalizar para o resto da esteira, que não expõe essa etapa.

**Decisão/próximo passo:** Desenhar o eval de consistência plano-execução para os dois agentes com `planningStep` (Cálculo Cível Trabalhista, Agente Bacen).

**Tags:** achado, agentdebug, planningstep, tag-plan, thought, observation, eval-de-consistencia, plano-vs-execucao, calculo-civil-trabalhista, agente-bacen, eixo-cognitivo, esteira-juridica, sub-2.1, sub-2.2

### Leitura — TRAIL finalizado, promovido de 🔎 a ✅

**Tipo:** leitura — **Sub-atividade:** 2.1 — **Canal:** pessoal

**Registro objetivo:** Finalizou hoje a leitura própria do TRAIL (arXiv:2505.08638), cumprindo a decisão registrada em 14/09 — promovido de 🔎 (leitura por agente) para ✅ no fichamento e na fila de leitura, como feito com o AgentDebug em 09/09. Continua investigando a base sob a ótica do TRAIL: a vertente do paper que mede erros invisíveis no pipeline (taxonomia + dataset anotado), a partir da qual o fichamento já deriva 11 análises executáveis próprias (§4, `trail-2505.08638.md`) — heurísticas nossas mapeadas sobre a taxonomia do paper, não uma ferramenta que o TRAIL propõe — consideradas de mais valor para a análise atual do que a classificação por exceção Python. **Correção 15/09 (checado contra o fichamento a pedido do Rafael):** a formulação original desta entrada ("a contribuição de detectores determinísticos [do TRAIL]") overclaimava — o TRAIL contribui a taxonomia e o dataset anotado; os 11 detectores são derivação própria do projeto, não algo que o paper entrega como ferramenta.

**Reflexão:** Fecha o cluster de leitura dirigida AgentDebug+TRAIL iniciado em 09/09 e retomado em 14/09; faltam MAST e ToolScan para completar os quatro papers do cluster de taxonomia de erro.

**Decisão/próximo passo:** Seguir investigando a base pela ótica das 11 análises executáveis que já derivamos da taxonomia de pontos-cegos do TRAIL (fichamento §4, ranqueadas por impacto×facilidade), das quais só 2–3 estão hoje no roadmap — pendência já registrada em 14/09.

**Tags:** leitura, trail, promocao-de-leitura, fichamento, erros-invisiveis, detectores-deterministicos, custo-x-impacto, roadmap, cluster-taxonomia-de-erro, sub-2.1

### Achado — triagem de candidatos a memória refeita por mecanismo (régua: Hu et al. 2025)

**Tipo:** achado — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Pediu para revalidar a §7 de `01-racionais.md` (tabela de 7 candidatos a unidade de memória e o gráfico), por achar confusos o Passo 4 ("5 assinaturas excluídas por terem várias causas") e a ressalva sobre o AgentDebug, usando o survey *Memory in the Age of AI Agents* (Hu et al. 2025, arXiv 2512.13564, §4) como régua. Um agente (sem provider definido) refez a análise do zero, reexecutando o notebook inteiro duas vezes: saídas idênticas, e os CSVs das outras seções byte-idênticos à versão anterior. Novo método: cada um dos 498 erros recebe um **mecanismo** por regra fixa (mensagem de exceção + linha de código rejeitada, sem LLM); erros repetidos em sequência no mesmo papel contam uma vez (437 ocorrências); a triagem exige conteúdo único e ≥3 execuções em ≥2 meses; o tipo vem da função do conteúdo em Hu et al. — *factual · ambiente* (§4.1.2, p. 36) ou *experiencial · estratégia* (§4.2.2, p. 40), trechos conferidos no PDF. Resultado: 14 unidades — **10 candidatas** (5 de cada tipo), 2 não-memória, 2 fora —, cobrindo 90% dos erros e 92% dos tokens em steps com erro. Nenhuma das 5 assinaturas excluídas era multi-causa: 3 eram a mesma causa de um candidato existente, escrita com outra exceção; 2 escondiam causas novas. A assinatura "Retorno é dict" (136 erros) se dividia em três: 89 dict indexado por posição, 37 **string** indexada por chave, 10 campo inexistente. O contrato das ferramentas de documento caiu para 96 erros, todos do `ConversationAgent`; surgiu a candidata "Retorno pode chegar como string" (47 erros, 36 execuções, 7 meses, 7 papéis).

**Reflexão:** O critério "causa única, conteúdo numa frase" estava certo; o erro era aplicá-lo à mensagem de erro em vez de a cada erro. A política "uma unidade por cascata, na raiz" era citada na §7, mas nunca tinha sido aplicada no cálculo. A revisão achou ainda dois pontos que contradiziam a triagem: `01-racionais.md` §1 ainda atribuía ao AgentDebug o "roteamento módulo→tipo de memória" (o overclaim de 14/09), e o §2.2 do relatório dava a causa errada para `CalculoCivel` e `RespostaBacen`. Os dois foram corrigidos.

**Decisão/próximo passo:** Tabela e gráfico novos no notebook (§9) e nos docs (`01-racionais.md` §7, `02-relatorio-achados.md` §6, `04-roadmap.md`, nota do survey em `papers/`). Limítrofe: "Após step com erro, o que ele definiria não existe" sai da triagem com ≥5 execuções e ≥3 meses. Pendente: variar as regras do submecanismo — hoje só conferidas por amostra.

**Tags:** achado, triagem, candidatos-memoria, mecanismo, sintoma, hu-2025, factual-ambiente, experiencial-estrategia, cascata, ocorrencia, idempotencia, overclaim, agentdebug, retorno-como-string, sub-2.1, sub-2.2

### Decisão — as três etiquetas de um erro: sintoma → mecanismo → motivo

**Tipo:** decisão — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Formulou a distinção que passa a organizar a classificação de erros. **Etiqueta 1 · sintoma:** o que o Python reclamou (a mensagem, via `classify()`). **Etiqueta 2 · mecanismo:** o que o agente fez de errado — o nível do TRAIL, obtido por regra fixa. **Etiqueta 3 · motivo:** por que ele fez isso — o nível do AgentDebug, só alcançável lendo o raciocínio, com humano ou juiz LLM. Analogia: febre → amigdalite ou pneumonia → qual micro-organismo, qual exposição. Exemplo real, conferido no trace cru (`RespostaBacen`, execução `1be966e7…`): "Could not index … KeyError: 'quebra_sigilo'" → campo inexistente no retorno → o nome da ferramenta `validar_quebra_sigilo` induziu o agente a pedir `quebra_sigilo`, mas o campo real é `vazamento_sigilo`. Ficou definido onde cada etiqueta vale:
- **sintoma:** inventário e custo (8.1, §2.3, §3.2); os gráficos que não usam etiqueta não mudam;
- **mecanismo:** repetição e lição (§2.2/8.8, 8.5, §5, §6/8.4, §7);
- **motivo:** decidir onde vai o conserto e escrever/validar a memória — na fase dos candidatos de verdade, com gold standard.

Documentado em `01-racionais.md` §8.

**Reflexão:** Ajuste no próprio entendimento: o TRAIL também lê o raciocínio do agente — a diferença para o AgentDebug está na pergunta (*que tipo de erro aconteceu* × *em que parte do raciocínio ele nasceu*), não no que cada um lê. Na numeração do `04-roadmap.md`, "camada 2" é o motivo, não o mecanismo.

**Correção 15/09, mais tarde na mesma sessão (checado campo a campo contra os dois PDFs, a pedido do Rafael):** a equivalência "Etiqueta 2 = mecanismo = TRAIL; Etiqueta 3 = motivo = AgentDebug" não se sustentou. `01-racionais.md` §8, na versão final depois de três rodadas de correção, conclui o oposto: os dois papers ficam no **mesmo degrau** — diagnóstico, isto é rótulo reaproveitável + descrição do caso (`category`/`description` no TRAIL; `error_type`/`root_cause` no AgentDebug Stage 2) — nenhum "é" o mecanismo e o outro "é" o motivo. O que de fato distingue os dois é qual campo extra cada um carrega e o outro não tem: **TRAIL tem `impact`** (severidade HIGH/MEDIUM/LOW, ausente no AgentDebug); **AgentDebug tem `correction_guidance`** (diretiva corretiva, Stage 2 — o único dos dois que chega ao degrau 3, "correção"; TRAIL não tem equivalente). A tabela de "onde cada etiqueta vale" (sintoma/mecanismo/motivo, linhas acima) continua útil como guia prático de qual granularidade usar em cada análise do notebook — isso não mudou. O que mudou é só a atribuição "etiqueta = paper": não existe essa correspondência 1:1. Ver `01-racionais.md` §8 para a versão corrigida, com a tabela campo a campo e as citações verbatim que a sustentam.

**Correção 16/09 — completando a de 15/09, não a desfazendo (a pedido do Rafael, que apontou que faltava a
distinção mais estrutural).** A correção de 15/09 acima vale para **um** eixo — o que cada *schema de saída*
carrega (produto): nisso, de fato, os dois ficam no mesmo degrau, e a diferença é campo a campo (`impact` só no
TRAIL, `correction_guidance` só no AgentDebug). Mas existe um segundo eixo, de **método**, que essa correção não
cobria e que não contradiz a primeira: **os dois usam lentes diferentes, e as duas fazem sentido para o
projeto.** AgentDebug analisa em **nível de módulo cognitivo**, com busca dirigida a um alvo causal único — o
*critical error*, o passo mais precoce cuja correção evitaria o fracasso da trajetória — porque seu racional
central é que a **propagação de erro** é o que mais compromete a confiabilidade do agente. TRAIL analisa em
**nível de sistema/observabilidade** — o trace já estruturado em spans OpenTelemetry/OpenInference — e audita
exaustivamente todo span, sem buscar uma raiz única. Constroem a taxonomia de formas distintas por isso: os 5
módulos do AgentDebug nascem de uma arquitetura cognitiva imposta ao agente (tags forçadas no prompt); as 3
áreas/20 tipos do TRAIL nascem de observar erros num formato de trace já estruturado por infraestrutura, sem
exigir nada do agente. Nenhuma lente é mais "certa" — uma dá cobertura (quanto do que aconteceu estamos vendo),
a outra dá causa raiz (qual passo consertar primeiro). Documentado como novo parágrafo em `01-racionais.md` §8,
antes da tabela campo a campo.

**Tags:** decisao, etiquetas-de-erro, sintoma, mecanismo, motivo, causa-raiz, trail, agentdebug, analogia-febre, quebra-sigilo, juiz-llm, gold-standard, correcao, overclaim, lentes-distintas, nivel-de-modulo, nivel-de-sistema, opentelemetry, propagacao-de-erro, erro-critico, sub-2.1, sub-2.2

### Implementação — mecanismo aplicado às análises de repetição, triangulado com drill_down

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** A pedido do Rafael, um agente (sem provider definido) aplicou o mecanismo às análises de repetição e de lição do notebook: mecanismo por papel (§2.2 e 8.8), custo por mecanismo (§3 e 8.5), reincidência dentro da execução (§5) e mês a mês (§6 e 8.4). A célula "Do sintoma ao mecanismo" passou para a §2. Números:
- **Reincidência:** 11,9% por mensagem × **13,5% por mecanismo** — as réguas concordam em 65 de 76 repetições; 20 dos 58 casos vêm do laço de dez/2025.
- **Recorrência entre meses:** "texto longo dentro de literal" aparece nos 9 meses com dado.
- **Por papel:** `CadastroTrabalhista` 94% argumento nomeado; `CalculoCivel` 76% retorno como string; `managerAgent` 62% texto longo; `RespostaBacen` empate entre campo inexistente e string (33% cada).

O notebook foi reexecutado duas vezes, sem erro e com saídas idênticas. `drill_down.py` ganhou o comando `mecanismo`. Seis casos foram conferidos no trace cru:
- `CalculoCivel` `42891135…`: a ferramenta de correção monetária devolve JSON como texto; o agente quebra e corrige sozinho com `json.loads` no step seguinte;
- `RespostaBacen` `1be966e7…`: o caso `quebra_sigilo`;
- `ConversationAgent` `008d142f…` (`docs[0]`) e `0adcc967…` (`next()` sobre gerador);
- os dois pares em que mensagem e mecanismo discordam (`cd794f02…`, `95344639…`).

Documentos atualizados: racionais §3 (Passo 8) e §6; relatório TL;DR, §2.2 e §4; procedimento §1.5, §1.6 e triangulação — nesta última, o comando foi corrigido para rodar a partir de `pipeline/`.

**Reflexão:** O caso do `CalculoCivel` é a tese em miniatura: o agente aprende a lição dentro da execução e a perde na próxima. A manchete continua 11,9%; por mecanismo, o achado fica um pouco mais forte, não mais fraco.

**Decisão/próximo passo:** Pendentes:
- **grupo 1:** renomear na `classify()` as 4 etiquetas que afirmam uma causa falsa para parte do conteúdo — "Retorno é dict…", "Sintaxe inválida (prosa…)", "Variável inexistente (estado perdido)", "Import/ferramenta não autorizado" —, dar nome à caixa não classificada e mudar o título do 8.1 para "por mensagem de erro";
- conferir a divergência na tabela da §3.3 do relatório (`ConversationAgent` 27.988 no doc × 27.062 no notebook; `managerAgent` 18.775 × 17.592);
- nada foi commitado ainda.

**Tags:** implementacao, notebook, mecanismo, reincidencia, 11-9-vs-13-5, drill-down, triangulacao, calculocivel, respostabacen, racionais, relatorio, procedimento-validacao, grupo-1-pendente, sub-2.2

## 16/09/2026

**Tipo:** achado — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Retomou a mineração das unidades de memória, partindo de uma primeira análise de erros muito genérica, que fez sentido no início para conseguir agregar o volume de erros do trace. A partir dela, desenvolveu a metodologia de rodar análises independentes por script, com o `drill_down.py` disponível para investigar o trace cru por palavras-chave quando necessário. Numa segunda análise, roteou os erros para unidades de memória mais específicas — menos genéricas que a primeira. Exemplo concreto: um grupo genérico juntava erros de "serialização de lista" quando na verdade o objeto era um dict com chave e valor — grupo genérico porque escondia várias causas diferentes. Chegou à analogia que passou a organizar o trabalho: a primeira análise olhava o sintoma (ex.: "tenho febre"), e a febre é causada por vários mecanismos distintos; a segunda análise focou em separar por mecanismo. Constatou que alguns grupos de erro precisavam de subcategoria própria.

**Reflexão:** Apesar de a segunda análise ir para o mais específico, continua achando que memórias mais gerais, na forma de regras, também têm valor — não é uma substituição de granularidade, é uma granularidade adicional.

**Tags:** achado, mineracao-de-memoria, sintoma-vs-mecanismo, analogia-febre, drill-down, submecanismo, granularidade, sub-2.1, sub-2.2

## 17/09/2026

**Tipo:** achado — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Concluindo essa abordagem, minerou as duas primeiras unidades de memória, nomeadas nº2 e nº10. A unidade nº2 trata do retorno das ferramentas de documento como dict; a nº10 trata de um campo inexistente no retorno estruturado. Investigou dois agentes — `ConversationAgent` e `RespostaBacen`. Ao aprofundar nos traces e nas derivações, encontrou que os erros da unidade nº2 vinham de o agente não entender o schema usado pela ferramenta, faltando indexar pelo campo `result`. Já a nº10 estava relacionada a uma ferramenta cujo contrato de retorno está incorreto — na verdade, o próprio prompt que o agente recebe induz o agente a usar um nome de campo que não é válido no contrato real da ferramenta. Chegou assim às duas primeiras unidades de memória mineradas.

**Reflexão:** Ver as duas unidades saírem inteiras do trace — o schema real de retorno da ferramenta e o contrato induzido pelo prompt — confirma que a abordagem por mecanismo (e não por sintoma) chega a um conteúdo realmente ensinável, no formato de frase única que motivou a mudança de método em 16/09.

**Decisão/próximo passo:** Uma vez fundamentada, essa metodologia (sintoma → mecanismo → unidade de memória, com mineração aprofundada caso a caso) passa a ser a base para as próximas análises do projeto.

**Tags:** achado, mineracao-de-memoria, unidade-2, unidade-10, conversationagent, respostabacen, schema-de-retorno, contrato-de-ferramenta, campo-inexistente, prompt-induz-erro, sub-2.1, sub-2.2
