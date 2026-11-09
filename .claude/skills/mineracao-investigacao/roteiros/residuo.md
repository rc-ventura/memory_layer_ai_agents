# Roteiro de investigação — resíduo

As perguntas que o procedimento do resíduo (`docs/*procedimento-residuo*.md`, passos 3 a 5) deixa para leitura de
caso depois do determinístico. O porquê está em `docs/*racionais-residuo*.md`. Use só as categorias fechadas daqui; o
que não couber é `indeterminado`, com uma palavra do porquê.

**Um padrão por vez.** O pesquisador escolhe a ordem a partir do relatório da `mineracao-residuo`: primeiro os que
passam na recorrência, depois o topo de tokens. Cada pergunta abaixo é feita para **um padrão** de
`mineracao/residuo/residuo_padroes.csv`. As três vão em ordem: R2 só se R1 disse que o padrão é um erro só (ou depois
de dividi-lo), e R3 só se R2 disse `agente`.

**Para todas as perguntas:**
- **População:** `mineracao/residuo/casos.csv --onde "padrao=<padrão exato>"`.
- **Amostra e cru:** `montar_evidencia.py --nome inv_residuo_<n>_<BASE_ID> --de mineracao/residuo/casos.csv --onde
  "padrao=<padrão exato>"`. Leia todos se forem até 10; acima disso, `--regra primeiro-por-mes`.
- **O que ler:** a janela de cada caso (`drill_down.py caso <exec_id> <papel> <idx>`, ou o `derivados/` da evidência):
  a mensagem do erro, o código do passo, o passo anterior e o seguinte. Se a pergunta precisar do prompt ou do resto
  da execução, e a base só tiver a janela, a resposta é `indeterminado: fora da janela`.

## R1 · O agrupamento: é um erro só?

*Quando abrir:* sempre, para cada padrão escolhido. A máscara pode juntar erros diferentes, e a chave pode esconder
mecanismos diferentes (racional §2 e §5).

- **Campo:** a mensagem e o código do passo.
- **Categorias** (`agrupamento`):
  - `um_erro`: os casos são o mesmo erro, com a mesma causa;
  - `dividir:<critério curto>`: são dois ou mais erros, separáveis por um critério que se vê no texto (ex.: o motivo
    do parser, o nome da ferramenta, o tipo do valor);
  - `formato`: a mensagem não está no formato que a regra de parsing espera (coluna `linha_rejeitada_ok` falsa), e o
    erro só está no resíduo por isso;
  - `indeterminado`.
- **Hipótese nula:** o padrão é um erro só.
- **Regra a propor:** com `dividir`, a regex que separa as partes, contada com `testar_regra.py --populacao
  <casos.csv> --onde "padrao=<padrão>" --campo-csv mensagem --regex '<rx>'`. Cada parte volta ao R1 como um padrão
  próprio.

## R2 · De quem é a falha?

*Quando abrir:* depois de R1 = `um_erro` (ou para cada parte de um `dividir`).

- **Campo:** o código do passo (o que o agente escreveu) e a mensagem (quem levantou o erro).
- **Categorias** (`dono`):
  - `agente`: o código que ele escreveu ou o jeito como chamou a ferramenta;
  - `harness`: o interpretador ou o harness não suporta algo, ou limita (passos, tempo, import);
  - `infra`: a ferramenta, a rede, a API ou o serviço falhou, e o agente fez certo;
  - `llm`: um limite do modelo (resposta cortada, formato);
  - `indeterminado`.
- **Hipótese nula:** a falha é do agente.
- **Destino que decorre:** `agente` → R3. `harness`, `infra` e `llm` → uma unidade `H_*` nova, tipo não-memória (o
  procedimento, passo 4). O nome e a frase da unidade ficam para o pesquisador.

## R3 · Que unidade?

*Quando abrir:* depois de R2 = `agente`.

- **Campo:** o código do passo e a lição que evitaria o erro.
- **Categorias** (`unidade`):
  - `estender:<unidade>`: uma unidade que já existe no `SUB2UNI` do `base_pipeline.py` da análise já tem a lição; a
    regra dela só não reconhecia esta mensagem;
  - `unidade_nova:<nome curto>`: nenhuma unidade tem a lição. Dê o tipo (factual · ambiente ou experiencial ·
    estratégia) e o conteúdo numa frase;
  - `indeterminado`.
- **Hipótese nula:** a lição já existe numa unidade (a regra só não alcançou).
- **Regra a propor:** a regex sobre a mensagem que levaria os casos à unidade, contada com `testar_regra.py
  --campo-csv mensagem` **na população inteira do resíduo** (sem `--onde padrao`): quantos do padrão ela pega, e
  quantos de outros padrões. A conta só diz o alcance dentro do resíduo. Onde a regra entra no `submecanismo()` decide
  se ela alcança outras unidades (procedimento, passo 6).

## O que o dossiê entrega

Para cada padrão:
- R1, R2 e R3, com a concordância dos dois leitores;
- a regra proposta, com a contagem `[conferido]`;
- a pasta de evidência.

**A regra é uma proposta.** Ela muda número publicado, então é um Ajuste: a interpretação se fecha com o pesquisador,
a proposta de código vem depois, e a mudança só depois da aprovação.
