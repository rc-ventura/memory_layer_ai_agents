# Glossário — os códigos e termos das análises, explicados uma vez

**Para que serve:** os documentos das análises usam códigos curtos (M1, S5, `U_repr_colado`, "o [4]"…) para caber em
tabelas e para o histórico (commits, livro-razão, diário) continuar legível. **Este arquivo diz o que cada um quer
dizer.** Todo documento que usa códigos aponta para cá no topo. Código novo entra aqui no mesmo commit em que aparece.

---

## 1 · Os dois baldes de erro

| Termo | O que é |
|---|---|
| **balde visível** | os erros que levantaram exceção (`ActionStep.error` preenchido). É o que o notebook da esteira classifica (família → assinatura → mecanismo → unidade). |
| **balde invisível** / **falha silenciosa** | a ferramenta falhou, mas devolveu o erro **como texto** (`"Error calling tool '<nome>': …"`), e o step ficou com `error: null`. Para o pipeline, o step "deu certo". Notebook `falhas_silenciosas.ipynb`, docs 13–15. |
| **consolidação** | a etapa que junta as ocorrências dos dois baldes numa triagem só: `consolidacao_unidades.ipynb` (§14.x), Ajuste 12. Conta execuções, meses e papéis sobre a união dos canais; erros e tokens continuam do visível. |
| **canal** | de onde vem uma ocorrência de unidade: **visível** (erro com exceção) ou **silencioso** (falha devolvida como texto). A mesma unidade pode ter os dois — hoje, a `U_repr_colado`. |
| **`REGRAS_INVISIVEL`** | as regras que levam uma falha silenciosa a uma unidade do catálogo, sem nome de ferramenta (`base_pipeline.py`). Hoje, uma: JSON inválido com argumento colado de um retorno impresso → `U_repr_colado`. O que não casa fica sem unidade. |
| **ocorrência** | uma **cascata × unidade**, nos dois baldes (decisão de 02/10, aplicada no Ajuste 12): erros — ou falhas silenciosas — seguidos do mesmo papel contam uma vez por unidade. |
| **cascata** | erros consecutivos do mesmo papel na mesma execução. O 1º é o que importa; os seguintes são "seguidores". |

## 2 · As unidades de memória (os nomes `U_…`, `H_…`, `X_…`, `C_…`)

O prefixo diz **quem corrige**: `U_` = o agente (candidata a memória), `H_` = o harness ou a plataforma (não é
memória), `X_` = resíduo sem regra (revisar), `C_` = erro crítico (a execução morreu).

| Código | Nome | Em uma frase |
|---|---|---|
| `U_texto_literal` | Texto longo nunca dentro de literal de string | o agente põe um texto grande dentro de aspas no código e quebra a sintaxe |
| `U_contrato_dict` | Retorno das ferramentas de documento é dict | o agente indexa o retorno como lista, mas ele é um dicionário |
| `U_tipo_retorno` | Retorno pode chegar como string | o agente trata como dicionário um retorno que veio como texto |
| `U_campo_inexistente` | Campo inexistente no retorno estruturado | o agente pede uma chave que o retorno não tem |
| `U_texto_solto` | Explicação nunca solta no bloco de código | o agente escreve explicação em prosa dentro do bloco de código |
| `U_arg_nomeado` | Ferramentas só aceitam argumento nomeado | chamada posicional numa ferramenta que exige `nome=valor` |
| `U_sandbox` | Inventário do sandbox | uso de módulo ou função que o ambiente bloqueia |
| `U_next_gerador` | `next()` sobre expressão geradora falha no sandbox | um idioma de Python que o ambiente não aceita |
| `U_estado_perdido` | Após step com erro, o que ele definiria não existe | o agente usa uma variável que o step com erro nunca chegou a criar |
| `U_nome_inventado` | Nome usado sem ter sido definido | o agente usa um nome (variável ou função) que não existe |
| `U_repr_colado` | Não colar retorno impresso de volta no código | o agente copia o print de um retorno para dentro do código em vez de usar a variável |
| `U_codigo_lento` | Não rodar laço pesado dentro do bloco de código | o tempo do interpretador estoura num laço sem ferramenta |
| `U_resultado_bruto` | Não entregar o resultado bruto de uma ferramenta na resposta final | o agente põe o retorno inteiro da ferramenta no `final_answer` e estoura o tempo |
| `H_bloco_code` | Protocolo do harness | a resposta do modelo veio sem o bloco `<code>…</code>` que o harness exige (família própria, docs 10–12) |
| `H_timeout_ferramenta` | Ferramenta excedeu o timeout | a ferramenta demorou mais que o limite — conserto na plataforma |
| `H_infra_llm` | Falha do LLM upstream | o serviço do modelo falhou — política de retry |
| `C_limite_passos` | Limite de passos atingido | a execução morreu sem se recuperar ("erro crítico") |
| `X_causa_nao_identificada` | Causa não identificada | o sintoma é conhecido, a causa não tem regra |
| `X_sintoma_nao_reconhecido` | Sintoma não reconhecido | nenhuma regra reconhece a mensagem — cobertura |

**Decisões da triagem:** *candidata* = passa na régua de recorrência (≥3 execuções e ≥2 meses) e vira memória
candidata; *sinal de harness* = recorrente, mas quem corrige é o prompt ou a ferramenta, não a memória; *não-memória* =
plataforma; *fora: sem recorrência* = não passou na régua; *revisar* = resíduo.

