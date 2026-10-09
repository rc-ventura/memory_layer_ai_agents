# Procedimento de validação — como os números da base 3 foram conferidos e como reproduzi-los

> Códigos e siglas: [glossário](../../glossario.md).

**Para que serve este documento:** antes de apresentar o [relatório](02-relatorio-achados.md), saber de onde vem
cada número, o que foi conferido e o que a extração não permite afirmar. As razões das escolhas estão nos
[racionais](01-racionais.md).

**Onde cada coisa roda.** A base 3 só existe na máquina 2. O código é o mesmo nas duas máquinas (branch
`2026-10-08-validacao-base-3`). Nesta máquina rodam os testes e o teste com a base 1; na máquina 2 rodam a rodada real
e as conferências contra o parquet. Da máquina 2 saem só contagens, nomes de unidade e motivos.

---

## 1 · Reproduzir a rodada (máquina 2, da raiz do repositório)

```bash
uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py analisar      # grava resultados/observada_<id>/
uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/resumo_rodada.py # resumo, triagem e cobertura
```

O `<id>` da rodada é o hash de (contrato, base, fonte, código). Mesma fonte e mesmo código dão a mesma pasta — a
rodada deste relatório é `observada_0d23103afd4fc0f4`. Código ou fonte diferentes dão outra pasta; a antiga não é
sobrescrita. Para gerar também o perfil de uma candidata: `executar.py analisar --perfil <unidade>`.

| Arquivo da rodada | O que tem |
|---|---|
| `manifesto.json` | fonte (hash), hash de cada arquivo de código, resumo, hash de cada artefato |
| `triagem_visivel_observada.csv` | a triagem (§3 do relatório) |
| `triagem_sensibilidade.csv`, `triagem_por_papel*.csv` | régua estrita; triagem dentro de cada papel |
| `cobertura_mecanismos.csv`, `cobertura_sintomas.csv` | o que é observável e o que é pendente, com o motivo |
| `consolidacao_*.csv` | limítrofes, componentes, unidade × papel × mês, fila de pendências, global × papel |
| `genealogia_arestas.csv`, `genealogia_observada.png` | a genealogia completa, todos os erros em cada coluna |
| `unidades_observadas.png`, `papel_unidade.png` | tokens por unidade; erros por papel × unidade |
| `perfis/<unidade>/` | casos, amostra de investigação (até 30, por regra fixa), antes/depois, estabilidade |

`ler_artefato()` (em `mineracao_observada.py`) só aceita um arquivo se o hash dele, o da fonte e o do código baterem
com o manifesto.

## 2 · O que foi conferido

| Conferência | Onde | Resultado (08/10) |
|---|---|---|
| Suíte de testes (`analysis/tests/`, 7 arquivos) | as duas máquinas | **162 testes, todos passam** |
| Regras e catálogos comparados por estrutura de código com a base 2 (`classify`, `submecanismo`, `SUB2UNI`, `UNI`, `triagem`…) | máquina 2, `executar.py validar` | **10 de 10 iguais** |
| Conferência da rodada contra o parquet lido direto (contagens, tokens, duração, conservação de erros e tokens entre tabelas, genealogia, perfis, hashes, fonte inalterada) | máquina 2, `executar.py conferir` | **46 verificações, todas passam** |
| Fonte | máquina 2 | SHA-256 `7604f77d…c2873f1`, igual à referência no código (`FONTE_REFERENCIA_SHA256`) |

As 46 verificações estão listadas em `resultados/conferencia_observada_2026-10-07/conferencia.json` (máquina 2).
Elas conferem que os números são consistentes entre si e com o parquet — **não** conferem que a causa atribuída a cada
erro está certa. Isso é a leitura de casos, na mineração de cada candidata.

## 3 · Teste com resposta conhecida: a base 1 pela mesma query

A pergunta: o que o modo observado faz com erros cuja resposta já sabemos? A base 1 está aqui como trace completo e
já foi analisada pelo pipeline das bases 1 e 2. A query da base 3 foi reescrita em Python
(`pipeline/validacao/porta_query_v1.py`, CTE a CTE) e aplicada à base 1; o resultado passou pelo modo observado e foi
comparado erro a erro com o pipeline da base 1.

```bash
uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/comparar_base1.py   # nesta máquina
```

| Pergunta | Resultado |
|---|---|
| A extração reproduz a população? | sim: 5.781 ActionSteps e 498 erros estruturados, iguais ao pipeline da base 1 |
| Todo erro tem par no pipeline da base 1? | 498 de 498 |
| Quantos caem na mesma unidade? | **415** |
| Quantos caem em unidade diferente? | **0** |
| Quantos ficam pendentes, e por quê? | 83: 81 do retorno-dict e 1 do retorno-string por **mensagem cortada**; 1 do texto em literal por **histórico incompleto** |
| A triagem muda? | não: mesmas decisões. Única diferença: campo inexistente sai "candidata" em vez de "sinal de harness", porque o destino decidido na base 1 não é herdado (de propósito) |

