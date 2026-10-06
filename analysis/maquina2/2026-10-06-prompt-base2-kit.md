# Prompt para o agente da máquina 2 — base 2, validação do kit de mineração (06/10/2026)

> **Como usar:** atualize o repositório da máquina 2 para o `main` (o merge do PR #33, `ebc641d`, ou posterior), copie
> este arquivo e entregue-o inteiro ao agente. O agente roda os passos, preenche o **Relatório** do fim e o grava em
> `pipeline/resultados/relatorio_maquina2_2026-10-06_kit.md` (git-ignored). O Rafael fotografa o relatório e traz para
> a máquina 1.
> Origem: `analysis/plano-atual.md` §4.14, passo 1 (com o §4.11). Os termos estão explicados em `analysis/glossario.md`;
> o kit, em `.claude/skills/mineracao-base/referencias/kit.md`.

---

## Você é o agente da máquina 2

Você trabalha na pasta da **base 2**: `analysis/2026-09-trace-law-flow-second/`. Os comandos do pipeline rodam de dentro
de `pipeline/`, no **terminal** (Git Bash), com `uv run` na frente. **Não rode notebooks pelo editor.** As skills e os
agentes do kit são disparados **da raiz do repositório** (`.claude/skills/mineracao-base/referencias/ambiente.md`).

Antes de tudo, no Git Bash: `export PYTHONIOENCODING=utf-8`. Se a gravação falhar com `FileNotFoundError` num caminho
que parece existir, é o limite de 260 caracteres: siga o `ambiente.md` (unidade virtual com `subst`).

Três tipos de passo:

- **Passos 0–2:** preparar, rodar e copiar números. É conferência determinística: marque **[conferido]**.
- **Passos 3–5:** as skills do kit. O que vem das tabelas e dos scripts é **[conferido]**; o que vem da leitura dos
  subagentes (`investigador`, `segundo-leitor`) é **[assistido]** e vale como hipótese.
- **Passo 6:** comparar com o publicado. É **fora do kit** (o kit não compara com relatório, de propósito): só depois
  que as três skills terminarem.

### Regras (compliance)

1. **Do relatório só saem:** contagens, percentuais, nomes de papel, ferramenta, modelo e unidade, hashes, meses,
   sim/não, as categorias fechadas das leituras e os nomes das paradas.
2. **Nunca saem:** `exec_id`, texto de caso (pergunta, documento, resposta, observação, justificativa), código do agente,
   texto de prompt, mensagem de erro, nome de variável do agente. As frases livres da leitura aberta ficam na máquina.
3. **Não altere arquivos do repositório**, exceto as cópias e as duas linhas do passo 0. Arquivos novos só em
   `pipeline/resultados/`. Nada de commit nem push.
4. **Não invente número nem conserte.** Se um comando falhar, copie a última linha da mensagem de erro (sem dado de caso)
   e siga para o próximo passo que não dependa dele. Se um número divergir do esperado, registre os dois.
5. **Os gates são do Rafael**, que está na máquina: quando uma skill parar num gate (a lista da leitura aberta, a
   situação da lição), pergunte a ele no chat e registre a resposta com o script que a skill indica.

---

## Passo 0 — Preparar a pasta `-second`

**0.1 · Ambiente.** Da raiz do repositório: `uv sync` (traz o `pyarrow`). O `analysis/leitor_trace.py`, o
`analysis/base_utils.py`, o `analysis/monitoramento.json`, o `analysis/esquema-memoria.json`, o `.gitignore` e o
`.claude/` já chegam com o `main`.

**0.2 · Copiar** de `analysis/2026-09-trace-law-flow/` para `analysis/2026-09-trace-law-flow-second/`, mesmo caminho
relativo:

| O quê | Arquivos |
|---|---|
| pipeline | `pipeline/base_pipeline.py`, `checklist.py`, `drill_down.py`, `metadados_steps.py` |
| notebooks | `pipeline/analise_trace_esteira_juridica.ipynb`, `mineracao_generica.ipynb`, `mineracao_unidades_n2_n10.ipynb`, `falhas_silenciosas.ipynb`, `consolidacao_unidades.ipynb` |
| auditorias | `audit/scripts/audit_recompute6.py`, `audit_recompute9.py`, `audit_recompute10.py` |
| docs | a pasta `docs/` inteira (as skills leem o procedimento e o racional de lá; o funil das candidatas está no `16`) |

Isso replica, de uma vez, o parquet (plano 4.10: as trocas de leitura no `base_pipeline.py`, `checklist.py` e
`drill_down.py`) e os Ajustes 13–16.

**0.3 · A camada da base.** No `pipeline/base_pipeline.py` da `-second`, troque **só** duas coisas: o nome do arquivo
no `TRACE` (linhas 42–43) para `"a0b49c79-8e90-4fd7-8cd2-c7ab38eaa43e.csv"` e `BASE_ID = "base2"` (linha 46).

**0.4 · A versão do código.** Da raiz:

```
uv run python .claude/skills/mineracao-base/scripts/conferir_versao.py analysis/2026-09-trace-law-flow-second
cat .claude/skills/mineracao-base/VERSAO
```

**Esperado:** os 14 arquivos `ok` e "versão do código: IGUAL ao manifesto" (o script mascara o `TRACE` e o `BASE_ID`,
o fim de linha e as saídas dos notebooks); a versão do kit é `0.6.0`. Se algum der `DIFERE` ou `FALTA`, **pare**: copie
a lista para o relatório.

**0.5 · O Copilot acha o kit no `.claude/`?** No chat do Copilot, digite `/`: devem aparecer `mineracao-silenciosas`,
`mineracao-protocolo`, `mineracao-candidata`, `investigar` e `propor-notebook`. Depois, apague as cópias antigas, se
existirem: `.github/agents/{auditor-independente,investigador,segundo-leitor,validador-de-notebook}.agent.md`,
`.github/prompts/{rodada-*,investigar,propor-notebook}.prompt.md` e qualquer `.github/skills/mineracao-*`. Registre
quais existiam.

## Passo 1 — Os notebooks e as tabelas, no terminal (a pendência do 4.2a)

De dentro de `pipeline/`, nesta ordem:

```
uv run python checklist.py
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 analise_trace_esteira_juridica.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 falhas_silenciosas.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 consolidacao_unidades.ipynb
uv run python drill_down.py silenciosas
uv run python drill_down.py protocolo > resultados/protocolo_base2.txt
```

Para cada notebook: **terminou? sim/não** (se não, a última linha do erro). Copie os números; a comparação com o
publicado é no passo 6.

| De onde | O que copiar |
|---|---|
| `checklist.py` | formato, linhas, memórias que parseiam e quebradas, tipos fora da dupla conhecida |
| esteira | erros · unidades · erros críticos |
| falhas silenciosas | falhas com exceção · silenciosas · % · candidatos a sucesso falso por grupo |
| consolidação §14.2 | unidades · candidatas (erros) · sinal de harness (quais) · críticos |
| consolidação §14.1 / §14.3 | `U_repr_colado`: visíveis · silenciosas · execuções em comum · ocorrências depois da consolidação |
| `protocolo` [1]–[6] | erros · execuções · por mês · por papel · recuperação |
| `protocolo` [4] (Ajuste 15) | a linha "sinal de resto": total e por papel |
| `protocolo` [10] (Ajuste 16) | a linha inteira (papel · erros · depois da ferramenta de resposta final · pela regra) |

## Passo 2 — O monitoramento primeiro

Da raiz:

```
uv run python .claude/skills/mineracao-base/scripts/monitorar.py analysis/2026-09-trace-law-flow-second
```

Copie a saída inteira (só tem contagens e nomes). **Esperado:**

| Item | Esperado |
|---|---|
| `U_nome_inventado` | **alerta**: ~118 erros contra 5 na base 1 (gatilhos `regua` e `cresce`; `sub_muda` e `sem_regra` podem disparar também — copie quais) |
| `U_campo_inexistente` | **alerta** de crescimento: 38 ≥ 3 × 10 |
| `ferramenta_concorre_com_final_answer` | **sem alerta** (o único caso da base 2 é de dez/2025, antes do gatilho `aparece_desde 2026-01`) |

O script sai com 1 por causa dos alertas. **Se os alertas forem exatamente estes dois, siga** — o Rafael já decidiu:
a `U_nome_inventado` é a candidata do passo 5, e o `U_campo_inexistente` é sinal de harness na base 2 (Ajuste 13). As
skills dos passos 3–5 rodam o monitoramento de novo no passo 0.5 delas e vão parar no alerta: responda que os alertas
são os esperados deste passo. **Qualquer outro alerta, ou um destes faltando: pare e chame o Rafael.**

## Passo 3 — `/mineracao-silenciosas analysis/2026-09-trace-law-flow-second`

Siga a skill até o fim (preparação → auditoria `audit_recompute9` em paralelo → mineração das tabelas → encontro →
relatório → `versao_para_sair.py` → `varrer_pii.py`). **Não abra a investigação das paradas**: só liste-as.

Traga: os achados principais em números, o encontro (n divergências; se ≠ 0, quais medidas), as conferências internas
(ok/falhou), a lista das paradas (nome e pergunta, sem caso) e se o varredor passou.

## Passo 4 — `/mineracao-protocolo analysis/2026-09-trace-law-flow-second`

O mesmo fluxo, com a auditoria `audit_recompute10`. **Não abra a investigação das paradas.**

Traga: o cenário de cobertura (papéis e a cobertura acumulada), incidente ou fundo por mês, a camada (modo, modelo), o
M1 medido, o [10], o encontro (n divergências), as paradas e se o varredor passou.

## Passo 5 — `/mineracao-candidata U_nome_inventado analysis/2026-09-trace-law-flow-second` (o 4.11)

Siga a skill: parte genérica (`mineracao_generica.ipynb` com `UNIDADE=U_nome_inventado`) → auditoria `audit_recompute6`
em paralelo → encontro → funil. No funil, a lição é `investigação:candidata`, então a skill abre a
`mineracao-investigacao` com o roteiro `candidata`:

1. **Leitura aberta** (frase livre; `investigador` e, às cegas, `segundo-leitor`) na amostra por regra fixa.
2. **Gate da lista** — pare e leve ao Rafael a lista de categorias proposta. Ele aprova, ajusta ou recusa; registre com
   `registrar_decisao.py --etapa lista`.
3. **Leitura fechada** em **≥ 20 outros casos** (não os da aberta), nas categorias aprovadas; concordância com o
   `concordancia.py`.
4. **As regras da base 1, sem mudança**, contadas na população inteira com o `testar_regra.py`
   (`--populacao mineracao/U_nome_inventado/casos.csv`), **lado a lado**:

   | Hipótese (base 1) | Regra |
   |---|---|
   | nunca definido (lição: não supor nome) | `--regex 'The variable \`[^\`]+\` is not defined' --campo-passo error` |
   | definido em chamada anterior (lição: o que foi definido em chamada anterior não vale) | `--condicao 'chamada > 1'` |
   | a mesma, na forma alternativa | `--regex 'Forbidden function evaluation' --campo-passo error` |

   Na base 1 (5 erros) as duas formas da segunda coincidiram; a base 2 decide qual fica. Para cada uma: pega certo ·
   pega a mais · deixa de pegar · concordância.
5. **O painel e o gate da situação:** `valor_da_licao.py` e, se a situação tem gate, pare e leve ao Rafael (registro com
   `registrar_decisao.py --etapa situacao`).
6. **O arquivo final** `memoria_U_nome_inventado_base2.json`, validado pelo `validar_memoria.py` (aprovado / reprovado /
   pendências).

**A pergunta do 4.11 — o modelo do ContestacaoCivel antes de agosto.** De dentro de `pipeline/`, depois do passo 1:

```
uv run python -c "import pandas as pd; m=pd.read_csv('resultados/evidencia/protocolo/modelos.csv'); print(m[m.role.str.contains('ontestacao',na=False)&(m.eixo=='modelo')][['role','valor','meses','steps']].to_string(index=False)); e=pd.read_csv('resultados/erros_mecanismo.csv'); x=e[e.role.str.contains('ontestacao',na=False)&(e.unidade=='U_nome_inventado')]; print('U_nome_inventado no ContestacaoCivel, por mês:'); print(x.groupby('mes').size().to_string() if len(x) else '  nenhum')"
```

O `modelos.csv` traz todos os papéis (não só os que têm erro de protocolo): modelo, meses (steps). A pergunta: o
ContestacaoCivel já rodava com o `gpt-5.2-2025-12-11` antes de ago/2026, e com quantos erros da lição?

## Passo 6 — Comparar com o publicado (fora do kit, depois dos passos 3–5)

Preencha a coluna "agora" com os números dos passos 1–5. Diferença ≠ 0: registre os dois e, se souber, de onde vem
(por exemplo, um Ajuste posterior à publicação). **Não conserte.**

| Medida | Publicado | Onde |
|---|---|---|
| erros · unidades · críticos | 479 · 16 · 1 | livro-razão §6 |
| candidatas (erros) | **7 (332)** depois do Ajuste 13 (eram 8 / 370) | livro-razão Ajuste 13 |
| `U_campo_inexistente` | sinal de harness, 38 erros · 36 execuções | Ajuste 13 |
| `U_repr_colado` | 18 visíveis · 86 silenciosas · 0 execuções em comum · 104 ocorrências | livro-razão Etapa 10d |
| falhas com exceção · silenciosas · % | 20 · 134 · 87% | `14` |
| candidatos a sucesso falso | 24/116 (plataforma 17/22 · argumento do agente 2/6 · não reconhecido 2/2 · JSON inválido 3/86) | `14` §5 |
| protocolo: erros · ago/2026 | 69 · 61 (58 execuções) | `11` §2.1 |
| protocolo: por papel | RoteadorCivel 56 · OBFCivel 4 · CalculoCivel 4 · RespostaBacen 4 · CalculoTrabalhista 1 | `11` §2.1 |
| protocolo: recuperação | papel entregou depois 66/69 · execução com resposta 69/69 | `11` §2.1 |
| protocolo: modelo | RoteadorCivel `gpt-5.6-terra-2026-07-09` 54 em 478 steps; `gpt-4.1` 0 em 1.341 | `11` §2.2 |
| protocolo: sinal de resto (Ajuste 15) | os erros do surto de ago/2026 com o sinal (0,03–0,18 do normal) | Ajuste 15 |
| protocolo: [10] (Ajuste 16) | um M2, de dez/2025 | Ajuste 16 |
| `U_nome_inventado` | 118 erros · 112 execuções · 5 meses · 6 papéis | livro-razão §6 |
| `U_nome_inventado`: concentração | 101 no ContestacaoCivel, ago/2026, `gpt-5.2-2025-12-11` · 104 no 1º step da chamada · 107 com o nome definido depois · 1 de chamada anterior · 1 logo depois de resposta sem bloco de código | livro-razão Etapa 10d |

---

## Relatório (gravar em `pipeline/resultados/relatorio_maquina2_2026-10-06_kit.md`)

```markdown
# Relatório da máquina 2 — base 2, validação do kit — 06/10/2026

## 0. Preparação [conferido]
uv sync: ok/erro · conferir_versao: IGUAL / lista DIFERE-FALTA · VERSAO do kit:
Copilot: as 5 skills aparecem no `/`? sim/não (quais faltam) · cópias antigas em .github/ que existiam e foram apagadas:

## 1. Notebooks e tabelas [conferido]
checklist: formato · linhas · memórias ok/quebradas · tipos fora da dupla
esteira terminou? · erros · unidades · críticos
falhas silenciosas terminou? · com exceção · silenciosas · % · [4] por grupo
consolidação terminou? · unidades · candidatas (erros) · sinal de harness · críticos · U_repr_colado (vis./sil./comum/ocorr.)
protocolo: erros · execuções · por mês · por papel · recuperação · sinal de resto · [10]

## 2. Monitoramento [conferido]
<a saída inteira do monitorar.py> · os alertas foram exatamente os esperados? sim/não

## 3. Falhas silenciosas (skill) [conferido]
achados em números · encontro: n divergências · conferências internas · paradas (nome e pergunta) · varredor: passou?

## 4. Protocolo do harness (skill) [conferido]
cobertura · incidente/fundo por mês · camada · M1 · [10] · encontro: n divergências · paradas · varredor: passou?

## 5. U_nome_inventado (skill) [conferido] e [assistido]
parte genérica (G1–G6, só contagens) · encontro: n divergências
leitura aberta: n casos · lista proposta (as categorias, sem frase de caso) · decisão do Rafael no gate
leitura fechada: n casos · contagem por categoria, leitor 1 × leitor 2 · concordância (kappa)
regras da base 1: | regra | pega certo | a mais | deixa de pegar | concordância |
painel: frequência · confiança · situação · decisão do Rafael no gate
arquivo final: aprovado / reprovado / pendências
ContestacaoCivel: modelo por mês (steps) · erros da lição por mês

## 6. Comparação com o publicado (fora do kit)
| medida | publicado | agora | diferença e de onde vem |

## 7. O que chamou atenção e não estava no roteiro (sem dado de caso)
```
