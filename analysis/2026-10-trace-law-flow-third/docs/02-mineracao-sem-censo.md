# Mineração dos erros observados — contrato, racional e procedimento

> **Atualização de 07/10, após restauração:** fonte histórica recuperada e
> rodada real concluída/conferida tecnicamente. Ver [resultado atual](04-relatorio-rodada-observada-real.md).
> A ocorrência de fonte inválida abaixo é histórico, não bloqueio atual.
> Gates semânticos, localização final e kit continuam pendentes.

> Códigos: [glossário](../../glossario.md). Método de referência:
> [erro → memória](../../2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md) e
> [procedimento de candidatas](../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md).

**Data:** 07/10/2026. **Autorização:** implementação do plano de retomada sem
censo, seguida da autorização para continuar com testes sintéticos enquanto o
pesquisador restaura/confere a fonte. **Contrato:** `mineracao_erros_observados_v1`.
Não é fechamento integral, nova taxonomia, memória aprovada nem execução Athena.

## 1. Por que este modo existe

A second contém 1.000 registros de execuções com traces brutos. A third contém
problemas exportados e suas janelas: não é censo das ações nem trace completo.
O caminho completo `carregar_base()` permanece bloqueado para fontes estruturais.
Retirar esse guard permitiria índices, custos totais e ausências fictícios.

O [novo módulo](../pipeline/mineracao_observada.py) compõe carga, sintomas e
mecanismos elegíveis e implementa consumidores **somente do observado**. Não
chama `montar_unidades`, `medir_sucesso` ou `falhas_silenciosas` do caminho raw.
As regras `classify`, `submecanismo`, `sinais_de_parsing`, `SUB2UNI` e `UNI`
continuam as existentes. Nome/unidade do catálogo não é diretiva factual
validada nesta base. Destinos específicos da base 1/2 não são herdados.

## 2. Proveniência e situação da fonte

O inventário da retomada comparou SHA-256, não timestamps: **os dez CSVs
canônicos da third e o Sankey são idênticos aos da second**. São legado, não
resultado da third. Incluem 479 linhas de erros e 1.000 de execuções. Nenhum
foi apagado nem sobrescrito; o novo caminho não os lê como entrada.

Os relatórios e resultados datados da Etapa 7 descrevem sua fonte histórica.
No início desta implementação, o arquivo local tinha **426.346.727 bytes**, hash
`50e0dd38a3e37d397344bf5dbf80d4ef3a71c0d30c41513915471ec36d192238`, distinto da
referência histórica, e `pyarrow.parquet.read_metadata` falhou com `Invalid data`.
Não sabemos se foi substituição, sincronização incompleta ou outro problema.
Não houve reparo, releitura de casos ou classificação real dessa fonte.

**Gate atual:** restaurar/conferir o arquivo. Se for uma nova exportação, fazer
intake e declarar nova coorte/snapshot; não forçar contagens da Etapa 7 como
asserts. Outputs de notebooks são restaurados e não certificados; os cabeçalhos
os identificam explicitamente. Testes Python de sources sintéticos não são
execução Jupyter confirmada.

## 3. Universo e capacidades

| Capacidade | Neste modo |
|---|---|
| Sintomas, mecanismos/unidades | Apenas insumos elegíveis por regra |
| Recorrência | Execução + agente, papel e mês real; observada, não taxa de risco |
| Ocorrência | Componente estruturada × unidade, condicional aos vínculos |
| Custos | `n` único; conhecido + quantidade de ausentes |
| Contexto | Slots e vínculos; ausência/não identificação = desconhecido |
| Silenciosas | Não medidas, nunca zero artificial |
| Suspeitas | Canal separado, fora da taxonomia oficial |
| Taxas/orçamento globais | Bloqueados; agregado opcional próprio |
| Sucesso semântico/chamada/namespace | Não comprovados |
| Localização | `step_ref`, identidade e `step_pos`; `idx` só se a fonte o possuir |
| Memória/skills legadas | Não aprovadas/habilitadas automaticamente |

