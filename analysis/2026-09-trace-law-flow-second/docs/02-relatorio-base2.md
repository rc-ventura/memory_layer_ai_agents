# Relatório da base 2 — reunido dos documentos onde os resultados estavam espalhados

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, [conferido]/[assistido]): o que cada um quer dizer
> está no [glossário](../../glossario.md). Índice da pasta: [README](../README.md). Backlog: [roadmap](04-roadmap.md).

**Data:** 09/10/2026 · **O que é este documento:** os resultados da base 2 num lugar só. **Nenhum número é novo e nenhum
foi recalculado**: cada um foi copiado do documento de origem, que vem indicado na própria linha. Em caso de
divergência, vale a origem. O texto original **não foi movido** — continua nos docs `10`–`14` da
[base 1](../../2026-09-trace-law-flow/docs/) e no livro-razão [`pipeline-entre-bases.md`](../../pipeline-entre-bases.md).

**Fonte dos dados:** a base 2 (lote de ago/2026, 1.000 registros, independente da base 1: `b1 #27`) roda no ambiente de
compliance; de lá só saem contagens, nomes de papel, ferramenta e modelo, hashes e sim/não. Os números abaixo vêm de
rodadas lá (29/09 a 05/10), recalculadas pelas funções do pipeline e conferidas pelo `audit_recompute9`, uma
implementação independente (0 divergências). **Limites da rodada:** os notebooks não foram reexecutados inteiros no
terminal (`b2 #1`), e as cópias levadas ao ambiente tinham hashes diferentes das do repositório (livro-razão, Etapa 10d);
o que sustenta os números é o `audit_recompute9`.

**Estado: finalizada (decisão do Rafael, 05/10/2026)** — com os itens abertos da §8.

---

## TL;DR

- **479 erros** com exceção em 3.907 ActionSteps; **16 unidades; 8 candidatas a memória** (370 erros, 77%), 1 crítico,
  3 não-memória (90 erros), 2 para revisar (9), 2 fora (9). *(livro-razão §6)*
- **A maior candidata é `U_nome_inventado`: 118 erros em 112 execuções** (na base 1, 5). Mas **101 deles são um papel
  (ContestacaoCivel), um mês (ago/2026) e um modelo**: cara de incidente, não de lição. Os 17 espalhados sustentam a
  candidatura. Ainda não foi minerada (`b2 #3`). *(Etapa 10d)*
- **O protocolo do harness é incidente de plataforma, causado por troca de modelo:** 69 erros, 61 em ago/2026; no
  RoteadorCivel, o modelo antigo teve 0 erros em 381 steps de agosto e o novo, 54 em 478. *(`11` §2)*
- **~87% das falhas de ferramenta são silenciosas** (134 contra 20 com exceção). **Nenhum sucesso falso confirmado:**
  nos 24 candidatos a resposta final **declara a falha**. *(`14`, Etapa 10d)*
- **O único erro crítico** (CalculoCivel, fev/2026) começa numa falha silenciosa da calculadora e termina em narração
  executada como código: 21 steps e 2,09 milhões de tokens só na chamada que morreu. *(`11` §2.5)*
- **O "campo inexistente" nasce do prompt:** 38 de 38 com a chave errada no próprio system prompt — sinal de harness,
  como na base 1 (Ajuste 13). *(Etapa 10d)*
- **O alarme de cobertura disparou (5,2%) por um padrão só** — o Timeout de ferramenta, 16 de 25 erros. Com os
  Ajustes 3, 4, 8 e 9, o resíduo caiu para 9 erros. *(Etapas 3, 4, 6)*

---

## 1 · A triagem da base 2

