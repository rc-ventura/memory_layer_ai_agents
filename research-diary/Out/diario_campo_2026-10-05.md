# Diário de Campo — Rafael Coelho Ventura

## Semana de 05/10 a 09/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 05/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 1.5 — **Canal:** formal-tutor

**Registro objetivo:** Dia de fechar tudo pra rodar a base 3 amanhã. A base 3 não é "mais uma amostra": são todos os traces consolidados, a nossa fonte da verdade. As bases 1 e 2 serviram pra sedimentar e discutir o método; o que sai delas é o que vamos aplicar na base 3. Fechei a base 2 com a segunda rodada (o agente da outra máquina respondeu as seis perguntas que estavam abertas) e o resultado mais importante foi: nenhum sucesso falso confirmado — nos 24 candidatos, a resposta final declara a falha. Também confirmamos que o "campo inexistente" da base 2 nasce do prompt (ele pede `quebra_sigilo` e a ferramenta devolve `vazamento_sigilo`, 38 de 38 com a chave errada no próprio prompt), igual à base 1, e decidi que ele vira sinal de harness nas duas bases. E a maior candidata da base 2, "nome usado sem ter sido definido", tá concentrada num papel, num mês e num modelo só — cara de incidente, não de lição. Com um agente (sem provider definido) implementando, a branch da consolidação ficou pronta pra fechar.

Até quinta que vem tenho reunião com o meu tutor, e ficou decidido que vou apresentar um relatório concreto das unidades de memória mineradas: formato de equipe técnica, mas com linguagem palatável pra gerência. A mensagem é mostrar que o projeto faz sentido: temos X erros, essas unidades de memória mitigariam parte deles, e isso tem um valor em dinheiro.

Pra isso quero fechar a fundamentação e criar skills específicas, pra ter reprodutibilidade sem ficar repetindo prompt: uma pra mineração de unidade de memória (como fizemos com as unidades nº2 e nº10 na base 1), uma pra minerar o resíduo (como nas bases 1 e 2), uma pra erros críticos, uma pra erros de protocolo do harness e uma pras falhas silenciosas. Assim as análises ficam padronizadas.

**Reflexão:** O grande achado da semana passada foram os erros silenciosos: a ferramenta falha e o step não loga o erro. Mas a minha preocupação principal é outra: quando a ferramenta falha, o agente precisava daquele retorno pra seguir o fluxo e entregar uma resposta final completa e certa? Se precisava e entregou mesmo assim, é sucesso falso — e isso seria um medidor muito importante pro Update Engine da arquitetura de memória. Quero achar um jeito determinístico de medir, nem que precise de LLM só pra parte semântica (aí marcado como leitura assistida, fora do caminho de classificação, que continua sem LLM). A base 2 já ensinou uma coisa: tem um terceiro desfecho no meio — a resposta que **declara** a falha. Ela não mente, mas também não entrega a tarefa completa. Então o meu medo se divide em dois: resposta errada (sucesso falso) e resposta incompleta (falha declarada).

Isso puxa a definição de sucesso. A ideia é um sucesso em três níveis (o step rodou sem exceção · a ferramenta devolveu resultado · a tarefa terminou com resposta final), mas ainda falta o racional, porque um step de sucesso pode ter chamada de ferramenta com erro, e terminar com resposta final não garante que a resposta saiu completa. Provavelmente o terceiro nível precisa separar "terminou" de "terminou com o conteúdo que a tarefa pedia" — e essa última parte é semântica.

Sobre contar o mesmo erro duas vezes agora que temos dois baldes: o mesmo step nunca entra nos dois (o funil separa por step; conferido, zero nas duas bases), e a consolidação conta execuções pela união. O que ainda pode acontecer é o mesmo episódio aparecer nos dois canais em steps seguidos (uma falha silenciosa e logo depois um erro visível, com a mesma causa) e virar duas ocorrências. Na unidade que juntamos ("colar o print"), isso deu zero nas duas bases, mas não existe regra pra isso em geral. Tá registrado no plano.

E vimos que parte dos erros nasce do prompt do agente e de documentação de ferramenta ambígua, como a `resposta_final`, que compete com o `final_answer` do framework. Isso não é memória: é sinal de harness.

**Decisão/próximo passo:** Fechar a branch da consolidação e abrir uma nova pra discutir as medidas (o que de fato queremos medir em cada uma, antes de implementar). Preparar a leitura do parquet pra base 3 — hoje o código não lê parquet. Criar as skills de mineração, resíduo, erro crítico, protocolo do harness e falhas silenciosas. Montar o relatório pro tutor, tomando cuidado com o número em dinheiro: o que o trace dá é o custo dos erros que caem em unidades candidatas (um teto); a economia de verdade depende de quanto a memória evita, e isso só um teste mede.

**Tags:** base-3, fonte-da-verdade, base-2-finalizada, sucesso-falso, falha-declarada, sucesso-em-tres-niveis, update-engine, dois-baldes, dupla-contagem, sinal-de-harness, skills, relatorio-tutor, custo-dos-erros, parquet, sub-2.2, sub-1.5
