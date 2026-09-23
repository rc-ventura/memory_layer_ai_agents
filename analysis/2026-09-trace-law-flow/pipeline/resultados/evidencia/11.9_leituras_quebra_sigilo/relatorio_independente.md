# Relatório independente — 11.9 Leituras de quebra_sigilo

> ⚠️ **Parcialmente desatualizado desde 23/09/2026.** Os casos desta pasta não mudaram, mas as contagens por
> mês (ex.: "em 3 meses") usam o mês de `anomesdia` (o lote de corte); hoje o `mes` vem de `dat_hor_inio_exeo`
> (quando a execução rodou) e essas contagens mudam. → `docs/04-roadmap.md` (Agora) ·
> `docs/03-procedimento-validacao.md` §1.12

Data: 2026-09-18

## Escopo

Auditoria da sétima evidência externa da análise nº9 (`U_campo_vazio`: "campo do payload estruturado
entregue fora dos valores SIM/NAO" — aqui, `quebra_sigilo`). O resultado publicado afirma que, das
26 execuções `RespostaBacen` que declaram `validar_quebra_sigilo`, 21 chamam a ferramenta e entregam
o campo `quebra_sigilo` na `request` final — e que **9/21 (43%) entregam o campo fora dos valores
regulatórios SIM/NAO**: 7 o objeto inteiro, 1 texto livre, 1 string vazia — em 3 meses distintos,
"sem nenhuma exceção registrada em nenhuma delas". A análise também contém duas retratações
formais (§1.10 do `03-procedimento-validacao.md`) e uma tabela de comparações de grafia divergente.

O resultado é classificado `VALIDADO` com destino `harness` e `impact` = "campo regulatório
entregue fora dos valores válidos em 9/21 (43%) das respostas finais que entregam o campo, sem
exceção registrada — sem evidência de que o erro tenha sido percebido".

A auditoria reabre os 13 crus, verifica os 122 trechos salvos, reconta o universo inteiro no CSV
bruto (não só nos 13 casos salvos), classifica o valor entregue em cada execução, confere a tabela
de grafia e testa as duas retratações.

## Resumo executivo

Os números centrais e as duas retratações **conferem por leitura independente** — incluindo a
contagem 9/21 idêntica, mês a mês, com as mesmas classes de valor entregue. A publicação
"2 comparações divergentes nunca avaliadas" em `07 §6.2` é uma **subcontagem da saída formal**
(`grafia.csv` tem 5 comparações: as 2 não avaliadas na linha da falha **mais 3 avaliadas** dentro
de um `in [...]` defensivo — inócuas porque os literais divergentes já estão cobertos pelo
contexto). E a frase "**sem nenhuma exceção registrada em nenhuma delas**" é literalmente falsa
para 2 das 9 execuções: `95344639…` (3 erros) e `dbc472b0…` (3 erros) têm exceções na trajetória
— embora nenhuma delas assinale o mecanismo `quebra_sigilo` (elas falham em outros campos/mecanismos
do mesmo dict final). A afirmação de impacto "silencioso" **se sustenta** no sentido correto:
o campo errado é entregue sem que nenhum erro o registre — mas a redação "nenhuma exceção em
nenhuma" é imprecisa e deve ser corrigida no próximo rerun.

## Corpus auditado

| item | valor |
|------|-------|
| derivados | 13 `derivados/*.json` (um por (exec,role,idx)), 13 entradas em `casos.csv` |
| crus | 13 `crus/<exec_id>.json` |
| trechos | 122 `trechos_do_cru` — **122/122 conferem com o cru** |
| tabelas | `quebra_sigilo_por_papel.csv` (21 execuções), `grafia.csv` (5 comparações) |
| universo | 26 papéis `RespostaBacen` que declaram a ferramenta, no CSV bruto |

## Método

Sem reutilizar o código do notebook. Reimplementação independente com `csv.DictReader` +
`json.loads` + `ast`:

1. `csv.DictReader` (field_size_limit ampliado) varre as 641 linhas; `json.loads` aplica-se só às
   linhas `RespostaBacen` com `validar_quebra_sigilo` no memo.
2. `chamadas_de`: um step `code_action` "chama" a ferramenta sse o nome aparece seguido de `(` —
   contagem literal, por exec.
3. Valor entregue: `action_output.request.quebra_sigilo` no último step que chama a ferramenta —
   o que a §11.9 chama "o que o campo entregou", medido no payload e não inferido do código.
4. `tree_acao` (`ast.parse` + `ast.walk`) lista `Subscript`/`Call(func=.get)`/`Compare` — em
   `code_action` **e** `observations` (o trace concatena os dois em `txt_etap_memo`; a filtragem
   cru observa o atributo `observations` não-nulo — §1.10). Aninhamento `.get` resolvido como
   uma cadeia: a primeira chave real decide; a de fallback **não conta como leitura independente**.
5. Comparações de grafia: só contam quando o objeto comparado **deriva da variável que recebeu o
   retorno de `validar_quebra_sigilo`** (`deriva_do_retorno`) — a correção de escopo da retratação-2.
   "Avaliada" = não está na mesma linha da falha (`linha_da_falha` via `observations`).
6. Integridade dos trechos: o `texto` de cada `trechos_do_cru` deve ser igual (ou fatia/derivação
   documentada) do nó `cru` apontado; `n_chaves`/`n_itens` dos objetos grandes conferem com o cru.

## Resultado por componente

### 1. Universo e o 9/21 — CONFIRMADO

Recontagem independente no CSV bruto:

| medida | publicado | recomputado |
|--------|-----------|-------------|
| papéis que declaram `validar_quebra_sigilo` | 26 | **26** |
| execuções que chamam a ferramenta | 21 | **21** (5 declaram e nunca chamam) |
| execuções com `request.quebra_sigilo` presente | 21 | **21** |
| entregas fora de SIM/NAO | **9 (43%)** | **9 (43%)** — idênticas |
| └ objeto inteiro (`justificativa`,`vazamento_sigilo`) | 7 | 7 |
| └ texto livre (203 caracteres) | 1 | 1 (`783ff70b…`) |
| └ string vazia | 1 | 1 (`dbc472b0…`) |
| meses dos 9 | dez/25, mai/26, jun/26 | **2025-12, 2026-05, 2026-06** ✓ |
| conformes | 12 (11 NAO + 1 SIM) em 4 meses | **12 (11 NAO + 1 SIM)** ✓ |

A tabela publicada `quebra_sigilo_por_papel.csv` confere **linha a linha** com a recomputação
(chave lida, classe de leitura, valor entregue, mês).

### 2. Retratação-1 — CONFIRMADA

`8dd410c8…` entrega `'NAO'` (correto) — verificado em `crus/8dd410c8-….json` →
`action_output.request.quebra_sigilo` = `'NAO'`. O step idx4 contém a cadeia
`.get('vazamento_sigilo', new_quebra.get('quebra_sigilo'))` — a chave real `vazamento_sigilo`
existe e decide; a de fallback nunca é consultada. A leitura inicial por código (que contou a
chave de fallback como a leitura) estava errada; a correção por medição do payload está certa.

### 3. Retratação-2 — CONFIRMADA

Em `8dd410c8…` idx4 há **2 comparações espúrias** que o detector antigo teria contado: a variável
comparada é `validade_info`/`new_validade` — retorno de `validar_resposta_bacen` (outra ferramenta),
campo `validade_resposta`. O filtro `deriva_do_retorno` as exclui corretamente (recomputado:
`deriva_do_retorno=False` nas duas). O detalhe qualitativo é ainda mais específico que a narrativa
de §1.10: as comparações não são só "fora do escopo" — são sobre um campo-irmão no mesmo dict final.

### 4. Tabela de grafia — CONFIRMADA com nota de precisão

`grafia.csv` tem **5 comparações em 2 execuções** (`21a4fa6c…` e `50d6c3bd…`) — a recomputação
reproduz exatamente: 2 na mesma linha da falha (`execução:mesma linha da falha`) e 3 em
`21a4fa6c…` idx3 marcadas `avaliada`. Verificação direta do cru mostra que as 3 são um único
`quebra in ["NÃO","NAO","Não","Nao"]` defensivo no step de recuperação — avaliado, mas inócuo
porque todos os literais divergentes já estão cobertos pela lista.

> **Nota de precisão**: o texto de `07 §6.2` diz "duas comparações divergentes — a saber, o
> 'Não' com acento e o 'Nao' capitalizado — a comparação nunca foi avaliada". A saída formal é
> mais rica: 2 não avaliadas **+ 3 avaliadas defensivas**. A conclusão de risco ("corrigir só a
> chave liga o erro de acento") continua valendo — mas a narrativa publicada omite que metade do
> universo de comparações divergentes já é avaliada num guard-rail defensivo.

### 5. Integridade dos trechos — CONFIRMADA

**122/122** `trechos_do_cru` conferem com o nó `cru` apontado (string exata, fatia documentada
ou derivação `mensagens`). Nenhum trecho divergente, nenhum caminho quebrado.

### 6. Distribuição temporal — CONFIRMADA

Meses dos 9 não conformes: dez/2025, mai/2026, jun/2026 — não é incidente isolado, atravessa
3 janelas do trace. Os 12 conformes cobrem dez/2025–jun/2026 (4 meses). A janela jan–abr/2026
tem 7 entregas conformes (todas `NAO`) — o que sustenta a leitura "3 meses distintos" sem
sugerir concentração.

## Ressalva registrada — "sem nenhuma exceção registrada em nenhuma delas"

Recomputação sobre `observations` de todos os steps das 9 execuções:

| execução | erros `Exception` na trajetória | o erro toca o campo `quebra_sigilo`? |
|----------|-------------------------------|--------------------------------------|
| `95344639…` | **3** (idx2 AttributeError; idx4 KeyError `"['resposta_ia1']"`) | **não** — falham em outros campos/mecanismos do mesmo dict final |
| `dbc472b0…` | **3** (idx5 TypeError `PydanticCustomError`; idx6 AttributeError; idx7 KeyError `"['resposta_bacen']"`) | **não** — o campo errado é entregue mesmo assim |
| as outras 7 | 0 | — |

A frase publicada é literalmente falsa para 2/9. A **afirmação substantiva** que a análise quer
fazer — "o campo errado é entregue sem que nenhum erro o registre" — continua correta: em
`95344639` os 3 erros são de outros mecanismos (o idx4 quebra num campo-irmão do mesmo dict, não
em `quebra_sigilo`); em `dbc472b0` a leitura silenciosa `quebra.get('quebra_sigilo', '')` não
levanta exceção (verificado no cru: idx7, `quebra_saida = quebra.get("quebra_sigilo", "")` →
entrega `""`). Mas a redação "nenhuma exceção em nenhuma" deve ser corrigida para algo como
"nenhum erro registra o mecanismo `quebra_sigilo` — as exceções existentes em 2/9 execuções
falham em outros campos/mecanismos do mesmo dict final". O campo `impact` de `unidades_memoria.json`
carrega a mesma imprecisão ("sem exceção registrada" — incorreto como afirmação categórica).

## Conclusões finais

1. **9/21 (43%) não conformes — CONFIRMADO** por recontagem independente, com decomposição
   idêntica (7 objeto, 1 texto livre, 1 vazio) e meses idênticos.
2. **As duas retratações estão corretas** — a correção de escopo (`deriva_do_retorno`) e a
   resolução de cadeia `.get` aninhada são as decisões certas e o `8dd410c8…` de fato entrega
   `'NAO'`.
3. **122/122 trechos conferem** — integridade evidência↔cru total.
4. **Duas correções redacionais pendentes**: (a) "sem nenhuma exceção registrada em nenhuma
   delas" — falso literalmente para 2/9, embora a tese de silêncio do mecanismo se mantenha;
   (b) a narrativa "2 comparações nunca avaliadas" omite 3 avaliadas-defensivas — a saída formal
   (`grafia.csv`) é mais completa que o texto de `07 §6.2`. Nenhuma altera o `VALIDADO` nem o
   `harness`, mas ambas devem ser corrigidas no próximo rerun.

## Referências

- `resultados/evidencia/11.9_leituras_quebra_sigilo/` — crus, derivados, `quebra_sigilo_por_papel.csv`, `grafia.csv`
- `unidades_memoria.json` → `n9` → `validation.analise_funda` (o resultado auditado)
- `docs/03-procedimento-validacao.md` §1.10 (as duas retratações)
- `docs/07-relatorio-mineracao-unidades-n2-n10.md` §6.2 (a narrativa auditada)
- Notebook §11.9 (a célula que materializou a evidência)
- `audit/scripts/audit_recompute7.py` — script desta recomputação independente
