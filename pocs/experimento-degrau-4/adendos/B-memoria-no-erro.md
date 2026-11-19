> **Sub-atividade:** 1.6 / 1.7 · **Tipo:** Adendo de braço ao [plano do experimento](../01-plano-geral.md) · **Braço:** memória consultada no erro (middleware) · **Status:** rascunho · **Data:** 12/11/2026

# Adendo B — Memória consultada quando o erro aparece (middleware)

Este adendo é diferente do [adendo do sandbox](A-inventario-sandbox.md): aquele preenche o plano para **uma
unidade**; este detalha **um braço** do plano, o que vale para toda unidade. Ele existe porque o braço pede uma medida
própria e uma condição de poder que não cabem no corpo do plano, e porque, no plano principal, ele é
**confirmatório** (hipótese 5), com a condição de poder de B.5.

## B.1 A ideia

Os outros braços testam **ter a memória à mão**: na região `<memory>` desde o começo (antecipação) ou numa ferramenta que o
agente decide chamar. Este braço testa outra coisa: **reagir quando o erro aparece**. O agente começa sem memória; o erro
da unidade acontece; um middleware do harness reconhece o erro, **consulta o catálogo** pela unidade e pelo papel, e põe o
texto da memória na observação que o agente lê no passo seguinte.

| Momento | Braço | Quem decide a consulta | Pergunta |
|---|---|---|---|
| antes (antecipação) | injetada no contexto | o harness, ao montar o agente | basta ter a memória à mão? |
| durante, se o agente quiser | por ferramenta (`recall_memory`) | o agente | o agente sabe quando consultar? |
| **depois do erro** | **no erro (este adendo)** | **o harness, ao ver o erro** | **basta reagir quando o erro aparece?** |

Este braço **não testa recuperação nem antecipação**. O erro acontece uma vez, por construção, e a consulta parte da
assinatura do erro. O que ele pode reduzir é o que vem depois: o segundo erro e a cascata.

## B.2 O mecanismo

1. **Gancho.** `step_callbacks` do smolagents recebe o passo recém-executado e o agente, e pode alterar a observação.
2. **Reconhecer o erro.** O classificador do pipeline (o mesmo que mede o erro, §8.1 do plano) roda no resultado do
   passo. Sem LLM.
3. **Consultar.** Se o erro é o da unidade, o middleware busca no catálogo as memórias que valem para aquele papel, com as
   regras do catálogo: `nao_vale_em` exclui, `vale_junto_com` traz o par (num erro de `pandas`, entram as duas memórias,
   a do pandas e a dos imports).
4. **Entregar.** O texto literal da memória é anexado à observação, **no mesmo invólucro `<memory>`** dos outros braços,
   para que a única diferença seja o momento.
5. **Registrar.** O registro da execução guarda o passo em que o middleware disparou, qual memória entregou e a versão do
   texto.

A decisão é do harness. O agente não escolhe consultar e não vê a consulta acontecer, só vê a observação com a memória
dentro, como veria a mensagem de erro.

## B.3 A medida: reincidência, não "teve o erro?"

A medida principal do plano ("a execução teve o erro da unidade?") **não serve aqui**: com a memória chegando depois do
primeiro erro, a resposta é "sim" quase sempre. A medida é a **reincidência**:

> dado que a execução teve o primeiro erro da unidade, ela teve um segundo? (sim/não)

comparada com a do braço sem memória. Condicionar ao primeiro erro é válido **neste braço**, porque o primeiro erro vem
antes da entrega e acontece com a mesma probabilidade nos dois braços. O mesmo condicionamento **não** valeria para a
memória injetada, que muda a chance do primeiro erro. Medidas secundárias: o tamanho da cascata, os passos a menos
depois do primeiro erro, e os tokens e o tempo depois do primeiro erro (§8.2 e §8.3 do plano).

**Compensação.** O custo `c` é praticamente zero por construção: numa execução sem erro nada entra no contexto. A
pergunta passa a ser se a economia `s` (passos e tokens a menos depois do primeiro erro) é maior que zero, e quanto.

## B.4 Hipótese e expectativa

**Hipótese 5 do plano:** a memória consultada pelo middleware reduz a reincidência. Não evita o primeiro erro.

**Expectativa honesta.** A mensagem de erro do interpretador já diz o que faltou ("a variável `json` não está definida"),
e o agente costuma corrigir no passo seguinte sozinho. Por isso o ganho esperado é **pequeno onde o erro tem uma causa
só**, e **maior onde uma lição cobre dois erros em sequência**: o primeiro erro tem uma mensagem, o segundo é o que a
mensagem não anuncia. No inventário do sandbox, é o caso do par imports + pandas no papel JoogleAnalytics, onde 77% dos
erros de `pandas` são seguidos de outro erro. Em unidades sem esse padrão, é provável que o braço não mostre efeito, e
isso também é resultado.