## 3 · Os mecanismos do erro de protocolo (M1–M6)

A família `H_bloco_code` — "a resposta veio sem o bloco de código" — tem seis mecanismos, descritos em
[`2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md`](2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md) §4.

| Código | Nome | O que acontece | Quem corrige |
|---|---|---|---|
| **M1** | resposta final fora do bloco | o modelo escreve a resposta final (relatório, JSON pedido, pergunta ao usuário) sem o bloco `<code>`; no step seguinte reembrulha em `final_answer` | o prompt (sinal de harness) |
| **M2** | ferramenta concorrente do `final_answer` | uma ferramenta chamada "resposta final" faz o modelo achar que já terminou | o contrato da ferramenta (sinal de harness) |
| **M3** | marca do bloco digitada errada | intenção certa, tag errada (só o plano, ou `</code>` na abertura) | ninguém — taxa de fundo |
| **M4** | resposta esvaziada pelo modelo | o modelo gasta centenas de tokens e entrega pouco ou nada de texto | a plataforma (modelo/modo) |
| **M5** | step vazio aceito | a resposta vem vazia e o harness roda um bloco vazio sem erro | o harness |
| **M6** | narração executada como código | o harness concatena trechos do pensamento e executa narração como se fosse código | o harness |

## 4 · As medidas do balde invisível ([1]–[4])

Os números entre colchetes são as seções da saída do `drill_down.py silenciosas` e do notebook §13.

| Código | Nome | Pergunta |
|---|---|---|
| **[1]** | por ferramenta | onde as falhas silenciosas se concentram |
| **[1b]** | por grupo do motivo | o que a ferramenta reclamou: sem resultado · fora da cobertura · argumento do agente · plataforma · JSON inválido · não reconhecido |
| **[2]** | o que vem depois | o 1º erro com exceção do mesmo papel nos 3 steps seguintes (se nenhum, a falha passou sem rastro) |
| **[3]** | contrato precedido | quanto das memórias de contrato de retorno vem logo depois de uma falha silenciosa |
| **[4]** | candidato a sucesso falso | a ferramenta falhou de verdade e o papel entregou a resposta final sem ela ter funcionado — **teto**, só a leitura confirma |
| **[4b]** | sucesso falso conferido (proposta) | o mesmo, conferido pelo estado final das variáveis (`txt_vrvl_locl`) — plano-atual 4.1c |

**Sucesso falso** = a execução parece ter dado certo, mas a resposta usa um dado que a ferramenta não entregou.
**Desfecho de uma falha real de ferramenta** (o que aconteceu com a tarefa — não é família, submecanismo nem unidade;
decidido em 02/10): **recuperou** (a ferramenta funcionou numa nova tentativa) · **não dependia** (a resposta não
precisava do dado, ou ele veio de outra fonte) · **falha declarada** (a resposta diz ao usuário que não conseguiu) ·
**sucesso falso** (a resposta usa o dado que não veio — inventa, ou omite a falha).

## 5 · As seções do `drill_down.py protocolo` ([1]–[9])

[1] por mês · [2] por papel · [3] mês × papel · [4] a forma do que o modelo escreveu no lugar do bloco · [5]
recuperação · [6] cascata (o que vem logo depois) · [7] modo do agente (versões do prompt: JSON × texto com `<code>`) ·
[8] modelo e versão do agente · [9] a medida da resposta final fora do bloco (M1).

## 6 · Os itens do plano (S1–S6, D2, números como 4.2b)

Os números (4.1b, 4.2b-0, 4.11…) são as seções do [`plano-atual.md`](plano-atual.md) §4. Os códigos S e D vêm da
investigação do erro crítico (01/10):

| Código | Nome |
|---|---|
| **S1** | leitura do erro crítico da base 2 |
| **S2** / **S2b** | o detector de falhas silenciosas / os grupos do motivo |
| **S3** | medir a narração executada como código (M6) nas duas bases |
| **S4** | ferramentas que respeitam as chamadas do papel (o `idx` mistura chamadas) |
| **S5** | sucesso em três níveis: o Python executou · a ferramenta funcionou · a tarefa foi concluída |
| **S6** | o erro crítico como gatilho de destino |
| **D2** | os erros de protocolo do RespostaBacen na base 2 |
| **roadmap #N** | o item N do backlog numerado da análise (`2026-09-trace-law-flow/docs/04-roadmap.md`) |
| **Ajuste N** | a N-ésima mudança de regra do método, registrada no livro-razão (`pipeline-entre-bases.md` §3) |

## 7 · Bases, máquinas e o grau de certeza

| Termo | O que é |
|---|---|
| **base 1** / **base 2** / **base 3** | três extrações independentes de 1.000 execuções da esteira (base 1: out/2025–ago/2026; base 2: lote de ago/2026) |
| **máquina 2** | a máquina de compliance onde a base 2 está; de lá só saem contagens e nomes, nunca texto de caso nem `exec_id` |
| **[conferido]** | verificado de forma determinística (contagem, AST, regex reproduzida) |
| **[assistido]** | leitura feita por LLM na máquina 2 — entra como hipótese, nunca como fato |
| **teto** | contagem que inclui tudo o que *pode* ser o fenômeno; o número real é menor ou igual |