| | Base 2 |
|---|---|
| Erros | **479** |
| Unidades | 16: **8 candidatas** (370 erros, 77%), 1 crítico, 3 não-memória (90), 2 revisar (9), 2 fora (9) |
| Maior candidata | **`U_nome_inventado`** (118 erros, 112 execuções, 5 meses, 6 papéis) |
| `U_campo_inexistente` | candidata na triagem de 02/10 (38 erros, 2 papéis); **esperado depois do Ajuste 13: sinal de harness**, candidatas 8 → 7 e 370 → 332 erros cobertos — não conferido na base 2 (replicar no ambiente de compliance) |
| `U_repr_colado` | candidata: **18** erros em 18 execuções, 3 meses, só RoteadorCivel (o "7" antigo contava só o recorte do Ajuste 2.2) |
| Críticos | 1 (CalculoCivel, fev/2026, 49 steps, 25 erros antes, 1ª unidade `U_nome_inventado`) |
| Resíduo | 9 erros: 7 causa + 2 sintoma (antes dos Ajustes 3–9: 32) |
| Alarme de cobertura | 25/09: disparou (5,2%); depois dos Ajustes 3, 4, 8 e 9 o sintoma não reconhecido caiu para 2 erros — a reconferir na Etapa 6 |
| Balde invisível | 20 com exceção · 134 silenciosas (87%) · [4] 24/116 |

*Origem: livro-razão §6 (02/10/2026) e Etapa 10c, passo 1 da rodada de 02/10 (triagem recalculada pelas funções do
pipeline; coincide com o agregado gravado).*

### 1.1 Três unidades que a base 2 tornou diferentes da base 1

**`U_nome_inventado`** (a maior candidata, 118 erros). *(Etapa 10d)*
- 101 erros são **um papel (ContestacaoCivel), um mês (ago/2026), um modelo** (`gpt-5.2-2025-12-11`).
- 104 estão no 1º step da chamada; em 107 o nome só é definido depois; 1 vem de uma chamada anterior do papel; 1 vem
  logo depois de uma resposta sem bloco de código **[conferido]**.
- **Leitura (hipótese, não decisão):** incidente concentrado, como o do protocolo; os 17 restantes sustentam a
  candidatura. Também é a 1ª unidade do único erro crítico — conferir se é nome inventado, definição que expirou entre
  steps (`b1 #23`) ou narração executada como código (M6, `transversal #4`).

**`U_campo_inexistente`** (38 erros em 36 execuções; RespostaBacen e RespostaOficios). *(Ajuste 13, Etapa 10d)*
- **38 de 38 com a chave pedida no system prompt**; 31 são `quebra_sigilo` pedido ao retorno do `validar_quebra_sigilo`,
  que tem `justificativa` e `vazamento_sigilo` **[conferido, `investigacao_achados.py` seção C]**.
- O prompt declara um nome e a ferramenta devolve outro: o conserto é no contrato do prompt. **Decisão do Rafael
  (05/10):** `DESTINO_MINERACAO` aceita mais de uma base, e a unidade vale `("base1", "base2")`.

**`U_repr_colado`** — o gesto de colar o print de volta no código, nos dois canais. *(`14` §6, Etapa 10d)*

| | Visível | Silencioso | **Consolidada** |
|---|---:|---:|---|
| Ocorrências | 18 | 86 | **104 · 104 execuções**, 4 meses, 1 papel **[conferido, 05/10]** |

Os 18 visíveis estão na linha rejeitada que chama o `busca_obf` — o mesmo gesto dos 86 silenciosos, na mesma ferramenta.

---

## 2 · O protocolo do harness: incidente de ago/2026 = o modelo novo

*(Origem: `11` §2 e §3; livro-razão Etapa 10b. Racional dos mecanismos M1–M6: `10`.)*

| Bloco | Fato |
|---|---|
| total | **69 erros** |
| mês | **ago/2026: 61** (37,8 por 1k steps, 58 execuções); dez/2025 1, fev 4, abr 2, mai 1 |
| papel | **RoteadorCivel 56** (todos em ago); em ago também OBFCivel 4 e CalculoTrabalhista 1; fora de ago, CalculoCivel 4 (fev, 1 execução) e RespostaBacen 4 (3 meses) |
| forma | 67 texto sem marcador, 2 vazios; mediana **138 caracteres**, tokens de saída mediana **242** |
| recuperação | papel entregou resposta depois em 66/69; execução com resposta em 69/69 |
| cascata | 61 seguidos de step sem erro; 5 `U_estado_perdido`, 3 `U_texto_solto`; nunca repetiu |

