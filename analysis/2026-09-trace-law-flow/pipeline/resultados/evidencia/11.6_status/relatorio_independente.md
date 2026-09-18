# Relatório independente — 11.6_status

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.6_status/` no estado atual dos artefatos em `pipeline/resultados/evidencia/`. O objetivo é verificar se a pasta sustenta, por si mesma e em triangulação com os documentos de método, a alegação do Passo 5 sobre:

1. cobertura de leitura das sub-unidades candidatas; e
2. situação do resíduo (`objeto não lido`).

Guidance consultado para interpretar a análise:

- `docs/`06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.9;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Limitação importante

Diferentemente das pastas 11.1–11.5 e 11.7, a pasta `11.6_status/` **não contém atualmente casos abertos** para reabrir no cru:

- não há `casos.csv`;
- não há `crus/*.json`;
- não há visões em `derivados/`;
- o único arquivo presente é `leia-me.md`.

Portanto, esta auditoria independente é necessariamente **de consistência dos artefatos e do método**, e não uma reabertura caso a caso dentro da própria pasta.

## Resumo executivo

1. O `leia-me.md` da pasta declara explicitamente **"Regra de escolha dos 0 casos"**.
2. A ausência de `casos.csv` e de arquivos crus é consistente com a nota metodológica publicada em `03-procedimento-validacao.md`: após a emenda de 17/09, o **resíduo verdadeiro fechou em 0**, e a regeneração das pastas deixou `11.6_status/` sem casos.
3. O `02-relatorio-achados.md` também é consistente com esse estado: reporta cobertura final de **91/91 erros** para `get_available_documents` e **7/7** para `validar_quebra_sigilo`, com **resíduo real = 0**.
4. Assim, no estado atual, a pasta 11.6 não oferece contraevidência ao resultado publicado; ao contrário, sua vacuidade é coerente com ele.
5. A limitação é só uma: como os casos do antigo resíduo não estão mais materializados nesta pasta, esta auditoria não substitui uma reabertura histórica desses casos em outras pastas/fontes, se isso vier a ser necessário.

## Evidência disponível na própria pasta

Arquivo presente:

- `leia-me.md`

O `leia-me.md` informa:

- que a pasta sustenta “a cobertura de leitura de cada candidata e o motivo de cada erro do resíduo”;
- e que a **regra de escolha** é “todos os erros do resíduo das sub-unidades candidatas”, com **0 casos**.

A inspeção do diretório confirmou que não há outros arquivos nesta pasta no estado atual.

## Triangulação com os documentos de método

### 1. O procedimento de validação explica por que a pasta ficou vazia

O `03-procedimento-validacao.md` registra dois pontos relevantes:

1. a conferência do Passo 5 havia aberto **2 erros do resíduo**;
2. depois da emenda metodológica de 17/09, o texto afirma que o **resíduo de verdade é 0** e que `11.6_status/` ficou com **0 casos (esperado)** após regerar as pastas de evidência.

Isso é compatível com o estado material atual da pasta.

### 2. O relatório de achados confirma o fechamento do resíduo

O `02-relatorio-achados.md` reporta:

- `get_available_documents` (nº2): **86/86 ocorrências** e **91/91 erros** lidos ou confirmados, `Status = derived-and-checked`, `Leitura estrita = parcial`;
- `validar_quebra_sigilo` (nº10): **7/7 ocorrências** e **7/7 erros** lidos ou confirmados, `Status = derived-and-checked`;
- **resíduo real = 0**.

Assim, a inexistência de casos em `11.6_status/` não é um acidente de geração; ela bate com o resultado publicado.

## Leitura independente

Com base no que está disponível hoje, a auditoria independente conclui:

- a pasta `11.6_status/` está **coerente com o método e com os resultados publicados**;
- não há sinal de descompasso entre o estado atual dos artefatos e a narrativa metodológica dos docs;
- a ausência de casos deve ser lida como **resultado da análise** (resíduo fechado), não como lacuna acidental.

## Conclusões finais

1. No estado atual dos artefatos, `11.6_status/` sustenta de forma consistente a conclusão publicada de que o resíduo fechou em zero.
2. A pasta vazia não enfraquece o Passo 5; ela é exatamente o que os documentos dizem que deveria existir após a emenda de 17/09.
3. Esta é, porém, uma validação **de consistência do artefato final**, não uma reabertura caso a caso dentro da própria pasta, porque os casos deixaram de estar materializados nela.
4. Se você quiser uma validação histórica mais forte do antigo resíduo, o próximo passo seria reabrir explicitamente os casos citados nos docs a partir de outras pastas que ainda preservam esses crus.
