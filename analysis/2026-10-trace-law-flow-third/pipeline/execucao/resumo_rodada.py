"""Resumo de uma rodada observada para levar da máquina 2: só contagens, nomes de unidade e motivos.

Lê a pasta da rodada (a mais recente em resultados/observada_*, ou --rodada) e imprime:
  1. o resumo do manifesto (erros, elegíveis, observáveis, pendentes, candidatas, tokens);
  2. a triagem visível (unidade, decisão, erros, execuções, meses, papéis, tokens);
  3. a cobertura dos mecanismos (situação, motivo, erros, tokens).
Nenhum identificador de execução nem texto de caso. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/resumo_rodada.py [--rodada <pasta>]
"""
import argparse
import json
from pathlib import Path

import pandas as pd

RESULTADOS = Path(__file__).resolve().parents[1] / "resultados"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", type=Path)
    args = p.parse_args(argv)
    if args.rodada:
        pasta = args.rodada
    else:
        rodadas = sorted(RESULTADOS.glob("observada_*/manifesto.json"), key=lambda m: m.stat().st_mtime)
        if not rodadas:
            print("Nenhuma rodada em", RESULTADOS, "- rode antes: executar.py analisar")
            return 1
        pasta = rodadas[-1].parent
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    r = m["resumo"]
    print("RODADA", pasta.name, "| estado:", m.get("estado"))
    for k in ["erros_estruturados", "suspeitas_fora_taxonomia", "sintomas_elegiveis", "mensagem_limitada",
              "mecanismos_observaveis", "pendentes", "unidades_observaveis", "candidatas_observadas",
              "tokens_estruturados_conhecidos"]:
        print(f"  {k}: {r.get(k)}")
    pd.set_option("display.width", 200, "display.max_columns", 20, "display.max_rows", 200)
    t = pd.read_csv(pasta / "triagem_visivel_observada.csv")
    t["tokens_mi"] = (t.tokens_n_conhecidos / 1e6).round(1)
    print("\nTRIAGEM")
    print(t[["unidade", "decisao", "erros_observaveis", "execucoes", "meses", "papeis", "tokens_mi"]].to_string(index=False))
    c = pd.read_csv(pasta / "cobertura_mecanismos.csv")
    c["tokens_mi"] = (c.tokens_n_conhecidos / 1e6).round(1)
    print("\nCOBERTURA DOS MECANISMOS")
    print(c[["situacao_mecanismo", "motivo_evidencia", "erros", "tokens_mi"]]
          .sort_values("erros", ascending=False).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