**O que a literatura sustenta, e o que não.** O análogo publicado mais próximo é a terceira etapa do AgentDebug (Zhu et
al., 2025): injetar a orientação corretiva no passo crítico e continuar dali; a arquitetura do projeto já o registra
(componente C). Dois limites: o AgentDebug reexecuta a partir do passo e aplica sem gate, e este braço continua
adiante com a memória revisada. O DoVer (Ma et al., 2025) intervém no ponto da falha pelo mesmo princípio. Nenhum dos
dois mediu reincidência de um erro de ambiente como este.

## B.5 Poder: quantas execuções

Como a medida é condicional, o que conta é quantas execuções com o primeiro erro cada braço tem. Número por braço
(poder de 80%, bilateral), conforme a reincidência de base:

| Reincidência de base | redução de 50% (α = 0,05) | de 70% (α = 0,05) | redução de 50% (α = 0,01, se for corrigida com outras 4 comparações) |
|---:|---:|---:|---:|
| 77% | 25 | 13 | 37 |
| 50% | 58 | 27 | 87 |
| 30% | 121 | 55 | 180 |
| 20% | 199 | 90 | 297 |

Execuções com o primeiro erro esperadas por braço e por agente-espelho (240 tarefas-gatilho na versão cheia; 120 na
enxuta): com taxa do primeiro erro de 60%, 144 e 72; de 40%, 96 e 48; de 20%, 48 e 24.

**Condição de poder, calculada com o piloto.** O piloto (só o braço sem memória) mede duas coisas: a taxa do primeiro
erro e a reincidência de base. O braço só tem comparação válida num espelho se as execuções esperadas com primeiro erro
forem maiores que o número da tabela para aquela reincidência. Exemplo: reincidência de 50% pede 58 execuções (α = 0,05),
e 40% de primeiro erro dá 96 na versão cheia: cabe. Reincidência de 20% pede 199: não cabe, e o braço fica sem
conclusão naquele espelho. Para o braço, nenhuma execução a mais é rodada: os seis braços do plano já incluem este.

## B.6 Critério

O braço passa como **forma de entrega** de uma memória, num agente e num modelo, se:

1. **Eficácia.** A reincidência é menor que a do braço sem memória (intervalo de 95% da diferença sem incluir zero).
2. **Compensação.** A economia `s` é maior que zero, com intervalo que não inclui zero.
3. **Sem dano.** As mesmas guardas do §11 do plano: sucesso da tarefa, erros de outras unidades, latência.

**O que não se consegue concluir.** O placebo do plano fica na região `<memory>` desde o começo; ele não separa o
conteúdo da memória do efeito de "uma mensagem a mais depois do erro". Para isso falta um braço de **placebo no erro**:
no mesmo momento, a mesma região, um texto sem relação. É um sétimo braço, exploratório, que custa mais uma coluna de
execuções só nos espelhos em que a condição de poder for atendida. Sem ele, a conclusão fica "a reincidência cai quando
se anexa a memória", sem separar conteúdo de formato.

## B.7 Riscos e perguntas abertas

| Risco ou pergunta | Controle ou encaminhamento |
|---|---|
| A consulta duplica o que a mensagem de erro já diz, e o efeito é nulo | é a expectativa de B.4; por isso o braço tem unidade de interesse (o par) e a condição de poder |
| O classificador dispara onde não devia (falso positivo) e injeta a memória fora de hora | o disparo é registrado; segunda implementação do classificador (§12 do plano); amostra de execuções lida |
| O erro acontece e o agente já tinha corrigido no mesmo passo | o middleware age só sobre o passo que falhou; o passo seguinte é o do agente |
| **A plataforma real permite esse middleware?** O experimento o monta com `step_callbacks` do smolagents; se a plataforma não deixar o harness alterar a observação, o braço vale como teste de conceito, não como desenho de integração | pergunta para a revisão de integração (Sub 2.5): onde, na plataforma, um middleware desse tipo poderia ficar |
| A memória entregue depois do erro é lida como o texto de erro e não como memória | a região `<memory>` no mesmo invólucro dos outros braços; o braço "sem rótulo" do plano testa o rótulo |

## B.8 Decisão tomada

**O braço é confirmatório** no experimento 1 (12/11/2026), com a condição de poder de B.5: só vale como comparação
confirmatória no espelho em que o piloto mostrar reincidência suficiente; nos outros fica exploratório. A família do
experimento 1 passou a ter 5 comparações, e a amostra por braço sobe de 116 para 122 (taxa de base de 40%, redução de
50%); a versão cheia dá conta, no limite (126 execuções efetivas contra 122).
