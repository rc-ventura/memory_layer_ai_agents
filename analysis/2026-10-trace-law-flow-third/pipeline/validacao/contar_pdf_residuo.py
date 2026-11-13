"""Base 3: o grupo "PDF" do resíduo (b3 #5) — o que o agente muda no passo seguinte para o erro sumir?

O grupo `pdf_layout` do balde "sintoma não reconhecido" (13 erros, 12 execuções, fev a abr, papel AgenteEstruturador) é o
`LayoutError` do gerador de PDF: uma linha de tabela maior que a página. A linha que falhou chama uma de duas ferramentas
(`orquestrador_eletronico`, `orquestrador_papel`), e o agente conserta no passo seguinte em 13 de 13 (relatório do
ambiente, 13/11). Falta saber **o que ele muda**, e a resposta decide o destino (procedimento do resíduo, passo 4,
pergunta R2: a falha é do agente, que passa conteúdo grande demais, ou da ferramenta, que não parte a linha?).

A medida, por erro, entre o código do passo que falhou e o do passo seguinte (só números, nenhum trecho de código):
  - os caracteres e as linhas do código;
  - quantas vezes a ferramenta da linha que falhou é chamada em cada um (`chamadas`);
  - o maior literal de texto (caracteres) — onde mora o conteúdo que o PDF recebe;
  - **as ferramentas chamadas** no passo seguinte e no depois dele (nomes chamados como função simples, fora os embutidos
    do Python e as funções definidas no próprio código; um `from x import y` conta), se a ferramenta que falhou volta a
    ser chamada no segundo passo e se a execução termina no passo seguinte;
e o que mudou, por regra e na ordem (a primeira que casa vale):
  sem_passo           o papel não teve passo seguinte;
  nao_parseia         um dos dois códigos não é Python inteiro (só os caracteres contam);
  outra_ferramenta    o passo seguinte não chama mais a ferramenta;
  dividiu             o passo seguinte chama a ferramenta mais vezes (parte o conteúdo em várias chamadas);
  encurtou            o código do passo seguinte é pelo menos 20% menor;
  outra_mudanca       nenhuma das anteriores (o agente muda outra coisa).
Por ferramenta: erros, execuções, a distribuição do que mudou, a mediana e os extremos de caracteres (falhou → seguinte)
e do maior literal. É um sinal, não um veredito: ler o código dos casos é a investigação, no ambiente.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel e de ferramenta, e meses.
Grava `pdf_medidas.csv` (um erro por linha, só números, sem identificador) na pasta do `casos.csv`. Uso, da raiz:
    uv run --no-sync python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_pdf_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv> --fonte <parquet da base>
"""
import argparse
import ast
import builtins
from collections import Counter
from pathlib import Path
import statistics
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contar_infra_residuo as INFRA  # noqa: E402
import contar_limites_interpretador_residuo as LIM  # noqa: E402
import contar_recorrencia_sintoma_residuo as REC  # noqa: E402

GRUPO = "pdf_layout"
MUDANCAS = ["sem_passo", "nao_parseia", "outra_ferramenta", "dividiu", "encurtou", "outra_mudanca"]
ENCURTOU = 0.8      # o código do passo seguinte é pelo menos 20% menor
COLUNAS = ["role", "mes", "ferramenta", "mudanca", "chars_falhou", "chars_seguinte", "linhas_falhou",
           "linhas_seguinte", "chamadas_falhou", "chamadas_seguinte", "literal_falhou", "literal_seguinte",
           "ferramentas_seguinte", "ferramentas_next2", "chamadas_next2", "fim_no_seguinte"]
EMBUTIDOS = set(dir(builtins))


def _nome(f):
    """O último componente do nome chamado (`pdf.orquestrador_papel` → `orquestrador_papel`), ou None."""
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _arvore(codigo):
    if LIM._vazio(codigo):
        return None
    try:
        return ast.parse(str(codigo))
    except (SyntaxError, ValueError):
        return None


