"""Transforma a hipótese do investigador em número: aplica uma regra determinística (regex) à população inteira e,
se houver leitura, compara com ela. A regra é proposta pelo LLM; a contagem é deste script.

    python testar_regra.py <pasta-da-analise> --populacao <casos.csv>
                           (--regex '<rx>' (--campo-passo code|observations|model_output|error|action_output | --campo-csv <coluna>)
                            | --condicao '<expressão sobre as colunas da população>')
                           [--onde coluna=valor ...] [--coluna-idx idx] [--deslocamento N] [--ignorar-caixa]
                           [--lidos <leitura.csv> --rotulo <coluna> --alvo <valor>] [--saida <resultado.csv>]

--campo-passo  lê o campo do ActionStep (exec_id, role, idx) direto no trace da análise (o TRACE do base_pipeline),
               pelo leitor único: idx = posição entre os ActionSteps do papel, como no pipeline. `error` é a mensagem.
--campo-csv    usa uma coluna de texto da própria população.
--condicao     regra numérica ou lógica sobre as colunas da própria população, em Python, sem trace (ex.:
               "tok_out > 3 * chars / 3 and chars < 20"). Coluna numérica vira número; o resto, texto.
--onde         filtra a população antes (pode repetir), como no amostrar.py (=, !=, >=, <=).
--deslocamento  com --campo-passo, lê o step idx+N em vez do próprio (ex.: -1 = o step anterior ao erro, para regras
               do tipo "o step anterior chamou a ferramenta X"). Caso sem esse step conta como "sem texto".
--coluna-idx   qual coluna da população é o idx do step (ex.: idx_final para a resposta final).
--lidos        a leitura do investigador (exec_id, role, a mesma coluna de idx, e a coluna --rotulo): compara a regra
               com a leitura, tratando `--rotulo == --alvo` como o que a regra deveria pegar.

Imprime só contagens (nenhum texto, nenhum identificador). Semântica de regex: `re` do Python (a do pipeline).
"""

import argparse, csv, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mineracao-base", "scripts"))
from amostrar import aplicar_onde   # o mesmo filtro da amostra e da evidência (as skills são instaladas lado a lado)

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
    ap.add_argument("pasta"); ap.add_argument("--populacao", required=True)
    regra = ap.add_mutually_exclusive_group(required=True)
    regra.add_argument("--regex"); regra.add_argument("--condicao")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--campo-passo", choices=list(CAMPOS)); g.add_argument("--campo-csv")
    ap.add_argument("--onde", action="append", default=[]); ap.add_argument("--coluna-idx", default="idx")
    ap.add_argument("--deslocamento", type=int, default=0); ap.add_argument("--ignorar-caixa", action="store_true")
    ap.add_argument("--lidos"); ap.add_argument("--rotulo"); ap.add_argument("--alvo"); ap.add_argument("--saida")
    a = ap.parse_args()
    if a.regex and not (a.campo_passo or a.campo_csv):
        sys.exit("--regex pede --campo-passo ou --campo-csv")
    rx = re.compile(a.regex, re.I if a.ignorar_caixa else 0) if a.regex else None

    with open(a.populacao, encoding="utf-8", newline="") as fh:
        pop = list(csv.DictReader(fh))
    pop = aplicar_onde(pop, a.onde)
    chave = lambda r: (r["exec_id"], r["role"], int(float(r[a.coluna_idx]))) if r.get(a.coluna_idx) not in (None, "") else None
    chaves = {chave(r) for r in pop if chave(r)}
    if a.condicao:
        def valor(x):
            try: return float(x)
            except (TypeError, ValueError): return x
        casou = {}
        for r in pop:
            if chave(r):
                casou[chave(r)] = casou.get(chave(r), False) or bool(
                    eval(a.condicao, {"__builtins__": {}}, {k: valor(v) for k, v in r.items()}))
        textos = casou
    elif a.campo_passo:
        alvo = {k: (k[0], k[1], k[2] + a.deslocamento) for k in chaves}
        lidos = campos_do_trace(os.path.abspath(a.pasta), set(alvo.values()), a.campo_passo)
        textos = {k: lidos[v] for k, v in alvo.items() if v in lidos}
    else:
        textos = {chave(r): r.get(a.campo_csv) or "" for r in pop if chave(r)}
    if not a.condicao:
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
