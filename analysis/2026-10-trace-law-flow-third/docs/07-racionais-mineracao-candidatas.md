# Racionais — minerar uma candidata a memória (o porquê de cada passo)

> Códigos e siglas: [glossário](../../glossario.md). O passo a passo com os comandos:
> [`06-procedimento-mineracao-candidatas.md`](06-procedimento-mineracao-candidatas.md). O racional de cada lição
> (a regra dela e os limiares): `propostas/<u>/racional.md`. A origem do método, na base 1:
> [`16`](../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md) e
> [`06` §9–§10](../../2026-09-trace-law-flow/docs/06-racionais-mineracao-unidades-n2-n10.md).

**Atualizado:** 16/10/2026 · **Branch:** `2026-10-16-base3-comparar-rodadas`.

**Para que serve:** minerar uma lição é transformá-la num arquivo de memória com estrutura fixa: o que o agente deve
fazer diferente, onde vale, a evidência e o destino proposto (memória × harness). Este documento explica **por que**
cada passo existe e quando ele para a mineração. Vale para qualquer lição; o que é próprio de uma lição (a regra que
lê o erro, os limiares) mora no racional dela, escrito **antes** de rodar.

**Três camadas, um documento cada:**

| Camada | Documento | Diz |
|---|---|---|
| O porquê, para toda lição | este | o que cada passo garante e quando para |
| O como, para toda lição | o procedimento `06` | o comando de cada passo (pela skill ou à mão) |
| O que é da lição | `propostas/<u>/racional.md` | a regra específica, o limiar de cobertura, como o arquivo final é montado |

---

## Os passos

### 1 · Conferir a rodada

**O que garante:** que a mineração lê números conferidos. A rodada (`executar.py analisar`) grava cada tabela com o
hash no manifesto; uma tabela mexida depois não é lida.
**Para se:** a rodada não está concluída, um artefato está fora do manifesto, a lição não está entre as candidatas
da triagem ou o perfil dela não foi gravado.

### 2 · Monitoramento

**O que garante:** que uma lição que o pesquisador decidiu monitorar não seja minerada como se nada tivesse mudado. É a
única comparação com outra base que a mineração faz, e é de propósito (a linha de base foi registrada por ele).
**Para se:** um alerta. A lição volta ao pesquisador.

### 3 · A parte genérica

**O que garante:** a mesma descrição para toda lição: recorrência e escopo, sub-unidades, o que vem antes, o que vem
depois, estabilidade no tempo e a população. Ela descreve a lição, não a escreve.
**De onde vem:** do perfil da lição na rodada (`perfis/<u>/`), sem recalcular: o que já foi conferido não se refaz.

### 4 · A parte específica

**O que garante:** o conteúdo da lição, extraído por uma regra **determinística** escrita no racional dela (nenhum LLM
no caminho da contagem). O funil (a tabela do procedimento) diz qual é: um script (`script:<nome>`) ou a investigação
por leitura de casos (`investigação:candidata`).
**Por que um script, e não um notebook:** roda por comando, entra na suíte de testes e grava manifesto (livro-razão,
Ajuste 20).

### 5 · A confiança da regra

**O que garante:** que a regra pega o que diz pegar. Há dois jeitos, conforme a lição:
- **a regra lê só a mensagem de erro** (um nome, um tipo): a confiança é a **cobertura**, os erros em que a regra acha
  o que procura ÷ os erros da população, com o limiar escrito no racional antes de rodar;
- **a regra precisa de leitura de caso:** dois leitores às cegas, concordância e regras contadas (`16`, "A regra de
  criação").

**Para se:** a confiança abaixo do limiar. As tabelas ficam gravadas, o arquivo final não, e a lição volta à
investigação.

### 6 · Os números para o destino

**O que garante:** que a decisão memória × harness tem fatos. A memória ensina o agente; o harness muda o ambiente ou o
prompt. As perguntas típicas: o fato é igual em todos os papéis e meses (então é configuração, e talvez o lugar seja o
prompt)? O agente repete o erro na mesma execução (então não aprende sozinho)? Cada racional de lição diz as suas.
**Quem decide:** o pesquisador. O passo só conta.

### 7 · A auditoria independente e o encontro

**O que garante:** que os números não são um artefato do código que os produziu. "Re-rodar não é verificar": a
auditoria é uma **segunda implementação**, escrita a partir do racional da lição, sem importar o pipeline nem o script,
lendo a fonte crua. O encontro compara medida a medida: a população, a confiança e as tabelas da lição.
**Para se:** qualquer medida diferir. **A divergência é o achado**: não se conserta para fechar.

### 8 · O arquivo final

**O que garante:** que toda memória tem a mesma estrutura e diz de onde veio cada campo (`checado`, com o comando que
o reproduz, ou `hipotese`). O esquema é [`registros/esquema-memoria.json`](../../registros/esquema-memoria.json)
(0.2): na base 3, cada caso é apontado por `exec_id` + `step_ref` + `fonte_id` + `rodada_id`.
**Por que não o `idx`:** o número do passo na trajetória não existe na base 3 (a extração só traz os passos com erro);
o `step_ref` aponta o passo, e a fonte e a rodada dizem de onde ele veio (livro-razão, Ajuste 19).
**Para se:** o `validar_memoria.py` reprova.

### 9 · A saída

**O que garante:** que cada número pode ser refeito e que nada sigiloso sai. O manifesto da mineração guarda o hash
dos códigos, da rodada e da fonte lidas e de cada arquivo gravado. O relatório completo (com a evidência) fica no
ambiente; sai a versão varrida e um resumo só com contagens e nomes.

---

## O gate do pesquisador

A mineração termina em três decisões que não são do script: **a lição** (o texto da `correction_guidance` está bom?),
**o destino** (memória, harness ou monitorar) e, quando a confiança passa por cobertura, **a criação do script** (a
regra de criação aceita a decisão do Rafael, registrada em [`decisoes.md`](../../decisoes.md)). Cada decisão fica
registrada com as palavras dele (`registrar_decisao.py`).
