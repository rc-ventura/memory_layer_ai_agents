# -*- coding: utf-8 -*-
"""Auditoria independente da evidencia 11.10_leituras_get_available_documents (notebook §11.10).

Recomputa do zero, com csv.DictReader + json + ast (sem pandas, sem funcoes do
notebook/base_pipeline), os numeros publicados:

  1. universo: papeis que declaram `def get_available_documents(` no system prompt;
  2. leituras rastreadas: para cada `x = get_available_documents(...)`, toda
     leitura de x nos steps seguintes do mesmo papel (ate x ser reatribuido a
     algo que nao e chamada da mesma ferramenta): x[k] ou x.get(k, ...);
     classificacao (chave real 'result' x errada) x (guardada por if sobre x)
     x (protegida por try/except) — implementacao propria, mais simples que a
     do notebook, com diff linha a linha contra leituras_universo_completo.csv;
  3. ocorrencias silenciosas: chave errada + sem guarda + sem try + sem erro no
     step + fora dos erros conhecidos — esperado 4;
  4. guarda sobre chave fantasma: `if 'k' in x` com k != 'result' cujo ramo vivo
     nao usa x — esperado 1 (15f6ad52…, 'documents');
  5. nas 5 execucoes confirmadas: resposta real do managerAgent (ultimo step
     is_final_answer) — DEGENERADO, None/null literal, dict impresso;
  6. consistencia: as leituras erradas+desprotegidas COM erro reconciliam com os
     91 erros conhecidos da no2 (erros_mecanismo.csv, U_contrato_dict);
  7. integridade: cada trecho dos derivados deve bater com o cru (64 trechos).

Saida: audit_out8.txt (git-ignored). So estrutura — nenhum texto de documento
ou de resposta na saida.
"""
import csv, json, re, ast, os, sys
from collections import defaultdict

csv.field_size_limit(sys.maxsize)

REPO = os.path.dirname(os.path.abspath(__file__))
TRACE = os.path.join(REPO, "..", "..", "data", "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")
EVID = os.path.join(REPO, "..", "..", "pipeline", "resultados", "evidencia",
                    "11.10_leituras_get_available_documents")
RES = os.path.join(REPO, "..", "..", "pipeline", "resultados")
FN = "get_available_documents"
DECL = re.compile(r"def\s+" + FN + r"\s*\(")
DEGENERADO = re.compile(r"n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente", re.I)
NULO = re.compile(r"\bNone\b|\bnull\b", re.I)
DICT_IMP = re.compile(r"\{[^{}]{0,300}:[^{}]{0,300}\}")
PEGA_TUDO = {"Exception", "BaseException", "KeyError", "LookupError", "IndexError", "TypeError"}
EMBRULHO = {"list", "sorted", "reversed", "iter", "enumerate", "tuple"}

def system_prompt(st):
    mim = st.get("model_input_messages")
    if not mim:
        return ""
    m0 = mim[0] if isinstance(mim[0], dict) else {}
    c = m0.get("content")
    return c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")

def load_steps():
    import lzma
    passos, memos, mes_de = defaultdict(dict), {}, {}
    with lzma.open(TRACE, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t = row.get("txt_etap_memo")
            if not t:
                continue
            try:
                memo = json.loads(t)
            except Exception:
                continue
            ex = row["cod_idef_exeo"]
            memos[ex] = memo
            mes_de[ex] = row["anomesdia"][:6]
            for role, steps in memo.items():
                if not isinstance(steps, list):
                    continue
                i = 0
                for st in steps:
                    if isinstance(st, dict) and st.get("__class__") == "ActionStep":
                        passos[(ex, role)][i] = st
                        i += 1
    return passos, memos, mes_de

# ---------- AST helpers (reescritos) ----------

def origem(e):
    """('call', fn) | ('name', var) | (None, None) — o que a expressao e, na raiz."""
    while True:
        if isinstance(e, (ast.Subscript, ast.Attribute, ast.Starred)):
            e = e.value
        elif isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Name) and f.id in EMBRULHO and e.args:
                e = e.args[0]
            elif isinstance(f, ast.Name):
                return "call", f.id
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and e.args and (
                    f.value.id == "json" or (f.value.id in ("pd", "pandas")
                                             and f.attr in ("DataFrame", "json_normalize"))):
                e = e.args[0]
            elif isinstance(f, ast.Attribute):
                e = f.value
            else:
                return None, None
        elif isinstance(e, ast.Name):
            return "name", e.id
        else:
            return None, None

