# -*- coding: utf-8 -*-
"""Auditoria independente da evidencia 11.9_leituras_quebra_sigilo (notebook §11.9).

Recomputa do zero, com csv.DictReader + json + ast (sem pandas, sem nenhuma
funcao do notebook nem de base_pipeline), os numeros publicados:

  1. universo: quantos papeis declaram `def validar_quebra_sigilo(` no system
     prompt e quantos de fato a chamam no code_action;
  2. payload entregue: action_output.request['quebra_sigilo'] do ultimo step
     final de cada papel que chamou — categoria por tipo, sem imprimir conteudo;
  3. as 9 execucoes nao conformes: nenhum erro registrado em nenhum ActionStep
     do papel (e, separado, da execucao inteira);
  4. retratacao 1: em 8dd410c8… o payload entregue deve ser 'NAO' e o codigo
     deve conter a cadeia .get('vazamento_sigilo', .get('quebra_sigilo'));
  5. retratacao 2 (detector de grafia): comparacoes ==/!=/in contra literal
     que so vira SIM/NAO ao normalizar acento+caixa, sobre variavel derivada do
     retorno da ferramenta — esperado: 5, em 2 execucoes; e a comparacao de
     8dd410c8… sobre new_validade NAO pode entrar (proveniencia);
  6. integridade: cada trecho dos 13 derivados/<exec>_<role>_idx<n>.json deve
     bater com o crus/<exec_id>.json no caminho declarado (122 trechos).

Saida: audit_out7.txt (git-ignored). Nada de conteudo de caso na saida —
so tipos, chaves, comprimentos e contagens.
"""
import csv, json, re, ast, os, sys, unicodedata
from collections import defaultdict

csv.field_size_limit(sys.maxsize)

REPO = os.path.dirname(os.path.abspath(__file__))
TRACE = os.path.join(REPO, "..", "..", "data", "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")
EVID = os.path.join(REPO, "..", "..", "pipeline", "resultados", "evidencia",
                    "11.9_leituras_quebra_sigilo")
FN = "validar_quebra_sigilo"
DECL = re.compile(r"def\s+" + FN + r"\s*\(")
CHAMADA = re.compile(r"\b" + FN + r"\s*\(")
FALHOU = re.compile(r"^Code execution failed at line '(.*?)' due to: ", re.S)

def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").upper()

def system_prompt(st):
    mim = st.get("model_input_messages")
    if not mim:
        return ""
    m0 = mim[0] if isinstance(mim[0], dict) else {}
    c = m0.get("content")
    return c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")

def load_steps():
    """(exec_id, role) -> {idx: step-dict}; tambem memo cru por exec_id."""
    import lzma
    passos, memos, mes_de = defaultdict(dict), {}, {}
    with lzma.open(TRACE, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            memo_txt = row.get("txt_etap_memo")
            if not memo_txt:
                continue
            try:
                memo = json.loads(memo_txt)
            except Exception:
                continue
            ex, mes = row["cod_idef_exeo"], row["anomesdia"][:6]
            memos[ex] = memo
            mes_de[ex] = mes
            for role, steps in memo.items():
                if not isinstance(steps, list):
                    continue
                i = 0
                for st in steps:
                    if isinstance(st, dict) and st.get("__class__") == "ActionStep":
                        passos[(ex, role)][i] = st
                        i += 1
    return passos, memos, mes_de

# ---------- AST helpers (reescritos do zero) ----------

def vars_da_chamada(codigo, fn):
    """nomes de variaveis que recebem `x = fn(...)` no step."""
    try:
        arv = ast.parse(codigo)
    except SyntaxError:
        return set()
    out = set()
    for n in ast.walk(arv):
        if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
            alvo = n.targets[0] if isinstance(n, ast.Assign) else n.target
            v = n.value
            while isinstance(v, (ast.Subscript, ast.Attribute, ast.Starred)):
                v = v.value
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == fn:
                if isinstance(alvo, ast.Name):
                    out.add(alvo.id)
    return out

def ultima_atrib(arv, nome, antes_de):
    melhor = None
    for n in ast.walk(arv):
        if isinstance(n, ast.Assign) and n.value is not None and n.lineno < antes_de:
            if any(isinstance(t, ast.Name) and t.id == nome for t in n.targets):
                if melhor is None or n.lineno > melhor.lineno:
                    melhor = n
    return melhor.value if melhor is not None else None

def deriva_de(v, retorno_vars, arv, linha, prof=0):
    """v vem de alguma variavel que recebeu a chamada da ferramenta (1+ niveis)."""
    if isinstance(v, ast.Name):
        if v.id in retorno_vars:
            return True
        if prof < 3:
            rhs = ultima_atrib(arv, v.id, linha)
            if rhs is not None:
                return deriva_de(rhs, retorno_vars, arv, getattr(rhs, "lineno", linha), prof + 1)
        return False
    if isinstance(v, (ast.Subscript, ast.Attribute)):
        return deriva_de(v.value, retorno_vars, arv, linha, prof)
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute):
        return deriva_de(v.func.value, retorno_vars, arv, linha, prof)
    return False