**O modo não explica o surto; o modelo explica.** Todos os papéis com o erro rodam em modo texto o tempo todo (RoteadorCivel
e OBFCivel `168d70e2`; RespostaBacen, CalculoCivel e CalculoTrabalhista `b0f37eea`, o mesmo hash da base 1). Ninguém
mudou de modo; o RoteadorCivel usa a mesma versão de mai a ago (965 steps e 0 erros em mai–jul; 871 steps e 56 erros em
ago). O modelo:

| Papel | Modelo | Meses | Steps | Erros | Por 1k |
|---|---|---|---:|---:|---:|
| RoteadorCivel | `gpt-4.1-2025-04-14` | mai → ago (381 em ago) | 1.341 | 0 | 0 |
| RoteadorCivel | **`gpt-5.6-terra-2026-07-09`** | só ago | 478 | **54** | **113** |
| RoteadorCivel | (não registrado) | jul, ago | 17 | 2 | 118 |
| OBFCivel | `claude-sonnet-4-5` | abr → ago | 721 | 0 | 0 |
| OBFCivel | **`gpt-5.6-terra-2026-07-09`** | só ago | 22 | **4** | **182** |

Mesmo papel, mesmo mês, mesmo prompt, mesmo modo: o modelo antigo, 0 erros em 381 steps de agosto; o novo, 54 em 478.

**RoteadorCivel, 7 casos lidos (Rafael) e os metadados (30/09).** O texto visível é um **resto**: 150 a 300 tokens
gerados que não viraram texto. **M4** — o modelo novo gasta tokens de saída e entrega pouco ou nada (`finish = stop`);
causa mais provável, não comprovável com o que o trace grava, raciocínio interno. **M5** — quando o `content` vem vazio, o
harness roda um bloco vazio **sem erro**, e o erro aparece um step depois: **achado de harness** (aviso à plataforma). A
resposta não foi para outro campo, e o harness não perdeu nada: a API já entregou curto ou vazio. Os 7 recuperam no step
seguinte. A causa dos tokens gastos é hipótese.

**RespostaBacen, 4 erros (leitura assistida, 02/10).** `o4-mini`, `b0f37eea`, modo texto. **M1 em 3** (JSON do negócio
×2 e pergunta ao usuário, os 3 com a declaração `resposta_gerada` e o prompt pedindo formato). **M2 em 1**: dez/2025,
logo depois do `resposta_final`, com o contrato antigo `json_resposta`. O M2 **não** reapareceu com o contrato atual: é
sinal de harness já corrigido pela plataforma, não vira memória.

**M1 medido (`protocolo` [9], 02/10)** — antecipou a resposta final (≥ 50%) / mediana / copiou da observação anterior:

| Papel | Erros | Antecipou | Mediana | Copiou da observação |
|---|---:|---:|---:|---:|
| RoteadorCivel | 56 | 0/56 | 0% | 0/56 |
| OBFCivel | 4 | 0/4 | 0% | 0/4 |
| CalculoCivel | 4 | 0/4 | 0% | **3/4** |
| RespostaBacen | 4 | **2/4** | 56% | 1/4 |
| CalculoTrabalhista | 1 | 0/1 | 32% | 0/1 |

O surto de ago/2026 **não é M1**; o RespostaBacen é o único com sinal de M1 (o 3º caso lido é a pergunta ao usuário, de 496
caracteres, o falso negativo conhecido da medida).

