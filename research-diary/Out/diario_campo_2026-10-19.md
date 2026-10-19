# Diário de Campo — Rafael Coelho Ventura

## Semana de 19/10 a 23/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 19/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Fechamos o piloto de mineração da unidade do sandbox (base 3). O inventário tinha 3.653 erros de sandbox; ficaram 1.401 no sandbox, e a unidade virou 14 memórias, registradas num catálogo versionado. O que descobrimos:

1. **A unidade nasce do sintoma; a lição se define pela causa raiz e pelo conserto.** Achávamos que a unidade do sandbox era só "o agente chama comandos ou bibliotecas proibidos". Isso se confirmou, com adendos: a maior parte dos erros vinha do ContestacaoCivel, e o mesmo sintoma tinha causas diferentes. Dividir a unidade quando ela junta causas é um resultado normal (procedimento da mineração). Na hierarquia: família "Ambiente & sandbox" → assinatura "Função ou import bloqueado pelo sandbox" → unidade "Inventário do sandbox".
2. **A maior parte dos erros virou sinal de harness (2.252 dos 3.653, cerca de 62%).** O prompt do ContestacaoCivel tem duas versões. A antiga só diz algo genérico, "verifique se a variável existe", sem dizer como; o agente decide sozinho e em geral usa `globals()`. A nova diz para usar `try/except` e não usar `globals()`. Resultado: três sintomas — `globals()`, `try/except` e `eval` dentro de uma função auxiliar escrita pelo agente. Antes, `globals` e `eval` estavam no sandbox e o `try/except` tinha unidade própria; juntamos os três na unidade da **verificação de existência** (a antiga unidade do `try/except`, renomeada). As duas formas, a genérica e a explícita, acabam bloqueadas pelo sandbox (no `try/except`, o erro de variável inexistente sai do alcance do `except`). Por isso o destino é harness: o conserto é no prompt ou no interpretador. Só a verificação saiu para outra unidade; o resto continua no sandbox, dividido em partes.
3. **O resto é hábito do agente, e vira memória**, porque o prompt não pede nada disso: (C) esquecer o import de `json` ou `pd`, 656 erros; (B) importar uma ferramenta como se fosse biblioteca, 212, quase tudo no OBFCivel; (D) importar fora da lista autorizada, 40; (E) funções e atributos proibidos, 488, sobretudo depuração do tipo `type(x).__name__` e `repr(x)` sobre o retorno das ferramentas. Uma memória injetada poderia mitigar esses erros.
4. **Memória global e memória por papel.** C e E valem para qualquer papel. B é por papel porque quase todo o erro está num papel só. D é por papel porque cada papel tem a sua lista de imports autorizados: são 6 listas diferentes em 16 papéis, e cada memória D leva a lista do seu papel. O catálogo (`analysis/registros/memorias.json`) registra as 14 memórias.
5. **Observação:** as execuções do ContestacaoCivel que escrevem direto, sem verificar a variável, terminam sem esse erro.
6. **Possível contorno:** com `globals` proibido no prompt, o agente pode estar validando a variável com `eval`, que o sandbox também bloqueia.

**Reflexão:**
- A observação 5 é consistente com o prompt induzir o erro, mas não prova: execuções que não verificam podem ser casos mais simples. A evidência mais forte é a troca de versão do prompt.
- O contorno com `eval` é hipótese. O `eval` já aparecia em julho (15 erros), antes de o prompt proibir `globals`, e foi para 31 em agosto. O uso do `eval` dentro da função auxiliar é inferência: os dados mostram a chamada, não o corpo da função. A base 3 não tem o prompt; o prompt foi visto na base 2 e no de julho da base 1.
- Só o `eval` que verifica a variável e a cria chamando uma ferramenta foi para o harness. O `eval(texto)`, que converte texto em objeto, continua como memória.
- Pergunta aberta: umas 134 verificações com valor padrão (`if 'x' not in globals(): x = '…'`) continuam como memória, no grupo E, mas provavelmente têm a mesma causa do prompt.
- O destino "memória" de C, B e D foi decidido sem ler os prompts desses papéis; só o grupo E foi testado contra prompts, e fracamente (na base 2 ele tem só 7 erros).
- As 14 memórias foram construídas, não testadas. A redução dos erros só se mede no teste de compensação (`b3 #39`).

**Decisão/próximo passo:** Destinos decididos: a verificação de existência vai para o harness; C e E viram memória global; B e D, memória por papel. Pendência `b3 #48`: seis das 14 memórias têm de 1 a 3 erros; decidir se aplico a régua de "memória rara" antes de usá-las no experimento. Próximo: a segunda unidade de memória e a apresentação de sete slides, com este piloto nos slides 5 e 6.

**Tags:** base-3, sandbox, mineracao, memoria, harness, verificacao-existencia, contestacaocivel, eval, globals, try-except-nameerror, catalogo, memoria-por-papel, sub-2.2, sub-2.5
