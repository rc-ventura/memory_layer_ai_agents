---
name: mineracao-investigacao
description: "Investigação depois do determinístico (kit de mineração): pega o relatório de uma rodada de mineração do trace, abre as perguntas que as regras não fecham (o roteiro da mineração), lê casos amostrados por regra fixa, mede a concordância com um segundo leitor, transforma a hipótese numa regra determinística contada por script e entrega ao pesquisador um dossiê de decisão. Use quando pedirem para 'investigar mais a fundo', 'investigar as paradas do relatório', 'montar o dossiê de <decisão>', 'ler os candidatos a sucesso falso', ou depois de uma skill mineracao-* que terminou com paradas. Nunca decide, nunca edita regra do pipeline: propõe e conta."
---

# Mineração do trace — a investigação depois do determinístico

O determinístico vai até onde as regras alcançam e para nos pontos que pedem leitura de caso, as **paradas** do
relatório. Esta skill continua dali e termina num **dossiê de decisão** para o pesquisador. A regra de ouro é que o
LLM propõe e o script conta. Nenhum número do dossiê sai da leitura do modelo; a leitura entra como categoria e
contagem, marcada `[assistido]`, e vale como hipótese.

**Antes:** a skill `mineracao-base` (Passo 0), na mesma pasta de análise, e um relatório de rodada em
`pipeline/resultados/relatorio_<mineracao>_<BASE_ID>_*.md`. Sem relatório, rode antes a skill da mineração.

## Peças

- **Roteiros** (`roteiros/<mineracao>.md`): as perguntas abertas de cada mineração, quando abrir cada uma, a
  população, o campo do step e as categorias fechadas. Hoje: [`silenciosas`](roteiros/silenciosas.md), [`protocolo`](roteiros/protocolo.md) e
  [`candidata`](roteiros/candidata.md) (a parte específica de uma candidata a memória, que entrega o arquivo final no
  esquema da memória).
- **Scripts** (determinísticos):
  - `montar_evidencia.py` e `amostrar.py` (na `mineracao-base`): quem escolhe os casos é uma regra fixa, e cada caso
    lido fica com o cru gravado;
  - `testar_regra.py`: a hipótese vira contagem na população inteira e é comparada com a leitura;
  - `concordancia.py`: o acordo entre os dois leitores.
- **Agentes:**
  - `investigador`: o primeiro leitor;
  - `segundo-leitor`: relê às cegas;
  - `auditor-independente`: a conferência do relatório.

  Quando o ambiente não tiver subagentes, faça os papéis em sequência, e o segundo leitor não pode ver a primeira
  leitura.
- **Esqueleto do dossiê:** [`referencias/dossie.md`](referencias/dossie.md).

## Passos (um dossiê por pergunta)

1. **Escolher a pergunta.** No relatório, liste as paradas. Para cada uma, ache no roteiro a pergunta que ela abre e
   confira o "quando abrir". Uma pergunta por dossiê. Se o relatório tiver várias, pergunte ao pesquisador por qual
   começar.
2. **Hipóteses antes de ler.** Escreva H0 (a nula do roteiro) e pelo menos uma alternativa, cada uma com o que se
   veria no caso se fosse verdadeira. Escrever depois de ler é ajustar a hipótese aos dados.
3. **Amostrar e gravar a evidência crua** (de qualquer lugar):
   ```
   uv run python <skill mineracao-base>/scripts/montar_evidencia.py <pasta-da-analise> --nome inv_<decisao>_<BASE_ID> \
       --de <população, relativa a pipeline/resultados/> --onde <col>=<valor> \
       --afirmacao "<a pergunta do roteiro>" --reproduzir "<o comando que gerou a população>"
   ```
   A amostra é o `casos.csv` da pasta `resultados/evidencia/inv_<decisao>_<BASE_ID>/`, e cada caso já tem o cru
   (`crus/`) e a visão (`derivados/`). Use a regra `procedimento` (o padrão). Só use `--regra semente --n <k>`
   quando a população for grande demais para ler o primeiro de cada mês.
4. **Ler (o `investigador`).** Para cada caso da amostra, rode `uv run python drill_down.py caso <exec_id> <role>` e
   classifique nas categorias fechadas do roteiro. Grave `resultados/leitura_<decisao>_<BASE_ID>.csv` com
   `exec_id, role, idx` (ou a coluna de idx do roteiro), uma coluna por eixo ou categoria e `onde_no_cru` (o campo do
   step lido). Não copie texto de caso para a leitura nem para a conversa.
5. **Segundo leitor.** Faça a amostra da amostra
   (`<skill mineracao-base>/scripts/amostrar.py resultados/evidencia/inv_<decisao>_<BASE_ID>/casos.csv --regra semente --n <k> --saida resultados/amostra2_<decisao>_<BASE_ID>.csv`,
   com k ≈ um terço, no mínimo 5). O `segundo-leitor` classifica sem ver a leitura 1 e grava
   `resultados/leitura2_<decisao>_<BASE_ID>.csv`. Depois:
   ```
   uv run python <esta skill>/scripts/concordancia.py resultados/leitura_….csv resultados/leitura2_….csv --rotulo <coluna>
   ```
   Se a concordância for baixa (kappa < 0,6), a categoria está mal definida: registre isso como achado e não proponha
   regra.
6. **Propor a regra e contar.** Escreva a regra que separaria a categoria-alvo (regex num campo do step) e conte:
   ```
   uv run python <esta skill>/scripts/testar_regra.py <pasta-da-analise> --populacao <população.csv> --campo-passo <campo> --regex '<rx>' --lidos resultados/leitura_….csv --rotulo <coluna> --alvo <valor>
   ```
   Itere sobre a regra, nunca sobre a leitura. Toda versão testada entra no dossiê, inclusive as que falharam.
7. **Dossiê.** Preencha `referencias/dossie.md` em `resultados/dossie_<mineracao>_<decisao>_<BASE_ID>_<data>.md`.
   Cada número leva o comando que o produziu. A amostra leva o `bloco.md` da pasta de evidência, colado com `cat`. A
   leitura leva o caminho do CSV e, por categoria, os casos que a sustentam: as linhas do `leitura_….csv`, que já têm
   `exec_id`. Para sair, use `versao_para_sair.py` e `varrer_pii.py`, da `mineracao-base`.
8. **Entregar.** Na resposta ao pesquisador vão a pergunta, as hipóteses, as contagens (leitura, concordância, regra),
   as opções e a recomendação. A decisão é dele. Se a regra entraria no pipeline e mudaria número publicado, diga
   que é um *Ajuste* e pare.

## O que esta skill não faz

- Não escolhe os casos a ler, não edita `base_pipeline.py`, notebook nem procedimento, não roda o pipeline com a
  regra nova.
- Não transforma leitura em número publicado: a leitura é `[assistido]`, e só a regra contada é `[conferido]`.
- Não lê mais do que a amostra pede. Cada caso lido é texto do trace indo para o modelo, e o sigilo da
  `mineracao-base` vale inteiro.
