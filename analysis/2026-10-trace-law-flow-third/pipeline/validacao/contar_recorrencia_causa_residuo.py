"""Base 3: o balde "causa não identificada" do resíduo (b3 #5) — que famílias de erro recorrem e quais valem a investigação?

O balde (376 erros na rodada `c2e5e8b31f297d21`: 250 `causa_sem_regra` e 126 `codigo_mal_escrito`) é onde o sintoma tem
nome e falta a causa; dos 20 padrões do resíduo que passam na régua, 19 estão aqui. Como no balde do sintoma (decisão do
Rafael, 13/11), a pergunta vem antes de qualquer leitura: o grupo recorre (≥ 3 execuções e ≥ 2 meses), com um mecanismo
só? Só o que passa vai à investigação; o resto fica no resíduo com motivo, numa tabela de decisão em lote.

As famílias são hipóteses de mecanismo lidas pela mensagem (o trecho depois do último "due to:"; a primeira regra que casa
vale), não unidades. Estão em `FAMILIAS`, da mais específica à mais geral:
  sintaxe: continuação de linha com barra · f-string · `invalid syntax` · outra sintaxe/indentação
  indexação recusada pelo interpretador (`Could not index`)
  `round`/formato sobre valor que é texto (`__round__`, `Unknown format code`)
  "Número inválido: deve conter n dígitos" (a mensagem de validação de uma ferramenta)
  JSON ausente no retorno · JSON não serializável
  construtor de DataFrame chamado errado · data e hora · outro erro do pandas
  soma/concatenação entre tipos · comparação entre tipos · objeto não chamável · índice de lista com texto
  chave ausente (`KeyError`) · outro `TypeError` · outro `ValueError` · `outro` (nenhuma regra casa: o grupo novo é o achado)

Por família: erros, execuções (exec_id + agente), meses, papéis, tokens, os padrões que a compõem e quantos passam
sozinhos (uma família pode recorrer só somada, e então é uma sacola de mecanismos), o padrão dominante, o erro máximo por
execução e as funções chamadas na linha que falhou. Com `--fonte <parquet da base>`: o que veio no passo seguinte (sem
passo, sem erro, a mesma família de novo, outra família). O veredito é por regra e diz só se vale investigar; a decisão
é do pesquisador.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, papéis, meses, nomes de função e o padrão
já mascarado. Grava `recorrencia_causa.csv` (uma linha por família, sem mensagem nem identificador) e `padroes_causa.csv`
(um padrão por linha, com a família) na pasta do `casos.csv`. Uso, da raiz:
    uv run --no-sync python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_recorrencia_causa_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv> [--fonte <parquet da base>]
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contar_infra_residuo as INFRA  # noqa: E402
import contar_limites_interpretador_residuo as LIM  # noqa: E402
import contar_recorrencia_sintoma_residuo as REC  # noqa: E402

bp = REC.bp
BALDE = "X_causa_nao_identificada"
# da mais específica à mais geral: a primeira que casa o trecho depois do último "due to:" vale
FAMILIAS = [
    ("sintaxe_continuacao_barra", re.compile(r"unexpected character after line continuation")),
    ("sintaxe_fstring", re.compile(r"f-string")),
    ("sintaxe_invalid_syntax", re.compile(r"invalid syntax")),
    ("sintaxe_outra", re.compile(r"SyntaxError|IndentationError|TabError")),
    ("indexacao_do_interpretador", re.compile(r"Could not index")),
    ("round_ou_formato_em_texto", re.compile(r"__round__|Unknown format code")),
    ("numero_invalido_da_ferramenta", re.compile(r"Número inválido: deve conter")),
    ("json_nao_serializavel", re.compile(r"not JSON serializable")),
    ("json_ausente_no_retorno", re.compile(r"JSON|Expected object or value|Nenhum objeto")),
    ("dataframe_construtor", re.compile(r"DataFrame constructor not properly called")),
    ("data_ou_hora", re.compile(r"datetime|Timestamp|strftime|NaTType|time data")),
    ("pandas_outro", re.compile(r"DataFrame|dtype|orient|reshape|mismatched columns")),
    ("soma_ou_concatenacao_entre_tipos", re.compile(r"unsupported operand|can only concatenate|ufunc")),
    ("comparacao_entre_tipos", re.compile(r"not supported between instances")),
    ("objeto_nao_chamavel", re.compile(r"is not callable")),
    ("indice_de_lista_com_texto", re.compile(r"list indices must be integers")),
    ("chave_ausente", re.compile(r"KeyError")),
    ("tipo_outro", re.compile(r"TypeError")),
    ("valor_outro", re.compile(r"ValueError")),
]
CHAVE_EXEC = REC.CHAVE_EXEC
COLUNAS = ["familia", "erros", "execucoes", "meses", "papeis", "tokens", "padroes", "padroes_que_passam",
           "padrao_dominante_pct", "max_erros_por_execucao", "passa", "passa_sozinho", "motivo"]
DESFECHOS = ["sem_passo", "sem_erro", "mesma_familia", "outra_familia"]


def trecho(msg):
    """A parte da mensagem depois do último "due to:" (a exceção que falhou, sem o código da linha)."""
    return str(msg).rsplit("due to:", 1)[-1]


def familia(msg):
    t = trecho(msg)
    for nome, rx in FAMILIAS:
        if rx.search(t):
            return nome
    return "outro"


def contar(C):
    """A população do balde, com a coluna `familia`."""
    S = C[C.unidade.eq(BALDE)].copy()
    S["mensagem"] = S["mensagem"].fillna("").astype(str)
    S["familia"] = [familia(m) for m in S.mensagem]
    return S


def tabela(S):
    linhas = []
    for nome, g in S.groupby("familia", sort=False):
        execs = len(g[CHAVE_EXEC].drop_duplicates())
        meses = g.mes.nunique()
        padroes = g.groupby("padrao", dropna=False)
        pass_pad = sum(REC._padrao_passa(x) for _, x in padroes)
        passa = bool(execs >= bp.MIN_EXECS and meses >= bp.MIN_MESES)
        motivo = []
        if execs < bp.MIN_EXECS:
            motivo.append(f"{execs} execuções (< {bp.MIN_EXECS})")
        if meses < bp.MIN_MESES:
            motivo.append(f"{meses} mês (< {bp.MIN_MESES})")
        if passa and not pass_pad:
            motivo.append("passa só somando padrões")
        linhas.append({"familia": nome, "erros": len(g), "execucoes": execs, "meses": meses,
                       "papeis": g.role.nunique(), "tokens": int(g.tok_tot.fillna(0).sum()),
                       "padroes": padroes.ngroups, "padroes_que_passam": int(pass_pad),
                       "padrao_dominante_pct": round(100 * g.padrao.fillna("?").value_counts().iloc[0] / len(g), 1),
                       "max_erros_por_execucao": int(g.groupby(CHAVE_EXEC).size().max()), "passa": passa,
                       "passa_sozinho": bool(pass_pad), "motivo": "; ".join(motivo) if motivo else "passa a régua"})
    T = pd.DataFrame(linhas, columns=COLUNAS)
    return T.sort_values(["passa_sozinho", "passa", "erros"], ascending=False).reset_index(drop=True)


def tabela_padroes(S):
    """Um padrão por linha, com a família (a mais frequente entre os erros do padrão) e a régua."""
    linhas = []
    for padrao, g in S.groupby("padrao", dropna=False):
        linhas.append({"padrao": padrao, "familia": g.familia.value_counts().index[0], "erros": len(g),
                       "execucoes": len(g[CHAVE_EXEC].drop_duplicates()), "meses": g.mes.nunique(),
                       "papeis": g.role.nunique(), "passa_na_recorrencia": REC._padrao_passa(g)})
    return pd.DataFrame(linhas).sort_values(["passa_na_recorrencia", "erros"], ascending=False).reset_index(drop=True)


def funcoes(g, n=4):
    c = Counter(INFRA.funcao_na_linha(m) for m in g.mensagem)
    return dict(c.most_common(n))


def depois(S, F):
    """O que veio no passo seguinte de cada erro (ver DESFECHOS). Devolve (série alinhada a S, erros sem linha na fonte)."""
    por = {}
    for r in F.to_dict("records"):
        por.setdefault((str(r["cod_idef_exeo"]), str(r["cod_idef_aget"]), str(r["papel"]), int(float(r["step_pos"]))), r)
    saida, faltam = [], 0
    for _, r in S.iterrows():
        l = por.get(LIM._chave_casos(r))
        faltam += l is None
        if l is None or LIM._vazio(l.get("next_step_number")):
            saida.append("sem_passo")
        elif LIM._vazio(l.get("next_error_message")):
            saida.append("sem_erro")
        else:
            saida.append("mesma_familia" if familia(l["next_error_message"]) == r["familia"] else "outra_familia")
    return pd.Series(saida, index=S.index), faltam


def _imprimir(S, T, P, dep, faltam):
    print(f"balde {BALDE}: {len(S)} erros em {len(T)} famílias · régua: ≥ {bp.MIN_EXECS} execuções e ≥ {bp.MIN_MESES} "
          f"meses (execução = exec_id + agente)")
    print("\nfamília | erros | execuções | meses | papéis | padrões (passam sozinhos) | dominante | passa")
    for r in T.itertuples():
        marca = "PASSA SOZINHO" if r.passa_sozinho else ("passa somando" if r.passa else "não passa")
        print(f"  {r.familia} | {r.erros} | {r.execucoes} | {r.meses} | {r.papeis} | {r.padroes} ({r.padroes_que_passam}) | "
              f"{r.padrao_dominante_pct}% | {marca}")
    for r in T[T.passa].itertuples():
        g = S[S.familia.eq(r.familia)]
        print(f"\n== {r.familia}: {r.erros} erros · {r.execucoes} execuções · {r.meses} meses · {r.papeis} papéis · "
              f"{r.tokens:,} tokens · até {r.max_erros_por_execucao} por execução · {r.motivo}".replace(",", "."))
        print(f"  papéis: {g.role.value_counts().to_dict()}")
        print(f"  meses: {g.mes.value_counts().sort_index().to_dict()}")
        print(f"  funções na linha que falhou: {funcoes(g)}")
        if dep is not None:
            d = dep[g.index].value_counts().reindex(DESFECHOS, fill_value=0)
            print(f"  passo seguinte: {d[d > 0].to_dict()}")
    print(f"\n== resumo: {int(T.passa.sum())} de {len(T)} famílias passam a régua; "
          f"passam com um padrão que recorre sozinho: {', '.join(T[T.passa_sozinho].familia) or 'nenhuma'}")
    if (T.familia == "outro").any():
        print("  atenção: há erros em `outro` — nenhuma regra os casa; os padrões deles:")
        for r in P[P.familia.eq("outro")].itertuples():
            print(f"    {r.erros} · {r.padrao}")
    if dep is not None:
        print(f"  (passo seguinte lido na fonte; {faltam} erros sem linha na fonte)")


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", required=True)
    p.add_argument("--fonte")
    a = p.parse_args(argv)
    C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
    faltam = [c for c in ("mensagem", "padrao", "unidade", "tok_tot", "idx") if c not in C.columns]
    if faltam:
        print(f"casos.csv sem a coluna {faltam}: rode o `especificas/residuo.py` desta versão")
        return 1
    S = contar(C)
    if S.empty:
        print(f"o `casos.csv` não tem erros do balde {BALDE}")
        return 1
    T, P = tabela(S), tabela_padroes(S)
    dep, sem_linha = (None, 0) if not a.fonte else depois(S, LIM.ler_fonte(a.fonte))
    _imprimir(S, T, P, dep, sem_linha)
    pasta = Path(a.casos).parent
    T.to_csv(pasta / "recorrencia_causa.csv", index=False)
    P.to_csv(pasta / "padroes_causa.csv", index=False)
    print(f"\n→ {pasta / 'recorrencia_causa.csv'} ({len(T)} famílias) e padroes_causa.csv ({len(P)} padrões); "
          f"sem mensagem nem identificador")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
