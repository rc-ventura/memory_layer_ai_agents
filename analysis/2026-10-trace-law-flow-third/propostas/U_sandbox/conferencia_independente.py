"""Conferência independente da lição U_sandbox (validador-de-script), escrita só a partir do `racional.md`.

Não importa o pipeline, o script da lição, o `minerar.py` nem a auditoria da candidata. Lê o parquet cru pelo
`analysis/leitor_trace.py` (abrir o arquivo não é lógica auditada) e o `casos.csv` do perfil da rodada com `csv`.
Grava as medidas num JSON (contagens, nomes de papel, mês, módulo e função, exec_id e step_ref; nenhum texto de caso).

    uv run python analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/conferencia_independente.py \
        --fonte <parquet> --casos <rodada>/perfis/U_sandbox/casos.csv --perfil <rodada>/perfis/U_sandbox/perfil.csv \
        --json <arquivo>
"""

import argparse, builtins, collections, csv, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "..", "..", "..")))  # analysis/
from leitor_trace import linhas_do_trace  # noqa: E402

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# ------------------------------------------------------------------ passo 1 (prosa do racional, para a auditoria)
EMBUTIDAS = set(dir(builtins))
MODULOS_VARIAVEL = {"json", "pd", "np", "re", "os", "math", "datetime"}
RE_FFE = re.compile(r"Forbidden function evaluation: '([^']+)'")
RE_IMPORT = re.compile(r"Import of|Import from|ModuleNotFound")
RE_FORBIDDEN = re.compile(r"Forbidden")
RE_VARIAVEL = re.compile(r"The variable `([^`]+)` is not defined")
# os sinais que o pipeline decide antes (o racional os nomeia; o padrão literal é a leitura deste validador)
SINAIS_ANTES = {
    "sintaxe": re.compile(r"SyntaxError|invalid syntax|Error in code parsing"),
    "could_not_index": re.compile(r"Could not index"),
    "has_no_attribute": re.compile(r"has no attribute"),
    "jsondecode": re.compile(r"JSONDecode"),
    "argumento_posicional": re.compile(r"positional argument"),
    "nao_iterador": re.compile(r"object is not an iterator"),
    "limite_passos": re.compile(r"[Mm]ax(imum)?[ _-]?(number of )?steps|Reached max"),
    "tempo_interpretador": re.compile(r"[Tt]ime ?out|timed out|execution time"),
}


def criterio_sandbox(msg):
    """Qual braço do passo 1 a mensagem satisfaz (ou None)."""
    m = RE_FFE.search(msg)
    if m and m.group(1) in EMBUTIDAS:
        return "funcao_embutida"
    if RE_IMPORT.search(msg):
        return "import_modulenotfound"
    # "Forbidden (qualquer outro)": outro Forbidden que não a avaliação de função
    if RE_FORBIDDEN.search(RE_FFE.sub("", msg)):
        return "forbidden_outro"
    v = RE_VARIAVEL.search(msg)
    if v and v.group(1) in MODULOS_VARIAVEL:
        return "variavel_modulo"
    return None


# ------------------------------------------------------------------ passo 4 (a regra específica)
REGRAS = [
    ("funcao_proibida", re.compile(r"Forbidden function evaluation: '([^']+)'")),
    ("import_bloqueado", re.compile(r"Import (?:of|from) (\S+?) is not allowed")),
    ("modulo_ausente", re.compile(r"No module named '([^']+)'")),
    ("atributo_dunder", re.compile(r"Forbidden access to dunder attribute: (\S+)")),
    ("modulo_sem_import", re.compile(r"The variable `([^`]+)` is not defined")),
]
RE_AUTORIZADOS = re.compile(r"Authorized imports are: \[([^\]]*)\]")
ROTULOS = [  # a ordem da correction_guidance no racional
    ("Não chame", "funcao_proibida"),
    ("não importe", "import_bloqueado"),
    ("importe antes de usar", "modulo_sem_import"),
    ("não existe no ambiente", "modulo_ausente"),
    ("não acesse", "atributo_dunder"),
]


def trecho_final(msg):
    return msg.rsplit("due to:", 1)[-1] if "due to:" in msg else msg


def nome_recusado(msg, integro):
    if not integro:
        return "sem_nome", None
    t = trecho_final(msg)
    for tipo, rx in REGRAS:
        m = rx.search(t)
        if m:
            return tipo, m.group(1).strip().rstrip(".,;:").strip("'\"`")
    return "sem_nome", None


