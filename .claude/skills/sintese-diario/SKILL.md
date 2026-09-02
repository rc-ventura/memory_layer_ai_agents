---
name: sintese-diario
description: "Sumariza o diário de campo de pesquisa de Rafael Coelho Ventura (projeto Inova Talentos / IPT Open Nº 1335844346). (Re)gera research-diary/summarization/<Mês>/sintese_AAAA-MM.md (pasta de mês em abreviação PT, ex.: summarization/Ago/sintese_2026-08.md) — um digest mensal com ATÉ 4 registros, um por semana, cada um a reflexão daquela semana (tirada das entradas episódicas do arquivo semanal research-diary/<Mês>/diario_campo_AAAA-MM-DD.md, ou do bloco de síntese embutido no arquivo legado research-diary/<Mês>/diario_campo_AAAA-MM.md) organizada num parágrafo curto + 'Decidido:' + 'Em aberto:'. NÃO escreve nada dentro dos arquivos semanais — eles são só episódicos. Cria a pasta research-diary/summarization/<Mês>/ se não existir. Use SEMPRE que a mensagem for '/sintese-diario', 'sumariza meu diário', 'sumariza o diário de campo', 'roda a sumarização do diário', 'gera o resumo mensal do diário', 'gera o digest mensal do diário', 'atualiza a síntese mensal do diário', ou pedido equivalente de consolidar o diário num resumo. Aceita um mês alvo opcional ('sumariza o diário de agosto', '/sintese-diario 2026-08'). NÃO use para registrar uma entrada nova nem para ver o status do diário — isso é a skill diario-campo — nem quando Rafael só menciona de passagem ter lido/testado algo sem pedir a sumarização."
---

# Síntese do Diário de Campo — digest mensal (camada semântica)

## O que esta skill faz (e o que não faz)

Esta skill (re)gera **um arquivo por mês**: `research-diary/summarization/<Mês>/sintese_AAAA-MM.md` (pasta de mês em abreviação PT de 3 letras, title case — `Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez`; ex.: `research-diary/summarization/Ago/sintese_2026-08.md`), um digest com **até 4 registros — um por semana**. Cada registro é a reflexão daquela semana, tirada das entradas episódicas da semana e só **organizada** aqui (a interpretação já foi feita nas próprias entradas). É a camada semântica do diário: curta, para releitura rápida semana a semana.

**Esta skill NÃO escreve nada dentro dos arquivos semanais** `research-diary/<Mês>/diario_campo_AAAA-MM-DD.md` — eles são só episódicos. A síntese de cada semana vive só no digest mensal.

Divisão de trabalho com a skill **`diario-campo`**:

| Ação | Skill |
|---|---|
| Registrar uma entrada nova / corrigir uma entrada | `diario-campo` |
| Ver o status do mês (contagens, últimos registros) sem escrever | `diario-campo` |
| Export `.docx` limpo para o coordenador | `diario-campo` (fechamento mensal) |
| **(Re)gerar o digest mensal (`summarization/`)** | **`sintese-diario` (esta)** |

Nunca reescreva registros episódicos (o `Registro objetivo`, `Reflexão`, `Decisão/próximo passo`, `Tags` de uma entrada `##`/`###` de data). A camada episódica é imutável; só o digest mensal é derivado e regenerável.

## Por que este design (contexto que não pode se perder)

O diário tem duas camadas por decisão de projeto: **episódica** (entradas diárias nos arquivos semanais, baratas de escrever, nunca resumidas no lugar) e **semântica** (o digest mensal, destilado, maior valor de releitura, regenerável se o entendimento mudar). É a mesma separação episódico/semântico que o Plano de Trabalho propõe para o mecanismo de memória do agente (Sub 2.2), aplicada à prática de pesquisa do bolsista — por isso o digest mensal em Markdown vive no repo (barato, versionado, regenerável) e **não substitui** nem o log episódico (fica nos arquivos semanais) nem o export `.docx` para o coordenador (continua sendo tarefa da skill `diario-campo`).

## Fluxo obrigatório

Use as ferramentas de arquivo (Glob / Read / Write / Edit) — não faça isso por manipulação de shell.

### 1. Determinar o mês alvo

