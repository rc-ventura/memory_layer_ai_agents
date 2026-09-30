# Agents — operando no pipeline desta base

Guia operacional para qualquer agente CLI trabalhando nesta pasta (`pipeline/` de uma base de trace).
O procedimento de investigação detalhado (receitas, pontos de parada) está na skill
`.claude/skills/investiga-trace/SKILL.md` do repo; o método e o porquê estão nos docs canônicos.

## Fronteira

1. **Read-only por padrão.** `drill_down.py` e `checklist.py` apenas leem. Nunca rodar os notebooks
   (reescrevem `resultados/`), nunca editar `base_pipeline.py`/`drill_down.py`/`genealogia_sankey.py`
   sem pedido explícito do Rafael e aprovação do diff — as regras são hipóteses validadas por base;
   mudá-las tem ciclo próprio (`analysis/pipeline-entre-bases.md` §2).
2. **PII.** A saída dos comandos reproduz nomes de clientes e números de processo em claro:
   nunca commitar, nunca salvar fora de `resultados/` (git-ignored), nunca colocar conteúdo do cru
   em prompt de LLM externo sem autorização explícita. Na máquina de compliance, nada sai da máquina.
3. **O cru é a fonte.** Nenhum número apresentado sem apontar o caso concreto (`exec_id`/`role`/`idx`)
   que o sustenta — eixo central do `docs/03-procedimento-validacao.md`.

## Pré-condições

- Comandos rodam **deste diretório**: `python drill_down.py <cmd>`.
- `padrao`, `residuo`, `tempo`, `protocolo`, `mecanismo` leem `resultados/erros_mecanismo.csv`
  (gerado pelo notebook — se faltar, avisar; não rodar o notebook sozinho).
- Base nova: `python checklist.py` primeiro (intake), ver `analysis/README.md`.

## Catálogo rápido

| Comando | Uso |
|---|---|
| `tutorial` | referência guiada completa |
| `amostra [n]` | execuções quaisquer |
| `listar "<assinatura>"` | casos por sintoma |
| `mecanismo "<nome>"` | casos por mecanismo |
| `planos [n]` | execuções com PlanningStep |
| `ferramenta <nome>` | declaração da tool no system prompt |
| `caso <exec_id> <role> [--json]` | trajetória do papel no cru |
| `padrao ["<trecho>"]` | padrões do resíduo e seus casos |
| `residuo` / `tempo` / `protocolo` / `relogios` | evidências estruturais específicas |
| `evidencia ...` | pastas de evidência (escreve em git-ignored) |

Companheiros: `checklist.py` (intake/overlap), `genealogia_sankey.py` (figura; regenerar só após
mudança aprovada nas regras).

## Docs canônicos (não duplicar o que já está lá)

- Procedimento pós-triagem (Frente 3): `docs/03-procedimento-validacao.md`
- Método e cadeia erro→memória: `docs/01-racionais.md` §7, `docs/09-metodologia-erro-a-memoria.md`
- Ajustes entre bases: `analysis/pipeline-entre-bases.md`
- Intake de base nova e regras de PII: `analysis/README.md`
