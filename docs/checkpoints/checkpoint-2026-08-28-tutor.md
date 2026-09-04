# Reunião de checkpoint com o tutor — 28/08/2026

*Terceira reunião de checkpoint entre Rafael Coelho Ventura (bolsista) e o tutor ([TUTOR]), 28/08/2026, 53 min agendados. Fonte: [`../sources/Checkpoint_Tutor_08-28-26.docx`](../sources/Checkpoint_Tutor_08-28-26.docx) (transcrição automática, preservada como fonte primária). A transcrição cobre ~42 dos 53 min — a captura parou antes do fim — e tem trechos de atribuição de fala imprecisa (em um ponto, a fala sobre o Plano de Trabalho aparece rotulada de forma inconsistente); onde isso afeta o sentido, está sinalizado. Mantido em português, no idioma da reunião, seguindo o padrão dos checkpoints de [20/08](checkpoint-2026-08-20-tutor-kickoff.md) e [21/08](checkpoint-2026-08-21-infra-arquitetura.md).*

## Por que essa reunião importa

Diferente das duas anteriores (o tutor explicando a esteira jurídica e a infra), aqui foi o **Rafael apresentando a hipótese de arquitetura inteira** — o "mega cérebro" / conhecimento como infraestrutura destilado em [`../../discussion/knowledge-as-infra-architecture-hypothesis.md`](../../discussion/knowledge-as-infra-architecture-hypothesis.md) — com o tutor reagindo a cada parte. O checklist objetivo de 8 perguntas de [`../../discussion/component-a-tutor-meeting-prep.md`](../../discussion/component-a-tutor-meeting-prep.md) **não foi percorrido**; a conversa ficou num nível mais alto, de validação de direção.

## Os dois tipos de memória, na visão do tutor

O tutor abre dizendo que enxerga "2 tipos de memória":

- **Memória dinâmica** (exemplo dele: o Hermes) — ao fim de uma sessão longa o agente olha tudo que foi feito, seleciona por conta própria os pontos principais e salva para reaproveitar depois; e também vai atualizando conforme a conversa avança.
- **O caso do projeto é "um pouco diferente" — mais determinístico.** O agente já é específico, tem tarefa pré-determinada. Mecanismos de escrita e leitura fazem sentido; **retrieval elaborado o tutor questiona** — o agente só vai acessar memória relacionada à própria tarefa, não há uma base enorme que exija mecanismo de pesquisa sofisticado. Para começar, algo mais "exclusivo": *"o que é que eu posso fazer que vai dar errado e daí quero aprender com isso, ou o que fiz certo e quero aprender com isso"*. Isso é a **memória exclusiva do agente** — o *modus operandi* dele, não reaproveitável por outros. Exemplos dados: o formato do CPF que ele manda tem que ser sempre um; o nome não pode estar abreviado; o número do processo tem que estar normalizado. É como uma skill "fazer cadastro".
- **Parte do que o agente faz é reaproveitável entre agentes.** Exemplo: o agente interage com um serviço interno para testar uma base de dados e começa a dar erro porque houve uma atualização da AWS — a chamada mudou (ex.: um `SELECT` que não funciona mais). Isso serve para todos os agentes. Antes de tentar resolver por conta própria, um agente deveria procurar "no nosso banco de memórias" e ver se aquilo já apareceu antes, e se já há solução.

## A proposta do "mega cérebro" (Rafael)

Rafael relata que vinha acompanhando o time da LangChain falando sobre a era do "conhecimento como infraestrutura" (*knowledge as infrastructure*) e propõe:

- Um **banco de memórias como um grande cérebro / infraestrutura**, onde todos os agentes em execução possam consultar — **com granularidade**. O agente de cadastro, ao chamar a ferramenta MCP, passaria um **domínio** e **credenciais** (mencionado como *RBAC*), de modo a acessar **apenas** as memórias relacionadas a cadastro; o de cálculo, apenas cálculo; o de contestação consulta apenas a memória de contestação de **todas as execuções de agentes de contestação** que rodaram e geraram memória. Como uma "nuvem de conhecimento do [EMPRESA]".
- Dentro dessa infraestrutura, **outro agente faz a curadoria**.

