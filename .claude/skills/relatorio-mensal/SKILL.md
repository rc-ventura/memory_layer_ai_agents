---
name: relatorio-mensal
description: "Gera o relatório mensal do bolsista Rafael Coelho Ventura para a instituição de fomento ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO]). Lê o formulário mensal que Rafael cola (os campos pedidos), os relatórios anteriores em docs/reports/, o diário do mês e a síntese, o Plano de Trabalho e o git; escreve docs/reports/relatorio-mensal-AAAA-MM.md e a versão em texto puro para colar no formulário. Use SEMPRE que a mensagem for '/relatorio-mensal', 'gera o relatório mensal', 'cria o relatório do mês', 'relatório número N', 'relatório de <mês>', ou quando Rafael colar o texto do formulário mensal da instituição e pedir para preenchê-lo. NÃO use para registrar entrada no diário nem para o export .docx do coordenador (diario-campo), para a síntese do diário (sintese-diario) nem para checkpoints de reunião (checkpoint-reuniao)."
---

# Relatório mensal ao fomento — gerado do diário, conferido contra o formulário

## O que esta skill produz

Um relatório mensal que **responde aos campos que o formulário da instituição pede naquele mês**, no mesmo formato dos relatórios já enviados, com cada afirmação rastreável a uma entrada do diário, a um documento do repo ou ao git:

| Saída | Onde | Para quê |
|---|---|---|
| `relatorio-mensal-AAAA-MM.md` | `docs/reports/` | registro versionado do que foi submetido (os dois campos de texto, com cabeçalho) |
| `relatorio-mensal-AAAA-MM-envio.txt` | `docs/reports/` | os mesmos dois campos em **texto puro**, para colar no formulário (o formulário não renderiza Markdown: negrito e títulos viram texto colado) |
| lista "Para você conferir" | só no chat | o que depende de Rafael (opção do campo de seleção, datas de reunião, afirmações sem prova no diário) |

A skill **não envia** o formulário, **não faz commit** e **não escreve no diário** (a camada episódica é imutável; ver `diario-campo` e `sintese-diario`).

## Por que o formulário vem primeiro

O formulário muda (o de outubro já avisava "novo formato"). Por isso, **em toda execução a skill lê o formulário colado antes de escrever** e só usa `references/formulario.md` como a última versão conhecida, para comparar. Se Rafael não colou o formulário, peça: "cole o texto do formulário deste mês (da tela, com os campos e a tabela de relatórios já criados)". Sem ele, siga com a última versão conhecida e **avise que não foi conferida**.

## Fluxo obrigatório

Use Read / Write / Edit e o Bash só para `git log` e para o script de conversão. Não faça isso por manipulação de shell.

### 1. Ler o formulário e comparar com a última versão

1. Liste os campos do formulário colado: rótulo exato, obrigatório (`*`), tipo (número, texto livre, seleção), a dica entre parênteses, e o formato pedido (ex.: "Mês de Competência — Ex: 03/2023").
2. Compare com `references/formulario.md`. Diga a Rafael o que **mudou** (campo novo, dica nova, campo removido, formato). Campo novo → decida com ele onde entra; atualize `references/formulario.md` no mesmo ato (data da versão incluída).
3. Leia a tabela "Resumo dos relatórios já criados" do formulário, se colada: ela mostra o que a instituição tem registrado de cada mês (inclusive diferenças entre o que está no repo e o que foi enviado).
4. Determine o **número do relatório** (padrão: 1 + o maior número já enviado) e o **mês de competência** no formato pedido (`MM/AAAA`).

### 2. Ler os relatórios anteriores (`docs/reports/relatorio-mensal-*.md`)

Todos, em ordem. Extraia:
- **A janela de cobertura:** do dia seguinte à última atividade relatada até o fim do mês-alvo. A *data de emissão* do relatório anterior pode ser anterior ao fim do mês dele, e a semana que cruza a virada de mês pertence ao mês da quarta-feira (regra do diário): **atividade entre a emissão do anterior e o fim do mês dele ainda não foi relatada** e entra neste relatório, dita como tal.
- **Compromissos e pontos de atenção** do "Observações" e do "Cumprimento do cronograma" anteriores: este relatório tem de dizer o que aconteceu com cada um (cumprido, em andamento, mudou de forma, abandonado e por quê).
- **Estrutura, vocabulário e tamanho** (ver `references/estrutura-e-estilo.md`). Não repita o que um relatório anterior **já explicou** (o método, a taxonomia, a arquitetura): **confira nos anteriores** se foi explicado e, se foi, não redefina. Mas inclua um **adendo curto** (2–4 frases, logo depois da abertura) com **para que serve o trabalho do mês e qual o objetivo final** dele, ligado ao objetivo do Plano; é o que mantém o relatório legível sozinho sem repetir o método (feedback de Rafael, 28/10, sobre o relatório 3, que abria direto nos resultados). Se o método **não** foi explicado antes, explique-o.

