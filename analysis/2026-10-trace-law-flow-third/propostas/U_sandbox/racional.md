# Racional da lição — o inventário do sandbox (`U_sandbox`)

> Códigos e siglas: [glossário](../../../glossario.md). O porquê de cada passo, para toda lição:
> [`07`](../../docs/07-racionais-mineracao-candidatas.md). Os comandos: [`06`](../../docs/06-procedimento-mineracao-candidatas.md).
> Aqui fica só o que é desta lição, na ordem dos passos do `07`.

**Status:** proposta · **Escrito em:** 16/10/2026 · **Hash:** o do commit que traz este arquivo, registrado antes de o
script rodar na base 3 (a ordem do pré-registro).

## A lição

O agente escreve código que o interpretador do sandbox recusa: chama uma função proibida (`repr`, `eval`, `globals`,
`dir`), importa um módulo fora da lista autorizada (`ast`), usa um módulo sem importar (`json`, `datetime`) ou um
módulo que não existe no ambiente (`openpyxl`). É uma lição **factual sobre o ambiente**: o conteúdo da memória é a
lista do que pode e do que não pode.

**A hipótese que o script testa:** a lição sai da própria mensagem de erro. O interpretador escreve o nome do que
recusou e, no import, a lista dos imports autorizados; não é preciso ler o caso.

**De onde veio a regra.** Base 1, pela porta da query (16/10/2026): 17 erros em `U_sandbox`, **17 com nome (100%)**:
`modulo_sem_import` (datetime 3, json 3), `funcao_proibida` (repr 3, globals 2, dir 1, eval 1), `modulo_ausente`
(openpyxl 1), `atributo_dunder` (`__name__` 1), `import_bloqueado` (autojson 1, ast 1). Duas listas de imports
autorizados distintas (uma com `pandas` e `json`, outra sem), o que sugere que a lista depende do papel. Os padrões são
os da regra de classificação do `base_pipeline.py` (a assinatura e a sub-unidade); nada novo.

## Passo 1 · A população, em prosa (para a auditoria)

Na rodada: os erros classificados em `U_sandbox` (sub-unidades `inventario_sandbox` e `modulo_sem_import`), o
`casos.csv` do perfil. Os pendentes não entram.

Na auditoria, sem importar o pipeline: o passo é um erro estruturado (o tipo do erro preenchido) e a mensagem tem
- `Forbidden function evaluation: '<nome>'` com `<nome>` uma função embutida do Python (um nome que não é embutido é
  "nome não definido", outra lição); ou
- `Import of` / `Import from`, `ModuleNotFound` ou `Forbidden` (qualquer outro); ou
- ``The variable `<nome>` is not defined`` com `<nome>` em `json`, `pd`, `np`, `re`, `os`, `math`, `datetime`;

e não tem nenhum dos sinais que o pipeline decide antes (resposta sem bloco de código — `regex pattern`; falha do LLM —
`AgentGenerationError`, `internally hosted`, `Error code: 422`, `UnprocessableEntity`; timeout de ferramenta —
`excedeu o timeout`, `TimeoutError`; sintaxe, `Could not index`, `has no attribute`, `JSONDecode`, argumento
posicional, `object is not an iterator`, limite de passos, tempo do interpretador).

**Emenda 2, de 16/10, depois da primeira rodada na base 3** (`observada_e3ebc8274dcf108c`): a lista acima não tinha os
três primeiros sinais (bloco de código, falha do LLM, timeout de ferramenta), que o pipeline decide antes do sandbox
(o timeout desde o Ajuste 4 do livro-razão). Na base 3, **1 erro de 3.653** tinha a função proibida e o timeout de
ferramenta na mesma mensagem: o pipeline o pôs no timeout, e a auditoria, no sandbox. O encontro divergiu só por ele
(`passo7_divergencia.csv`). A emenda corrige a definição da auditoria; a população da mineração (a da rodada), as
regras do passo 4 e os limiares não mudam. Decisão do Rafael.

## Passo 4 · A regra específica: o nome recusado de cada erro

Sobre o último trecho da mensagem (depois do último `due to:`, porque o começo repete a linha de código do agente, que
pode ter as mesmas palavras), na ordem; vale a primeira que casar:

