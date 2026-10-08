# Retomada sem censo — implementação e verificação

> **Registro histórico da primeira entrega.** A fonte foi depois recuperada;
> [rodada real atual](04-relatorio-rodada-observada-real.md): 154 testes,
> 42 verificações, dez candidatas/perfis. Não houve aprovação de memória.

> **Scripts reorganizados posteriormente:** os comandos abaixo registram o que
> foi executado naquela entrega. Para executar hoje, usar a entrada única
> [executar.py](../pipeline/executar.py) e o [índice operacional](../README.md).

> Códigos: [glossário](../../glossario.md). Contrato/racional/procedimento:
> [mineração sem censo](02-mineracao-sem-censo.md).

**Data:** 07/10/2026. **Estado:** implementação validada sinteticamente;
**execução real bloqueada pela fonte**, ainda sem candidata investigada ou
memória aprovada. O pesquisador autorizou continuar o código enquanto confere
ou restaura o arquivo. Não é fechamento da análise nem atualização do kit.

## 1. Entrega implementada

- [Fachada](../pipeline/base_pipeline.py) `carregar_mineracao_observada` e
  [módulo observado](../pipeline/mineracao_observada.py): composição dos
  classificadores existentes, triagem global/por papel e sensibilidade;
  identidade de execução inclui agente; componentes antes do subconjunto.
- [Consolidação](../pipeline/consolidacao_unidades.ipynb) e
  [G1–G6](../pipeline/mineracao_generica.ipynb) adaptados para o canal visível
  observado, sem dependência artificial de silenciosas/sucesso/censo.
- Manifesto privado por rodada/fonte/código, hashes dos artefatos, rejeição de
  dados de outra base/rodada ou modificados. Custos desconhecidos explícitos;
  localização original sem `idx` fictício; amostra determinística privada.
- Gráficos de unidades/papéis e genealogia incluindo caminhos de evidência
  insuficiente, separados do resíduo. Motor de desenho existente reutilizado.
- [Gerador Python (relocalizado)](../pipeline/execucao/executar_observada.py), [validador sintético (relocalizado)](../pipeline/validacao/validar_observada.py)
  e [proposta de agregados](proposta_agregados_sem_censo.sql). SQL não executado
  nem validado na engine Athena. Somente especificação de metadados dirigidos,
  não uma extração do banco nem novo contrato integrado ao adaptador.

Os guards raw/globais permanecem. Nenhuma regra nova de classificação,
mudança de destino específico da base 3 ou diretiva checada foi introduzida.
Não houve atualização do esquema final, manifesto de skills, commit ou push.

## 2. Evidência de verificação

**Comando efetivamente executado, da raiz:**
`uv run python analysis/2026-10-trace-law-flow-third/pipeline/validar_observada.py`.

| Verificação | Resultado | Artefato local privado |
|---|---|---|
| Suíte completa | **153 testes passaram**, 27 novos da retomada | [log](../pipeline/resultados/validacao_observada_2026-10-07/testes.txt) |
| Regras e catálogos comparados por AST com second | **10/10 iguais** | [validação](../pipeline/resultados/validacao_observada_2026-10-07/validacao.json) |
| Células dos consumidores em Python sintético | Consolidação 10/10; genérica 7/7 | Testes `TestConsumidoresNotebook` no log |
| Publicação e desenho sintéticos | Manifesto, perfis, gráficos e genealogia testados | Teste de publicação no log |
| CSVs canônicos e Sankey | **11 artefatos idênticos por SHA-256 à second** | [inventário](../pipeline/resultados/validacao_observada_2026-10-07/inventario.csv) |
| Fonte atual | Hash divergente; Parquet não abre | `fonte_intake` na validação |
| Jupyter/rodada real/auditoria semântica | **Não realizados/confirmados** | Flags e gate da validação |

AST conferida: `classify`, `linha_do_codigo`, `sinais_de_parsing`, `linha_rejeitada`,
`submecanismo`, `SUB2UNI`, `UNI`, `DESTINO_MINERACAO`, `triagem` e
`triagem_por_papel`. Guards das funções raw da third não são removidos para
obter equivalência. Regressões sintéticas do caminho raw continuam passando.

O teste das células omite apenas a magic gráfica, injeta fixtures sintéticas e
publicação mockada. Não regrava notebook por script e não é execução Jupyter.
O teste de publicação escreve artefatos reais sintéticos numa pasta temporária,
sem casos bancários; não comprova uma rodada no Parquet corporativo.

A tentativa de revisão delegada retornou 403. Nenhuma revisão independente
delegada foi concluída; não descrevemos os testes como auditoria semântica.

## 3. Fonte e artefatos antigos

O Parquet de início desta retomada tinha 426.346.727 bytes e SHA-256
`50e0dd38a3e37d397344bf5dbf80d4ef3a71c0d30c41513915471ec36d192238`.
É diferente da referência histórica; leitura de metadados Arrow falhou.
Motivo não determinado, sem reparo automático. Os números da Etapa 7 **não
foram aplicados** a esse arquivo. Dados e resultados históricos foram preservados.

O inventário confirma dez CSVs iguais à second: candidatas, críticos, erros
classificados, erros com mecanismo, execuções, genealogia, payoff, reincidência,
resíduo e triagem por assinatura; o Sankey é o 11º artefato. Os cinco notebooks
também são inventariados, mas seus outputs não certificam fonte atual.

## 4. Retomada e gates pendentes

1. Restaurar/conferir o Parquet; se for nova exportação, declarar intake/coorte.
2. Rodar a entrada observada, validar as contagens da fonte e conferir gráficos
   da nova rodada; não consumir os CSVs canônicos legados.
3. Escolher uma candidata efetivamente recorrente e gerar seu perfil/amostra.
4. Obter complemento dirigido somente se seus insumos forem insuficientes;
   agregados de população são opcionais e não bloqueiam triagem visível.
5. Resolver localização final por metadados `action_idx` só dos erros ou evolução
   aprovada do esquema. Perfis atuais não são JSONs finais de memória.
6. Leitura dupla, concordância/regras contadas, auditoria independente, dossiê
   e decisão de destino. Sem esse gate, nenhuma aprovação/promulgação de memória.
7. Adaptar evidências/drill-down/monitoramento/skills e versionar kit com revisão
   de contratos; não rodar ferramentas raw legadas sobre janelas.

**Conclusão:** os consumidores visíveis podem funcionar sem censo no contrato
implementado e testado. Não está comprovado ainda o resultado empírico da
terceira base nesta retomada. A próxima dependência operacional é a fonte íntegra,
não a exportação de todos os ActionSteps.