- **Mês alvo padrão:** o mês a que **pertence** (pela [regra da quarta-feira](#2-listar-as-semanas-do-mês)) a semana do arquivo semanal `diario_campo_AAAA-MM-DD.md` de data mais alta (`Glob` recursivo em `research-diary/**/diario_campo_*.md` — os arquivos ficam nas pastas de mês; considere semanal só o que casa três componentes de data). Atenção: o mês alvo pode não ser o `MM` do nome do arquivo (ex.: `Set/diario_campo_2026-08-31.md` → alvo setembro).
- Se Rafael passou um mês explícito (`2026-08`, `agosto`, `mês passado`), use esse.
- Se o arquivo mais recente **abre um mês novo** (a semana dele pertence, pela regra da quarta-feira, a um mês diferente do arquivo de data imediatamente anterior) **e** o digest do mês anterior não existe ou está desatualizado, gere/atualize os **dois** meses (o que fechou e o corrente).
- Se não existir nenhum arquivo semanal nem legado, avise Rafael e pare.

### 2. Listar as semanas do mês

- **Uma semana pertence ao mês que contém a sua quarta-feira** — o mesmo que "o mês com a maioria dos 5 dias úteis da semana". Uma semana que cruza a virada de mês conta para o mês que tem ≥3 dos dias dela; o `MM` do nome do arquivo pode não bater com a pasta/mês (ex.: `Set/diario_campo_2026-08-31.md` conta para setembro).
- Semana = **segunda a sexta-feira** (5 dias úteis).
- Fonte de cada semana (arquivos em `research-diary/<Mês>/`):
  - `diario_campo_AAAA-MM-DD.md` cuja semana pertence ao mês alvo pela regra da quarta-feira → a reflexão da semana vem das entradas episódicas desse arquivo;
  - o arquivo legado `research-diary/<Mês>/diario_campo_AAAA-MM.md` do mês, se existir → a reflexão de cada semana vem do bloco `## Síntese da Semana — DD/MM a DD/MM/AAAA` já embutido nele (a data inicial do intervalo é a segunda daquela semana). O arquivo legado **nunca é reescrito** — só lido.
- Semanas sem nenhum registro episódico não entram no digest.
- Num mês normal sobram **no máximo 4 semanas**. Se um mês tiver 5 semanas com registro, mantenha as 4 com mais conteúdo e sinalize no relatório final que uma ficou de fora (ou pergunte a Rafael qual unir).

### 3. Montar cada registro semanal

Para cada semana, produza **um** registro no [formato abaixo](#formato--digest-mensal):

```markdown
### Semana N · DD–DD/MM/AAAA · N registros

{parágrafo curto: o que aconteceu na semana — a linha de raciocínio, não uma lista das entradas}

**Decidido:** {decisões da semana; "nenhuma decisão formal esta semana" se for o caso}

**Em aberto:** {pendências da semana; marque as que vêm de uma semana anterior com "arrasta da semana X"}
```

- `N` da semana = ordinal cronológico entre as semanas **atribuídas ao mês** (pela regra da quarta-feira), 1ª, 2ª… — não o número da segunda-feira dentro do mês. Uma semana cuja segunda cai no mês anterior mas que pertence a este mês (ex.: 31/08–04/09 → setembro) pode ser a Semana 1.
- `N registros` = contagem de blocos `##`/`###` episódicos daquela semana (no arquivo legado, conte as entradas do intervalo).
- **Organize, não reinterprete** — a reflexão já foi feita nas entradas (campos `Reflexão` / `Decisão`); aqui é destilação/arrumação, não análise nova.
- Mantenha **curto** — o digest existe para leitura rápida.
- **Atribuição de agente:** se a semana teve trabalho feito por um agente de IA e não pelo Rafael (leitura de papers, sprint, etc.), escreva de forma **genérica** — "um agente (sem provider definido)", "leitura por agente, não pelo Rafael" — nunca nomeie assistente / modelo / provider. Mesma convenção do `research-diary/README.md` e da skill `diario-campo`.

### 4. Escrever `research-diary/summarization/<Mês>/sintese_AAAA-MM.md`

- A pasta `summarization/<Mês>/` é criada pelo `Write` se não existir (`<Mês>` = abreviação PT de 3 letras do mês alvo, ex.: `Set`).
- Estrutura: cabeçalho curto + **Última regeneração** + os registros semanais em ordem cronológica, separados por `---`.
- Se o arquivo já existir, **regenere-o por inteiro** a partir do estado atual das entradas. Atualize **Última regeneração** para a data de hoje.
- O digest **não** duplica o log episódico — ele para na camada semântica.

### 5. Manter os índices coerentes (`research-diary/README.md` + `CLAUDE.md` / `AGENTS.md`)

- **`research-diary/README.md`** já descreve a hierarquia de pastas de mês, a regra da quarta-feira e a pasta `summarization/<Mês>/` (seções "Month folders" + "The monthly digest" + item em "Files"). Se por algum motivo não descrever, acrescente uma subseção curta e o item — não reescreva o resto do README.
- **Índice do projeto:** confira o `CLAUDE.md` na raiz do repo (ou `AGENTS.md`, se o repo usar esse nome). Ele deve ter um ponteiro para o diário que aponte para `research-diary/README.md`. Esse arquivo é um índice, não um rulebook — mudança de convenção vai no doc, não nele. Só edite o `CLAUDE.md` / `AGENTS.md` se o ponteiro do diário estiver faltando, quebrado ou apontando para o lugar errado, e aí conserte apenas essa linha.

### 6. Verificar e reportar

- `Read` o arquivo recém-escrito para conferir a estrutura.
- Reporte a Rafael, sem escrever num arquivo: qual digest mensal foi escrito, semanas cobertas, contagem de registros por semana, e o lembrete de que a skill **não** fez commit e **não** gerou o `.docx` do coordenador.

## Formato — digest mensal

Arquivo `research-diary/summarization/<Mês>/sintese_AAAA-MM.md`:

```markdown
# Síntese Mensal do Diário — {Mês} de {Ano}

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Leitura rápida do mês, semana a semana. Até 4 registros — a reflexão de cada semana, tirada dos arquivos episódicos em `../../<Mês>/diario_campo_*.md` e apenas organizada aqui. Regenerável. Não duplica o log episódico nem substitui o export `.docx` do coordenador.*

- **Última regeneração:** {DD/MM/AAAA}

---

### Semana 1 · DD–DD/MM/AAAA · N registros

{parágrafo curto}

**Decidido:** {...}

**Em aberto:** {...}

---

### Semana 2 · DD–DD/MM/AAAA · N registros

{...}
```

## Regras de regeneração / idempotência

- Rodar a skill duas vezes seguidas é seguro: o digest mensal é sempre regenerado por inteiro.
- A camada episódica (os arquivos semanais) **nunca** é alterada por esta skill.
- O arquivo legado `research-diary/<Mês>/diario_campo_AAAA-MM.md` nunca é reescrito — dele só se **lê** as sínteses semanais já embutidas.
- Regenerar um registro semanal a partir das entradas é o padrão; se Rafael quiser preservar uma redação anterior de alguma semana, ele avisa.

## Casos de borda

- **Semana ainda em curso:** a semana fecha na **sexta-feira** (5 dias úteis). Se hoje cai de segunda a quinta da semana mais recente e Rafael não pediu explicitamente, avise que o registro daquela semana será **parcial** e confirme antes de gravar. Da sexta-feira em diante (inclusive sábado/domingo) a semana está fechada — registro normal.
- **Mês sem nenhum registro:** não crie `sintese_AAAA-MM.md` vazio — avise Rafael.
- **Mês com 5 semanas com registro:** mantenha as 4 com mais conteúdo, sinalize no relatório (ou pergunte qual unir).
- **Cabeçalho de semana ausente/errado no arquivo semanal:** derive o intervalo da segunda do nome do arquivo + 4 dias (segunda a sexta) e sinalize a divergência no relatório final.
- **Entrada de sábado/domingo:** conta para a semana que fechou na sexta anterior.
- **Semana que cruza a virada de mês:** pertence ao mês da **quarta-feira** dela (maioria dos dias úteis). O arquivo pode estar numa pasta de mês cujo nome não bate com o `AAAA-MM` do nome do arquivo — ex.: `research-diary/Set/diario_campo_2026-08-31.md` conta para setembro, entra em `summarization/Set/sintese_2026-09.md`, e o `Glob` recursivo é o que garante que ele seja encontrado.

## Git

Não faça commit nem push automaticamente. Ao terminar, liste os arquivos criados/alterados e sugira o commit. Se for pushar depois, siga a checagem de merge da branch descrita em `CLAUDE.md` antes.

## Exemplos

**Exemplo 1 — digest do mês corrente:**
> `/sintese-diario`

→ Arquivo semanal de data mais alta = `research-diary/Ago/diario_campo_2026-08-24.md` (semana 24–28/08, quarta 26/08 → agosto) → mês alvo agosto/2026. Semanas de agosto com registro: 17–23/08 (reflexão lida do bloco `## Síntese da Semana` já embutido no arquivo legado `research-diary/Ago/diario_campo_2026-08.md`) e 24–28/08 (reflexão destilada das entradas episódicas do arquivo semanal). Cria `research-diary/summarization/Ago/` e escreve `sintese_2026-08.md` com 2 registros (Semana 1 e Semana 2), cada um parágrafo + Decidido + Em aberto. **Não toca** nos arquivos semanais. Reporta e lembra que não fez commit nem `.docx`.

**Exemplo 2 — mês explícito:**
> `sumariza o diário de agosto`

→ Mesmo fluxo, mês fixado em agosto/2026 mesmo que o arquivo mais recente já pertença a setembro. Regenera `research-diary/summarization/Ago/sintese_2026-08.md` por inteiro.

**Exemplo 3 — virada de mês (regra da quarta-feira):**
> `/sintese-diario` rodado em 02/09 com `research-diary/Set/diario_campo_2026-08-31.md` como arquivo mais recente

→ A semana 31/08–04/09 pertence a **setembro** (quarta em 02/09), apesar do `2026-08` no nome e de a segunda cair em agosto. O arquivo de data imediatamente anterior (`research-diary/Ago/diario_campo_2026-08-24.md`) pertence a agosto → houve virada de mês. Se `summarization/Ago/sintese_2026-08.md` estiver desatualizado, regenera agosto **e** cria/atualiza `summarization/Set/sintese_2026-09.md` — onde a semana 31/08–04/09 entra como **Semana 1** de setembro.

## Referências

- `../diario-campo/SKILL.md` — skill de registro do diário e export `.docx` mensal para o coordenador; esquema dos campos das entradas.
- `../diario-campo/references/sub_atividades.md` — mapa de sub-atividades (usado no `.docx` do coordenador, não no digest).
- `../../research-diary/README.md` — convenção de arquivos (semanal episódico vs. legado mensal), pastas de mês (abreviação PT), **regra da quarta-feira** ("semana conta para o mês que contém a sua quarta-feira"), camadas episódica/semântica.
