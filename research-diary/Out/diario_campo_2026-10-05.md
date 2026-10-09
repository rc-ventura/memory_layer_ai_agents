# Diário de Campo — Rafael Coelho Ventura

## Semana de 05/10 a 09/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 05/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 1.5 — **Canal:** formal-tutor

**Registro objetivo:** Dia de fechar tudo pra rodar a base 3 amanhã. A base 3 não é "mais uma amostra": são todos os traces consolidados, a nossa fonte da verdade. As bases 1 e 2 serviram pra sedimentar e discutir o método; o que sai delas é o que vamos aplicar na base 3. Fechei a base 2 com a segunda rodada (o agente respondeu as seis perguntas que estavam abertas) e o resultado mais importante foi: nenhum sucesso falso confirmado — nos 24 candidatos, a resposta final declara a falha. Também confirmamos que o "campo inexistente" da base 2 nasce do prompt (ele pede `quebra_sigilo` e a ferramenta devolve `vazamento_sigilo`, 38 de 38 com a chave errada no próprio prompt), igual à base 1, e decidi que ele vira sinal de harness nas duas bases. E a maior candidata da base 2, "nome usado sem ter sido definido", tá concentrada num papel, num mês e num modelo só — cara de incidente, não de lição. A branch da consolidação ficou pronta pra fechar.

Até quinta que vem tenho reunião com o meu tutor, e ficou decidido que vou apresentar um relatório concreto das unidades de memória mineradas: formato de equipe técnica, mas com linguagem palatável pra gerência. A mensagem é mostrar que o projeto faz sentido: temos X erros, essas unidades de memória mitigariam parte deles, e isso tem um valor em dinheiro.

Pra isso quero fechar a fundamentação e criar skills específicas, pra ter reprodutibilidade sem ficar repetindo prompt: uma pra mineração de unidade de memória (como fizemos com as unidades nº2 e nº10 na base 1), uma pra minerar o resíduo (como nas bases 1 e 2), uma pra erros críticos, uma pra erros de protocolo do harness e uma pras falhas silenciosas. Assim as análises ficam padronizadas.

**Reflexão:** O grande achado da semana passada foram os erros silenciosos: a ferramenta falha e o step não loga o erro. Mas a minha preocupação principal é outra: quando a ferramenta falha, o agente precisava daquele retorno pra seguir o fluxo e entregar uma resposta final completa e certa? Se precisava e entregou mesmo assim, é sucesso falso — e isso seria um medidor muito importante pro Update Engine da arquitetura de memória. Quero achar um jeito determinístico de medir, nem que precise de LLM só pra parte semântica (aí marcado como leitura assistida, fora do caminho de classificação, que continua sem LLM). A base 2 já ensinou uma coisa: tem um terceiro desfecho no meio — a resposta que **declara** a falha. Ela não mente, mas também não entrega a tarefa completa. Então o meu medo se divide em dois: resposta errada (sucesso falso) e resposta incompleta (falha declarada).

Isso puxa a definição de sucesso. A ideia é um sucesso em três níveis (o step rodou sem exceção · a ferramenta devolveu resultado · a tarefa terminou com resposta final), mas ainda falta o racional, porque um step de sucesso pode ter chamada de ferramenta com erro, e terminar com resposta final não garante que a resposta saiu completa. Provavelmente o terceiro nível precisa separar "terminou" de "terminou com o conteúdo que a tarefa pedia" — e essa última parte é semântica.

Sobre contar o mesmo erro duas vezes agora que temos dois baldes: o mesmo step nunca entra nos dois (o funil separa por step; conferido, zero nas duas bases), e a consolidação conta execuções pela união. O que ainda pode acontecer é o mesmo episódio aparecer nos dois canais em steps seguidos (uma falha silenciosa e logo depois um erro visível, com a mesma causa) e virar duas ocorrências. Na unidade que juntamos ("colar o print"), isso deu zero nas duas bases, mas não existe regra pra isso em geral. Tá registrado no plano.

E vimos que parte dos erros nasce do prompt do agente e de documentação de ferramenta ambígua, como a `resposta_final`, que compete com o `final_answer` do framework. Isso não é memória: é sinal de harness.

**Decisão/próximo passo:** Fechar a branch da consolidação e abrir uma nova pra discutir as medidas (o que de fato queremos medir em cada uma, antes de implementar). Preparar a leitura do parquet pra base 3 — hoje o código não lê parquet. Criar as skills de mineração, resíduo, erro crítico, protocolo do harness e falhas silenciosas. Montar o relatório pro tutor, tomando cuidado com o número em dinheiro: o que o trace dá é o custo dos erros que caem em unidades candidatas (um teto); a economia de verdade depende de quanto a memória evita, e isso só um teste mede.

**Tags:** base-3, fonte-da-verdade, base-2-finalizada, sucesso-falso, falha-declarada, sucesso-em-tres-niveis, update-engine, dois-baldes, dupla-contagem, sinal-de-harness, skills, relatorio-tutor, custo-dos-erros, parquet, sub-2.2, sub-1.5

