"""Base 2 (trace completo): o erro de nome não definido no primeiro ActionStep do papel — o mesmo grupo da base 3.

Na base 3 (só os erros, em parquet), 5.818 erros de nome não definido são o primeiro ActionStep do papel, um por
execução, 27 nomes (os 3 mais frequentes = 90%), 98% em agosto de 2026, 92% no ContestacaoCivel; onde o código veio
inteiro, 78% usam o nome antes de defini-lo no mesmo código. A base 2 tem o trace inteiro e o mesmo mês: aqui dá para
conferir sem regex de janela e responder o que o parquet não responde.

  A. a base: execuções, ActionSteps, erros estruturados, erros de nome não definido;
  B. onde caem os erros de nome: primeiro passo × depois de um passo com erro × depois de um passo sem erro;
  C. a regra da base 3 conferida no trace real: "primeiro ActionStep" = step_number 1 e posição na lista <= 3;
  D. o denominador: em cada papel e mês, quantas execuções do papel começam com esse erro;
  E. o grupo do primeiro passo: nomes (só contagens, salvo --mostrar-nomes), modelo, o nome usado antes de ser
     definido no mesmo código, definido no passo seguinte, presente na tarefa, presente no system prompt, e se a mesma
     conversa teve antes uma execução com o mesmo papel.

Usa as funções do pipeline da base 1 (o método é o mesmo nas duas bases). Não grava nada. Imprime só contagens,
nomes de papel, meses e nomes de modelo — nenhum identificador de execução nem texto de caso. Os nomes das variáveis
só saem com --mostrar-nomes. Uso, da raiz, na máquina onde está a base 2:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_primeiro_passo_nome_base2.py --trace <arquivo do trace da base 2> [--mostrar-nomes]
"""
import argparse
import json
from pathlib import Path
import re
import sys

import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ANALYSIS))
sys.path.insert(0, str(ANALYSIS / "2026-09-trace-law-flow" / "pipeline"))
import base_pipeline as bp

RE_NOME = (re.compile(r"variable `(\w+)` is not defined"), re.compile(r"Forbidden function evaluation: '(\w+)'"))


def nome_do_erro(msg):
    for rx in RE_NOME:
        m = rx.search(str(msg))
        if m:
            return m.group(1)
    return None


def _texto(c):
    if isinstance(c, list):
        return " ".join(p.get("text", "") for p in c if isinstance(p, dict))
    return str(c or "")


def _usado_antes_de_definir(code, nome):
    """(aparece, atribuído no mesmo código, primeira atribuição depois do primeiro uso) — regex, uma pista."""
    n = re.escape(nome)
    uso = re.search(rf"\b{n}\b", code)
    if not uso:
        return False, False, False
    padroes = [rf"^[^\n=#]*\b{n}\b[^\n=#]*(?<![=!<>])=(?!=)", rf"^\s*def\s+{n}\b", rf"^\s*for\s+[^\n:]*\b{n}\b[^\n:]*\bin\b",
               rf"\bas\s+{n}\b", rf"^\s*(?:from\s+\S+\s+)?import\s+[^\n]*\b{n}\b"]
    linhas = sorted({code.count("\n", 0, m.start()) for p in padroes for m in re.finditer(p, code, re.M)})
    if not linhas:
        return True, False, False
    return True, True, linhas[0] > code.count("\n", 0, uso.start())