def linha_da_falha(codigo, err):
    m = FALHOU.search(err or "")
    if not m:
        return None
    primeira = m.group(1).strip().split("\n")[0].strip()
    try:
        arv = ast.parse(codigo)
    except SyntaxError:
        return None
    for n in ast.walk(arv):
        if isinstance(n, ast.stmt):
            seg = ast.get_source_segment(codigo, n) or ""
            if seg.strip().split("\n")[0].strip() == primeira:
                return n.lineno
    return None

def categoria(v):
    if v is None:
        return "ausente"
    if isinstance(v, dict):
        return "dict:" + ",".join(sorted(map(str, v.keys())))
    if isinstance(v, list):
        return f"lista[{len(v)}]"
    if isinstance(v, str):
        if v == "":
            return "vazia"
        if norm(v) in ("SIM", "NAO") and len(v) <= 4:
            return "conforme:" + v
        if len(v) <= 12:
            return "curto_inesperado"
        return f"texto_longo:{len(v)}"
    return type(v).__name__

def resolver_caminho(obj, caminho):
    for k in caminho:
        obj = obj[k]
    return obj

def main():
    passos, memos, mes_de = load_steps()
    print(f"[carga] {len(passos)} papeis, {len(memos)} execucoes")

    # 1) universo
    papeis_decl = {(ex, role) for (ex, role), ps in passos.items()
                   if any(DECL.search(system_prompt(st)) for st in ps.values())}
    chamou = {p for p in papeis_decl
              if any(CHAMADA.search(st.get("code_action") or "") for st in passos[p].values())}
    print(f"[universo] declaram {FN}: {len(papeis_decl)} | chamam: {len(chamou)} | "
          f"nunca chamam: {len(papeis_decl - chamou)}")

    # 2) payload entregue
    entregue, sem_payload = {}, []
    for p in sorted(chamou):
        ps = passos[p]
        idxs_final = [i for i, st in ps.items() if st.get("is_final_answer")]
        achado = None
        for i in sorted(ps):
            out = ps[i].get("action_output")
            if isinstance(out, dict) and isinstance(out.get("request"), dict) \
               and "quebra_sigilo" in out["request"]:
                achado = out["request"]["quebra_sigilo"]
        if achado is None and not idxs_final:
            sem_payload.append(p)
        entregue[p] = achado
    n_entregues = sum(1 for v in entregue.values() if v is not None)
    print(f"[payload] {n_entregues} execucoes entregaram request.quebra_sigilo")

    cats = defaultdict(list)
    for p, v in entregue.items():
        cats[categoria(v)].append((p, mes_de[p[0]]))
    for c, l in sorted(cats.items(), key=lambda kv: -len(kv[1])):
        meses = sorted({m for _, m in l})
        print(f"  {c:45s} n={len(l):2d} meses={meses}")

    nao_conf = [(p, v) for p, v in entregue.items()
                if v is not None and not categoria(v).startswith("conforme")]
    meses_nc = sorted({mes_de[p[0]] for p, _ in nao_conf})
    print(f"[decisivo] {len(nao_conf)}/{n_entregues} nao conformes, meses={meses_nc}")

    # 3) erros nas execucoes nao conformes
    for p, v in nao_conf:
        ex, role = p
        errs_papel = sum(1 for st in passos[p].values() if st.get("error"))
        errs_exec = sum(1 for r2, steps in memos[ex].items() if isinstance(steps, list)
                        for st in steps
                        if isinstance(st, dict) and st.get("__class__") == "ActionStep" and st.get("error"))
        cat = categoria(v)
        det = ""
        if isinstance(v, dict):
            det = " chaves=" + ",".join(sorted(map(str, v.keys())))
        elif isinstance(v, str) and v == "":
            det = " (string vazia)"
        print(f"  {ex[:8]}… {role} mes={mes_de[ex]} erros_papel={errs_papel} "
              f"erros_exec={errs_exec} {cat}{det}")

    # 4) retratacao 1 — 8dd410c8 entregou 'NAO' e tem a cadeia .get
    alvo = next((p for p in passos if p[0].startswith("8dd410c8")), None)
    if alvo:
        v = entregue.get(alvo)
        print(f"[retratacao-1] {alvo[0][:8]}… payload entregue = {categoria(v)} "
              f"(literal SIM/NAO normalizado: {norm(v) if isinstance(v, str) else 'n/a'})")
        achou_cadeia = False
        for i, st in sorted(passos[alvo].items()):
            cod = st.get("code_action") or ""
            if ".get('vazamento_sigilo'" in cod or '.get("vazamento_sigilo"' in cod:
                achou_cadeia = True
        print(f"[retratacao-1] cadeia .get('vazamento_sigilo', ...) presente no codigo: {achou_cadeia}")

    # 5) grafia — comparacoes com literal que normaliza p/ SIM|NAO
    print("[grafia] comparacoes divergentes sobre var derivada do retorno:")
    n_grafia = 0
    for p in sorted(chamou):
        retorno_vars = set()
        for i, st in passos[p].items():
            retorno_vars |= vars_da_chamada(st.get("code_action") or "", FN)
        for i, st in sorted(passos[p].items()):
            cod = st.get("code_action") or ""
            try:
                arv = ast.parse(cod)
            except SyntaxError:
                continue
            lf = linha_da_falha(cod, str((st.get("error") or {}).get("message") or ""))
            for n in ast.walk(arv):
                if not isinstance(n, ast.Compare):
                    continue
                lados = [n.left] + list(n.comparators)
                for a, b in zip(lados, lados[1:]):
                    for var_side, lit_side in ((a, b), (b, a)):
                        lits = [x for x in ast.walk(lit_side)
                                if isinstance(x, ast.Constant) and isinstance(x.value, str)
                                and len(x.value) <= 8]
                        for x in lits:
                            lit = x.value
                            if lit in ("SIM", "NAO") or norm(lit) not in ("SIM", "NAO"):
                                continue
                            if not deriva_de(var_side, retorno_vars, arv, n.lineno):
                                continue
                            n_grafia += 1
                            if lf is not None and n.lineno > lf:
                                alc = "nao avaliada"
                            elif lf is not None and n.lineno == lf:
                                alc = "mesma linha da falha"
                            else:
                                alc = "avaliada"
                            print(f"  {p[0][:8]}… idx={i} linha={n.lineno} literal={lit!r} {alc}")
    print(f"[grafia] total: {n_grafia} comparacoes (esperado 5, em 2 execucoes)")

    # 5b) a comparacao estranha de 8dd410c8 (new_validade) — deve existir e NAO derivar do retorno
    if alvo:
        for i, st in sorted(passos[alvo].items()):
            cod = st.get("code_action") or ""
            try:
                arv = ast.parse(cod)
            except SyntaxError:
                continue
            retorno_vars = set()
            for j, st2 in passos[alvo].items():
                retorno_vars |= vars_da_chamada(st2.get("code_action") or "", FN)
            for n in ast.walk(arv):
                if isinstance(n, ast.Compare):
                    lits = [x.value for x in ast.walk(n)
                            if isinstance(x, ast.Constant) and isinstance(x.value, str)
                            and norm(x.value) in ("SIM", "NAO") and x.value not in ("SIM", "NAO")]
                    if lits:
                        deriva = deriva_de(n.left, retorno_vars, arv, n.lineno)
                        print(f"[retratacao-2] {alvo[0][:8]}… idx={i} linha={n.lineno} lits={lits} "
                              f"deriva_do_retorno={deriva}")

    # 6) integridade dos trechos
    print("[trechos] conferindo derivados contra crus:")
    total, ok, falhas = 0, 0, []
    for fn_json in sorted(os.listdir(os.path.join(EVID, "derivados"))):
        if not fn_json.endswith(".json"):
            continue
        d = json.load(open(os.path.join(EVID, "derivados", fn_json)))
        cru = json.load(open(os.path.join(EVID, "crus", d["caso_segundo_o_notebook"]["exec_id"] + ".json")))
        for t in d.get("trechos_do_cru", []):
            total += 1
            try:
                v = resolver_caminho(cru, t["cru"])
            except (KeyError, IndexError, TypeError):
                v = None
            if "caracteres" in t:
                v = v[t["caracteres"][0]:t["caracteres"][1]] if isinstance(v, str) else None
            elif "mensagens" in t:
                v = [{"role": m.get("role"), "texto": "".join(x.get("text","") for x in m.get("content",[])) if isinstance(m.get("content"), list) else str(m.get("content") or "")}
                     for m in v[t["mensagens"][0]:t["mensagens"][1]]]
            if t["texto"] is None or v == t["texto"]:
                ok += 1
            else:
                falhas.append((fn_json, t["o_que"]))
    print(f"[trechos] {ok}/{total} conferem; divergentes: {falhas if falhas else 'nenhum'}")

if __name__ == "__main__":
    main()
