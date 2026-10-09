---
type: tooling-workflow
title: "Kit de Mineração de Traces (skills, agentes e scripts)"
description: O pacote versionado em .claude/ que roda uma rodada de mineração do trace igual em qualquer ambiente e base — preparação comum, mineração determinística com auditoria independente em paralelo, encontro por script, relatório com evidência por afirmação, investigação assistida até o dossiê de decisão.
tags: [mining-kit, claude-skills, deterministic-pipeline, independent-audit, evidence-discipline, pii-secrecy]
verified:
  - by: openwiki/0.6.0
    at: 2026-10-09T17:09:54.387Z
sources:
  - id: openwiki-source-4c0def1f2b951f491e33a3e9
    resource: repo://.claude/agents/auditor-independente.md
  - id: openwiki-source-ece2d48f7732dc7f7e397d5a
    resource: repo://.claude/agents/validador-de-notebook.md
  - id: openwiki-source-0f078484b791a8e13e468c94
    resource: repo://.claude/skills/mineracao-base/manifesto.json
  - id: openwiki-source-bdcfe063182a99198f34a102
    resource: repo://.claude/skills/mineracao-base/referencias/kit.md
  - id: openwiki-source-849c31889570728b74f0720c
    resource: repo://.claude/skills/mineracao-base/SKILL.md
  - id: openwiki-source-97af608bd2887674b819dc83
    resource: repo://.claude/skills/propor-notebook/SKILL.md
  - id: openwiki-source-eb3a346108886797f62f7271
    resource: repo://analysis/registros/README.md
  - id: openwiki-source-7c2d1833faef47d99e8e11da
    resource: repo://analysis/roadmap-transversal.md
generated: { by: "claude-code", at: "2026-10-09T17:09:54.387Z" }
---

O kit de mineração é um pacote de **skills, agentes e scripts que vive no próprio `.claude/` do repositório, versionado** — sem nada a instalar: o Claude Code e o GitHub Copilot (documentação de 2026: lê `.claude/skills/` e `.claude/agents/` direto) enxergam o mesmo lugar, e não há cópia para `.github/` porque a cópia viraria uma segunda versão que envelhece. Ele existe para que uma **rodada de mineração** rode com o mesmo procedimento em qualquer ambiente (esta máquina, a máquina de compliance) e em qualquer base. O documento de desenho é `.claude/skills/mineracao-base/referencias/kit.md`; uma rodada real de exemplo, passo a passo, está em `referencias/exemplo.md`.

A separação fundamental do kit: **o método mora na análise, não no kit.** Os passos de cada mineração estão nos `docs/*procedimento*` da pasta datada; a skill correspondente só diz como rodar, o que conferir e onde parar. O kit não tem nome de base, unidade, ferramenta nem número de nenhuma base — a conferência disso é um `grep` documentado no próprio kit.

## As três camadas de uma rodada

```
preparação ──┬──► mineração (lê as tabelas da base) ──┐
             │                                         ├─► encontro (script) ──► relatório ──► investigação ──► dossiê
             └──► auditor independente (em paralelo:   │    tabelas × auditoria    (achados,      → o pesquisador decide
                  recalcula do trace, grava JSON) ─────┘                           paradas)
```

- **Mineração (determinística):** a skill de cada mineração lê as tabelas que o pipeline produziu para a base, passo a passo do procedimento da análise, e descreve o que elas mostram. Não compara com relatório publicado nem com outra base — **os números são o resultado**, e o que garante que estão certos é a segunda implementação e as conferências internas.
- **Verificação em paralelo:** o agente `auditor-independente` roda uma segunda implementação (`audit/scripts/audit_recompute<N>.py --base <BASE_ID> --trace <TRACE> --json <arquivo>`) que recalcula as medidas direto do trace, sem ler o pipeline nem o que a mineração achou. Um script de **encontro** (`comparar_auditoria.py` de cada skill) confronta as medidas dele com as tabelas.
- **Investigação:** a skill `mineracao-investigacao` pega as **paradas** (os pontos do relatório que as regras não fecham). Quem escolhe os casos é regra fixa (`amostrar.py`); o `investigador` lê; o `segundo-leitor` relê às cegas e a concordância é medida por `concordancia.py` (na candidata, a leitura é em duas etapas: frase livre → categorias da lista aprovada); a hipótese vira regra contada na população inteira por `testar_regra.py`. **O LLM propõe, o script conta** — nenhum número sai da leitura do modelo, que entra como `[assistido]` (hipótese).
- **Decisão:** sempre do pesquisador. Uma regra que mudaria número publicado é um *Ajuste* — e o kit para ali. Na candidata, o painel (`valor_da_licao.py`) marca as situações que param no gate do pesquisador, e a decisão fica registrada (`registrar_decisao.py`).

## O passo 0 — `mineracao-base`

A skill `mineracao-base` são as pré-condições comuns de **toda** mineração; as skills específicas (`mineracao-silenciosas`, `mineracao-protocolo`, `mineracao-candidata`) começam por ela:

1. **Localizar a análise** — a pasta datada com `pipeline/`, `docs/` e `audit/` (sem `pipeline/base_pipeline.py`, parar e perguntar);
2. **Ler a base e o trace** — `BASE_ID` e formato do `TRACE`, pelo `leitor_trace.py` (o nome do arquivo do trace tem formato de identificador e não entra no relatório);
3. **Conferir a versão do código** — `conferir_versao.py` compara o código da análise com o `manifesto.json` do kit (hashes por arquivo: pipeline, notebooks, leitor compartilhado, audit_recompute*); a camada da base (`TRACE`, `BASE_ID`), o fim de linha e saídas de notebook não contam. Divergiu → **para** e lista DIFERE/FALTA: duas bases só se comparam mineradas pelo mesmo código;
4. **Intake** — `checklist.py` da pasta (formato, schema, saúde do JSON, censo de `error.type`, contexto);
5. **Monitoramento** — `monitorar.py` confere nesta base cada lição/sinal que o pesquisador decidiu monitorar (`analysis/registros/monitoramento.json`, um só para todas as bases): **é a única comparação com outra base que o kit faz**, de propósito. Saiu com alerta → as lições voltam ao gate do pesquisador antes de minerar.

