"""Bases 1 e 2 (trace completo): o que o interpretador mostrou de cada papel, para o degrau 2 da validação das memórias.

O `conferir_memorias.py` (kit, skill mineracao-candidata) confere se o que uma memória manda importar é aceito no papel.
A lista do prompt não serve para isso: na mesma execução, o prompt não lista o `json` e o `import json` roda (531 de 531
nas bases 1 e 2; dossiê do sandbox na base 3, §2h, 18–21; decisão do Rafael, 21/10). Este script grava, por papel, as
duas evidências do interpretador:
  - `listas`: as listas da mensagem de erro "Authorized imports are: [...]" (o último trecho da mensagem, depois do
    último "due to:"), cada uma com os meses e o número de erros em que aparece;
  - `importados`: os módulos de `import X` / `from X import` (pela raiz, antes do ponto) num ActionStep sem erro — o
    import rodou —, com o número de passos e os meses.
Formato (o do `--ambiente` do kit): {"fonte": {...}, "papeis": {"<papel>": {"listas": [...], "importados": {...}}}}.
Só nomes de papel e de módulo, meses e contagens: pode ficar no repositório. Uso, da raiz:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/extrair_ambiente_base2.py --trace <trace> --saida <ambiente.json>
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import sys

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

AUTORIZADOS = re.compile(r"Authorized imports are: \[([^\]]*)\]")
IMPORT = re.compile(r"(?m)^\s*import\s+([\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)")
FROM = re.compile(r"(?m)^\s*from\s+([\w.]+)\s+import\b")


def lista_da_mensagem(msg):
    a = AUTORIZADOS.search(str(msg or "").rsplit("due to:", 1)[-1])
    if not a:
        return None
    return tuple(sorted(x.strip().strip("'\"") for x in a.group(1).split(",") if x.strip()))


def modulos_importados(code):
    """As raízes dos módulos importados no código (`import a.b as c, d` → a, d; `from e.f import g` → e)."""
    raizes = set()
    for m in IMPORT.finditer(code or ""):
        for parte in m.group(1).split(","):
            raizes.add(parte.split()[0].split(".")[0])
    raizes.update(m.group(1).split(".")[0] for m in FROM.finditer(code or ""))
    return raizes


def ambiente(S):
    """S: um ActionStep por linha (role, mes, code, err_msg) → {papel: {"listas", "importados"}}."""
    papeis = {}
    for r in S.itertuples(index=False):
        p = papeis.setdefault(r.role, {"listas": {}, "importados": {}})
        lista = lista_da_mensagem(r.err_msg)
        if lista is not None:
            x = p["listas"].setdefault(lista, {"meses": set(), "erros": 0})
            x["meses"].add(r.mes)
            x["erros"] += 1
        if not str(r.err_msg or ""):
            for mod in modulos_importados(r.code):
                x = p["importados"].setdefault(mod, {"meses": set(), "passos": 0})
                x["meses"].add(r.mes)
                x["passos"] += 1
    return {papel: {"listas": [{"modulos": list(k), "meses": sorted(v["meses"]), "erros": v["erros"]}
                               for k, v in sorted(d["listas"].items())],
                    "importados": {m: {"passos": v["passos"], "meses": sorted(v["meses"])}
                                   for m, v in sorted(d["importados"].items())}}
            for papel, d in sorted(papeis.items(), key=lambda kv: str(kv[0]))
            if d["listas"] or d["importados"]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru (CSV ou parquet)")
    p.add_argument("--saida", required=True, type=Path)
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    from contar_primeiro_passo_nome_base2 import bp, explodir   # o leitor do trace (importa o pipeline da base 1)
    bp.TRACE = str(a.trace)
    papeis = ambiente(explodir(bp.carregar_trace()))
    doc = {"fonte": {"trace": a.trace.name, "gerado_em": datetime.date.today().isoformat(),
                     "script": "extrair_ambiente_base2.py"}, "papeis": papeis}
    a.saida.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{'papel':22} {'listas':>6} {'módulos importados sem erro'}")
    for papel, d in papeis.items():
        print(f"{str(papel):22} {len(d['listas']):>6} {', '.join(d['importados'])}")
    print(f"{len(papeis)} papéis → {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
