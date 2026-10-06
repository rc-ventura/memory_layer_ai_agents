# Kit de mineração do trace

> **Primeira vez?** Leia o [`exemplo.md`](exemplo.md): uma rodada real, do zero, numa base nova simulada, passo a passo.
>
> **Onde o kit mora:** no próprio `.claude/` do repositório, versionado — as skills em `.claude/skills/mineracao-*/`,
> os agentes em `.claude/agents/`, os prompts em `.claude/commands/`. Este documento e a `VERSAO` ficam na skill
> `mineracao-base`. O Copilot usa cópias geradas (abaixo).

Um pacote de skills, agentes, prompts e scripts para rodar as minerações do trace de agentes com o mesmo procedimento
em qualquer ambiente e em qualquer base. Ele funciona com qualquer agente que leia o formato aberto de skill
(`SKILL.md`), como o Claude Code e o GitHub Copilot.

## As três camadas de uma rodada

```
preparação ──┬──► mineração (lê as tabelas da base) ──┐
             │                                         ├─► encontro (script) ──► relatório ──► investigação ──► dossiê ──► o pesquisador decide
             └──► auditor independente (em paralelo:   │    tabelas × auditoria    (achados,      (o LLM lê uma    (hipóteses,
                  recalcula do trace, grava JSON) ─────┘                           paradas)        amostra por      leitura, regra
                                                                                                   regra fixa)      contada)
```

- **Mineração (determinística):** a skill de cada mineração (hoje `mineracao-silenciosas`) lê as tabelas que o
  pipeline produziu para a base, passo a passo do procedimento da análise, e descreve o que elas mostram. Ela não
  compara com relatório nem com outra base. Os números são o resultado.
- **Verificação, sem relatório nenhum:** o `auditor-independente` roda em paralelo uma segunda implementação, que
  recalcula as medidas direto do trace. Um script de encontro confronta as medidas dele com as tabelas. Somam-se as
  conferências internas, que valem em qualquer base. A mineração termina nas **paradas**, os pontos que pedem leitura
  de caso.
- **Investigação:** a `mineracao-investigacao` pega uma parada.
  - Quem escolhe os casos é uma regra fixa (`amostrar.py`), e o `investigador` lê.
  - O `segundo-leitor` relê às cegas (`concordancia.py`, com a tabela dos dois leitores lado a lado). Na candidata, a
    leitura é em duas etapas: primeiro em frase livre, depois nas categorias da lista que o pesquisador aprovou.
  - A hipótese vira regra contada na população inteira (`testar_regra.py`).
  - **O LLM propõe, o script conta.** Nenhum número sai da leitura do modelo.
- **Decisão:** é do pesquisador. Uma regra que mudaria número publicado é um *Ajuste*, e o kit para ali. Na candidata,
  o painel marca as situações que param no **gate do pesquisador**, e a decisão fica registrada
  (`registrar_decisao.py`).

## Evidência em todo relatório

O relatório é a análise final: quem o lê não pode precisar ir buscar evidência depois. **Cada afirmação leva:**
- o comando, com os parâmetros, que reproduz o número;
- a tabela derivada, com o filtro;
- nos achados que viram decisão ou parada, os casos crus: `exec_id`, a pasta `crus/` com a linha inteira do trace, a
  visão conferida em `derivados/` e o comando de recorte `drill_down.py caso <exec_id> <role>`.

O `montar_evidencia.py` monta tudo isso por regra fixa e escreve o bloco do relatório. O relatório completo fica no
ambiente do trace; a versão que sai troca os identificadores por `caso-N`, por script (`versao_para_sair.py`).
Detalhe em `skills/mineracao-base/referencias/evidencia.md`.

## O que mora onde

| Camada | Onde | Exemplos |
|---|---|---|
| **Método** | neste kit e nos docs de procedimento da análise | os passos, as conferências, o sigilo, o dossiê. O kit aponta para o procedimento e não o copia |
| **Base** | na pasta da análise | `TRACE`, `BASE_ID`, `DESTINO_MINERACAO`, as tabelas que o pipeline produziu para a base |
| **Objeto da rodada** | no argumento da chamada | a pasta da análise, a pergunta do roteiro (`silenciosas S2`) |

O kit não tem nome de base, pasta datada, unidade, ferramenta nem número de nenhuma base. Para conferir:
`grep -rnE "base ?[123]\b|U_[a-z]|2026-" .claude/skills/mineracao-* .claude/agents .claude/commands` não deve achar
nada fora do `manifesto.json` e do `exemplo.md`, que é uma rodada real e cita números de propósito.

## Conteúdo