**Conclusão do teste:** onde o modo observado classifica, classifica igual ao pipeline completo; onde a janela não
traz o dado, o erro fica pendente — não vai para unidade errada. O custo é a perda de recorrência nas unidades que
dependem do fim da mensagem (retorno-dict).

## 4 · Limitações da extração (v1), medidas

| # | Limitação | Evidência | Efeito na base 3 |
|---|---|---|---|
| 1 | A mensagem de erro é cortada em 20.000 caracteres | base 1: 82 de 498 erros passam do corte; 81 dos 96 do retorno-dict perdem a causa (o `KeyError` fica no fim) | 1.009 erros pendentes por mensagem limitada; retorno-dict com 2 erros observáveis |
| 2 | Só há passos com erro — sem denominador | a query filtra antes de exportar | nenhuma taxa por passo, execução, papel ou versão |
| 3 | A regex de suspeita não reconhece "Error calling tool" | base 1: pega 0 das 119 falhas silenciosas | falhas silenciosas não medidas; as 1.280 suspeitas ficam fora da taxonomia |
| 4 | Sem system prompt, modelo e resposta final | colunas ausentes na query | protocolo do harness só por contagem; sucesso por conteúdo indisponível; 215 timeouts pendentes |
| 5 | A janela não traz a chamada | base 1: 27 erros com o passo anterior em outra chamada; o `step_number` reinicia nos 27 | componentes condicionais; 5 pendentes por numeração ambígua |
| 6 | A partição do contexto não inclui o agente | `PARTITION BY execução, papel` na query | se dois agentes da mesma execução dividem um papel, os passos se misturam; o pipeline suspende esses vínculos |
| 7 | O filtro de tamanho exclui a execução quando um dos três textos é NULL | no SQL, `length(NULL)` torna a soma NULL; base 1: se vazio fosse NULL, sobrariam 100 de 1.000 execuções | 20.971 de 20.986 execuções com erro têm resposta gravada (base 1: 34 de 318). Não dá para saber, sem a tabela de origem, se a extração cortou as sem resposta |
| 8 | `tool_name` é só a primeira ferramenta do passo | base 1: 5.742 de 5.742 são `python_interpreter` | a coluna não identifica a ferramenta que falhou; ela sai do código e da mensagem |

Contagens da limitação 7 na máquina 2: `pipeline/validacao/contar_filtro_nulo.py`. Cada limitação vira item do pedido
da próxima versão da query ([roadmap](04-roadmap.md) #2).

**Sobre os 5.818 pendentes por "predecessor não identificado".** Esse motivo é gerado só para erros de nome não
definido, quando a janela não identifica o passo anterior. Isso cobre dois casos: (a) não existe passo anterior — o
erro está no primeiro ActionStep do papel; (b) existe passo anterior, mas sem `step_number`. Na base 1, todos os
casos sem passo anterior são o primeiro ActionStep (50 de 50) e o caso (b) não ocorre. **Na base 3 a proporção entre
(a) e (b) não foi medida.** Por isso esses erros continuam pendentes, sem unidade, até a investigação
([roadmap](04-roadmap.md) #1).

## 5 · Do número ao caso

Na base 3 o "cru" é a linha do parquet: o erro e a janela em volta. Para cada candidata, `perfis/<unidade>/` traz:

- `casos.csv` — todos os erros da unidade, localizados por execução, agente, papel, `step_pos` e `step_ref` (o
  `idx` das bases 1 e 2 não existe aqui e não é inventado);
- `amostra_investigacao.csv` — até 30 casos, por regra fixa (intercalando papéis), para a leitura;
- `antes.csv`, `depois.csv`, `proximo_final.csv`, `estabilidade.csv`, `sub_unidades.csv`.

Esses arquivos têm identificadores e ficam na máquina 2. Voltar ao trace inteiro de uma execução exige uma consulta
por `cod_idef_exeo` na tabela de origem, que não está disponível hoje.

## 6 · Antes de apresentar

- [ ] Os números do relatório saem da rodada `observada_0d23103afd4fc0f4` (a pasta existe e o manifesto está como
      `concluida_tecnicamente_sem_aprovacao_semantica`).
- [ ] "Candidata" é dita como "recorrente o suficiente para minerar", não como memória aprovada.
- [ ] Nenhuma taxa é citada (limitação 2).
- [ ] Os pendentes são apresentados como limite da extração, não como erros sem explicação.
- [ ] A ausência do retorno-dict é explicada pelo corte (limitação 1), não como "o padrão sumiu".
