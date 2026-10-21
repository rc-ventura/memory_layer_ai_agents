"""Rodada de ensaio: a base 1 pela porta da query, gravada como uma rodada da base 3 (procedimento 06, §3).

Serve para ensaiar a mineração de candidata (`especificas/minerar.py`) aqui, onde a base 1 está, antes de rodar na
base real. A base 1 passa pela `porta_query_v1` (a mesma extração que gerou a base 3), o parquet resultante vira a
fonte, e a análise observada grava a rodada com o perfil de todas as candidatas. Imprime só contagens.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/rodada_base1.py [--saida <subpasta>]

A saída padrão é `pipeline/resultados/ensaio_base1/` (git-ignored): a fonte em `fonte_base1_v1.parquet` e a rodada
em `rodada/`. A rodada é da extração v1 (a porta reproduz o corte SUBSTR).
"""
import argparse
from pathlib import Path
import sys

PIPELINE = Path(__file__).resolve().parents[1]
ANALYSIS = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(ANALYSIS))
import matplotlib
matplotlib.use("Agg")
import base_pipeline as bp
import mineracao_observada as mo
from leitor_trace import ler_trace
from validacao.comparar_base1 import base1
from validacao.porta_query_v1 import porta_v1


def gerar(pasta):
    pasta = Path(pasta).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    fonte = pasta / "fonte_base1_v1.parquet"
    if not fonte.exists():
        antes = set(sys.modules)
        trace = base1().TRACE
        # o base1() põe a pipeline da base 1 no sys.path; tirá-la (e os módulos que vieram de lá) para a gravação
        # usar os módulos da base 3 (genealogia_sankey, paleta) e não os homônimos da base 1
        pasta_b1 = str(Path(trace).resolve().parent.parent / "pipeline")
        sys.path[:] = [x for x in sys.path if Path(x).resolve() != Path(pasta_b1).resolve()]
        for nome in set(sys.modules) - antes:
            if (getattr(sys.modules[nome], "__file__", "") or "").startswith(pasta_b1):
                del sys.modules[nome]
        v1, _, cont = porta_v1(ler_trace(trace), False)
        v1.to_parquet(fonte, index=False)
        print("porta da query:", {k: cont[k] for k in ("action_steps", "estruturados")})
    mo.conferir_fonte(fonte, extracao="v1")
    analise = bp.carregar_mineracao_observada(fonte, "v1")
    triagem = analise.tabelas["triagem_visivel_observada"]
    candidatas = sorted(triagem.loc[triagem.decisao.eq(mo.CANDIDATO), "unidade"])
    rodada = mo.gravar(analise, pasta / "rodada", candidatas)
    print(f"rodada {analise.manifesto['rodada_id'][:16]} em {rodada} · {len(candidatas)} candidatas com perfil:",
          ", ".join(candidatas))
    return rodada


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", type=Path, default=PIPELINE / "resultados" / "ensaio_base1",
                   help="subpasta de pipeline/resultados/ (a rodada vai em <saida>/rodada)")
    gerar(p.parse_args(argv).saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
