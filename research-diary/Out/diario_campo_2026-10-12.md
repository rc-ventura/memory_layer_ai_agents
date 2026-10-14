# Diário de Campo — Rafael Coelho Ventura

## Semana de 12/10 a 16/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 13/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Eu fiquei finalizando as pendências dos 24% da última análise da base 3. Tínhamos 7.107 erros sem classificação (24%), dos quais mais de 5 mil (5.818) eram erros de nome não definido. Descobrimos uma coisa bem valiosa: grande parte desses erros, que nossa análise colocava em um bucket de pendência, estava relacionada com um sinal de harness. Eu explico como encontramos isso.

Inicialmente, ao classificá-los, vimos que eles tinham o mecanismo de nome não definido e que, por estarem no primeiro passo, seriam classificados como nome_inventado. Esse mecanismo é quando o agente usa uma variável, por exemplo X, que nunca definiu. Então existem, dentro da mesma família, alguns mecanismos distintos: se ele chamou uma variável que não existia e isso aconteceu como um step inicial, ou essa variável não existia nos steps anteriores, o mecanismo é classificado como nome_inventado. Quando o step anterior deu algum erro (a linha de código levantou alguma exceção), a variável que ele criaria não chegou a ser definida e mesmo assim o agente assume que ela já foi definida, temos o mecanismo perda de estado da variável (estado_perdido).

No entanto, esses erros investigados tinham uma outra causa. Eles aconteciam sempre em um step inicial, onde a variável não tinha sido vista, então poderia ser um nome_inventado, mas os erros propriamente ditos tinham uma outra característica: parecia uma inversão de linha de código, ou seja, a variável não existia mas era definida depois de ele chamar a tal variável. O agente deveria definir e depois chamá-la, mas chamava e depois definia. Após isso ele ajusta e acerta. Então acreditávamos que poderia existir um novo mecanismo relacionado apenas à ordem de escrita do código. Essa leitura se mostrou errada (ver Reflexão).

Ao investigar melhor, vimos que quase todos esses erros eram de apenas um papel, o agente ContestacaoCivel (5.762 dos 5.764 com a assinatura), e que ele errava frequentemente em um único mês, agosto (5.667; julho tem 95). Ao investigar o system prompt (na base 2, que traz o prompt) vimos que o erro estava relacionado a uma diretiva do prompt: para verificar se uma variável já existe (e pular a chamada da ferramenta se ela já estiver preenchida), usar try/except com NameError, a exceção que o Python levanta para um erro de variável inexistente. No entanto, esse try/except não era corretamente tratado, pois o erro levantado dentro do sandbox não era NameError, e sim InterpreterError. Por isso, o agente, ao executar estritamente as ordens do prompt, verificava a variável com try/except; se ela não existisse, o erro deveria ser capturado, mas isso não acontecia e o erro era levantado. O próprio agente, em um comentário no código do passo seguinte, dizia que não ia mais usar o try/except ("para evitar o erro do interpretador"), definia a variável sem usar esse bloco e consertava o workflow (nos três casos que li). Reproduzi o comportamento num interpretador de teste: `except NameError` falha quando a variável ainda não existe; `except Exception` e a chamada direta funcionam.

Assim percebemos que esses erros eram candidatas a memória, mas deveriam ter seu destino como não-memória e sim como sinal de harness: um sinal para monitoramento. Principalmente porque um ajuste de harness pontual poderia ser mais efetivo do que injetar uma lição.

Aplicado como Ajuste 17 (13/10): nova unidade `U_verificacao_try_nameerror` (5.764 erros, 5.442 execuções, 112 milhões de tokens), com destino harness. Na rodada nova (14/10) os pendentes caíram de 7.107 (24%) para 1.803 (6%); 28.338 erros observáveis (94%).

**Reflexão:** A hipótese de "inversão de linha / ordem de escrita" era uma leitura da contagem, não da causa: o que a contagem pegava era o `try: variável` seguido de `except NameError`, e a "chamada antes da definição" é a própria verificação de existência. O mecanismo deixou de ser "nome usado antes de ser definido" e passou a ser "verificação de existência por try/except NameError, instruída pelo prompt, que o ambiente não suporta". Outro efeito: 460 desses erros (334 em estado_perdido, 126 em nome_inventado) estavam em unidades de memória só pela posição do passo anterior, e inflariam o cartão de memória de unidades cuja lição não preveniria esse erro. O que ainda não está provado: a evidência do prompt é da base 2 (a base 3 não tem o prompt), e a assinatura na base 3 só prova o padrão, não que o prompt o instruiu; julho já tem 95 erros com a mesma assinatura, então o problema não nasceu em agosto, só explodiu nele. Também não sei se o parágrafo da instrução já existia no prompt de julho. Os 514 erros do primeiro passo sem a assinatura são outro mecanismo (quase todos RoteadorCivel e RespostaBacen, por dedução).

**Decisão/próximo passo:** O destino desta unidade é o harness (corrigir a instrução do prompt ou o interpretador), não uma lição de memória. O registro de monitoramento ainda não foi escrito e o aviso a quem cuida do harness ficou adiado. Pedir o hash do trecho do prompt no pedido de dados à base 3 para fechar a questão do prompt lá. Fechar os pedidos de dados ao tutor.

**Tags:** base-3, sinal-de-harness, try-except-nameerror, interpretererror, sandbox, nome-inventado, estado-perdido, pendentes, ajuste-17, contestacaocivel, system-prompt, sub-2.2, sub-2.5
