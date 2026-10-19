"""Replica o Ajuste 21 no pipeline da base 2 (a pasta `pipeline/` desta análise, que só existe na máquina da base 2).

O pipeline da base 2 é uma cópia do da base 1 (`2026-09-trace-law-flow/pipeline/`) com outro TRACE e BASE_ID; o kit de
mineração confere isso (`conferir_versao.py`). O Ajuste 21 (livro-razão `pipeline-entre-bases.md`) muda três arquivos:
`base_pipeline.py`, `paleta.py` e `genealogia_sankey.py`. Este script:

  1. confere que cada arquivo da base 2 é o da base 1 de ANTES do ajuste (o mesmo hash do `conferir_versao.py`, que
     ignora fim de linha e as atribuições de TRACE e BASE_ID). Se algum difere, não grava nada e diz qual;
  2. se já é o de DEPOIS do ajuste, não faz nada;
  3. se não, copia o arquivo da base 1 (já com o ajuste) e põe de volta as linhas de TRACE e BASE_ID da base 2.

Por padrão só mostra o que faria. Uso, de dentro de `analysis/2026-09-trace-law-flow-second/scripts`, depois de copiar
para a máquina da base 2 os três arquivos novos da base 1:
    uv run replicar_ajuste21.py            # mostra
    uv run replicar_ajuste21.py --aplicar  # grava
Depois: `conferir_versao.py analysis/2026-09-trace-law-flow-second` tem de dar IGUAL ao manifesto do kit novo.
"""
import argparse
import ast
from pathlib import Path
import sys

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
BASE1 = RAIZ / "analysis" / "2026-09-trace-law-flow" / "pipeline"
BASE2 = AQUI.parent / "pipeline"
sys.path.insert(0, str(RAIZ / ".claude" / "skills" / "mineracao-base" / "scripts"))
from conferir_versao import assinatura  # noqa: E402

# o hash (conferir_versao.assinatura) de cada arquivo da base 1 antes do Ajuste 21 (commit 23461e0..ff6ea58)
ANTES = {"base_pipeline.py": "45d3e4784e049b3d", "paleta.py": "626d6cf1844058e4", "genealogia_sankey.py": "6b66cdce1d72b8bd"}
CAMADA_DA_BASE = {"TRACE", "BASE_ID"}


def camada_da_base(txt):
    """As linhas (texto) das atribuições de TRACE e BASE_ID, por nome."""
    linhas, out = txt.split("\n"), {}
    for no in ast.parse(txt).body:
        if isinstance(no, ast.Assign):
            nome = next((t.id for t in no.targets if getattr(t, "id", None) in CAMADA_DA_BASE), None)
            if nome:
                out[nome] = (no.lineno, no.end_lineno, "\n".join(linhas[no.lineno - 1:no.end_lineno]))
    return out


def com_camada(novo, da_base2):
    """O texto `novo` (base 1) com as atribuições de TRACE e BASE_ID trocadas pelas da base 2."""
    linhas = novo.split("\n")
    alvo = camada_da_base(novo)
    for nome, (ini, fim, _) in sorted(alvo.items(), key=lambda kv: -kv[1][0]):
        if nome in da_base2:
            linhas[ini - 1:fim] = da_base2[nome][2].split("\n")
    return "\n".join(linhas)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--aplicar", action="store_true")
    a = p.parse_args(argv)
    plano, problemas = [], []
    for nome, h_antes in ANTES.items():
        b1, b2 = BASE1 / nome, BASE2 / nome
        if not b1.exists() or not b2.exists():
            problemas.append(f"{nome}: falta {'na base 1' if not b1.exists() else 'na base 2'}")
            continue
        h1, h2 = assinatura(str(b1)), assinatura(str(b2))
        if h1 == h_antes:
            problemas.append(f"{nome}: o arquivo da base 1 ainda é o de antes do ajuste — copie o novo primeiro")
        elif h2 == h1:
            print(f"  já aplicado  {nome}")
        elif h2 != h_antes:
            problemas.append(f"{nome}: a base 2 difere da base 1 de antes do ajuste ({h2} ≠ {h_antes}) — conferir à mão")
        else:
            plano.append((nome, b1, b2))
            print(f"  aplicar      {nome}  ({h2} → {h1})")
    if problemas:
        print("\nNÃO GRAVA:\n  " + "\n  ".join(problemas))
        return 1
    if not a.aplicar:
        print("\n(só mostrei; rode com --aplicar para gravar)" if plano else "\nnada a fazer")
        return 0
    for nome, b1, b2 in plano:
        txt2 = b2.read_bytes().decode("utf-8").replace("\r\n", "\n")
        novo = com_camada(b1.read_bytes().decode("utf-8").replace("\r\n", "\n"), camada_da_base(txt2))
        b2.write_bytes(novo.encode("utf-8"))
        h = assinatura(str(b2))
        print(f"  gravado      {nome}  ({'confere' if h == assinatura(str(b1)) else 'NÃO CONFERE: ' + h})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