def chamadas(codigo, fn):
    """[(var, lineno)] de `x = fn(...)`."""
    try:
        arv = ast.parse(codigo)
    except SyntaxError:
        return []
    out = []
    for n in ast.walk(arv):
        if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
            alvo = n.targets[0] if isinstance(n, ast.Assign) else n.target
            if isinstance(alvo, ast.Name) and origem(n.value) == ("call", fn):
                out.append((alvo.id, n.lineno))
    return out

def ids_try(arv):
    ids = set()
    for n in ast.walk(arv):
        if isinstance(n, ast.Try):
            pega = any(h.type is None or any(isinstance(x, ast.Name) and x.id in PEGA_TUDO
                                           for x in ast.walk(h.type)) for h in n.handlers)
            if pega:
                ids |= {id(x) for b in n.body for x in ast.walk(b)}
    return ids

def ids_guarda(arv, var):
    """ids dos nos dentro de if/else (ou IfExp) cujo teste menciona a propria var."""
    ids = set()
    for n in ast.walk(arv):
        if isinstance(n, (ast.If, ast.IfExp)) and any(
                isinstance(x, ast.Name) and x.id == var for x in ast.walk(n.test)):
            ramos = (n.body + n.orelse) if isinstance(n, ast.If) else [n.body, n.orelse]
            ids |= {id(x) for r in ramos for x in ast.walk(r)}
    return ids

def leituras(arv, var, fn):
    """[(forma, chave, protegido, guardado)] — leituras de var, cortando na
    reatribuicao de var a algo que nao e chamada de fn (mesmo criterio do
    notebook: leituras dentro do lado direito da reatribuicao contam)."""
    prot = ids_try(arv)
    guard = ids_guarda(arv, var)
    ligs = [n for n in ast.walk(arv)
            if (isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and any(
                isinstance(x, ast.Name) and x.id == var and isinstance(x.ctx, ast.Store)
                for t in (n.targets if isinstance(n, ast.Assign) else [n.target]) for x in ast.walk(t))
                and not (n.value is not None and origem(n.value) == ("call", fn)))
            or (isinstance(n, ast.For) and any(
                isinstance(x, ast.Name) and x.id == var for x in ast.walk(n.target)))]
    corte, dentro = None, set()
    if ligs:
        b = min(ligs, key=lambda n: (n.lineno, n.col_offset))
        corte = b.lineno
        valor = b.iter if isinstance(b, ast.For) else b.value
        dentro = {id(x) for x in ast.walk(valor)} if valor is not None else set()
    out = []
    for n in ast.walk(arv):
        if corte is not None and id(n) not in dentro and getattr(n, "lineno", 0) >= corte:
            continue
        if isinstance(n, ast.Subscript) and not isinstance(n.ctx, ast.Load):
            continue
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == var:
            k = n.slice.value if isinstance(n.slice, ast.Constant) else (
                "<fatia>" if isinstance(n.slice, ast.Slice) else "<expr>")
            out.append(("[]", k, id(n) in prot, id(n) in guard))
        elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr == "get" and isinstance(n.func.value, ast.Name)
              and n.func.value.id == var and n.args):
            k = n.args[0].value if isinstance(n.args[0], ast.Constant) else "<expr>"
            out.append((".get", k, id(n) in prot, id(n) in guard))
    return out

def raiz_nome(v):
    while isinstance(v, (ast.Subscript, ast.Attribute)):
        v = v.value
    return v.id if isinstance(v, ast.Name) else None

def guardas_fantasma(arv, var):
    """[(chave, descarta)] — if 'k' in var / 'k' not in var com k != 'result';
    descarta = o ramo que SEMPRE roda (condicao sempre falsa) nao menciona var."""
    out = []
    for n in ast.walk(arv):
        if not isinstance(n, (ast.If, ast.IfExp)):
            continue
        t = n.test
        if not (isinstance(t, ast.Compare) and len(t.ops) == 1
                and isinstance(t.ops[0], (ast.In, ast.NotIn))):
            continue
        esq, dir_ = t.left, t.comparators[0]
        if not (isinstance(esq, ast.Constant) and isinstance(esq.value, str)):
            continue
        if raiz_nome(dir_) != var:
            continue
        chave = esq.value
        if chave == "result":
            continue
        vivo = n.orelse if isinstance(t.ops[0], ast.In) else n.body
        if not vivo:
            descarta = True
        else:
            blocos = vivo if isinstance(vivo, list) else [vivo]
            nomes = {x.id for b in blocos for x in ast.walk(b) if isinstance(x, ast.Name)}
            descarta = var not in nomes
        out.append((chave, descarta))
    return out

