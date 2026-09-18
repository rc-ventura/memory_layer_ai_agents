# Relatório independente — 11.8_registro_final

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.8_registro_final/` por leitura direta dos arquivos `crus/*.json`, usando `casos.csv` e `derivados/unidades_memoria.json` como artefatos de referência. O objetivo é verificar se os **casos citados no campo `evidence` do registro final** de cada candidata realmente:

1. correspondem aos primeiros casos listados em `location`;
2. aparecem em `casos.csv` conforme a regra de escolha da pasta;
3. e seguem o padrão estrutural que o registro final resume.

Guidance consultado para interpretar a análise:

- `docs/01-racionais.md` §8 – `06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.9;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Resumo executivo

1. A pasta contém **6 casos**, exatamente **3 por candidata**: os três primeiros meses listados no `location` de cada registro final.
2. Em ambos os registros de `unidades_memoria.json`, os itens de `evidence` são **idênticos** aos **3 primeiros casos de `location.casos`**.
3. Os 6 casos de `evidence` também aparecem integralmente em `casos.csv`, com o mesmo `exec_id`, `role`, `idx`, `mes`, `pedido` e `forma` esperados.
4. A leitura do cru confirma que esses 6 casos são representativos do que o registro final descreve:
   - na nº2, o agente pede `0` sobre um retorno cujo topo é `result`;
   - na nº10, o agente pede `quebra_sigilo` sobre um retorno cujo topo é `justificativa` / `vazamento_sigilo`.
5. Assim, a pasta `11.8_registro_final/` sustenta bem a parte observável do registro final: **seleção das evidências**, **alinhamento com `location`** e **compatibilidade das descrições com os casos citados**.

## Corpus auditado

| exec_id | role | idx | unidade | ferramenta | motivo |
|---|---|---:|---|---|---|
| `1eed2931…` | ConversationAgent | 1 | `U_contrato_dict` | `get_available_documents` | citado em `evidence` do registro final |
| `0cd5e2c0…` | ConversationAgent | 1 | `U_contrato_dict` | `get_available_documents` | citado em `evidence` do registro final |
| `0572af0b…` | ConversationAgent | 1 | `U_contrato_dict` | `get_available_documents` | citado em `evidence` do registro final |
| `d3d64194…` | RespostaBacen | 1 | `U_campo_inexistente` | `validar_quebra_sigilo` | citado em `evidence` do registro final |
| `1be966e7…` | RespostaBacen | 6 | `U_campo_inexistente` | `validar_quebra_sigilo` | citado em `evidence` do registro final |
| `21a4fa6c…` | RespostaBacen | 2 | `U_campo_inexistente` | `validar_quebra_sigilo` | citado em `evidence` do registro final |

## Método

A checagem independente fez três confrontos:

1. **`casos.csv` × `unidades_memoria.json`**: verificar se cada linha da pasta corresponde a um item efetivamente citado em `evidence`.
2. **`location` × `evidence`**: verificar se o `evidence` de cada registro é formado exatamente pelos 3 primeiros casos de `location.casos`, conforme a regra descrita nos racionais.
3. **`casos.csv` × cru**: abrir cada `ActionStep` alvo para confirmar que o `pedido` e a `forma` resumidos no registro final batem com o erro real observado.

## Resultado por registro

### Registro 1 — nº2 / `get_available_documents`

- `location.total_erros = 91`;
- `location.casos` alterna os meses com erro;
- os 3 primeiros casos em `location.casos` são:
  - `1eed2931…` / `2025-12`;
  - `0cd5e2c0…` / `2026-04`;
  - `0572af0b…` / `2026-05`.

Esses mesmos três aparecem em `evidence`, na mesma ordem, e são exatamente os três casos de `get_available_documents` presentes em `11.8_registro_final/casos.csv`.

No cru, os três confirmam o mesmo padrão resumido no registro final:

- o agente indexa o retorno como se fosse lista (`[0]`);
- a mensagem mostra objeto com topo `{'result': ...}`;
- a `forma_do_objeto_indexado` registrada em `evidence` é compatível com o erro real.

### Registro 2 — nº10 / `validar_quebra_sigilo`

- `location.total_erros = 7`;
- os 3 primeiros casos em `location.casos` são:
  - `d3d64194…` / `2026-04`;
  - `1be966e7…` / `2026-05`;
  - `21a4fa6c…` / `2026-06`.

Esses mesmos três aparecem em `evidence`, na mesma ordem, e são exatamente os três casos de `validar_quebra_sigilo` presentes em `11.8_registro_final/casos.csv`.

No cru, os três confirmam o padrão resumido no registro final:

- o agente pede a chave `quebra_sigilo`;
- a mensagem mostra retorno com topo `{'vazamento_sigilo': ..., 'justificativa': ...}`;
- a `forma_do_objeto_indexado` registrada em `evidence` é compatível com o erro real.

## Achados principais

### 1. `evidence` é realmente derivado dos primeiros casos de `location`

A comparação automática e a leitura dos arquivos mostram que, para as duas candidatas, vale exatamente a regra descrita nos racionais:

- `evidence = primeiros 3 casos de location`;
- um caso por mês nos três primeiros meses com erro;
- sem casos “escolhidos a dedo” fora do que o registro lista.

### 2. Os 6 casos escolhidos são representativos do padrão que o registro final narra

A leitura do cru confirma que o `evidence` não é meramente um ponteiro arbitrário. Os seis casos de fato exibem:

- na nº2, retorno de `get_available_documents` como dict com `result`, embora o agente o indexe por posição;
- na nº10, retorno de `validar_quebra_sigilo` com `vazamento_sigilo` / `justificativa`, embora o agente peça `quebra_sigilo`.

Ou seja, o texto de `description` e `correction_guidance` do registro final está ancorado em exemplos que realmente exibem o mecanismo descrito.

### 3. A pasta sustenta o recorte observável do registro final, não a decisão conceitual inteira

A auditoria independente desta pasta valida bem:

- a escolha dos casos citados em `evidence`;
- a consistência entre `location`, `evidence` e `casos.csv`;
- o alinhamento estrutural entre o registro final e os erros reais do cru.

Ela não resolve, por si só, questões conceituais maiores já deixadas em aberto pelos docs — por exemplo, o `destino` da nº10 (`memória × harness`). Mas o que a pasta promete sustentar, ela sustenta.

## Conclusões finais

1. A pasta `11.8_registro_final/` é consistente com a regra declarada de seleção das evidências: os 6 casos são exatamente os 3 primeiros `location` de cada uma das 2 candidatas.
2. Os 6 casos presentes em `casos.csv` batem com os itens de `evidence` em `unidades_memoria.json`.
3. A leitura do cru confirma que esses casos mostram o mesmo mecanismo descrito nos registros finais.
4. Portanto, a parte auditável do Passo 8 — `location`, `evidence` e ancoragem dos registros em casos reais — ficou **validada** nesta auditoria independente.
