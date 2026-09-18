# Meta-relatório independente — evidências 11.1 a 11.8

Data: 2026-09-17

## Escopo

Este meta-relatório consolida as auditorias independentes produzidas para as pastas `11.1_origem_do_erro/` até `11.8_registro_final/`. O objetivo é responder, em um único lugar, se a cadeia de validação do notebook mineracao_unidades_n2_n10.ipynb §11 se sustenta quando reaberta a partir do trace cru.

As leituras foram feitas com base nos `crus/*.json` de cada pasta de evidência, usando `casos.csv`, `leia-me.md`, `unidades_memoria.json` e os documentos de método apenas como índice e referência interpretativa.

## Relatórios consolidados

- `11.1_origem_do_erro/relatorio_independente.md`
- `11.2_schema_real/relatorio_independente.md`
- `11.3_prompt_declara/relatorio_independente.md`
- `11.4_conserto/relatorio_independente.md`
- `11.5_estabilidade/relatorio_independente.md`
- `11.6_status/relatorio_independente.md`
- `11.7_amostra_passo6/relatorio_independente.md`
- `11.8_registro_final/relatorio_independente.md`

## Veredito consolidado

### Síntese curta

A cadeia 11.1–11.8 ficou, no conjunto, **bem sustentada** pela auditoria independente. Não apareceu nenhuma pasta que contradissesse frontalmente o que o notebook/publicação afirma. O quadro consolidado é:

1. **Passo 1 (origem do erro)**: sustentado; as atribuições positivas conferem e os `não resolvido` permanecem cautelas justificadas.
2. **Passo 2 (schema real)**: sustentado; quando o objeto aparece na mensagem, a forma registrada bate com o cru, e quando não aparece a categoria `objeto não lido` é apropriada.
3. **Passo 3 (o que o prompt declara)**: sustentado e importante; separa corretamente **prompt contraditório** de **prompt omisso**.
4. **Passo 3b / conserto**: sustentado; o step seguinte realmente contém os padrões de correção que o notebook classificou.
5. **Passo 4 (estabilidade)**: sustentado; os schemas das candidatas são estáveis por nível da estrutura, com uma única variação de “campos a mais” em ago/2026 para `get_available_documents`.
6. **Passo 5 (status/cobertura)**: sustentado no estado final dos artefatos; a pasta 11.6 ficou vazia porque o resíduo foi fechado, o que bate com os docs.
7. **Passo 6 (amostra humana)**: sustentado; a amostra 11.7 confirma diretamente no cru as interpretações centrais das duas candidatas.
8. **Passo 8 (registro final)**: sustentado na parte auditável; `location`, `evidence` e os casos escolhidos batem entre si e com os crus.

## O que cada pasta validou

| pasta | pergunta validada | resultado independente |
|---|---|---|
| `11.1_origem_do_erro` | de qual função/ferramenta vem o erro? | **confirma** 7/7 atribuições positivas; mantém 5/5 `não resolvido` |
| `11.2_schema_real` | qual é o schema real impresso na mensagem? | **confirma** 6/6 objetos parseáveis; 4/4 `objeto não lido` corretos |
| `11.3_prompt_declara` | o prompt declara a chave certa, errada ou nenhuma? | **confirma** `validar_quebra_sigilo` e `extrair_evidencias` como contraditórios; `get_available_documents` como omisso |
| `11.4_conserto` | o que o agente faz depois do erro? | **confirma** os 3 tipos de conserto; 4/5 passos seguintes sem erro, 1/5 com erro novo posterior |
| `11.5_estabilidade` | a forma é estável ao longo dos meses? | **confirma** estabilidade; 1 variação com campos extras nulos em ago/2026 |
| `11.6_status` | a cobertura/resíduo fecha? | **confirma** consistência do artefato final: resíduo real = 0, por isso pasta sem casos |
| `11.7_amostra_passo6` | a leitura do cru numa amostra cega confirma os achados? | **confirma** os dois mecanismos centrais; nota adicional: erro de `draft_resposta` aparece em 1/10 caso |
| `11.8_registro_final` | os casos citados no registro final batem com `location` e com o cru? | **confirma** `evidence = 3 primeiros casos de location` para as 2 candidatas |

## Achados integrados por mecanismo

### 1. Candidata nº2 — `(ConversationAgent, get_available_documents)`

A leitura consolidada das pastas 11.1, 11.2, 11.3, 11.4, 11.5, 11.7 e 11.8 converge para o mesmo mecanismo:

- o retorno real relevante é um **dict** cujo topo traz `result`;
- em vários erros, o agente trata o retorno como se fosse lista (`r[0]`) ou desce um nível a mais (`r['result'][0][0]` e depois itera como se ainda fosse lista de documentos);
- o prompt da ferramenta **não declara explicitamente** o envelope `result`, mas descreve “documentos + summary”, o que deixa margem para inferência errada;
- quando o agente corrige, o acesso mais estável observado é `r['result'][0]`.

### 2. Candidata nº10 — `(RespostaBacen, validar_quebra_sigilo)`

A leitura consolidada das pastas 11.1, 11.2, 11.3, 11.4, 11.5, 11.7 e 11.8 converge ainda mais fortemente:

- o retorno real é `{justificativa, vazamento_sigilo}`;
- o prompt da ferramenta declara `{quebra_sigilo, motivo}`;
- o agente, nos casos auditados, **segue o prompt** e pede `quebra_sigilo`;
- o step seguinte costuma descobrir a chave real e trocar para `vazamento_sigilo` ou usar `.get(...)` para aceitar os dois contratos.

Aqui a evidência é mais forte do que na nº2 porque há **contradição explícita de contrato** entre prompt e runtime, não só omissão.

### 3. Subunidade de 1 caso — `extrair_evidencias`

Embora não seja candidata recorrente no Passo 1, ela aparece de forma relevante nas auditorias:

- o prompt declara `informacoes_evidencias`;
- o retorno real auditado traz `dados_evidencias`;
- o agente pede a chave do prompt e depois corrige para a chave real.

Ou seja, o mesmo padrão de **prompt contraditório** existe aqui, mas sem recorrência suficiente para virar candidata como as duas principais.

## O que ficou mais forte depois da auditoria independente

### A. A distinção “prompt contraditório” vs “prompt omisso” não é retórica

Ela ficou confirmada diretamente no cru:

- **contraditório**: `validar_quebra_sigilo`, `extrair_evidencias`;
- **omisso**: `get_available_documents`.

Isso importa porque muda a interpretação causal do erro:

- se o prompt contradiz o runtime, o agente pode estar simplesmente obedecendo à instrução errada;
- se o prompt é omisso, o erro depende mais da inferência estrutural do agente sobre o retorno.

### B. A correção do agente é observável e informativa

Os passos seguintes ao erro, auditados em 11.4 e amostrados de novo em 11.7, mostram que o agente frequentemente:

- lê a chave real no log/erro do próprio step;
- atualiza o acesso no step seguinte;
- às vezes escreve um conserto mais robusto, aceitando dois contratos (`.get`) ou guardando o tipo.

Isso fortalece a ideia de que o registro final não está “inventando” o `correction_guidance`; ele o deriva de padrões reais de autocorreção.

### C. O schema das duas candidatas é estável o suficiente para virar guidance

A auditoria de 11.5 e a validação por amostra de 11.7 mostraram que:

- `validar_quebra_sigilo` é estável nos meses observados;
- `get_available_documents` também é estável no nível relevante, com uma única variação por campos extras simples e nulos.

Isso dá base empírica para transformar a leitura em guidance reaproveitável.

## Limites e ressalvas

1. **11.6 é diferente das outras pastas.** Ela valida o estado final do artefato, não reabre casos, porque hoje não há mais crus nela.
2. **A nº10 ainda mantém uma questão conceitual em aberto** já registrada nos docs: como o conserto contradiz o próprio system prompt, o destino “memória × harness” segue pendente.
3. **O erro de `draft_resposta`/assunto inválido não deve ser generalizado.** Ele apareceu em 1 caso da amostra 11.7 (`9be7b413…`), como fenômeno local, e não como explicação da subunidade inteira.
4. **Os relatórios independentes validam a cadeia observável**, não um replay contrafactual completo. Eles mostram que os artefatos batem com o cru; não provam sozinhos que um prompt corrigido evitaria todos os erros.

## Conclusão final

No conjunto, a auditoria independente **valida a espinha dorsal da seção 11** do notebook e dos achados publicados:

- a origem dos erros foi atribuída de forma defensável;
- o schema real foi lido corretamente quando o erro o expôs;
- o conteúdo do prompt foi distinguido corretamente entre contradição e omissão;
- os consertos escritos pelo agente foram classificados de forma fiel;
- a estabilidade temporal das duas candidatas se sustenta;
- o fechamento do resíduo é coerente com os artefatos finais;
- a amostra humana confirma os mecanismos centrais diretamente no cru;
- e o registro final está bem ancorado em casos reais, com `location` e `evidence` coerentes.

Se eu tivesse que resumir em uma frase: **as auditorias independentes não encontraram uma ruptura importante na cadeia 11.1–11.8; ao contrário, elas reforçaram que os dois mecanismos candidatos estão bem identificados, com força maior para `validar_quebra_sigilo` do que para `get_available_documents`.**