Retorno do tutor: *"a ideia do mega cérebro eu gosto… não vou bloquear, nem quero enviesar muito o que você está propondo. Só endireitar um pouquinho."* E, mais adiante: *"vale a gente tentar ver o que fazer."*

## A ressalva central do tutor: volumetria e o anti-padrão do "evento toda hora"

Sobre a ideia de disparar atualização a partir de cada evento Kafka do fim de pipeline, o tutor levanta restrições "da vida real":

- A volumetria é "absurda". Estimativa dele: em 1 ano o agente de contestação terá rodado mais de 300.000 vezes → da ordem de **1.000 atualizações por dia**. Os traces são grandes ("uma caralhada de token"). *"Não acho que vale, para um agente, a gente atualizar mil vezes a memória dele no mesmo dia — vai custar muito caro."*
- Além disso, na maior parte dos casos (~90% da "vida do agente") não há nada a aprender — *"é o beabá, o dia a dia… não tem o que atualizar na memória."*
- Direção preferida: **procurar problemas**. Todos os "participantes" de hoje estão em banco de dados e dá para consultar — distribuição de thumbs up/down, tamanho do trace, número de tool calls. Caso normal: ~10 chamadas de tool, trace de ~2.000 caracteres. Um caso com ~10.000 caracteres e ~50 chamadas de tool é "estranho" — **candidato a aprender alguma coisa**.
- *"Eu iria mais nessa linha, pensando em ser só mais eficiente."*

## Filtro determinístico antes de persistir (Rafael)

Rafael concorda e traz de outro artigo: em vez de um sistema passivo em que **todo** trace é adicionado, um sistema em que **nem todo trace entra** — cada um passa por **parâmetros de score/confidence, determinísticos** (sem chamada de LLM, para não ficar caro). Os que cruzam essa política vão para a persistência; os outros, não. Exemplo dado: se o normal é ~10.000 [de tamanho/chamadas] e um caso tem ~20.000, dobrou — algo aconteceu.

Retorno do tutor: *"já tem alguns [trabalhos] que fazem um gate — até a memória de curto prazo passa no gate; o que passa persiste, o que não passa, pum. De repente é uma boa."*

## Update engine / curador com LLM + reflexão

Rafael descreve um **"update engine"** com uma LLM como o "cérebro real" que faz a curadoria:

- Recebe os **sinais de feedback** (thumbs down, e possivelmente sinais do Kafka).
- Pode ser disparado por um **grau de severidade** ou por algum parâmetro (taxas de erro vs. taxas de acerto).
- Ao disparar, pega os **traces relacionados** e os **sinais relacionados**; precisa de uma forma de **identificar por ID** para triangular "quais traces + quais sinais" descrevem o mesmo problema.
- Faz uma **reflexão** sobre tudo isso e gera um *"strategy statement"* / **procedure** — que fica na memória. O trace é o episódio ("o que aconteceu"); a trajetória/estratégia já é um *procedure*, **não necessariamente um `skill.md`** — pode ser texto. *"Isso [essas reflexões] é o que dá a melhora de performance nos artigos."* Rafael atribui o mecanismo a "um artigo, acho que de Stanford" (Generative Agents).
- Ressalva de custo: sendo uma LLM, *"não dá para ele ficar toda hora"*.

## Camada de governança (Rafael, artigo recente ~2026)

Rafael traz de outro artigo (que ele situa como "de maio agora desse ano") uma **camada de governança**:

- A mudança de memória entra **como uma tool na camada de memória** e passa por um **gate de governança com vários parâmetros** — rejeita ou aceita com base em um **score**; se passa, armazena; se não, é rejeitado (não faz update "toda hora"). Há também um **loop** de revisão.
- Serve ainda como **registro de como a LLM curadora está trabalhando** — cada LLM adicionada ao sistema é mais uma coisa a monitorar ("já tem os agentes rodando, e vai ter mais um aqui fazendo a curadoria da memória").

