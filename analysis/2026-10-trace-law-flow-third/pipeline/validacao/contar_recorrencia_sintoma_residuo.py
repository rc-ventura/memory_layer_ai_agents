"""Base 3: o que sobrou do balde "sintoma não reconhecido" (b3 #5) — cada grupo recorre? Vale investigar?

Depois dos Ajustes 35 a 38 o balde tem 44 erros em poucos padrões pequenos. Antes de investigar qualquer grupo, a
pergunta é a da régua da triagem (procedimento do resíduo, passo 3): o grupo aparece em pelo menos 3 execuções e em pelo
menos 2 meses? Um grupo que não passa não ganha regra: fica no resíduo com o motivo, decidido junto com os outros
(`decisoes.md`, 12/11: a meta não é zerar o resíduo).

Os grupos são hipóteses de mecanismo lidas pela mensagem (o primeiro que casa vale), não unidades:
  recusa_llm          política de conteúdo do LLM — já decidido em 11/11 (em observação); entra só para a conta fechar
  pdf_layout          `LayoutError`: uma linha de tabela maior que a página do PDF
  decodificar_barra   `UnicodeDecodeError`: texto terminado em barra solta
  dado_tipo_ou_conta  `.str` em número, data que não converte, divisão por zero
  etapa_ja_executada  a trava da ferramenta contra repetir a etapa ("Pipeline já concluído", "Etapa n já foi executada")
  arquivo_nao_achado  `FileNotFoundError`
  planilha_caractere  `IllegalCharacterError`
  desempacotar        "Cannot unpack non-tuple value" (falha também no Python normal)
  sem_nome            a mensagem não traz o nome da exceção (a chave do padrão é "sem nome")
  outro               o que nenhuma regra casa (esperado: 0; se não for, o grupo novo é o achado)

Por grupo: erros, execuções (exec_id + agente), meses, papéis, tokens, os erros por execução (a mesma execução repete?),
se passa na régua, e, dentro dele, quantos padrões passam sozinhos (um grupo pode recorrer só somado). O veredito é por
regra, e ele só diz se vale investigar: a decisão é do pesquisador.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel, de grupo e meses. Grava
`recorrencia_sintoma.csv` (uma linha por grupo, sem mensagem nem identificador) na pasta do `casos.csv`. Uso, da raiz:
    uv run --no-sync python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_recorrencia_sintoma_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv>
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
import base_pipeline as bp  # noqa: E402  (a régua e a chave sem impressão digital são as da triagem)

BALDE = "X_sintoma_nao_reconhecido"
# os grupos da hipótese, em ordem: o primeiro que casa a mensagem vale
GRUPOS = [
    ("recusa_llm", re.compile(r"\bBadRequestError\b|ContentPolicyViolation")),
    ("pdf_layout", re.compile(r"\bLayoutError\b")),
    ("decodificar_barra", re.compile(r"\bUnicodeDecodeError\b")),
    ("dado_tipo_ou_conta", re.compile(r"Can only use \.str accessor|\bDateParseError\b|\bZeroDivisionError\b")),
    ("etapa_ja_executada", re.compile(r"Pipeline já concluído|Etapa .{1,12} já foi executada|não foi possível persistir")),
    ("arquivo_nao_achado", re.compile(r"\bFileNotFoundError\b")),
    ("planilha_caractere", re.compile(r"\bIllegalCharacterError\b")),
    ("desempacotar", re.compile(r"Cannot unpack non-tuple value")),
]
CHAVE_EXEC = ["exec_id", "agente"]
COLUNAS = ["grupo", "erros", "execucoes", "meses", "papeis", "tokens", "max_erros_por_execucao",
           "padroes", "padroes_que_passam", "passa", "motivo"]


def grupo(msg, padrao):
    for nome, rx in GRUPOS:
        if rx.search(msg):
            return nome
    if isinstance(padrao, str) and padrao.startswith(bp.SEM_NOME):
        return "sem_nome"
    return "outro"


def _padrao_passa(g):
    """A régua da triagem para um padrão: identificado (não é sem impressão digital), execuções e meses."""
    chave_ok = not (g.padrao.isna().all() or str(g.padrao.iloc[0]).startswith(bp.SEM_NOME))
    return bool(chave_ok and len(g[CHAVE_EXEC].drop_duplicates()) >= bp.MIN_EXECS and g.mes.nunique() >= bp.MIN_MESES)


def contar(C):
    """A população do balde, com a coluna `grupo`."""
    S = C[C.unidade.eq(BALDE)].copy()
    S["mensagem"] = S["mensagem"].fillna("").astype(str)
    S["grupo"] = [grupo(m, p) for m, p in zip(S.mensagem, S.padrao)]
    return S


def tabela(S):
    linhas = []
    for nome, g in S.groupby("grupo", sort=False):
        execs = len(g[CHAVE_EXEC].drop_duplicates())
        meses = g.mes.nunique()
        padroes = g.groupby("padrao", dropna=False)
        pass_pad = sum(_padrao_passa(x) for _, x in padroes)
        passa = bool(execs >= bp.MIN_EXECS and meses >= bp.MIN_MESES)
        motivo = []
        if execs < bp.MIN_EXECS:
            motivo.append(f"{execs} execuções (< {bp.MIN_EXECS})")
        if meses < bp.MIN_MESES:
            motivo.append(f"{meses} mês (< {bp.MIN_MESES})")
        linhas.append({"grupo": nome, "erros": len(g), "execucoes": execs, "meses": meses,
                       "papeis": g.role.nunique(), "tokens": int(g.tok_tot.fillna(0).sum()),
                       "max_erros_por_execucao": int(g.groupby(CHAVE_EXEC).size().max()),
                       "padroes": padroes.ngroups, "padroes_que_passam": int(pass_pad), "passa": passa,
                       "motivo": "; ".join(motivo) if motivo else "passa a régua"})
    T = pd.DataFrame(linhas, columns=COLUNAS)
    return T.sort_values(["passa", "erros"], ascending=False).reset_index(drop=True)


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", required=True)
    a = p.parse_args(argv)
    C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
    faltam = [c for c in ("mensagem", "padrao", "unidade", "tok_tot") if c not in C.columns]
    if faltam:
        print(f"casos.csv sem a coluna {faltam}: rode o `especificas/residuo.py` desta versão")
        return 1
    S = contar(C)
    if S.empty:
        print(f"o `casos.csv` não tem erros do balde {BALDE}")
        return 1
    T = tabela(S)
    print(f"balde {BALDE}: {len(S)} erros · régua: ≥ {bp.MIN_EXECS} execuções e ≥ {bp.MIN_MESES} meses "
          f"(execução = exec_id + agente)")
    for r in T.itertuples():
        marca = "PASSA" if r.passa else "não passa"
        print(f"\n== {r.grupo}: {r.erros} erros · {r.execucoes} execuções · {r.meses} meses · {r.papeis} papéis · "
              f"{r.tokens:,} tokens".replace(",", ".") + f" · até {r.max_erros_por_execucao} por execução → {marca}")
        print(f"  {r.padroes} padrões, {r.padroes_que_passam} passam sozinhos · {r.motivo}")
        g = S[S.grupo.eq(r.grupo)]
        print(f"  papéis: {g.role.value_counts().to_dict()}")
        print(f"  meses: {g.mes.value_counts().sort_index().to_dict()}")
    passam = T[T.passa & ~T.grupo.isin(["recusa_llm"])]
    print(f"\n== resumo: {int(T.passa.sum())} de {len(T)} grupos passam a régua; "
          f"para investigar (fora a recusa do LLM, já decidida): {', '.join(passam.grupo) or 'nenhum'}")
    if (T.grupo == "outro").any():
        print("  atenção: há erros em `outro` — nenhuma regra os casa; olhar os padrões antes de decidir")
    destino = Path(a.casos).parent / "recorrencia_sintoma.csv"
    T.to_csv(destino, index=False)
    print(f"\n→ {destino} ({len(T)} grupos; sem mensagem nem identificador)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
