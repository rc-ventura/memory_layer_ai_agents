"""Base 3: abrir um caso (o passo do erro e os vizinhos) e gravar a evidência de uma amostra — o contrato do kit.

A base 3 só guarda os ActionSteps com erro, cada um com a janela que a extração trouxe: o passo anterior (n-1), o do
erro (n) e os dois seguintes (n+1, n+2) — o código, a saída do modelo, as observações e o erro de cada um. Não guarda o
prompt nem o resto da execução. O kit de mineração (skill mineracao-base, `montar_evidencia.py`) chama
`drill_down.py evidencia <nome>` na pasta `pipeline/` da análise e o bloco de evidência manda abrir cada caso com
`drill_down.py caso <exec_id> <papel>`; o `drill_down.py` da base 1 faz isso no trace inteiro, este faz na janela.
Feito para o degrau 3 do fechamento do sandbox (ler os casos de cada memória na base 3; decisão do Rafael, 22/10;
dossiê do sandbox §2h, 26).

    python drill_down.py tabela <memoria_id> [--de mineracao/U_sandbox/erros_lidos.csv]
        → resultados/mineracao/<unidade>/casos_<memoria_id>.csv: os erros da memória (exec_id, agente, role, idx = a
          posição do passo, mes, memoria_id, step_ref), a população para o `montar_evidencia.py --de`
    python drill_down.py caso <exec_id> <papel> [<idx>] [--max 4000]
        → a janela de cada erro do papel nessa execução (ou só o do idx), campo a campo, com o nome da coluna
    python drill_down.py evidencia <nome>
        → para cada caso de resultados/evidencia/<nome>/casos.csv: crus/<exec_id>__<papel>__<idx>.json (a linha inteira
          da fonte) e derivados/<…>.md (a janela); a última linha diz quantos crus conferem

A fonte é a do pipeline (`base_pipeline.TRACE`, a extração v2) ou a da variável de ambiente `DRILL_DOWN_FONTE`. O texto
dos casos fica na máquina da base (`resultados/` é git-ignored).
"""
import argparse
import csv
import json
import os
from pathlib import Path
import sys

import pyarrow.compute as pc
import pyarrow.parquet as pq

PIPELINE = Path(__file__).resolve().parent
RESULTADOS = PIPELINE / "resultados"
CHAVE = ("cod_idef_exeo", "papel", "step_pos")
# a janela: (rótulo, [(campo, coluna da fonte)]) — a ordem em que o leitor vê o caso
JANELA = [
    ("passo anterior (n-1)", [("passo", "prev_step_number"), ("saída do modelo", "prev_model_output"),
                              ("código", "prev_code_action"), ("observações", "prev_observations"),
                              ("erro", "prev_error_type")]),
    ("passo do erro (n)", [("passo", "step_number"), ("saída do modelo", "error_model_output"),
                           ("código", "error_code_action"), ("observações", "error_observations"),
                           ("erro", "error_type"), ("mensagem", "error_message")]),
    ("passo seguinte (n+1)", [("passo", "next_step_number"), ("saída do modelo", "next_model_output"),
                              ("código", "next_code_action"), ("observações", "next_observations"),
                              ("erro", "next_error_type"), ("mensagem", "next_error_message"),
                              ("resposta final", "next_is_final_answer")]),
    ("passo n+2", [("passo", "next2_step_number"), ("saída do modelo", "next2_model_output"),
                   ("código", "next2_code_action"), ("observações", "next2_observations"),
                   ("erro", "next2_error_type"), ("mensagem", "next2_error_message"),
                   ("resposta final", "next2_is_final_answer")]),
]


def fonte():
    if os.environ.get("DRILL_DOWN_FONTE"):
        return Path(os.environ["DRILL_DOWN_FONTE"])
    sys.path.insert(0, str(PIPELINE))
    import base_pipeline as bp
    return Path(bp.TRACE)


