# Miller — Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations

**arXiv:** 2411.00640v1 [stat.AP], 1 nov. 2024 (data no PDF: 4 nov. 2024) · **Autor:** Evan Miller (Anthropic) · **Venue:** nenhum informado no PDF (preprint); só a v1 foi lida · **14 páginas**, com 3 apêndices.

> **Nível de leitura: 🔎 — texto completo lido por um agente em 12/11/2026; falta o ✅ (a leitura do Rafael).**
> Não colapsar em "lido" em nenhum entregável. Método: `curl` no PDF + `pdftotext -layout` (como no [README](README.md)); o texto extraído foi lido inteiro, apêndices incluídos. Autoria, arXiv ID e data conferidos contra a primeira página do próprio PDF. Todo número e toda fórmula abaixo vêm do PDF v1; as páginas são as do PDF. O que é derivação ou leitura minha vai marcado **[derivação minha]** ou **[inferência minha]**.

---

## O que é

Um artigo de **estatística de avaliação**, não de taxonomia de erro nem de memória. A tese: avaliações de LLMs são experimentos, e a literatura de avaliações ignorou a de análise e planejamento de experimentos (resumo, p. 1). O artigo ensina, para quem tem alguma base de estatística, a calcular erro-padrão, comparar dois modelos e planejar o tamanho de uma avaliação.

A hipótese de base é que as perguntas de uma avaliação foram **sorteadas de uma super-população** de perguntas que não vemos (§2, p. 2): o objeto de inferência é a habilidade que a avaliação quer medir, não aquele conjunto de perguntas.

Os exemplos de scores (MATH, HumanEval, MGSM, "Galleon" × "Dreadnought") são **hipotéticos**; só a Tabela 4 usa "números não ficcionais", de modelos da Anthropic (p. 4).

## As cinco recomendações (p. 2)

1. Calcular o erro-padrão da média pelo Teorema Central do Limite.
2. Quando as perguntas vêm em grupos relacionados, usar erro-padrão **agrupado** (clustered).
3. Reduzir a variância **reamostrando as respostas** e analisando probabilidades do próximo token.
4. Ao comparar dois modelos, fazer inferência sobre as **diferenças pareadas por pergunta**, não sobre os resumos de cada população.
5. Usar **análise de poder** para saber se uma avaliação (ou um subconjunto sorteado) consegue testar a hipótese de interesse.

## O núcleo: a decomposição da variância (§2.1 e §3, p. 2–5)

O score de uma pergunta é `s_i = x_i + ε_i`: uma **média condicional** `x_i` (o quanto a pergunta é fácil ou difícil para o modelo) mais um **ruído de média zero** `ε_i` com variância condicional `σ_i²` (a variação de uma resposta para outra à mesma pergunta).

- Erro-padrão pelo TCL: `SE = √(Var(s)/n)` (Eq. 1, p. 3); para score binário, `SE = √(s̄(1−s̄)/n)` (Eq. 2). Intervalo de 95%: `s̄ ± 1,96 × SE` (Eq. 3).
- A variância da média se decompõe, pela lei da variância total, em duas partes aditivas (p. 5):

  `Var(µ̂) = Var(s)/n = (Var(x) + E[σ_i²]) / n`

  `Var(x)` é a variância **entre perguntas** — "uma propriedade da super-população e, portanto, imutável". `E[σ_i²]` é a variância **dentro da pergunta**.
- "A forma mais simples de reduzir a variância de µ̂ é aumentar n, o número de perguntas sorteadas" (p. 5).

## Reamostragem: quantas repetições (§3.1, p. 5)

Se cada pergunta é respondida `K` vezes e o score é a média das `K` respostas, a variância condicional vira `σ_i²/K`. **Só o segundo termo encolhe:** `Var(µ̂) = (Var(x) + E[σ_i²]/K) / n`.

- Quando `E[σ_i²]/K ≪ Var(x)`, aumentar `K` quase não muda o erro-padrão (p. 5). O paper **dá o critério** para escolher `K`: `K` tal que `E[σ_i²]/K ≪ Var(x)`; **não dá um número fixo**.
- Exemplo trabalhado (p. 5): score binário e dificuldade uniforme, `x ~ U[0,1]`. Então `Var(x) = 1/12` e `E[σ_i²] = 1/6`, o critério vira `K ≫ 2`, e `Var(µ̂|K>1) = Var(µ̂|K=1) × (1 + 2/K)/3`. Redução de variância: `K=2` → 1/3; `K=4` → 1/2; `K=6` → 5/9; limite com `K → ∞` → 2/3.
- **Aviso explícito** (p. 5): calcular o erro-padrão agrupando as `K·N` respostas é **inconsistente**, porque várias respostas à mesma pergunta violam a independência. O cálculo certo é sobre as **médias por pergunta**.
- Para estimar `Var(x)` e `E[σ_i²]` é preciso ter dados com `K ≫ 1`; o apêndice C divide por `K−1` (e não por `K`) para ter estimador consistente com `K` pequeno (p. 14).

