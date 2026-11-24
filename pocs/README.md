# POCs

Documentos de desenho e material de referência das provas de conceito do projeto — hoje centrados no **experimento que valida uma memória** (o degrau 4 da [validação de memórias](../analysis/2026-09-trace-law-flow/docs/17-validacao-memorias.md): injetada, ela reduz o erro e compensa o custo?).

## Ordem de leitura

| Doc | O que é |
|---|---|
| [`blueprint-m1-pocs-minimos.md`](blueprint-m1-pocs-minimos.md) | O guarda-chuva das POCs mínimas do M1 (Sub 1.6/1.7): etapas de construção e os experimentos EX-1..EX-8. |
| [`experimento-degrau-4/01-plano-geral.md`](experimento-degrau-4/01-plano-geral.md) | O plano do experimento — genérico, vale para qualquer unidade de memória; a ficha do §16 gera um adendo por unidade. |
| [`experimento-degrau-4/02-fase-1-mitiga-erro.md`](experimento-degrau-4/02-fase-1-mitiga-erro.md) | O que roda **antes** do plano geral: a memória mitiga o erro? Receita com os agentes reais, volumetria e critérios de sucesso. |
| [`experimento-degrau-4/03-conceitos.md`](experimento-degrau-4/03-conceitos.md) | Os conceitos que os planos usam (replay, quantas execuções para o erro aparecer, intervalos de confiança, Holm), em linguagem simples. |
| [`experimento-degrau-4/04-relatorio-volumetria.md`](experimento-degrau-4/04-relatorio-volumetria.md) | A volumetria das memórias por agente que alimenta o §4.6 da fase 1 — com método e intervalos (o §9 diz o que falta medir e com que comando). |
| [`experimento-degrau-4/adendos/`](experimento-degrau-4/adendos/) | Um arquivo por unidade de memória (pela ficha do §16 do plano) ou por braço transversal do experimento. Hoje: `A-inventario-sandbox.md` e `B-memoria-no-erro.md`. |

## Material de referência

| Pasta | O que é |
|---|---|
| [`literature/`](literature/README.md) | Fichamentos dos artigos em que o plano do experimento se apoia (mesma regra da `analysis/literature/`). |
| [`sdk-memory-docs/`](sdk-memory-docs/README.md) | Transcrição anonimizada da documentação do SDK interno de memória. A análise comparativa com o mecanismo do projeto vive fora daqui, em [`../discussion/hipoteses/internal-memory-sdk-vs-mechanism.md`](../discussion/hipoteses/internal-memory-sdk-vs-mechanism.md). |

## Convenções

- **Novo adendo de unidade:** copiar a ficha do §16 do plano geral para `experimento-degrau-4/adendos/<letra>-<nome-da-unidade>.md` (próxima letra livre) e registrar a linha na tabela do §0 do plano.
- **Código das POCs:** vive em `pocs/<data>-<slug>/` (a criar na etapa E0, nome em aberto), seguindo a convenção datada de `analysis/`.
