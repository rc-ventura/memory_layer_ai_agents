---
name: diario-campo
description: "Registra, organiza e sintetiza o diário de campo pessoal de pesquisa de Rafael Coelho Ventura para o projeto Inova Talentos/IPT Open (Nº 1335844346, mecanismo de atualização de memória para agentes de IA em fluxos jurídicos). Use esta skill SEMPRE que a mensagem começar com 'diário:', 'diario:', 'registro de campo:', 'novo registro:', ou quando o usuário disser explicitamente 'registra isso no diário' / 'guarda isso no meu diário de campo'. Use também quando ele pedir para ver, revisar ou fechar/exportar o diário do mês ('como está meu diário desse mês', 'fecha o diário de agosto', 'exporta o diário pro Luis Felipe'). Para 'gera a síntese da semana' / 'sumariza o diário' / 'gera o digest mensal', a skill é `sintese-diario`, não esta. NÃO use para conversas normais de trabalho onde ele apenas menciona ter lido algo ou testado algo sem pedir explicitamente para registrar — isso evitaria logging não solicitado e ruído no arquivo."
---

# Diário de Campo — memória episódica/semântica pessoal do bolsista

## Por que este design (contexto que não pode se perder)

Este diário é deliberadamente estruturado como uma aplicação em miniatura da própria teoria de memória de agentes que o projeto estuda (Zhang et al., ACM TOIS 2025; Generative Agents/Park et al.): uma camada **episódica** (registros brutos, diários, de baixo custo de escrita) e uma camada **semântica** (sínteses periódicas, destiladas, de maior custo e maior valor de releitura). Não é um adorno — é a mesma separação que o Plano de Trabalho propõe para o mecanismo de memória do agente (Sub 2.2), aplicada à prática de pesquisa do próprio bolsista. Trate as duas camadas como funcionalmente distintas: a episódica nunca deve ser reescrita ou resumida no lugar; a semântica é derivada, e pode ser regenerada se algo mudar de entendimento.

O diário serve três públicos ao mesmo tempo, e cada entrada deve continuar servindo aos três sem edição adicional:
1. Memória de trabalho pessoal do Rafael (não perder nada).
2. Acompanhamento do coordenador do projeto (leitura do arquivo bruto, sem tratamento).
3. Rastreabilidade formal para os Entregáveis do Plano de Trabalho (por isso toda entrada é tageada por sub-atividade — ver `references/sub_atividades.md`).

## Onde o diário vive

O diário fica em `research-diary/`. **Um arquivo por semana:** `diario_campo_AAAA-MM-DD.md`, onde `AAAA-MM-DD` é a **segunda-feira** que abre a semana; a semana do diário vai de **segunda a sexta-feira (5 dias úteis)**. O arquivo legado `research-diary/diario_campo_AAAA-MM.md` (dois componentes de data, um por mês) é da convenção antiga — só de leitura, nunca reescrito.

Cada arquivo semanal contém **só entradas episódicas** — nunca um bloco de síntese. A reflexão destilada de cada semana vive no digest mensal `research-diary/summarization/sintese_AAAA-MM.md`, produzido pela skill `sintese-diario`.

Fluxo em toda interação com esta skill:

1. **Ler o estado atual**: `Glob` em `research-diary/diario_campo_*.md`, pegue o arquivo semanal de data mais alta e `Read` o conteúdo dele — é o estado atual, não recrie do zero.
2. **Anexar a nova entrada** ao final desse arquivo.
3. Se a nova entrada cair numa semana ainda sem arquivo, crie o arquivo novo com o cabeçalho definido abaixo. Não há síntese a escrever no arquivo da semana que fechou — ela entra no digest mensal quando a skill `sintese-diario` roda.

## Gatilhos de acionamento

Acione esta skill quando a mensagem:
- Começar com `diário:`, `diario:`, `registro de campo:` ou `novo registro:` (o texto após os dois-pontos é o conteúdo bruto da entrada).
- For um pedido explícito para registrar algo ("registra isso no diário", "guarda isso no meu diário de campo").
- For um pedido sobre o estado do diário: ver o mês atual, fechar/exportar o mês para o coordenador, ou corrigir uma entrada anterior. (Para gerar/atualizar a síntese semana a semana, a skill é `sintese-diario`.)

