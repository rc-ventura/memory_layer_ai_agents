---
name: checkpoint-reuniao
description: "Processa a transcrição crua de uma reunião (tutor, infra, colega) no repositório do projeto Inova Talentos / IPT Open (Nº 1335844346, mecanismo de atualização de memória para agentes de IA em fluxos jurídicos), seguindo o meeting-record pattern de docs/README.md: (1) extrai o texto da fonte em docs/sources/, (2) grava um resumo factual em português em docs/checkpoints/, (3) triangula a reunião contra a hipótese de arquitetura, open-questions.md, as decisões de escopo, o work-plan e o registro da reunião de infra (cross-check obrigatório do que é infra viva vs. proposta), (4) gera uma nota de reflexões em discussion/ e (5) atualiza os docs canônicos afetados (open-questions, arquitetura, scope-and-terminology) e os índices. SEMPRE apresenta o resultado para aprovação antes de considerar fechado. Use SEMPRE que a mensagem for '/checkpoint-reuniao', 'processa o checkpoint', 'processa essa reunião', 'processa a transcrição', 'anexa e processa a transcrição', 'roda o meeting-record dessa reunião', 'gera o checkpoint da reunião de <X>', ou quando o Rafael apontar um arquivo novo em docs/sources/ e pedir para transformá-lo em checkpoint + reflexões. Aceita um caminho de arquivo e/ou um slug alvo. NÃO use para registrar uma entrada no diário de campo nem para o export .docx mensal do coordenador — isso é a skill diario-campo. NÃO use para o relatório mensal da instituição. NÃO acione implicitamente só porque uma reunião foi mencionada na conversa — só quando o Rafael pedir para processar a transcrição."
---

# Checkpoint de reunião — meeting-record pattern automatizado

## Por que este design (contexto que não pode se perder)

O repositório separa, para cada reunião que moldou escopo ou arquitetura, **dois artefatos com funções distintas** (ver `docs/README.md` → "Meeting-record pattern"; todos os caminhos nesta skill são relativos à raiz do repo):

1. **Resumo factual** em `docs/checkpoints/` — em **português** (idioma da fonte), **só o que foi dito/mostrado**, sem análise. É a camada "episódica" da reunião: barata de reler, fiel à fonte, serve de âncora citável.
2. **Reflexões cross-cutting** em `discussion/` — em **inglês** por padrão (consistência de cross-links da pasta), conectando a reunião ao Plano de Trabalho, às decisões já registradas e às questões abertas, e **atualizando esses arquivos com backlinks**. É a camada "semântica": interpretação, tensões, novas perguntas.

Essa separação é a mesma episódico/semântico que o projeto estuda no próprio mecanismo de memória (Sub 2.2) — factual imutável, derivado regenerável. Não a colapse: o checkpoint nunca leva análise; as reflexões nunca substituem o factual.

Regra de ouro das edições em doc canônico: **os docs de decisão/arquitetura são append-only em cima do que já está assentado.** Uma reunião nova não reescreve `open-questions.md` nem `knowledge-as-infra-architecture-hypothesis.md` — ela **anexa uma nota datada com backlink** ao item afetado. O padrão já existente no repo é `**Update DD/MM/AAAA (tutor checkpoint — [`checkpoint-...-reflections.md#N`](...)):** ...`.

## Quando acionar / não acionar

**Acione** quando a mensagem for `/checkpoint-reuniao` ou um pedido equivalente para **processar a transcrição de uma reunião**: "processa o checkpoint", "processa essa reunião", "anexa e processa a transcrição", "roda o meeting-record", "gera o checkpoint da reunião de X". Também quando o Rafael apontar um arquivo novo em `docs/sources/` (`.docx`, `.txt`, `.vtt`, `.md`) e pedir para transformá-lo em checkpoint + reflexões.

**Não acione:**
- Para registrar uma entrada no **diário de campo** ou gerar o **export `.docx` mensal do coordenador** — skill `diario-campo`.
- Para a **síntese mensal do diário** — skill `sintese-diario`.
- Para o **relatório mensal da instituição** (`docs/reports/`).
- **Implicitamente**, só porque uma reunião foi citada na conversa. Só quando o Rafael pedir para processar a transcrição.

## O que a skill produz

