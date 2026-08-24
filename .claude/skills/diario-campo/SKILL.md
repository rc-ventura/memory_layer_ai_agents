---
name: diario-campo
description: "Registra, organiza e sintetiza o diário de campo pessoal de pesquisa de Rafael Coelho Ventura para o projeto Inova Talentos/IPT Open (Nº 1335844346, mecanismo de atualização de memória para agentes de IA em fluxos jurídicos). Use esta skill SEMPRE que a mensagem começar com 'diário:', 'diario:', 'registro de campo:', 'novo registro:', ou quando o usuário disser explicitamente 'registra isso no diário' / 'guarda isso no meu diário de campo'. Use também quando ele pedir para ver, revisar, sintetizar ou fechar o diário do mês ('como está meu diário desse mês', 'gera a síntese da semana', 'fecha o diário de agosto', 'exporta o diário pro Luis Felipe'). NÃO use para conversas normais de trabalho onde ele apenas menciona ter lido algo ou testado algo sem pedir explicitamente para registrar — isso evitaria logging não solicitado e ruído no arquivo."
---

# Diário de Campo — memória episódica/semântica pessoal do bolsista

## Por que este design (contexto que não pode se perder)

Este diário é deliberadamente estruturado como uma aplicação em miniatura da própria teoria de memória de agentes que o projeto estuda (Zhang et al., ACM TOIS 2025; Generative Agents/Park et al.): uma camada **episódica** (registros brutos, diários, de baixo custo de escrita) e uma camada **semântica** (sínteses periódicas, destiladas, de maior custo e maior valor de releitura). Não é um adorno — é a mesma separação que o Plano de Trabalho propõe para o mecanismo de memória do agente (Sub 2.2), aplicada à prática de pesquisa do próprio bolsista. Trate as duas camadas como funcionalmente distintas: a episódica nunca deve ser reescrita ou resumida no lugar; a semântica é derivada, e pode ser regenerada se algo mudar de entendimento.

O diário serve três públicos ao mesmo tempo, e cada entrada deve continuar servindo aos três sem edição adicional:
1. Memória de trabalho pessoal do Rafael (não perder nada).
2. Acompanhamento do coordenador do projeto (leitura do arquivo bruto, sem tratamento).
3. Rastreabilidade formal para os Entregáveis do Plano de Trabalho (por isso toda entrada é tageada por sub-atividade — ver `references/sub_atividades.md`).

## Limitação operacional crítica — leia antes de tudo

O ambiente de execução é efêmero: o sistema de arquivos não persiste entre sessões de conversa. O único lugar onde o arquivo do diário sobrevive de uma sessão para a próxima é dentro dos **Project Files** do projeto Claude (os documentos listados no início da conversa, montados em `/mnt/project/`, somente leitura).

Isso implica um fluxo obrigatório em toda interação com esta skill:

1. **Ler o estado atual**: procure nos documentos/arquivos do projeto já disponíveis na conversa um arquivo chamado `diario_campo_<AAAA-MM>.md` para o mês corrente. Se ele aparecer no contexto (como os demais arquivos do projeto), use o conteúdo dele como estado atual — não recrie do zero.
2. **Escrever a versão atualizada** em `/mnt/user-data/outputs/diario_campo_<AAAA-MM>.md`.
3. **Apresentar o arquivo** com a ferramenta de apresentação de arquivos.
4. **Sempre terminar a resposta lembrando Rafael** (em uma linha, sem alarde) de que ele precisa baixar e reenviar esse arquivo para os Project Files do projeto, substituindo a versão antiga, para que a próxima sessão continue de onde esta parou. Nunca omita esse lembrete — é o único jeito de o diário não perder dados entre sessões.

Se o arquivo do mês corrente não existir em nenhum documento do projeto (nem como versão antiga), assuma que é a primeira entrada do mês e crie o arquivo do zero com o cabeçalho definido abaixo.

## Gatilhos de acionamento

Acione esta skill quando a mensagem:
- Começar com `diário:`, `diario:`, `registro de campo:` ou `novo registro:` (o texto após os dois-pontos é o conteúdo bruto da entrada).
- For um pedido explícito para registrar algo ("registra isso no diário", "guarda isso no meu diário de campo").
- For um pedido sobre o estado do diário: ver o mês atual, gerar a síntese da semana, fechar/exportar o mês, ou corrigir uma entrada anterior.

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

Anexe a nova entrada ao final do arquivo do mês corrente, mantendo ordem cronológica.

## Cabeçalho de um arquivo novo (primeira entrada do mês)

