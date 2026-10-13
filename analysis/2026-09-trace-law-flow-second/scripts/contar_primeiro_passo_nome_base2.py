"""Base 2 (trace completo): o erro de nome não definido no primeiro ActionStep do papel — o mesmo grupo da base 3.

Na base 3 (só os erros, em parquet), 5.818 erros de nome não definido são o primeiro ActionStep do papel, um por
execução, 27 nomes (os 3 mais frequentes = 90%), 98% em agosto de 2026, 92% no ContestacaoCivel; onde o código veio
inteiro, 78% têm a referência ao nome antes da atribuição (a leitura de três casos, em 13/10, mostrou que é o padrão `try/except NameError` instruído pelo prompt). A base 2 tem o trace inteiro e o mesmo mês: aqui dá para
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
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[2]
REPO = ANALYSIS.parent
sys.path.insert(0, str(ANALYSIS))
sys.path.insert(0, str(ANALYSIS / "2026-09-trace-law-flow" / "pipeline"))
import base_pipeline as bp

# depois do Ajuste 17, o erro com a assinatura try/except NameError tem mecanismo próprio; os dois são "nome não definido"
NOMES = {"nome_nao_definido", "verificacao_try_nameerror"}
RE_NOME = (re.compile(r"variable `(\w+)` is not defined"), re.compile(r"Forbidden function evaluation: '(\w+)'"))


def nome_do_erro(msg):
    for rx in RE_NOME:
        m = rx.search(str(msg))
        if m:
            return m.group(1)
    return None


LINHA_FALHA = re.compile(r"failed at line '(.*?)' due to", re.S)


def assinatura(msg):
    """Na linha que falhou (a mensagem a traz): 'try/except NameError', 'duvidoso' (começa com try: sem except NameError) ou 'não'."""
    m = LINHA_FALHA.search(str(msg))
    trecho = m.group(1) if m else ""
    if re.search(r"except\s+\(?[^)\n:]*\bNameError\b", trecho):
        return "try/except NameError"
    return "duvidoso" if trecho.lstrip().startswith("try:") else "não"


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
    p.add_argument("--evidencia", type=Path, help="pasta FORA do repositório onde gravar os casos para leitura (texto do caso; não sai da máquina)")
    p.add_argument("--n-casos", type=int, default=3, help="quantos casos com erro gravar (padrão 3), mais 1 de contraste")
    args = p.parse_args(argv)
    if args.evidencia is not None and args.evidencia.resolve().is_relative_to(REPO.resolve()):
        p.error("--evidencia deve ficar fora do repositório: os casos têm texto e identificador e não podem ser versionados")
    bp.TRACE = str(args.trace)
    df = bp.carregar_trace()
    S = explodir(df)
    S["erro"] = S.err_type.notna()
    S["sub"] = [bp.submecanismo(m) if e else None for m, e in zip(S.err_msg, S.erro)]
    S = S.sort_values(["exec_id", "agente", "role", "idx"])
    S["anterior_com_erro"] = S.groupby(["exec_id", "agente", "role"]).erro.shift()

    # A · a base
    print("A · base: execuções", S.exec_id.nunique(), "| ActionSteps", len(S), "| erros estruturados", int(S.erro.sum()),
          "| nome não definido", int(S["sub"].isin(NOMES).sum()))

    # B · onde caem os erros de nome
    N = S[S["sub"].isin(NOMES)].copy()
    N["onde"] = "depois de passo sem erro (nome inventado)"
    N.loc[N.anterior_com_erro.eq(True), "onde"] = "depois de passo com erro (estado perdido)"
    N.loc[N.idx.eq(0), "onde"] = "primeiro ActionStep do papel"
    print("\nB · erros de nome não definido por posição:", N.onde.value_counts().to_dict())
    print(N.groupby(["role", "onde"]).size().rename("erros").reset_index().sort_values("erros", ascending=False).head(10).to_string(index=False))

    # H · a assinatura try/except NameError na mensagem (a regra proposta para a base 3), em cada posição
    N["assinatura"] = N.err_msg.map(assinatura)
    print("\nH · assinatura `try/except NameError` na linha que falhou, por posição do erro de nome:")
    print(pd.crosstab(N.onde, N.assinatura, margins=True, margins_name="total").to_string())
    outros = S[S.erro & ~S["sub"].isin(NOMES) & S.err_msg.str.contains("except NameError", regex=False)]
    print("  erros que não são de nome não definido, mas cuja mensagem traz 'except NameError':", len(outros),
          "| por tipo:", outros.err_type.value_counts().head(5).to_dict())
    com = N[N.assinatura.eq("try/except NameError")]
    print("  com a assinatura, por papel × mês × modelo:")
    print(com.groupby(["role", "mes", com.modelo.fillna("(sem modelo)")]).size().rename("erros").reset_index().to_string(index=False)
          if len(com) else "    nenhum")

    # C · a regra da base 3, no trace real (todos os ActionSteps)
    regra = S.step.eq(1) & S.step_pos.le(3)
    print("\nC · regra 'step_number 1 e posição <= 3' × primeiro ActionStep real (todos os ActionSteps):")
    print(pd.crosstab(regra.rename("regra"), S.idx.eq(0).rename("primeiro_real")).to_string())

    # D · o denominador: execuções do papel que começam com o erro
    prim = S[S.idx.eq(0)].copy()
    prim["comeca_com_nome"] = prim["sub"].isin(NOMES)
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

    # G · o system prompt mudou? O prompt traz conteúdo do caso, então o hash do prompt inteiro varia por execução.
    # O que se compara entre meses: se o prompt ATRIBUI algum nome do grupo ("nome = ..."), e a assinatura dessas
    # linhas de atribuição (hash das linhas, ordenadas) — essa parte é do modelo de prompt, não do caso.
    nomes_grupo = set(ok.nome)
    def _linhas_atrib(t):
        return sorted({l.strip() for l in t.splitlines() for n in nomes_grupo
                       if re.search(rf"^[^=#]*\b{re.escape(n)}\b[^=#]*(?<![=!<>])=(?!=)", l)})
    P1["atrib"] = P1.sysprompt.map(_linhas_atrib)
    P1["atribui_nome"] = P1.atrib.map(bool)
    P1["assinatura"] = P1.atrib.map(lambda ls: hashlib.sha256("\n".join(ls).encode("utf-8")).hexdigest()[:10] if ls else "(nenhuma)")
    P1["hash_prompt"] = P1.sysprompt.map(lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()[:10])
    H = P1.groupby(["role", "mes", "modelo"]).agg(
        execucoes=("exec_id", "size"), comecam_com_nome=("comeca_com_nome", "sum"),
        prompts_distintos=("hash_prompt", "nunique"), prompt_atribui_nome_do_grupo=("atribui_nome", "sum"),
        assinaturas=("assinatura", "nunique"),
        assinatura_mais_comum=("assinatura", lambda x: x.value_counts().index[0])).reset_index()
    print("\nG · o system prompt atribui os nomes do grupo? (por papel, mês e modelo; dos", len(nomes_grupo), "nomes do grupo)")
    print("  assinatura = hash das linhas do prompt que atribuem nomes do grupo — igual entre execuções = mesmo trecho de modelo")
    print(H.sort_values(["role", "mes", "modelo"]).to_string(index=False))
    X = P1[P1.atribui_nome].groupby(["role", "assinatura"]).agg(
        execucoes=("exec_id", "size"), comecam_com_nome=("comeca_com_nome", "sum"),
        primeiro_mes=("mes", "min"), ultimo_mes=("mes", "max")).reset_index().sort_values("execucoes", ascending=False).head(10)
    print("\n  por assinatura (as 10 maiores): execuções, quantas começam com o erro, primeiro e último mês")
    print(X.to_string(index=False))

    if args.evidencia is not None:
        gravar_evidencia(args.evidencia, args.n_casos, G, P1, seg)
    return 0


def _trechos(texto, nome, contexto=6):
    linhas = texto.splitlines()
    alvo = [i for i, l in enumerate(linhas) if re.search(rf"\b{re.escape(nome)}\b", l)]
    blocos, fim = [], -1
    for i in alvo:
        a, b = max(0, i - contexto), min(len(linhas), i + contexto + 1)
        if a <= fim:
            blocos[-1] = (blocos[-1][0], b)
        else:
            blocos.append((a, b))
        fim = b
    return "\n...\n".join("\n".join(f"{j + 1:5d}| {linhas[j]}" for j in range(a, b)) for a, b in blocos) or "(o nome não aparece)"


def gravar_evidencia(pasta, n, G, P1, seg):
    """Casos para LEITURA na própria máquina: o trecho do system prompt em volta do nome, o código do primeiro passo,
    o erro e o código do passo seguinte; mais um caso de contraste (mesmo papel e modelo, mês anterior, sem o erro) e o
    diff entre os dois prompts. Regra fixa de escolha: o papel com mais erros, no mês com mais erros, casos espalhados
    no tempo (primeiro, do meio, último). Na tela, só contagens."""
    pasta.mkdir(parents=True, exist_ok=True)
    role, mes = G.groupby(["role", "mes"]).size().idxmax()
    E = G[G.role.eq(role) & G.mes.eq(mes)].sort_values("inicio").reset_index(drop=True)
    pos = sorted({round(i * (len(E) - 1) / max(1, n - 1)) for i in range(n)}) if len(E) > 1 else [0]
    modelo = E.modelo.mode().iloc[0] if E.modelo.notna().any() else None
    ctr = P1[P1.role.eq(role) & P1.modelo.eq(modelo if modelo is not None else "(sem modelo)") & P1.mes.lt(mes) & ~P1.comeca_com_nome]
    ctr = ctr.sort_values("inicio").tail(1)
    gravados = 0
    for k, i in enumerate(pos, start=1):
        r = E.iloc[i]
        k1 = (r.exec_id, r.agente, r.role, 1)
        prox = seg.loc[k1, "code"] if k1 in seg.index else "(sem passo seguinte)"
        prox = prox.iloc[0] if isinstance(prox, pd.Series) else prox
        h = hashlib.sha256(r.sysprompt.encode("utf-8")).hexdigest()[:10]
        txt = (f"CASO {k} — papel {r.role} · mês {r.mes} · modelo {r.modelo} · hash do prompt {h}\n"
               f"exec_id {r.exec_id} · agente {r.agente} · nome que falta: {r.nome}\n\n"
               f"=== ERRO ===\n{r.err_msg}\n\n=== TRECHOS DO SYSTEM PROMPT EM VOLTA DO NOME ===\n{_trechos(r.sysprompt, r.nome)}\n\n"
               f"=== CÓDIGO DO PRIMEIRO ActionStep ===\n{r.code}\n\n=== CÓDIGO DO PASSO SEGUINTE ===\n{prox}\n")
        (pasta / f"caso_{k}.txt").write_text(txt, encoding="utf-8")
        gravados += 1
    linhas_diff = 0
    if len(ctr):
        c, r0 = ctr.iloc[0], E.iloc[pos[0]]
        hc = hashlib.sha256(c.sysprompt.encode("utf-8")).hexdigest()[:10]
        txt = (f"CONTRASTE — papel {c.role} · mês {c.mes} · modelo {c.modelo} · hash do prompt {hc} · SEM o erro\n"
               f"exec_id {c.exec_id} · agente {c.agente}\n\n=== TRECHOS DO SYSTEM PROMPT EM VOLTA DO NOME '{r0.nome}' ===\n"
               f"{_trechos(c.sysprompt, r0.nome)}\n\n=== CÓDIGO DO PRIMEIRO ActionStep ===\n{c.code}\n")
        (pasta / "contraste.txt").write_text(txt, encoding="utf-8")
        diff = list(difflib.unified_diff(c.sysprompt.splitlines(), r0.sysprompt.splitlines(),
                                         fromfile=f"prompt {c.mes} ({hc}, sem erro)", tofile=f"prompt {r0.mes} (com erro)", lineterm="", n=3))
        (pasta / "diff_prompt_contraste_x_caso1.txt").write_text("\n".join(diff), encoding="utf-8")
        linhas_diff = sum(1 for l in diff if l[:1] in "+-" and not l.startswith(("+++", "---")))
    print(f"\nEvidência gravada fora do repositório: {gravados} casos de {role} {mes}, contraste: {len(ctr)} (mês anterior, mesmo modelo, sem o erro);",
          f"diff entre os prompts: {linhas_diff} linhas mudadas. Leia lá; não copie o texto para fora da máquina.")


if __name__ == "__main__":
    raise SystemExit(main())
