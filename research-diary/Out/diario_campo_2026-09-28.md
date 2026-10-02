# Diário de Campo — Rafael Coelho Ventura

## Semana de 28/09 a 02/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 28/09/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Dia cheio de ajustes na triagem da mineração de memória rodando na base 2, feitos junto com um agente (sem provider definido) que implementou as mudanças no pipeline. Fez a decisão de mineração de uma unidade passar a contar na triagem — quando um erro já foi minerado antes, isso vira sinal pro relatório em vez de ficar escondido. O agente tentou também comparar a composição de cada unidade com a composição de referência da base 1, pra pegar o caso de uma base nova trazer a mesma mensagem de erro só que com causa diferente por trás — mas essa ideia não fechou e teve que reverter no mesmo dia. No fim resolveram um jeito mais simples: cada base decide sozinha, e a decisão de mineração só vale dentro da base onde foi tomada (criou um identificador de base pra isso). Fechou o dia desmontando um erro "?" que juntava sete casos de três tipos diferentes (timeout do interpretador, código lento, limite de passos) — separou cada um na família certa. No meio disso ainda entregou o relatório mensal de setembro pro fomento.

**Reflexão:** O ajuste que reverteu foi importante — mostrou que tentar comparar bases direto, uma "olhando" pra outra, complica mais do que resolve; é melhor cada base ter sua própria régua e deixar a mineração pegar o que destoa, sem inventar uma camada de comparação cruzada. Foi um dia de ida e volta, mas no fim ficou mais simples do que antes.

**Decisão/próximo passo:** Seguir olhando os erros "?" que sobraram e continuar batendo a base 2 contra a base 1 caso a caso.

**Tags:** mineracao, triagem, identificador-de-base, composicao-revertida, relatorio-mensal, erro-desmontado, timeout-interpretador, codigo-lento, limite-de-passos, sub-2.2, sub-2.5

## 29/09/2026

**Tipo:** achado — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Passou o dia investigando, com um agente (sem provider definido) fazendo a leitura no cru e as mudanças de código, os casos de "código lento" que pareciam ser de um dos agentes jurídicos (Procurações). A hipótese inicial — de que era só a ferramenta final de resposta rodando fora de um laço — não se sustentou de cara e o agente teve que reverter de novo. Voltaram com mais calma pra investigar de verdade, olhando o texto cru na outra máquina, e descobriram que não é código lento: o agente jurídico estava jogando o resultado bruto da busca (um textão de 25 a 60 mil caracteres) direto na resposta final, e era isso que demorava — nada a ver com laço no código. O agente montou uma ferramenta de linha de comando pra conseguir olhar esses casos de forma repetível. Fecharam também a etapa que tava pendente sobre os erros de tempo da base 2 — os 6 casos bateram com a explicação nova. E deram ao erro crítico (quando a execução simplesmente morre no meio) uma cor e família só dele, porque ele tava escondido dentro da família errada.

**Reflexão:** Essa foi a segunda vez em dois dias que reverteu uma mudança de regra por falta de evidência — e isso é bom sinal, não ruim: mostra que o processo de "olhar o cru antes de mudar regra" está funcionando, mesmo custando um passo a mais. O caso do resultado bruto também é interessante porque não é bug de código — é o próprio agente "se afogando" no tamanho da resposta, uma lição que vale a pena guardar como memória mesmo.

**Decisão/próximo passo:** Usar a ferramenta nova pra fechar os casos parecidos que ainda restam e seguir de olho no que aparecer na família "protocolo do harness".

**Tags:** codigo-lento, resultado-bruto, drill-down-tempo, reversao-de-regra, erro-critico, cor-propria, etapa-fechada, agente-procuracoes, sub-2.2

## 30/09/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Dia inteiro em cima de outro erro chato da base 2, investigado com um agente (sem provider definido): o modelo respondendo sem colocar o código no bloco que o sistema espera. Primeiro confirmaram que isso é coisa nova dessa base (concentrado em agosto, quase todo num agente jurídico só) e não repete dentro da mesma execução — parece incidente isolado de plataforma, não erro recorrente. O agente foi cavando mais fundo e achou que existem dois "modos" de o agente jurídico escrever código (um mais estruturado, outro em texto livre com marcação) e o erro só acontece no modo texto livre. Juntando isso com o histórico, viram que o motivo de agosto ter tanto erro foi simplesmente ter trocado de modelo bem naquele mês. Compararam também com a base 1: lá o mesmo tipo de erro aparece só num mês específico do ano passado, ligado a uma versão antiga de um contrato de resposta. No meio disso teve uma ideia minha: o prompt do sistema explica o formato técnico de um jeito no começo e depois, no fim, pede outra coisa em cima da tarefa de negócio — e parece que o modelo escuta o pedido de negócio e esquece o formato técnico; o agente confirmou isso batendo em alguns casos concretos. Fecharam o dia arrumando uma ferramenta pra olhar os metadados dos passos (tamanho, motivo de parada, tokens) e organizando tudo num documento novo, com a família "protocolo do harness" ganhando espaço próprio.

**Reflexão:** Foi um bom dia de conseguir separar "isso é comportamento do agente" de "isso é decisão de plataforma" — no caso, trocar de modelo sem revalidar o formato de saída. A ideia da ambiguidade do prompt (formato técnico no começo, pedido de negócio no fim) é minha e parece fazer sentido com o que apareceu nas evidências — vale registrar como hipótese própria, não só como achado técnico solto. É engraçado ver o projeto virando também uma ferramenta de auditoria da própria plataforma, não só da memória do agente.

**Decisão/próximo passo:** Seguir pros próximos papéis (Cálculo e Resposta Bacen) com esse mesmo olhar de "modo do agente + versão do modelo" e formalizar a hipótese da ambiguidade do prompt em algum lugar que dê pra testar depois.

**Tags:** resposta-sem-bloco-de-codigo, incidente-de-plataforma, troca-de-modelo, modo-texto-vs-estruturado, hipotese-do-rafael, ambiguidade-do-prompt, protocolo-do-harness, metadados-dos-passos, sub-2.2, sub-2.5
