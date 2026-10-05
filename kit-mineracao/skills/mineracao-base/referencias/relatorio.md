# Relatório de uma rodada de mineração — esqueleto

Toda rodada termina num relatório em `pipeline/resultados/relatorio_<mineracao>_<BASE_ID>_<AAAA-MM-DD>.md`. A pasta é
git-ignored.

**Toda afirmação leva a evidência dela** ([`evidencia.md`](evidencia.md)): o comando que reproduz o número, a tabela
derivada com o filtro e, nos achados que viram decisão ou parada, os casos crus (`exec_id`, a pasta `crus/` e o
recorte). Os blocos de evidência vêm do `montar_evidencia.py`, colados com `cat`, nunca digitados.

O relatório completo fica no ambiente. A versão que sai é feita pelo `versao_para_sair.py` e passa no
`varrer_pii.py`.

O relatório descreve **esta base**. Ele não compara com relatório publicado nem com outra base. A verificação vem de
duas fontes: o encontro das duas implementações (as tabelas da mineração × a auditoria independente) e as
conferências internas.

Marque cada número com a origem:
- **[conferido]**: saiu de forma determinística, de tabela, contagem, regex ou script;
- **[assistido]**: saiu de leitura de caso com ajuda do LLM. Vale como hipótese.

```markdown
# Relatório — <mineração> · <BASE_ID> · <AAAA-MM-DD>

## 0 · Identificação
- kit de mineração: versão <VERSAO>
- pasta da análise: <nome da pasta datada> · base: <BASE_ID>
- trace: <formato do §0 do checklist: csv | xz | gz | parquet> · <linhas> linhas · <memórias que parseiam> com memória
- versão do código (`conferir_versao.py`): IGUAL ao manifesto | <n> arquivo(s) fora — parou aqui
- intake (`checklist.py`): passou | parou (motivo, sem dado de caso)

## 1 · Entradas
| Tabela | Gerada por | Gerada nesta rodada? |
|---|---|---|
| … | … | sim / não (já existia, mais nova que o trace e o código) |

## 2 · Achados, passo a passo  [conferido]
### Passo <n> · <nome do passo do procedimento>
- <o que a tabela mostra, em contagens e proporções>
- **Reproduzir:** `<comando com os parâmetros>` (de dentro de `pipeline/`) · **Derivada:** `<tabela>`, `<filtro>` →
  <n> linhas · <ou a seção do notebook>

<o bloco do montar_evidencia.py, quando o achado vira decisão ou parada — `cat …/bloco.md >> relatório`>

## 3 · Verificação
- **auditoria × tabelas** (`comparar_auditoria.py`): tudo igual | <n> divergência(s)
  - <cada linha DIVERGE: medida, tabelas, auditoria>
  - **Reproduzir:** `<o comando do auditor, com --json>` e `<o comando do comparar_auditoria.py>` · **Derivada:**
    `<o JSON do auditor>`
- **conferências internas:** <cada uma, OK | FALHA>

## 4 · Paradas — o que precisa de leitura de caso (para a investigação)
| Parada | Pergunta do roteiro | O que a motiva (contagens) | Evidência (a pasta montada) |
|---|---|---|---|
| … | S1 / S2 / S3 … | … | `resultados/evidencia/<nome>/` |

## 5 · Comandos que falharam
- <comando>: <última linha do erro, sem dado de caso>

## 6 · Sigilo
- versão que sai: `<relatório>_saida.md` (`versao_para_sair.py`, <n> identificadores → caso-N) · `varrer_pii.py`: limpo
```