| Artefato | Local | Idioma | Natureza |
|---|---|---|---|
| Resumo factual | `docs/checkpoints/checkpoint-AAAA-MM-DD-<slug>.md` | português | só o que foi dito/mostrado, sem análise |
| Reflexões | `discussion/checkpoint-AAAA-MM-DD-reflections.md` | inglês (padrão da pasta) | confirma / tensiona / abre, com backlinks |
| Edições datadas | `discussion/open-questions.md`, `discussion/knowledge-as-infra-architecture-hypothesis.md`, `discussion/scope-and-terminology-decisions.md` (as que forem afetadas) | mesmo idioma do arquivo | notas datadas anexadas, nunca reescrita de texto assentado |
| Linhas de índice | `discussion/README.md` (tabela), `docs/README.md` ("Meetings recorded so far") | — | uma linha nova cada |

## Fluxo obrigatório

Use as ferramentas de arquivo (Glob / Read / Write / Edit) para tudo que for repo. Shell só para extrair texto da fonte binária.

### 0. Identificar a fonte e o alvo

- **Fonte:** o arquivo em `docs/sources/` que o Rafael indicou (por caminho ou por nome). Se ele não indicou, `Glob` `docs/sources/*` e pegue o mais recente que **ainda não tem** checkpoint correspondente em `docs/checkpoints/`; confirme com ele antes de prosseguir.
- **Data:** extraia da própria transcrição (linha de cabeçalho tipo "August 28, 2026") ou do nome do arquivo. Formato do nome de arquivo: `AAAA-MM-DD`.
- **Slug:** curto, minúsculo, hifenizado, descrevendo a reunião — `tutor`, `infra-arquitetura`, `tutor-kickoff`, `hermes-memoria`. Se houver duas reuniões no mesmo dia, o slug desambigua os dois arquivos.
- **Tipo de reunião:** tutor / infra / colega — determina participantes e o tom do "Por que essa reunião importa".
- **Meeting-prep:** procure um `discussion/component-*-meeting-prep.md` ou `discussion/*-prep.md` relacionado. Se existir, os checkboxes/perguntas dele são um checklist a confrontar com o que a reunião resolveu (marque no arquivo de prep o que foi respondido, com data e onde ficou — só se de fato foi).

### 1. Extrair o texto da transcrição

- `.docx` → `pandoc -f docx -t markdown "<fonte>" -o <scratchpad>/<slug>.md` (ou `python3 -c "import docx; ..."` se `pandoc` não existir). Grave o texto extraído **na pasta de scratchpad da sessão, nunca no repo**; apague `media/` e qualquer artefato que o pandoc deixar na raiz.
- `.vtt` / `.txt` / `.md` → leia direto.
- Note as **limitações da fonte**, para registrar no cabeçalho do checkpoint:
  - transcrição automática (rótulos de fala podem estar trocados);
  - captura parcial (compare a duração declarada com o timestamp da última fala — ex.: "53 min" mas a última fala é 42:17 → ~11 min não capturados);
  - **screen-share não entra na transcrição de áudio** — se a reunião teve tela compartilhada, o que foi *mostrado* pode não estar no texto (precedente: a emenda de 25/08 em `checkpoint-2026-08-21-infra-reflections.md#3`). Sinalize isso como possível lacuna, não afirme que não houve conteúdo visual.

### 2. Resumo factual → `docs/checkpoints/`

Escreva `docs/checkpoints/checkpoint-AAAA-MM-DD-<slug>.md`, seguindo o padrão dos checkpoints já em `docs/checkpoints/` (`checkpoint-2026-08-20-tutor-kickoff.md`, `checkpoint-2026-08-21-infra-arquitetura.md`, `checkpoint-2026-08-28-tutor.md`):

- **Cabeçalho em itálico:** o que é a reunião, participantes (nome completo na primeira menção), data, duração, link para a fonte (`../sources/<arquivo>`), natureza da transcrição + limitações da §1, e a nota de que está em português por casar com a fonte / decisão do bolsista.
- **`## Por que essa reunião importa`** — 2–4 frases situando; ainda factual (o que a reunião cobre), não interpretação.
- **Seções `##` temáticas** — uma por bloco de assunto. **Só o que foi dito.** Cite trechos curtos entre aspas quando a formulação exata importa (é o que torna o arquivo citável). Nada de "isto confirma X" / "isto abre Y" — isso é reflexão.
- **Última seção: `## Não investigado aqui`** (ou `## Não resolvido nesta reunião`) apontando para o arquivo de reflexões e dizendo que o fechamento de loop no diário fica pendente de pedido explícito do Rafael.
- Links relativos a partir de `docs/checkpoints/`: fonte = `../sources/...`; discussion = `../../discussion/...`; outros checkpoints = nome do arquivo (mesma pasta).

### 3. Triangular

Leia (ou releia) e cruze a reunião contra:

- `discussion/knowledge-as-infra-architecture-hypothesis.md` — os componentes A–G, as fronteiras de escopo, o worked example.
- `discussion/open-questions.md` — cada item aberto: a reunião fecha, avança, ou não toca?
- `discussion/scope-and-terminology-decisions.md` — alguma decisão foi reforçada, matizada ou reaberta?
- `docs/work-plan.md` e `docs/sub-activity-map.md` — mudou sequenciamento, premissa, ponto de coleta de sinal?
- **O registro da reunião de infra — cross-check obrigatório.** `docs/checkpoints/checkpoint-2026-08-21-infra-arquitetura.md` + `discussion/checkpoint-2026-08-21-infra-reflections.md` (e qualquer checkpoint de infra mais recente — `Glob` em `docs/checkpoints/*infra*`). É a **fonte de verdade sobre o que é infra viva vs. o que é proposta**: os tópicos Kafka de conclusão de stage, o Postgres único por conta, a API "Yoda" + tópico Kafka assíncrono, os três mecanismos de memória já em produção, a ausência de auth centralizada (token propagado camada a camada), o banco de config de agentes. Toda afirmação da reunião nova sobre "isso já existe" / "a infra já faz isso" tem que ser conferida contra esse registro: **confirma** (a infra bate — cite o ponto do checkpoint de infra), **contradiz** (a reunião nova diz algo diferente do que a equipe de infra descreveu — sinalize a divergência, não escolha um lado sozinho), ou **é infra nova** (a reunião revela um recurso/limite que o registro de 21/08 não tinha — vira premissa nova, registrar como tal). Lembre da ressalva registrada em `discussion/checkpoint-2026-08-21-infra-reflections.md` (seção 3): a transcrição de infra é só áudio, o que foi *mostrado* na tela pode não estar no texto.
- Checkpoints e reflexões de tutor anteriores (`docs/checkpoints/*`, `discussion/checkpoint-*-reflections.md`) — a reunião confirma ou corrige algo de uma anterior?
- Notas temáticas relevantes: `discussion/thumbs-feedback-reliability.md`, `discussion/cross-trial-vs-forgetting-gap.md`, os `discussion/*-meeting-prep.md`.

Para cada ponto da reunião, classifique: **confirma/avança** (e o quê exatamente, com qual doc), **tensiona** (contradiz ou complica algo já escrito — reconciliação recomendada), **abre** (nova questão). Distinga sempre **retorno informal / convergência** de **sign-off formal** — o repo é rigoroso nisso; o critério de graduação de hipótese → decisão continua sendo a validação em POC (Sub 1.6/1.7), não uma reunião. Para afirmações sobre infraestrutura, distinga também **infra confirmada viva** (bate com o registro de infra) de **infra assumida** (inferência encadeada, ainda não confirmada pela equipe de plataforma) — é uma distinção que o doc de arquitetura já faz explicitamente (ex.: "confirmado live no checkpoint 21/08" vs. "inferência encadeada da lógica 'evitar nova dependência operacional'").

### 4. Reflexões → `discussion/`

Escreva `discussion/checkpoint-AAAA-MM-DD-reflections.md` no estilo das duas existentes:

- Blockquote de cabeçalho: `> **Sub-atividade:** ... · **Type:** Cross-cutting reflection on a primary source · **Logged:** [DD/MM/AAAA](../research-diary/...)`.
- Primeiro parágrafo: fonte (link para o checkpoint e para a `.docx`), natureza da transcrição, e o enquadramento (o que essa reunião foi).
- **Seções numeradas `## 1.`, `## 2.` …** — uma por achado, cada uma com título afirmativo. Ordem: primeiro o que confirma/avança, depois tensões, depois o que abre. Backlink para o item de `open-questions.md` ou a decisão afetada em cada seção.
- **`## What this meeting did not do`** — o que ficou de fora (ex.: um checklist de prep não percorrido, uma pergunta não feita).
- **`## Not investigated here`** — logística e afins que ficam só no checkpoint.
- Inglês por padrão. Só escreva em português se o Rafael pedir explicitamente para essa nota (override por-arquivo, como em `component-a-tutor-meeting-prep.md`).
- Convenção de atribuição de trabalho de agente de IA: genérica ("an agent, no defined provider", "agent-read, not Rafael-read"), nunca nomear assistente/modelo/provider — igual ao resto do repo.

### 5. Atualizar os docs canônicos afetados

Só os que a triangulação (§3) mostrou afetados. **Sempre `Edit` cirúrgico, nunca `Write` por cima.**

