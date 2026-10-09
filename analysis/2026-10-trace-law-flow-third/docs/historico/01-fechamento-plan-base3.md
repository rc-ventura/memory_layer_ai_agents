# Fechamento do plano de adaptação — base 3

> Códigos e siglas: [glossário](../../glossario.md).

> **Retomada posterior em 07/10:** este fechamento registra a fonte histórica
> da Etapa 7. O [modo observado sem censo](02-mineracao-sem-censo.md) implementa
> triagem/perfis parciais e tem [validação sintética própria](03-relatorio-retomada-sem-censo.md).
> O arquivo local da retomada divergiu do hash abaixo e não abriu como Parquet;
> execução real suspensa até restauração/conferência. Não aplicar os números
> deste documento ao arquivo divergente. Demais gates continuam independentes.

> **Restauração posterior confirmada:** o arquivo histórico foi recuperado,
> reproduziu o hash e abriu normalmente. A [rodada real sem censo](04-relatorio-rodada-observada-real.md)
> concluiu triagem visível/perfis; não é fechamento semântico/integral.

**Data:** 07/10/2026. **Escopo:** plano iterativo de adaptação ao Parquet,
não encerramento do roadmap geral do projeto.

**Veredito:** fechada e validada tecnicamente a integração disponível até a
Etapa 7. O plano integral permanece **parcial e condicionado** ao §4; não houve
auditoria semântica independente nem execução Jupyter integral confirmada.

## 1. Critério de fechamento

Separar conclusão da implementação disponível de validação integral do estudo.
O objetivo é reutilizar o método existente, não fabricar informação para obter
100% de cobertura. O Parquet atual é a fonte de verdade; não se reconstrói um
`txt_etap_memo` fictício nem se transforma ausência em sucesso/custo zero.

| Etapa | Estado | Entrega / condição de saída |
|---|---|---|
| 1 — diagnóstico do Parquet/SQL | Concluída | Chaves, canais, cortes, custos e restrições da extração identificados |
| 2 — especificação e pool técnico | Concluída | Mapeamento das análises e pedido privado de quatro traces; não equivale a recebimento |
| 3 — propostas A/B | Concluída como proposta | Consultas complementares (documento removido em 08/10; o que ficou está no [contrato sem censo](02-mineracao-sem-censo.md) §5); revisão estática, sem Athena |
| 4 — núcleo estrutural | Concluído e validado tecnicamente | [Adaptador](../../adaptador_trace.py), identidade, slots e vínculos com cobertura |
| 5 — integração da carga | Concluída e validada tecnicamente | [Pipeline](../pipeline/base_pipeline.py), modo `apenas_carga` e bloqueios explícitos |
| 6 — sintomas e custos | Concluída e validada tecnicamente | Mensagens elegíveis, custos preservados e suspeitas fora da taxonomia |
| 7 — mecanismos e episódios | Concluída e validada tecnicamente | [Episódios](../../episodios_trace.py) e trecho integrado do [notebook](../pipeline/analise_trace_esteira_juridica.ipynb) |
| Complementos e demais consumidores | Não concluídos | Condições e dependências descritas no §4; não marcar como feitos |

## 2. Validação reproduzível

O [validador técnico histórico](../pipeline/validacao/historico/validar_base3.py) executava,
no checkout daquela etapa (entrada atual protegida para não sobrescrever o histórico):

1. A suíte de testes do adaptador, sintomas, mecanismos, episódios e regressão
   **sintética** dos caminhos raw das bases 1/2.
2. Leitura direta pelo PyArrow, independente do leitor/adaptador em produção,
   para conferir contagens, tokens e duração de `n`.
3. Segunda implementação da comparação recíproca das janelas e contagem dos
   componentes estruturados/mistos; conserva as ambiguidades.
4. Conservação de erros/custos nos quadros de cobertura e pendências; suspeitas
   não entram na taxonomia e slots não são somados como ações.
5. Comparação AST das regras existentes, sem criar uma nova taxonomia.
6. Smoke **Python** das oito células integradas, gráficos e bloqueio esperado
   na seção 3.1. A magic gráfica é omitida; o notebook não é regravado por script.
7. Hash da fonte e preservação dos arquivos anteriores em relação ao baseline
   da Etapa 7. Arquivos novos são entregas desta adaptação, não artefatos antigos.

O comando efetivamente usado e suas saídas ficam registrados no relatório de
validação. Não interpretar recomputação como auditoria semântica independente:
ela verifica medidas e invariantes, não a causa real nem a lição de um caso.

**Jupyter:** as tentativas pelo editor não trouxeram execução concluída nem
metadados atuais. Outputs restaurados não comprovam execução. A validação
Python não deve ser descrita como execução Jupyter integral.

### Ocorrência no validador

A primeira execução completa parou na comparação direta de vínculos. O Parquet
tipa números de `n` como inteiros e vizinhos nullable como `double`; o verificador
comparava suas representações textuais (`2` versus `2.0`), gerando conflito falso.
O verificador foi corrigido para comparar valores numéricos, sem alterar o
adaptador ou a taxonomia. Cinco regressões sintéticas passaram: equivalência
inteiro/double, diferença real, custo ausente, reset e número ausente.

A rodada interrompida **não é validação aprovada**. A nova execução completa é
a referência para o estado final, com as regressões adicionais incluídas.

## 3. Resultados da rodada

**Rodada final aprovada tecnicamente:** 126 testes e 30 verificações passaram.
O estado gravado é `integracao_parcial_validada_tecnicamente`.