## Regras que valem em toda rodada

- **Nenhuma afirmação sem evidência:** cada número do relatório leva o comando que o reproduz e a tabela de onde sai; achados que viram decisão ou parada levam também os casos crus (`exec_id`, a pasta `crus/`, o recorte `drill_down.py caso`). O `montar_evidencia.py` monta os casos por regra fixa e escreve o bloco do relatório.
- **Nenhum LLM no caminho da classificação** — família, assinatura, mecanismo e unidade vêm das regras determinísticas do pipeline.
- **Não conserta:** divergência mineração × auditoria é registrada com os dois valores e para — a divergência é o achado. Regra nova é proposta, nunca edição.
- **Não edita o repositório:** arquivos novos só em `pipeline/resultados/` (git-ignored); sem commit, sem push.
- **Sigilo:** para fora do ambiente só vão contagens, nomes de papel/ferramenta/unidade, meses, sim/não e categorias fechadas. A versão do relatório que sai troca os identificadores por `caso-N` (`versao_para_sair.py` — o mapa fica no ambiente) e o `varrer_pii.py` bloqueia a saída se achar processo, CPF, CNPJ, e-mail ou identificador de execução.

O relatório fica em `pipeline/resultados/relatorio_<mineração>_<BASE_ID>_<AAAA-MM-DD>.md`, no esqueleto de `referencias/relatorio.md` — quem o lê não precisa buscar evidência depois.

## O que mora onde

| Camada | Onde | O que é |
|---|---|---|
| **Método** | o kit + os docs de procedimento da análise | os passos, as conferências, o sigilo, o dossiê — o kit aponta para o procedimento, não o copia |
| **Base** | a pasta da análise | `TRACE`, `BASE_ID`, `DESTINO_MINERACAO`, as tabelas que o pipeline produziu |
| **Objeto da rodada** | o argumento da chamada | a pasta da análise, a pergunta do roteiro (`silenciosas S2`) |

## Inventário

| Peça | Papel |
|---|---|
| `skills/mineracao-base` | passo 0 comum (pasta, base, versão, intake, monitoramento, sigilo, esqueleto do relatório) + `VERSAO` + `manifesto.json` |
| `skills/mineracao-silenciosas` | a mineração do balde invisível (ferramenta falhou sem exceção) + `comparar_auditoria.py` × `audit_recompute9` |
| `skills/mineracao-protocolo` | a mineração da família "protocolo do harness" (resposta sem bloco `<code>`) + `comparar_auditoria.py` × `audit_recompute10` e `cobertura.py` |
| `skills/mineracao-candidata` | minera uma `U_...` (parte genérica → funil → parte específica → arquivo final validado contra `analysis/registros/esquema-memoria.json`) + `validar_memoria.py`, `valor_da_licao.py`, `registrar_decisao.py` |
| `skills/mineracao-investigacao` | a investigação depois do determinístico: roteiros (`silenciosas`, `protocolo`, `candidata`), `testar_regra.py`, `concordancia.py` |
| `skills/investigar`, `skills/propor-notebook` | os passos de depois, skills **só de chamada manual** (`disable-model-invocation: true`) — a segunda propõe notebook específico só quando a lição cumpre a regra de criação (frequência + confiança + gate registrado) |
| `agents/auditor-independente` | roda em paralelo o `audit_recompute*` da pasta e grava as medidas em JSON; nunca lê o pipeline, nunca conserta |
| `agents/investigador` | primeiro leitor da amostra feita por regra fixa; propõe a regra determinística; devolve contagens, nunca texto de caso |
| `agents/segundo-leitor` | relê os mesmos casos às cegas, para medir concordância |
| `agents/validador-de-notebook` | valida a proposta de notebook específico com segunda implementação escrita só do racional, antes da aprovação do pesquisador |

## Versão e limites desta versão

A versão do kit é o arquivo `VERSAO` da skill `mineracao-base`; o `manifesto.json` guarda os hashes do código para o qual essa versão foi escrita. Quando o pipeline muda de propósito (um Ajuste aprovado), o manifesto é regenerado com `conferir_versao.py <pasta> --gerar` e a versão sobe.

Limites declarados: a leitura do `investigador` ainda não rodou ao vivo (a ponte foi validada reproduzindo uma classificação determinística conhecida); a auditoria em paralelo existe hoje só para falhas silenciosas e protocolo (`audit_recompute9` e `10`, com `--json`) — cada mineração nova do backlog (resíduo, erro crítico — itens `transversal #8` e `#9`) precisa antes de uma auditoria com `--json` e um script de encontro; e a leitura do `.claude/` pelo Copilot depende da versão do VS Code.

## Como se conecta ao resto do projeto

- O que o kit minera é o pipeline descrito em [Metodologia de Taxonomia de Erros](metodologia-de-taxonomia-de-erros.md) e [Metodologia de Análise de Traces](metodologia-de-analise-de-traces.md).
- As bases em que as rodadas rodam e o livro-razão dos Ajustes: [Análises Multi-Base](analises-multi-base.md).
- Os registros que o kit lê (`monitoramento.json`, `esquema-memoria.json`) e os roadmaps onde ficam os itens de backlog do kit (`transversal #8–#10`): [Governança das Análises](../referencia/governanca-das-analises.md).