**Conclusão:** protocolo do harness na base 2 = **plataforma (o modelo novo)**. Sem lição aprendida (o agente se
recupera no step seguinte; o conserto é modelo ou modo), sem sinal de harness no sentido do projeto. **Um achado de
harness:** o harness aceita o `content` vazio sem erro (M5). Nos 13 erros dos outros papéis, os mecanismos M1/M2 da base 1
não foram verificados, exceto no RespostaBacen. **Não-memória, com evidência própria.**

---

## 3 · O único erro crítico: CalculoCivel, fev/2026

*(Origem: `11` §2.5; livro-razão Etapa 10d.)* A execução tem **4 chamadas** do papel, não uma tentativa contínua — o `idx`
as junta e o `step_number` recomeça a cada uma **[conferido: 4 `TaskStep`]**.

| Chamada | idx | Steps | Erros | Como terminou |
|---|---|---:|---:|---|
| 1 | 0–16 | 17 | 9 | `final_answer` |
| 2 | 17–19 | 3 | 0 | `final_answer` |
| 3 | 20–27 | 8 | 5 | `final_answer` (a mensagem de que o cálculo não pode ser feito para a data pedida) |
| **4** | **28–48** | **21** | **11** + o limite | **`AgentMaxStepsError`, sem `final_answer`** |

**A cadeia que matou a 4ª chamada:**
1. **idx 28 — a calculadora falha em silêncio:** `calculo_correcoes_monetarias` devolve a string
   `"Error calling tool … 'DEFAULT'"` no lugar do `dict` declarado; a falha volta como **valor**, o step fica com
   `error: null` **[conferido]**. Nas 5 chamadas da ferramenta: 4 devolvem esse texto. O que é o `DEFAULT` não se fecha
   pelo trace.
2. **idx 29–30** — o agente imprime as tabelas e responde em texto sem `<code>`: erro de protocolo (**M1**).
3. **idx 31–46** — narração capturada como código (**M6**): o agente escreve que o código deve ficar entre `<code>` e
   `</code>`, e a regex do harness extrai e executa isso **[conferido: a reprodução da regex bate nos 12 steps]**. Os erros
   resultantes recebem os rótulos `U_estado_perdido`, `U_nome_inventado`, `U_texto_solto` e `X_causa_nao_identificada`;
   **não** são perda de estado nem nome inventado.
4. O agente diagnostica errado e repete; **nenhum step da 4ª chamada chama o `final_answer`.**
5. **idx 48 — limite de passos.**

**Custo da 4ª chamada:** ~2,09 milhões de tokens e ~8,8 min **[conferido]** — mais que as outras três somadas. **Leitura
retirada (01/10):** "4 ciclos do mesmo loop", "morte por acúmulo de 25 erros" e "o passo crítico é o idx 20" — o cru
mostrou 4 chamadas e a cadeia terminal começando no idx 28 e no 30.

**O que muda:** é a primeira exceção ao "o agente se recupera no step seguinte"; o protocolo aparece **no meio de uma
cadeia**; contar só o `H_bloco_code` subestima a família, porque os efeitos do M6 aparecem como erros de execução com
rótulos de memória. **Em aberto:** o que a 4ª tarefa dizia; o `DEFAULT`. A investigação do crítico → `transversal #5`.

---

## 4 · As falhas silenciosas (o balde invisível)

*(Origem: `14`; racional `13`; procedimento `15`; `audit_recompute9` rodado no ambiente da base 2, 02/10.)*

| | Base 2 |
|---|---:|
| falhas de ferramenta com exceção (balde visível) | 20 |
| **falhas silenciosas** | **134** (87%) |
| execuções · meses · papéis · ferramentas | 124 · 7 · 10 · 18 |
| sobreposição visível × invisível (por step) | 0 |
| steps · sequências de steps consecutivos | 134 · 129 |

**Por ferramenta:** `busca_obf` 86 (de 697 steps, 12%); `get_peticao_inicial_from_pasta` 8 (de 380); `calculo_correcoes_monetarias` 7
(de 15, 47%); `calculo_horas_extras` 4 (de 12); `draft_resposta` 4 (de 90).