### Triagem e ocorrências

Componentes são construídas **antes** de selecionar mecanismos observáveis.
Um erro intermediário pendente não desaparece para criar uma nova cascata.
Vínculos candidatos, fronteiras abertas e custos pendentes são preservados.
Ocorrências condicionais não são contagens exatas de episódios nem
necessariamente limites inferiores: vínculos ausentes podem dividir uma cascata.
Não usar Pareto de ocorrências condicionais como prioridade definitiva.

A candidatura exige ≥3 execuções e ≥2 meses; a sensibilidade usa ≥5/3.
São evidências de recorrência no subconjunto atribuído. O não atendimento é
**recorrência não demonstrada**, não inexistência do padrão. Plataforma permanece
não-memória, críticos vão à investigação e resíduos à revisão por padrão.
Não aplicar alarme histórico da taxonomia com outro denominador sem decisão.
Soma de tokens ausentes não vira zero; percentuais de custo ficam indisponíveis
se o universo tiver custos desconhecidos. Custos conhecidos não são economia.

## 4. Procedimento executável após restaurar a fonte

Da raiz, entrada única [executar.py](../pipeline/executar.py). A implementação
de geração mora em [execucao](../pipeline/execucao/executar_observada.py) e
as verificações em [validacao](../pipeline/validacao/validar_observada.py):

1. Inventário, sem minerar fonte:
   `uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py inventariar`.
2. Intake e mineração visível:
   `uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py analisar`.
   Para exigir snapshot conhecido, adicionar `--referencia-sha256 <hash conferido>`;
   para outra exportação, `--fonte <arquivo local>`, seguido de intake próprio.
3. Só depois de uma unidade passar nesta triagem, solicitar `--perfil <unidade>`.
   Isso gera G1–G6 e amostra estrutural, não redige a lição.
   `validar` roda a suíte/AST; `conferir` roda conferência real e prepara todos os
   perfis. São ações distintas, não pré-condições para redigir memória automaticamente.
4. Alternativa pelo editor: [consolidação](../pipeline/consolidacao_unidades.ipynb)
   e [mineração genérica](../pipeline/mineracao_generica.ipynb), com `UNIDADE`
   definida no ambiente. Não executar o restante do notebook principal como se
   a análise completa tivesse sido integrada.

Saídas vão a **uma subpasta privada da rodada**, nunca à raiz canônica. Manifesto
carimba fonte, contrato, código dos consumidores e hashes de cada artefato;
`ler_artefato` rejeita outra base/rodada/código, estado incompleto ou hash alterado.
Hash de código dos notebooks ignora outputs/metadados de execução, mas inclui
sources/tipos das células. Não há publicação canônica ou atualização do kit.

Entregas: cobertura, triagem visível e por papel, sensibilidade, custos,
genealogia conservando pendências, gráficos de unidades/papéis e perfis opcionais.
Casos e amostras têm referências privadas, sem payloads exibidos nos notebooks.
Cada perfil distingue primeira ferramenta registrada de origem do valor,
versão de agente de variante do prompt, final no vizinho de sucesso.

## 5. Complementos opcionais, sem bloquear a triagem

### 5.1 Agregados para exposição e orçamento

[Proposta de agregados](proposta_agregados_sem_censo.sql): SELECT sobre a mesma
elegibilidade/ranking do SQL produtor, antes de filtrar problemas. Exporta
contagens e somas conhecidas/ausentes, por mês/papel/versão/canal e no total;
controle de snapshots/parse/classes, sem ActionSteps ou payloads no resultado.
É proposta estática, não Athena/EXPLAIN/benchmark; agrupar reduz transferência,
não garante menor custo computacional. Não fornece medianas, Lorenz ou sucesso.

