---
name: sintese-diario
description: "Sumariza e consolida o diário de campo de pesquisa de Rafael Coelho Ventura (projeto Inova Talentos / IPT Open Nº 1335844346). Faz duas coisas numa passada: (1) lê o arquivo semanal mais recente em research-diary/ (o diario_campo_AAAA-MM-DD.md de data mais alta), destila TODOS os registros episódicos dele e (re)gera o bloco 'Síntese da Semana' no final desse mesmo arquivo; (2) cria a pasta research-diary/summarization/ se não existir e (re)gera research-diary/summarization/sintese_AAAA-MM.md — um resumo mensal único que consolida as sínteses semanais de todas as semanas daquele mês. Use SEMPRE que a mensagem for '/sintese-diario', 'sumariza meu diário', 'sumariza o diário de campo', 'roda a sumarização do diário', 'gera o resumo mensal do diário', 'consolida as sínteses semanais do mês', 'atualiza a síntese mensal do diário', ou pedido equivalente de fechar/consolidar o diário num resumo. Aceita um mês alvo opcional ('sumariza o diário de agosto', '/sintese-diario 2026-08'). NÃO use para registrar uma entrada nova nem para ver o status do diário — isso é a skill diario-campo — nem quando Rafael só menciona de passagem ter lido/testado algo sem pedir a sumarização."
---

# Síntese do Diário de Campo — camada semântica semanal + resumo mensal

## O que esta skill faz (e o que não faz)

Esta skill é a operação de **sumarização em lote** do diário. Ela produz duas saídas numa passada:

1. **(Re)gera a `## Síntese da Semana` no final do arquivo semanal mais recente** (`research-diary/diario_campo_AAAA-MM-DD.md` de data mais alta), destilando todos os registros episódicos daquele arquivo.
2. **(Re)gera o resumo mensal** em `research-diary/summarization/sintese_AAAA-MM.md` (a pasta é criada se não existir), consolidando as sínteses semanais de todas as semanas cujo *Monday* cai naquele mês.

Divisão de trabalho com a skill **`diario-campo`**:

| Ação | Skill |
|---|---|
| Registrar uma entrada nova / corrigir uma entrada | `diario-campo` |
| Ver o status do mês (contagens, últimas sínteses) sem escrever | `diario-campo` |
| Export `.docx` limpo para o coordenador | `diario-campo` (fechamento mensal) |
| **(Re)gerar a síntese semanal sob demanda + resumo mensal em Markdown** | **`sintese-diario` (esta)** |

Nunca reescreva registros episódicos (o `Registro objetivo`, `Reflexão`, `Decisão/próximo passo`, `Tags` de uma entrada `##`/`###` de data). A camada episódica é imutável; só a camada semântica (as sínteses) é derivada e regenerável.

## Por que este design (contexto que não pode se perder)

O diário tem duas camadas por decisão de projeto: **episódica** (entradas diárias, baratas de escrever, nunca resumidas no lugar) e **semântica** (síntese destilada, mais cara, maior valor de releitura, regenerável se o entendimento mudar). Esta skill opera só na camada semântica e acrescenta um **segundo nível** dela: o resumo mensal é uma síntese das sínteses semanais. É a mesma separação episódico/semântico que o Plano de Trabalho propõe para o mecanismo de memória do agente (Sub 2.2), aplicada à prática de pesquisa do bolsista — por isso o resumo mensal em Markdown vive no repo (barato, versionado, regenerável) e **não substitui** nem o log episódico (fica nos arquivos semanais) nem o export `.docx` para o coordenador (continua sendo tarefa da skill `diario-campo`).

## Fluxo obrigatório

Use as ferramentas de arquivo (Glob / Read / Write / Edit) — não faça isso por manipulação de shell.

### 1. Descobrir o arquivo semanal mais recente

- `Glob` em `research-diary/diario_campo_*.md`.
- Considere **arquivo semanal** só o que casa `diario_campo_AAAA-MM-DD.md` (três componentes de data). O arquivo legado `diario_campo_AAAA-MM.md` (dois componentes) **não** é semanal — não entra nesta etapa (mas pode entrar na etapa 4).
- A data no nome do arquivo é a **segunda-feira** que abre a semana. Escolha o arquivo de data mais alta.
- Se não existir nenhum arquivo semanal, avise Rafael e pare — provavelmente o diário ainda está no formato mensal legado.

### 2. (Re)gerar a `## Síntese da Semana` no final desse arquivo