**Grupos do motivo:** `json_invalido` **86** · `plataforma` 22 · `fora_da_cobertura` 10 · `sem_resultado` 8 · `argumento_do_agente`
6 · `nao_reconhecido` 2 → **116 falhas reais**.

**O que vem depois:** em 122 das 134, o mesmo papel não tem nenhum erro com exceção nos 3 steps seguintes; nas demais:
`U_tipo_retorno` 3, `H_bloco_code` 3, `U_campo_inexistente` 3, outros 3. As memórias de contrato **não nascem** da falha
silenciosa: `U_tipo_retorno` 5/79 (6%), `U_campo_inexistente` 3/38 (8%) vêm logo depois de uma. **Nenhum Ajuste** nas
unidades de contrato.

**Candidato a sucesso falso [4] — um teto, não um achado.** 24/116: `plataforma` 17/22 (77%), `argumento_do_agente` 2/6,
`nao_reconhecido` 2/2, `json_invalido` 3/86 (3%).
- **Rodada de 02/10 (6 casos, [assistido]):** 0/6 — nas 3 calculadoras (plataforma) a resposta não usa o dado que
  faltou; nos 3 de `json_invalido` a resposta **declara a falha**.
- **Rodada de 04–05/10:** a leitura ampliada cobriu os 20 candidatos de plataforma e de JSON inválido: **em 0 a resposta
  usou o dado que faltou** (15 "não", 2 indeterminados; nos 15, 10 não precisavam do dado e 4 o pegaram de outra
  ferramenta — a soma dos subgrupos que o `14` cita é 17 de 20). A regra pelo estado final das variáveis achou a
  resposta **declarando a falha em 24 de 24**; o único marcado "sucesso falso provável" foi lido e não era.
- **Conclusão: nenhum sucesso falso confirmado na base 2.** O candidato é quase sempre **falha declarada**, e o desfecho
  precisa de dois eixos (usou o dado? declarou a falha?) → `transversal #1`.

**O `json_invalido` é o `repr_colado` no canal silencioso.** Na `busca_obf`: 80 são `str(dict/lista colado de um retorno
impresso)` e 6 são string literal colada — o agente cola o print do `puxa_doc_decisao` em vez de passar a variável. Destino:
memória (a lição do `repr_colado` estendida) **e** aviso à plataforma (o tipo `(str)` de `textos_decisoes` convida ao
`str(...)`). Na declaração do `busca_obf`, uma versão só nos 4 meses; a taxa de JSON inválido cai de 21% para 9% com a
mesma declaração — não há experimento natural.

**Detectores de comportamento (contagens, não falhas confirmadas):** inventário declarado 116 ferramentas; Result-Ignore
203 de 8.661 atribuições (2,3%); RAC 350; Reasoning-action mismatch 23 (retirado, só registro); Tool-Skip 3 de 1.000
execuções (0,3%, provisório); ferramentas chamadas × declaradas 103 × 116.

---

## 5 · O que a base 2 trouxe à taxonomia (Ajustes e etapas)

*(Origem: livro-razão §3 — Ajustes 3, 4, 8, 9, 13 — e as Etapas 3, 4, 5, 5b, 6.)*

