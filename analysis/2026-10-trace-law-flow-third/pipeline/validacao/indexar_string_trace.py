"""Evidência, num trace completo (base 1 por padrão; base 2 com --trace), da hipótese do roadmap b3 #34: o "Could not index" com `string indices must be
integers` é o agente indexando TEXTO como se fosse dict (o retorno da ferramenta chega como string).

Para cada ActionStep com "Could not index" na mensagem de erro: como o valor indexado começa (`{"` = JSON em texto,
`{'` = dict ou repr Python em texto, `[`, outro), como a mensagem termina, qual função produziu a variável indexada
(a atribuição `var = funcao(` no código do passo ou dos anteriores do mesmo papel) e o que o agente faz no passo
seguinte (usa `json.loads`/`ast.literal_eval`? erra de novo?). Reprodução do mecanismo no sandbox: dict → KeyError;
texto (JSON ou repr) → `string indices must be integers` (smolagents 1.26.0, 14/10).

Saída: só contagens, nomes de papel e nomes de função. Na base 1, os identificadores ficam em
`2026-09-trace-law-flow/pipeline/resultados/evidencia/34_indexar_string/casos.csv` (fora do git); em outra base, só
com --evidencia (uma pasta fora do repositório). Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/indexar_string_trace.py
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/indexar_string_trace.py --trace <trace da base 2>
Resultado na base 1 (14/10): 136 "Could not index"; 37 com o erro de string, nenhum com valor começando por `{`
(9 `[`, 28 texto); 13 dos 37 desserializam no passo seguinte; 88 retorno-dict (`{'`, `get_available_documents`).
"""
import argparse
import json
from pathlib import Path
import re
import sys

import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ANALYSIS))
from leitor_trace import ler_trace

TRACE = ANALYSIS / "2026-09-trace-law-flow/data/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"
SAIDA_BASE1 = ANALYSIS / "2026-09-trace-law-flow/pipeline/resultados/evidencia/34_indexar_string"
REPO = ANALYSIS.parent
FIM = [("string indices must be integers", re.compile(r"string indices must be integers(, not '\w+')?\s*$")),
       ("KeyError: <número>", re.compile(r"KeyError: \d+\s*$")),
       ("KeyError: '<campo>'", re.compile(r"KeyError: '[^']*'\s*$")),
       ("list indices must be integers", re.compile(r"list indices must be integers[^\n]*$"))]
LINHA = re.compile(r"failed at line '(.*?)' due to", re.S)


def comeco(m):
    i = m.find("Could not index ")
    v = m[i + 16:i + 18]
    return {'{"': '{" (JSON em texto)', "{'": "{' (dict ou repr em texto)"}.get(v, "[" if v[:1] == "[" else "outro")


def fim(m):
    return next((r for r, rx in FIM if rx.search(m.strip())), "outro fim")


def produtora(linha, codigos):
    v = re.search(r"(\w+)\s*\[", linha or "")
    if not v:
        return "(variável não lida)"
    for code in reversed(codigos):   # a atribuição mais recente vence
        a = re.findall(rf"\b{re.escape(v.group(1))}\s*=\s*([\w.]+)\s*\(", code or "")
        if a:
            return a[-1]
    return "(atribuição não achada)"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", type=Path, default=TRACE, help="trace cru completo (CSV ou parquet); padrão: a base 1")
    p.add_argument("--evidencia", type=Path, help="pasta para o casos.csv (fora do repositório, se não for a base 1)")
    args = p.parse_args(argv)
    saida = args.evidencia or (SAIDA_BASE1 if args.trace.resolve() == TRACE.resolve() else None)
    if args.evidencia is not None and args.evidencia.resolve().is_relative_to(REPO.resolve()):
        p.error("--evidencia deve ficar fora do repositório: o casos.csv tem identificadores")
    df = ler_trace(str(args.trace), colunas=["cod_idef_exeo", "cod_idef_aget", "txt_etap_memo"])
    linhas = []
    for _, r in df[df.txt_etap_memo.notna()].iterrows():
        try:
            memo = json.loads(r.txt_etap_memo)
        except Exception:
            continue
        for role, steps in memo.items():
            if not isinstance(steps, list):
                continue
            acts = [s for s in steps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            for i, st in enumerate(acts):
                m = str((st.get("error") or {}).get("message") or "")
                if "Could not index" not in m:
                    continue
                prox = acts[i + 1] if i + 1 < len(acts) else None
                code_prox = (prox or {}).get("code_action") or ""
                linha = LINHA.search(m)
                linhas.append({
                    "exec_id": r.cod_idef_exeo, "agente": r.cod_idef_aget, "papel": role, "idx": i,
                    "comeco": comeco(m), "fim": fim(m), "comprimento": len(m),
                    "produtora": produtora(linha.group(1) if linha else "", [a.get("code_action") for a in acts[:i + 1]]),
                    "proximo": "sem próximo passo" if prox is None else (
                        "próximo com erro" if (prox.get("error") or {}).get("type") else "próximo sem erro"),
                    "proximo_desserializa": bool(re.search(r"json\.loads|ast\.literal_eval|eval\(", code_prox)),
                })
    t = pd.DataFrame(linhas)
    if saida is not None:
        saida.mkdir(parents=True, exist_ok=True)
        t.to_csv(saida / "casos.csv", index=False)
    print(f"'Could not index': {len(t)} | casos: {saida / 'casos.csv' if saida else 'não gravados (sem --evidencia)'}")
    print(pd.crosstab(t.comeco, t.fim, margins=True).to_string())
    s = t[t.fim.eq("string indices must be integers")]
    print(f"\n== com 'string indices must be integers': {len(s)} | mensagens > 20.000: {int((s.comprimento > 20000).sum())}")
    print("função que produziu a variável indexada:", s.produtora.value_counts().head(8).to_dict())
    print("papéis:", s.papel.value_counts().head(6).to_dict())
    print("passo seguinte:", s.proximo.value_counts().to_dict(),
          "| usa json.loads/literal_eval:", int(s.proximo_desserializa.sum()))
    c = s[s.comeco.str.startswith("{")]
    print(f"-- valor começando com '{{' e erro de string (o caso dos longos da base 3): {len(c)}")
    if len(c):
        print("   começo:", c.comeco.value_counts().to_dict(), "| papéis:", c.papel.value_counts().head(5).to_dict())
        print("   função:", c.produtora.value_counts().head(6).to_dict(), "| desserializa no seguinte:",
              int(c.proximo_desserializa.sum()), "| seguinte:", c.proximo.value_counts().to_dict())
    d = t[t.fim.eq("KeyError: <número>")]
    print(f"\n== com 'KeyError: <número>' (o retorno-dict): {len(d)} | mensagens > 20.000: {int((d.comprimento > 20000).sum())}")
    print("função que produziu a variável indexada:", d.produtora.value_counts().head(5).to_dict())
    print("começo:", d.comeco.value_counts().to_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