def linhas(exec_id, papel, idx=None, caminho=None):
    """As linhas da fonte do erro (ou dos erros) desse papel nessa execução, pela posição."""
    t = pq.read_table(caminho or fonte())
    m = pc.and_(pc.equal(t["cod_idef_exeo"], str(exec_id)), pc.equal(t["papel"], str(papel)))
    if idx not in (None, ""):
        m = pc.and_(m, pc.equal(pc.cast(t["step_pos"], "int64"), int(idx)))
    return sorted(t.filter(m).to_pylist(), key=lambda r: int(r["step_pos"]))


def janela(r, maximo=None):
    """A janela de um erro, em markdown, com o nome da coluna de cada trecho (o caminho no cru)."""
    L = [f"### Erro em `{r['papel']}` · posição {r['step_pos']} · {r.get('mes_execucao')}", ""]
    for rotulo, campos in JANELA:
        L.append(f"**{rotulo}**")
        for nome, col in campos:
            v = r.get(col)
            if v in (None, ""):
                continue
            v = str(v)
            if maximo and len(v) > maximo:
                v = v[:maximo] + f" […] ({len(v)} caracteres)"
            L.append(f"- {nome} (`{col}`):" + (f"\n```\n{v}\n```" if "\n" in v or len(v) > 80 else f" {v}"))
        L.append("")
    return "\n".join(L)


def tabela(memoria_id, de):
    unidade = memoria_id.split(".")[0]
    origem = RESULTADOS / de
    with open(origem, encoding="utf-8", newline="") as fh:
        sel = [r for r in csv.DictReader(fh) if r.get("memoria_id") == memoria_id]
    if not sel:
        sys.exit(f"nenhum erro de {memoria_id} em {de}")
    destino = RESULTADOS / "mineracao" / unidade / f"casos_{memoria_id}.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    campos = ["exec_id", "agente", "role", "idx", "mes", "memoria_id", "step_ref"]
    with open(destino, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows({**{c: r.get(c, "") for c in campos}, "idx": r["step_pos"]} for r in sel)
    print(f"{memoria_id}: {len(sel)} erros → resultados/{destino.relative_to(RESULTADOS)}")


def evidencia(nome, caminho=None):
    pasta = RESULTADOS / "evidencia" / nome
    with open(pasta / "casos.csv", encoding="utf-8", newline="") as fh:
        casos = list(csv.DictReader(fh))
    (pasta / "crus").mkdir(exist_ok=True)
    (pasta / "derivados").mkdir(exist_ok=True)
    ok = 0
    for c in casos:
        rs = linhas(c["exec_id"], c["role"], c.get("idx"), caminho)
        if len(rs) != 1:
            continue
        base = f"{c['exec_id']}__{c['role']}__{c.get('idx')}"
        (pasta / "crus" / f"{base}.json").write_text(json.dumps(rs[0], ensure_ascii=False, indent=2, default=str),
                                                    encoding="utf-8")
        (pasta / "derivados" / f"{base}.md").write_text(janela(rs[0]) + "\n", encoding="utf-8")
        ok += 1
    print(f"crus conferidos: {ok} de {len(casos)} (a linha da fonte achada pela chave exec_id × papel × posição)")
    return 0 if ok == len(casos) else 1


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tabela"); t.add_argument("memoria_id")
    t.add_argument("--de", default="mineracao/U_sandbox/erros_lidos.csv")
    c = sub.add_parser("caso"); c.add_argument("exec_id"); c.add_argument("papel"); c.add_argument("idx", nargs="?")
    c.add_argument("--max", type=int, default=4000)
    e = sub.add_parser("evidencia"); e.add_argument("nome")
    a = p.parse_args(argv)
    if a.cmd == "tabela":
        tabela(a.memoria_id, a.de)
        return 0
    if a.cmd == "caso":
        rs = linhas(a.exec_id, a.papel, a.idx)
        if not rs:
            print("nenhum erro com essa chave na fonte")
            return 1
        print("\n".join(janela(r, a.max) for r in rs))
        return 0
    return evidencia(a.nome)


if __name__ == "__main__":
    raise SystemExit(main())
