"""Gera a versão de um relatório ou dossiê que pode sair do ambiente onde o trace mora, sem máscara feita à mão.

    python versao_para_sair.py <relatório.md>

O relatório completo fica no ambiente, com os identificadores de execução nas tabelas de evidência. Este script:
  - troca cada identificador (formato UUID) por uma referência estável, `caso-1`, `caso-2`… (pela ordem em que
    aparece), em todo o texto, inclusive nos comandos de recorte;
  - grava <relatório>_saida.<ext> (a mesma extensão: .md, .json…), a versão que sai, e <relatório>_mapa.csv (referência → identificador), que NÃO sai:
    é com ele que alguém no ambiente volta da referência ao trace.
Depois rode o `varrer_pii.py` na versão `_saida.md`. Só biblioteca padrão.
"""

import csv, os, re, sys

UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    arq = sys.argv[1]
    base, ext = os.path.splitext(arq)
    txt = open(arq, encoding="utf-8").read()
    ref = {}
    saida = UUID.sub(lambda m: ref.setdefault(m.group(0), f"caso-{len(ref) + 1}"), txt)
    with open(base + "_saida" + ext, "w", encoding="utf-8") as fh:
        fh.write(saida)
    with open(base + "_mapa.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["referencia", "exec_id"]); w.writerows((r, e) for e, r in ref.items())
    print(f"{len(ref)} identificador(es) trocados por referência → {base}_saida{ext} (sai) · {base}_mapa.csv (não sai)")


if __name__ == "__main__":
    main()