| Tipo | Padrão na mensagem | O nome extraído |
|---|---|---|
| `funcao_proibida` | `Forbidden function evaluation: '<nome>'` | a função |
| `import_bloqueado` | `Import of <módulo> is not allowed` ou `Import from <módulo> is not allowed` | o módulo |
| `modulo_ausente` | `No module named '<módulo>'` | o módulo |
| `atributo_dunder` | `Forbidden access to dunder attribute: <nome>` | o atributo |
| `modulo_sem_import` | ``The variable `<nome>` is not defined`` | o módulo |
| `sem_nome` | nenhuma das anteriores | — |

A mensagem é a do passo com erro, inteira (a v2 não tem corte); com estado não íntegro, conta como `sem_nome`.

**As listas de imports autorizados:** quando a mensagem tem `Authorized imports are: [...]`, os nomes entre os
colchetes, em ordem alfabética, viram uma lista; listas iguais contam como uma.

**Tabelas:** uma linha por erro (`exec_id`, `step_ref`, papel, mês, tipo, nome); o inventário por tipo e nome (erros,
execuções, papéis, meses); nome × papel; nome × mês; cada lista autorizada distinta com os papéis e os meses.

## Passo 5 · A confiança: cobertura ≥ 95%

Erros com nome ÷ erros da população; o `sem_nome` contado pela primeira palavra do trecho. **Abaixo de 95%,** a hipótese
"a lição sai da mensagem" não vale: o arquivo final não é gravado e a lição volta à investigação.

## Passo 6 · Os números para o destino

1. A lista autorizada é uma só, em todos os papéis e meses? (sim → é configuração fixa do ambiente, e cabe perguntar se
   o lugar dela é o prompt do harness)
2. O mesmo nome reaparece na mesma execução e papel depois do primeiro erro? (sim → o agente não aprende sozinho
   dentro da execução)

## Passo 7 · O que o encontro compara

A população, a cobertura, o inventário por tipo e nome e as listas autorizadas.

## Passo 8 · O arquivo final

| Campo | Como é montado | Origem |
|---|---|---|
| `category` | "Inventário do sandbox (factual · ambiente)" | checado |
| `scope` | `role: null` (o sandbox é um ambiente só); com mais de uma lista autorizada, a guidance as separa | checado |
| `location` | até 10 casos, o primeiro de cada papel na ordem (papel, mês, `step_ref`), com `exec_id`, `step_ref`, `fonte_id`, `rodada_id` | checado |
| `evidence` | 3 casos: o primeiro de cada um dos três tipos mais frequentes, com tipo e nome | checado |
| `description` | frase montada das contagens: quantos erros, de que tipos, em quantos papéis | checado |
| `correction_guidance` | montada da tabela, sem texto livre: "Não chame: …; não importe: …; importe antes de usar: …; não existe no ambiente: …; não acesse: …; imports autorizados: …" — todos os nomes vistos, por ordem de erros; com mais de uma lista autorizada, uma por grupo de papéis | checado |
| `occurrences` | erros, ocorrências, execuções e meses do perfil da rodada | checado |
| `status` | `derived-and-checked` se a cobertura passa e o encontro fecha | checado |
| `validation` | cobertura, encontro, listas autorizadas, os números do passo 6; `destino: "em aberto"` até o Rafael decidir | checado / pendente |
| `impact` | `null` | pendente |

**Emenda de 16/10 (depois do primeiro ensaio na base 1, antes de qualquer rodada na base 3).** Duas mudanças na linha
`correction_guidance` do passo 8, nenhuma em regra, limiar ou população:
1. o rótulo "não acesse" (o tipo `atributo_dunder`, que já estava no passo 4);
2. "com mais de uma lista autorizada, uma por grupo de papéis", que repete o que a linha `scope` já dizia.

**A base de confirmação é a base 3.** A regra foi escrita olhando a base 1 (ver "De onde veio a regra"), então o ensaio
na base 1 confere o **código** (o script faz o que o racional diz), não a **hipótese** (a lição sai da mensagem). Quem
confirma a hipótese é a primeira rodada na base 3, depois do commit desta emenda. O hash do pré-registro fica
registrado no funil do procedimento `06`.

## O que não mede

- Se o agente se recuperou depois do erro (é o "depois" da parte genérica).
- Se a memória reduz os erros: é o teste de compensação (`b3 #39`), depois de haver memória.
- O que não gerou erro: a lista autorizada só aparece nos erros de import.
