"""Bases 1 e 2 (trace completo, com prompt): o "módulo usado sem import" acontece mais quando o prompt não lista o módulo?

Hipótese (dossiê do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, §2h, 12): a lista de imports autorizados
do prompt e a do sandbox divergem — na base 3, o sandbox (a mensagem de erro) autoriza o `json` no ContestacaoCivel e no
OBFCivel; na base 2, o prompt desses papéis e o do RoteadorCivel, no mesmo período, não o lista. Se o agente segue o
prompt, não importa o `json` e o usa assim mesmo ("The variable `json` is not defined"): o erro seria induzido pelo
prompt (sinal de harness), não esquecimento. Se vale, a taxa de execuções com o erro é maior nas versões do prompt sem o
módulo na lista; se não vale, as duas taxas são parecidas.

Por execução (execução × agente × papel): a versão do prompt (o hash do system prompt do primeiro passo, como no
`extrair_prompts_base2.py`), se o módulo está na lista dele, e quantos erros "The variable `<apelido>` is not defined" ela
tem. Imprime, por papel e no total, as execuções, as com o erro e os erros, separados por "na lista" × "fora da lista"
× "sem a frase". Não grava nada. Só contagens e nomes de papel. Uso, da raiz:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_modulo_sem_import_base2.py --trace <trace> [--modulo json]
"""
import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contar_modulo_na_lista_base2 import modulos  # noqa: E402

APELIDOS = {"pandas": "pd", "numpy": "np"}   # o nome que o agente usa no código (o do sandbox, mineracao_U_sandbox.py)


def medir(S, modulo):
    """S: um ActionStep por linha (exec_id, agente, role, idx, sysprompt, err_msg). Uma linha por papel, mais o total."""
    nome = APELIDOS.get(modulo, modulo)
    erro = re.compile(rf"The variable `{re.escape(nome)}` is not defined")
    chave = ["exec_id", "agente", "role"]
    prim = S[S.idx.eq(0)].drop_duplicates(chave)
    lista = {tuple(k): ("sem a frase" if m is None else ("na lista" if modulo in m else "fora da lista"))
             for k, m in zip(prim[chave].itertuples(index=False, name=None), map(modulos, prim.sysprompt.fillna("")))}
    E = S[S.err_msg.fillna("").str.contains(erro)]
    erros = E.groupby(chave).size().to_dict()
    T = defaultdict(lambda: {g: {"execucoes": 0, "com_erro": 0, "erros": 0} for g in ("na lista", "fora da lista", "sem a frase")})
    for k, g in lista.items():
        for papel in (k[2], "(total)"):
            d = T[papel][g]
            d["execucoes"] += 1
            d["com_erro"] += k in erros
            d["erros"] += erros.get(k, 0)
    return dict(sorted(T.items(), key=lambda kv: (kv[0] == "(total)", kv[0])))


def _taxa(d):
    return f"{d['com_erro']}/{d['execucoes']} ({d['com_erro'] / d['execucoes']:.0%})" if d["execucoes"] else "—"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru (CSV ou parquet)")
    p.add_argument("--modulo", default="json", help="o módulo (padrão: json; pandas e numpy pelos apelidos pd e np)")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    from contar_primeiro_passo_nome_base2 import bp, explodir   # o leitor do trace (importa o pipeline da base 1)
    bp.TRACE = str(a.trace)
    T = medir(explodir(bp.carregar_trace()), a.modulo)
    print(f"`{a.modulo}` usado sem import × `{a.modulo}` na lista autorizada do prompt da execução")
    print("execuções com o erro / execuções (taxa) · erros — por papel; só os papéis com o erro ou com o módulo fora da lista")
    print(f"{'papel':22} {'na lista':>22} {'fora da lista':>22} {'sem a frase':>18}")
    for papel, g in T.items():
        if papel != "(total)" and not any(d["com_erro"] for d in g.values()) and not g["fora da lista"]["execucoes"]:
            continue
        print(f"{papel:22} " + " ".join(f"{_taxa(g[k]):>16} · {g[k]['erros']:<3}" for k in ("na lista", "fora da lista"))
              + f" {_taxa(g['sem a frase']):>14}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
