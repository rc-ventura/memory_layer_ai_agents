# Estrutura, estilo e verificação dos relatórios mensais

Extraído dos relatórios 1 (agosto) e 2 (setembro) em `docs/reports/`. Português, voz impessoal na 3ª pessoa ou passiva ("construiu-se", "foram lidos"), como nos já enviados.

## Estrutura do arquivo

```markdown
# Relatório Mensal — {Mês} de {Ano}

- **Projeto:** Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos
- **Programa:** [PROGRAMA-FOMENTO] — Nº [ANONIMIZADO]
- **Bolsista:** Rafael Coelho Ventura
- **Número do relatório:** {N}
- **Mês de competência:** {MM/AAAA}
- **Atividades previstas para o mês:** {a opção que Rafael escolher no formulário}
- **Período de referência:** {DD/MM/AAAA a DD/MM/AAAA; se houver atividade anterior ainda não relatada, dizê-lo aqui}
- **Data de emissão:** {DD/MM/AAAA}

Este arquivo guarda, versionado, o que foi submetido no formulário mensal da instituição. Os dois blocos abaixo
correspondem aos dois campos de texto do formulário; o texto puro para colar está em
[`relatorio-mensal-AAAA-MM-envio.txt`](relatorio-mensal-AAAA-MM-envio.txt).

---

## Desenvolvimento das atividades no período

*(etapas e atividades realizadas, alterações introduzidas, acompanhamento, orientação e cumprimento do cronograma)*

{parágrafo de abertura: onde o trabalho se concentrou, em quais Macroatividades/Sub}

**{Frente 1} (Sub x.y / x.y).** ...
**{Frente 2} (Sub x.y).** ...
**Alterações introduzidas.** (i) ... (ii) ...
**Acompanhamento e orientação.** ...
**Cumprimento do cronograma.** ...

---

## Observações/comentários

*(qualquer aspecto considerado relevante para o andamento das atividades)*

{o que transcende o período; pontos de atenção do próximo; transparência metodológica}
```

## O que cada bloco carrega

- **Parágrafo de abertura:** 2–3 frases. Diz em que Macroatividade o mês se concentrou e quais frentes houve.
- **Adendo de propósito:** um parágrafo de 3–4 frases logo depois da abertura, com **para que serve o trabalho do mês e qual o objetivo final dele** (ligado ao Plano). Se o método já foi explicado num relatório anterior, **cite que foi** e não o redefina; o adendo só diz o propósito. Se não foi, explique-o. **"Nomeado" não é "explicado":** conferir se o relatório anterior *definiu* cada termo que o atual usa (um nome numa lista, como a cadeia família → assinatura → mecanismo → unidade → destino de setembro, não conta). Termo usado e nunca definido ganha uma frase de definição no adendo.
- **Frentes:** uma por linha de trabalho, **com as Sub entre parênteses**, na ordem de importância (a frente principal primeiro, como em setembro). Cada uma: o que foi feito → o que se achou (número com unidade e base) → o limite do achado (o que ainda é hipótese).
- **Alterações introduzidas:** mudanças de **escopo, método ou entendimento** (decisões), numeradas (i), (ii)... Não é lista de commits.
- **Acompanhamento e orientação:** reuniões com o tutor e com a área da plataforma; o que foi pedido a quem; o que ficou pendente. **Reunião com o tutor sem data** (feedback de Rafael, 28/10): a reunião é semanal, normalmente na quinta e às vezes na sexta, então data solta engana; escreva "houve reunião com o tutor" (ou "em reunião com o tutor") e o que foi tratado. Reunião com a área da plataforma ou com terceiros pode ter data, se o diário a registra.
- **Cumprimento do cronograma:** por Macroatividade vigente, com o prazo formal do Plano; o que avançou (Sub), o que permanece pendente do Entregável, e a dependência entre eles.
- **Observações:** (1) o resultado do mês que vai além do diagnóstico; (2) pontos de atenção para o próximo período, numerados (a), (b)...; (3) um parágrafo de **transparência metodológica** (o que é determinístico, o que é leitura assistida por agente de IA, o que passou por auditoria independente).

## Estilo

- **Títulos de frente em negrito com ponto final dentro do negrito** — `**Título (Sub 2.2).**` — e o texto na sequência, no mesmo parágrafo. (O script de conversão põe o título em linha própria no texto puro.)
- Termos técnicos em itálico na primeira ocorrência (*harness*, *gate*, *rollback*), como nos relatórios anteriores. Nome de campo ou de função em crase.
- **Números:** com a base de onde vieram ("na base 1", "na base 3"), unidade (erros, execuções, passos, tokens) e, se for taxa, o denominador. Evite percentual solto.
- **Hipótese × achado:** "o achado" só para o que foi medido ou lido no cru; "hipótese", "inferência", "associação" para o resto, como o diário marca.
- Continuidade: retome o ponto de atenção do relatório anterior em uma frase ("o ponto levantado em setembro... foi...").
- **Didático, para quem não acompanha o pipeline** (feedback de Rafael, 28/10, sobre o relatório 3): o leitor é a instituição, não a equipe técnica. Em cada frente, diga primeiro **o que é o objeto** ("as bases 1 e 2 são duas amostras de 1.000 execuções reais"), depois **o que foi feito**, depois **o que se achou**, numerando os achados (i), (ii), (iii) quando houver mais de um. Defina cada termo do projeto na primeira ocorrência, em português simples (falha silenciosa, sucesso falso, pendente, sinal de *harness*, degrau). Uma ideia por frase; evite os rótulos internos do pipeline ("canal", "unidade", "régua", "balde") sem explicação.
- Tamanho-alvo: **7 a 13 mil caracteres** no total (setembro: 7 mil; outubro, depois da versão didática: 12,6 mil). O didatismo custa caracteres: se estourar, corte detalhe de método e número secundário, nunca a explicação do que é o objeto.

## Verificação (antes de entregar)

1. **Campos:** todos os campos obrigatórios do formulário colado têm resposta; os cinco subtemas do "Desenvolvimento" estão presentes.
2. **Cobertura:** o período cobre a janela da §2 do fluxo (inclusive o que ficou entre a emissão do relatório anterior e o fim do mês dele).
3. **Continuidade:** cada compromisso e ponto de atenção do relatório anterior tem uma frase de desfecho.
4. **Fonte:** cada número e cada data de reunião aparecem no diário, num documento do repo ou no git; o resto está na lista "Para você conferir".
5. **Cronograma:** o prazo formal da Macroatividade está certo e nada é declarado entregue sem estar; nenhum compromisso novo foi inventado.
6. **Anonimização:** sem nomes de pessoas, de assistente/modelo/provider, de cliente; sem identificador de execução; `INTERESSADO` para a empresa.
7. **Texto puro:** o `-envio.txt` não tem `**`, crase nem `#`; os títulos de frente estão em linha própria.
8. **Tamanho:** dentro do alvo; se passar, dizer a Rafael onde cortar.
