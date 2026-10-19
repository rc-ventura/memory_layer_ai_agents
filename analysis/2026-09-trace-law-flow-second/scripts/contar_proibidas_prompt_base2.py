"""Base 2 (trace completo): a parte E do inventário do sandbox (funções e atributos proibidos) vem do prompt?

Hipótese a testar (dossiê do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, §2b; b3 #12, decisão de 19/10):
os 523 erros da parte E na base 3 estão concentrados no ContestacaoCivel (`__name__` 172 de 182, `eval` 46 de 49, `repr`
54 de 98). Se, como na verificação de existência (Ajuste 21), o prompt desse papel pede algo que o agente cumpre com uma
função barrada (por exemplo, "registre as seções com falha" → `type(e).__name__`), é sinal de harness; se não, é uso
espontâneo e a lição é de memória. A base 3 não tem o prompt; a base 2 tem.

  A. os erros da parte E por papel × mês × nome;
  B. o uso da linha que falhou (a regra do `contar_proibidas_linha.py` da base 3), por grupo (ContestacaoCivel ×
     outros) × nome;
  C. o teste: por papel × versão do trecho do prompt (hash das linhas com os termos abaixo) → execuções, com erro da
     parte E, e se o prompt menciona cada termo;
  D. as linhas do prompt do ContestacaoCivel com os termos (sem repetição; números longos → '#'), com quantas
     execuções têm cada uma — é o que diz se o prompt pede o que o agente faz;
  E. o nome barrado está escrito no prompt da execução (o agente pode ter copiado), por grupo × nome.

Termos: `__name__`, `type(`, `repr`, `eval`, `exec(`, `traceback`, `except Exception`, `str(e)`, e a instrução de
registrar falhas (`falha`). Usa o leitor do `contar_primeiro_passo_nome_base2.py`, a população da auditoria da base 3
(`populacao_sandbox`, tipos `funcao_proibida` e `atributo_dunder`) e a regra do uso da base 3 (o método é o mesmo nas
bases). Não grava nada. Imprime contagens, nomes de papel, meses, hashes e linhas do prompt (texto técnico, não do
caso). Uso, da raiz, na máquina da base 2:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_proibidas_prompt_base2.py --trace <trace da base 2>
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contar_primeiro_passo_nome_base2 import bp, explodir  # noqa: E402
sys.path.insert(0, str(AQUI.parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"))
from contar_proibidas_linha import PARTE_E, LINHA_FALHA, extrair_sandbox, grupo, populacao_sandbox, uso_proibida  # noqa: E402

TERMOS = {"__name__": re.compile(r"__name__"), "type(": re.compile(r"\btype\s*\("), "repr": re.compile(r"\brepr\b|!r\b"),
          "eval": re.compile(r"\beval\s*\(|literal_eval"), "exec(": re.compile(r"\bexec\s*\("),
          "traceback": re.compile(r"traceback"), "except Exception": re.compile(r"except\s+Exception"),
          "str(e)": re.compile(r"\bstr\s*\(\s*e\s*\)"), "falha": re.compile(r"(?i)falh(?:a|as|ou|ar)\b")}
NO_PROMPT = {"__name__": r"__name__", "__class__": r"__class__", "repr": r"\brepr\s*\(", "eval": r"\beval\s*\(",
             "exec": r"\bexec\s*\(", "dir": r"\bdir\s*\(", "globals": r"globals\s*\(", "locals": r"locals\s*\(",
             "vars": r"\bvars\s*\(", "open": r"\bopen\s*\(", "__import__": r"__import__"}


def trecho(prompt):
    """As linhas do prompt com os termos, o hash delas (a versão do trecho) e quais termos aparecem."""
    linhas = sorted({l.strip() for l in str(prompt).splitlines() if any(rx.search(l) for rx in TERMOS.values())})
    h = hashlib.sha256("\n".join(linhas).encode("utf-8")).hexdigest()[:10] if linhas else "(nenhuma)"
    return h, linhas, {t: bool(rx.search(str(prompt))) for t, rx in TERMOS.items()}


def medir(S):
    """S: um ActionStep por linha (exec_id, agente, role, idx, mes, err_type, err_msg, code, sysprompt)."""
    S = S.copy()
    regs = []
    for r in S[S.err_type.notna()].itertuples():
        if not populacao_sandbox(r.err_msg, r.code):
            continue
        tipo, nome = extrair_sandbox(r.err_msg)
        if tipo not in PARTE_E:
            continue
        m = LINHA_FALHA.search(r.err_msg)
        regs.append({"exec_id": r.exec_id, "agente": r.agente, "role": r.role, "mes": r.mes, "nome": nome,
                     "grupo": grupo(r.role), "uso": uso_proibida(nome, m.group(1) if m else "", r.code),
                     "no_prompt": bool(re.search(NO_PROMPT.get(nome, re.escape(nome)), r.sysprompt or ""))})
    R = pd.DataFrame(regs, columns=["exec_id", "agente", "role", "mes", "nome", "grupo", "uso", "no_prompt"])
    A = R.groupby(["role", "mes", "nome"]).size().rename("erros").reset_index()
    B = R.groupby(["grupo", "nome", "uso"]).size().rename("erros").reset_index().sort_values(["grupo", "erros"],
                                                                                              ascending=[True, False])
    prim = S[S.idx.eq(0)][["exec_id", "agente", "role", "mes", "sysprompt"]].copy()
    tr = [trecho(p) for p in prim.sysprompt]
    prim["versao_trecho"] = [t[0] for t in tr]
    for t in TERMOS:
        prim[f"menciona_{t}"] = [x[2][t] for x in tr]
    com_e = R.groupby(["exec_id", "agente", "role"]).size().rename("erros_parte_e").reset_index()
    ex = prim.merge(com_e, on=["exec_id", "agente", "role"], how="left").fillna({"erros_parte_e": 0})
    papeis = sorted(set(R.role))
    C = (ex[ex.role.isin(papeis)].groupby(["role", "versao_trecho"] + [f"menciona_{t}" for t in TERMOS])
         .agg(execucoes=("exec_id", "size"), com_erro_parte_e=("erros_parte_e", lambda s: int((s > 0).sum())),
              erros_parte_e=("erros_parte_e", "sum"))
         .reset_index().sort_values(["role", "execucoes"], ascending=[True, False]))
    linhas_cc = {}
    for (h, linhas, _), role in zip(tr, prim.role):
        if grupo(role) == "ContestacaoCivel":
            for l in linhas:
                linhas_cc[l] = linhas_cc.get(l, 0) + 1
    D = pd.DataFrame(sorted(linhas_cc.items(), key=lambda kv: -kv[1]), columns=["linha", "execucoes"])
    D["linha"] = D.linha.map(lambda l: re.sub(r"\d{6,}", "#", l)[:200])
    E = R.groupby(["grupo", "nome"]).agg(erros=("uso", "size"), nome_escrito_no_prompt=("no_prompt", "sum")).reset_index()
    return {"total": len(R), "A": A, "B": B, "C": C, "D": D, "E": E}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru da base 2 (CSV ou parquet)")
    args = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    bp.TRACE = str(args.trace)
    T = medir(explodir(bp.carregar_trace()))
    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 200)
    print(f"parte E: {T['total']} erros")
    print("\nA · papel × mês × nome")
    print(T["A"].to_string(index=False) if len(T["A"]) else "  nenhum")
    print("\nB · o uso da linha que falhou, por grupo × nome")
    print(T["B"].to_string(index=False) if len(T["B"]) else "  nenhum")
    print("\nC · o teste: papel × versão do trecho do prompt → execuções, com erro da parte E (menciona_* = o prompt tem o termo)")
    print(T["C"].to_string(index=False) if len(T["C"]) else "  nenhum papel com erro da parte E")
    print("\nD · as linhas do prompt do ContestacaoCivel com os termos (execuções com a linha)")
    print(T["D"].head(40).to_string(index=False) if len(T["D"]) else "  nenhuma")
    print("\nE · o nome barrado está escrito no prompt da execução?")
    print(T["E"].to_string(index=False) if len(T["E"]) else "  nenhum")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
