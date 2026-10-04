# Procedimento — medir as falhas silenciosas numa base

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Para que serve este documento:** o roteiro para rodar o balde invisível numa base nova (ou na base 2) e validar as
regras. Mesmo papel do [`03-procedimento-validacao.md`](03-procedimento-validacao.md), só para o erro que não vira
exceção. O **porquê** de cada passo está em [`13-racionais-falhas-silenciosas.md`](13-racionais-falhas-silenciosas.md);
os resultados por base, em [`14-relatorio-falhas-silenciosas.md`](14-relatorio-falhas-silenciosas.md).

**Regra de ouro (do 03):** nenhum número agregado sem um caso concreto que o sustente — e nenhuma regra nova escrita
olhando uma base só.

## 0 · Pré-condições e o que sai da máquina

- Rodar de dentro da pasta `pipeline/` da base (`2026-09-trace-law-flow` ou `-second`). Na máquina 2, `uv run` na frente
  de cada comando.
- **Copiar para a `-second`** (convenção do livro-razão): `base_pipeline.py` (restaurar `TRACE` e `BASE_ID`),
  `drill_down.py` e `falhas_silenciosas.ipynb`. O notebook importa `analysis/base_utils.py` (dois níveis acima de
  `pipeline/`), que já vem com o repositório.
- As medidas [2]/[3] do `drill_down.py silenciosas` precisam do `resultados/erros_mecanismo.csv` (gerado pelo notebook
  da esteira); o notebook das falhas silenciosas não precisa — monta os erros sozinho.
- **Sai da máquina de compliance:** contagens, nomes de papel e de ferramenta, grupos, formas (só o tipo), motivos
  **mascarados** (`--motivos`). Tudo o que o notebook e o `silenciosas` imprimem é isso — pode ser fotografado.
- **Não sai:** `exec_id`, texto de caso, código do agente. `resultados/evidencia/silenciosas/casos.csv` e
  `ocorrencias.csv` têm `exec_id`: **ler na máquina**. `resultados/` é git-ignored.

## Passo 1 — Rodar o balde

```
jupyter nbconvert --to notebook --execute --inplace falhas_silenciosas.ipynb
```

(ou abrir e rodar tudo). Equivalente rápido, só as medidas [1]–[4]:

```
python drill_down.py silenciosas
```

Conferir na §13.1 do notebook:

- **sobreposição visível × invisível = 0** (se não for, o funil quebrou — parar);
- a soma dos grupos (§13.3) = total de silenciosas;
- a escala: % silenciosas entre as falhas de ferramenta (base 1: 93%; base 2: 87%).

## Passo 2 — Cobertura das regras de motivo

```
python drill_down.py silenciosas --motivos
```

Lista os motivos mascarados por ferramenta, com o grupo atribuído. Olhar o `nao_reconhecido` e os grupos que parecem
errados.

- **Regra nova só olhando as duas bases.** Antes de propor uma palavra-chave, conferir se o mesmo texto aparece (ou o
  equivalente) na outra base; a regra entra em `MOTIVO_REGRAS` anotando a base de origem (`b1`, `b2`, `b1 b2`).
- Uma regra nova que muda o grupo de casos já publicados é um **Ajuste**: apresentar, aprovar, rodar nas duas bases.
- `nao_reconhecido` alto numa base nova é sinal de cobertura (ferramentas novas), não de erro do método.

## Passo 3 — O dono do `json_invalido` (e de qualquer grupo com dono "a conferir")

```
python drill_down.py silenciosas --forma <ferramenta>
```

Para cada ferramenta com falhas `json_invalido`. Só contagem por tipo:

| Forma | Leitura |
|---|---|
| `json.dumps(...)` / variável devolvida por outra ferramenta | o JSON quebrado vem da ferramenta → plataforma |
| `str(...)`, dict ou string montados à mão | o agente → memória |
| … colado de um retorno impresso | o gesto do `repr_colado` → a unidade `U_repr_colado`, canal silencioso |

O rótulo do grupo no código **não muda** com o resultado (é genérico); o dono conferido vai para o relatório (`14`) e o
livro-razão.

## Passo 4 — O que vem depois e o contrato de retorno

No notebook, §13.4 ([2] e [3]):

- "(nenhum erro)" dominante → a falha passa sem rastro no visível (esperado);
- `U_tipo_retorno` / `U_contrato_dict` / `U_campo_inexistente` precedidos por falha silenciosa: se passar de ~1/3,
  investigar — a memória de contrato pode ser efeito da plataforma. Nas duas bases ficou em 0–9%.

## Passo 5 — Candidatos a sucesso falso

No notebook, §13.5 ([4]). É teto. Conferir no caso, na máquina:

1. Em `resultados/evidencia/silenciosas/casos.csv`, 2–3 linhas do grupo `plataforma` (e de outro grupo com taxa alta).
2. `python drill_down.py caso <exec_id> <papel>` → o `final_answer` usa um dado que deveria ter vindo da ferramenta
   que falhou?
3. Sai só **sim/não** e a contagem.

## Passo 6 — Detectores de comportamento

No notebook, §13.7. Os números da base 1 são a referência (inventário 90; Result-Ignore 103/3.053; RAC 125; Tool-Skip
10/840). Numa base nova:

- conferir o inventário declarado (união dos papéis) — se for muito menor que o número de ferramentas chamadas, o
  system prompt mudou de formato;
- Tool-Skip continua provisório; RAC é sensível à definição — reportar com a ressalva.

## Passo 7 — Ocorrências e registro

- A §13.8 grava `resultados/evidencia/silenciosas/ocorrencias.csv` — a entrada do balde invisível para a consolidação,
  com unidade (`REGRAS_INVISIVEL`) e ocorrência (cascata × unidade). Não sai da máquina.
- Depois, `consolidacao_unidades.ipynb` (§14.x): a §14.1 tem de dar 0 steps nos dois canais; a §14.3 lista o que a
  consolidação muda contra a triagem só do visível. Base 1: só a `U_repr_colado` (6 → 12). Conferência independente:
  bloco G do `audit_recompute9`.
- Registro: números no `14`; mudança de regra no livro-razão (gatilho → evidência → mudança → verificação → o que
  replicar); o item no `plano-atual.md`.

## Conferências

- Sobreposição visível × invisível = 0.
- Soma dos grupos = total de silenciosas; falhas reais = argumento + plataforma + JSON inválido + não reconhecido.
- `silenciosas` e o notebook dão os mesmos números (são as mesmas funções do `base_pipeline.py`).
- Detectores da §13.7 na base 1 iguais aos de referência.
