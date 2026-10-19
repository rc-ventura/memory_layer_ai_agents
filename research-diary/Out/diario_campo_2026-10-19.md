# Diário de Campo — Rafael Coelho Ventura

## Semana de 19/10 a 23/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 19/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Fechei o piloto de mineração da primeira unidade de memória, o inventário do sandbox (`U_sandbox`, base 3). Com apoio de um agente (sem provider definido), o caminho foi: rodar a mineração de ponta a ponta com scripts determinísticos, comparar cada número com uma auditoria independente e investigar a origem dos erros antes de decidir o destino de cada parte. Resultado na rodada `aedb9b5db70d6c92`: 1.401 erros, cobertura de 99,6%, 75 medidas iguais à auditoria e 14 memórias no esquema 0.3 (2 globais e 12 por papel), todas registradas num catálogo novo, versionado.

Os achados, em ordem:
1. **O sandbox é um inventário com quatro causas diferentes**, não uma lição só: (C) módulo usado sem import, 656 erros; (B) ferramenta importada como se fosse biblioteca, 212, quase tudo num papel; (D) import fora da lista autorizada, 40, com uma lista diferente por papel; (E) funções e atributos proibidos, 488.
2. **A mesma instrução do prompt do ContestacaoCivel ("verifique se a variável já existe") produz três sintomas**, conforme o que o agente tenta: `globals()` quando o prompt não diz como; `try/except NameError` quando o prompt diz como; e `eval` dentro de uma função auxiliar escrita pelo agente. O sandbox barra os três. Por isso o erro não é uma lição de memória: o conserto é no prompt (harness). Isso moveu 2.217 erros (Ajuste 21) e depois 35 (Ajuste 23) para a unidade da verificação de existência; o sandbox foi de 3.653 para 1.401 erros.
3. **A parte E mistura duas causas.** Cerca de um terço é a mesma verificação, feita com `eval` ou com valor padrão. O resto é hábito do agente: inspecionar o retorno das ferramentas com `type(x).__name__` e `repr(x)`. Nenhum prompt pede isso, e outros papéis fazem o mesmo; é memória ("use `print(type(x))` e `print(str(x)[:n])`").
4. **Contrafactual útil:** quando o ContestacaoCivel não verificou nada e escreveu direto, não teve erro. A instrução custa mais do que o erro que ela evita.

**Reflexão:**
- A unidade se define pela causa e pelo conserto, não pelo sintoma. Três sintomas com a mesma causa e o mesmo conserto são uma lição só; um grupo de sintomas com duas causas são duas lições. Foi a lição metodológica do dia.
- Hipótese (não provada): o `eval` cresceu em agosto, quando o prompt passou a proibir `globals()` e `locals()`. Pode ser o agente contornando o caminho fechado. O corpo da função auxiliar não aparece nos dados, só a chamada, então o uso do `eval` por dentro dela é inferência; vale como no Ajuste 21. Na base 2 a parte E tem só 7 erros, então ela sustenta pouco a conclusão de que nenhum prompt pede essas funções.
- A divisão em depuração × verificação saiu de regras sobre a linha que falhou. Não li os casos um a um.
- O que mais protegeu o resultado: a auditoria independente. Quando a máquina da base rodou com uma versão antiga da auditoria, o encontro divergiu em exatamente 35 erros, que são o efeito do Ajuste 23. A divergência apontou a versão desatualizada. Outro sinal: a rodada saiu com o mesmo identificador de antes, o que mostra código antigo, porque o identificador é uma impressão digital do código.
- O validador do script reprovou duas vezes. Em ambas, o script seguia regras de montagem que o racional não declarava. O racional funciona como contrato; o script não pode saber mais do que ele.

**Decisão/próximo passo:** Registrada a pendência `b3 #48`: seis das 14 memórias têm de 1 a 3 erros. Decidir se aplico a régua de "memória rara" (pelo menos 3 execuções em 2 meses) para separar o que entra no experimento do que só fica em monitoramento. Próximo: a segunda unidade de memória e a apresentação de sete slides, que pode usar este piloto no slide 5 (os principais erros, com dossiê) e no slide 6 (do erro à memória).

**Tags:** base-3, sandbox, u-sandbox, mineracao, memoria, harness, verificacao-existencia, contestacaocivel, eval, globals, try-except-nameerror, auditoria-independente, catalogo, ajuste-21, ajuste-22, ajuste-23, sub-2.2, sub-2.5

### 19/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Decisões tomadas hoje, todas registradas em `analysis/decisoes.md`:
- **Destino das partes do sandbox:** C vira memória global; B, memória do papel OBFCivel; D, memória por papel; E, memória global, depois de investigada.
- **Ajuste 21:** a introspecção usada para verificar se a variável existe, e que guarda a criação dela por uma chamada, vai para o harness. A leitura com valor padrão (`globals().get('x', padrão)`) fica no sandbox.
- **Ajuste 23:** o mesmo vale para o `eval` dentro da função auxiliar de verificação. O `eval(texto)` que converte texto em objeto fica no sandbox. Aprovei o formato estreito depois de ver que os outros papéis usam `eval` só para converter texto.
- **Ajuste 22:** uma lição pode ter várias memórias, uma por parte (esquema 0.3). As memórias fechadas entram num catálogo versionado (`analysis/registros/memorias.json`), com só conteúdo técnico e o hash do arquivo final. O arquivo completo continua na máquina da base.
- **Sigilo (opção 1):** o conteúdo técnico pode sair da máquina da base (identificadores, mensagens de erro, nomes de variável, contagens); dado pessoal e conteúdo do cliente não. A varredura continua obrigatória antes de qualquer saída.
- Aprovei o script do sandbox dividido em partes, depois de o validador independente conferir 114 de 114 medidas.

**Reflexão:** Decidi aos poucos, uma mudança de método por vez, cada uma com a evidência na frente. Isso deu trabalho, mas resolveu a dificuldade que anotei na sexta: voltar a entender por que cada passo foi dado. O livro-razão e o `decisoes.md` agora guardam o porquê.

**Decisão/próximo passo:** Escolher a próxima unidade do funil, pela ordem de tokens, e rodar o mesmo caminho (racional → script → auditoria → validador → catálogo). Montar os slides 5 e 6 com este piloto como exemplo.

**Tags:** base-3, decisoes, sigilo, catalogo, esquema-memoria, ajuste-22, metodo, sub-2.2
