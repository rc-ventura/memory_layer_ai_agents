# Roteiro de investigação — a parte específica de uma candidata a memória (análise funda por LLM)

Para a lição (unidade) que, no funil do procedimento de mineração de candidatas (`docs/*procedimento-mineracao-candidatas*.md`),
tem `investigação:candidata`. **Entrada:** o relatório da parte genérica e as tabelas em
`pipeline/resultados/mineracao/<u>/` (`perfil`, `sub_unidades`, `antes`, `depois`, `estabilidade`, `casos`).
**Saídas:**
- o dossiê, no esqueleto do kit;
- `memoria_<u>_<BASE_ID>.json`, no esquema da análise (`analysis/esquema-memoria.json`);
- `regras.json`, com as regras que funcionaram.

O porquê das perguntas está no `06` §9: o Passo 2 é o que extrair, o Passo 3 é o conserto, o Passo 7 é a causa raiz e
o destino.

## As perguntas, nesta ordem

### L1 · Qual é a lição de verdade?
- **Antes de ler,** escreva no dossiê duas ou mais formulações candidatas da lição, como **fato** ("a ferramenta X
  devolve Y") ou como **hábito** ("antes de Z, faça W"). Inclua a nula: "não há uma lição única; são erros
  parecidos por acaso".
- **Categorias** (`licao`): `fato:<rótulo curto>` · `habito:<rótulo curto>` · `sem_licao_unica` · `indeterminado`.
  Use só os rótulos escritos antes de ler; um rótulo novo exige escrevê-lo no dossiê e reler a amostra.

### L2 · O que dispara o erro?
- **Antes de ler,** escreva as hipóteses de causa. Use as tabelas da parte genérica: o que vem antes (G3), a
  concentração (G5) e as sub-unidades (G2). Por exemplo: "o nome foi definido numa chamada anterior do papel",
  "é texto de explicação executado como código", "é efeito de um modelo".
- **Categorias** (`causa`): uma por hipótese, mais `outra:<rótulo>` e `indeterminado`.

### L3 · O agente se corrige?
- **Use primeiro o G4,** o que vem depois (determinístico). Leia só para separar "corrigiu entendendo" de "contornou".
- **Categorias** (`conserto`): `corrigiu_a_licao` · `contornou` · `repetiu` · `desistiu` · `indeterminado`.

### L4 · É memória ou sinal de harness?
- **A regra do `06` §9 Passo 7/8:**
  - se o prompt ou o contrato da ferramenta **induz** o erro (o prompt diz uma coisa e a ferramenta faz outra), é
    **sinal de harness**: o conserto é na origem;
  - se o agente precisaria **saber ou fazer diferente** e o ambiente está certo, é **memória**.
- **Categorias** (`destino_lido`): `memoria` · `harness` · `em_aberto`.
- **A decisão é do pesquisador.**

## Leitura e contagem

- **Amostra:** `montar_evidencia.py --nome inv_candidata_<u>_<BASE_ID> --de mineracao/<u>/casos.csv` (regra
  `procedimento`; com população grande ou concentrada num mês, `--regra semente --n 10`). Na lição com sub-unidades
  que passam sozinhas, `--por role` (ou a dimensão do G2).
- **Primeira leitura:** o `investigador` lê cada caso (`drill_down.py caso <exec_id> <role>`; o step do erro, o
  anterior e o seguinte) e grava `leitura_candidata_<u>_<BASE_ID>.csv` com `licao`, `causa`, `conserto`,
  `destino_lido` e `onde_no_cru`.
- **Segunda leitura:** o `segundo-leitor` relê uma subamostra às cegas. A concordância (`concordancia.py`) é medida
  por coluna, **sempre com `--registrar resultados/mineracao/<u>/confianca.json`**. O mesmo vale para cada regra
  contada no `testar_regra.py`: é desse arquivo que o painel lê a confiança.
- **Reconfirmação numa partição nova:** a mesma leitura e as mesmas regras, sem mudança, numa amostra da partição, com
  `--local "partição <id>"` no `--registrar`.
- **Regras:** para cada hipótese de L1/L2 que a leitura sustenta, uma regra contada (`testar_regra.py`, `--regex` num
  campo do step ou `--condicao` nas colunas do `casos.csv`). A regra que funciona (concordância ≥ 90%, "pega a mais"
  ≤ 10%) vai para `regras.json`:
  ```
  [{"hipotese": "...", "regra": {"regex"|"condicao": "...", "campo_passo": "...", "deslocamento": 0, "onde": ["..."]},
    "populacao": "mineracao/<u>/casos.csv", "contagem": "<a linha do testar_regra.py>", "base": "<BASE_ID>",
    "data": "AAAA-MM-DD",
    "confirmacoes": [{"particao": "<id da partição nova>", "contagem": "<a linha>", "data": "AAAA-MM-DD"}]}]
  ```

## O arquivo final (o rascunho da memória)

Os campos são os do esquema da análise. Para cada um, a origem:

| Campo | De onde vem | Origem |
|---|---|---|
| `category` | a unidade e o tipo (a triagem) | `checado` (o `perfil.csv`) |
| `occurrences` | o `perfil.csv` (erros, ocorrências, execuções, meses) | `checado` (o comando do notebook genérico) |
| `location` | a lista da amostra (o `casos.csv` da evidência), capada em ~10 | `checado` (o comando do `montar_evidencia.py`) |
| `scope` | a sub-unidade que passa sozinha no G2 (papel, ferramenta); `null` quando não restringe | `checado` se o G2 sustenta; senão `hipotese` |
| `evidence` | 2–3 casos da amostra, só estrutura (sem texto de caso) | `checado` (a pasta de evidência) |
| `description` | a lição (L1) e a causa (L2), em uma ou duas frases | `checado` se uma regra contada sustenta; senão `hipotese` |
| `correction_guidance` | o que o agente deve fazer diferente (L1 como hábito, ou o fato a lembrar) | `hipotese`, até ser testado (as POCs) |
| `status` | `derived-and-checked` se `description` e `scope` estão `checado`; senão `hipotese` | — |
| `validation` | as contagens de cada passo e `destino` = L4 (proposta) | `checado` nas contagens; o destino é proposta |
| `impact` | `null` (decisão do `06` §9 Passo 8) | `pendente` |

O arquivo só é entregue depois de aprovado pelo `validar_memoria.py` da skill `mineracao-candidata`.