```markdown
# Diário de Campo — Rafael Coelho Ventura

## {Mês} de {Ano}

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias) + camada semântica (síntese semanal, toda vez que uma semana se encerra). Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---
```

## Síntese semanal (camada semântica) — automática, sem precisar ser pedida

Sempre que processar uma nova entrada, verifique a data dela contra a última síntese semanal já registrada no arquivo (procure o `## Síntese da Semana` mais recente). Se a nova entrada cair numa semana (segunda a domingo) diferente da última síntese, e essa semana anterior já tiver ao menos uma entrada episódica sem síntese, gere a síntese daquela semana ANTES de processar a nova entrada, e insira-a no ponto correto (depois da última entrada daquela semana, antes da primeira entrada da semana seguinte).

Não espere Rafael pedir — isso é o comportamento padrão. Se ele pedir explicitamente para gerar a síntese de uma semana específica fora dessa lógica automática, atenda também.

Formato da síntese (mesmo padrão já usado em `Achados_Sessao_Pesquisa`, não invente uma estrutura nova):

```markdown
## Síntese da Semana — DD/MM a DD/MM/AAAA

**Achados centrais:** {síntese das entradas de leitura/teste da semana — o que de fato se aprendeu, não uma lista das entradas}

**Decisões tomadas:** {decisões registradas na semana, ou "nenhuma decisão formal esta semana"}

**Itens em aberto:** {o que ficou pendente, cruzando com a tabela de pendências do Plano se relevante}
```

Escreva a síntese como destilação real — releia as entradas episódicas da semana e sintetize, não copie os "Registro objetivo" um atrás do outro.

## Fechamento e exportação mensal (para o coordenador)

Quando (a) a primeira entrada de um novo mês calendário for registrada e o mês anterior ainda não tiver sido exportado, ou (b) Rafael pedir explicitamente para exportar/fechar o diário de um mês:

1. Garanta que todas as semanas daquele mês têm síntese semanal gerada (gere as que faltarem primeiro).
2. Leia o SKILL.md de docx em `/mnt/skills/public/docx/SKILL.md` antes de gerar o arquivo — não pule esse passo mesmo já tendo feito isso antes na conversa.
3. Monte um `.docx` limpo com esta estrutura:
   - Capa simples: mês/ano, nome do bolsista, número do projeto, contagem de registros do mês.
   - Corpo principal: as sínteses semanais do mês, em ordem — isto é o que o coordenador deve ler primeiro.
   - Anexo: o log episódico completo do mês (todas as entradas, formato tabela ou lista), para quem quiser o detalhe.
4. Verifique o resultado visualmente (converter para PDF com `soffice` e rasterizar com `pdftoppm`, conforme o SKILL.md de docx) antes de apresentar.
5. Apresente o `.docx` com a ferramenta de apresentação de arquivos, junto com o `.md` atualizado.

Nunca gere o export mensal sem que as sínteses semanais daquele mês já existam — o export é uma composição das sínteses, não uma reformatação do log bruto.

## Exemplos

**Exemplo 1 — captura rápida:**
> `diário: hoje li o Memory-R1 com atenção e testei uma POC bem simples do esquema ADD/UPDATE/DELETE/NOOP em Python, só pra sentir a lógica. Achei o NOOP mais delicado de acertar do que esperava.`

→ Tipo: leitura + teste/POC (pode dividir em duas entradas ou uma só cobrindo ambos, use julgamento — aqui, uma entrada só, Tipo: teste/POC, já que a leitura foi instrumental ao teste). Sub-atividade: 1.3 (RL aplicado à atualização de memória) ou 3.2, dependendo do que a tabela de sinais capturar melhor — prefira 1.3 se ainda estamos na Macroatividade 1. Canal: pessoal. Reflexão: a observação sobre o NOOP.

**Exemplo 2 — fechamento de semana implícito:**
Se a entrada de sexta-feira for a última da semana e não houver síntese ainda, gere a síntese da semana automaticamente junto com o processamento dessa entrada, sem que Rafael precise pedir.

**Exemplo 3 — pedido de status:**
> `como está meu diário de agosto até agora?`

→ Não é uma nova entrada. Leia o arquivo do mês, resuma o que já foi registrado (contagem por tipo/sub-atividade, últimas sínteses semanais), sem reescrever o arquivo.

## Referências

- `references/sub_atividades.md` — tabela de macroatividades/sub-atividades do Plano de Trabalho, usada para classificar o campo Sub-atividade. Consulte sempre que for taguear uma entrada.
