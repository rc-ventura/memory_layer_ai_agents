"""Estudo de caso do `U_sandbox` na base 3: de onde a unidade partiu (3.653 erros, 16/10) até os 1.100 de hoje, e como
os 1.100 se dividem nas memórias.

Os números não são lidos de uma rodada: são as contagens das rodadas da máquina da base, transcritas das fotos no
dossiê (`dossie_base3.md`, a seção de cada linha está ao lado). Só contagens. Uma contagem nova entra aqui com a seção do
dossiê que a registra.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/figura_estudo_caso.py
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "pipeline"))
from paleta import BASE, COR_ERRO, INK, INK2, MUTED   # noqa: E402

ROSA = COR_ERRO["Ambiente & sandbox"]   # a cor da família, a mesma da genealogia

# (rótulo, erros que saem, rodada e seção do dossiê) — cada degrau leva erros do sandbox para o sinal de harness
INICIO = (3653, "16/10 · rodada e3ebc827 · §1")
SAIDAS = [("Ajuste 21: verificação de existência por introspecção\n(globals/locals/vars, o prompt manda verificar)", 2217,
           "19/10 · 85706f1e · §2b (por diferença: 3.653 − 1.436)"),
          ("Ajuste 23: eval da função auxiliar de verificação", 35, "19/10 · aedb9b5d · §2d"),
          ("Ajuste 26: import de ferramenta citada e não declarada", 167, "21/10 · 99e032ad · §2h item 11"),
          ("Ajuste 27: verificação com globals no papel cujo prompt\nmanda verificar", 134,
           "21/10 · 99e032ad · §2h item 11 (por diferença)")]
HOJE = 1100

# as memórias dos 1.100 (rodada 99e032ad, §2h item 11); True = vai para o agente (§2h item 27)
MEMORIAS = [("C · importe json, re, datetime (global)", 423, True),
            ("E · não chame repr, dir…; inspecione com print(type(x)) (global)", 317, True),
            ("C.JoogleAnalytics · importe pandas as pd", 231, True),
            ("B.OBFCivel · chame a ferramenta direto, sem import", 44, False),
            ("D · import fora da lista, por papel (10 papéis)", 40, False),
            ("F · globals/eval/locals/vars restantes (em aberto)", 37, False),
            ("sem nome (InterpreterError sem padrão)", 5, False),
            ("C.CalculoTrabalhista · importe pandas as pd", 2, False),
            ("B.RespostaBacen", 1, False)]


def _n(v):
    return f"{v:,}".replace(",", ".")


def conferir():
    resto = INICIO[0] - sum(n for _, n, _ in SAIDAS)
    if resto != HOJE:
        raise SystemExit(f"os degraus não fecham: {INICIO[0]} − saídas = {resto}, e hoje são {HOJE}")
    if sum(n for _, n, _ in MEMORIAS) != HOJE:
        raise SystemExit(f"as memórias somam {sum(n for _, n, _ in MEMORIAS)}, e a unidade tem {HOJE}")


def desenhar(destino):
    conferir()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 10.5), gridspec_kw={"height_ratios": [1.05, 1], "hspace": 0.55})

    # 1 · a escada: o que a unidade tinha, o que saiu a cada ajuste, o que ficou
    linhas = [("U_sandbox em 16/10", INICIO[0], 0, ROSA, INICIO[1])]
    nivel = INICIO[0]
    for rot, n, fonte in SAIDAS:
        nivel -= n
        linhas.append((rot, n, nivel, MUTED, fonte))
    linhas.append(("U_sandbox hoje", HOJE, 0, ROSA, "21/10 · rodada 99e032ad · §2h item 11"))
    for i, (rot, n, esq, cr, fonte) in enumerate(linhas):
        a1.barh(i, n, left=esq, color=cr, height=0.62)
        sinal = "−" if cr == MUTED else ""
        a1.text(esq + n + 40, i, f"{sinal}{_n(n)}  ·  {fonte}", va="center", fontsize=8.5, color=INK2)
    a1.set_yticks(range(len(linhas)), [r for r, *_ in linhas], fontsize=9)
    a1.invert_yaxis()
    a1.set_xlim(0, INICIO[0] * 1.55)
    a1.set_xlabel("erros estruturados")
    a1.set_title(f"De onde a unidade partiu: {_n(INICIO[0])} erros em 16/10, {_n(HOJE)} hoje — "
                 f"{_n(INICIO[0] - HOJE)} ({100 * (INICIO[0] - HOJE) / INICIO[0]:.0f}%) foram para o sinal de harness "
                 "(conserto no prompt), não memória", loc="left", fontsize=11, color=INK)

    # 2 · os 1.100 de hoje, por memória
    m = MEMORIAS
    agente = sum(n for _, n, a in m if a)
    for i, (rot, n, vai) in enumerate(m):
        a2.barh(i, n, color=ROSA if vai else BASE, height=0.62)
        a2.text(n + 6, i, f"{_n(n)} ({100 * n / HOJE:.0f}%)" if n >= 11 else _n(n), va="center", fontsize=8.5,
                color=INK2)
    a2.set_yticks(range(len(m)), [r for r, *_ in m], fontsize=9)
    a2.invert_yaxis()
    a2.set_xlim(0, max(n for _, n, _ in m) * 1.25)
    a2.set_xlabel("erros estruturados")
    a2.set_title(f"Os {_n(HOJE)} de hoje: 3 memórias vão para o agente (rosa) e cobrem {_n(agente)} "
                 f"({100 * agente / HOJE:.0f}%); as outras ficam no catálogo, monitoradas ou em aberto", loc="left",
                 fontsize=11, color=INK)
    for ax in (a1, a2):
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _n(int(v))))
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.text(0.01, 0.005, "Contagens das rodadas da máquina da base, transcritas das fotos em dossie_base3.md. "
             "Cinza = saiu do sandbox para o sinal de harness (as unidades da verificação de existência e da ferramenta citada e não declarada).",
             fontsize=8, color=MUTED)
    fig.savefig(destino, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    saida = AQUI / "estudo_caso_sandbox.png"
    desenhar(saida)
    print("Figura:", saida)
