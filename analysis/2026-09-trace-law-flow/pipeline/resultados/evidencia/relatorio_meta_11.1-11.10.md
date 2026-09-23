# Meta-relatório independente — evidências 11.1 a 11.10

> ⚠️ **Desatualizado desde 23/09/2026 — refazer.** Esta auditoria verificou a amostra de casos escolhida quando
> o `mes` vinha de `anomesdia` (o lote de corte). Hoje o `mes` vem de `dat_hor_inio_exeo` (quando a execução
> rodou) e as regras de escolha, que ordenam por mês, trocaram parte dos casos desta pasta. Não citar como
> verificação da amostra atual. → `docs/04-roadmap.md` (Agora) · `docs/03-procedimento-validacao.md` §1.12

Data: 2026-09-18 (estende `relatorio_meta_11.1-11.8.md`, de 2026-09-17)

## Escopo

Este meta-relatório consolida as auditorias independentes produzidas para as pastas
`11.1_origem_do_erro/` até `11.10_leituras_get_available_documents/` do notebook
`mineracao_unidades_n2_n10.ipynb` §11, mais a decisão sobre a pasta `avulso/`. O objetivo é
responder, em um único lugar, se a cadeia de validação da §11 se sustenta quando reaberta a
partir do trace cru.

As leituras foram feitas com base nos `crus/*.json` de cada pasta de evidência, usando
`casos.csv`, `leia-me.md`, `unidades_memoria.json` e os documentos de método apenas como índice
e referência interpretativa. Para 11.9 e 11.10, a auditoria incluiu **recomputação independente
do universo inteiro** no CSV bruto (`csv.DictReader` + `json` + `ast`, sem reusar o código do
notebook) — não só a releitura dos crus salvos.

## Relatórios consolidados

- `11.1_origem_do_erro/relatorio_independente.md`
- `11.2_schema_real/relatorio_independente.md`
- `11.3_prompt_declara/relatorio_independente.md`
- `11.4_conserto/relatorio_independente.md`
- `11.5_estabilidade/relatorio_independente.md`
- `11.6_status/relatorio_independente.md`
- `11.7_amostra_passo6/relatorio_independente.md`
- `11.8_registro_final/relatorio_independente.md`
- `11.9_leituras_quebra_sigilo/relatorio_independente.md`
- `11.10_leituras_get_available_documents/relatorio_independente.md`

## Veredito consolidado

### Síntese curta

A cadeia 11.1–11.10 ficou, no conjunto, **bem sustentada** pela auditoria independente. Não
apareceu nenhuma pasta que contradissesse frontalmente o que o notebook/publicação afirma — e as
duas novas auditorias (11.9, 11.10) confirmam os números centrais por recomputação, **diff zero**
no caso da 11.10. O quadro consolidado:

1. **Passo 1 (origem do erro)**: sustentado; as atribuições positivas conferem e os
   `não resolvido` permanecem cautelas justificadas.
2. **Passo 2 (schema real)**: sustentado; quando o objeto aparece na mensagem, a forma registrada
   bate com o cru, e quando não aparece a categoria `objeto não lido` é apropriada.
3. **Passo 3 (o que o prompt declara)**: sustentado e importante; separa corretamente
   **prompt contraditório** de **prompt omisso**.
4. **Passo 3b / conserto**: sustentado; o step seguinte realmente contém os padrões de correção
   que o notebook classificou.
5. **Passo 4 (estabilidade)**: sustentado; os schemas das candidatas são estáveis por nível da
   estrutura, com uma única variação de "campos a mais" em ago/2026 para
   `get_available_documents`.
6. **Passo 5 (status/cobertura)**: sustentado no estado final dos artefatos; a pasta 11.6 ficou
   vazia porque o resíduo foi fechado, o que bate com os docs.
7. **Passo 6 (amostra humana)**: sustentado; a amostra 11.7 confirma diretamente no cru as
   interpretações centrais das duas candidatas.
8. **Passo 8 (registro final)**: sustentado na parte auditável; `location`, `evidence` e os casos
   escolhidos batem entre si e com os crus.
9. **Passo 9 (o que o campo entregou — nº9/quebra_sigilo)**: sustentado; 9/21 (43%) de entregas
   fora de SIM/NAO recontadas idênticas; as duas retratações (cadeia `.get` aninhada; escopo do
   detector de grafia) estão corretas — com **duas ressalvas redacionais** (ver §Limites).
