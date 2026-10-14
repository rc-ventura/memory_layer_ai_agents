"""Os erros de nome não definido no primeiro passo: execuções, nomes e o depois do erro.

Segue o `contar_predecessor_pendentes.py`, que mostrou que os 5.818 pendentes por "predecessor não identificado" são
todos o primeiro ActionStep do papel, 98% em agosto de 2026 e 92% em um papel. Este script responde às perguntas que
faltam para decidir se o grupo é um incidente ou um padrão, e se vira unidade própria:

  1. Execuções: quantas execuções distintas geraram esses erros, e quantos erros por execução? Poucas execuções com
     milhares de erros cada indicam incidente.
  2. Nomes: quantos nomes diferentes aparecem? Um ou dois nomes dominando indicam variável que o harness deveria
     fornecer; muitos nomes indicam o agente inventando.
  3. O nome no código: aparece no código do passo com erro? É atribuído no mesmo código? Só depois do primeiro uso?
     (heurística por regex — uma pista, não uma prova)
  4. O depois do erro: sinal de recuperação, o passo seguinte, tokens.

Não muda regra nem grava nada em resultados. Imprime só contagens, nomes de papel e meses — nenhum identificador de
execução nem texto de caso. Os NOMES das variáveis só saem com --mostrar-nomes (por padrão, só contagens e parcelas),
porque código de agente pode carregar termos do caso. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_primeiro_passo_nome.py [--fonte <parquet>] [--mostrar-nomes]
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE.parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import base_pipeline as bp
from contar_predecessor_pendentes import contar, MOTIVO
from episodios_trace import contexto_local

PRESENCA_PRIMEIRO = "nao_identificado_por_sql"
RE_NOME = (re.compile(r"variable `(\w+)` is not defined"), re.compile(r"Forbidden function evaluation: '(\w+)'"))


def nome_do_erro(msg):
    for rx in RE_NOME:
        m = rx.search(str(msg))
        if m:
            return m.group(1)
    return None


def _atribuicoes(code, nome):
    """Linhas (0-based) em que o nome é atribuído ou definido; regex, só uma pista."""
    n = re.escape(nome)
    padroes = [rf"^[^\n=#]*\b{n}\b[^\n=#]*(?<![=!<>])=(?!=)", rf"^\s*def\s+{n}\b", rf"^\s*for\s+[^\n:]*\b{n}\b[^\n:]*\bin\b",
               rf"\bas\s+{n}\b", rf"^\s*(?:from\s+\S+\s+)?import\s+[^\n]*\b{n}\b"]
    linhas = set()
    for p in padroes:
        for m in re.finditer(p, code, re.M):
            linhas.add(code.count("\n", 0, m.start()))
    return sorted(linhas)


def _parcela(contagens, k):
    t = contagens.sum()
    return round(float(contagens.sort_values(ascending=False).head(k).sum()) / t, 3) if t else None


def analisar(P, ctx, mostrar_nomes=False):
    out = {"erros_no_grupo": len(P), "tokens_total_do_grupo": int(P.tok_tot.sum(min_count=1)) if P.tok_tot.notna().any() else None}
    P = P.copy()
    P["chave_exec"] = P.exec_id.astype(str) + "|" + P.agente.astype(str)

    # 1 · execuções
    por_exec = P.groupby("chave_exec").size()
    out["1_execucoes_distintas"] = int(len(por_exec))
    out["1_erros_por_execucao"] = {"min": int(por_exec.min()), "mediana": float(por_exec.median()),
                                    "p90": float(por_exec.quantile(0.9)), "max": int(por_exec.max())}
    out["1_parcela_das_10_execucoes_com_mais_erros"] = _parcela(por_exec, 10)
    out["1_parcela_de_1_pct_das_execucoes_com_mais_erros"] = _parcela(por_exec, max(1, int(len(por_exec) * 0.01)))
    tab = P.groupby(["role", "mes"]).agg(erros=("step_ref", "size"), execucoes=("chave_exec", "nunique")).reset_index()
    tab["erros_por_execucao"] = (tab.erros / tab.execucoes).round(2)

    # 2 · nomes
    P["nome"] = P.err_msg.map(nome_do_erro)
    out["2_sem_nome_extraido"] = int(P.nome.isna().sum())
    nomes = P.nome.dropna().value_counts()
    out["2_nomes_distintos"] = int(len(nomes))
    out["2_parcela_do_nome_mais_frequente"] = _parcela(nomes, 1)
    out["2_parcela_dos_3_nomes_mais_frequentes"] = _parcela(nomes, 3)
    out["2_parcela_dos_10_nomes_mais_frequentes"] = _parcela(nomes, 10)
    if mostrar_nomes:
        out["2_10_nomes_mais_frequentes"] = nomes.head(10).to_dict()
    por_papel_nomes = []
    for role, g in P.dropna(subset=["nome"]).groupby("role"):
        c = g.nome.value_counts()
        por_papel_nomes.append({"role": role, "erros": int(len(g)), "nomes_distintos": int(len(c)),
                                "parcela_do_mais_frequente": _parcela(c, 1), "parcela_dos_3_mais": _parcela(c, 3)})
    nomes_papel = pd.DataFrame(por_papel_nomes).sort_values("erros", ascending=False).head(6)

    # 3 · o nome no código do passo com erro
    P["codigo_integral"] = P.code.notna() & P.code_estado.eq("sem_corte_sql")
    out["3_codigo_integral_disponivel"] = P.codigo_integral.value_counts().to_dict()
    ok = P[P.codigo_integral & P.nome.notna()]
    aparece = atribuido = depois = 0
    for code, nome in zip(ok.code, ok.nome):
        code = str(code)
        m = re.search(rf"\b{re.escape(nome)}\b", code)
        if not m:
            continue
        aparece += 1
        linhas = _atribuicoes(code, nome)
        if linhas:
            atribuido += 1
            if linhas[0] > code.count("\n", 0, m.start()):
                depois += 1
    out["3_com_codigo_integral_e_nome"] = len(ok)
    out["3_nome_aparece_no_codigo"] = aparece
    out["3_atribuido_no_mesmo_codigo(heuristica)"] = atribuido
    out["3_primeira_atribuicao_depois_do_primeiro_uso(heuristica)"] = depois

    # 4 · o depois do erro
    out["4_recovery_signal"] = P.recovery_signal_produtor.value_counts(dropna=False).to_dict()
    nxt = [ctx.get((r, 1), {}) for r in P.step_ref]
    out["4_passo_seguinte_presenca"] = pd.Series([s.get("presenca") for s in nxt]).value_counts(dropna=False).to_dict()
    out["4_passo_seguinte_com_erro"] = pd.Series([s.get("error_like") for s in nxt], dtype="object").value_counts(dropna=False).to_dict()
    return out, tab, nomes_papel


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    p.add_argument("--mostrar-nomes", action="store_true", help="imprime os 10 nomes mais frequentes (confira antes se podem sair)")
    args = p.parse_args(argv)
    carga = bp.carregar_carga(args.fonte)
    _, P = contar(carga)
    if not P.empty:
        P = P[P.presenca_n_menos_1.eq(PRESENCA_PRIMEIRO)]
    if P.empty:
        print("grupo vazio: nenhum erro de nome não definido pendente como primeiro passo")
        return 0
    out, tab, nomes_papel = analisar(P, contexto_local(carga), args.mostrar_nomes)
    for k, v in out.items():
        print(f"{k}: {v}")
    print("\npor papel × mês (os 12 maiores): erros, execuções, erros por execução")
    print(tab.sort_values("erros", ascending=False).head(12).to_string(index=False))
    print("\nnomes por papel (os 6 maiores): quantos nomes distintos e a parcela dos mais frequentes")
    print(nomes_papel.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