Não acione implicitamente. Se Rafael mencionar de passagem que leu um artigo ou fez um teste, sem pedir para registrar, não crie uma entrada — isso geraria ruído e quebraria a expectativa de que só entra no diário o que ele decidiu que vale registrar.

## Esquema da entrada episódica

Toda entrada tem campos obrigatórios e campos opcionais. Preencha o que puder inferir do texto bruto; nunca deixe de preencher os obrigatórios — se não houver informação suficiente, use o valor de fallback indicado.

**Obrigatórios:**
- **Tipo**: uma de `leitura | teste/POC | implementação | reunião | decisão | achado | observação livre`. Infira do verbo/contexto (ex.: "li o paper" → leitura; "testei" → teste/POC; "decidimos" → decisão).
- **Sub-atividade**: consulte `references/sub_atividades.md` e casse pela tabela de sinais. Fallback: `transversal` (gestão/ferramentas) ou `não classificado (confirmar)` se genuinamente incerto.
- **Canal**: `pessoal | informal-coordenador | formal-tutor`. Infira: menções a "coordenador" ou reunião de acompanhamento de escopo → `informal-coordenador`; menções a "Luis Felipe", "tutor", "sign-off", "aprovação formal" → `formal-tutor`; caso contrário → `pessoal`. Este campo existe especificamente para não misturar direção informal do coordenador com validação formal do tutor — uma ambiguidade que já está registrada como pendência do projeto.
- **Registro objetivo**: o fato em si, reescrito de forma clara e sucinta a partir do texto bruto de Rafael — o componente episódico, o que de fato aconteceu.

**Opcionais (inclua só se houver conteúdo real, nunca invente para preencher):**
- **Reflexão**: interpretação subjetiva, hipótese, ressalva.
- **Decisão/próximo passo**: se algo foi decidido ou ficou como próximo passo.
- **Tags**: palavras-chave livres, minúsculas, separadas por vírgula.

### Convenção — atribuição de trabalho feito por agente de IA

Quando a entrada registra que **um agente de IA** fez algo em vez do Rafael — leu um paper, rodou um sprint de leitura, ajudou a desenhar um esquema — refira-se a ele de forma **genérica**: "um agente (sem provider definido)", "leitura por agente, não pelo Rafael". Nunca nomeie o assistente, o modelo ou o provider. O que a nota carrega é a marca de *não é trabalho do próprio Rafael*; qual ferramenta produziu não é o ponto e envelhece o registro. Menção a produtos de IA como **assunto** (nota sobre um sistema, fato de tooling de uma reunião) mantém o nome — a convenção é só sobre atribuir trabalho feito para o diário.

### Formato de saída da entrada

Use exatamente este template (Markdown), como um bloco `##` de data (uma data pode acumular múltiplas entradas no mesmo dia — use `###` para a segunda entrada em diante do mesmo dia):

```markdown
## DD/MM/AAAA

**Tipo:** {tipo} — **Sub-atividade:** {sub} — **Canal:** {canal}

**Registro objetivo:** {texto}

**Reflexão:** {texto ou omitir a linha inteira se vazio}

**Decisão/próximo passo:** {texto ou omitir a linha inteira se vazio}

**Tags:** {tags ou omitir a linha inteira se vazio}
```

Anexe a nova entrada ao final do arquivo semanal corrente, mantendo ordem cronológica.

## Cabeçalho de um arquivo novo (primeira entrada da semana)

`DD/MM` iniciais = a segunda-feira do nome do arquivo; `DD/MM` finais = essa segunda + 4 dias (a sexta-feira que fecha a semana).

```markdown
# Diário de Campo — Rafael Coelho Ventura

## Semana de DD/MM a DD/MM/AAAA

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---
```

## Camada semântica — não é tarefa desta skill