10. **Passo 10 (universo completo de leituras — nº2/get_available_documents)**: sustentado com
    diff zero; 4 ocorrências silenciosas + 1 guarda de chave fantasma confirmadas; 0/5 dano medido
    na resposta final — a retratação da exploração anterior está correta.

## O que cada pasta validou

| pasta | pergunta validada | resultado independente |
|---|---|---|
| `11.1_origem_do_erro` | de qual função/ferramenta vem o erro? | **confirma** 7/7 atribuições positivas; mantém 5/5 `não resolvido` |
| `11.2_schema_real` | qual é o schema real impresso na mensagem? | **confirma** 6/6 objetos parseáveis; 4/4 `objeto não lido` corretos |
| `11.3_prompt_declara` | o prompt declara a chave certa, errada ou nenhuma? | **confirma** `validar_quebra_sigilo` e `extrair_evidencias` como contraditórios; `get_available_documents` como omisso |
| `11.4_conserto` | o que o agente faz depois do erro? | **confirma** os 3 tipos de conserto; 4/5 passos seguintes sem erro, 1/5 com erro novo posterior |
| `11.5_estabilidade` | a forma é estável ao longo dos meses? | **confirma** estabilidade; 1 variação com campos extras nulos em ago/2026 |
| `11.6_status` | a cobertura/resíduo fecha? | **confirma** consistência do artefato final: resíduo real = 0, por isso pasta sem casos |
| `11.7_amostra_passo6` | a leitura do cru numa amostra cega confirma os achados? | **confirma** os dois mecanismos centrais; nota adicional: erro de `draft_resposta` aparece em 1/10 caso |
| `11.8_registro_final` | os casos citados no registro final batem com `location` e com o cru? | **confirma** `evidence = 3 primeiros casos de location` para as 2 candidatas |
| `11.9_leituras_quebra_sigilo` | o que o campo `quebra_sigilo` entregou de fato? | **confirma** 26 declaram / 21 entregam / 9 fora de SIM/NAO (43%) em 3 meses; ambas as retratações corretas; 122/122 trechos conferem; 2 ressalvas redacionais |
| `11.10_leituras_get_available_documents` | o que o universo inteiro de leituras mostra? | **confirma** 635 papéis / 597 leituras / 4 silenciosas / 1 guarda fantasma — diff zero; 0/5 dano medido; 64/64 trechos conferem; 2 notas de precisão |

## Achados integrados por mecanismo

### 1. Candidata nº2 — `(ConversationAgent, get_available_documents)`

A leitura consolidada das pastas 11.1–11.5, 11.7, 11.8 e **11.10** converge para o mesmo
mecanismo, agora com contagem exaustiva:

- o retorno real relevante é um **dict** cujo topo traz `result`;
- o universo completo tem **597 leituras** do retorno; as 93 leituras erradas-desprotegidas-com-erro
  cobrem 85 steps únicos, e os 11 erros restantes da nº2 são acessos com a **chave real** em
  profundidade/forma errada (`r['result'][0][0]`, iteração direta do dict) — a mesma família de
  mecanismo, outra face;
- além dos erros, o universo expõe **4 leituras silenciosas** (chave errada sem guarda, sem
  proteção e sem exceção) — heterogêneas: 1 `.get` canônico, 2 `x[0]` sobre retorno-string
  (interseção com `U_tipo_retorno`), 1 fallback morto — e **1 guarda de chave fantasma**
  (`if 'documents' in pasta_docs`) que descarta os documentos reais;
- **nenhuma das 5 ocorrências produziu dano medido** na resposta final do `managerAgent`
  (0/5 em `DEGENERADO`, `None`/`null` e forma-dict) — o que corrige a leitura exploratória
  anterior e mantém `impact=null`, `destino=memory`;
- o prompt da ferramenta **não declara explicitamente** o envelope `result`, mas descreve
  "documentos + summary", o que deixa margem para inferência errada;
- quando o agente corrige, o acesso mais estável observado é `r['result'][0]`.

### 2. Candidata nº10 → nº9 — `(RespostaBacen, validar_quebra_sigilo)`

A leitura consolidada das pastas 11.1–11.5, 11.7, 11.8 e **11.9** converge ainda mais fortemente,
agora com medição do payload final:

- o retorno real é `{justificativa, vazamento_sigilo}`;
- o prompt da ferramenta declara `{quebra_sigilo, motivo}`;
- **9/21 (43%)** das execuções que entregam o campo `quebra_sigilo` na `request` final o entregam
  **fora dos valores regulatórios SIM/NAO** — 7 o objeto inteiro, 1 texto livre, 1 string vazia —
  em 3 meses distintos (dez/2025, mai/2026, jun/2026);
- o mecanismo é silencioso no sentido que importa: nenhum erro registra a entrega do campo errado
  (ressalva de redação: 2/9 execuções têm exceções na trajetória, mas em outros campos/mecanismos
  do mesmo dict final — ver §Limites);
- comparações de grafia divergente existem (5 registradas: 2 não avaliadas na linha da falha, 3
  avaliadas num guard-rail defensivo `in ["NÃO","NAO","Não","Nao"]`).

Aqui a evidência é mais forte do que na nº2 porque há **contradição explícita de contrato** entre
prompt e runtime, não só omissão — e a medição do payload entregue (9/21) é mais direta que a
contagem de erros.

### 3. Subunidade de 1 caso — `extrair_evidencias`

Embora não seja candidata recorrente no Passo 1, ela aparece de forma relevante nas auditorias:

- o prompt declara `informacoes_evidencias`;
- o retorno real auditado traz `dados_evidencias`;
- o agente pede a chave do prompt e depois corrige para a chave real.

Ou seja, o mesmo padrão de **prompt contraditório** existe aqui, mas sem recorrência suficiente
para virar candidata como as duas principais.

## O que ficou mais forte depois da auditoria independente

### A. A distinção "prompt contraditório" vs "prompt omisso" não é retórica

Ela ficou confirmada diretamente no cru:

- **contraditório**: `validar_quebra_sigilo`, `extrair_evidencias`;
- **omisso**: `get_available_documents`.

Isso importa porque muda a interpretação causal do erro:

- se o prompt contradiz o runtime, o agente pode estar simplesmente obedecendo à instrução errada;
- se o prompt é omisso, o erro depende mais da inferência estrutural do agente sobre o retorno.

### B. A correção do agente é observável e informativa

Os passos seguintes ao erro, auditados em 11.4 e amostrados de novo em 11.7, mostram que o agente
frequentemente:

- lê a chave real no log/erro do próprio step;
- atualiza o acesso no step seguinte;
- às vezes escreve um conserto mais robusto, aceitando dois contratos (`.get`) ou guardando o tipo.

Isso fortalece a ideia de que o registro final não está "inventando" o `correction_guidance`; ele
o deriva de padrões reais de autocorreção.

### C. O schema das duas candidatas é estável o suficiente para virar guidance

A auditoria de 11.5 e a validação por amostra de 11.7 mostraram que:

- `validar_quebra_sigilo` é estável nos meses observados;
- `get_available_documents` também é estável no nível relevante, com uma única variação por
  campos extras simples e nulos.

Isso dá base empírica para transformar a leitura em guidance reaproveitável.

### D. Medir o payload final e o universo inteiro muda o tipo de conclusão

As duas auditorias novas mostram o valor do salto metodológico da §11.9/§11.10:

- medir `action_output.request` (11.9) em vez de inferir do código corrigiu uma leitura falsa
  positiva (`8dd410c8…`) e produziu a métrica mais direta da análise (9/21 entregues errados);
- contar o universo inteiro de 597 leituras (11.10) em vez de amostrar casos conhecidos revelou
  dois mecanismos que a contagem por erros não via (leituras silenciosas; guarda de chave
  fantasma) — e, ao mesmo tempo, **derrubou** a suspeita exploratória de dano na resposta
  (0/5 medido).

## Decisão sobre `avulso/`

**Decisão: `avulso/` não requer relatório independente próprio.**

Justificativa auditada: a pasta contém 4 pulls avulsos de `drill_down.py evidencia` — casos
individuais salvos fora de uma análise numerada, não uma pergunta analítica nova:

- `aa3de754…` idx2 — o caso de resíduo histórico (Passo 5/6) materializado quando uma auditoria
  anterior constatou que ele só existia descrito em prosa. É artefato **suplementar** da trilha
  de resíduo já coberta por 11.6/11.7 (o outro caso residual, `3f44a68b…`, está em
  `11.7_amostra_passo6`).
- `15f6ad52…` idx0 e `910fde1e…` idx0 — leftovers da sessão exploratória pré-retratação (§1.11);
  ambos agora têm cópias canônicas dentro da evidência reconciliada de `11.10`.
