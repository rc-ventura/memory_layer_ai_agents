"""Simulação (nada é gravado): e se a assinatura `try/except NameError` passasse antes da posição do passo anterior?

A regra hoje decide o erro de nome não definido pela posição: o passo anterior teve erro → `U_estado_perdido`; não teve →
`U_nome_inventado`; não existe → pendente. A proposta (relatório §7.10) é testar antes a linha que falhou: se ela é um
`try/except NameError`, o erro vai para uma unidade própria (destino harness proposto; na base 3, em aberto).

Este script aplica a proposta SÓ na tabela em memória e confere:
  1. invariante: todo erro SEM a assinatura mantém exatamente a mesma situação (unidade ou motivo de pendência);
  2. antes × depois: erros, execuções distintas, meses distintos e tokens, por situação;
  3. cobertura: erros observáveis e pendentes, antes e depois;
  4. o que a régua da triagem (≥ 3 execuções e ≥ 2 meses) diz das unidades afetadas, antes e depois.

**Histórico:** a proposta virou o Ajuste 17 (13/10). Com o código de depois do ajuste, o "antes" já traz a unidade
nova e nada muda; os números da simulação (máquina 2, foto IMG_5721) são do código do commit `9fd032b`.

Imprime só contagens e nomes de unidade, papel e mês. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/simular_regra_assinatura.py [--fonte <parquet>]
"""
import argparse
from pathlib import Path
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE.parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import base_pipeline as bp
from contar_assinatura_try_nameerror import assinatura, situacao

NOVA = "U_verificacao_existencia (proposta; era U_verificacao_try_nameerror até o Ajuste 21)"
MIN_EXEC, MIN_MESES = 3, 2


def simular(EU):
    """Devolve a tabela com `antes` e `depois` (a situação de cada erro) e a marca `muda`."""
    T = EU.copy()
    T["antes"] = [situacao(r) for r in T.itertuples()]
    eh_nome = pd.Series([bp.submecanismo(m) in {"nome_nao_definido", "verificacao_try_nameerror"} for m in T.err_msg], index=T.index)
    T["assinatura"] = "n/a"
    T.loc[eh_nome, "assinatura"] = T.loc[eh_nome, "err_msg"].map(assinatura)
    T["depois"] = T["antes"]
    T.loc[T.assinatura.eq("try/except NameError"), "depois"] = NOVA
    T["muda"] = T.antes.ne(T.depois)
    T["chave_exec"] = T.exec_id.astype(str) + "|" + T.agente.astype(str)
    return T


def resumo(T, coluna):
    g = T.groupby(coluna).agg(erros=("step_ref", "size"), execucoes=("chave_exec", "nunique"),
                              meses=("mes", "nunique"), tokens=("tok_tot", lambda s: s.sum(min_count=1))).reset_index()
    g["passa_na_regua"] = (g.execucoes >= MIN_EXEC) & (g.meses >= MIN_MESES)
    return g.rename(columns={coluna: "situacao"})


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    args = p.parse_args(argv)
    A = bp.analisar_mecanismos_observaveis(bp.carregar_carga(args.fonte))
    T = simular(A.EU)

    print("erros estruturados:", len(T), "| mudam de situação:", int(T.muda.sum()))
    sem = T[~T.assinatura.eq("try/except NameError")]
    print("1 · invariante — erros SEM a assinatura que mudam de situação:", int(sem.muda.sum()),
          "(tem de ser 0) de", len(sem))

    pend_a = int(T.antes.str.startswith("pendente").sum()); pend_d = int(T.depois.str.startswith("pendente").sum())
    print(f"3 · cobertura — pendentes: {pend_a} ({pend_a / len(T):.1%}) → {pend_d} ({pend_d / len(T):.1%}); "
          f"com unidade: {len(T) - pend_a} → {len(T) - pend_d}")

    print("\n2 · de onde vêm os erros que mudam (antes → depois):")
    print(T[T.muda].groupby(["antes", "depois"]).size().rename("erros").reset_index().to_string(index=False))

    afet = set(T[T.muda].antes) | {NOVA}
    ant = resumo(T[T.antes.isin(afet)], "antes"); dep = resumo(T[T.depois.isin(afet)], "depois")
    print("\n4 · as situações afetadas — ANTES (erros, execuções, meses, tokens, passa na régua):")
    print(ant.to_string(index=False))
    print("\n    DEPOIS:")
    print(dep.to_string(index=False))

    N = T[T.depois.eq(NOVA)]
    print("\n   a unidade nova, por papel × mês (os 8 maiores):")
    print(N.groupby(["role", "mes"]).size().rename("erros").reset_index().sort_values("erros", ascending=False).head(8).to_string(index=False)
          if len(N) else "   (vazia)")
    print("   tokens da unidade nova:", int(N.tok_tot.sum(min_count=1)) if len(N) and N.tok_tot.notna().any() else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
