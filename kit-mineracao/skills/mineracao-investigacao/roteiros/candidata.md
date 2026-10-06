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
- **Antes de ler,** escreva no dossiê as formulações que a parte genérica sugere, como **fato** ("a ferramenta X
  devolve Y") ou como **hábito** ("antes de Z, faça W"), e a nula: "não há uma lição única; são erros parecidos por
  acaso". Elas são o ponto de partida, **não a lista final**: a lista sai da leitura aberta (abaixo).
- **Os resultados possíveis,** todos normais (a unidade nasceu do sintoma, e um sintoma pode ter várias causas):
  - **uma lição** que cobre a unidade;
  - **uma lição geral com variações por papel** (o mesmo hábito aparece de formas diferentes em papéis diferentes):
    a lição vai na `description`, e os papéis, com um exemplo de cada, no `scope`;
  - **várias lições:** a proposta de dividir a unidade, que é decisão do pesquisador (um Ajuste de taxonomia).
- **Categorias** (`licao`), na leitura fechada: as da lista aprovada no gate, mais `sem_licao_unica` e `indeterminado`.
  Em todas as leituras, cada leitor escreve também `licao_livre`: a lição com as próprias palavras, numa frase, em
  termos gerais (sem nome, número ou trecho do caso).

### L2 · O que dispara o erro?
- **Antes de ler,** escreva as hipóteses de causa. Use as tabelas da parte genérica: o que vem antes (G3), a
  concentração (G5) e as sub-unidades (G2). Por exemplo: "o nome foi definido numa chamada anterior do papel",
  "é texto de explicação executado como código", "é efeito de um modelo".
- **Categorias** (`causa`): as da lista aprovada (as hipóteses escritas antes entram como candidatas), mais
  `outra:<rótulo>` e `indeterminado`. Quando o roteiro pedir dois eixos (por exemplo, **o que é o texto** e **o que
  quebrou**), cada eixo é uma coluna, e cada um se mede à parte. Uma lista que mistura os dois eixos numa coluna só faz
  cada leitor responder uma pergunta diferente.

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

## Leitura e contagem — em duas etapas: primeiro aberta, depois fechada

A leitura não começa por uma lista escrita antes de ver os casos: se a lição certa não está na lista, cada leitor marca
a mais próxima, e a discordância é da lista, não da lição. Ela também não fica só em frase livre, porque o script não
sabe comparar duas frases. Por isso, duas etapas: as frases dos leitores viram a lista, o pesquisador a aprova, e só
então os leitores classificam e o script mede.

- **Amostra:** `montar_evidencia.py --nome inv_candidata_<u>_<BASE_ID> --de mineracao/<u>/casos.csv --por role` (ou a
  dimensão do G2 que passa sozinha), com `--regra semente --n 30` quando a população passar de 30. Com população de
  até 30, todos os casos.
- **A divisão, por regra fixa e sem sorteio:** os casos de posição ímpar da amostra (1º, 3º, 5º…), até 10, vão para a
  **leitura aberta**; os outros, para a **leitura fechada**. Com população pequena (menos de 30 casos), as duas etapas
  usam os mesmos casos, e o dossiê declara que a concordância sai otimista.
- **Etapa 1 · Leitura aberta.** O `investigador` e o `segundo-leitor`, cada um sem ver o outro, leem os casos da
  leitura aberta e escrevem, por caso, `licao_livre` e `causa_livre` (uma frase cada, em termos gerais). Gravam
  `leitura_aberta_candidata_<u>_<BASE_ID>.csv` e `leitura2_aberta_candidata_<u>_<BASE_ID>.csv`.
- **O gate da lista.** A skill grava as frases lado a lado
  (`concordancia.py <aberta1> <aberta2> --lado-a-lado resultados/mineracao/<u>/lista_lado_a_lado.md --mostrar licao_livre causa_livre`),
  agrupa as frases parecidas numa lista de categorias (cada uma com a frase que a define, a nula, `outra:<rótulo>` e
  `indeterminado`; em dois eixos, quando as frases misturarem "o que é" e "o que quebrou") e **para**: o pesquisador
  aprova ou edita a lista (`registrar_decisao.py --etapa lista`). A lista aprovada vai para o dossiê antes da etapa 2.
- **Etapa 2 · Leitura fechada.** Os dois leitores, às cegas, classificam **todos** os casos da leitura fechada (pelo
  menos 20, ou todos os que restam quando a população é menor) na lista aprovada, e escrevem também `licao_livre`.
  Gravam `leitura_candidata_<u>_<BASE_ID>.csv` (com `licao`, `causa`, `conserto`, `destino_lido`, `licao_livre`,
  `onde_no_cru`) e `leitura2_candidata_<u>_<BASE_ID>.csv` (com `licao`, `causa`, `licao_livre`, `onde_no_cru`).
- **A medida.** A concordância (`concordancia.py`) é medida por coluna, **sempre com
  `--registrar resultados/mineracao/<u>/confianca.json --nula sem_licao_unica`**, e a tabela lado a lado vai para o
  dossiê:
  ```
  concordancia.py <leitura1> <leitura2> --rotulo licao --nula sem_licao_unica --mostrar causa licao_livre --lado-a-lado resultados/mineracao/<u>/leitores_lado_a_lado.md --registrar resultados/mineracao/<u>/confianca.json
  ```
  O mesmo vale para cada regra contada no `testar_regra.py`: é desse arquivo que o painel lê a confiança.
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

## O que o dossiê leva ao gate do pesquisador

Depois da leitura fechada, a skill roda o painel (`valor_da_licao.py <pasta> <u>`). Nas situações com gate, ela **para**
e leva ao pesquisador, no dossiê:
1. **a lição principal**, com quanto da unidade ela cobre (a regra contada na população) e os papéis onde aparece;
2. **a tabela dos dois leitores lado a lado** (`leitores_lado_a_lado.md`), com a lição de cada um nas próprias
   palavras, as discordâncias primeiro;
3. **o resto:** as causas que não cabem na lição principal, cada uma com a contagem e a dúvida aberta (é do harness? é
   falso positivo da classificação?);
4. **as opções do gate**, que o painel imprime, e a recomendação.

A decisão é registrada com `registrar_decisao.py --etapa situacao`, com as palavras do pesquisador. "Os leitores
discordam" não quer dizer "não há lição": se a regra contada sustenta o padrão, a lição existe e o que está em aberto é
a redação dela.

## O arquivo final (o rascunho da memória)

Os campos são os do esquema da análise. Para cada um, a origem:

| Campo | De onde vem | Origem |
|---|---|---|
| `category` | a unidade e o tipo (a triagem) | `checado` (o `perfil.csv`) |
| `occurrences` | o `perfil.csv` (erros, ocorrências, execuções, meses) | `checado` (o comando do notebook genérico) |
| `location` | a lista da amostra (o `casos.csv` da evidência), capada em ~10 | `checado` (o comando do `montar_evidencia.py`) |
| `scope` | a sub-unidade que passa sozinha no G2 (papel, ferramenta); numa lição geral com variações por papel, os papéis com um exemplo de cada; `null` quando não restringe | `checado` se o G2 sustenta; senão `hipotese` |
| `evidence` | 2–3 casos da amostra, só estrutura (sem texto de caso) | `checado` (a pasta de evidência) |
| `description` | a lição principal (L1), a cobertura pela regra contada e a causa (L2), em uma ou duas frases | `checado` se uma regra contada sustenta; senão `hipotese` |
| `correction_guidance` | o que o agente deve fazer diferente (L1 como hábito, ou o fato a lembrar) | `hipotese`, até ser testado (as POCs) |
| `status` | `derived-and-checked` se `description` e `scope` estão `checado`; senão `hipotese` | — |
| `validation` | as contagens de cada passo e `destino` = L4 (proposta) | `checado` nas contagens; o destino é proposta |
| `impact` | `null` (decisão do `06` §9 Passo 8) | `pendente` |

O arquivo só é entregue depois de aprovado pelo `validar_memoria.py` da skill `mineracao-candidata`.