def lista_autorizada(msg):
    m = RE_AUTORIZADOS.search(msg)
    if not m:
        return None
    nomes = re.findall(r"'([^']+)'", m.group(1)) or [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
    return tuple(sorted(nomes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", required=True)
    ap.add_argument("--casos", required=True)
    ap.add_argument("--perfil", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()

    # ---- a população na rodada (casos.csv do perfil; os pendentes não entram)
    casos = list(csv.DictReader(open(a.casos, encoding="utf-8", newline="")))
    casos = [c for c in casos if c.get("unidade", "U_sandbox") == "U_sandbox"]
    chave_rodada = {(c["exec_id"], c["agente"], c["role"], c["step_pos"]): c for c in casos}
    assert len(chave_rodada) == len(casos), "chave (exec_id, agente, papel, step_pos) não é única na rodada"

    # ---- a população na fonte crua (prosa do passo 1)
    colunas = ["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos", "mes_execucao", "structured_error",
               "error_type", "error_message"]
    fonte, excluidos_por_sinal, linhas, estruturados = {}, collections.Counter(), 0, 0
    chaves_fonte = collections.Counter()  # (exec, agente, papel, step_pos): a chave precisa do papel
    msgs_rodada = {}
    for r in linhas_do_trace(a.fonte, colunas=colunas):
        linhas += 1
        k = (r["cod_idef_exeo"], r["cod_idef_aget"], r["papel"], r["step_pos"])
        chaves_fonte[k] += 1
        if k in chave_rodada:
            msgs_rodada[k] = r
        if not r["error_type"]:
            continue
        estruturados += 1
        msg = r["error_message"] or ""
        braco = criterio_sandbox(msg)
        if not braco:
            continue
        sinais = [n for n, rx in SINAIS_ANTES.items() if rx.search(msg)]
        if sinais:
            for n in sinais:
                excluidos_por_sinal[n] += 1
            continue
        fonte[k] = (r, braco)

    so_rodada = sorted(set(chave_rodada) - set(fonte))
    so_fonte = sorted(set(fonte) - set(chave_rodada))

    # ---- passo 4 sobre a população da rodada, com a mensagem da fonte crua
    erros = []
    for k, c in sorted(chave_rodada.items()):
        r = msgs_rodada.get(k)
        msg = (r or {}).get("error_message", "") or ""
        integro = c.get("err_msg_estado", "sem_corte_sql") == "sem_corte_sql"
        tipo, nome = nome_recusado(msg, integro)
        primeira = (trecho_final(msg).strip().split() or [""])[0] if tipo == "sem_nome" else None
        erros.append({
            "exec_id": c["exec_id"], "agente": c["agente"], "step_ref": c["step_ref"], "step_pos": int(c["step_pos"]),
            "papel": (r or {}).get("papel") or c["role"], "papel_rodada": c["role"],
            "mes": (r or {}).get("mes_execucao") or c["mes"], "mes_rodada": c["mes"],
            "tipo": tipo, "nome": nome, "sem_nome_primeira_palavra": primeira,
            "lista": lista_autorizada(msg), "code_estado": c.get("code_estado"),
            "err_msg_estado": c.get("err_msg_estado"), "msg_na_fonte": r is not None,
        })

    n = len(erros)
    com_nome = sum(1 for e in erros if e["tipo"] != "sem_nome")
    cobertura = com_nome / n if n else 0.0
    # variante: se o "estado" fosse o do código (code_estado), não o da mensagem
    com_nome_var_code = sum(1 for e in erros if e["tipo"] != "sem_nome" and e["code_estado"] in (None, "sem_corte_sql"))

    # ---- inventário
    inv = collections.defaultdict(list)
    for e in erros:
        inv[(e["tipo"], e["nome"] or "")].append(e)
    inventario = sorted(([t, nm, len(v), len({x["exec_id"] for x in v}), len({x["papel"] for x in v}),
                          len({x["mes"] for x in v})] for (t, nm), v in inv.items()), key=lambda x: (-x[2], x[0], x[1]))
    inv_papel = sorted(collections.Counter((e["nome"] or "", e["papel"]) for e in erros).items())
    inv_mes = sorted(collections.Counter((e["nome"] or "", e["mes"]) for e in erros).items())

    listas = collections.defaultdict(list)
    for e in erros:
        if e["lista"] is not None:
            listas[e["lista"]].append(e)
    listas_out = [{"lista": list(L), "erros": len(v), "papeis": sorted({x["papel"] for x in v}),
                   "meses": sorted({x["mes"] for x in v})} for L, v in sorted(listas.items())]

    # ---- passo 6
    grupos = collections.defaultdict(list)
    for e in erros:
        if e["nome"]:
            grupos[(e["exec_id"], e["papel"], e["nome"])].append(e["step_pos"])
    repet = {k: len(v) - 1 for k, v in grupos.items() if len(v) > 1}
    papeis_todos = sorted({e["papel"] for e in erros})
    meses_todos = sorted({e["mes"] for e in erros})

    # ---- passo 8 (o que é determinado pelo racional)
    ordem = sorted(erros, key=lambda e: (e["papel"], e["mes"], e["step_ref"]))
    location, vistos = [], set()
    for e in ordem:
        if e["papel"] not in vistos:
            vistos.add(e["papel"])
            location.append({"exec_id": e["exec_id"], "step_ref": e["step_ref"], "papel": e["papel"]})
    location = location[:10]
    por_tipo = collections.Counter(e["tipo"] for e in erros if e["tipo"] != "sem_nome")
    tres = [t for t, _ in sorted(por_tipo.items(), key=lambda x: (-x[1], x[0]))[:3]]
    evidence = []
    for t in tres:
        e = next(x for x in ordem if x["tipo"] == t)
        evidence.append({"exec_id": e["exec_id"], "step_ref": e["step_ref"], "tipo": t, "nome": e["nome"]})
    nomes_por_tipo = {}
    for rot, t in ROTULOS:
        c = collections.Counter(e["nome"] for e in erros if e["tipo"] == t)
        nomes_por_tipo[rot] = [nm for nm, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))]
        nomes_por_tipo[rot + " (contagens)"] = dict(c)

    perfil = next(csv.DictReader(open(a.perfil, encoding="utf-8", newline="")))

    out = {
        "fonte": {"linhas": linhas, "erros_estruturados_tipo_preenchido": estruturados,
                  "chaves_repetidas_com_papel": sum(1 for v in chaves_fonte.values() if v > 1)},
        "passo1": {
            "populacao_rodada": len(chave_rodada),
            "populacao_fonte_prosa": len(fonte),
            "so_na_rodada": [list(k) for k in so_rodada],
            "so_na_fonte": [list(k) for k in so_fonte],
            "braco_na_fonte": dict(collections.Counter(b for _, b in fonte.values())),
            "excluidos_por_sinal_antes": dict(excluidos_por_sinal),
            "execucoes": len({e["exec_id"] for e in erros}),
            "papeis": len(papeis_todos), "papeis_lista": papeis_todos,
            "meses": len(meses_todos), "meses_lista": meses_todos,
            "papel_igual_rodada": all(e["papel"] == e["papel_rodada"] for e in erros),
            "mes_igual_rodada": all(e["mes"] == e["mes_rodada"] for e in erros),
            "mensagem_achada_na_fonte": sum(e["msg_na_fonte"] for e in erros),
            "err_msg_estado": dict(collections.Counter(e["err_msg_estado"] for e in erros)),
            "code_estado": dict(collections.Counter(e["code_estado"] for e in erros)),
        },
        "passo4": {
            "erros_por_tipo": dict(collections.Counter(e["tipo"] for e in erros)),
            "inventario": [{"tipo": t, "nome": nm, "erros": ne, "execucoes": nx, "papeis": np_, "meses": nmes}
                           for t, nm, ne, nx, np_, nmes in inventario],
            "nome_x_papel": [{"nome": k[0], "papel": k[1], "erros": v} for k, v in inv_papel],
            "nome_x_mes": [{"nome": k[0], "mes": k[1], "erros": v} for k, v in inv_mes],
            "listas_autorizadas": listas_out,
            "linhas": [{k: e[k] for k in ("exec_id", "step_ref", "papel", "mes", "tipo", "nome")} for e in erros],
        },
        "passo5": {
            "com_nome": com_nome, "populacao": n, "cobertura": cobertura, "limiar": 0.95,
            "passa": cobertura >= 0.95,
            "sem_nome_por_primeira_palavra": dict(collections.Counter(
                e["sem_nome_primeira_palavra"] for e in erros if e["tipo"] == "sem_nome")),
            "variante_estado_do_codigo": {"com_nome": com_nome_var_code,
                                          "cobertura": com_nome_var_code / n if n else 0.0},
        },
        "passo6": {
            "listas_distintas": len(listas),
            "lista_unica_em_todos_papeis_e_meses": len(listas) == 1,
            "papeis_com_lista": sorted({p for v in listas.values() for p in (x["papel"] for x in v)}),
            "erros_com_lista": sum(len(v) for v in listas.values()),
            "grupos_exec_papel_nome": len(grupos),
            "grupos_com_repeticao": len(repet),
            "erros_repetidos_depois_do_primeiro": sum(repet.values()),
        },
        "passo8": {
            "location": location, "evidence": evidence,
            "correction_guidance_nomes": nomes_por_tipo,
            "occurrences_perfil": {k: perfil[k] for k in ("erros_observaveis", "ocorrencias_condicionais",
                                                          "execucoes", "meses", "papeis")},
        },
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"populacao_rodada": n, "populacao_fonte": len(fonte), "cobertura": round(cobertura, 4),
                      "listas": len(listas), "repetidos": sum(repet.values())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