| O que a base 2 mostrou | O que mudou | Efeito na base 2 |
|---|---|---|
| `Import from X is not allowed` (4 erros) e `FinalAnswerTool….forward() got an unexpected keyword argument` (1) sem regra | **Ajuste 3:** o sandbox casa `Import of` e `Import from`; o argumento inexistente vai para `U_arg_nomeado` | resíduo com 8 padrões; causa não identificada **12 → 7** |
| 16 dos 25 erros do sintoma não reconhecido eram um padrão só: Timeout de ferramenta | **Ajuste 4:** família nova `Infra / ferramenta`, unidade `H_timeout_ferramenta` (não-memória) | o alarme de cobertura deve desligar (esperado 25 → 9; conferido depois dos Ajustes 3, 4, 8 e 9: 2 erros) |
| a chave `?` do resíduo (6 `AgentExecutionError` sem `due to` + 1 `AgentMaxStepsError`) passava na recorrência sem ser padrão | `sem impressão digital: <err_type>`, marcada como não recorrente | o `?` deixa de passar (critério de aceitação da Etapa 5; o item está fechado: `b1 #30`) |
| o tempo esgotado do AgenteProcuracoes: plataforma ou agente? | **Ajustes 8 e 9** (tempo do interpretador por ferramenta; o `final_answer` num bloco sem laço com texto grande → `U_resultado_bruto`) | a regra acerta os 6 casos de tempo |
| 38 de 38 com a chave pedida no prompt | **Ajuste 13:** `U_campo_inexistente` = sinal de harness também na base 2 | esperado: candidatas 8 → 7 |
| os dois canais contavam o mesmo gesto | **Ajuste 12:** a consolidação | `U_repr_colado` 104 · 104 |

**O Timeout de ferramenta (Etapa 4 e Ajuste 4):** 16 erros, só ContestacaoCivel, em 5 ferramentas; limites de 600 s (12
erros) e 1800 s (4); 10/08 (6), 11/08 (6), 18/08 (1), 20/08 (2), 25/08 (1) — pico de dois dias (incidente) e uma cauda. 16
de 16 terminam com `final_answer` (o agente segue o fallback do prompt). O código do agente estava certo. **O gatilho do
monitoramento foi acionado** (dono: a plataforma; ação: ticket com as ferramentas, os limites, o pico e a cauda) → seção
Monitoramento do [roadmap da base 1](../../2026-09-trace-law-flow/docs/04-roadmap.md).

**O alarme de cobertura (Etapa 6):** 5,22% de sintoma não reconhecido, margem de cerca de 1 erro; 64% do balde era um
padrão de 1 mês. Decisão: manter o 5% (calibrar com 2 bases seria ajustar o limiar à amostra); a triagem passa a mostrar o
maior padrão e a taxa sem ele → `b1 #34`.

---

## 6 · Achados para a plataforma (sem mudança de código)

*(Origem: Etapa 5b, 29/09 — leitura do cru, só tamanhos e estrutura.)*

1. **Várias ferramentas pesadas num bloco.** OBFCivel jul (limite 30 s): `get_final_answer_schema`, `get_fields_definition`
   e `get_docs_from_filters` no mesmo bloco; o pensamento seguinte diz que está chamando muitas ferramentas de uma vez.
   RespostaOficios mar (30 s): `estrutura_subsidios` + `gera_transcricao_imagens`. Lição candidata: **"uma ferramenta
   pesada por step"** — sem regra: 2 casos, 1 confirmado (`b2 #12`).
2. **Ferramenta fora do laço.** OBFCivel ago (limite **180 s**, step de 222 s): o `extract_obf_requests` roda uma vez, fora
   do laço → uma chamada lenta mesmo com 180 s → plataforma. **Nenhum caso de ferramenta em laço nem de código lento na
   base 2.**
3. **O contrato `['result']` generalizado.** RespostaOficios: `Could not index … with 'result'` — o agente supôs
   `{'result': …}` numa ferramenta de validação; o desvio da base 1, confirmado na base 2.
4. **A busca de procurações só com CPF não achou; com nome + CPF achou** (AgenteProcuracoes, 1 execução): a ferramenta pede
   o nome, ou a documentação dela não diz isso.
5. **Possível falso negativo** (AgenteProcuracoes, 1 execução): a resposta final foi "não localizei procurações
   concluídas" depois de achar procurações. Em aberto: se o que achou não eram concluídas, está certa (`b2 #11`).
6. **Limites diferentes no interpretador:** 30 s (jul, mar) e 180 s (ago).