### 05/10/2026 (tarde)

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Fiz a primeira parte da adaptação à base 3: o código deixa de assumir CSV. Criei um leitor único do trace (`analysis/leitor_trace.py`) que abre CSV (puro, `.xz`, `.gz`) ou um único parquet, decidindo o formato pelo conteúdo e não pela extensão. O parquet é normalizado coluna a coluna para o mesmo contrato do `read_csv(dtype=str)` — coluna tipada vira texto, coluna aninhada vira JSON, vazio vira nulo — de modo que o `base_pipeline.py`, o `checklist.py`, o `drill_down.py` e as nove auditorias independentes só trocaram a abertura do arquivo. Conferência na base 1: idêntica em CSV, parquet em texto e parquet tipado (nove auditorias byte a byte, as 275 saídas de `resultados/` iguais, cinco notebooks sem erro). Entrou o `pyarrow` no projeto, `.parquet` e `.csv.gz` no `.gitignore` (PII). No mesmo dia, o kit de mineração ganhou as skills, os agentes e os scripts (versões 0.4.1 a 0.5.2).

**Reflexão:** Descobri uma pegadinha do `pyarrow`: com ele instalado, o pandas passa a guardar todo texto em arrow, e as regex de `.str` rodariam no RE2 do arrow, não no `re` do Python — `\s` deixa de casar o espaço não separável e o lookahead não compila. As regras da taxonomia foram escritas e auditadas no `re`, então o pandas ficou fixado no texto em Python. Sem isso o parquet mudaria número sem avisar.

**Decisão/próximo passo:** Ler o parquet já não é o problema. O próximo é o que o parquet da base 3 *não* tem — ver a entrada de amanhã.

**Tags:** base-3, parquet, leitor-do-trace, pyarrow, re2, kit-mineracao, adaptacao, sub-2.2

## 06/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** O dia em que ficou claro que a base 3 pede mais do que um adaptador de leitura. As bases 1 e 2 eram amostragens com ideia de censo: tínhamos os traces crus, então dava para uma visão holística — ActionSteps com e sem erro, gasto de tokens com e sem erro, o prompt de cada agente, a posição de cada step dentro da cascata da trajetória. A base 3 é derivada: só tem os ActionSteps com erro (a query `ICTI_crossmemory_query_mineracao_erros` no Athena, que guarda cada erro e uma janela com o passo anterior e os dois seguintes), sem trace cru. Isso quebra partes da análise anterior: algumas famílias e baldes da taxonomia foram construídos em cima do registro populacional completo — as falhas silenciosas, o sucesso por conteúdo, qualquer taxa (erros por passo, por papel, por mês), o protocolo lido do prompt, a posição na trajetória. Fiz o diagnóstico do que a extração entrega e do que não entrega, e a especificação do que cada parte do método precisa.

Em paralelo, fechei a branch do kit de mineração (0.6.0: leitura em duas etapas com o gate do pesquisador, monitoramento determinístico, a fonte do kit passando a ser o próprio repositório, versionada) e cortei o `plano-atual.md` de 857 para 296 linhas, deixando o porquê e os números nos documentos certos. Deixei pronto o prompt para validar o kit na base 2.

**Reflexão:** O risco de adaptar sem cuidado é fabricar informação para fechar a conta: tratar ausência como zero, como sucesso, ou numerar os passos só entre os erros e chamar isso de posição na trajetória. A pergunta que guia a adaptação não é "como fazer a regra rodar" e sim "o que esta regra precisa e a janela dá".

**Decisão/próximo passo:** Não reescrever a taxonomia. Reaplicar as mesmas regras, só onde o dado basta, e marcar o resto como pendente (com o motivo), sem misturar com resíduo.

**Tags:** base-3, base-derivada, censo, trace-cru, taxonomia, denominador, adaptacao, kit-mineracao, plano-atual, sub-2.2, sub-2.5

## 07/10/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Dia de implementar a adaptação. Ficou em camadas: (1) um adaptador estrutural que normaliza a extração em passos, janelas (n−1, n+1, n+2) e vínculos candidatos entre erros seguidos, sem inventar posição de step nem fronteira de chamada, e que já prevê o formato de censo caso ele venha; (2) as componentes observadas (o equivalente da "cascata" das bases 1 e 2, mas condicional ao que a janela confirma); (3) o `base_pipeline.py` com um modo só de carga e bloqueios explícitos que impedem rodar regras de trace completo em dados parciais; (4) sintomas e custos; (5) mecanismos observáveis; (6) a triagem e o perfil da candidata. Cada regra de classificação é a mesma das bases 1 e 2 (conferido por estrutura de código).

Resultado na base 3 (31.421 linhas = 30.141 erros estruturados + 1.280 suspeitas): 29.132 mensagens elegíveis, 1.009 cortadas; 23.034 erros caem numa unidade e 7.107 ficam pendentes; 592,9 milhões de tokens nos erros. Um percalço no meio: o arquivo local do parquet apareceu com outro hash e não abria; restaurei a fonte e ela reproduziu o hash conferido. Com a fonte íntegra, a rodada real deu 10 candidatas a memória, 154 testes e 42 verificações passando. Limpei as cópias legadas da base 2 da pasta da base 3.