- **`discussion/open-questions.md`:**
  - Item existente afetado → **anexe** ao fim dele `**Update DD/MM/AAAA (tutor checkpoint — [`checkpoint-AAAA-MM-DD-reflections.md#N`](checkpoint-AAAA-MM-DD-reflections.md)):** ...`. Não apague o texto anterior; não mude o `**Not yet done.**` para resolvido a menos que a reunião realmente feche o item (aí mova a resolução para `scope-and-terminology-decisions.md` e remova daqui, como o cabeçalho do arquivo manda).
  - Questão genuinamente nova → **novo bullet** no formato dos outros (negrito na pergunta, contexto, trade-offs, `**Not decided.**` / `**Not yet done.**`, com data e backlink).
- **`discussion/knowledge-as-infra-architecture-hypothesis.md`:**
  - Nota datada de corroboração/tensão **anexada** ao componente afetado (`### A`…`### G`, ou a seção de fronteiras de escopo). Formato: `**Tutor corroboration, DD/MM/AAAA (reflections [`...#N`](...)).** ...` ou `**Scope-boundary revision, DD/MM/AAAA ...**`.
  - Se a reunião estreita/matiza uma linha de escopo, edite a linha **e** anexe a nota explicando por quê — nunca só apague.
- **`discussion/scope-and-terminology-decisions.md`:** só se uma decisão foi reforçada (nova fonte primária), matizada ou reaberta. Parágrafo datado dentro da seção da decisão. Não renumere seções.
- Se a reunião tocar `reading-queue.md`, `cross-trial-vs-forgetting-gap.md` ou um `*-meeting-prep.md`, aplique a mesma lógica (nota datada + backlink) e marque os checkboxes de prep que foram respondidos.

### 6. Manter os índices coerentes

- **`discussion/README.md`** — adicione uma linha na tabela para o novo `checkpoint-AAAA-MM-DD-reflections.md` (coluna "What it covers" = 1 frase). Ponha junto das outras linhas de checkpoint-reflections.
- **`docs/README.md`** — acrescente `checkpoints/checkpoint-AAAA-MM-DD-<slug>.md` à lista "Meetings recorded so far".
- **`CLAUDE.md` da raiz** — é índice, não rulebook. Só toque se algum ponteiro estiver quebrado; não adicione linha por reunião.

### 7. Apresentar para aprovação (o gate — obrigatório)

Antes de considerar o trabalho fechado, **apresente ao Rafael, na conversa** (não num arquivo):

1. O resumo de pontos-chave (o conteúdo do checkpoint, condensado).
2. A avaliação da triangulação: **confirma/avança**, **tensões**, **novas questões** — cada uma com o doc/ítem afetado.
3. As reflexões propostas (condensadas).
4. A lista exata de arquivos criados/editados.

Se o Rafael **já** disse na mensagem para fazer tudo ("faz tudo", "aplica direto", "não precisa perguntar"), grave e **depois** reporte o que foi feito. Caso contrário, ofereça as opções de escopo (só checkpoint; checkpoint + reflexões; padrão completo com as edições) e espere o OK antes de gravar os docs canônicos. O checkpoint factual em si pode ser gravado antes (é o pedido central e não é opinativo); as reflexões e as edições em `open-questions.md` / arquitetura / scope **precisam de OK**.

### 8. Verificar e reportar

- `Read` cada arquivo novo/editado para conferir estrutura e links.
- `git status --short` e liste o que mudou.
- Reporte: arquivos, o que ficou pendente (fechamento de loop no diário — só sob pedido explícito, via `diario-campo`), e o lembrete de que a skill **não fez commit nem push**.

## Convenção de nomes de arquivo

- Checkpoint: `docs/checkpoints/checkpoint-AAAA-MM-DD-<slug>.md`.
- Reflexões: `discussion/checkpoint-AAAA-MM-DD-reflections.md`. Se houver duas reuniões no mesmo dia, `discussion/checkpoint-AAAA-MM-DD-<slug>-reflections.md` (espelhando o slug do checkpoint).
- `AAAA-MM-DD` = data da reunião, não a data em que a skill roda.

## Idempotência / re-execução

- Se o checkpoint alvo **já existe**: não sobrescreva em silêncio. Pergunte se é para regenerar (o factual pode ser regenerado a partir da fonte) ou se a fonte é uma versão nova da transcrição.
- As reflexões são derivadas e regeneráveis; as edições datadas em doc canônico **não** — se a skill já rodou para essa reunião, não duplique as notas `**Update DD/MM…**`. Cheque `git log --oneline -- discussion/open-questions.md` e o próprio conteúdo antes de anexar.
- A camada factual (checkpoints) e o log episódico do diário **nunca** são reescritos por esta skill.