Mais, do erro crítico e das falhas silenciosas: o `'DEFAULT'` da calculadora nas duas bases; o passe dict → string JSON
entre `puxa_doc_decisao` e `busca_obf`; o prompt que pede um campo com outro nome; a troca de modelo sem revalidar; o
harness que aceita o `content` vazio sem erro (M5) → `transversal #7` (aviso à plataforma).

---

## 7 · Base 1 × base 2

*(Origem: `11` §3; `14`; livro-razão §6.)*

| | Base 1 | Base 2 |
|---|---|---|
| Erros | 498 (313 execuções) | 479 |
| Candidatas | 10 (440 erros, 88%) | 8 (370 erros, 77%) |
| Maior candidata | `U_texto_literal` (182) | `U_nome_inventado` (118; 5 na base 1) |
| Protocolo — modo | trocou (texto só em out/2025, 2 papéis) | texto o tempo todo |
| Protocolo — o que disparou o surto | modo; contrato de ferramenta | modelo |
| Protocolo — onde na tarefa | **no fim** (a resposta final) — M1, M2 | **no começo** (1º e 2º step) — M4, M5 |
| Protocolo — o que o LLM escreveu | texto longo (mediana 2.859 car.) | fragmento curto (mediana 138 car.), tokens "sumidos" |
| Falhas silenciosas | 9 com exceção · 120 silenciosas (93%) · [4] 54/75 | 20 · 134 (87%) · [4] 24/116 |
| Críticos | 0 | 1 |
| `U_campo_inexistente` | sinal de harness (mineração) | candidata na triagem; sinal de harness pelo Ajuste 13 |

**O que vale nas duas:** o erro de protocolo só existe no modo texto; um surto se explica por uma troca de configuração
lida no trace; o agente se recupera; memória não é o conserto. O contraste das falhas silenciosas: `plataforma` quase
sempre termina sem a ferramenta ter funcionado (84% e 77%), `json_invalido` quase nunca (0% e 3%); "o erro do agente se
recupera" **não** vale como regra (73% × 2/6).

---

## 8 · O que ficou aberto

- [ ] Preparar a pasta `-second` e reexecutar os notebooks no terminal → `b2 #1`; o monitoramento → `b2 #2`.
- [ ] Minerar `U_nome_inventado` (incidente ou lição?) → `b2 #3`.
- [ ] As minerações de silenciosas e de protocolo no método novo de leitura → `b2 #4`.
- [ ] Conferir na base 2 os efeitos esperados dos Ajustes 4 (alarme) e 13 (candidatas 8 → 7) → `b1 #31`, `b2 #1`.
- [ ] Falso negativo do AgenteProcuracoes → `b2 #11`; a lição "uma ferramenta pesada por step" → `b2 #12`.
- [ ] A investigação do erro crítico pela causa, e a medida do M6 → `transversal #5` e `#4`; o sucesso em dois eixos e em três
  níveis → `transversal #1` e `#2`.
- [ ] O ticket do timeout de ferramenta para a plataforma → seção Monitoramento do roadmap da base 1.

## Onde está cada coisa

| Parte deste relatório | Origem (o texto original continua lá) |
|---|---|
| §1 triagem | livro-razão §6, Etapas 10c e 10d, Ajuste 13 |
| §2 protocolo | [`11`](../../2026-09-trace-law-flow/docs/11-relatorio-protocolo-harness.md) §2 e §3; Etapa 10b; racional [`10`](../../2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md) |
| §3 erro crítico | `11` §2.5; Etapa 10d |
| §4 falhas silenciosas | [`14`](../../2026-09-trace-law-flow/docs/14-relatorio-falhas-silenciosas.md); racional [`13`](../../2026-09-trace-law-flow/docs/13-racionais-falhas-silenciosas.md); Etapas 10c e 10d |
| §5 taxonomia | livro-razão Ajustes 3, 4, 8, 9, 13; Etapas 3, 4, 5, 6 |
| §6 plataforma | livro-razão Etapa 5b |
| §7 comparação | `11` §3; `14`; livro-razão §6 |
