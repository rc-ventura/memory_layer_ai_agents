"""Bases 1 e 2 (com prompt): um módulo está na lista de imports autorizados do prompt de cada papel, por versão?

Pergunta (dossiê do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, §2g e §2h): no prompt da base 1, versões
recentes de quatro papéis tiram o `json` da lista autorizada (OBFCivel, RoteadorCivel, managerAgent, ContestacaoCivel).
O RoteadorCivel é o papel com mais erros de `json` sem import na base 3; se o `json` também saiu da lista dele lá, a
memória "importe json" mandaria fazer um import proibido. A base 2, do mesmo período, responde. A frase do prompt é a do
smolagents: "You can use imports in your code, but only from the following list of modules: [...]".

Lê o JSONL do `extrair_prompts_base2.py` (uma linha por papel e versão do prompt, gravado fora do repositório). Por
papel: quantas versões têm o módulo na lista, quantas não têm, as execuções e os meses das que não têm. Não grava nada.
Imprime só nomes de papel, contagens e meses. Uso, da raiz:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_modulo_na_lista_base2.py --prompts <jsonl> [--modulo json]
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

LISTA = re.compile(r"only from the following list of modules:\s*\[([^\]]*)\]")


def modulos(prompt):
    """Os módulos da lista autorizada do prompt; None se o prompt não tem a frase."""
    m = LISTA.search(prompt or "")
    return {x.strip(" '\"") for x in m.group(1).split(",") if x.strip(" '\"")} if m else None


def contar(linhas, modulo):
    """linhas: dicts do JSONL (role, versao, execucoes, meses, prompt). Uma linha por papel."""
    P = defaultdict(lambda: {"com": 0, "sem": 0, "sem_lista": 0, "execucoes_sem": 0, "meses_sem": set()})
    for r in linhas:
        d, mods = P[r["role"]], modulos(r.get("prompt"))
        if mods is None:
            d["sem_lista"] += 1
        elif modulo in mods:
            d["com"] += 1
        else:
            d["sem"] += 1
            d["execucoes_sem"] += int(r.get("execucoes") or 0)
            d["meses_sem"].update(r.get("meses") or [])
    return [{"papel": p, "versoes_com": d["com"], "versoes_sem": d["sem"], "versoes_sem_lista": d["sem_lista"],
             "execucoes_sem": d["execucoes_sem"], "meses_sem": sorted(d["meses_sem"])} for p, d in sorted(P.items())]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompts", required=True, type=Path, help="o JSONL do extrair_prompts_base2.py")
    p.add_argument("--modulo", default="json", help="o módulo procurado na lista (padrão: json)")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    linhas = [json.loads(l) for l in a.prompts.read_text(encoding="utf-8").splitlines() if l.strip()]
    T = contar(linhas, a.modulo)
    print(f"`{a.modulo}` na lista autorizada do prompt · {len(linhas)} versões em {len(T)} papéis ({a.prompts.name})")
    print(f"{'papel':22} {'versões com':>11} {'sem':>5} {'sem a frase':>11} {'execuções sem':>13}  meses sem")
    for r in T:
        print(f"{r['papel']:22} {r['versoes_com']:>11} {r['versoes_sem']:>5} {r['versoes_sem_lista']:>11} "
              f"{r['execucoes_sem']:>13}  {', '.join(r['meses_sem'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