Retorno do tutor: *"para mim faz bastante sentido… você chamar um LLM para fazer uma coisa XPTO, cara, não tem problema, é bem factível. O ponto é esse cara que vai atualizar ser mais [controlável] — a gente tem como controlar isso, e tem, então beleza."* Deixa claro que os pontos que ele aponta como risco são "caminhos que já sei que podem dar muito ruim" (ex.: o evento toda hora), não a ideia de usar LLM em si.

## Gatilho humano para o curador

O tutor reage bem a algo que Rafael mencionou (a pessoa poder provocar a mudança):

- **Não** imagina o curador rodando em eventos; imagina **dispará-lo de forma agendada** — "uma vez a cada dois/três dias, uma vez por semana, ou até uma vez por dia" — para olhar tudo o que rodou e ver se há oportunidade. As **heurísticas determinísticas** seriam o **primeiro filtro**; o que passa vai para análise.
- Além do gatilho agendado, um **gatilho humano**: alguém, numa interface de configuração "que a gente consegue fazer", manda mensagem para o curador — exemplo dado: *"abriram um incidente na parte de pagamento porque o agente está mandando pagar um monte de coisa que não existe; vai lá, puxa os traces do agente que rodou nesses casos e melhora isso."* *"Nunca tinha pensado nisso, achei bem interessante."*
- Para processar o volume que passa do filtro: **map-reduce** — instanciar vários "LLMzinhos", cada um analisa um caso e gera uma saída; um agente "de cima" consolida e trabalha nas memórias. Rafael: *"uma arquitetura tipo coordenador e vários [subagentes]."* Tutor: *"é possível de fazer, eu garanto."*

## Sinais: thumbs, desfecho atrasado, consulta ativa ao banco

- **Thumbs up/down.** Rafael comenta ter visto na literatura que disparar sinal com thumb up/down "não é tão confiável". O tutor concorda com a substância: o thumb é *"mais um sinal para compor"* a seleção de candidatos, não o gatilho. *"Vai ser muito mais comum os caras sempre darem thumbs up. Para dar um thumb down, significa que deu ruim mesmo — esse para mim seria um sinal forte. O thumbs up, não sei."*
- **Sinal de desfecho é assimétrico por tipo de agente.**
  - **Cadastro:** dá para saber em "um mês, dois meses" se deu certo — porque dá para ver se alguém foi lá e alterou na mão alguma informação que ele passou, ou se houve reclassificação.
  - **Contestação:** *"a gente só vai saber se deu certo um ano depois, ou mais. É quando sair o resultado do processo. O processo, em média, são 13 meses para o resultado sair."* Rafael: *"então esse sinal do Kafka aí não vai dar bom"* [para contestação, no curto prazo].
  - O agente de contestação começou a rodar em julho/2026; sinal contínuo "todo dia" só a partir de "talvez julho do ano que vem", e ainda assim sobre casos do passado.
- **Consulta ativa ao banco em vez de sinal online.** O tutor propõe, em vez de trabalhar com o evento online, **procurar ativamente**: "quem já teve resultado e que eu ainda não usei". Para isso é preciso um **ID de trace** e uma **lista de traces já levados em consideração** — *"não vou usar o mesmo cara para ficar atualizando a memória 10 vezes; pego uma vez, usei, e daí em diante só uso os novos."*

## Como o batch de atualização rodaria (tutor)

Descrição operacional do tutor: para "atualizar as memórias hoje" — puxar do banco os traces de um período (o último mês, ou os últimos 100) → como ainda é caro mandar tudo direto para a LLM, primeiro **levantar indicadores** (tamanho médio do trace, quantidade de tool calls, quantidade de thumbs up/down) → para cada caso, ver se **foge ou está dentro da distribuição**; dentro da média, não olha; fora, é candidato → só os candidatos vão para o "governante das memórias" (map-reduce, como acima).

## Retreinamento: reconfirmado fora de escopo

