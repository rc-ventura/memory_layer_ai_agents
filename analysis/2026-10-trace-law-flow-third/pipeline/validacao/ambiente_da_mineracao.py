"""Base 3: o ambiente do interpretador por papel, a partir da tabela de listas autorizadas da mineração do sandbox.

O `conferir_memorias.py` (kit) lê, em `--ambiente`, o que o interpretador mostrou de cada papel (decisão do Rafael,
21/10: a lista do prompt não é a do interpretador — dossiê do sandbox, §2h, 18–21). Nas bases 1 e 2 isso sai do trace
(`extrair_ambiente_base2.py`). A base 3 só guarda os passos com erro, mas a mineração do sandbox já grava a tabela
`imports_autorizados.csv` (`pipeline/resultados/mineracao/U_sandbox/`): cada lista da mensagem de erro "Authorized
imports are: [...]", com os erros, os papéis e os meses em que aparece. Este script a converte no formato do kit
({"fonte", "papeis": {"<papel>": {"listas": [...], "importados": {}}}}). Os meses da lista valem para todos os papéis
dela (a tabela não separa mês por papel): é aproximação, e o resultado diz a fonte. Sem `importados`: na base 3 não há
passo sem erro. Só nomes de papel e de módulo, meses e contagens. Uso, da pasta `pipeline/` da base 3:
    python validacao/ambiente_da_mineracao.py --tabela resultados/mineracao/U_sandbox/imports_autorizados.csv --saida <ambiente.json>
"""
import argparse
import csv
import datetime
import json
from pathlib import Path
import sys


def separar(texto):
    return [x.strip() for x in str(texto or "").split(",") if x.strip()]


def ambiente(linhas):
    """linhas: dicts com lista_autorizada, erros, papeis, meses → {papel: {"listas", "importados"}}."""
    papeis = {}
    for r in linhas:
        lista = {"modulos": sorted(separar(r["lista_autorizada"])), "meses": sorted(separar(r["meses"])),
                 "erros": int(r["erros"])}
        for papel in separar(r["papeis"]):
            papeis.setdefault(papel, {"listas": [], "importados": {}})["listas"].append(lista)
    return dict(sorted(papeis.items()))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tabela", required=True, type=Path, help="o imports_autorizados.csv da mineração")
    p.add_argument("--saida", required=True, type=Path)
    a = p.parse_args(argv)
    with open(a.tabela, encoding="utf-8") as fh:
        papeis = ambiente(list(csv.DictReader(fh)))
    doc = {"fonte": {"tabela": str(a.tabela), "gerado_em": datetime.date.today().isoformat(),
                     "script": "ambiente_da_mineracao.py",
                     "aproximacao": "os meses de cada lista valem para todos os papéis dela"}, "papeis": papeis}
    a.saida.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for papel, d in papeis.items():
        print(f"{papel:22} {len(d['listas'])} lista(s)")
    print(f"{len(papeis)} papéis → {a.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
