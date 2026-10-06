---
name: mineracao-base
description: "Pré-condições comuns de toda mineração do trace de agentes (kit de mineração): localizar a pasta da análise, ler a base e o trace que ela aponta, conferir se o código é a versão do kit, rodar o intake, as regras de sigilo do que pode sair do ambiente, o esqueleto do relatório, a regra de que toda afirmação leva evidência (comando, tabela e caso cru), o montador de evidência e o varredor de PII. Use SEMPRE no início de qualquer skill mineracao-* (silenciosas, protocolo, resíduo, crítico, candidata), e quando pedirem para 'conferir a versão do pipeline', 'rodar o intake de uma base' ou 'varrer o relatório antes de sair'. Não decide nada sobre o método: o passo a passo de cada mineração está nos docs de procedimento da própria análise."
---

# Mineração do trace — a base comum

Esta skill é o **passo 0** de toda mineração. Ela não sabe qual base, qual pasta, quais unidades nem quais números:
tudo isso vem da pasta da análise. O método também não mora aqui. O porquê e o passo a passo estão nos docs da
análise (`docs/*racionais*`, `docs/*procedimento*`, `docs/*relatorio*`); a skill de cada mineração aponta para o doc
dela.

## Regras que valem em toda a rodada

0. **Nenhuma afirmação sem evidência** ([`referencias/evidencia.md`](referencias/evidencia.md)). Cada número do
   relatório leva o comando que o reproduz e a tabela de onde sai. Cada achado que vira decisão ou parada leva também
   os casos crus: `exec_id`, `crus/`, o recorte com `drill_down.py caso`. Os casos são montados pelo
   `scripts/montar_evidencia.py`, por regra fixa, e entram no relatório colados do `bloco.md` que ele escreve. O
   relatório é a análise final: quem o lê não pode precisar ir buscar evidência depois.
1. **Nenhum LLM no caminho da classificação.** Família, assinatura, mecanismo, unidade e grupo vêm das regras
   determinísticas do pipeline. O agente roda, confere e organiza. A leitura de caso é `[assistido]` e vale como
   hipótese até o pesquisador conferir.
2. **Não conserta.** Quando a mineração e a auditoria independente divergem, ou quando uma conferência interna falha,
   registre os dois valores e pare. A divergência é o achado. Uma regra nova (uma palavra-chave, um padrão, uma
   unidade) é uma proposta para o pesquisador, nunca uma edição. Se ela mudasse número já publicado, seria um
   *Ajuste*: parar e perguntar.
3. **Não compara com relatório nem com outra base.** A mineração descreve a base que está na mesa. A verificação é
   interna: uma segunda implementação (a auditoria, em paralelo) e as conferências que valem em qualquer base.
4. **Não edita o repositório.** Arquivos novos vão só em `pipeline/resultados/` (git-ignored). Sem commit, sem push.
5. **Sigilo:** [`referencias/sigilo.md`](referencias/sigilo.md). Em resumo, para fora só vão contagens, nomes de
   papel, ferramenta e unidade, meses, sim/não e categorias fechadas. Nunca identificador de execução, texto de caso,
   código ou prompt.
6. **Ambiente:** [`referencias/ambiente.md`](referencias/ambiente.md) (`uv run`, notebooks pelo terminal, Windows:
   UTF-8 e o limite de 260 caracteres).

## Passo 0 — antes de minerar

**0.1 · Localizar a análise.** É a pasta datada que tem `pipeline/`, `docs/` e `audit/`, dentro de `analysis/`. Use a
pasta que vier no pedido. Se não vier, use a pasta corrente: se ela for `pipeline/`, suba um nível. Se não houver
`pipeline/base_pipeline.py`, pare e pergunte.

**0.2 · Ler a base e o trace** (de dentro de `pipeline/`):

```
uv run python -c "import os, base_pipeline as b; from leitor_trace import formato_do_trace as f; print('base:', b.BASE_ID, '| trace:', f(b.TRACE), '|', round(os.path.getsize(b.TRACE)/1e6), 'MB')"
```

O `BASE_ID` é o rótulo da base em todos os passos e no nome do relatório. O nome do arquivo do trace não entra no
relatório: tem formato de identificador.

**0.3 · Conferir a versão do código** (de qualquer lugar):

```
uv run python <esta skill>/scripts/conferir_versao.py <pasta-da-analise>
```

O script compara o código da análise com o manifesto do kit. A camada da base (`TRACE`, `BASE_ID`), o fim de linha e
as saídas dos notebooks não contam. Se ele sair com 1, **pare**: liste os arquivos DIFERE/FALTA e pergunte. Há dois
motivos para parar: os comandos, as tabelas e a auditoria que as skills usam são os deste código; e duas bases só se
comparam se forem mineradas pelo mesmo código.

**0.4 · Intake** (de dentro de `pipeline/`):

```
uv run python checklist.py
```

Copie para o relatório o formato do §0, as linhas, as memórias que parseiam e as quebradas, e os tipos fora da dupla
conhecida no §4. Se ele sair com 1 (memória do parquet que não parseia), **pare**.

**0.5 · Monitoramento** (de qualquer lugar):

```
uv run python <esta skill>/scripts/monitorar.py <pasta-da-analise>
```

Confere, nesta base, cada lição ou sinal que o pesquisador decidiu monitorar (o `monitoramento.json` da pasta da
análise ou, normalmente, o da pasta acima, compartilhado pelas pastas de todas as bases). É a
única comparação com outra base que o kit faz, e é de propósito: a linha de base e os gatilhos foram registrados pelo
pesquisador quando ele decidiu monitorar. Se sair com 1, **pare** e leve os alertas ao pesquisador antes de minerar:
a lição volta ao gate dele. Se sair com 2, falta uma tabela (o script diz o comando que a gera) ou falta o próprio registro. Copie a saída para o
relatório.

## Depois do passo 0

Siga a skill da mineração pedida. Ao terminar:

1. preencha o relatório no esqueleto de [`referencias/relatorio.md`](referencias/relatorio.md), em
   `pipeline/resultados/relatorio_<mineracao>_<BASE_ID>_<AAAA-MM-DD>.md`, com a evidência de cada achado;
2. gere a versão que sai e varra:
   `uv run python <esta skill>/scripts/versao_para_sair.py <relatório>`, depois
   `uv run python <esta skill>/scripts/varrer_pii.py <relatório>_saida.md`. Se o varredor sair com 1, corrija e rode
   de novo;
3. na resposta ao pesquisador, entregue os achados principais, o resultado da verificação (auditoria × tabelas e
   conferências internas), as **paradas** (o que precisa de leitura de caso ou de decisão dele) e o caminho do
   relatório completo, onde está a evidência. No chat, o sigilo vale: sem identificador.

## A versão do kit

O arquivo `VERSAO` desta skill é a versão do kit (as skills, os agentes e os comandos de mineração em `.claude/`; a
descrição do kit inteiro está em [`referencias/kit.md`](referencias/kit.md)). Copie a versão para o relatório. Quando o pipeline muda de propósito (um Ajuste aprovado), o manifesto é regenerado
na fonte do kit com `conferir_versao.py <pasta> --gerar`, e a versão sobe.