- `ad9044ad…` idx0 — idem (exemplo de leitura guardada por `isinstance`, fora das 4 silenciosas).

Verificação executada nesta auditoria: **30/30** `trechos_do_cru` dos 4 derivados conferem com os
crus (incluindo os 11/11 já registrados para `aa3de754…` em `03 §1.9`). A pasta é evidência
suporte, íntegra, sem conclusão própria a auditar — documentada aqui para fechar o item do
roadmap.

## Limites e ressalvas

1. **11.6 é diferente das outras pastas.** Ela valida o estado final do artefato, não reabre
   casos, porque hoje não há mais crus nela.
2. **A nº9 ainda mantém uma questão conceitual em aberto** já registrada nos docs: como o conserto
   contradiz o próprio system prompt, o destino "memória × harness" segue pendente — a 11.9
   registra `destino=harness`, que é a decisão da análise, não resolução da questão conceitual.
3. **O erro de `draft_resposta`/assunto inválido não deve ser generalizado.** Ele apareceu em 1
   caso da amostra 11.7 (`9be7b413…`), como fenômeno local, e não como explicação da subunidade
   inteira.
4. **Os relatórios independentes validam a cadeia observável**, não um replay contrafactual
   completo. Eles mostram que os artefatos batem com o cru; não provam sozinhos que um prompt
   corrigido evitaria todos os erros.
5. **Ressalva redacional da 11.9**: a frase "sem nenhuma exceção registrada em nenhuma delas" é
   literalmente falsa para 2/9 execuções (`95344639…`, `dbc472b0…` têm 3 exceções cada na
   trajetória — em outros campos/mecanismos). A tese de silêncio do mecanismo se mantém
   ("nenhum erro registra o `quebra_sigilo`"), mas a redação — inclusive no `impact` de
   `unidades_memoria.json` — deve ser corrigida no próximo rerun.
6. **Ressalva redacional da narrativa de grafia (11.9)**: `07 §6.2` diz "2 comparações divergentes
   nunca avaliadas"; `grafia.csv` registra 5 — 2 não avaliadas + 3 avaliadas num `in [...]`
   defensivo (inócuas, mas avaliadas). A conclusão de risco se mantém; a narrativa omite metade
   do universo.
7. **Notas de precisão da 11.10**: (a) as "4 leituras silenciosas" são 4 vereditos do detector
   sobre 3 mecanismos distintos (`.get` canônico; `x[0]` em retorno-string; código morto);
   (b) a reconciliação publicada "93 ≈ 91" deve ser lida como "93 leituras / 85 steps únicos +
   11 erros de forma/profundidade com a chave real = os 91 steps de erro da nº2".
8. **O que 11.10 não estabelece**: groundedness/completude factual das respostas — os detectores
   medem forma, não correção. Se a guarda fantasma empobreceu a resposta ao descartar documentos
   reais permanece em aberto.

## Conclusão final

No conjunto, a auditoria independente **valida a espinha dorsal da seção 11** do notebook e dos
achados publicados, agora incluindo as duas análises de universo/payload:

- a origem dos erros foi atribuída de forma defensável;
- o schema real foi lido corretamente quando o erro o expôs;
- o conteúdo do prompt foi distinguido corretamente entre contradição e omissão;
- os consertos escritos pelo agente foram classificados de forma fiel;
- a estabilidade temporal das duas candidatas se sustenta;
- o fechamento do resíduo é coerente com os artefatos finais;
- a amostra humana confirma os mecanismos centrais diretamente no cru;
- o registro final está bem ancorado em casos reais, com `location` e `evidence` coerentes;
- **a medição do payload final (11.9) reconta idênticos os 9/21 fora de SIM/NAO**, com ambas as
  retratações metodologicamente corretas;
- **a contagem exaustiva de leituras (11.10) reproduz com diff zero** os 597 registros, confirma
  4 silenciosas + 1 guarda fantasma e zera o dano medido nas respostas finais — corrigindo a
  leitura exploratória anterior.

Se eu tivesse que resumir em uma frase: **as auditorias independentes não encontraram uma ruptura
importante na cadeia 11.1–11.10; ao contrário, elas reforçaram que os dois mecanismos candidatos
estão bem identificados — com força maior para `validar_quebra_sigilo` (contradição explícita +
9/21 entregues errados medidos no payload) do que para `get_available_documents` (omissão +
mecanismos estruturais reais mas sem dano medido na resposta).**
