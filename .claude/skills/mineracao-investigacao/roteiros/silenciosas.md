# Roteiro de investigação — falhas silenciosas

As perguntas que o procedimento das falhas silenciosas (`docs/*procedimento-falhas-silenciosas*.md`) deixa para leitura
de caso depois do determinístico. O porquê de cada uma está em `docs/*racionais-falhas-silenciosas*.md`. Use só as
categorias fechadas daqui; o que não couber é `indeterminado`, com uma palavra do porquê.

## S1 · O dono de um grupo com dono "a conferir"

*Quando abrir:* o relatório da rodada tem um grupo cujo dono o procedimento manda conferir (hoje, o `json_invalido`,
Passo 3), ou a forma do argumento (`drill_down.py silenciosas --forma <ferramenta>`) não decide sozinha.

- **População:** `pipeline/resultados/evidencia/silenciosas/casos.csv`, filtrada pelo grupo e pela ferramenta
  (`--onde grupo=<g> --onde ferramenta=<f>`).
- **Campo para ler e para a regra:** `code` (o step que chamou a ferramenta).
- **Categorias** (`dono`):
  - `plataforma`: o argumento quebrado veio pronto de outra ferramenta;
  - `agente`: o agente montou o argumento à mão;
  - `colado`: o agente colou um retorno impresso. É o gesto descrito no racional (§ da forma do argumento);
  - `indeterminado`.
- **Hipótese nula:** o grupo é homogêneo, e a forma que o determinístico já mede explica o dono.

## S2 · Candidato a sucesso falso: a resposta usou o dado que não veio?

*Quando abrir:* sempre que o relatório tiver candidatos a sucesso falso (Passo 5). É teto, não contagem.

- **População:** os candidatos de `casos.csv` (`--onde sucesso_falso_candidato=True`). A coluna do step final é
  `idx_final_depois`. Se a análise tiver um `desfechos.csv` de rodada anterior, ele traz sinais determinísticos
  (`usa`, `declara`, `guarda`) e a coluna `idx_final`, e pode servir de referência, mas a população é a do
  `casos.csv` desta base.
- **Campo:** `action_output` no step final do papel (`--coluna-idx idx_final_depois`); para o contexto, `code` no step
  da falha.
- **Dois eixos, não categorias exclusivas:**
  - `usa`: a resposta final depende do dado da ferramenta que falhou. Valores: `sim`, `nao`, `indeterminado`;
  - `declara`: a resposta diz ao usuário que a ferramenta falhou ou que o dado faltou. Valores: `sim`, `nao`,
    `indeterminado`.
  - Sucesso falso provável = `usa=sim` e `declara=nao`.
- **Hipótese nula:** o agente se recupera ou declara a falha, e o candidato não é sucesso falso.
- **Regra a propor:** para `declara`, uma regex de frases de falha declarada no `action_output`. Teste com o
  `testar_regra.py --lidos … --rotulo declara --alvo sim`.

## S3 · O que o `nao_reconhecido` é

*Quando abrir:* o grupo `nao_reconhecido` não está vazio (Passo 2), ou cresceu em relação à base anterior.

- **População:** `casos.csv --onde grupo=nao_reconhecido`.
- **Campo:** `observations` (onde está a mensagem da ferramenta).
- **Categorias** (`grupo_lido`): um dos grupos existentes da tabela de motivos do pipeline (o motivo só não casou a
  regra), `grupo_novo:<nome curto>` ou `indeterminado`.
- **Hipótese nula:** são motivos de grupos já existentes, e falta só palavra-chave na regra.
- **Regra a propor:** a palavra-chave que levaria os casos ao grupo lido, contada com `--campo-passo observations`.
  Antes de propor, a regra precisa casar o mesmo texto, ou o equivalente, em outra base. Regra olhando uma base só não
  entra.
