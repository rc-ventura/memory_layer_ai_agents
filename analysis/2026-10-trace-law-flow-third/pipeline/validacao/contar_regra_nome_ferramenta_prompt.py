"""Ajuste 37, a evidência do destino: o prompt de sistema já proíbe dar a uma variável o nome de uma ferramenta.

O grupo "nome de ferramenta usado como variável" do resíduo da base 3 (49 erros, `U_nome_ferramenta_como_variavel`) é
memória de reforço, não sinal de harness nem memória nova, porque o prompt padrão do framework (smolagents) já traz,
na lista "Here are the rules you should always follow", a regra "Don't name any new variable with the same name as a
tool: for instance don't name a variable 'final_answer'". A base 3 não tem prompt de sistema (o adaptador o marca
`nao_exportado`). Por isso a contagem é feita num trace completo (base 1 aqui, base 2 no ambiente da base), nos
mesmos papéis.

Mede, por papel, nas execuções com prompt (o prompt é a 1ª mensagem do 1º ActionStep do papel, como no
`base_pipeline.py`):
  - quantas trazem a regra ("same name as a tool") e com que texto (a frase é do framework; muda só o número);
  - quantas declaram cada um dos nomes do grupo (`def <nome>(`);
  - quantas atribuem `final_answer =` no próprio prompt (o prompt induziria o erro).

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel e a frase da regra (texto
do framework, sem dado de cliente). Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_regra_nome_ferramenta_prompt.py
        [--trace <arquivo do trace completo>]     (padrão: o trace da base 1)
"""
import argparse
from collections import Counter, defaultdict
import glob
import json
from pathlib import Path
import re
import sys

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ / "analysis"))

REGRA = re.compile(r"[^\n]*same name as a tool[^\n]*")
NOMES = ["final_answer", "resposta_final", "calculo_horas_extras", "calculo_enquadramento", "exp"]


def prompt_do_papel(steps):
    """A 1ª mensagem do 1º ActionStep com model_input_messages (o prompt de sistema), ou '' se não houver."""
    for st in steps:
        if isinstance(st, dict) and st.get("__class__") == "ActionStep" and st.get("model_input_messages"):
            m0 = st["model_input_messages"][0]
            c = m0.get("content") if isinstance(m0, dict) else None
            return c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
    return ""


def medir(memos):
    """memos: os `txt_etap_memo` (JSON) das execuções. Devolve {papel: Counter} e as frases da regra."""
    por, frases = defaultdict(Counter), Counter()
    for txt in memos:
        try:
            memo = json.loads(txt)
        except (TypeError, ValueError):
            continue
        for papel, steps in memo.items():
            p = prompt_do_papel(steps) if isinstance(steps, list) else ""
            if not p:
                continue
            c = por[papel]
            c["execuções"] += 1
            r = REGRA.search(p)
            if r:
                c["regra"] += 1
                frases[re.sub(r"^\s*\d+\.\s*", "", r.group(0).strip())] += 1
            for n in NOMES:
                c[f"def {n}"] += bool(re.search(rf"def\s+{n}\s*\(", p))
            c["atribui final_answer"] += bool(re.search(r"\bfinal_answer\s*=(?!=)", p))
    return por, frases


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--trace", default=None)
    args = a.parse_args(argv)
    from leitor_trace import ler_trace
    trace = args.trace or glob.glob(str(RAIZ / "analysis/2026-09-trace-law-flow/data/*.csv.xz"))[0]
    por, frases = medir(ler_trace(trace)["txt_etap_memo"])
    print("a regra no prompt (sem o número):")
    for f, k in frases.items():
        print(f"  {k}x | {f}")
    tot = sum(c["execuções"] for c in por.values())
    print(f"execuções-papel com prompt: {tot} · com a regra: {sum(c['regra'] for c in por.values())}")
    print("papel | execuções | com a regra | " + " | ".join(f"def {n}" for n in NOMES) + " | atribui final_answer")
    for papel, c in sorted(por.items(), key=lambda kv: -kv[1]["execuções"]):
        print(f"  {papel} | {c['execuções']} | {c['regra']} | " + " | ".join(str(c[f'def {n}']) for n in NOMES)
              + f" | {c['atribui final_answer']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
