"""Base 2 (trace completo): a introspecção proibida (`globals`, `locals`…) vem de uma instrução do prompt?

Hipótese (dossiê do inventário do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, parte A): na base 3, 2.347
dos 2.352 erros de `globals` são do ContestacaoCivel, 1.592 em julho e 754 em agosto de 2026; no mesmo papel, a
verificação por `try/except NameError` tem 95 erros em julho e 5.667 em agosto. A leitura: a mesma instrução do prompt
("verifique se a variável existe antes de chamar a ferramenta"), cumprida com `'x' in globals()` em julho e com
`try/except NameError` em agosto, quando o prompt passou a proibir `globals()`/`locals()` (§7.9 do relatório da base 3).

O teste: por papel × mês × versão do trecho do prompt que fala da verificação, quantas execuções têm erro de
introspecção, quantas têm o erro do `try/except` e quantas nenhum. Se a hipótese vale, os erros de introspecção ficam
numa versão do trecho que manda verificar e não proíbe `globals()`, e somem nas versões sem a instrução.

  A. os erros de introspecção (função proibida `globals`, `locals`, `vars`, `dir`) por papel e mês;
  B. o trecho do prompt de cada execução (primeiro ActionStep do papel): tem a instrução de verificar se a variável
     existe ("VERIFIQUE se a variável… já está preenchida em memória… PULE a chamada")? Menciona `NameError`?
     `globals()`? `locals()`? A versão do trecho = hash das linhas do prompt com esses termos (parte do modelo de
     prompt, não do caso);
  C. a tabela do teste: papel × mês × versão do trecho → execuções, com introspecção, com try/except, com nenhum;
  D. a linha que falhou nos erros de introspecção: verificação de existência, atribuição dinâmica, leitura por nome ou
     outro uso (a mesma regra do `contar_introspeccao_linha.py` da base 3);
  E. como o primeiro passo verificou, por versão do trecho do prompt e com/sem erro: com introspecção, com `try/except
     NameError`, com `try/except` de outro tipo, ou não verificou (regex no código do passo — uma pista);
  F. em TODOS os papéis: quantas execuções têm, no prompt, a instrução de verificar a variável, e quantas verificaram
     no primeiro passo (com introspecção ou `try/except`). Responde se a verificação fora do ContestacaoCivel é
     instruída pelo prompt ou espontânea.

Usa o leitor do `contar_primeiro_passo_nome_base2.py` e as funções do pipeline da base 1 (o método é o mesmo nas duas
bases). Não grava nada. Imprime só contagens, nomes de papel, meses e hashes. Uso, da raiz, na máquina da base 2:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_introspeccao_prompt_base2.py --trace <trace da base 2>
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contar_primeiro_passo_nome_base2 import assinatura, bp, explodir  # noqa: E402
sys.path.insert(0, str(AQUI.parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"))
from contar_introspeccao_linha import uso_da_linha, VERIFICA  # noqa: E402  (a mesma regra nas duas bases)

INTROSPECCAO = ("globals", "locals", "vars", "dir")
RE_PROIBIDA = re.compile(r"Forbidden function evaluation: '(\w+)'")
# a instrução de verificar (julho, na base 1: "VERIFIQUE se a variável de saída correspondente já está preenchida em
# memória. Se já estiver, PULE a chamada"), e os termos de COMO verificar que a versão de agosto acrescenta (§7.9)
TERMOS = {"instrucao_verificar": re.compile(r"(?i)verifi\w*\s+se\s+a\s+vari[aá]vel|preenchida\s+em\s+mem[oó]ria|pule\s+a\s+chamada"),
          "NameError": re.compile(r"NameError"), "globals()": re.compile(r"globals\s*\(\s*\)"),
          "locals()": re.compile(r"locals\s*\(\s*\)")}
LINHA_FALHA = re.compile(r"failed at line '(.*?)' due to", re.S)
TRY_NAMEERROR = re.compile(r"except\s+\(?[^)\n:]*\bNameError\b")
TRY_OUTRO = re.compile(r"^\s*try\s*:\s*\n\s*[A-Za-z_]\w*\s*\n\s*except\b(?![^\n:]*NameError)", re.M)


def como_verificou(code):
    """Como o código do passo verifica se uma variável existe (regex; uma pista, não uma prova)."""
    code = str(code or "")
    if VERIFICA.search(code):
        return "introspecção (globals/locals/vars)"
    if TRY_NAMEERROR.search(code):
        return "try/except NameError"
    if TRY_OUTRO.search(code):
        return "try/except de outro tipo"
    return "não verificou"


def introspeccao(msg):
    """O nome da função de introspecção recusada, ou None."""
    m = RE_PROIBIDA.search(str(msg))
    return m.group(1) if m and m.group(1) in INTROSPECCAO else None


def uso_na_linha(msg):
    """O uso da introspecção na linha que falhou (a regra do `contar_introspeccao_linha.py`)."""
    m = LINHA_FALHA.search(str(msg))
    return uso_da_linha(m.group(1)) if m else "outro uso"


def trecho(prompt):
    """As linhas do prompt que mencionam os termos da verificação, e o hash delas (a versão do trecho)."""
    linhas = sorted({l.strip() for l in str(prompt).splitlines() if any(rx.search(l) for rx in TERMOS.values())})
    h = hashlib.sha256("\n".join(linhas).encode("utf-8")).hexdigest()[:10] if linhas else "(nenhuma)"
    return h, {t: bool(rx.search(str(prompt))) for t, rx in TERMOS.items()}


def medir(S):
    """S: um ActionStep por linha (exec_id, agente, role, idx, mes, err_type, err_msg, sysprompt). Devolve as tabelas."""
    S = S.copy()
    S["erro"] = S.err_type.notna()
    S["intro"] = [introspeccao(m) if e else None for m, e in zip(S.err_msg, S.erro)]
    S["tryexc"] = [e and assinatura(m) == "try/except NameError" for m, e in zip(S.err_msg, S.erro)]
    I = S[S.intro.notna()]
    A = I.groupby(["role", "mes", "intro"]).size().rename("erros").reset_index()
    ex = S.groupby(["exec_id", "agente", "role"]).agg(mes=("mes", "first"), intro=("intro", lambda s: s.notna().any()),
                                                      tryexc=("tryexc", "any")).reset_index()
    prim = S[S.idx.eq(0)][["exec_id", "agente", "role", "sysprompt", "code"]]
    prim = prim.assign(como_verificou=prim.code.map(como_verificou))
    prim = prim.assign(**{"versao_trecho": [trecho(p)[0] for p in prim.sysprompt]},
                       **{f"menciona_{t}": [trecho(p)[1][t] for p in prim.sysprompt] for t in TERMOS})
    ex = ex.merge(prim.drop(columns=["sysprompt", "code"]), on=["exec_id", "agente", "role"], how="left")
    ex["versao_trecho"] = ex.versao_trecho.fillna("(sem primeiro passo)")
    papeis = sorted(set(I.role))
    C = (ex[ex.role.isin(papeis)].groupby(["role", "mes", "versao_trecho"] + [f"menciona_{t}" for t in TERMOS], dropna=False)
         .agg(execucoes=("exec_id", "size"), com_introspeccao=("intro", "sum"), com_tryexcept=("tryexc", "sum"))
         .reset_index())
    C["com_nenhum"] = C.execucoes - (C.com_introspeccao + C.com_tryexcept).clip(upper=C.execucoes)
    D = I.assign(uso=I.err_msg.map(uso_na_linha)).groupby(["role", "intro", "uso"]).size().rename("erros").reset_index()
    ex["algum_erro"] = ex.intro | ex.tryexc
    E = (ex[ex.role.isin(papeis)].groupby(["role", "versao_trecho", "como_verificou", "algum_erro"], dropna=False)
         .size().rename("execucoes").reset_index())
    algum = (S.assign(v=S.code.map(como_verificou).ne("não verificou")).groupby(["exec_id", "agente", "role"]).v.any()
             .rename("verificou_em_algum_passo").reset_index())
    todos = prim.assign(verificou=prim.como_verificou.ne("não verificou")).merge(algum, on=["exec_id", "agente", "role"], how="left")
    F = (todos.groupby("role").agg(execucoes=("exec_id", "size"), prompt_com_instrucao=("menciona_instrucao_verificar", "sum"),
                                   verificaram_no_primeiro_passo=("verificou", "sum"),
                                   verificaram_em_algum_passo=("verificou_em_algum_passo", "sum"))
         .reset_index().query("prompt_com_instrucao > 0 or verificaram_em_algum_passo > 0").sort_values("execucoes", ascending=False))
    return {"A": A, "C": C, "D": D, "E": E, "F": F}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru da base 2 (CSV ou parquet)")
    args = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    bp.TRACE = str(args.trace)
    T = medir(explodir(bp.carregar_trace()))
    pd.set_option("display.width", 200)
    print("A · erros de introspecção (função proibida) por papel × mês × função:")
    print(T["A"].to_string(index=False) if len(T["A"]) else "  nenhum")
    print("\nC · o teste: papel × mês × versão do trecho do prompt (hash das linhas da instrução e de NameError/globals()/locals())")
    print("    menciona_* = o prompt da execução tem o termo; execuções contadas pelo papel")
    print(T["C"].sort_values(["role", "mes", "execucoes"], ascending=[True, True, False]).to_string(index=False)
          if len(T["C"]) else "  nenhum papel com erro de introspecção")
    print("\nD · a linha que falhou, nos erros de introspecção:")
    print(T["D"].to_string(index=False) if len(T["D"]) else "  nenhum")
    print("\nE · como o primeiro passo verificou, por versão do trecho (algum_erro = introspecção ou try/except na execução):")
    print(T["E"].to_string(index=False) if len(T["E"]) else "  nenhum")
    print("\nF · todos os papéis: o prompt tem a instrução de verificar? o primeiro passo verificou? (só papéis com algum dos dois)")
    print(T["F"].to_string(index=False) if len(T["F"]) else "  nenhum")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
