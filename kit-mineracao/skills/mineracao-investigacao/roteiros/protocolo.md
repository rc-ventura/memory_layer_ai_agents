# Roteiro de investigação — protocolo do harness

As perguntas que o procedimento do protocolo (`docs/*procedimento-protocolo-harness*.md`) deixa para leitura depois do
determinístico. O catálogo de mecanismos e a regra de destino estão em `docs/*racionais-protocolo-harness*.md`. Use só
as categorias fechadas daqui; o que não couber é `indeterminado`, com uma palavra do porquê.

**Antes de ler qualquer caso, a camada** (regra de ouro do procedimento): o relatório da rodada já tem o modo
(`versoes.csv`) e o modelo (`modelos.csv`) do período. Leia-os primeiro.

## P1 · A camada do surto: o que o fim do prompt pede?

*Quando abrir:* o relatório achou um período concentrado (o gatilho do passo 1), e o modo ou o modelo não explicam
sozinhos.

- **População:** as versões do formato dos papéis com erro no período: `evidencia/protocolo/versoes.csv`, filtrada
  por papel. Uma leitura por versão.
- **O que ler:** `uv run python drill_down.py protocolo --prompt <versão>` grava `prompt_<papel>_<versão>.txt`. Leia
  **o fim**, antes de "Now Begin!".
- **Categorias** (`fim_do_prompt`, a pergunta D do procedimento):
  - `pede_formato`: pede markdown ou JSON na resposta;
  - `responder_direto`: diz que pode responder diretamente;
  - `final_e_ferramenta`: define a resposta final como a saída de uma ferramenta (o M2 do catálogo);
  - `nenhum` ou `indeterminado`.
- **Hipótese nula:** a camada (modo ou modelo) já explica o surto, e o texto do prompt não acrescenta.
- **Evidência:** os arquivos `prompt_*.txt` (o cru do prompt, no ambiente) e, por versão, a linha da `versoes.csv`.
  A amostra é a lista de versões. Não há casos de execução a montar.

## P2 · O mecanismo de cada caso

*Quando abrir:* sempre que houver erros nos papéis do cenário de cobertura que o pesquisador escolheu (a parada P0).

- **População:** `evidencia/protocolo/casos.csv --onde role=<papel>`, um papel por vez, na ordem da cobertura.
- **Amostra e cru:** `montar_evidencia.py --nome inv_protocolo_<papel>_<BASE_ID> --de evidencia/protocolo/casos.csv
  --onde role=<papel>`.
- **O que ler:**
  - `uv run python drill_down.py protocolo --casos <papel> [<versão>] [<quantos>]`, que grava `erro_<papel>_*.txt`
    com o prompt, a observação anterior, o que o modelo escreveu, o erro, o step seguinte e a resposta final;
  - `uv run python metadados_steps.py <papel>`, com os tamanhos, os tokens e o `finish_reason`.
  - **Antes de ler uma sequência**, confira as colunas `chamada`/`chamadas_do_papel` do caso: a seção 2 pode ser o
    fim da chamada anterior.
- **Perguntas por caso**, as A/B/C do procedimento, anotadas como colunas da leitura:
  - `escreveu` (A): `texto`, `final_answer_sem_code`, `so_plano`, `tag_errada`, `json_do_negocio`,
    `pergunta_ao_usuario`, `fragmento`, `vazio`;
  - `antes` (B): `primeiro_step`, `observacao_normal`, `last_output_none`, `erro_de_ferramenta`, `json_de_resposta_final`;
  - `seguinte` (C): `recuperou`, `final_answer`, `outra_ferramenta`, `nada`, `reembrulhou`.
- **Categoria** (`mecanismo`): um dos mecanismos do catálogo (`M1` … `M6`), `novo:<nome curto>` ou `indeterminado`.
  Quando dois mecanismos se aplicam, vale o desempate escrito no catálogo (ex.: erro depois da ferramenta de resposta
  final **e** reembrulhado no step seguinte é resposta final fora do lugar, não a ferramenta concorrendo).
  Leitura que dependa só do texto de um step com `sinal_resto` não vale como mecanismo: o texto é um resto.
- **Hipótese nula:** os mecanismos do catálogo explicam todos os casos do papel.
- **Já vêm prontas no `casos.csv`**, sem precisar propor: o M1 (`sobreposicao_final ≥ 0.5`) e o M2 pela regra
  (`regra_ferramenta_final`: o step anterior chamou uma ferramenta cujo nome a apresenta como resposta final, e sem
  reembrulho). Confira a leitura contra elas com `--condicao "regra_ferramenta_final == 'True'"`.
- **Regras a propor e contar** para os outros mecanismos (`testar_regra.py`, com `--lidos … --rotulo mecanismo --alvo <M>`):
  - o M1 já é medido: `--condicao "sobreposicao_final >= 0.5"`;
  - M4 e M5 são regras numéricas sobre `chars` e `tok_out`, por exemplo `--condicao "chars < 20 and tok_out > 0"`
    para o M5;
  - formas do texto: `--regex` com `--campo-passo model_output`;
  - o que veio antes do erro: `--regex` com `--campo-passo code --deslocamento -1` (ex.: "o step anterior chamou a
    ferramenta que se apresenta como resposta final");
  - **o sinal de resto vem pronto** na coluna `sinal_resto` do `casos.csv`. Ele compara o texto por token do step com
    o normal do próprio papel na mesma execução, e não com um valor fixo, por isso vale também para modelos de
    raciocínio. Com o sinal, não leia intenção no texto: o caso é `indeterminado`, ou o mecanismo vem de um sinal
    estrutural (por exemplo, a ferramenta chamada no step anterior), nunca do texto.
- **Destino** (nas opções do dossiê, pela regra do racional): configuração → não-memória (plataforma); desenho do
  prompt ou da ferramenta → sinal de harness; sobra aprendível que se repete → memória candidata, com escopo.
  Mecanismo novo: como reconhecer, gatilho e os casos que o sustentam (os `#` da tabela de evidência), para o
  pesquisador decidir se entra no catálogo.