def resolver_caminho(obj, caminho):
    for k in caminho:
        obj = obj[k]
    return obj

def main():
    passos, memos, mes_de = load_steps()
    print(f"[carga] {len(passos)} papeis, {len(memos)} execucoes")

    papeis = sorted({(ex, role) for (ex, role), ps in passos.items()
                     if any(DECL.search(system_prompt(st)) for st in ps.values())})
    print(f"[universo] papeis que declaram {FN}: {len(papeis)} "
          f"(papeis: {sorted({r for _, r in papeis})})")

    # erros conhecidos da no2 (referencia externa: erros_mecanismo.csv do pipeline)
    conhecidos = set()
    with open(os.path.join(RES, "erros_mecanismo.csv")) as f:
        for r in csv.DictReader(f):
            if r["unidade"] == "U_contrato_dict":
                conhecidos.add((r["exec_id"], r["role"], int(r["idx"])))
    print(f"[referencia] erros U_contrato_dict em erros_mecanismo.csv: {len(conhecidos)}")

    # leituras rastreadas
    linhas, linhas_g = [], []
    for (ex, role) in papeis:
        ps = passos[(ex, role)]
        idxs = sorted(ps)
        for idx0 in idxs:
            ch = chamadas(ps[idx0].get("code_action") or "", FN)
            for var, _linha in ch:
                for idx in idxs:
                    if idx < idx0:
                        continue
                    st = ps[idx]
                    cod = st.get("code_action") or ""
                    try:
                        arv = ast.parse(cod)
                    except SyntaxError:
                        continue
                    for forma, chave, prot, guard in leituras(arv, var, FN):
                        linhas.append({"exec_id": ex, "role": role, "idx_chamada": idx0,
                                       "idx_leitura": idx, "mes": mes_de[ex],
                                       "forma": forma, "chave": str(chave),
                                       "real": str(chave) == "result",
                                       "protegido": prot, "guardado": guard,
                                       "tem_erro": bool(st.get("error")),
                                       "conhecido": (ex, role, idx) in conhecidos})
                    for chave_t, descarta in guardas_fantasma(arv, var):
                        linhas_g.append({"exec_id": ex, "role": role, "idx_chamada": idx0,
                                         "idx_leitura": idx, "chave_testada": chave_t,
                                         "descarta": descarta})
                    # reatribuicao corta o rastreio entre steps
                    cortou = False
                    for n in ast.walk(arv):
                        if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
                            alvo = n.targets[0] if isinstance(n, ast.Assign) else n.target
                            if isinstance(alvo, ast.Name) and alvo.id == var \
                               and origem(n.value) != ("call", FN):
                                cortou = True
                    if cortou:
                        break

    print(f"[leituras] total rastreado: {len(linhas)}")
    grupos = defaultdict(int)
    for l in linhas:
        grupos[(l["real"], l["guardado"], l["protegido"])] += 1
    for g, n in sorted(grupos.items()):
        print(f"  real={g[0]} guardado={g[1]} protegido={g[2]}: {n}")

    erradas = [l for l in linhas if not l["real"]]
    sem_prot = [l for l in erradas if not l["guardado"] and not l["protegido"]]
    g2 = defaultdict(int)
    for l in sem_prot:
        g2[(l["conhecido"], l["tem_erro"])] += 1
    for g, n in sorted(g2.items()):
        print(f"  errada sem protecao | conhecido={g[0]} tem_erro={g[1]}: {n}")

    # consistencia: errada+desprotegida+com erro  x  os 91 conhecidos
    steps_erro = {(l["exec_id"], l["role"], l["idx_leitura"]) for l in sem_prot if l["tem_erro"]}
    inter = steps_erro & conhecidos
    print(f"[consistencia] leituras erradas+sem prot+com erro: {sum(1 for l in sem_prot if l['tem_erro'])} "
          f"em {len(steps_erro)} steps | desses, em U_contrato_dict: {len(inter)} | "
          f"conhecidos nao cobertos: {len(conhecidos - steps_erro)}")

    silenciosas = {}
    for l in sem_prot:
        if not l["conhecido"] and not l["tem_erro"]:
            silenciosas.setdefault((l["exec_id"], l["role"], l["idx_leitura"]), l)
    print(f"[silenciosas] {len(silenciosas)} ocorrencias (exec, role, idx_leitura):")
    for (ex, role, idx), l in sorted(silenciosas.items()):
        print(f"  {ex[:8]}… {role} chamada_idx={l['idx_chamada']} leitura_idx={idx} "
              f"mes={mes_de[ex]} {l['forma']}[{l['chave']!r}]")

    # guardas fantasma
    gdesc = {}
    for g in linhas_g:
        if g["descarta"]:
            gdesc.setdefault((g["exec_id"], g["role"], g["idx_leitura"]), g)
    print(f"[guardas-fantasma] total={len(linhas_g)} descartando documentos={len(gdesc)}:")
    for (ex, role, idx), g in sorted(gdesc.items()):
        print(f"  {ex[:8]}… {role} idx={idx} chave_testada={g['chave_testada']!r} mes={mes_de[ex]}")

    # as 5: resposta real do managerAgent
    casos5 = sorted(set(silenciosas) | set(gdesc))
    print("[finais] resposta real do managerAgent nas execucoes confirmadas:")
    for ex, role, idx in casos5:
        finais = [st for st in passos.get((ex, "managerAgent"), {}).values()
                  if st.get("is_final_answer")]
        if not finais:
            print(f"  {ex[:8]}… SEM step final do managerAgent")
            continue
        txt = str(finais[-1].get("action_output") or "")
        print(f"  {ex[:8]}… len={len(txt)} DEGENERADO={bool(DEGENERADO.search(txt))} "
              f"None/null={bool(NULO.search(txt))} parece_dict={bool(DICT_IMP.search(txt))}")

    # diff contra a tabela publicada
    pub = {}
    with open(os.path.join(EVID, "derivados", "leituras_universo_completo.csv")) as f:
        for r in csv.DictReader(f):
            pub.setdefault((r["exec_id"], r["role"], int(r["idx_chamada"]), int(r["idx_leitura"]),
                            r["forma"], r["chave"]), []).append(r)
    minhas = defaultdict(int)
    for l in linhas:
        minhas[(l["exec_id"], l["role"], l["idx_chamada"], l["idx_leitura"], l["forma"], l["chave"])] += 1
    so_minhas, so_pub = [], []
    for k, n in minhas.items():
        m = len(pub.get(k, []))
        if n != m:
            so_minhas.append((k, n, m))
    for k, l in pub.items():
        if k not in minhas:
            so_pub.append((k, 0, len(l)))
    print(f"[diff] leituras so na minha varredura: {len(so_minhas)} | so na publicada: {len(so_pub)}")
    for k, n, m in so_minhas[:15]:
        print("  +", k, f"minha={n} pub={m}")
    for k, n, m in so_pub[:15]:
        print("  -", k, f"pub={m}")

    # integridade dos trechos
    total, ok, falhas = 0, 0, []
    for fn_json in sorted(os.listdir(os.path.join(EVID, "derivados"))):
        if not fn_json.endswith(".json"):
            continue
        d = json.load(open(os.path.join(EVID, "derivados", fn_json)))
        cru = json.load(open(os.path.join(EVID, "crus",
                                          d["caso_segundo_o_notebook"]["exec_id"] + ".json")))
        for t in d.get("trechos_do_cru", []):
            total += 1
            try:
                v = resolver_caminho(cru, t["cru"])
            except (KeyError, IndexError, TypeError):
                v = None
            if "caracteres" in t:
                v = v[t["caracteres"][0]:t["caracteres"][1]] if isinstance(v, str) else None
            elif "mensagens" in t:
                v = [{"role": m.get("role"),
                      "texto": "".join(x.get("text", "") for x in m.get("content", []))
                              if isinstance(m.get("content"), list) else str(m.get("content") or "")}
                     for m in v[t["mensagens"][0]:t["mensagens"][1]]]
            if t["texto"] is None or v == t["texto"]:
                ok += 1
            else:
                falhas.append((fn_json, t["o_que"]))
    print(f"[trechos] {ok}/{total} conferem; divergentes: {falhas if falhas else 'nenhum'}")

if __name__ == "__main__":
    main()
