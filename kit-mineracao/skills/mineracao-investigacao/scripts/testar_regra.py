"""Transforma a hipótese do investigador em número: aplica uma regra determinística (regex) à população inteira e,
se houver leitura, compara com ela. A regra é proposta pelo LLM; a contagem é deste script.

    python testar_regra.py <pasta-da-analise> --populacao <casos.csv> --regex '<rx>'
                           (--campo-passo code|observations|model_output|error|action_output | --campo-csv <coluna>)
                           [--onde coluna=valor ...] [--coluna-idx idx] [--ignorar-caixa]
                           [--lidos <leitura.csv> --rotulo <coluna> --alvo <valor>] [--saida <resultado.csv>]

--campo-passo  lê o campo do ActionStep (exec_id, role, idx) direto no trace da análise (o TRACE do base_pipeline),
               pelo leitor único: idx = posição entre os ActionSteps do papel, como no pipeline. `error` é a mensagem.
--campo-csv    usa uma coluna de texto da própria população.
--onde         filtra a população antes (pode repetir), como no amostrar.py.
--coluna-idx   qual coluna da população é o idx do step (ex.: idx_final para a resposta final).
--lidos        a leitura do investigador (exec_id, role, a mesma coluna de idx, e a coluna --rotulo): compara a regra
               com a leitura, tratando `--rotulo == --alvo` como o que a regra deveria pegar.

Imprime só contagens (nenhum texto, nenhum identificador). Semântica de regex: `re` do Python (a do pipeline).
"""

import argparse, csv, json, os, re, sys

CAMPOS = {"code": "code_action", "observations": "observations", "model_output": "model_output",
          "error": "error", "action_output": "action_output"}


def texto_do_campo(st, campo):
    v = st.get(CAMPOS[campo])
    if campo == "error":
        v = (v or {}).get("message") if isinstance(v, dict) else v
    return "" if v is None else (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))


def campos_do_trace(pasta, chaves, campo):
    """{(exec_id, role, idx): texto} para as chaves pedidas, lendo o trace em fluxo."""
    pipeline = os.path.join(pasta, "pipeline")
    sys.path.insert(0, pipeline)
    import base_pipeline                     # só para achar o TRACE e o leitor; nenhuma regra do pipeline é usada
    from leitor_trace import abrir_trace
    execs = {k[0] for k in chaves}
    out = {}
    with abrir_trace(base_pipeline.TRACE, colunas=["cod_idef_exeo", "txt_etap_memo"]) as linhas:
        for r in linhas:
            if r["cod_idef_exeo"] not in execs or not r["txt_etap_memo"]:
                continue
            try:
                memo = json.loads(r["txt_etap_memo"])
            except Exception:
                continue
            for role, steps in memo.items():
                if not isinstance(steps, list):
                    continue
                acts = [s for s in steps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
                for i, st in enumerate(acts):
                    k = (r["cod_idef_exeo"], role, i)
                    if k in chaves:
                        out[k] = texto_do_campo(st, campo)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("--populacao", required=True); ap.add_argument("--regex", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--campo-passo", choices=list(CAMPOS)); g.add_argument("--campo-csv")
    ap.add_argument("--onde", action="append", default=[]); ap.add_argument("--coluna-idx", default="idx"); ap.add_argument("--ignorar-caixa", action="store_true")
    ap.add_argument("--lidos"); ap.add_argument("--rotulo"); ap.add_argument("--alvo"); ap.add_argument("--saida")
    a = ap.parse_args()
    rx = re.compile(a.regex, re.I if a.ignorar_caixa else 0)

    with open(a.populacao, encoding="utf-8", newline="") as fh:
        pop = list(csv.DictReader(fh))
    for cond in a.onde:
        col, val = cond.split("=", 1)
        pop = [r for r in pop if r.get(col) == val]
    chave = lambda r: (r["exec_id"], r["role"], int(float(r[a.coluna_idx]))) if r.get(a.coluna_idx) not in (None, "") else None
    chaves = {chave(r) for r in pop if chave(r)}
    if a.campo_passo:
        textos = campos_do_trace(os.path.abspath(a.pasta), chaves, a.campo_passo)
    else:
        textos = {chave(r): r.get(a.campo_csv) or "" for r in pop if chave(r)}
    casou = {k: bool(rx.search(textos[k])) for k in chaves if k in textos}
    sem_texto = len(chaves) - len(casou)

    n = sum(casou.values())
    print(f"população: {len(pop)} linhas, {len(chaves)} steps distintos · regra casa em {n} "
          f"({n / max(len(casou), 1):.0%})" + (f" · {sem_texto} sem texto no campo" if sem_texto else ""))

    if a.lidos:
        if not (a.rotulo and a.alvo):
            sys.exit("--lidos pede --rotulo e --alvo")
        with open(a.lidos, encoding="utf-8", newline="") as fh:
            lidos = [r for r in csv.DictReader(fh) if chave(r) in casou]
        vp = sum(1 for r in lidos if casou[chave(r)] and r[a.rotulo] == a.alvo)
        fp = sum(1 for r in lidos if casou[chave(r)] and r[a.rotulo] != a.alvo)
        fn = sum(1 for r in lidos if not casou[chave(r)] and r[a.rotulo] == a.alvo)
        vn = len(lidos) - vp - fp - fn
        print(f"contra a leitura ({len(lidos)} lidos; alvo `{a.rotulo} = {a.alvo}`): "
              f"pega certo {vp} · pega a mais {fp} · deixa de pegar {fn} · deixa certo {vn} · "
              f"concordância {(vp + vn) / max(len(lidos), 1):.0%}")
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh); w.writerow(["exec_id", "role", a.coluna_idx, "casou"])
            w.writerows([*k, v] for k, v in sorted(casou.items()))


if __name__ == "__main__":
    main()