## Casos de borda

- **Transcrição parcial / rótulos de fala trocados:** registre no cabeçalho do checkpoint; onde a atribuição afeta o sentido, sinalize no ponto ("em um trecho a fala sobre X aparece rotulada de forma inconsistente"). Não invente quem disse o quê.
- **Screen-share não capturado:** trate conteúdo visual como possivelmente ausente do texto; peça o artefato (repo, screenshot) em vez de concluir que não existiu — precedente registrado em `checkpoint-2026-08-21-infra-reflections.md#3`.
- **Reunião sem nada novo para a arquitetura:** grave o checkpoint factual mesmo assim; as reflexões podem ser curtas e nenhum doc canônico precisa ser editado — diga isso explicitamente no report.
- **`pandoc` indisponível:** tente `python3` + `python-docx`; se nenhum, peça ao Rafael para converter a fonte e apontar o `.md`/`.txt`.
- **Meeting-prep com checklist:** confronte cada pergunta com o que a reunião respondeu; marque só as que foram de fato respondidas, com data e onde ficou registrado.

## Diário de campo — não é tarefa desta skill

O passo 4 do meeting-record pattern ("close the loop in the research diary") **fica de fora** desta skill por decisão do projeto: o diário só é tocado quando o Rafael pede explicitamente (regra do `CLAUDE.md` e gatilhos da skill `diario-campo`). A skill deve **lembrar** no report que esse fechamento está pendente e que quem faz é a `diario-campo`.

## Git

Não faça commit nem push automaticamente. Ao terminar, liste os arquivos criados/alterados e sugira o commit. Antes de qualquer push, siga a checagem de merge da branch descrita no `CLAUDE.md` (`git fetch origin main` + `git merge-base --is-ancestor HEAD origin/main`).

## Exemplos

**Exemplo 1 — fluxo completo:**
> `processa o checkpoint da reunião de 28/08 em docs/sources/Checkpoint_Tutor_08-28-26.docx`

→ Extrai o `.docx` (nota: ~42 de 53 min capturados). Grava `docs/checkpoints/checkpoint-2026-08-28-tutor.md` (PT, factual). Triangula contra a hipótese de arquitetura, `open-questions.md`, `scope-and-terminology-decisions.md`, `work-plan.md` e os checkpoints anteriores. Escreve `discussion/checkpoint-2026-08-28-reflections.md` (EN). Anexa notas datadas aos itens afetados de `open-questions.md`, aos componentes afetados da arquitetura e à decisão de escopo reforçada; adiciona a linha nos dois índices. **Apresenta tudo e pede aprovação** antes de fechar. Reporta `git status`, lembra do diário pendente e de que não houve commit.

**Exemplo 2 — só o factual, rápido:**
> `só gera o checkpoint dessa transcrição, as reflexões eu vejo depois`

→ Passos 0–2 + 8. Grava só `docs/checkpoints/checkpoint-AAAA-MM-DD-<slug>.md` e a linha em `docs/README.md`. Não escreve reflexões nem edita docs canônicos. Diz no report o que ficou por fazer.

**Exemplo 3 — pré-aprovado:**
> `processa a reunião de infra e aplica tudo direto, não precisa perguntar`

→ Fluxo completo, grava os cinco tipos de artefato, e **depois** reporta o que foi feito em vez de pedir OK.

## Referências

Caminhos relativos à raiz do repo, exceto o último (relativo a esta skill).

- `docs/README.md` — "Meeting-record pattern" (a fonte de verdade deste fluxo) e a nota de idioma.
- `discussion/README.md` — quando algo é nota de `discussion/` vs. fica no `Reflexão` do diário; idioma padrão inglês.
- `docs/checkpoints/checkpoint-2026-08-21-infra-arquitetura.md` + `discussion/checkpoint-2026-08-21-infra-reflections.md` — o registro de infra, cross-check obrigatório do passo 3 (o que é infra viva vs. proposta).
- `docs/checkpoints/checkpoint-2026-08-28-tutor.md` + `discussion/checkpoint-2026-08-28-reflections.md` — par de referência mais recente (checkpoint factual + reflexões).
- `discussion/open-questions.md` — formato dos itens e das notas `**Update DD/MM/AAAA…**`.
- `../diario-campo/SKILL.md` — quem fecha o loop no diário e faz o export `.docx` do coordenador.
