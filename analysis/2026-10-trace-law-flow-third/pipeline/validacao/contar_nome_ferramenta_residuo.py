"""Base 3: o grupo "nome de ferramenta usado como variável" do resíduo (b3 #5) — quem, onde e de que forma, antes de
ler casos.

O maior padrão do balde "sintoma não reconhecido" na rodada `7f146976cf5c74ed` (Ajuste 36) é o `InterpreterError`
"Cannot assign to name '<nome>': doing this would erase the existing tool!" (49 erros). O interpretador do agente
(smolagents) protege os nomes das ferramentas declaradas: atribuir qualquer valor a um desses nomes é barrado. A
hipótese (procedimento do resíduo, passo 4, perguntas R2 e R3): a falha é do agente (guardou um valor num nome que é de
ferramenta) e o destino é uma lição — uma unidade nova, ou a extensão de uma que já existe.

As medidas, por regra, sem ler caso:
  - **o nome atribuído** (o que está entre aspas na mensagem): é sempre a mesma ferramenta, ou várias?
  - **a forma da linha que falhou** (`Code execution failed at line '<linha>'`):
      resultado_com_o_nome    `x = x(...)`: guardou o retorno da ferramenta numa variável com o nome dela
      outro_valor             `x = ...` com outro valor do lado direito
      alvo_multiplo           `a, x = ...` ou `x, a = ...`: o nome é um dos alvos
      laco                    `for x in ...` ou `for ..., x in ...`
      funcao                  `def x(...)`: redefiniu a ferramenta como função
      outra                   a linha não tem nenhuma dessas formas
      sem_linha               a mensagem não traz a linha
  - **a repetição:** quantas execuções têm o erro mais de uma vez no mesmo papel, e se com o mesmo nome (o agente
    repete o erro depois de vê-lo?);
  - erros, execuções, meses, papéis e tokens; e papel × nome.

Grava `casos_nome_ferramenta.csv` (os erros do grupo, com `nome` e `forma`, sem a mensagem) na pasta do `casos.csv`,
para o `montar_evidencia.py --de mineracao/residuo/<pasta>/casos_nome_ferramenta.csv --onde forma=<f>` montar a
amostra com os crus.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel, de ferramenta, as formas
e os meses: nada de mensagem, de código nem de identificador. Uso, da raiz, no ambiente da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_nome_ferramenta_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv>
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd

ERRO = re.compile(r"Cannot assign to name '([^']*)': doing this would erase the existing tool")
LINHA = re.compile(r"failed at line '(.*?)' due to", re.S)
FORMAS = ["resultado_com_o_nome", "outro_valor", "alvo_multiplo", "laco", "funcao", "outra", "sem_linha"]


def forma(msg, nome):
    """A forma da linha que falhou, para o nome atribuído (ver o docstring do módulo)."""
    m = LINHA.search(msg)
    if not m:
        return "sem_linha"
    linha, n = m.group(1).strip(), re.escape(nome)
    if re.match(rf"def\s+{n}\s*\(", linha):
        return "funcao"
    if re.match(rf"for\s+[^:]*\b{n}\b[^:]*\s+in\b", linha):
        return "laco"
    if re.match(rf"{n}\s*=\s*{n}\s*\(", linha):
        return "resultado_com_o_nome"
    alvo = re.match(r"([^=]+?)=(?!=)", linha)
    if alvo and re.search(rf"\b{n}\b", alvo.group(1)):
        return "alvo_multiplo" if "," in alvo.group(1) else "outro_valor"
    return "outra"


def contar(C):
    C = C.copy()
    C["mensagem"] = C["mensagem"].fillna("").astype(str)
    nomes = C.mensagem.map(lambda m: (ERRO.search(m) or [None, None])[1])
    G = C[nomes.notna()].copy()
    G["nome"] = nomes[nomes.notna()]
    G["forma"] = [forma(m, n) for m, n in zip(G.mensagem, G.nome)]
    return G


def repeticao(G):
    """Por (execução, papel): quantas vezes o erro aparece e com quantos nomes diferentes."""
    por = G.groupby(["exec_id", "agente", "role"]).agg(erros=("nome", "size"), nomes=("nome", "nunique"))
    return {"execuções-papel com o erro": len(por), "com o erro 1 vez": int((por.erros == 1).sum()),
            "com o erro 2+ vezes": int((por.erros >= 2).sum()),
            "2+ vezes com o mesmo nome": int(((por.erros >= 2) & (por.nomes == 1)).sum()),
            "máximo de vezes": int(por.erros.max()) if len(por) else 0}


def _resumo(g):
    return (f"{len(g)} erros · {len(g[['exec_id', 'agente']].drop_duplicates())} execuções · {g.mes.nunique()} meses · "
            f"{g.role.nunique()} papéis · {int(g.tok_tot.fillna(0).sum()):,} tokens".replace(",", "."))


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", required=True)
    a = p.parse_args(argv)
    C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
    if "mensagem" not in C.columns:
        print("casos.csv sem a coluna `mensagem`: rode o `especificas/residuo.py` desta versão")
        return 1
    G = contar(C)
    print(f"resíduo: {len(C)} erros · nome de ferramenta usado como variável: {_resumo(G)}")
    if G.empty:
        return 0
    print(f"  por balde: {G.unidade.value_counts().to_dict()}")
    print(f"  meses: {G.mes.value_counts().sort_index().to_dict()}")
    print(f"  papéis: {G.role.value_counts().to_dict()}")
    print(f"  nome atribuído: {G.nome.value_counts().to_dict()}")
    print(f"  forma da linha: {G.forma.value_counts().reindex(FORMAS, fill_value=0).to_dict()}")
    print(f"  repetição: {repeticao(G)}")
    print("  papel × nome (execuções):")
    for (r, n), k in (G.drop_duplicates(["exec_id", "agente", "role", "nome"]).groupby(["role", "nome"]).size()
                      .sort_values(ascending=False).items()):
        print(f"    {k:4d}  {r} · {n}")
    destino = Path(a.casos).parent / "casos_nome_ferramenta.csv"
    G.drop(columns=["mensagem"]).to_csv(destino, index=False)
    print(f"\n→ {destino} ({len(G)} erros; sem a coluna mensagem)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