**[derivação minha]** Com a decomposição acima, a razão entre as variâncias é `(1 + (K−1)ρ)/K` por pergunta, com `ρ = Var(x)/(Var(x)+E[σ_i²])`. No exemplo do paper `ρ = (1/12)/(1/12 + 1/6) = 1/3`, e `K=4` dá `(1 + 3/3)/4 = 1/2`, que bate com o 1/2 do texto. Essa forma, o chamado **efeito de desenho** `1 + (K−1)ρ`, **não está escrita no paper**; é uma consequência algébrica da decomposição dele.

## Próximo token e temperatura (§3.2 e §3.3, p. 6)

- Sem cadeia de raciocínio, dá para tirar a variância condicional por inteiro analisando a probabilidade do próximo token em vez da resposta amostrada: `s_i = x_i = p_i` e `ε_i = 0`. No exemplo uniforme, a redução é de 2/3. **Não se aplica** a respostas que exigem cadeia de raciocínio ou "outra interação complexa" (p. 6) — e é o caso de um agente de vários passos.
- **"Don't touch the thermostat!"** (p. 6): não reduzir a temperatura de amostragem para baixar a variância, a menos que o objetivo seja estudar o modelo nessa temperatura. A temperatura muda o comportamento do modelo, e pode só deslocar a variância condicional para a variância das médias condicionais (que não se reduz com `K`), ou reduzi-la injetando viés. Dois exemplos numéricos no texto.

## Perguntas em grupos: erro-padrão agrupado (§2.2, p. 4; Apêndice A, p. 12)

Quando as perguntas vêm em grupos (várias perguntas sobre o mesmo texto; a mesma pergunta traduzida em vários idiomas), o TCL ingênuo viola a independência. O erro-padrão agrupado (Eq. 4) funciona como uma "escala deslizante": de clusters perfeitamente correlacionados (cada cluster vale uma observação) a perfeitamente não correlacionados (igual ao ingênuo).

Números reais (Tabela 4, p. 4): a razão entre o agrupado e o ingênuo foi 3,05 no DROP, 1,10 no RACE-H e 1,88 no MGSM. "Os erros-padrão agrupados podem ser mais de 3 vezes maiores" (p. 4). O paper conclui que os intervalos do relatório do Llama 3 para compreensão de leitura são provavelmente **estreitos demais** (p. 5), e que, para scores fracionários, o `SE_Bernoulli` usado lá é conservador (largo demais) (p. 3).

**Atenção ao que "cluster" quer dizer aqui:** são grupos de perguntas **diferentes e relacionadas** (o mesmo texto, a mesma pergunta traduzida). **Não** são as `K` repetições da mesma pergunta; essas são o tema da reamostragem (§3.1).

## Comparar dois modelos: o pareamento (§4, p. 6–8)

- Não pareado: `SE_{A−B} = √(SE_A² + SE_B²)` (§4.1).
- **Pareado** (Eq. 7): inferência sobre a diferença de scores por pergunta, `s_{A−B,i}`. A variância pareada é a não pareada menos `2·Cov(x_A, x_B)/n`: **o pareamento reduz a variância desde que as médias condicionais dos dois modelos sejam correlacionadas**, isto é, que concordem sobre quais perguntas são fáceis e quais são difíceis (p. 8).
- Exemplo (p. 8): com correlação 0,5 e scores contínuos uniformes, a variância cai de 1/6 para 1/9. "Como é provável que os scores sejam positivamente correlacionados, até entre modelos sem relação, as diferenças pareadas são uma redução 'de graça' na variância" (p. 8).
- Versão pareada e agrupada: Eq. 8 (p. 8).
- Formato de reporte sugerido (Tabela 5, p. 8): diferença, erro-padrão, intervalo de confiança e correlação.

## Análise de poder (§5, p. 9–10; Apêndices B e C)

Entradas: nível de significância `α`, poder `1−β` e **efeito mínimo detectável** `δ`. Com `ω² = Var(x_A) + Var(x_B) − 2Cov(x_A, x_B)`, `σ_A² = E[σ_{A,i}²]` e `K_A`, `K_B` respostas por pergunta, o número de **perguntas independentes** necessárias é (Eq. 9, p. 9):

`n = (z_{α/2} + z_β)² · (ω² + σ_A²/K_A + σ_B²/K_B) / δ²`

- Exemplo (p. 9–10): `σ² = 0`, `ω² = 1/9`, `δ = 0,03`, `α = 0,05`, `β = 0,20` → `n ≈ 969`; os autores concluem que avaliações novas deveriam ter pelo menos ~1.000 perguntas "para ter bom poder de sinalização" (p. 10). Os parâmetros são **fictícios**, mas "razoáveis".
- Invertendo (Eq. 10), o efeito mínimo detectável com `n` fixo. Exemplo (p. 10): `σ² = 1/6`, `ω² = 1/9`, `n = 198`; passar `K` de 1 para 10 reduz o efeito mínimo detectável de **13,2% para 7,5%**.
- Versão para perguntas agrupadas: apêndice C (p. 13–14).
- `ω²`, `σ_A²` e `σ_B²` devem ser estimados de dados anteriores (p. 9).

