# Reunião de checkpoint com o tutor — 20/08/2026

*Resumo da primeira reunião de checkpoint substantiva entre Rafael Coelho Ventura (bolsista) e Luis Felipe Chary de Lima (tutor), 20/08/2026, ~45 min. Fonte: [`../sources/Checkpoint_Tutor_2026-08-20.docx`](../sources/Checkpoint_Tutor_2026-08-20.docx) (transcrição automática da reunião, preservada como fonte primária). Esta é a transcrição referenciada como "pendente de anexar" na [entrada de 20/08 do diário de campo](../../research-diary/diario_campo_2026-08.md#20082026) para o Sub 1.4 (mapeamento dos fluxos jurídicos) — já está anexada. Mantido em português, no idioma original da reunião, por decisão explícita do bolsista.*

## Por que essa reunião importa

Aqui o tutor explica a Rafael o fluxo jurídico real ("esteira jurídica") em que o mecanismo do projeto vai atuar e, de passagem, sem que ninguém perguntasse diretamente, descreve com as próprias palavras que tipo de "aprendizado por reforço" ele espera. Essa segunda parte é o ponto central: é a fonte real por trás da decisão de 20/08 já registrada em [`../../discussion/scope-and-terminology-decisions.md#2`](../../discussion/scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title) (ajuste de harness via sinal do usuário, não SFT) — ver a nota de reflexões para o trecho exato.

## O fluxo jurídico ("esteira jurídica")

Cerca de 1.000 pessoas hoje tocam toda a esteira jurídica do banco. Exemplo concreto usado na explicação: um cliente contesta um "consignado" (empréstimo com desconto em folha) que não reconhece e entra com uma ação. O banco é avisado por vários canais (carta, oficial de justiça, e-mail, um webhook do tribunal) e o caso entra num pipeline em etapas:

1. **Cadastro** — registrar o caso: ler a petição inicial, extrair nome do reclamante, tribunal, UF, data de início, o pedido.
2. **Subsídios** — levantar evidência interna de suporte (por exemplo: o cliente assinou mesmo o contrato do consignado?).
3. **Contestação** — montar a defesa do banco a partir do pedido + evidência levantada.
4. Despacho para um escritório de advocacia terceirizado — o banco tem mais de 600 mil processos ativos, volume muito maior do que a equipe interna daria conta; os escritórios tocam audiências, tentativas de acordo, e retornam pelos sistemas do banco (propostas de acordo, resultado da sentença).
5. Decisão pós-sentença: recorrer, ou cumprir (pagar a indenização definida, cancelar o contrato, tirar o nome do cliente do Serasa, encerrar o caso).

Isso era tradicionalmente chamado de "esteira" (linha de produção): padronizado, guiado por checklist, mas operado por ~1.000 pessoas executando o que já é um workflow digital — "a gente tem um workflow digital... mas são as pessoas que estão imputando o dado, lendo o documento e decidindo as coisas."

## Como a automação evoluiu, em três etapas

1. **Dicionário de regras** — o jurídico definia um livro de regras explícito por cenário (ex.: se existe contrato assinado → defender até o fim; se não existe → tentar acordo).
2. **ML clássico** — a equipe do tutor treinou um modelo sobre o histórico de resultados de processos para prever probabilidade de ganho/perda, substituindo o dicionário de regras como critério de decisão em algumas etapas. Confirmado como inferência clássica supervisionada, não o RL que este projeto estuda.
3. **Agentes, agora** — cada etapa do pipeline está sendo substituída, bloco por bloco, por um agente de LLM fazendo o que a pessoa fazia: o agente de cadastro lê a petição e gera um JSON (nome, tribunal, UF, pedido, ...) que alimenta a próxima etapa; um agente de subsídios identifica que evidência falta e vai buscá-la via APIs internas; um agente de contestação redige a defesa inteira. Nas palavras do tutor: "a gente está com a carroça andando... a gente está construindo um novo workflow... que vai funcionar em prol do agente" — o próprio workflow digital ao redor está sendo reconstruído em função dos agentes, não o contrário.

## Arquitetura atual dos agentes: agentes separados, sem conversa cross-agent

Cada agente de cada etapa foi construído de forma independente. Eles **não** conversam diretamente entre si — o output de um agente é o input do próximo, "como se fosse sistemas separados." Dois motivos dados pelo tutor:

- **Escopo estreito por etapa** — cadastro é relativamente trivial (ler e extrair); outras etapas (ex.: interpretar uma sentença e gerar as ordens decorrentes — pagamento, baixa de contrato, remoção do Serasa) já pressionam o limite de contexto do agente sozinhas, sem contar coordenação entre agentes.
- **Atrito de segurança/compliance** — Rafael levantou isso diretamente e o tutor confirmou: fazer agentes se chamarem não é simples mesmo rodando na mesma infraestrutura, por causa de autenticação e barreiras de compliance entre eles.

## Modos de interação

Duas formas de acionar os agentes hoje:

- **Modo copiloto/chat** — como um agente novo costuma começar: uma pessoa sobe um documento e pede para o agente fazer a tarefa; o agente responde; a pessoa imputa o resultado manualmente no sistema.
- **Modo sistêmico/orientado a eventos** — adicionado quando um agente já provou ser confiável: um serviço de backend chama o agente direto via API (um prompt é enviado, sem pessoa no meio), e a resposta volta como um evento Kafka. O tutor espera que o mecanismo do projeto rode "de uma forma... puramente sistêmica," disparado por um gatilho de tempo ou de volume de anotação (ex.: "juntei mais 100 avaliações aqui desse case, vamos avaliar e ver se precisa atualizar a skill, a memória, seja lá qual for o mecanismo").

## Regras de negócio ficam fora do agente, via MCP

Regras que mudam com frequência e são de propriedade da área de negócio — ex.: o limiar de "grande causa" (causa de alto valor), hoje R$500.000 mas ajustável a qualquer momento — **não** ficam codificadas na memória ou no contexto do agente. Elas são expostas como tools MCP controladas pela área de negócio (ex.: uma tool `is_grande_causa(valor)` retornando `true`/`false`), para que a área possa mudar a regra sem exigir deploy de nenhum agente. MCP é a camada de integração padrão no Itaú tanto para ferramentas internas (acesso a banco de dados, documentos) quanto para esse padrão de desacoplamento de regra de negócio.

## O problema, na formulação do próprio tutor

O número de agentes está crescendo rápido — algo como 2 em produção até o fim de 2026, ~6 em meados de 2027, mais de 20 no ano seguinte — contra um volume de casos e um cenário jurídico em evolução contínua. Hoje, humanos validam tudo que cada agente faz; essa dependência de humano no loop é exatamente o que não escala além de um punhado de agentes. A formulação do tutor sobre o que é necessário: "a gente vai anotando alguns casos ao longo do tempo... avalie aqueles que estavam certos, aqueles que estavam errados e se corrija... a forma de fazer, para tentar diminuir ao longo do tempo esses casos errados."

## Notas de logística e infraestrutura (para a próxima reunião de infra)

- Uma reunião separada foi marcada com "Fed" (descrito como um engenheiro muito técnico e especializado) mais Adriano e Yoshio, para cobrir: um desenho completo da arquitetura, os serviços AWS usados (toda a plataforma roda em AWS), o serviço de containers em que os agentes rodam, arquitetura Kafka/eventos, chamada síncrona vs. assíncrona, tools MCP de regra de negócio, e a estrutura dos repositórios.
- Existe um "monorepo" — um mapeamento assistido por um agente (sem provider definido) sobre cerca de 130 repositórios — que indexa onde cada agente vive, sua arquitetura, e seus pontos de entrada; o tutor ia mandar o link.
- Existe um banco de dados dedicado à configuração dos agentes que poderia, em tese, também servir como local de armazenamento de memória — vale uma pergunta concreta na reunião de infra, ainda não confirmado como adequado.
- Não há convenção formal rígida de commit/PR além de "não seja burro" (ex.: não subir cinco features num commit só); testes automáticos e checagens de segurança liberam o merge, mas só o PR final para produção exige aprovação humana — a revisão de time acontece de forma combinada, na conversa.
- Para a experimentação do próprio Rafael (sem tráfego de produção, sem paralelismo), a escolha de modelo é livre — disciplina de custo importa para o trabalho do próprio tutor gerando dados sintéticos em larga escala, não para a conta de dev deste projeto. O VS Code precisa de um proxy HTTP interno configurado para acessar as APIs de LLM; algumas ferramentas (Claude via a conta compartilhada, Copilot) estão sujeitas a cotas de uso compartilhadas que se esgotam rápido quando abertas amplamente pela organização — o tutor contorna isso usando seu próprio acesso via AWS Bedrock.
- Rafael confirmou explicitamente com o tutor que a amplitude atual da revisão bibliográfica (panorama geral de memória/RL, para depois generalizar e afunilar) está dentro do escopo, não é um desvio.

## Não resolvido nesta reunião

Ver [`../../discussion/checkpoint-2026-08-20-reflections.md`](../../discussion/checkpoint-2026-08-20-reflections.md) para o que isso muda ou abre em relação ao plano de trabalho, e [`../../discussion/open-questions.md`](../../discussion/open-questions.md) para os itens que essa reunião adiciona.