| Medida | Resultado |
|---|---:|
| Registros `n` preservados | 31.421 |
| Erros estruturados | 30.141 |
| Suspeitas fora da taxonomia | 1.280 |
| Mensagens elegíveis para sintomas | 29.132 |
| Mensagens limitadas, sem classificação | 1.009 |
| Mecanismos observáveis pela regra/proxy existente | 23.034 |
| Mecanismos pendentes por insuficiência de evidência | 7.107 |
| Vínculos candidatos compatíveis | 7.843 |
| Vínculo mantido ambíguo | 1 |
| Tokens nos erros estruturados | 592.858.874 |
| Tokens atribuídos a mecanismos observáveis | 449.653.876 |
| Tokens em mecanismos pendentes, preservados no custo | 143.204.998 |

Pendências de mecanismos: predecessor não identificado pelo SQL **5.818**;
mensagem limitada **1.009**; timeout sem prompt/código suficientes **215**;
linha rejeitada sem código integral **46**; histórico insuficiente para excluir
retorno colado **14**; numeração/predecessor ambíguos **5**. Esses motivos não
são novos mecanismos ou resíduos da taxonomia.

| Definição de componente | Componentes | Âncoras | Fechadas na definição | Maior componente |
|---|---:|---:|---:|---:|
| Estruturada | 22.848 | 30.141 | 10.380 | 19 |
| Mista (`error_like`) | 23.578 | 31.421 | 11.077 | 19 |

As duas linhas se sobrepõem; não somar custos/âncoras entre elas. A segunda
implementação conferiu vínculos, número de componentes e conservação dos
custos; não conferiu semanticamente cada limite, chamada ou causa.

**Evidências locais da rodada:** [resultado das verificações](../pipeline/resultados/validacao_fechamento_2026-10-07/validacao.json),
[log dos 126 testes](../pipeline/resultados/validacao_fechamento_2026-10-07/testes.txt),
[log do smoke Python](../pipeline/resultados/validacao_fechamento_2026-10-07/smoke_python.txt)
e [componentes agregadas](../pipeline/resultados/validacao_fechamento_2026-10-07/componentes_agregadas.csv).
Esses resultados são privados/git-ignored; o resumo acima é a evidência
versionável, sem texto ou identificador de caso.

**Execução usada:** `uv run python analysis/2026-10-trace-law-flow-third/pipeline/validar_base3.py`,
a partir da raiz do repositório, **no checkout histórico**. O arquivo foi depois
movido para validação/histórico; não repetir esse comando na versão atual.
O validador executou `unittest discover` e as
células 2, 4, 6, 8, 10, 12, 14 e 16 em Python controlado. A célula 18 produziu
o bloqueio esperado na seção 3.1; os três gráficos atuais foram gerados.
As demais células de código foram compiladas, não executadas.

O SHA-256 da fonte permaneceu
`7604f77df9fe6127bd7fb9db18337b558b1f2587b0a99621c087b0cf3c2873f1`,
igual à Etapa 6. As cinco regras comparadas por AST foram preservadas.
No baseline de arquivos anteriores da Etapa 7, só mudaram o pipeline e o
notebook principal da base 3; bases 1/2, consultas e kit foram preservados.

## 4. O que continua aberto e por quê

| Frente | O que falta | Critério para desbloquear |
|---|---|---|
| Taxas globais, orçamento e comparação com ações sem erro | Ações sem sinal não estão no Parquet atual | Receber **A + problemas**, com união disjunta validada, **ou B**, com censo/snapshot conferidos; manifest de elegibilidade |
| `idx` ActionStep e sequência completa | `step_pos` inclui outras classes e a população foi filtrada | Censo/união completos e validados; não enumerar só as linhas problemáticas |
| Continuidade por chamada, namespace e numeração ambígua | TaskSteps/prompt/histórico completo não exportados | Conferir os quatro traces do pool no mesmo snapshot; B traz contador, não prova namespace |
| Mensagens/códigos limitados e mecanismos pendentes | Texto, prompt ou histórico insuficientes | Traces dirigidos e suficiência dos insumos de cada regra; não preencher pendência como resíduo |
| Sucesso por conteúdo e recuperação semântica | Payload final completo/ground truth indisponíveis | Dados correspondentes e protocolo próprio; flag final e vizinho sem sinal não são sucesso |
| Falhas silenciosas | Sinal produtor não é o detector original; faltam inventário e observações completas | Adaptar consumidor com cobertura e conferir interseção dos canais; não substituir automaticamente suspeitas por silenciosas |
| Consolidação, triagem e mineração de candidatas | Ocorrências/canais ainda não integrados nos consumidores finais | Integração explícita e testes; gates do pesquisador preservados, sem herdar destinos das bases 1/2 |
| Demais notebooks, `drill_down`, evidências, skills e auditorias | Preservados, mas ainda assumem trace completo | Adaptar contratos/capacidades, versionar kit e fazer encontro com auditoria independente; não rodar cópias legadas como resultado da base 3 |
| Execução integral no Jupyter | Editor não confirmou execução | Kernel funcional e metadados/log atuais do trecho compatível; estudo completo continua condicionado aos demais insumos |

**Ordem de retomada:** receber/conferir o material → resolver lacunas dirigidas →
integrar os consumidores restantes com seus gates → auditoria independente →
fechamento integral. O pedido ao tutor já está preparado em resultados privados;
nenhum ID ou texto de caso entra neste documento.

## 5. Limites das conclusões

- Um mecanismo observável é a aplicação elegível de uma regra/proxy existente,
  não prova de causalidade ou validação factual do texto da memória.
- Componentes fechadas são fechadas na definição da extração/papel, não prova
  de mesma chamada ou de recuperação. Vínculos de janelas são candidatos.

<!-- TRANSCRIÇÃO: o resto do §5 (depois da linha 160 na máquina 2) não estava nas fotos. -->