Recebimento exige identificação query/engine/snapshot, controle de perdas,
conferência dos problemas atuais e validação dos NULLs. Linhas de níveis
GROUPING SETS se sobrepõem e controles globais são repetidos: não somar níveis.
Execuções representadas por canal também se sobrepõem, pois uma execução pode
ter ações dos três canais. Para comparação de execuções com/sem erro, agregar
a execução **inteira** antes de formar os grupos e solicitar distribuição de
custos ou estatísticas específicas no banco.

### 5.2 Metadados somente dos problemas

Solicitar, calculando **antes do filtro final**:

- identidade execução/agente/papel original, snapshot/query e hash do trace;
- `action_idx`, `n_actions_role`, `step_pos` e posições/presença dos vizinhos;
- tipo/flags do predecessor, `is_final_answer` de n e posição da última flag final;
- contador TaskStep calculado antes de remover as classes; não prova namespace;
- comprimentos originais/flags de corte dos textos de n e slots;
- tipo e representação JSON de retornos quando necessários.

É complemento por chave, não novas ações a concatenar. O legado não tem hash
de trace; reexecução numa tabela mutável pode mudar snapshots. Não corrigir o
filtro NULL/tamanho ou particionar diferente silenciosamente: comparar e declarar
a alteração de coorte/contrato. Metadados podem recuperar `idx` dos erros sem
exportar o censo. Agregados não recuperam o conteúdo/contexto faltante.

### 5.3 Material dirigido para lições

Mensagem/código integrais dos casos limitados; prompt/inventário/contrato real
da versão; histórico anterior requerido pela regra; retornos e correções
selecionados; traces do pool técnico para ambiguidades/fronteiras. Amostra por
regra fixa, estratificada por papel/mês/cobertura, ampliada se insuficiente.
O pool técnico não substitui a amostra semântica da candidata.

## 6. Gate até o esquema da memória

G1–G6 não escrevem a lição. Depois: leitura aberta independente → aprovação da
lista → leitura fechada → concordância/regras contadas → auditoria independente
→ dossiê → decisão memória/harness do pesquisador. Evidência insuficiente
interrompe aquela unidade, não toda a mineração visível. Custo alto não é causa
nem confiança. Nenhum texto histórico `UNI` é copiado automaticamente como
orientação checada.

O [esquema 0.1](../../esquema-memoria.json) continua inalterado nesta entrega.
Seu `location.idx` é ordinal de ActionStep, desconhecido em janelas. Os perfis
preservam localizador real, mas **não são arquivos finais de memória**. Antes
de finalizar uma candidata, escolher: metadados só dos erros para recuperar
`action_idx`, ou evolução aprovada para localizador tipado `step_pos`/`step_ref`
com origem e fonte. O validador atual confere tipos superiores; passar nele não
resolve localização nem valida semanticamente uma lição.

**Ainda pendentes:** execução real após restauração; leitura independente;
piloto/dossiê/JSON; localização final; integração de evidências/drill-down,
monitoramento e skills/manifesto. O kit real disponível neste checkout está em
`.github/skills`; a árvore `.claude` referida nos docs anteriores não está
disponível. Não regenerar manifesto para ocultar diferença nem rodar auditorias
legadas que pressupõem trace completo. Bases 1/2 e diário foram preservados.

## 7. Verificação desta implementação

[Testes sintéticos](../../tests/test_mineracao_observada_base3.py) cobrem
proveniência/alteração de custos, NULLs, suspeitas fora, componentes antes do
subconjunto, recorrência/sensibilidade/destinos por base, localização sem idx,
publicação identificada e todas as células dos dois consumidores em Python
controlado. A magic gráfica é omitida, sem editar outputs por script.

Reprodução: `uv run python -m unittest discover -s analysis/tests -p 'test_*.py' -v`.
Contagens/log e limitações da rodada ficam no [relatório](03-relatorio-retomada-sem-censo.md).
Teste/recomputação não é auditoria semântica independente. Benefício causal e
redução de recorrência cross-trial precisam de experimentos posteriores.
