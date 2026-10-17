"""Auditoria independente da mineração de uma candidata na base 3 (procedimento 06, passo 7; racional 07, passo 7).

    python audit_candidata_base3.py <unidade> --fonte <parquet> --json <arquivo>

Uma segunda implementação, escrita a partir do racional da lição (`propostas/<u>/racional.md`), **sem importar o
pipeline nem o script específico**: lê o parquet cru com o pyarrow, aplica a definição da população em prosa e as
regras da lição, e grava as medidas num JSON. Quem compara com a mineração é o `minerar.py` (passo 7). "Re-rodar não
é verificar": nada aqui vem do `base_pipeline.py`.

Cada erro é identificado pela chave da fonte (execução, agente, papel, posição do passo), a mesma que o `casos.csv`
da rodada tem. Imprime só contagens. Sai com 2 se a lição não tem auditoria escrita.
"""
import argparse
import builtins
from collections import Counter, defaultdict
import json
import re
import sys

import pyarrow.parquet as pq

COLUNAS = ["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos", "mes_execucao", "structured_error", "error_type",
           "error_message"]


# ── U_sandbox (racional: propostas/U_sandbox/racional.md) ──────────────────────────────────────────────────────────
MODULOS = {"json", "pd", "np", "re", "os", "math", "datetime"}
# "os sinais que o pipeline decide antes" (racional, passo 1)
ANTES = ["SyntaxError", "Code parsing failed", "IndentationError", "Could not index", "has no attribute",
         "JSONDecode", "does not support multiple positional", "object is not an iterator", "Reached max steps",
         "AgentMaxStepsError", "exceeded the maximum execution time"]
REGRAS_SANDBOX = [  # (tipo, padrão no último trecho) — racional, passo 4, na ordem
    ("funcao_proibida", r"Forbidden function evaluation: '([^']+)'"),
    ("import_bloqueado", r"Import (?:of|from) ([\w.]+) is not allowed"),
    ("modulo_ausente", r"No module named '([^']+)'"),
    ("atributo_dunder", r"Forbidden access to dunder attribute: (\w+)"),
    ("modulo_sem_import", r"The variable `(\w+)` is not defined"),
]
AUTORIZADOS = re.compile(r"Authorized imports are: \[([^\]]*)\]")


def populacao_sandbox(msg):
    if any(s in msg for s in ANTES):
        return False
    v = re.search(r"The variable `(\w+)` is not defined", msg)
    if v and v.group(1) in MODULOS:
        return True
    f = re.search(r"Forbidden function evaluation: '([^']+)'", msg)
    if f:
        return hasattr(builtins, f.group(1))
    return "Import of" in msg or "Import from" in msg or "ModuleNotFound" in msg or "Forbidden" in msg


def extrair_sandbox(msg):
    trecho = msg.rsplit("due to:", 1)[-1]
    for tipo, rx in REGRAS_SANDBOX:
        x = re.search(rx, trecho)
        if x:
            return tipo, x.group(1)
    return "sem_nome", (trecho.strip().split(":")[0].split()[0] if trecho.strip() else "")


def autorizados(msg):
    a = AUTORIZADOS.search(msg.rsplit("due to:", 1)[-1])
    if not a:
        return None
    return ", ".join(sorted(x.strip().strip("'\"") for x in a.group(1).split(",") if x.strip()))


LICOES = {"U_sandbox": (populacao_sandbox, extrair_sandbox, autorizados)}


def auditar(unidade, fonte):
    if unidade not in LICOES:
        sys.exit(2)
    pop, extrair, listas = LICOES[unidade]
    linhas = pq.read_table(fonte, columns=COLUNAS).to_pylist()
    erros = []
    for r in linhas:
        if not (r["structured_error"] == 1 and (r["error_type"] or "").strip()):
            continue
        msg = r["error_message"] or ""
        if not pop(msg):
            continue
        tipo, nome = extrair(msg)
        erros.append({"chave": [str(r["cod_idef_exeo"]), str(r["cod_idef_aget"]), str(r["papel"]), int(r["step_pos"])],
                      "papel": str(r["papel"]), "mes": str(r["mes_execucao"]), "tipo": tipo, "nome": nome,
                      "lista": listas(msg)})
    por_nome = defaultdict(lambda: {"erros": 0, "execucoes": set(), "papeis": set(), "meses": set()})
    for e in erros:
        if e["tipo"] == "sem_nome":
            continue
        d = por_nome[f"{e['tipo']}|{e['nome']}"]
        d["erros"] += 1; d["execucoes"].add(e["chave"][0]); d["papeis"].add(e["papel"]); d["meses"].add(e["mes"])
    com_nome = sum(e["tipo"] != "sem_nome" for e in erros)
    return {
        "unidade": unidade,
        "populacao": {"erros": len(erros), "execucoes": len({e["chave"][0] for e in erros}),
                      "papeis": len({e["papel"] for e in erros}), "meses": len({e["mes"] for e in erros}),
                      "erros_por_papel": dict(sorted(Counter(e["papel"] for e in erros).items())),
                      "chaves": sorted(e["chave"] for e in erros)},
        "cobertura": {"com_nome": com_nome, "erros": len(erros),
                      "sem_nome_por_tipo": dict(sorted(Counter(e["nome"] for e in erros if e["tipo"] == "sem_nome").items()))},
        "inventario": {k: {"erros": d["erros"], "execucoes": len(d["execucoes"]), "papeis": len(d["papeis"]),
                           "meses": len(d["meses"])} for k, d in sorted(por_nome.items())},
        "listas_autorizadas": dict(sorted(Counter(e["lista"] for e in erros if e["lista"]).items())),
        # uma linha por erro, só para o diagnóstico de uma divergência (o encontro não compara este bloco)
        "linhas": [{"chave": e["chave"], "mes": e["mes"], "tipo": e["tipo"], "nome": e["nome"]}
                   for e in sorted(erros, key=lambda e: e["chave"])],
    }


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):   # terminal do Windows (cp1252) não recusa acento nem o traço do resumo
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("unidade"); p.add_argument("--fonte", required=True); p.add_argument("--json", required=True)
    a = p.parse_args(argv)
    if a.unidade not in LICOES:
        print(f"sem auditoria escrita para {a.unidade} (lições com auditoria: {', '.join(LICOES)})")
        return 2
    med = auditar(a.unidade, a.fonte)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(med, fh, ensure_ascii=False, indent=2)
    c = med["cobertura"]
    print(f"auditoria {a.unidade}: {med['populacao']['erros']} erros · {med['populacao']['execucoes']} execuções · "
          f"{med['populacao']['papeis']} papéis · {med['populacao']['meses']} meses · com nome {c['com_nome']} · "
          f"{len(med['inventario'])} nomes · {len(med['listas_autorizadas'])} listas autorizadas → {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
