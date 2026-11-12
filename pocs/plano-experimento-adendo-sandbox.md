> **Sub-atividade:** 1.6 / 1.7 · **Tipo:** Adendo de unidade ao [plano do experimento](plano-experimento-validacao-memorias.md) (ficha do §16) · **Unidade:** Inventário do sandbox · **Status:** rascunho · **Data:** 12/11/2026

# Adendo A — Inventário do sandbox

**O que é essa unidade.** O *sandbox* é o interpretador Python restrito onde o código do agente roda: ele aceita certos
módulos e barra certas funções. A unidade reúne os erros em que o agente **usa algo que o ambiente barra** (por exemplo,
`repr`) ou **esquece de importar algo que o ambiente aceita** (por exemplo, `json`). É a primeira unidade que fechou no
degrau 3 da validação.

> Tudo o que está aqui é específico desta unidade; o protocolo é o do [plano](plano-experimento-validacao-memorias.md),
> e os números de seção (§8.2, §9.2…) apontam para ele. Os termos do projeto estão no [glossário](../analysis/glossario.md).
> A fonte de cada fato é o [dossiê do sandbox](../analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/dossie_base3.md)
> e o catálogo [`memorias.json`](../analysis/registros/memorias.json); o identificador de cada memória no catálogo vem
> entre parênteses.

## A.1 Unidade e memórias (ficha 16.1)

**As partes da unidade.** A mineração dividiu o sandbox em partes, e cada parte gerou memórias com lição e escopo
próprios (global, ou de um papel). São 16 entradas no catálogo:

| Parte | O erro | Memórias | Situação |
|---|---|---|---|
| B | importar uma ferramenta como se fosse módulo | 2, por papel (OBFCivel, RespostaBacen) | monitoradas: a do OBFCivel é de reforço, a do RespostaBacen é rara |
| C | usar um módulo sem importá-lo | 3: a global (`json`, `re`, `datetime`), a do JoogleAnalytics (`pandas`), a do CalculoTrabalhista | **a global e a do JoogleAnalytics vão para o teste**; a do CalculoTrabalhista é rara |
| D | importar algo fora da lista autorizada | 10, uma por papel | monitoradas, de reforço |
| E | chamar funções ou atributos que o interpretador barra | 1, global | **vai para o teste** |
| F | verificar se uma variável existe | nenhuma | foi inteira para a futura memória de verificação de existência (roadmap da base 3, #51) |

A unidade fechou no degrau 3 em 09/11/2026. Três memórias estão prontas para o degrau 4. Neste adendo elas têm nome:

| Nome neste adendo (id no catálogo) | Onde vale | Texto literal (o `correction_guidance`) | Revisão (degrau 3) | Erros · execuções · meses |
|---|---|---|---|---|
| **Memória dos imports** (`U_sandbox.C`) | todos os papéis, **menos o `managerAgent`** (campo `nao_vale_em`) | "Importe antes de usar: import json, import re, import datetime." | 04/11/2026; causa confirmada em 30 de 30 casos lidos | 423 · 422 · 10 |
| **Memória do pandas** (`U_sandbox.C.JoogleAnalytics`) | papel `JoogleAnalytics`; **só vale junto com a memória dos imports** (campo `vale_junto_com`) | "Importe antes de usar: import pandas as pd." | 04/11/2026; 30 de 30 | 231 · 231 · 6 |
| **Memória das funções proibidas** (`U_sandbox.E`) | todos os papéis | "Não chame: repr, dir, exec, __import__, bytes, open, hash; Não acesse: __name__, __class__, __doc__, __len__. Para inspecionar um valor, use print(type(x)) e print(str(x)[:n])." | 09/11/2026; 27 de 30 (as 2 discordâncias relidas) | 317 · 314 · 9 |

O hash de cada texto é gravado no pré-registro (etapa 4), a partir do catálogo.

**Por que a memória do pandas só vale junto com a dos imports.** No JoogleAnalytics a linha que falha esquece dois
imports, `pandas` e `json`: o `json` aparece na instrução que falhou em 231 de 231 erros. Nos 10 casos lidos, 5 importam
só o `pandas` e caem no `json` não definido (99 na população). O bilhete "import pandas as pd" sozinho corrige só o
primeiro erro. Por isso as duas são testadas como par (dossiê §2h, 31).

**Por que as outras 13 ficam fora dos braços confirmatórios.** Ficaram no degrau 1, monitoradas, não injetadas, por
dois motivos (decisões de 20/10 e 22/10, [`decisoes.md`](../analysis/decisoes.md)):

- **11 de reforço — repetiriam o prompt.** As 10 da parte D: a lista de imports autorizados já está no prompt de cada
  papel ("You can use imports in your code, but only from the following list of modules: [...]"), e o agente importa
  fora dela mesmo assim. Uma memória "só importe da lista" repetiria a instrução, o que reprova a checagem 3 do degrau 2.
  A do OBFCivel na parte B também repete o prompt. As 11 alimentam o braço exploratório "memória de reforço" (o
  experimento de reforço do blueprint): a pergunta é se repetir a instrução perto do ponto de uso ajuda, e ela é outra
  pergunta que a do teste confirmatório.
- **2 raras — poucos casos.** A do RespostaBacen (1 erro, 1 mês) e a do CalculoTrabalhista na parte C (2 erros, 1 mês)
  ficam abaixo da régua de memória rara (pelo menos 3 execuções em pelo menos 2 meses). Seguem vigiadas: se crescerem,
  viram candidatas.

## A.2 Erro-alvo (ficha 16.2)

| Memória | O erro-alvo (o que o classificador conta) |
|---|---|
| dos imports | passo cuja linha usa `json`, `re` ou `datetime` sem importá-los (a parte "módulo usado sem import" da unidade) |
| do pandas | o mesmo, para `pd` (`pandas`), no papel `JoogleAnalytics` |
| das funções proibidas | passo cuja linha chama uma função ou acessa um atributo que o interpretador barra e que está na lista da memória (a parte "funções e atributos proibidos") |

O classificador é o do script específico da mineração do sandbox, o mesmo que gerou as contagens. **Fora do erro-alvo
da memória das funções proibidas** ficam `globals`, `locals`, `vars` e a verificação de existência de variável instruída
pelo prompt: isso é sinal de harness (a unidade de verificação de existência), e a memória deixa essas funções de fora
de propósito (roadmap da base 3, #51).

## A.3 Onde os erros moram (ficha 16.3)

| Memória | Papéis (erros) | Fonte |
|---|---|---|
| dos imports (`json`) | 10 papéis; **RoteadorCivel 241**, JoogleAnalytics 105, CalculoTrabalhista 41 (soma 415 de `json`); mais `re` 5 e `datetime` 3 | dossiê §1, parte C |
| do pandas (`pd`) | **JoogleAnalytics 231** (de 233 de `pd` na base 3; os outros 2 são do CalculoTrabalhista) | dossiê §1, parte C; catálogo |
| das funções proibidas | concentrada no **ContestacaoCivel** (450 de 523 na leitura do dossiê de 19/10, antes dos ajustes seguintes) e, nos outros papéis, `repr` e `dir` em depuração; 92% dos erros são inspeção de valor | dossiê §2e–§2h, 26/10 |

**Falta (etapa 1):** a incidência `π` por papel e mês (execuções com o erro ÷ execuções do papel); a divisão por papel
da memória das funções proibidas com os números atuais (317); o teto de economia por papel e memória; a duração mediana
do passo com erro por papel. Nenhum desses números foi calculado para este plano.

Fatos sobre o comportamento do erro que moldam o desenho:

- O agente quase não repete o erro do `json` na mesma execução (5 casos); o que se evita é **um passo perdido** por erro
  (dois no par `pandas` + `json`). O ganho por execução é pequeno, e o custo da injeção precisa ser menor ainda.
- No JoogleAnalytics, 77% dos erros de `pandas` têm outro erro em seguida (o `json`), o que é a razão do par.

## A.4 Tipo da lição (ficha 16.4)

**Fato do ambiente** (o que o interpretador aceita), com chave por papel. Duas consequências:

- A hipótese 3 (a ferramenta perde para a injetada) vale como está escrita; é a unidade em que ela foi pensada.
- O espelho reproduz o erro **sem precisar do contrato de nenhuma ferramenta**: basta o mesmo interpretador. O smolagents
  1.26.0 reproduz os erros do sandbox localmente (`pipeline/validacao/historico/testar_sandbox_*.py`); a versão da
  plataforma não é conhecida (limite).

Cuidado próprio: a lista de imports do prompt e a do interpretador podem divergir. O `json` roda sem estar na lista do
prompt (531 de 531 nas bases 1 e 2), porque um interpretador passado de fora não recebe a lista do agente. A ficha de
fidelidade registra as duas, e o espelho usa a do **interpretador** (decisão registrada no livro-razão, Ajuste 28).

## A.5 Agentes-espelho (ficha 16.6)

| Agente-espelho | Papel real | Por que é prioritário | Memória testada | Tarefa-gatilho (sem citar o objeto da lição) |
|---|---|---|---|---|
| **Roteador** | RoteadorCivel | 241 dos 415 erros de `json` sem import | dos imports | a ferramenta devolve um registro como texto JSON; o agente lê campos e decide um destino |
| **Analítico** | JoogleAnalytics | 231 erros de `pandas` e 105 de `json`, na mesma linha | o par: dos imports + do pandas | a ferramenta devolve linhas como texto JSON; o agente monta uma tabela e calcula agregados |
| **Calculista** | CalculoTrabalhista / ContestacaoCivel | inspeção de valores com `repr`, `dir`, `__name__` | das funções proibidas | cálculo em vários passos sobre um retorno aninhado, cuja forma o agente precisa descobrir |

**Suposição de desenho, a confirmar na etapa 1:** o texto JSON é a escolha de trabalho porque o `json` só é necessário
quando há algo a desserializar. O formato real do retorno das ferramentas do RoteadorCivel e do JoogleAnalytics não foi
conferido para este plano; ele vem da ficha de fidelidade (base 2). Se for outro, a tarefa-gatilho muda, e o erro-alvo
(esquecer o import) não.

**Tarefas neutras:** as que se resolvem sem nenhum dos módulos (nos dois primeiros) e sem inspecionar o valor (no
terceiro).

**Regra do injetor.** A memória dos imports não entra em nenhum espelho do `managerAgent` (`nao_vale_em`); a memória do
pandas só entra junto com a dos imports. Nenhum espelho copia o `managerAgent`.

**Fichas de fidelidade.** Fontes: `extrair_ambiente_base2.py` e a tabela `imports_autorizados.csv` da mineração do
sandbox. As listas de imports são 6, e variam por papel: `pandas`, `numpy` e `dateutil` só existem para CalculoTrabalhista
e JoogleAnalytics. Cada espelho usa a lista do papel que copia.

## A.6 Modelos (ficha 16.5)

| | Modelo | De onde vem |
|---|---|---|
| **Antigo** | `gpt-4.1-2025-04-14` | Base 1: todos os passos do RoteadorCivel (131), do JoogleAnalytics (10) e do CalculoTrabalhista (68) com o campo. Base 2: RoteadorCivel de maio a agosto |
| **Atual** | `gpt-5.6-terra-2026-07-09` (RoteadorCivel e OBFCivel, só em agosto) e `gpt-5.2-2025-12-11` (ContestacaoCivel) | Base 2, lote de agosto/2026 |

**Falta:** o modelo atual do JoogleAnalytics e do CalculoTrabalhista não aparece nas bases de que se dispõe; e em que
modelo cada erro das três memórias aconteceu. Ambos são da etapa 1 (a base 2, para agosto).

## A.7 Hipóteses e braços próprios (ficha 16.9)

Além das hipóteses do plano (§4):

| # | Hipótese da unidade | Tipo | Como se testa |
|---|---|---|---|
| S1 | No par, a memória do pandas **sozinha** corrige só o primeiro erro: o `json` continua faltando e o erro seguinte aparece | exploratória | braço "só pandas" no espelho Analítico, contra o par |
| S2 | A "memória no erro" (hipótese 5) encurta a recuperação no par: ao primeiro erro, entrega as duas lições e evita o segundo passo perdido | exploratória | tamanho da cascata no espelho Analítico (§8.4) |
| S3 | A memória das funções proibidas troca `repr` e `dir` por `print(type(x))` sem empurrar o agente para outra função barrada | confirmatória (é a guarda do §8.5, item 2, para esta unidade) | taxa de erros de funções barradas fora da lista da memória |

Braços exploratórios do §6.1 desta unidade:

- **conserto no ambiente:** o módulo já importado no interpretador (`json`, `re`, `datetime`, `pd`) e uma ferramenta
  `inspecionar(x)` no lugar de `repr` e `dir`. É o teto prático da hipótese 6: o que o sinal de harness da unidade pediria.
- **carga de memória:** todas as entradas do catálogo que valem no papel (das 16 da unidade), para a hipótese 7.

Os braços exploratórios, incluindo o "só pandas" da hipótese S1, não entram nos totais do A.8: rodam depois, com
amostra menor, como diz o §6.1 do plano.
- **memória de reforço:** as 11 de "import fora da lista", que só repetem o prompt (experimento de reforço do blueprint).

## A.8 Tamanhos e custo (ficha 16.8)

Três agentes-espelho. Pela fórmula do §9.2:

| | Por agente-espelho | Total (3 espelhos) |
|---|---:|---:|
| **Piloto** (só o braço "sem memória", 130 por modelo) | 130 por modelo | **390 por modelo; 780 nos dois** |
| **Replay de passo** (300 chamadas por memória) | — | **900** (3 testes: a dos imports, o par imports + pandas, a das funções proibidas) |
| **Confirmatório, versão cheia** | 2.160 | **6.480** |
| **Confirmatório, versão enxuta** | 1.080 | **3.240** |
| **Checagem no outro modelo** (2 ÷ 6 do total) | — | 2.160 (cheia) ou 1.080 (enxuta) |

Conferência da guarda do sucesso, com os três espelhos juntos: 3 × 360 = 1.080 execuções por braço na versão cheia, cerca
de 570 efetivas, acima das 446 que a guarda pede (§9.2).

**Custo (hipótese, a medir no piloto):** a ordem de 100 a 160 milhões de tokens na versão cheia, e a metade na enxuta.

## A.9 Etapas e prazo

O prazo é o do §10: cerca de 20 dias úteis para esta unidade, por ser a primeira (a etapa 0 e o executor entram na
conta). Específico desta unidade:

- **Etapa 1:** na **base 3**, por papel (RoteadorCivel, JoogleAnalytics, CalculoTrabalhista, ContestacaoCivel) e mês: as
  execuções com cada erro e as sem. Na **base 2**: o modelo de cada erro das memórias dos imports e das funções
  proibidas em agosto, e o prompt e os imports de cada papel para as fichas. Os scripts de contagem por papel e mês são
  a escrever (aqui, na base 1; depois no ambiente).
- **Etapa 2:** os três geradores de tarefa e os verificadores. As tarefas-gatilho do Roteador e do Analítico precisam de
  algo a desserializar; o formato exato vem das fichas da etapa 1 (A.5).

## A.10 Riscos próprios (ficha 16.10)

| Risco | Controle |
|---|---|
| A lista do prompt e a do interpretador divergem, e o espelho fica com a errada | a ficha registra as duas; vale a do interpretador (A.4) |
| O smolagents local (1.26.0) não é o da plataforma | declarado como limite; a trilha 2 é a resposta |
| A memória das funções proibidas conflita com o prompt do ContestacaoCivel, que manda verificar a existência de variável (e o sandbox barra as duas formas) | o espelho Calculista não leva essa instrução: ela é sinal de harness, fora do erro-alvo (A.2). Limite declarado: o espelho não reproduz esse conflito |
| O espelho Analítico depende do par: sem a memória dos imports, a do pandas sozinha parece falhar | o par é a unidade de teste (A.1); a hipótese S1 mede a diferença |
| A memória dos imports é injetada num papel onde não vale | o injetor lê o `nao_vale_em` (§6) |

## A.11 Decisões abertas (ficha 16.11)

1. **Os três agentes-espelho** são os certos? A escolha saiu dos papéis com mais erros das três memórias; o Calculista
   junta CalculoTrabalhista e ContestacaoCivel, e o primeiro tem poucos erros da memória das funções proibidas nos
   números de que se dispõe.
2. **A memória da ferramenta de documento** (o grupo de erros do retorno de documento, base 1) entra como exploratória?
   Ela não está no catálogo nem passou pelos degraus 2 e 3.
3. **O modelo atual** do JoogleAnalytics e do CalculoTrabalhista (A.6) precisa ser pedido à base 2.
