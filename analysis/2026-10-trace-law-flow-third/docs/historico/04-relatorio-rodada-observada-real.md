# Rodada observada real — fonte restaurada, triagem e perfis

> **Limpeza posterior autorizada em 07/10:** removidas as cópias legadas da
> second, preservando fonte/rodada e histórico próprio. O [índice operacional](../README.md)
> distingue código ativo de auxiliares históricos. O inventário da rodada é
> registro anterior à limpeza, não lista dos arquivos que ainda devem existir.

> **Reorganização posterior de scripts:** a rodada e os comandos deste relatório
> registram a execução anterior. Scripts agora agrupados em execução/validação;
> entrada atual: [executar.py](../pipeline/executar.py), conforme [README](../README.md).
> Manifestos antigos não são reescritos para parecer compatíveis com código novo.

> **Conferência pós-reorganização concluída:** entrada única `executar.py conferir`,
> rodada [a4e7d295da2b6376](../pipeline/resultados/observada_a4e7d295da2b6376/manifesto.json).
> 162 testes e 42 verificações passaram; fonte/código/artefatos conferidos.
> Cinco tabelas (triagem global, por papel, coberturas de sintomas/mecanismos e
> genealogia) são iguais à rodada anterior. Dez perfis gerados. O corpo abaixo
> registra a execução anterior; o [README](../README.md) aponta a referência atual.
> Sem execução Jupyter confirmada ou aprovação semântica.

> Códigos: [glossário](../../glossario.md). Método e limites:
> [contrato sem censo](02-mineracao-sem-censo.md). Implementação anterior:
> [relatório sintético](03-relatorio-retomada-sem-censo.md).

**Data:** 07/10/2026. **Estado:** rodada real conferida tecnicamente, sem
aprovação semântica. A fonte restaurada abriu e reproduziu exatamente o SHA-256
histórico `7604f77df9fe6127bd7fb9db18337b558b1f2587b0a99621c087b0cf3c2873f1`:
324.479.988 bytes, 31.421 registros e 69 colunas. O bloqueio de integridade do
início da retomada foi resolvido. Os demais gates não foram removidos.

## 1. Reprodução e evidências

Comandos efetivamente executados da raiz:

1. `uv run python analysis/2026-10-trace-law-flow-third/pipeline/validar_observada.py`.
2. `uv run python analysis/2026-10-trace-law-flow-third/pipeline/conferir_rodada_observada.py`.

**154 testes passaram** (28 da retomada). As dez regras/catálogos AST continuaram
iguais à second. **42 verificações reais passaram**: leitura Arrow direta para
inventário/elegibilidade/tokens/duração; invariantes internos de triagem e
genealogia; perfil/localização de dez candidatas; hashes de artefatos e da fonte.
Recálculo interno de candidatura não é auditoria independente da regra.

Referência final: rodada `observada_9f52a7431290cf07`;
[manifesto](../pipeline/resultados/observada_9f52a7431290cf07/manifesto.json),
[conferência](../pipeline/resultados/conferencia_observada_2026-10-07/conferencia.json),
[log dos testes](../pipeline/resultados/validacao_observada_2026-10-07/testes.txt),
[log Python real](../pipeline/resultados/conferencia_observada_2026-10-07/smoke_python_real.txt).
Artefatos privados/git-ignored; este resumo agregado é versionável.

As dez células da consolidação e sete da genérica executaram suas sources em
Python controlado, sobre o objeto real já conferido; omitida a magic gráfica,
publicação reaproveitada da rodada. **Não é execução Jupyter confirmada.**
Os outputs restaurados no editor não viraram evidência automaticamente.

### Ocorrência operacional e rodadas anteriores

A primeira publicação com todos os perfis parou no limite de caminhos do
Windows. Corrigido somente I/O com caminho estendido e normalização de `..`,
incluindo regressão sintética e cleanup da fixture. Não alterou fonte,
classificadores ou diretivas. A rodada interrompida ficou não concluída;
consumidores a rejeitam. A primeira rodada sem perfis e a interrompida são
histórico, não a referência final acima.

A cor de **evidência insuficiente** foi explicitada na paleta da third para não
parecer plataforma/resíduo; só apresentação, sem mudar contagens. Gráficos
foram gerados e inspecionados: [unidades](../pipeline/resultados/observada_9f52a7431290cf07/unidades_observadas.png),
[papel × unidade](../pipeline/resultados/observada_9f52a7431290cf07/papel_unidade.png) e
[genealogia atual](../pipeline/resultados/observada_9f52a7431290cf07/genealogia_observada.png).

## 2. Cobertura medida na fonte real