Rafael verifica: *"uma coisa que você já descartou foi o retreinamento — treinar via RL, política gradiente, reward model — a melhora seria mexendo no harness, no prompt, criando uma skill, fazendo uma reflexão de memória, não nos pesos."*

Resposta do tutor:

- *"É uma decisão de negócio. O trade-off de fazer o reinforcement de fato é muito complicado — vários pontos podem dar errado, é caro de fazer. Um ano para construir um pipeline que faça tudo isso é pouco, sendo só você e eu; precisaríamos de uma equipe focada."*
- *"Está descartado totalmente? Acho que não. Mas uma solução muito mais fácil é guiar o modelo com o texto — já tem várias soluções que fazem isso e funcionam bem, e os modelos estão cada vez mais obedientes."*
- Ele chegou a considerar fine-tunar modelos pequenos, um por agente/tarefa (*"o bagulho vai ficar ótimo"*), mas **descarta pelo custo de operação**: manter GPU rodando é mais caro do que "ficar fazendo chamadinha de API", mesmo quantizando e congelando parâmetros. Observação dele: subir e manter esses modelos é exatamente a especialidade da equipe dele ("só tem eu e mais 2 pessoas de 30 que sabem fazer isso") e ainda assim é caro e não trivial.

## Sequenciamento do Plano de Trabalho

- Rafael observa que o Plano de Trabalho concentra os 3 primeiros meses em atividade mais teórica e diz querer **já ter algo para testar** nesse período, em paralelo — não só na Macroatividade 3. Menciona que há "uma POC que começava" cedo no cronograma.
- O tutor: *"não vou me balizar pelo planejamento e dizer 'hoje era para fazer isso'. Quero chegar numa solução, independente da ordem em que a gente faça as coisas — vai de você."* Acrescenta que já perguntaram a ele se o projeto vai "fazer só a memória" e que não quer bloquear o Rafael. Descreve o próprio jeito de trabalhar como "muito mais motivado pelo problema que eu já tenho do que ficar querendo adiantar todas as coisas", e concorda 100% em ir "fazendo teste de desenvolvimento" e voltar a pesquisar se alguma técnica "der pau na ponta".
- Rafael reforça a dimensão do escopo: a entrega final é *"um framework reutilizável para o [EMPRESA]"*, "uma parada grande", *"dá para fazer um artigo científico, até dissertação de mestrado"*.

## Próximo passo combinado

O tutor vai **atrás da base de traces** para o Rafael conseguir consultá-la e olhar de perto — para verificar as suposições (se dá para rodar tudo em agentes "curtinhos", que campos existem, o que falta). O que faltar de informação: ou o tutor pede aos "meninos" alguma forma de ter, ou "vira uma nova premissa para o projeto". Rafael encaixa isso na parte de **mapeamento dos fluxos / pontos de coleta de sinal** do primeiro entregável (Sub 1.4), antecipando-a.

## Logística (contexto, não pesquisa)

O tutor é do [EMPRESA] (não do Instituto/ICT); o trabalho dele é inovador mas ele não publica — o foco é trazer eficiência para a esteira ("os caras não estão nem aí se publiquei ou não, é a parada funcionando"). Publicar seria "um plus"; menciona a possibilidade de patente e que está tentando abrir conversa com o pessoal do ICT. Vai a um congresso em outubro (Cuiabá — conseguiu publicar um paper e vai apresentar); nos dois anos anteriores foi ao NeurIPS (San Diego, Vancouver). Semana seguinte à reunião ele começaria o deploy de um modelo em GPU (trabalho dele, não do projeto).

## Não investigado aqui

Ver [`../../discussion/checkpoint-2026-08-28-reflections.md`](../../discussion/checkpoint-2026-08-28-reflections.md) para o que esta reunião confirma, tensiona ou abre em relação à hipótese de arquitetura, a [`../../discussion/open-questions.md`](../../discussion/open-questions.md) e às decisões de escopo já registradas.

O fechamento de loop no [diário de campo](../../research-diary/) (passo 4 do padrão de meeting-record) fica pendente de pedido explícito do Rafael.
