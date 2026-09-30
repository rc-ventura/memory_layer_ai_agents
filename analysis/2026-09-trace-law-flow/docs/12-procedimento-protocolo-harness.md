# Procedimento — investigar a família "Protocolo do harness" numa base

**Para que serve este documento:** o roteiro para repetir, numa base nova (ou na base 2, onde está em andamento), a
investigação que fechou a base 1. Mesmo papel do [`03-procedimento-validacao.md`](03-procedimento-validacao.md), só para
esta família. O **porquê** de cada passo e o **catálogo de mecanismos** (M1–M5) estão em
[`10-racionais-protocolo-harness.md`](10-racionais-protocolo-harness.md); os resultados por base, em
[`11-relatorio-protocolo-harness.md`](11-relatorio-protocolo-harness.md).

**Regra de ouro (do 03):** nenhum número agregado sem um caso concreto que o sustente — e nenhuma leitura de caso antes
de conhecer a camada (modo, modelo, contrato).

## 0 · Pré-condições e o que sai da máquina

- Rodar de dentro da pasta `pipeline/` da base (`2026-09-trace-law-flow` ou `-second`), com o
  `resultados/erros_mecanismo.csv` já gerado pelo notebook. Na máquina 2, `uv run` na frente de cada comando.
- **Sai da máquina de compliance:** contagens, meses, nomes de papel, ferramenta e modelo, hashes de versão, sim/não,
  tamanhos e tokens. As saídas de `protocolo`, `protocolo` [7]/[8] e `metadados_steps.py` são só isso — podem ser
  fotografadas.
- **Não sai:** texto de caso, código do agente, nome de cliente, número de processo, `exec_id`. Os arquivos
  `resultados/evidencia/protocolo/erro_*.txt`, `prompt_*.txt` e `casos.csv` têm o caso em claro: **ler na máquina**.
  `resultados/` é git-ignored.

## Passo 1 — Contar: é incidente ou fundo?

```
python drill_down.py protocolo
```

Ler [1]–[6]: por mês (erros, por 1k steps, gatilho ≥ 2 casos/mês ou > 1/1k), por papel, mês × papel, forma, recuperação,
cascata.

- **Concentrado num período** (base 1: out/2025; base 2: ago/2026) → procurar a troca de configuração naquele período
  (passo 2).
- **Espalhado** → fundo do modo texto; ir direto aos casos (passo 4).
- Conferir: soma dos papéis = total; recuperação e cascata anotadas.

## Passo 2 — A camada: modo, modelo, contrato

1. **Modo** — `protocolo` [7]: por papel, as versões do formato do prompt, com modo (JSON × texto), meses, steps e erros.
   Um papel que alterna de modo e erra só em texto → incidente de modo (base 1).
2. **Modelo** — `protocolo` [8]: papel × modelo, com meses, steps, erros e taxa. Um modelo novo só no período do surto
   → incidente de modelo (base 2). O ideal é o "experimento natural": mesmo papel, mesmo mês, mesmo prompt, dois modelos.
3. **Contrato e texto do negócio:**
   - `python drill_down.py ferramenta <nome>` — as versões da declaração de uma ferramenta, com meses. Procurar
     ferramentas cujo nome ou descrição falem em "resposta final" (M2).
   - `python drill_down.py protocolo --prompt <versão>` — grava `prompt_<papel>_<versão>.txt`; ler **o fim**, antes de
     "Now Begin!": pede formato (markdown, JSON)? diz "pode responder diretamente"? define a resposta final como a saída de
     uma ferramenta? (M1)

Anotar a camada que explica o surto **antes** de ler casos.

## Passo 3 — O cenário de cobertura

Ordenar os papéis por número de erros e escolher até onde ir (base 1: 4 papéis = 33/33; base 2: RoteadorCivel sozinho =
56/69). A cobertura de um cenário fecha quando **cada erro dele** tem um mecanismo do catálogo, um mecanismo novo
(hipótese) ou está declarado "não lido".

## Passo 4 — Ler casos, papel por papel

```
python drill_down.py protocolo --casos <papel> [<versão>] [<quantos>]
```

