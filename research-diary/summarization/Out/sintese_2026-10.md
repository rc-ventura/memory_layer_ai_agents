# Síntese Mensal do Diário — Outubro de 2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Leitura rápida do mês, semana a semana. Até 4 registros — a reflexão de cada semana, tirada dos arquivos episódicos em `../../Out/diario_campo_*.md` e apenas organizada aqui. Regenerável. Não duplica o log episódico nem substitui o export `.docx` do coordenador.*

- **Última regeneração:** 28/10/2026

---

### Semana 1 · 05–09/10/2026 · 6 registros

A semana foi de fechar as bases 1 e 2 como laboratório de método e de adaptar tudo à base 3, que passa a ser a fonte da verdade — mas é uma base **derivada**: só os ActionSteps com erro, cada um com a janela do passo anterior e dos dois seguintes, sem trace cru, sem prompt e sem denominador. Na base 2, a segunda rodada não achou nenhum sucesso falso nos 24 candidatos (a resposta final declara a falha) e mostrou que o "campo inexistente" nasce do próprio prompt, como na base 1. A adaptação foi feita em camadas — leitor único de CSV/parquet, adaptador estrutural, componentes observadas, mineração observada, painel — sem inventar posição de passo nem tratar ausência como zero; um teste com resposta conhecida (a base 1 passada pela query da base 3) deu 415 erros na mesma unidade, 83 pendentes e nenhum em unidade errada. A rodada real deu 10 candidatas, 76% dos erros numa unidade e 24% pendentes. Em paralelo, o kit de mineração ganhou skills, agentes e scripts (0.4.1 a 0.6.0) e foram escritos o painel com sete gráficos de leitura e o pedido de dados ao tutor (A: denominadores por execução/agente/papel; B: complemento dos pendentes; C: ajustes na extração).

**Decidido:** a base 3 é a fonte da verdade, e as bases 1 e 2 servem para fixar o método; o "campo inexistente" vira sinal de harness nas duas bases; pendente não é resíduo (três categorias: o que a regra explica, o que não explica, o que explicaria se o dado chegasse); não reescrever a taxonomia, só reaplicar onde o dado basta; nada afirmado sobre a base 3 sem contagem tirada dela; só orquestração em Python, sem notebooks novos; relatório concreto ao tutor, com o número em dinheiro tratado como teto, não como economia.

**Em aberto:** a definição de sucesso em três níveis (o passo rodou · a ferramenta devolveu · a tarefa terminou) ainda precisa separar "terminou" de "terminou com o conteúdo pedido", parte semântica; a dupla contagem do mesmo episódio em dois baldes (falha silenciosa e erro visível em passos seguidos) não tem regra geral; os 5.818 erros de nome não definido sem passo anterior (fechados na Semana 2); o filtro de tamanho da query exclui a execução quando um texto é nulo, com possível corte das execuções sem resposta (vai para o pedido da v2); os tokens por erro medem onde o erro acontece, não a gravidade — confirmar com a conta de entrada e saída.

---

### Semana 2 · 12–16/10/2026 · 2 registros

A semana abriu com a investigação dos 24% de pendentes da base 3. Mais de 5 mil eram erros de nome não definido, e quase todos (5.762 de 5.764) eram de um papel só, o ContestacaoCivel, concentrados em agosto. A hipótese de uma "inversão de linha" se mostrou leitura da contagem, não causa: o prompt manda verificar a variável com `try/except NameError` e o sandbox levanta `InterpreterError`, que o `except` não captura (reproduzido num interpretador de teste; a evidência do prompt vem da base 2). O Ajuste 17 criou a unidade da verificação de existência (5.764 erros, 5.442 execuções, 112 milhões de tokens), com destino harness, e os pendentes caíram de 24% para 6%. Na reunião com o tutor, a explicação de gráficos soltos não funcionou; ele pediu uma apresentação amarrada que dê sentido ao projeto, e ela foi estruturada em sete blocos (overview, base, panorama, taxonomia, principais erros, lições, quanto vale mitigar).

**Decidido:** o destino dessa unidade é o harness (prompt ou interpretador), não uma lição de memória; a apresentação segue a estrutura de sete slides; a semana seguinte é para finalizar a mineração de pelo menos duas unidades e montar a apresentação.

**Em aberto:** a base 3 não traz o prompt — a evidência é da base 2 e a assinatura só prova o padrão; não se sabe se a instrução já existia no prompt de julho (julho já tem 95 erros com a mesma assinatura); os 514 erros do primeiro passo sem essa assinatura são outro mecanismo, por dedução; o registro de monitoramento e o aviso a quem cuida do harness ficaram adiados; pedir o hash do trecho do prompt no pedido de dados; alguns gráficos ainda precisam de ajuste e discussão.

---

### Semana 3 · 19–23/10/2026 · 6 registros

A semana foi do piloto de mineração do sandbox e da montagem da apresentação. A unidade do sandbox se dividiu em partes com causa, dono e escopo próprios: A (introspecção do ContestacaoCivel, induzida pelo prompt → harness), B (ferramenta importada como módulo), C (módulo usado sem import), D (import fora da lista autorizada) e E (funções e atributos proibidos); a maior parte dos erros virou sinal de harness (cerca de 62% no piloto de 19/10; 69% na rodada nova de 21/10, com 77 medidas iguais às da auditoria independente). O resto é hábito do agente e vira memória, global (C, E) ou por papel (B, D). A conferência de ambiente passou a usar o interpretador e não o prompt, porque o prompt anuncia um ambiente diferente do que o interpretador aceita (na base 1, 11 de 11 `import json` rodam com um prompt que não o lista). Em 22/10, as memórias de poucos casos ou que só repetem o prompt ficaram catalogadas e vigiadas (raras e de reforço), e só C, E e C.JoogleAnalytics seguem para injeção e para o degrau 3. O kit de mineração e os quatro degraus de validação (candidata → conferida → revisada → validada) foram documentados.

**Decidido:** A vai para o harness; C e E são memória global; B e D, memória por papel; as não injetadas ficam monitoradas como rara ou reforço, com alarme no catálogo; a conferência de ambiente usa o interpretador; "sinal de harness" (erro induzido pelo prompt ou pelo contrato da ferramenta) e "destino harness" (infraestrutura, protocolo, timeout) ficam distintos nos slides; o degrau 3 (revisão de casos) vai para a base 3, com prioridade; apresentação segue com o piloto do sandbox nos slides 5 e 6.

**Em aberto:** seis das 14 memórias têm de 1 a 3 erros — decidir se aplica a régua de memória rara antes do experimento (`b3 #48`); as memórias foram construídas, não testadas: a redução do erro só se mede no teste de compensação (`b3 #39`); o destino memória de C, B e D foi decidido sem ler os prompts desses papéis; cerca de 134 verificações com valor padrão continuam na E, provavelmente com a mesma causa do prompt; a parte F (`globals`, `locals`, `vars`, `eval`) fica para depois; a divergência prompt × interpretador segue como aviso à plataforma (transversal #7); a segunda unidade de memória e o fechamento dos gráficos de cada slide.