### 3. Ler o diário do período

1. Arquivos semanais que cobrem a janela: `Glob` em `research-diary/**/diario_campo_*.md` e escolha pelas **datas das entradas**, não só pela pasta do mês.
2. A síntese `research-diary/summarization/<Mês>/sintese_AAAA-MM.md` serve de **mapa**, não de fonte: ela pode não cobrir a semana de virada nem a semana em curso. Se faltar ou estiver defasada, avise e sugira rodar `/sintese-diario`; não a regenere sem Rafael pedir.
3. Leia as entradas inteiras (Registro objetivo, Reflexão, Decisão/próximo passo, Tags). A **Reflexão** diz o que é hipótese e o que é achado: o relatório herda essa distinção.
4. **Semana sem arquivo** (a em curso, ou a que Rafael não registrou): complete com `git log --since=<data> --date=short --format='%ad %s'`, o roadmap/decisões da análise e `docs/checkpoints/`. Essa parte é **reconstruída**: diga a Rafael exatamente quais trechos vieram do git e não do diário.

### 4. Ler o Plano de Trabalho e o mapa de sub-atividades

`docs/work-plan.md` (prazos por Macroatividade, entregáveis) e `docs/sub-activity-map.md`. Daí saem: quais Macroatividades estão vigentes no mês, o que o Entregável de cada uma exige e **a data formal** do prazo. O mapa registra uma data de trabalho interna diferente da formal (Macroatividade 1: 30/10 formal, 30/11 interna): o relatório usa a **formal** e **não anuncia prorrogação nem compromisso novo** que Rafael não tenha decidido; levante a questão no chat.

### 5. Escrever `docs/reports/relatorio-mensal-AAAA-MM.md`

Siga `references/estrutura-e-estilo.md`. Ordem dos campos = ordem do formulário. Se o arquivo do mês já existe, **pare e pergunte** (é o registro do que foi enviado): ofereça gravar como rascunho em outro nome.

### 6. Gerar o texto puro

```
python3 .claude/skills/relatorio-mensal/scripts/gerar_texto_formulario.py docs/reports/relatorio-mensal-AAAA-MM.md
```

Grava `relatorio-mensal-AAAA-MM-envio.txt` ao lado, com os dois campos em texto puro (título de cada bloco em linha própria, sem Markdown). Leia o resultado e confira que nenhum `**`, `` ` `` ou `#` sobrou.

### 7. Verificar (antes de entregar)

Passe a checklist de `references/estrutura-e-estilo.md` (§ "Verificação") e entregue a Rafael, **no chat**, a lista **Para você conferir**: cada afirmação cuja fonte não é uma entrada do diário, cada reunião cuja ocorrência foi inferida (as com o tutor entram **sem data**), o campo de seleção e o que o texto diz ou deixa de dizer sobre o prazo da Macroatividade.

### 8. Reportar

Diga: quais arquivos foram escritos, a janela coberta, o que mudou no formulário, a lista "Para você conferir", e o lembrete de que **não houve envio nem commit**. Sugira o commit; siga a checagem de merge da branch do `CLAUDE.md` antes de qualquer push.

## Regras que não se negociam

- **Nada sem fonte.** Número, data de reunião, nome de papel ou afirmação de pendência que não esteja no diário, em documento do repo ou no git **não entra**; vai para "Para você conferir".
- **Hipótese continua hipótese.** O relatório não promove a achado o que o diário marca como hipótese, inferência ou "candidata". Memória candidata não é memória validada; número em tokens não é economia.
- **Cronograma honesto.** O "Cumprimento do cronograma" diz o que falta de cada Entregável vigente, mesmo quando a entrega está perto do prazo. Não declare entregue o que o repo mostra como proposta.
- **Anonimização.** Como nos relatórios anteriores: `INTERESSADO` para a empresa, sem nome de tutor, colegas ou clientes, sem identificador de execução, sem dado pessoal; agentes de IA sempre de forma genérica ("um agente", "com apoio de agentes de IA"), nunca nomeando assistente, modelo ou provider; nome de agente jurídico da plataforma só se for indispensável (preferir "um dos agentes jurídicos").
- **Não reescreva relatório enviado.** Os arquivos de meses anteriores são registro; erro neles se corrige em arquivo novo, com Rafael.

## Referências

- `references/formulario.md` — campos do formulário mensal (última versão vista) e como cada um mapeia no arquivo.
- `references/estrutura-e-estilo.md` — estrutura dos relatórios enviados, regras de estilo e a checklist de verificação.
- `../diario-campo/SKILL.md` e `../sintese-diario/SKILL.md` — onde vivem o diário e o digest mensal; regra da quarta-feira.
- `../../../docs/work-plan.md`, `../../../docs/sub-activity-map.md`, `../../../docs/reports/` — plano, mapa de sub-atividades e relatórios enviados.
