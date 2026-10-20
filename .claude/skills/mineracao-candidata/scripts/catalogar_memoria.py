"""O catálogo das memórias fechadas (`analysis/registros/memorias.json`): monta a entrada de cada arquivo final, registra
no catálogo e confere o catálogo.

    python catalogar_memoria.py <memoria_*.json> [...] [--saida catalogo.json]   # monta as entradas (passo 9)
    python catalogar_memoria.py --registrar <catalogo.json> [--registro <memorias.json>]
    python catalogar_memoria.py --conferir [--registro <memorias.json>]

Uma memória entra no catálogo quando está **fechada**: `validation.destino` = "memória" (decisão do pesquisador) e
`status` = "derived-and-checked". O que tem destino harness vai para o `monitoramento.json`, e o que tem destino em
aberto fica fora; as duas listas saem no resumo com o motivo. A entrada leva só conteúdo técnico (o que a memória diz,
onde vale, quantos erros, de que rodada) e o hash do arquivo final, que fica na pasta da mineração, na máquina da base:
sem `location` nem `evidence` (os casos). Desde o esquema 0.4, leva também `validation.nomes` (os nomes que a memória
manda usar ou evitar), que o `conferir_memorias.py` (degrau 2) confere. Passa pelo `varrer_pii.py` antes de sair (o `minerar.py` faz isso no passo 9).

`--registrar` põe as entradas no catálogo, trocando a que tiver o mesmo (id, base); `--conferir` confere os campos e
que (id, base) não se repete. Sai com 0 se tudo certo, 1 se não. Só biblioteca padrão.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[4]
REGISTRO = RAIZ / "analysis" / "registros" / "memorias.json"
CAMPOS = ("id", "unidade", "parte", "base", "rodada_id", "fonte_id", "gerado_em", "esquema", "parte_especifica",
          "destino", "status", "category", "scope", "description", "correction_guidance", "occurrences", "arquivo")


def _sha16(caminho):
    """O hash do arquivo final, sem o que um editor muda (BOM e fim de linha), como o conferir_versao."""
    txt = Path(caminho).read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]


def entrada(doc, caminho):
    """(entrada, None) se a memória está fechada; (None, motivo) se não."""
    mem = doc.get("memoria") or {}
    val = mem.get("validation") or {}
    destino, status = val.get("destino"), mem.get("status")
    ident = doc.get("id") or doc.get("unidade")
    if destino != "memória":
        return None, f"{ident}: destino {destino!r}" + (" (vai para o monitoramento.json)" if destino == "harness" else "")
    if status != "derived-and-checked":
        return None, f"{ident}: status {status!r}"
    caso = (mem.get("location") or {}).get("casos") or [{}]
    occ = mem.get("occurrences") or {}
    return {"id": ident, "unidade": doc.get("unidade"), "parte": doc.get("parte"), "base": doc.get("base"),
            "rodada_id": caso[0].get("rodada_id"), "fonte_id": caso[0].get("fonte_id"),
            "gerado_em": doc.get("gerado_em"), "esquema": doc.get("esquema"),
            "parte_especifica": doc.get("parte_especifica"), "destino": destino, "status": status,
            "destino_decidido_em": val.get("destino_decidido_em"),
            "category": mem.get("category"), "scope": mem.get("scope"), "description": mem.get("description"),
            "correction_guidance": mem.get("correction_guidance"),
            "nomes": val.get("nomes"),   # esquema 0.4: o que o degrau 2 confere (conferir_memorias.py)
            "occurrences": {"erros": occ.get("erros"), "execucoes": occ.get("execucoes"),
                            "meses": occ.get("meses") or []},
            "arquivo": {"nome": Path(caminho).name, "sha256_16": _sha16(caminho),
                        "onde": "na pasta da mineração, na máquina da base"}}, None


def montar(caminhos):
    entradas, fora = [], []
    for c in caminhos:
        e, motivo = entrada(json.loads(Path(c).read_text(encoding="utf-8")), c)
        (entradas.append(e) if e else fora.append(motivo))
    return entradas, fora


def ler_registro(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def conferir(reg):
    erros, vistos = [], set()
    for i, e in enumerate(reg.get("itens", [])):
        faltam = [c for c in CAMPOS if e.get(c) in (None, "")]
        if faltam:
            erros.append(f"item {i} ({e.get('id')}): sem {', '.join(faltam)}")
        if e.get("destino") != "memória":
            erros.append(f"item {i} ({e.get('id')}): destino {e.get('destino')!r} não é memória fechada")
        chave = (e.get("id"), e.get("base"))
        if chave in vistos:
            erros.append(f"item {i}: {chave} repetido")
        vistos.add(chave)
    return erros


def registrar(reg, entradas, hoje=None):
    novas = {(e["id"], e["base"]): {**e, "registrado_em": hoje or datetime.date.today().isoformat()} for e in entradas}
    itens = [e for e in reg.get("itens", []) if (e.get("id"), e.get("base")) not in novas] + list(novas.values())
    reg["itens"] = sorted(itens, key=lambda e: (str(e.get("unidade")), str(e.get("id")), str(e.get("base"))))
    return reg


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("memorias", nargs="*", help="arquivos finais memoria_*.json")
    p.add_argument("--saida", help="onde gravar as entradas montadas (catalogo_<u>_<base>.json)")
    p.add_argument("--registrar", help="as entradas (catalogo_*.json) a pôr no catálogo")
    p.add_argument("--conferir", action="store_true")
    p.add_argument("--registro", default=str(REGISTRO))
    a = p.parse_args(argv)
    if a.registrar:
        reg = registrar(ler_registro(a.registro), json.loads(Path(a.registrar).read_text(encoding="utf-8"))["entradas"])
        erros = conferir(reg)
        if erros:
            print("NÃO REGISTRA:\n  " + "\n  ".join(erros))
            return 1
        Path(a.registro).write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"registrado: {len(reg['itens'])} memória(s) no catálogo")
        return 0
    if a.conferir:
        erros = conferir(ler_registro(a.registro))
        print("\n".join(erros) if erros else f"catálogo ok: {len(ler_registro(a.registro).get('itens', []))} memória(s)")
        return 1 if erros else 0
    entradas, fora = montar(a.memorias)
    if a.saida:
        Path(a.saida).write_text(json.dumps({"entradas": entradas, "fora": fora}, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    for e in entradas:
        print(f"  catálogo  {e['id']} · {e['arquivo']['sha256_16']} · {e['occurrences']['erros']} erros")
    for f in fora:
        print(f"  fora      {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