**Reflexão:** O mais importante do dia foi separar três coisas que antes eram duas: o que a regra explica (unidade), o que a regra não explica (resíduo) e o que a regra *poderia* explicar se o dado chegasse (pendente). Sem essa terceira categoria, o resíduo ficaria inflado de erros que a taxonomia já conhece e a limitação da extração ficaria escondida.

**Decisão/próximo passo:** Pendente não é resíduo. Nenhum destino de memória decidido numa base vale para outra: toda candidata da base 3 começa com o destino em aberto. Não existe taxa sem denominador. Testar com uma resposta conhecida.

**Tags:** base-3, adaptador, janelas, componentes, modo-observado, pendente-nao-e-residuo, sem-denominador, hash-da-fonte, candidatas, sub-2.2, sub-2.5

## 08/10/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Fechei a adaptação do código à base 3: adaptador, componentes, pipeline, mineração observada, execução e validação, com os sete arquivos de teste — 162 testes passando. Decidi deixar só a orquestração em Python: a lógica dos dois notebooks pequenos virou tabelas gravadas pela própria rodada, com uma entrada única (`executar.py analisar`, `validar`, `conferir`). A validação deixou de depender de resultados de rodadas antigas, que eu tinha apagado. Rodei a rodada oficial: 46 verificações, 10 candidatas, igual à de 07/10.

Teste com resposta conhecida: reescrevi em Python a query da base 3 e passei a base 1 (trace completo) por ela. A extração reproduz a população (5.781 ActionSteps, 498 erros). Erro a erro contra o pipeline da base 1: 415 na mesma unidade, 83 pendentes (81 do retorno-dict pelo corte de 20.000 caracteres, 1 do retorno-string, 1 por histórico) e **nenhum em unidade errada**.

Achado: o filtro de tamanho da query soma três textos; no SQL, um texto nulo torna a soma nula e a execução sai da base. Na base 3, 20.971 das 20.986 execuções com erro têm resposta final gravada; na base 1, só 34 de 318. Pode ser que a extração tenha cortado as execuções sem resposta. Não tenho acesso ao Athena para conferir.

Escrevi do zero os documentos da base 3 (racionais, relatório da rodada, procedimento de validação com as oito limitações medidas, roadmap).

**Reflexão:** Os 5.818 erros de nome não definido sem passo anterior identificado pedem cuidado: a hipótese de que seriam todos o primeiro passo do papel, e de que cairiam em "nome inventado", era dedução e não fato. O que está provado é só a estrutura da extração; a proporção real e a causa só saem de contagens na própria base 3 e da leitura de casos. Aprendizado de método: nada sobre a base 3 sem contagem tirada dela.

**Decisão/próximo passo:** Os 5.818 continuam pendentes até a investigação. Montar um painel de apresentação e o pedido de dados ao tutor.

**Tags:** base-3, teste-com-resposta-conhecida, query-v1, sem-notebooks, orquestracao, 162-testes, filtro-nulo, limitacoes, docs-base-3, sub-2.2, sub-2.5

## 09/10/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Montei o painel da rodada (`executar.py painel`): um markdown com o resumo, a cobertura, a triagem e as figuras, tudo gerado dos CSVs da rodada com o hash de cada arquivo conferido, e só com contagens. Acrescentei sete gráficos de leitura, cada um com a pergunta que responde, como ler e a limitação: para onde vão erros e tokens, frequência × custo por erro, concentração de cada candidata por papel, quais papéis concentram os erros, linha do tempo por mês, o que vem depois do erro e onde estão os pendentes. Escrevi o pedido de dados complementares ao tutor, só descrevendo o que trazer, sem SQL: (A) uma linha por execução, agente e papel com todos os passos e tokens (os denominadores), (B) um complemento só das linhas com erro que fecha os pendentes de cada motivo, (C) ajustes na extração de erros. Atualizei o roadmap com o que foi feito e o que falta.

Leituras da rodada real da base 3: 76% dos erros caem numa unidade e 24% ficam pendentes; o resíduo é 1,8%, abaixo do alarme de 5%; as dez candidatas somam 61% dos tokens dos erros; o erro de protocolo (resposta sem bloco de código) aparece em 4.030 das 20.986 execuções com erro; cada candidata se concentra em poucos papéis.

**Reflexão:** Os tokens por erro mostram que o ranking por tokens mede onde o erro acontece (o contexto acumulado do passo), não a gravidade. O retorno-string e o argumento nomeado têm quantidade parecida de erros e um custo por erro cerca de três vezes diferente (perto de 39 mil contra 13 mil tokens). Antes de levar isso ao tutor, quero confirmar com a conta de tokens de entrada e de saída.

**Decisão/próximo passo:** Rodar o painel completo e só então atualizar o relatório com as leituras. Levar ao tutor o painel e o pedido de dados; o que mais pesa é o denominador por papel — sem ele não dá para separar "este papel erra mais" de "este papel roda mais".

**Tags:** base-3, painel, graficos, pedido-de-dados, denominadores, pendentes, protocolo-do-harness, custo-por-erro, relatorio-tutor, sub-2.2, sub-2.5