def explodir(df):
    """Uma linha por ActionStep, com o que este script precisa (inclui texto, que nunca é impresso)."""
    linhas = []
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try:
            memo = json.loads(r["txt_etap_memo"])
        except Exception:
            continue
        for role, steps in memo.items():
            if not isinstance(steps, list):
                continue
            idx, tarefa, chamada = -1, "", 0
            for pos, st in enumerate(steps, start=1):
                if not isinstance(st, dict):
                    continue
                if st.get("__class__") == "TaskStep":
                    tarefa, chamada = str(st.get("task") or ""), chamada + 1
                    continue
                if st.get("__class__") != "ActionStep":
                    continue
                idx += 1
                err = st.get("error") or {}
                mim = st.get("model_input_messages") or []
                m0 = mim[0] if mim and isinstance(mim[0], dict) else {}
                raw = (st.get("model_output_message") or {}).get("raw") or {}
                linhas.append({"exec_id": r["cod_idef_exeo"], "agente": r["cod_idef_aget"], "conversa": r.get("cod_idef_cvsa_asnc"),
                               "inicio": r["dat_hor_inio_exeo"], "mes": r["mes"], "role": role, "idx": idx, "step_pos": pos,
                               "step": st.get("step_number"), "chamada": chamada, "err_type": err.get("type"),
                               "err_msg": str(err.get("message") or ""), "code": str(st.get("code_action") or ""),
                               "tarefa": tarefa, "sysprompt": _texto(m0.get("content")),
                               "modelo": raw.get("model") if isinstance(raw, dict) else None})
    return pd.DataFrame(linhas)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru da base 2 (CSV ou parquet)")
    p.add_argument("--mostrar-nomes", action="store_true", help="imprime os 10 nomes mais frequentes (confira antes se podem sair)")
    args = p.parse_args(argv)
    bp.TRACE = str(args.trace)
    df = bp.carregar_trace()
    S = explodir(df)
    S["erro"] = S.err_type.notna()
    S["sub"] = [bp.submecanismo(m) if e else None for m, e in zip(S.err_msg, S.erro)]
    S = S.sort_values(["exec_id", "agente", "role", "idx"])
    S["anterior_com_erro"] = S.groupby(["exec_id", "agente", "role"]).erro.shift()

    # A · a base
    print("A · base: execuções", S.exec_id.nunique(), "| ActionSteps", len(S), "| erros estruturados", int(S.erro.sum()),
          "| nome não definido", int(S["sub"].eq("nome_nao_definido").sum()))

    # B · onde caem os erros de nome
    N = S[S["sub"].eq("nome_nao_definido")].copy()
    N["onde"] = "depois de passo sem erro (nome inventado)"
    N.loc[N.anterior_com_erro.eq(True), "onde"] = "depois de passo com erro (estado perdido)"
    N.loc[N.idx.eq(0), "onde"] = "primeiro ActionStep do papel"
    print("\nB · erros de nome não definido por posição:", N.onde.value_counts().to_dict())
    print(N.groupby(["role", "onde"]).size().rename("erros").reset_index().sort_values("erros", ascending=False).head(10).to_string(index=False))

    # C · a regra da base 3, no trace real (todos os ActionSteps)
    regra = S.step.eq(1) & S.step_pos.le(3)
    print("\nC · regra 'step_number 1 e posição <= 3' × primeiro ActionStep real (todos os ActionSteps):")
    print(pd.crosstab(regra.rename("regra"), S.idx.eq(0).rename("primeiro_real")).to_string())

    # D · o denominador: execuções do papel que começam com o erro
    prim = S[S.idx.eq(0)].copy()
    prim["comeca_com_nome"] = prim["sub"].eq("nome_nao_definido")
    D = prim.groupby(["role", "mes"]).agg(execucoes_do_papel=("exec_id", "size"), comecam_com_nome=("comeca_com_nome", "sum")).reset_index()
    D = D[D.comecam_com_nome.gt(0)]
    D["parcela"] = (D.comecam_com_nome / D.execucoes_do_papel).round(3)
    print("\nD · execuções do papel (papel × mês) e quantas começam com nome não definido:")
    print(D.sort_values("comecam_com_nome", ascending=False).head(12).to_string(index=False))

    # E · o grupo do primeiro passo
    G = N[N.onde.eq("primeiro ActionStep do papel")].copy()
    if G.empty:
        print("\nE · nenhum erro de nome no primeiro passo")
        return 0
    G["nome"] = G.err_msg.map(nome_do_erro)
    nomes = G.nome.dropna().value_counts()
    print("\nE · grupo do primeiro passo:", len(G), "erros em", G.exec_id.nunique(), "execuções")
    print("  nomes distintos:", len(nomes), "| sem nome extraído:", int(G.nome.isna().sum()),
          "| parcela do mais frequente:", round(nomes.iloc[0] / nomes.sum(), 3) if len(nomes) else None,
          "| dos 3 mais:", round(nomes.head(3).sum() / nomes.sum(), 3) if len(nomes) else None)
    if args.mostrar_nomes:
        print("  10 nomes mais frequentes:", nomes.head(10).to_dict())
    print("  modelo:", G.modelo.value_counts(dropna=False).to_dict())
    ok = G.dropna(subset=["nome"])
    r = [_usado_antes_de_definir(c, n) for c, n in zip(ok.code, ok.nome)]
    print("  nome aparece no código:", sum(a for a, _, _ in r), "| atribuído no mesmo código:", sum(b for _, b, _ in r),
          "| primeira atribuição depois do primeiro uso:", sum(c for _, _, c in r), "(regex, de", len(ok), ")")
    seg = S.set_index(["exec_id", "agente", "role", "idx"])
    def_seguinte = 0
    for _, g in ok.iterrows():
        k = (g.exec_id, g.agente, g.role, 1)
        if k in seg.index:
            code1 = seg.loc[k, "code"]
            code1 = code1.iloc[0] if isinstance(code1, pd.Series) else code1
            def_seguinte += bool(_usado_antes_de_definir(str(code1), g.nome)[1])
    print("  nome atribuído no código do passo seguinte:", def_seguinte)
    na_tarefa = sum(bool(re.search(rf"\b{re.escape(n)}\b", t)) for t, n in zip(ok.tarefa, ok.nome))
    no_prompt = sum(bool(re.search(rf"\b{re.escape(n)}\b", s)) for s, n in zip(ok.sysprompt, ok.nome))
    print("  nome aparece no texto da tarefa:", na_tarefa, "| no system prompt:", no_prompt, "(de", len(ok), ")")
    ex = df[["cod_idef_exeo", "cod_idef_cvsa_asnc", "dat_hor_inio_exeo"]].drop_duplicates("cod_idef_exeo")
    papeis_por_exec = S.groupby("exec_id").role.agg(set)
    antes = sem_conversa = 0
    for _, g in G.iterrows():
        if pd.isna(g.conversa) or str(g.conversa).strip() == "":
            sem_conversa += 1
            continue
        outros = ex[ex.cod_idef_cvsa_asnc.eq(g.conversa) & (ex.dat_hor_inio_exeo < g.inicio)]
        antes += any(g.role in papeis_por_exec.get(e, set()) for e in outros.cod_idef_exeo)
    print("  a mesma conversa teve antes uma execução (nesta amostra) com o mesmo papel:", antes,
          "| sem conversa registrada:", sem_conversa, "(de", len(G), ")")
    print("\n  por papel × mês:")
    print(G.groupby(["role", "mes"]).size().rename("erros").reset_index().sort_values("erros", ascending=False).head(10).to_string(index=False))

    # F · a causa: papel × modelo, o modelo do papel ao longo dos meses, e onde o nome aparece no system prompt
    print("\nF · papel × modelo, no grupo do primeiro passo:")
    print(pd.crosstab(G.role, G.modelo.fillna("(sem modelo)")).to_string())
    P1 = prim[prim.role.isin(set(G.role))].copy()
    P1["modelo"] = P1.modelo.fillna("(sem modelo)")
    F = P1.groupby(["role", "mes", "modelo"]).agg(execucoes=("exec_id", "size"), comecam_com_nome=("comeca_com_nome", "sum")).reset_index()
    print("\n  execuções dos papéis do grupo (primeiro ActionStep), por mês e modelo, e quantas começam com o erro:")
    print(F.sort_values(["role", "mes", "modelo"]).to_string(index=False))
    em_bloco = atribuido_no_prompt = def_no_prompt = so_texto = 0
    for sp, n in zip(ok.sysprompt, ok.nome):
        if not re.search(rf"\b{re.escape(n)}\b", sp):
            continue
        blocos = re.findall(r"```.*?```|<code>.*?</code>", sp, re.S)
        b = any(re.search(rf"\b{re.escape(n)}\b", x) for x in blocos)
        a = bool(re.search(rf"^[^\n=#]*\b{re.escape(n)}\b[^\n=#]*(?<![=!<>])=(?!=)", sp, re.M))
        d = bool(re.search(rf"\bdef\s+{re.escape(n)}\b", sp))
        em_bloco += b; atribuido_no_prompt += a; def_no_prompt += d; so_texto += not (b or a or d)
    print("\n  onde o nome aparece no system prompt (dos", no_prompt, "em que aparece):",
          "dentro de bloco de código", em_bloco, "| atribuído (nome = ...)", atribuido_no_prompt,
          "| declarado como função (def nome)", def_no_prompt, "| só no texto corrido", so_texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
