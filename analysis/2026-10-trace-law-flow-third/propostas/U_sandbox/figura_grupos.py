"""Os grupos de memória do `U_sandbox` na base 3 (as duas figuras principais do estudo de caso, aprovadas pelo Rafael em
26/10): (1) a rosca — em que grupo cada erro foi decidido, e o que acontece com o grupo; (2) as barras — erros,
execuções, papéis e meses de cada grupo.

Lê o catálogo de memórias (`analysis/registros/memorias.json`, as entradas do `U_sandbox` na rodada atual da base 3).
Duas partes não estão no catálogo e vêm do dossiê (`dossie_base3.md`, §2h item 11): a parte em aberto (37 erros) e os
erros sem nome (5). Quais memórias vão para o agente: §2h item 27. Só contagens. Confere que os grupos fecham nos 1.100
erros da unidade.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/figura_grupos.py
"""
import json
import math
from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "pipeline"))
from paleta import BASE, COR_ERRO, INK, INK2, MUTED   # noqa: E402

CATALOGO = AQUI.parents[2] / "registros" / "memorias.json"
RODADA = "99e032ad3a8528d8"
TOTAL = 1100                                   # a unidade na rodada 99e032ad (§2h item 11)
FORA_DO_CATALOGO = {"F": 37, "sem nome": 5}    # §2h item 11
VAI_PARA_O_AGENTE = {"U_sandbox.C", "U_sandbox.E", "U_sandbox.C.JoogleAnalytics"}   # §2h item 27

ROSA = COR_ERRO["Ambiente & sandbox"]          # a cor da família, a mesma da genealogia
DECISAO = {"vai para o agente": ROSA, "catálogo, monitorada": BASE, "em aberto": "#e8e6df", "—": "white"}
HACHURA = {"—": "////"}   # "outros" não tem decisão: branco com hachura, para não se confundir com "em aberto"

# (grupo, erros que entram, decisão, regra que põe a memória no grupo)
GRUPOS = [("esqueceu o import", "json, re, datetime", "vai para o agente", lambda i: i == "U_sandbox.C"),
          ("inspecionou com função barrada", "__name__, repr, dir…", "vai para o agente", lambda i: i == "U_sandbox.E"),
          ("esqueceu o import pandas (JoogleAnalytics)", "pd", "vai para o agente",
           lambda i: i == "U_sandbox.C.JoogleAnalytics"),
          ("importou a ferramenta em vez de chamar", "python_interpreter, tools…", "catálogo, monitorada",
           lambda i: i.startswith("U_sandbox.B.")),
          ("import fora da lista autorizada, por papel", "ast, copy, typing…", "catálogo, monitorada",
           lambda i: i.startswith("U_sandbox.D.")),
          ("verificação com globals/eval que sobrou", "globals, eval, locals, vars", "em aberto", None),
          ("outros", "sem nome 5; pandas no CalculoTrabalhista 2", "—",
           lambda i: i == "U_sandbox.C.CalculoTrabalhista")]


def _n(v):
    return f"{v:,}".replace(",", ".")


def _papeis(m):
    if (m.get("scope") or {}).get("role"):
        return {m["scope"]["role"]}
    achado = re.search(r"em (\d+) papel", m.get("description", ""))
    return int(achado.group(1)) if achado else None


def grupos():
    itens = [m for m in json.loads(CATALOGO.read_text(encoding="utf-8"))["itens"]
             if m["unidade"] == "U_sandbox" and m.get("base") == "base3" and m.get("rodada_id", "").startswith(RODADA)]
    linhas, usados = [], set()
    for nome, entram, decisao, regra in GRUPOS:
        ms = [m for m in itens if regra and regra(m["id"])]
        usados |= {m["id"] for m in ms}
        erros = sum(m["occurrences"]["erros"] for m in ms)
        execs = sum(m["occurrences"]["execucoes"] for m in ms) if ms else None
        meses = set().union(*[set(m["occurrences"]["meses"]) for m in ms]) if ms else set()
        pap = [_papeis(m) for m in ms]
        papeis = (len(set().union(*pap)) if pap and all(isinstance(p, set) for p in pap)
                  else (pap[0] if len(pap) == 1 else None))
        if nome.startswith("verificação"):
            erros += FORA_DO_CATALOGO["F"]
        if nome == "outros":
            erros += FORA_DO_CATALOGO["sem nome"]
            execs = papeis = None   # os sem nome não têm execuções nem papéis no catálogo
            meses = set()
        linhas.append(dict(grupo=nome, entram=entram, decisao=decisao, erros=erros, execucoes=execs, papeis=papeis,
                           meses=len(meses) or None, memorias=len(ms)))
    sobra = {m["id"] for m in itens} - usados
    if sobra:
        raise SystemExit("memórias do catálogo sem grupo: " + ", ".join(sorted(sobra)))
    if sum(l["erros"] for l in linhas) != TOTAL:
        raise SystemExit(f"os grupos somam {sum(l['erros'] for l in linhas)}, e a unidade tem {TOTAL}")
    if {m["id"] for m in itens if any(m["id"] == v for v in VAI_PARA_O_AGENTE)} != VAI_PARA_O_AGENTE:
        raise SystemExit("uma memória que vai para o agente não está no catálogo")
    return linhas


