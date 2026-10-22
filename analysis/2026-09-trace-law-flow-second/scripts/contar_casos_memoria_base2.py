"""Bases 1 e 2 (trace completo): quantos casos de cada memória do catálogo a base tem, e a evidência de "uma causa só".

Para o fechamento do sandbox (dossiê da base 3, `propostas/U_sandbox/dossie_base3.md`, §2h, 24): o degrau 3 lê até 30
casos por memória numa base com trace inteiro (decisão 8 de 21/10), e a checagem "uma causa só" do degrau 2 é decidida
pelo pesquisador com evidência (decisão 4). Este script responde as duas coisas, por memória, sem ler texto de caso.

A população de uma memória, pelos nomes dela no catálogo (`analysis/registros/memorias.json`, campo `nomes`) e pelas
regras de mensagem do script da mineração do sandbox (`mineracao_U_sandbox.py`: `extrair`, no último trecho da mensagem):
  - `importar`: "The variable `X` is not defined" com X (ou o módulo do apelido: `pd` → `pandas`) na lista;
  - `nao_usar`: "Forbidden function evaluation: 'X'" ou "Forbidden access to dunder attribute: X" com X na lista;
  - `nao_importar`: "Import of/from X is not allowed" ou "No module named 'X'" com a raiz de X na lista;
  - e o papel da memória, se ela tem um. É aproximação da unidade do pipeline (que pode mandar um erro desses para outra
    unidade); a contagem que vale para a memória é a da mineração da base dela.

A evidência de "uma causa só", por memória:
  - nas de `importar` (a C): em quantos erros o mesmo módulo foi importado **antes**, sem erro, na mesma execução e papel.
    No interpretador do smolagents um import vale nos passos seguintes (testado em 22/10, 1.26.0); se rodou antes e o
    nome sumiu, a causa não é esquecer o import, é o estado perdido entre passos — outra causa, outro conserto;
  - nas de `nao_usar` (a E): os erros por nome, e o que o agente faz no passo seguinte do mesmo papel (passo sem erro ou
    com erro) — nomes de usos diferentes (inspecionar um valor × abrir arquivo × executar código) são candidatos a
    causas diferentes.
Imprime só nomes, contagens e meses. Com `--listar <id>`, os exec_id, mês e idx dos casos, para abrir com
`drill_down.py caso` na máquina da base. Uso, da raiz:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_casos_memoria_base2.py --trace <trace> [--id <id> ...]
"""
import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
REGISTRO = RAIZ / "analysis/registros/memorias.json"
PADRAO = ["U_sandbox.C", "U_sandbox.E", "U_sandbox.C.JoogleAnalytics"]


def _regras():
    """As regras de mensagem do script da mineração do sandbox (sem copiar: um lugar só)."""
    arq = RAIZ / "analysis/2026-10-trace-law-flow-third/pipeline/especificas/mineracao_U_sandbox.py"
    spec = spec_from_file_location("mineracao_U_sandbox", arq)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mu = _regras()


def importados(code):
    """Os módulos importados no código (pela raiz), incluindo o apelido: `import pandas as pd` → pandas."""
    raizes = set()
    for m in re.finditer(r"(?m)^\s*import\s+([\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)", code or ""):
        raizes.update(p.split()[0].split(".")[0] for p in m.group(1).split(","))
    raizes.update(m.group(1).split(".")[0] for m in re.finditer(r"(?m)^\s*from\s+([\w.]+)\s+import\b", code or ""))
    return raizes


def casa(entrada, tipo, nome):
    """O erro (tipo, nome) é da memória, pelos nomes dela?"""
    n = entrada.get("nomes") or {}
    if tipo == "modulo_sem_import":
        return mu.modulo(nome) in n.get("importar", [])
    if tipo in ("funcao_proibida", "atributo_dunder"):
        return nome in n.get("nao_usar", [])
    if tipo in ("import_bloqueado", "modulo_ausente"):
        return str(nome).split(".")[0] in n.get("nao_importar", [])
    return False