- `Read` o arquivo inteiro. Extraia o intervalo da semana do cabeçalho `## Semana de DD/MM a DD/MM/AAAA` (linha ~3). Se faltar, derive: segunda do nome do arquivo + 6 dias.
- Releia **todos** os registros episódicos do arquivo (blocos `##` de data e `###` de sub-entrada). Destile — não concatene os `Registro objetivo` um atrás do outro.
- Monte o bloco no [formato exato abaixo](#formato--síntese-da-semana).
- Se o arquivo **já termina** com um `## Síntese da Semana — ...`, substitua esse bloco inteiro pelo novo (a semântica é regenerável). Se houver conteúdo depois do bloco de síntese, **pare e pergunte** — não sobrescreva às cegas.
- Se o arquivo **não tem** síntese ainda, anexe o bloco novo ao final, precedido de uma linha em branco.
- Se o arquivo semanal não tiver **nenhum** registro episódico, não escreva síntese vazia — avise Rafael.

### 3. Determinar o mês alvo e as semanas dele

- **Mês alvo padrão:** o mês da segunda-feira do arquivo semanal mais recente.
- Se Rafael passou um mês explícito (`2026-08`, `agosto`, `mês passado`), use esse.
- Se o arquivo mais recente **abre um mês novo** (a segunda dele caiu num mês diferente do arquivo anterior) **e** o resumo do mês anterior não existe ou está desatualizado, gere/atualize os **dois** meses (o que fechou e o corrente).
- **Semanas que pertencem ao mês:** toda semana cuja **segunda-feira** cai naquele mês (uma semana que cruza a virada de mês conta para o mês que contém a segunda dela). Fontes:
  - cada `diario_campo_AAAA-MM-DD.md` cuja data (segunda) está no mês alvo;
  - o arquivo legado `diario_campo_AAAA-MM.md` do mês alvo, se existir: extraia dele cada bloco `## Síntese da Semana — DD/MM a DD/MM/AAAA` (a data inicial do intervalo é a segunda daquela semana).
- Semanas sem nenhum registro episódico não entram no resumo.

### 4. Garantir a pasta `research-diary/summarization/`

- Se não existir, crie-a ao escrever o primeiro arquivo dentro dela (o `Write` cria o diretório).

### 5. (Re)gerar `research-diary/summarization/sintese_AAAA-MM.md`

- Para **cada** semana do mês alvo, garanta que a síntese semanal existe:
  - a semana do arquivo mais recente já foi (re)gerada na etapa 2;
  - para semanas **anteriores** do mesmo mês cujo arquivo semanal **não tem** síntese, gere a síntese daquele arquivo agora (mesmo formato da etapa 2) e grave-a no final daquele arquivo;
  - **não** reescreva uma síntese semanal anterior que já existe, a menos que Rafael peça explicitamente ("regenera todas as semanas").
- Monte o arquivo mensal no [formato abaixo](#formato--resumo-mensal): cabeçalho + **Resumo do mês** (destilação cruzando todas as semanas) + as sínteses semanais do mês copiadas na íntegra, em ordem cronológica.
- Se o arquivo mensal já existir, regenere-o por completo a partir do estado atual das sínteses semanais. Atualize sempre o campo **Última regeneração** para a data de hoje.
- O resumo mensal **não** duplica o log episódico completo — ele para na camada semântica. O detalhe episódico fica nos arquivos semanais e no export `.docx`.

### 6. Manter o `research-diary/README.md` coerente

- O `README.md` normalmente já descreve a pasta `summarization/` (seção "Second semantic layer" + item em "Files"). Se por algum motivo não descrever, acrescente uma subseção curta e o item na lista — não reescreva o resto do README.

### 7. Verificar e reportar

- `Read` o final do arquivo semanal e o arquivo mensal recém-escritos para conferir a estrutura.
- Reporte a Rafael, sem escrever num arquivo: qual arquivo semanal teve a síntese (re)gerada, qual(is) arquivo(s) mensal(is) foi(ram) escrito(s), semanas cobertas, contagem de registros, e o lembrete de que a skill **não** fez commit e **não** gerou o `.docx` do coordenador.

## Formato — Síntese da Semana

Use exatamente este bloco (mesmo padrão já usado nos arquivos do diário — não invente estrutura nova):

```markdown
## Síntese da Semana — DD/MM a DD/MM/AAAA

**Achados centrais:** {destilação das entradas de leitura/achado/teste da semana — o que de fato se aprendeu, a linha de raciocínio, não uma lista das entradas}

**Decisões tomadas:** {decisões registradas na semana, ou "nenhuma decisão formal esta semana"}

**Itens em aberto:** {o que ficou pendente, cruzando com pendências do Plano quando relevante}
```

## Formato — resumo mensal

Arquivo `research-diary/summarization/sintese_AAAA-MM.md`:

```markdown
# Síntese Mensal do Diário de Campo — {Mês} de {Ano}

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Segunda camada semântica: consolida as sínteses semanais de {mês}/{ano} num resumo mensal único. Derivado dos arquivos semanais em `../diario_campo_*.md` — regenerável a qualquer momento. Não duplica o log episódico nem substitui o export .docx para o coordenador.*

- **Semanas cobertas:** {DD/MM–DD/MM}, {DD/MM–DD/MM}, ...
- **Registros episódicos no mês:** {n}
- **Distribuição por sub-atividade:** {ex.: 1.1 ×4 · 1.6 ×3 · 2.2 ×3 · transversal ×1}
- **Última regeneração:** {DD/MM/AAAA}

---

## Resumo do mês

**Achados centrais do mês:** {destilação cruzando todas as semanas — a evolução do mês como uma narrativa curta, não a concatenação das sínteses semanais}

**Decisões tomadas no mês:** {lista consolidada; cada item com a data em que foi decidido; agrupe decisões relacionadas}

**Itens em aberto ao fim do mês:** {itens em aberto de todas as semanas, menos os que uma semana posterior fechou; marque os que se arrastam há mais de uma semana}

---

## Sínteses semanais do mês

### Semana de DD/MM a DD/MM/AAAA

{bloco "Síntese da Semana" dessa semana, copiado na íntegra — Achados centrais / Decisões tomadas / Itens em aberto}

### Semana de DD/MM a DD/MM/AAAA

{...}
```

## Regras de regeneração / idempotência

- Rodar a skill duas vezes seguidas deve ser seguro: a síntese semanal do arquivo mais recente é sempre substituída; o arquivo mensal é sempre regenerado por inteiro.
- Sínteses semanais de semanas **anteriores** que já existem não são tocadas por padrão — só quando Rafael pede "regenera todas as semanas".
- A camada episódica nunca é alterada.
- O arquivo legado `diario_campo_AAAA-MM.md` nunca é reescrito — dele só se **lê** as sínteses semanais já embutidas.

## Casos de borda

- **Semana ainda em curso:** se hoje não é o fim da semana do arquivo mais recente e Rafael não pediu explicitamente, avise que a síntese será uma "parcial" e confirme antes de gravar — a síntese semanal "de verdade" costuma ser gerada quando a semana fecha (via `diario-campo`).
- **Mês sem nenhum registro:** não crie `sintese_AAAA-MM.md` vazio — avise Rafael.
- **Cabeçalho de semana ausente/errado no arquivo:** derive o intervalo da segunda do nome do arquivo + 6 dias e sinalize a divergência no relatório final.
- **Conteúdo após o bloco de síntese no arquivo semanal:** pare e pergunte, não sobrescreva.
- **Sub-atividade de uma entrada com múltiplos valores** (ex.: `1.6 / 2.2`): conte em todas na distribuição.

## Git

Não faça commit nem push automaticamente. Ao terminar, liste os arquivos alterados/criados e sugira o commit. Se for pushar depois, siga a checagem de merge da branch descrita em `CLAUDE.md` antes.

## Exemplos

**Exemplo 1 — sumarização completa:**
> `/sintese-diario`

→ Acha `diario_campo_2026-08-24.md` (mais recente). (Re)gera a `## Síntese da Semana — 24/08 a 30/08/2026` no final dele a partir dos registros da semana. Mês alvo = agosto/2026. Semanas de agosto: 17–23/08 (síntese lida do arquivo legado `diario_campo_2026-08.md`) + 24–30/08 (recém-gerada). Cria `research-diary/summarization/` e escreve `sintese_2026-08.md` com o Resumo do mês + as duas sínteses semanais na íntegra. Reporta contagens e lembra que não fez commit nem `.docx`.

**Exemplo 2 — mês explícito:**
> `sumariza o diário de agosto`

→ Mesmo fluxo, mas mês alvo fixado em agosto/2026 mesmo que o arquivo mais recente já seja de setembro. Regenera as sínteses semanais que faltarem em agosto (sem tocar nas que já existem) e reescreve `sintese_2026-08.md`.

**Exemplo 3 — virada de mês:**
> `/sintese-diario` rodado em 02/09 com `diario_campo_2026-09-01.md` como mais recente

→ Detecta que o arquivo abre setembro e que `sintese_2026-08.md` está desatualizado (falta a semana 31/08–06/09, cuja segunda é agosto). Regenera `sintese_2026-08.md` (fechando agosto) **e** cria/atualiza `sintese_2026-09.md`.

## Referências

- `../diario-campo/SKILL.md` — skill de registro/exportação do diário; esquema dos campos, lógica original da síntese semanal, fechamento mensal `.docx`.
- `../diario-campo/references/sub_atividades.md` — mapa de sub-atividades, usado para a linha "Distribuição por sub-atividade" do resumo mensal.
- `../../research-diary/README.md` — convenção de arquivos do diário (semanal vs. legado mensal), regra "semana conta para o mês da sua segunda-feira", camadas episódica/semântica.