## Bootstrap (p. 3)

"O TCL se aplica a qualquer avaliação com scores de variância finita e muitas perguntas, e por isso consideramos o bootstrap desnecessário, a menos que se use um esquema de amostragem ou um estimador complicado" (p. 3).

## O que o paper **não** cobre — limites para o nosso uso

- **É um artigo sobre avaliações de pergunta e resposta.** Não trata de agentes de vários passos, de ferramentas, de ordem de execução entre braços nem de latência. **[inferência minha]** A transposição para um experimento de agentes (tarefa no lugar de pergunta, execução no lugar de resposta) é natural, mas é transposição: o paper não a faz.
- **As fórmulas supõem `n` grande** ("muitas perguntas", p. 3). Para amostras de poucas centenas, o plano cita Bowyer et al. (2025), que mostra que o TCL tende a subestimar a incerteza (ainda sem nota em `papers/`).
- **Os valores numéricos de poder são fictícios.** Os 969 e os 13,2% → 7,5% são exemplos construídos com parâmetros inventados; não são resultados medidos.
- **O exemplo de `K` é específico:** o `K ≫ 2` vale para escore binário com dificuldade uniforme. Em outros casos, `K` depende da razão `E[σ²]/Var(x)`.
- **Só a v1 foi lida.** Se houver versões posteriores, a leitura não as cobre.
- O autor é da Anthropic; os "números não ficcionais" da Tabela 4 são de modelos da Anthropic.

## Como o plano do experimento usa este paper, e o que estava impreciso

O plano ([`plano-experimento-validacao-memorias.md`](../plano-experimento-validacao-memorias.md)) cita o Miller em três pontos. Conferido contra o texto:

| O plano diz | O paper diz | Veredicto |
|---|---|---|
| "Diferenças pareadas por tarefa" (§12) | §4.2, Eq. 7: diferença por pergunta | **bate** |
| "O poder vem do número de tarefas, não de repetir a mesma" (§7.2 e §9) | §3.1: só `E[σ²]/K` encolhe com as repetições; `Var(x)` só encolhe com `n` | **bate** |
| "o erro-padrão agrupado de Miller: o tamanho efetivo é dividido por `1 + (k−1)·ρ`" (§9.1) | o erro-padrão agrupado (Eq. 4) é para **grupos de perguntas diferentes**; as `k` repetições são reamostragem (§3.1), e a fórmula `1 + (k−1)ρ` **não está no paper** | **impreciso:** a fórmula é consequência algébrica da decomposição dele **[derivação minha]**, não uma citação |
| "Diferenças pareadas por tarefa e erro-padrão agrupado (Miller, 2024)" (§12) | para as repetições, o paper manda tirar a **média por tarefa** e calcular o erro sobre as tarefas; o agrupado (Eq. 4) só entra se as tarefas nascem em famílias (ver abaixo) | **impreciso** |

Três consequências para o plano **[inferência minha]**:

1. **As `K` repetições viram uma média por tarefa**, e a incerteza se calcula sobre as tarefas, nunca sobre as execuções empilhadas (aviso da p. 5).
2. **Se as tarefas sintéticas nascem de um mesmo gerador**, com parâmetros diferentes, elas são "perguntas agrupadas" no sentido do §2.2, e o erro-padrão agrupado por gerador ou por espelho (Eq. 4) é o que se aplica a essa parte.
3. **A tabela de tamanho de amostra do plano é conservadora:** ela usa a fórmula de duas proporções independentes, e o desenho do experimento é **pareado** (os braços rodam as mesmas tarefas). A Eq. 9 do paper, com `ω²`, `σ²` e `K` estimados do piloto, dá o número exato, e ele tende a ser menor quando as médias condicionais dos braços são correlacionadas.

## Pontos para o seu check (✅)

Se for ler com a caneta na mão, estes são os trechos que sustentam o plano:

- §3.1 (p. 5): a decomposição da variância e o critério de `K`. É o que justifica "poucas repetições, muitas tarefas".
- A frase do aviso sobre o erro-padrão agrupado de `K·N` respostas (p. 5).
- §2.2 e a Tabela 4 (p. 4): para ver que "cluster" é grupo de perguntas diferentes, e não repetição da mesma.
- §4.2 (p. 7–8): o pareamento.
- Eq. 9 e o exemplo de `K` de 1 para 10 (p. 9–10): o que o piloto do plano deve estimar.
- §3.3 (p. 6): a razão de não mexer na temperatura. O plano segue essa orientação.

Até esse check, este fichamento é **🔎**.