def medir(S, entradas):
    """S: um ActionStep por linha (exec_id, agente, role, idx, mes, code, err_msg) → {id: resultado} e {id: casos}."""
    S = S.sort_values(["exec_id", "agente", "role", "idx"]).reset_index(drop=True)
    chave = ["exec_id", "agente", "role"]
    out, casos = {}, {}
    erros = S[S.err_msg.fillna("").ne("")]
    lidos = [(i, *mu.extrair(m)) for i, m in zip(erros.index, erros.err_msg)]
    for e in entradas:
        papel = (e.get("scope") or {}).get("role")
        sel = [(i, t, n) for i, t, n in lidos if casa(e, t, n) and (not papel or S.at[i, "role"] == papel)]
        r = {"erros": len(sel), "execucoes": len({tuple(S.loc[i, chave]) for i, _, _ in sel}),
             "meses": sorted({S.at[i, "mes"] for i, _, _ in sel}), "por_nome": {}}
        antes = 0
        seguinte = {"sem_erro": 0, "com_erro": 0, "sem_passo": 0}
        for i, t, n in sel:
            r["por_nome"][n] = r["por_nome"].get(n, 0) + 1
            mesma = S[(S.exec_id == S.at[i, "exec_id"]) & (S.agente == S.at[i, "agente"]) & (S.role == S.at[i, "role"])]
            if t == "modulo_sem_import":
                ant = mesma[(mesma.idx < S.at[i, "idx"]) & mesma.err_msg.fillna("").eq("")]
                antes += any(mu.modulo(n) in importados(c) for c in ant.code)
            prox = mesma[mesma.idx > S.at[i, "idx"]].head(1)
            seguinte["sem_passo" if prox.empty else ("com_erro" if str(prox.err_msg.iloc[0] or "") else "sem_erro")] += 1
        if e.get("nomes", {}).get("importar"):
            r["importado_antes_sem_erro"] = antes
        r["passo_seguinte"] = seguinte
        r["por_nome"] = dict(sorted(r["por_nome"].items(), key=lambda kv: (-kv[1], kv[0])))
        out[e["id"]] = r
        casos[e["id"]] = [(S.at[i, "exec_id"], S.at[i, "mes"], int(S.at[i, "idx"]), S.at[i, "role"]) for i, _, _ in sel]
    return out, casos


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru (CSV ou parquet)")
    p.add_argument("--id", nargs="*", default=PADRAO, help="as memórias do catálogo")
    p.add_argument("--registro", type=Path, default=REGISTRO)
    p.add_argument("--listar", metavar="ID", help="lista exec_id/mês/idx/papel dos casos dessa memória")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    reg = json.loads(a.registro.read_text(encoding="utf-8"))
    entradas = [e for e in reg["itens"] if e["id"] in a.id]
    from contar_primeiro_passo_nome_base2 import bp, explodir   # o leitor do trace (importa o pipeline da base 1)
    bp.TRACE = str(a.trace)
    out, casos = medir(explodir(bp.carregar_trace()), entradas)
    if a.listar:
        for c in casos.get(a.listar, []):
            print(f"  exec_id={c[0]}  mês={c[1]}  idx={c[2]}  papel={c[3]}")
        print(f"{len(casos.get(a.listar, []))} casos de {a.listar}. Caso inteiro (na pasta pipeline/ da base): "
              f"python drill_down.py caso <exec_id> <papel>")
        return 0
    for ident, r in out.items():
        print(f"{ident}: {r['erros']} erros · {r['execucoes']} execuções · {', '.join(r['meses']) or '—'}")
        print(f"  por nome: {r['por_nome']}")
        if "importado_antes_sem_erro" in r:
            print(f"  o módulo foi importado antes, sem erro, na mesma execução e papel: {r['importado_antes_sem_erro']}")
        print(f"  o passo seguinte do papel: {r['passo_seguinte']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
