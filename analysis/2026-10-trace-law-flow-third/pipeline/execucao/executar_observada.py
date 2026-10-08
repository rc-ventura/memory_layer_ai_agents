"""Entrada sem censo: intake da fonte → análise observada → rodada privada.

--inventario-only não abre nem minera a fonte; classifica artefatos por hashes.
Não executa notebooks/Jupyter, não substitui o kit e não aprova memórias.
"""
import argparse
import json
from pathlib import Path
import sys

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import base_pipeline as bp
import mineracao_observada as mo


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventario-only", action="store_true")
    parser.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    parser.add_argument("--referencia-sha256", help="Hash esperado do snapshot; divergência interrompe.")
    parser.add_argument("--perfil", action="append", default=[], help="Unidade que passou na triagem atual.")
    parser.add_argument("--saida", type=Path, help="Subpasta privada; não sobrescreve resultados canônicos.")
    args = parser.parse_args(argv)
    if args.inventario_only:
        out = mo.HERE / "resultados" / "intake_observada"
        out.mkdir(parents=True, exist_ok=True)
        table = mo.inventariar()
        table.to_csv(out / "inventario.csv", index=False)
        print("Inventário (sem leitura de casos):", table.estado.value_counts().to_dict())
        return 0
    try:
        mo.conferir_fonte(args.fonte, args.referencia_sha256)
        analysis = bp.carregar_mineracao_observada(args.fonte)
        out = mo.gravar(analysis, args.saida, args.perfil)
    except (bp.AnaliseNaoIntegrada, OSError, ValueError):
        print("BLOQUEADO: fonte/contrato/rodada não validada. Nenhuma memória aprovada; conferir intake local.")
        return 1
    print(json.dumps(analysis.resumo, ensure_ascii=False, indent=2))
    print("Rodada:", out.name, ". taxas globais e sucesso semântico não habilitados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
