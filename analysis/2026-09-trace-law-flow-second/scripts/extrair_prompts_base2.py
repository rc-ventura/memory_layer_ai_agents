"""Bases 1 e 2 (trace completo): o prompt de cada papel, uma linha por versão, para o degrau 2 da validação das memórias.

O `conferir_memorias.py` (kit, skill mineracao-candidata) confere cada memória contra o prompt do papel (doc 17 da base
1, "Degrau 2 · as cinco checagens"). O kit não lê trace: este script lê, com o leitor da base 1 (o mesmo do
`contar_ferramentas_prompt_base2.py`), e grava um JSONL com uma linha por (papel, versão do prompt):
    {"role", "versao" (hash do prompt, 10), "meses", "execucoes", "prompt"}
O prompt é o do primeiro ActionStep de cada execução e papel (o system prompt, `model_input_messages[0]`).

O arquivo tem o texto do prompt: grava só fora do repositório (como o --evidencia do `contar_primeiro_passo_nome_base2.py`)
e não sai da máquina; o que sai é o resultado do `conferir_memorias.py` (contagens, nomes e hashes). Imprime só papel,
versão, meses e contagens. Uso, da raiz:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/extrair_prompts_base2.py --trace <trace> --saida <fora do repo>/prompts.jsonl
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contar_primeiro_passo_nome_base2 import REPO, bp, explodir  # noqa: E402


def versoes(S):
    """S: um ActionStep por linha (exec_id, agente, role, idx, mes, sysprompt) → uma linha por (papel, versão do prompt)."""
    prim = S[S.idx.eq(0) & S.sysprompt.fillna("").ne("")].copy()
    prim["versao"] = [hashlib.sha256(t.encode("utf-8")).hexdigest()[:10] for t in prim.sysprompt]
    saida = []
    for (role, versao), g in prim.groupby(["role", "versao"], sort=True):
        saida.append({"role": role, "versao": versao, "meses": sorted(set(g.mes)),
                      "execucoes": int(g[["exec_id", "agente"]].drop_duplicates().shape[0]),
                      "prompt": g.sysprompt.iloc[0]})
    return saida


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru (CSV ou parquet)")
    p.add_argument("--saida", required=True, type=Path, help="o JSONL, FORA do repositório (tem o texto do prompt)")
    a = p.parse_args(argv)
    if a.saida.resolve().is_relative_to(REPO.resolve()):
        p.error("--saida deve ficar fora do repositório: o arquivo tem o texto do prompt")
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    bp.TRACE = str(a.trace)
    linhas = versoes(explodir(bp.carregar_trace()))
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    with open(a.saida, "w", encoding="utf-8") as fh:
        for r in linhas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    for r in linhas:
        print(f"  {r['role']} · versão {r['versao']} · {r['execucoes']} execuções · {', '.join(r['meses'])}")
    print(f"{len(linhas)} versões de prompt em {len({r['role'] for r in linhas})} papéis → {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