```
.claude/skills/mineracao-base/    passo 0 comum: pasta, base, versão do código, intake, sigilo, relatório
  VERSAO · referencias/kit.md (este documento) · referencias/exemplo.md
  scripts/gerar_copilot.py        gera as cópias do Copilot (.github/agents, .github/prompts) a partir de .claude/
  scripts/conferir_versao.py      o código da análise é o do manifesto? (CRLF, TRACE/BASE_ID e saídas de notebook não contam)
  scripts/montar_evidencia.py     a evidência de um achado: casos por regra fixa, crus, visões, origem e o bloco do relatório
  scripts/amostrar.py             a regra fixa de escolha de casos (usada pela evidência e pela investigação)
  scripts/versao_para_sair.py     a versão do relatório que sai: identificadores → caso-N (o mapa fica no ambiente)
  scripts/varrer_pii.py           bloqueia a versão que sai se tiver processo, CPF, CNPJ, e-mail ou identificador de execução
  scripts/monitorar.py            o monitoramento (passo 0.5): confere as lições e sinais monitorados da análise e para com alerta
  manifesto.json                  os hashes do código para o qual esta versão do kit foi escrita
.claude/skills/mineracao-silenciosas/  a mineração das falhas silenciosas (lê as tabelas, passo a passo do procedimento da análise)
  scripts/comparar_auditoria.py   o encontro: tabelas da mineração × medidas da auditoria independente (audit_recompute9)
.claude/skills/mineracao-candidata/  a mineração de uma candidata a memória: parte genérica → funil → parte específica → arquivo final
  scripts/validar_memoria.py      confere o arquivo final contra o esquema da memória da análise (e converte o registro de um notebook)
  scripts/comparar_auditoria.py   o encontro: a parte genérica × a auditoria independente (audit_recompute6)
  scripts/valor_da_licao.py       o painel das lições: frequência (Pareto · presença no tempo), confiança (lida do confianca.json), situação e decisão
  scripts/registrar_decisao.py    registra a decisão do pesquisador num gate (a lista da leitura aberta; a situação do painel)
  referencias/fluxo.md            os diagramas da rodada e do ciclo de vida da parte específica
.claude/skills/mineracao-protocolo/  a mineração do protocolo do harness (resposta sem bloco de código)
  scripts/comparar_auditoria.py   o encontro: casos/passos/versões/modelos × a auditoria independente (audit_recompute10)
  scripts/cobertura.py            o cenário de cobertura: papéis por erros, com a cobertura acumulada
.claude/skills/mineracao-investigacao/  a investigação depois do determinístico
  roteiros/silenciosas.md         as perguntas abertas (S1 dono, S2 sucesso falso, S3 não reconhecido)
  roteiros/protocolo.md           P1 a camada do surto (o fim do prompt), P2 o mecanismo de cada caso (catálogo M1–M6)
  roteiros/candidata.md           a parte específica de uma candidata: a lição, a causa, o conserto, o destino → o arquivo final
  scripts/testar_regra.py · concordancia.py
.claude/agents/                   auditor-independente · investigador · segundo-leitor · validador-de-notebook
.claude/commands/                 rodada-silenciosas · rodada-protocolo · rodada-candidata · investigar · propor-notebook
```

## Instalar

- **Claude Code:** nada a instalar. O kit já está no `.claude/` do repositório; basta clonar ou atualizar.
- **Copilot:** gere as cópias, da raiz do repositório, depois de clonar e a cada atualização do kit:
  ```
  python .claude/skills/mineracao-base/scripts/gerar_copilot.py .
  ```
  Ele grava `.github/agents/*.agent.md` e `.github/prompts/*.prompt.md` (git-ignored). As skills o Copilot lê de
  `.claude/skills/`.
- **Edite sempre a fonte** em `.claude/`; as cópias do Copilot são sobrescritas a cada geração.
- Para usar em outro repositório, copie `.claude/skills/mineracao-*`, os quatro agentes e os cinco comandos.

## Usar

- `/rodada-silenciosas <pasta da análise>`: preparação → auditor em paralelo → mineração das tabelas → encontro → relatório com as paradas.
- `/rodada-protocolo <pasta da análise>`: o mesmo fluxo para o protocolo do harness (auditoria `audit_recompute10`).
- `/rodada-candidata <U_...> [<pasta>]`: minera uma candidata a memória e entrega o arquivo final no esquema da memória
  (`analysis/esquema-memoria.json`). O desenho está em `.claude/skills/mineracao-candidata/referencias/fluxo.md`.
- `/propor-notebook <U_...>`: só quando a lição cumpre a regra de criação do procedimento; escreve em `propostas/` e
  pede o laudo do validador.
- `/investigar silenciosas S2 [<pasta>]` ou `/investigar protocolo P2 [<pasta>]`: uma parada até o dossiê de decisão.

No Copilot, os mesmos nomes ficam como prompt files. Sem prompt, peça em linguagem natural ("rode as falhas silenciosas
na análise X"), que as skills disparam pela descrição.

## Versão e manifesto

- A preparação para se o código da análise não for o do manifesto. Os comandos, as tabelas e a auditoria que as
  skills usam são os deste código, e duas bases só se comparam se forem mineradas pelo mesmo código.
- Quando o pipeline muda de propósito (um Ajuste aprovado), regenere o manifesto e suba a `VERSAO`:
  `python .claude/skills/mineracao-base/scripts/conferir_versao.py analysis/<pasta> --gerar`.

## Backlog: as próximas skills, uma por etapa

| Mineração | O que falta antes da skill |
|---|---|
| resíduo | tirar o "procedimento do resíduo" do doc de validação para um doc próprio, no formato do procedimento das silenciosas |
| erro crítico | escrever o procedimento e resolver as fronteiras de chamada (os comandos ainda misturam as chamadas) |

## Limites desta versão

- **A leitura do `investigador` ainda não rodou ao vivo.** A ponte foi validada com uma resposta conhecida: o
  `testar_regra.py` reproduz caso a caso uma classificação determinística que já existia. A primeira leitura real é a
  primeira rodada de uso.
- **A auditoria em paralelo existe hoje para as falhas silenciosas e o protocolo** (`audit_recompute9` e `10`, com `--json`). Cada mineração
  nova do backlog precisa de uma auditoria com `--json` e de um script de encontro. Sem isso, ela fica só com as
  conferências internas.
- **O formato do Copilot** (`.agent.md`, `.prompt.md` com `mode: agent`) segue a documentação de 2026. Se a versão
  instalada esperar outro cabeçalho, o ajuste é só no `gerar_copilot.py`.