def _legenda():
    return [plt.Rectangle((0, 0), 1, 1, facecolor=c, hatch=HACHURA.get(d), edgecolor=MUTED if d in HACHURA else c)
            for d, c in DECISAO.items()]


def _rotulos_legenda():
    return [d if d != "—" else "outros (sem decisão)" for d in DECISAO]


def rosca(linhas, destino):
    """1 · Em que grupo de memória cada erro foi decidido, e o que acontece com o grupo."""
    fig, ax = plt.subplots(figsize=(12, 7.5))
    erros = [l["erros"] for l in linhas]
    # gira para as fatias pequenas (o fim da volta) ficarem à esquerda, no meio, onde os rótulos têm espaço
    pequenas = sum(erros[3:]) / TOTAL * 360
    fatias, _ = ax.pie(erros, colors=[DECISAO[l["decisao"]] for l in linhas], startangle=180 + pequenas / 2,
                       counterclock=False, wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2))
    for f, l in zip(fatias, linhas):
        if l["decisao"] in HACHURA:
            f.set_hatch(HACHURA[l["decisao"]])
            f.set_edgecolor(MUTED)
    pos = []
    for f, l in zip(fatias, linhas):
        ang = math.radians((f.theta2 + f.theta1) / 2)
        pos.append([math.cos(ang), math.sin(ang), 1.15 * math.sin(ang)])
    for lado in (1, -1):   # espalha os rótulos de cada lado, de cima para baixo, com uma distância mínima
        idx = sorted((i for i, p in enumerate(pos) if (p[0] >= 0) == (lado == 1)), key=lambda i: -pos[i][2])
        for a, b in zip(idx, idx[1:]):
            pos[b][2] = min(pos[b][2], pos[a][2] - 0.24)
    for (x, y, y_rot), l in zip(pos, linhas):
        ax.annotate(f"{l['grupo']} · {_n(l['erros'])} ({100 * l['erros'] / TOTAL:.0f}%)\n{l['entram']} · {l['decisao']}",
                    xy=(0.81 * x, 0.81 * y), xytext=(1.3 if x >= 0 else -1.3, y_rot),
                    ha="left" if x >= 0 else "right", va="center", fontsize=9, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7, shrinkA=0, shrinkB=0))
    agente = sum(l["erros"] for l in linhas if l["decisao"] == "vai para o agente")
    ax.text(0, 0.06, _n(TOTAL), ha="center", va="center", fontsize=22, fontweight="bold", color=INK)
    ax.text(0, -0.14, "erros no sandbox", ha="center", va="center", fontsize=10, color=INK2)
    ax.set_title(f"O que foi decidido para os {_n(TOTAL)} erros do sandbox: 3 grupos vão para o agente e cobrem "
                 f"{_n(agente)} ({100 * agente / TOTAL:.0f}%)", loc="left", fontsize=12, color=INK, pad=18)
    ax.legend(handles=_legenda(), labels=_rotulos_legenda(), loc="lower center", bbox_to_anchor=(0.5, -0.12),
              ncol=4, frameon=False, fontsize=9)
    ax.set_aspect("equal")
    fig.savefig(destino, dpi=160, bbox_inches="tight")
    plt.close(fig)


def barras(linhas, destino):
    """2 · Os números de cada grupo: erros (a barra) e, ao lado, execuções, papéis e meses."""
    fig, ax = plt.subplots(figsize=(13, 0.62 * len(linhas) + 2))
    for i, l in enumerate(linhas):
        ax.barh(i, l["erros"], color=DECISAO[l["decisao"]], height=0.6, hatch=HACHURA.get(l["decisao"]),
                edgecolor=MUTED if l["decisao"] in HACHURA else "none")
        partes = [f"{_n(l['erros'])} erros"]
        if l["execucoes"] is not None:
            partes.append(f"{_n(l['execucoes'])} execuções")
        if l["papeis"] is not None:
            partes.append(f"{l['papeis']} {'papel' if l['papeis'] == 1 else 'papéis'}")
        if l["meses"] is not None:
            partes.append(f"{l['meses']} {'mês' if l['meses'] == 1 else 'meses'}")
        ax.text(l["erros"] + 6, i, "  ·  ".join(partes), va="center", fontsize=9, color=INK2)
    ax.set_yticks(range(len(linhas)), [f"{l['grupo']}\n({l['entram']})" for l in linhas], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max(l["erros"] for l in linhas) * 1.6)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _n(int(v))))
    ax.set_xlabel("erros estruturados")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_title(f"Os números de cada grupo de memória do sandbox ({_n(TOTAL)} erros)", loc="left", fontsize=11,
                 color=INK)
    ax.legend(handles=_legenda(), labels=_rotulos_legenda(), loc="lower right", frameon=False, fontsize=9)
    fig.text(0.01, -0.02, "Execuções: nos grupos com mais de uma memória, a soma das memórias. Sem execuções, papéis e "
             "meses: a parte em aberto (fora do catálogo) e os erros sem nome.", fontsize=8, color=MUTED)
    fig.savefig(destino, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    L = grupos()
    for l in L:
        print(l)
    rosca(L, AQUI / "grupos_rosca.png")
    barras(L, AQUI / "grupos_barras.png")
    print("Figuras:", AQUI / "grupos_rosca.png", AQUI / "grupos_barras.png")