O arquivo semanal é só episódico. A reflexão destilada de cada semana (um registro curto: parágrafo + `**Decidido:**` + `**Em aberto:**`) vive no digest mensal `research-diary/summarization/sintese_AAAA-MM.md`, com até 4 registros por mês — um por semana. Quem gera e regenera esse digest é a skill **`sintese-diario`**. Se Rafael pedir "gera a síntese da semana" / "sumariza o diário", acione `sintese-diario`, não escreva síntese no arquivo semanal.

Uma entrada de sábado ou domingo pertence à semana que fechou na sexta anterior — não abre semana nova.

## Fechamento e exportação mensal (para o coordenador)

Quando (a) a primeira entrada de um novo mês calendário for registrada e o mês anterior ainda não tiver sido exportado, ou (b) Rafael pedir explicitamente para exportar/fechar o diário de um mês:

1. Garanta que o digest mensal `research-diary/summarization/sintese_AAAA-MM.md` está atualizado — rode a skill `sintese-diario` primeiro (ela regenera o digest por inteiro).
2. Use a skill de geração de `.docx` disponível no ambiente antes de gerar o arquivo — não pule esse passo mesmo já tendo feito isso antes na conversa.
3. Monte um `.docx` limpo com esta estrutura:
   - Capa simples: mês/ano, nome do bolsista, número do projeto, contagem de registros do mês.
   - Corpo principal: os registros semanais do digest mensal, em ordem — isto é o que o coordenador deve ler primeiro.
   - Anexo: o log episódico completo do mês (todas as entradas dos arquivos semanais, formato tabela ou lista), para quem quiser o detalhe.
4. Verifique o resultado visualmente (converter para PDF com `soffice` e rasterizar com `pdftoppm`, conforme a skill de `.docx`) antes de apresentar.
5. Apresente o `.docx` com a ferramenta de apresentação de arquivos.
6. Confira que o índice do projeto — `CLAUDE.md` na raiz (ou `AGENTS.md`, se o repo usar esse nome) — ainda tem um ponteiro do diário apontando para `research-diary/README.md`. É um índice, não um rulebook: só edite se o ponteiro estiver faltando ou quebrado, e aí conserte só essa linha.

Nunca gere o export mensal sem que o digest mensal daquele mês esteja atualizado — o export é uma composição dos registros semanais do digest, não uma reformatação do log bruto.

## Exemplos

**Exemplo 1 — captura rápida:**
> `diário: hoje li o Memory-R1 com atenção e testei uma POC bem simples do esquema ADD/UPDATE/DELETE/NOOP em Python, só pra sentir a lógica. Achei o NOOP mais delicado de acertar do que esperava.`

→ Tipo: leitura + teste/POC (pode dividir em duas entradas ou uma só cobrindo ambos, use julgamento — aqui, uma entrada só, Tipo: teste/POC, já que a leitura foi instrumental ao teste). Sub-atividade: 1.3 (RL aplicado à atualização de memória) ou 3.2, dependendo do que a tabela de sinais capturar melhor — prefira 1.3 se ainda estamos na Macroatividade 1. Canal: pessoal. Reflexão: a observação sobre o NOOP.

**Exemplo 2 — pedido de síntese:**
> `gera a síntese da semana` / `sumariza o diário`

→ Não é tarefa desta skill. Acione a skill `sintese-diario`, que regenera o digest mensal `summarization/sintese_AAAA-MM.md`. Esta skill não escreve síntese em arquivo semanal.

**Exemplo 3 — pedido de status:**
> `como está meu diário de agosto até agora?`

→ Não é uma nova entrada. Leia os arquivos semanais das semanas daquele mês e o digest `summarization/sintese_2026-08.md` se existir; resuma o que já foi registrado (contagem por tipo/sub-atividade, últimos registros do digest), sem reescrever nada.

## Referências

- `references/sub_atividades.md` — tabela de macroatividades/sub-atividades do Plano de Trabalho, usada para classificar o campo Sub-atividade. Consulte sempre que for taguear uma entrada.