def chamadas(t, ferramenta):
    """Quantas vezes a ferramenta é chamada na árvore."""
    return sum(isinstance(n, ast.Call) and _nome(n.func) == ferramenta for n in ast.walk(t))


def ferramentas(t):
    """Os nomes chamados como função simples (não método), fora os embutidos do Python e as funções ou classes definidas
    no próprio código: as ferramentas que o passo chama. Ordenados, sem repetição."""
    definidas = {n.name for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    return sorted({n.func.id for n in ast.walk(t) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id not in EMBUTIDOS and n.func.id not in definidas})


def maior_literal(t):
    """O maior literal de texto da árvore, em caracteres (0 se não houver)."""
    return max((len(n.value) for n in ast.walk(t) if isinstance(n, ast.Constant) and isinstance(n.value, str)),
               default=0)


def mudanca(falhou, seguinte, ferramenta, depois=None):
    """O que mudou do código que falhou para o do passo seguinte, e as medidas (ver o docstring). `depois`: o código do
    segundo passo seguinte (ou None), para as ferramentas dele e para saber se a ferramenta que falhou volta."""
    c = _arvore(depois)
    m = {"chars_falhou": 0 if LIM._vazio(falhou) else len(str(falhou)),
         "chars_seguinte": 0 if LIM._vazio(seguinte) else len(str(seguinte)),
         "linhas_falhou": 0 if LIM._vazio(falhou) else len(str(falhou).splitlines()),
         "linhas_seguinte": 0 if LIM._vazio(seguinte) else len(str(seguinte).splitlines()),
         "chamadas_falhou": None, "chamadas_seguinte": None, "literal_falhou": None, "literal_seguinte": None,
         "ferramentas_seguinte": "", "ferramentas_next2": "" if c is None else " ".join(ferramentas(c)),
         "chamadas_next2": None if c is None else chamadas(c, ferramenta),
         "fim_no_seguinte": LIM._vazio(depois) and not LIM._vazio(seguinte)}
    if LIM._vazio(seguinte):
        return "sem_passo", m
    a, b = _arvore(falhou), _arvore(seguinte)
    if b is not None:
        m["ferramentas_seguinte"] = " ".join(ferramentas(b))
    if a is None or b is None:
        return "nao_parseia", m
    m.update(chamadas_falhou=chamadas(a, ferramenta), chamadas_seguinte=chamadas(b, ferramenta),
             literal_falhou=maior_literal(a), literal_seguinte=maior_literal(b))
    if m["chamadas_seguinte"] == 0:
        return "outra_ferramenta", m
    if m["chamadas_seguinte"] > m["chamadas_falhou"]:
        return "dividiu", m
    if m["chars_falhou"] and m["chars_seguinte"] <= ENCURTOU * m["chars_falhou"]:
        return "encurtou", m
    return "outra_mudanca", m


def medir(G, F):
    """Uma linha por erro do grupo, com a ferramenta, o que mudou e as medidas. `G`: os erros do grupo (do `casos.csv`,
    com a coluna `mensagem`); `F`: a fonte (colunas de `LIM.COLUNAS_FONTE`). Devolve (tabela, erros sem linha na fonte)."""
    por = {}
    for r in F.to_dict("records"):
        por.setdefault((str(r["cod_idef_exeo"]), str(r["cod_idef_aget"]), str(r["papel"]), int(float(r["step_pos"]))), r)
    linhas, faltam = [], 0
    for _, r in G.iterrows():
        l = por.get(LIM._chave_casos(r))
        faltam += l is None
        ferr = INFRA.funcao_na_linha(str(r["mensagem"])).split(".")[-1]
        quem, m = mudanca(*((None, None) if l is None else (l.get("error_code_action"), l.get("next_code_action"))),
                          ferr, None if l is None else l.get("next2_code_action"))
        linhas.append({"role": r["role"], "mes": r["mes"], "ferramenta": ferr, "mudanca": quem, **m})
    return pd.DataFrame(linhas, columns=COLUNAS), faltam


def _mediana(s):
    s = [x for x in s if x is not None and x == x]
    return int(statistics.median(s)) if s else None


def _contar_nomes(serie):
    return dict(Counter(n for s in serie for n in str(s).split() if s == s and n).most_common())


def _depois(g):
    """Para onde o agente vai: as ferramentas do passo seguinte (nos que largaram a ferramenta) e se ela volta."""
    larg = g[g.mudanca.eq("outra_ferramenta")]
    if len(larg):
        print(f"  os que largaram a ferramenta ({len(larg)}): ferramentas do passo seguinte "
              f"{_contar_nomes(larg.ferramentas_seguinte)}; do depois dele {_contar_nomes(larg.ferramentas_next2)}; "
              f"a ferramenta volta no depois dele em {int((larg.chamadas_next2.fillna(0) > 0).sum())}; a execução "
              f"termina no passo seguinte em {int(larg.fim_no_seguinte.sum())}")
    print(f"  todos ({len(g)}): a ferramenta volta no passo seguinte em {int((g.chamadas_seguinte.fillna(0) > 0).sum())} "
          f"e no depois dele em {int((g.chamadas_next2.fillna(0) > 0).sum())}; nunca volta nos dois passos em "
          f"{int(((g.chamadas_seguinte.fillna(0) == 0) & (g.chamadas_next2.fillna(0) == 0)).sum())}")


def _imprimir(T, faltam):
    print(f"grupo {GRUPO}: {len(T)} erros · {T.role.nunique()} papéis · meses {T.mes.value_counts().sort_index().to_dict()}"
          f" · {faltam} sem linha na fonte")
    for ferr, g in T.groupby("ferramenta"):
        d = g.mudanca.value_counts().reindex(MUDANCAS, fill_value=0)
        print(f"\n== {ferr}: {len(g)} erros")
        print(f"  o que mudou no passo seguinte: {d[d > 0].to_dict()}")
        print(f"  caracteres do código (falhou → seguinte): mediana {_mediana(g.chars_falhou)} → "
              f"{_mediana(g.chars_seguinte)}; extremos {g.chars_falhou.min()}–{g.chars_falhou.max()} → "
              f"{g.chars_seguinte.min()}–{g.chars_seguinte.max()}")
        print(f"  maior literal de texto (falhou → seguinte): mediana {_mediana(g.literal_falhou)} → "
              f"{_mediana(g.literal_seguinte)}")
        print(f"  chamadas da ferramenta (falhou → seguinte): {g.chamadas_falhou.tolist()} → "
              f"{g.chamadas_seguinte.tolist()}")
        _depois(g)
    d = T.mudanca.value_counts().reindex(MUDANCAS, fill_value=0)
    print(f"\n== resumo: {d[d > 0].to_dict()}")
    nunca = T[(T.chamadas_seguinte.fillna(0) == 0) & (T.chamadas_next2.fillna(0) == 0)]
    print(f"   a ferramenta nunca volta nos dois passos seguintes: {len(nunca)} de {len(T)}; desses, a execução termina "
          f"no passo seguinte em {int(nunca.fim_no_seguinte.sum())} (sem a ferramenta e sem fim: "
          f"{int((~nunca.fim_no_seguinte).sum())})")


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", required=True)
    p.add_argument("--fonte", required=True)
    a = p.parse_args(argv)
    C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
    faltam = [c for c in ("mensagem", "padrao", "unidade", "tok_tot", "idx") if c not in C.columns]
    if faltam:
        print(f"casos.csv sem a coluna {faltam}: rode o `especificas/residuo.py` desta versão")
        return 1
    S = REC.contar(C)
    G = S[S.grupo.eq(GRUPO)]
    if G.empty:
        print(f"o `casos.csv` não tem erros do grupo {GRUPO}")
        return 1
    T, sem_linha = medir(G, LIM.ler_fonte(a.fonte))
    _imprimir(T, sem_linha)
    destino = Path(a.casos).parent / "pdf_medidas.csv"
    T.to_csv(destino, index=False)
    print(f"\n→ {destino} ({len(T)} erros; só números, sem identificador)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
