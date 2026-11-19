"""Simula duas mudanças propostas no padrão do resíduo, sem mudar o pipeline:
  A · a máscara troca também o endereço hexadecimal (`0x…`) por `<id>`;
  B · A, e o corte de 90 caracteres da frase passa a ser feito DEPOIS da máscara, não antes.

A máscara de hoje (`base_pipeline.mascarar`) troca aspas, crases e números, mas não as letras de um endereço de memória
em hexadecimal (`Table@0x7F3B2D1E` → `Table@<n>x<n>F<n>B<n>D<n>E<n>`): o mesmo erro vira um padrão por execução, e a
régua de recorrência, que é aplicada a cada padrão, não o vê voltar (racional do resíduo, base 1 `docs/18` §2,
"divisão excessiva"). Este script lê o `casos.csv` que o `especificas/residuo.py` gravou, recalcula o padrão de cada
erro com a máscara proposta (a mesma `padrao_residuo()` do pipeline, só com a máscara trocada, em memória) e mostra:
  - quantos erros mudam de padrão (só podem ser os que têm `0x` na mensagem);
  - os padrões que se juntam (antes → depois) e os que só mudam de texto;
  - padrões e padrões que passam na recorrência, antes e depois, com a régua da triagem da base 3.

Por que B. Hoje `padrao_residuo()` pega até 90 caracteres da frase ORIGINAL e só depois mascara: se dois erros iguais
têm números de tamanhos diferentes ("3 rows" × "12 rows"), o corte cai em pontos diferentes e o fim do padrão sai
diferente (na base 3, 1 dos 13 `LayoutError` ficou fora do padrão dos outros 12). E o corte pode cair dentro de aspas:
a aspa fica sem par e o trecho não é mascarado. Cortando depois da máscara, o padrão tem sempre os mesmos 90
caracteres mascarados. Em B mudam também padrões sem `0x` (o texto do fim de mensagens longas): a saída lista as
junções, para conferir que cada uma é o mesmo erro, e conta os padrões que só mudam de texto.

Não grava nada e não muda nenhum arquivo do hash da rodada. Imprime só contagens e padrões mascarados. Uso, da raiz,
no ambiente da base, depois do `residuo.py`:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/simular_mascara_hex.py
        [--casos analysis/2026-10-trace-law-flow-third/pipeline/resultados/mineracao/residuo/casos.csv]
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
import base_pipeline as bp  # noqa: E402
from especificas.residuo import tabela_padroes  # noqa: E402

HEX = re.compile(r"\b0x[0-9a-fA-F]+\b")


def mascarar_proposta(frase):
    """A máscara de hoje, com o endereço hexadecimal trocado por `<id>` antes dos números."""
    frase = re.sub(r"'[^']*'|\"[^\"]*\"", "<q>", frase)
    frase = re.sub(r"`[^`]*`", "<id>", frase)
    frase = HEX.sub("<id>", frase)
    return re.sub(r"\d+", "<n>", frase).strip()


def padrao_cortado_depois(m, sub, err_type):
    """B: a `padrao_residuo()` com a máscara A e o corte de 90 caracteres feito sobre a frase JÁ mascarada. Muda só o
    ramo "classe: frase" (a sintaxe não tem corte; os ramos sem frase são os mesmos)."""
    if sub != "codigo_mal_escrito":
        k = re.findall(r"(\b\w+(?:Error|Exception)\b):\s*([^\n]*)", m)
        if k:
            return f"{k[-1][0]}: {mascarar_proposta(k[-1][1])[:90].strip()}"
    return bp.padrao_residuo(m, sub, err_type)


def padroes_propostos(C, cortar_depois=False):
    """O padrão de cada erro com a proposta (a `padrao_residuo()` do pipeline, com a máscara trocada em memória)."""
    original = bp.mascarar
    bp.mascarar = mascarar_proposta
    f = padrao_cortado_depois if cortar_depois else bp.padrao_residuo
    try:
        return [f("" if pd.isna(m) else str(m), s, None if pd.isna(t) else t)
                for m, s, t in zip(C.mensagem, C.submecanismo, C.err_type)]
    finally:
        bp.mascarar = original


def simular(C, cortar_depois=False):
    C = C.copy()
    C["situacao_mecanismo"] = "observavel"
    C["padrao_novo"] = padroes_propostos(C, cortar_depois)
    com_hex = C.mensagem.astype(str).str.contains(HEX)
    mudou = C.padrao.astype(str) != C.padrao_novo.astype(str)
    antes = tabela_padroes(C)
    depois = tabela_padroes(C.assign(padrao=C.padrao_novo))
    juncoes = (C[mudou].groupby(["unidade", "padrao_novo"]).padrao.agg(lambda s: sorted(set(s))).reset_index())
    # padrões de depois que receberam mais de um padrão de antes (inclusive um que não mudou de texto)
    origem = C.groupby(["unidade", "padrao_novo"]).padrao.agg(lambda s: sorted(set(s)))
    juntados = origem[origem.map(len) > 1].reset_index()
    return {"erros": len(C), "com_hex": int(com_hex.sum()), "mudam": int(mudou.sum()),
            "mudam_sem_hex": int((mudou & ~com_hex).sum()), "antes": antes, "depois": depois, "juncoes": juncoes,
            "juntados": juntados, "C": C}


def _imprimir(r, so_mudados):
    A, D = r["antes"], r["depois"]
    print(f"erros do resíduo: {r['erros']} · com endereço 0x: {r['com_hex']} · mudam de padrão: {r['mudam']} "
          f"(sem 0x: {r['mudam_sem_hex']}{', tem de ser 0' if so_mudados else ''})")
    print(f"padrões: {len(A)} → {len(D)} · passam na recorrência: {int(A.passa_na_recorrencia.sum())} → "
          f"{int(D.passa_na_recorrencia.sum())}")
    for b in sorted(set(A.unidade)):
        pa = bool(A.loc[A.unidade.eq(b), "passa_na_recorrencia"].any())
        pd_ = bool(D.loc[D.unidade.eq(b), "passa_na_recorrencia"].any())
        print(f"  {b}: algum padrão passa {pa} → {pd_} (decisão da triagem {'igual' if pa == pd_ else 'MUDA'})")
    lista, rotulo = ((r["juncoes"], "dos que mudaram") if so_mudados
                     else (r["juntados"], "só os que juntaram mais de um padrão de antes"))
    if not so_mudados:
        print(f"padrões que só mudam de texto (1 de antes → 1 de depois): "
              f"{int(r['juncoes'].padrao.map(len).eq(1).sum())}")
    print(f"\npadrões depois, {rotulo} (erros · execuções · meses · papéis · passa):")
    for _, j in lista.iterrows():
        d = D[(D.unidade == j.unidade) & (D.padrao == j.padrao_novo)].iloc[0]
        print(f"  {j.unidade} · {j.padrao_novo}\n      {int(d.erros)} · {int(d.execucoes)} · {int(d.meses)} · "
              f"{int(d.papeis)} · {bool(d.passa_na_recorrencia)}  ← {len(j.padrao)} padrão(ões) de antes")
        if not so_mudados:
            for p in j.padrao:
                print(f"        antes: {p}")


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", default=str(PIPELINE / "resultados" / "mineracao" / "residuo" / "casos.csv"))
    a = p.parse_args(argv)
    C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
    if "mensagem" not in C.columns:
        print("casos.csv sem a coluna `mensagem`: rode o `especificas/residuo.py` desta versão")
        return 1
    print("== A · só o endereço hexadecimal ==")
    r = simular(C)
    _imprimir(r, so_mudados=True)
    print("\n== B · A + cortar depois de mascarar ==")
    b = simular(C, cortar_depois=True)
    _imprimir(b, so_mudados=False)
    return 0 if r["mudam_sem_hex"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