Grava `erro_<papel>_<versão>_<k>.txt` (padrão 3 casos; escolhidos alternando entre as formas). Cada arquivo: cabeçalho
(papel, versão, modo, modelo, mês, idx), 1 system prompt exato, 2 observação anterior, 3 o que o modelo escreveu no lugar
do código, 4 erro, 5/5b step seguinte, 6 resposta final.

**Roteiro por caso** — anotar só a classificação:

| Pergunta | Seção | Opções |
|---|---|---|
| A. O que escreveu no lugar do código | 3 | resposta em texto/markdown · `final_answer(` sem `<code>` · só o plano · tag errada (```` ``` ````, `</code>` na abertura) · JSON do negócio · pergunta ao usuário · fragmento · vazio |
| B. O que havia antes | 2 | "(primeiro step do papel)" · observação normal · `Last output… None` · erro de ferramenta · JSON de uma ferramenta de "resposta final" |
| C. Step seguinte | 5 | recuperou? · chamou `final_answer`, outra ferramenta, nada · o mesmo conteúdo reembrulhado? |
| D. Fim do prompt | 1 | pede formato? "pode responder diretamente"? resposta final = saída de ferramenta? |

## Passo 5 — Metadados dos steps (quando o texto não basta)

```
python metadados_steps.py <papel> [<quantos steps>]
```

Lê os `erro_<papel>_*.txt` do passo 4 e, para cada caso, imprime os steps do papel (sempre até o seguinte ao último erro
de parse): tamanho do texto, do código, erro (`P` = parse), `finish_reason`, tokens de entrada/saída/raciocínio, filtro;
quantas vezes o papel foi chamado; e se a tarefa menciona "não foi possível" ou traz o molde `fluxo_encerramento`.

| Sinal | Leitura |
|---|---|
| texto/3 ≈ tokens de saída | o que o modelo gerou chegou — ler o texto (M1, M2, M3) |
| tokens de saída ≫ texto/3 | **M4** — o texto é um resto; não ler intenção nele |
| texto 0, erro "não", tokens > 0 | **M5** — step vazio silencioso; o erro seguinte é consequência |
| linha `cru:` — `content` da API = texto − 7 e os outros campos ∅ | a API entregou só aquilo (o `</code>` é do harness); nada foi para outro campo |
| linha `cru:` — algum outro campo grande (`tool_calls`, campo novo em `raw+`) | a resposta foi para um campo que o smolagents não lê |
| linha `cru:` — `raw vazio` | a execução não gravou a resposta crua; não dá para saber |
| `finish = length` | limite de tokens de saída |
| filtro = sim | filtro de conteúdo da API |
| papel chamado > 1 vez | ver se o erro está numa chamada posterior (cascata entre chamadas) |

## Passo 6 — Classificar no catálogo

Para cada caso, o mecanismo (M1–M5 do `10` §4) ou "novo". Um mecanismo novo precisa de: como reconhecer, gatilho,
casos que o sustentam — entra no `10` como hipótese. Resultado por papel: tabela papel × mecanismo, como o `11` §1.3.

## Passo 7 — Destino e registro

- Destino pela regra do `10` §5 (configuração → não-memória, plataforma; desenho do prompt/ferramenta → sinal de harness;
  sobra aprendível que se repete → memória candidata, com escopo).
- Registrar: resultados no `11` (seção da base); uma linha no livro-razão
  ([`../../pipeline-entre-bases.md`](../../pipeline-entre-bases.md), Etapa 10b); mecanismo novo no `10`.
- Monitor: gatilho do `04-roadmap.md` (≥ 2 casos/mês ou > 1/1k steps) e, a cada modelo novo num papel, conferir a taxa
  desta família (`protocolo` [8]).

## Conferências

- A soma por papel e por mês bate com o total de [1].
- Todo mecanismo atribuído aponta os casos (arquivo `erro_<papel>_<versão>_<k>`) que o sustentam.
- Leitura que depender só do texto de um step com M4 não vale como mecanismo.
- A base 1 é o teste de regressão: uma mudança no procedimento ou nos scripts tem que reproduzir o `11` §1.
