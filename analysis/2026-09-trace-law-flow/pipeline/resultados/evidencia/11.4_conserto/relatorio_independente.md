# Relatório independente — 11.4_conserto

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.4_conserto/` por leitura direta dos arquivos `crus/*.json`, usando `casos.csv` apenas como índice da amostra. O objetivo é verificar se o **desfecho de correção** atribuído no notebook realmente corresponde ao que o agente faz no **step seguinte ao erro**.

Guidance consultado para interpretar a análise:

- `docs/`06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.8 e §1.9;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Resumo executivo

1. A pasta contém **5 casos**, escolhidos como o primeiro caso, por ferramenta, de cada desfecho de correção observado.
2. Em **4/5** casos, o step seguinte corrige o acesso problemático e segue sem erro.
3. No caso restante (`95344639…` / `extrair_evidencias`), o step seguinte **corrige o erro original**, mas depois quebra por **outro motivo**, já em ferramenta posterior.
4. A tipologia do notebook se sustenta no cru: aparecem exatamente os três desfechos esperados nesta pasta — **troca sem guarda**, **troca com guarda de tipo** e **conserto com `.get`**.
5. Não encontrei caso nesta pasta em que o “conserto” publicado não apareça de fato no código do step seguinte.

## Corpus auditado

| exec_id | ferramenta | pedido | desfecho de correção no notebook |
|---|---|---|---|
| `1eed2931…` | `get_available_documents` | `0` | troca sem guarda |
| `c67b0502…` | `get_available_documents` | `0` | troca com guarda de tipo |
| `d3d64194…` | `validar_quebra_sigilo` | `quebra_sigilo` | troca sem guarda |
| `21a4fa6c…` | `validar_quebra_sigilo` | `quebra_sigilo` | conserto com `.get` |
| `95344639…` | `extrair_evidencias` | `informacoes_evidencias` | troca sem guarda |

## Método

Para cada caso, a auditoria independente abriu:

- o `ActionStep` alvo (`idx` do `casos.csv`), onde ocorre o erro;
- o `ActionStep` seguinte (`idx + 1`), onde o notebook afirma haver conserto.

A leitura verificou:

- qual chave/índice falhou no step do erro;
- qual acesso o agente escreveu no step seguinte;
- se o step seguinte elimina o problema anterior;
- e, quando o step seguinte ainda falha, se a nova falha é do mesmo mecanismo ou de outro.

## Resultado por caso

| exec_id | leitura do step do erro | leitura do step seguinte | veredito independente |
|---|---|---|---|
| `1eed2931…` | o agente tenta `for doc in documentos[0]`; a mensagem mostra `Could not index {'result': ...} with '0'` | o step seguinte troca para `for doc in documentos['result'][0]` e roda sem erro | **confere: troca sem guarda** |
| `c67b0502…` | o agente faz `all_docs_... = docs_info_...[0]` e erra no índice `0` sobre objeto com `result` | o step seguinte usa `docs_info_...['result'][0] if isinstance(..., dict) else docs_info_...[0]`; preserva ramo compatível com outro contrato | **confere: troca com guarda de tipo** |
| `d3d64194…` | o JSON final lê `quebra["quebra_sigilo"]`, mas o runtime mostrou `{'vazamento_sigilo', 'justificativa'}` | o step seguinte troca para `quebra["vazamento_sigilo"]` e fecha sem erro | **confere: troca sem guarda** |
| `21a4fa6c…` | o erro acontece já em `if validacao_sigilo["quebra_sigilo"] == "NÃO":` | o step seguinte cria `quebra = validacao_sigilo.get("quebra_sigilo", validacao_sigilo.get("vazamento_sigilo"))` e ainda normaliza as grafias de `NÃO/NAO` | **confere: conserto com `.get`** |
| `95344639…` | `draft_resposta(..., informacoes_evidencias=info_evidencias["informacoes_evidencias"])` falha porque o retorno real traz `dados_evidencias` | o step seguinte corrige para `info_evidencias["dados_evidencias"]`; depois o mesmo step quebra adiante por outro motivo (`resposta` textual/indexada como dict) | **confere: troca sem guarda do erro original, com nova falha posterior** |

## Achados principais

### 1. O step seguinte realmente contém o conserto anunciado

Nos cinco casos, o notebook não está “inferindo demais”: o conserto aparece explicitamente no código do step seguinte.

Os padrões observados são:

- **troca sem guarda**: substituir diretamente a chave/índice problemático pela chave real;
- **troca com guarda de tipo**: aceitar o contrato real, mas manter o acesso antigo num ramo condicional;
- **conserto com `.get`**: ler primeiro a chave declarada e, na falta dela, cair na chave real.

### 2. `validar_quebra_sigilo` mostra duas formas de correção robustamente distintas

Esta pasta confirma que a ferramenta `validar_quebra_sigilo` aparece com dois estilos de correção:

- troca direta para `vazamento_sigilo` (`d3d64194…`);
- compatibilização dos dois contratos com `.get(...)` e tolerância para `NÃO/NAO` (`21a4fa6c…`).

Isso bate com a leitura do procedimento de validação: o agente primeiro erra seguindo o contrato declarado e depois adapta o acesso ao contrato real observado no runtime.

### 3. O caso `95344639…` não contradiz o 11.4

O caso de `extrair_evidencias` é importante porque o step seguinte não fica “limpo”, mas isso **não invalida** o desfecho de correção registrado.

A sequência no cru é:

1. erro original: chave `informacoes_evidencias` ausente;
2. conserto no step seguinte: uso de `dados_evidencias`;
3. nova falha posterior, em outra parte do pipeline, ao tratar um texto de erro como se fosse dict.

Portanto, a classificação correta aqui é “o agente corrigiu **aquele** erro”, não “o step seguinte terminou a tarefa inteira com sucesso”.

## Conclusões finais

1. A pasta `11.4_conserto/` sustenta bem a leitura de que o Passo 3 identifica corretamente o **tipo de correção** escrito pelo agente no step seguinte.
2. Os três desfechos presentes em `casos.csv` apareceram de fato no cru, sem contradições.
3. O balanço independente desta pasta é:
   - **4/5 consertos seguidos de step sem erro**;
   - **1/5 conserto correto do erro original, com falha nova e distinta no restante do step**.
4. Não encontrei evidência, nesta pasta, de superinterpretação do notebook sobre o que o agente fez depois do erro.