| Medida | Resultado |
|---|---:|
| Erros estruturados preservados | 30.141 |
| Suspeitas separadas, fora da taxonomia | 1.280 |
| Mensagens elegíveis para sintomas | 29.132 |
| Mensagens limitadas | 1.009 |
| Mecanismos/unidades observáveis | 23.034 |
| Mecanismos pendentes por evidência | 7.107 |
| Unidades observáveis | 17 |
| Candidatas observadas ≥3 execuções/≥2 meses | 10 |
| Tokens em todos os erros estruturados | 592.858.874 |
| Tokens atribuídos a unidades observáveis | 449.653.876 |
| Tokens com mecanismo pendente, preservados | 143.204.998 |
| Tokens dos erros atribuídos às dez candidatas | 361.727.494 |

Evidência: resumo/conservações na conferência; cobertura e
[triagem atual](../pipeline/resultados/observada_9f52a7431290cf07/triagem_visivel_observada.csv).
Cada coluna da genealogia conserva **30.141** erros; pendências levam a
complementar evidência, não a X_. Custos de sintomas/mecanismos se sobrepõem:
não somar. Custos dos erros não são desperdício, orçamento total ou economia.

Pendências: predecessor não identificado **5.818**; mensagem limitada **1.009**;
timeout sem prompt/código **215**; linha rejeitada sem código integral **46**;
histórico insuficiente **14**; predecessor/numeração ambíguos **5**.

## 3. Candidatas — recorrência observada, destino em aberto
| Unidade | Erros atribuídos | Execuções/agente | Meses | Tokens de n |
|---|---:|---:|---:|---:|
| `U_tipo_retorno` | 4.317 | 3.042 | 10 | 169.880.087 |
| `U_sandbox` | 3.653 | 3.451 | 10 | 69.579.324 |
| `U_arg_nomeado` | 3.927 | 2.390 | 10 | 51.580.990 |
| `U_campo_inexistente` | 1.566 | 1.468 | 9 | 24.015.553 |
| `U_estado_perdido` | 878 | 834 | 10 | 19.786.288 |
| `U_nome_inventado` | 477 | 461 | 10 | 8.887.136 |
| `U_texto_solto` | 180 | 68 | 9 | 8.033.248 |
| `U_repr_colado` | 1.587 | 1.547 | 7 | 6.443.874 |
| `U_texto_literal` | 141 | 129 | 10 | 3.290.725 |
| `U_next_gerador` | 15 | 13 | 6 | 230.269 |

São contagens por unidade, não taxa de falha. Execuções entre unidades se
sobrepõem. Ocorrências são condicionais aos vínculos e não episódios exatos.
Destino de todas estas candidatas permanece **em aberto** nesta base.
`U_contrato_dict`: dois erros, duas execuções, um mês — recorrência não
demonstrada, sem herdar a candidatura da base 1.

Plataforma: três unidades não-memória; crítico: uma unidade com 25 erros;
revisão: dois resíduos com 350 e 188 erros. Isso não inclui as pendências de
evidência, que permanecem sem unidade taxonômica.

## 4. Perfis preparados e próximo gate

Os dez perfis G1–G6 foram gerados em `perfis/` dentro da rodada final, sem exibir
identificadores ou texto de caso. Amostra determinística de até 30 por candidata,
intercalando papéis: **285 casos amostrados** no conjunto, sem promessa de
representatividade probabilística. Para `U_next_gerador`, todos os 15 casos.
Populações dos perfis coincidem com a triagem; amostras/localizadores/hashes
foram conferidos. Índice ActionStep continua desconhecido; posição original
não é renomeada como `idx`.

[Cobertura agregada das amostras](../pipeline/resultados/conferencia_observada_2026-10-07/perfis_agregados.csv):
o código dos 30 casos de `U_tipo_retorno`, `U_arg_nomeado` e `U_sandbox` não está
cortado pelo SQL. Isso **não** comprova completude upstream, contrato real da
ferramenta, causa única, recuperação ou suficiência da diretiva de memória.

**Proposta de piloto:** `U_tipo_retorno`, por recorrência em dez meses e custo
observado elevado; investigar possíveis sublições por ferramenta/papel e
contrato do retorno. Não escrever a memória apenas a partir do nome do catálogo.
`U_campo_inexistente` requer conferir o prompt antes de decidir se o conserto é
no harness; nomes/estado são proxies, não prova de namespace.

**Ainda falta para gerar JSON final:** leitura aberta/fechada independente,
categorias aprovadas, concordância e regras contadas, auditoria semântica,
evidência suficiente da orientação e decisão do pesquisador; localização final
via `action_idx` dos erros ou evolução aprovada do esquema. Não foi gerado JSON
de memória nem realizada promoção. Taxas globais, silenciosas completas,
sucesso semântico, kit/evidências legadas continuam não habilitados.
