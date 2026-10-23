"""O catálogo das memórias fechadas (`analysis/registros/memorias.json`): monta a entrada de cada arquivo final, registra
no catálogo e confere o catálogo.

    python catalogar_memoria.py <memoria_*.json> [...] [--saida catalogo.json]   # monta as entradas (passo 9)
    python catalogar_memoria.py --registrar <catalogo.json> [--registro <memorias.json>]
    python catalogar_memoria.py --conferir [--registro <memorias.json>]
    python catalogar_memoria.py --monitorar <id> [<id> ...] --tipo rara|reforço --motivo "<o porquê>" [--base <BASE_ID>]
                                [--decidido-em <AAAA-MM-DD>] [--registro <memorias.json>] [--monitoramento <monitoramento.json>]

Uma memória entra no catálogo quando está **fechada**: `validation.destino` = "memória" (decisão do pesquisador) e
`status` = "derived-and-checked". O que tem destino harness vai para o `monitoramento.json`, e o que tem destino em
aberto fica fora; as duas listas saem no resumo com o motivo. A entrada leva só conteúdo técnico (o que a memória diz,
onde vale, quantos erros, de que rodada) e o hash do arquivo final, que fica na pasta da mineração, na máquina da base:
sem `location` nem `evidence` (os casos). Desde o esquema 0.4, leva também `validation.nomes` (os nomes que a memória
manda usar ou evitar), que o `conferir_memorias.py` (degrau 2) confere. Passa pelo `varrer_pii.py` antes de sair (o `minerar.py` faz isso no passo 9).

`--registrar` põe as entradas no catálogo, trocando a que tiver o mesmo (id, base); `--conferir` confere os campos e
que (id, base) não se repete. Sai com 0 se tudo certo, 1 se não. Só biblioteca padrão.

**Memória monitorada (não injetada):** o pesquisador decide que uma memória fica guardada e monitorada em vez de ir para
o agente — *rara* (não passa na régua de recorrência) ou *reforço* (repete o que o prompt já diz). `--monitorar` grava na
entrada o `monitorada`: o tipo, quando e por quê, a linha de base (rodada, erros, execuções, meses de agora) e os
gatilhos do tipo, com as regras do `monitoramento.json` (o `monitorar.py`): rara → `regua` (a régua do monitoramento);
reforço → `cresce` (erros ≥ 3 × a linha de base). No `--registrar` de uma mineração nova, o `monitorada` da entrada
anterior é preservado, os gatilhos são conferidos contra a linha de base e um que dispara sai como ALARME (registra
assim mesmo: a contagem nova é o fato; o alarme é para o pesquisador decidir de novo). A conferência do degrau 2
(`degrau`, `conferencia`) da entrada anterior não passa para a nova: é de outra rodada.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[4]
REGISTRO = RAIZ / "analysis" / "registros" / "memorias.json"
MONITORAMENTO = RAIZ / "analysis" / "registros" / "monitoramento.json"
TIPOS = ("rara", "reforço")
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
        mon = e.get("monitorada")
        if mon and (mon.get("tipo") not in TIPOS or not mon.get("gatilhos") or not (mon.get("linha_de_base") or {}).get("erros")):
            erros.append(f"item {i} ({e.get('id')}): `monitorada` sem tipo ({'/'.join(TIPOS)}), gatilhos ou linha de base")
        chave = (e.get("id"), e.get("base"))
        if chave in vistos:
            erros.append(f"item {i}: {chave} repetido")
        vistos.add(chave)
    return erros


def registrar(reg, entradas, hoje=None):
    """Põe as entradas no catálogo; preserva o `monitorada` da entrada anterior e devolve os alarmes dos gatilhos."""
    antes = {(e.get("id"), e.get("base")): e for e in reg.get("itens", [])}
    novas, alarmes = {}, []
    for e in entradas:
        n = {**e, "registrado_em": hoje or datetime.date.today().isoformat()}
        mon = antes.get((e["id"], e["base"]), {}).get("monitorada")
        if mon:
            n["monitorada"] = mon
            alarmes += [f"{e['id']} ({mon['tipo']}): {a}" for a in disparos(mon, n.get("occurrences") or {})]
        novas[(e["id"], e["base"])] = n
    itens = [e for e in reg.get("itens", []) if (e.get("id"), e.get("base")) not in novas] + list(novas.values())
    reg["itens"] = sorted(itens, key=lambda e: (str(e.get("unidade")), str(e.get("id")), str(e.get("base"))))
    return reg, alarmes


def gatilhos(tipo, monitoramento):
    """Os gatilhos de uma memória monitorada, com as regras do monitoramento.json."""
    if tipo == "rara":
        vistas = [g for it in monitoramento.get("itens", []) for g in it.get("gatilhos", []) if g.get("tipo") == "regua"]
        return [vistas[0] if vistas else {"tipo": "regua", "execucoes": 3, "meses": 2}]
    return [{"tipo": "cresce", "fator": 3}]


def disparos(mon, occ):
    """Os gatilhos que disparam na contagem nova, contra a linha de base."""
    base, saida = mon.get("linha_de_base") or {}, []
    erros, execs, meses = occ.get("erros") or 0, occ.get("execucoes") or 0, len(occ.get("meses") or [])
    for g in mon.get("gatilhos", []):
        if g["tipo"] == "regua" and execs >= g.get("execucoes", 3) and meses >= g.get("meses", 2):
            saida.append(f"passa na régua ({execs} execuções ≥ {g.get('execucoes', 3)}, {meses} meses ≥ {g.get('meses', 2)})")
        elif g["tipo"] == "cresce" and base.get("erros") and erros >= g.get("fator", 3) * base["erros"]:
            saida.append(f"cresceu: {erros} erros ≥ {g.get('fator', 3)} × {base['erros']}")
    return saida


def monitorar(reg, ids, tipo, motivo, monitoramento, base=None, decidido_em=None):
    """Marca as entradas como monitoradas (não injetadas), com a linha de base de agora."""
    alvo = [e for e in reg.get("itens", []) if e["id"] in ids and (not base or e.get("base") == base)]
    faltam = sorted(set(ids) - {e["id"] for e in alvo})
    if faltam or len(alvo) != len(ids):
        sys.exit(f"não acho uma entrada única para: {', '.join(faltam) or 'algum id (use --base)'}")
    for e in alvo:
        occ = e.get("occurrences") or {}
        e["monitorada"] = {"tipo": tipo, "decidido_em": decidido_em or datetime.date.today().isoformat(),
                           "motivo": motivo,
                           "linha_de_base": {"rodada_id": e.get("rodada_id"), "erros": occ.get("erros"),
                                             "execucoes": occ.get("execucoes"), "meses": len(occ.get("meses") or [])},
                           "gatilhos": gatilhos(tipo, monitoramento)}
    return alvo


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
    p.add_argument("--monitorar", nargs="+", metavar="ID", help="marca estas memórias como monitoradas (não injetadas)")
    p.add_argument("--tipo", choices=TIPOS, help="com --monitorar: rara ou reforço")
    p.add_argument("--motivo", help="com --monitorar: o porquê, nas palavras do pesquisador")
    p.add_argument("--base", help="com --monitorar: a base das entradas")
    p.add_argument("--decidido-em", help="com --monitorar: a data da decisão (padrão: hoje)")
    p.add_argument("--monitoramento", default=str(MONITORAMENTO))
    a = p.parse_args(argv)
    if a.monitorar:
        if not (a.tipo and a.motivo):
            p.error("--monitorar pede --tipo e --motivo")
        reg = ler_registro(a.registro)
        mon = json.loads(Path(a.monitoramento).read_text(encoding="utf-8"))
        for e in monitorar(reg, a.monitorar, a.tipo, a.motivo, mon, a.base, a.decidido_em):
            m = e["monitorada"]
            print(f"  monitorada  {e['id']} · {m['tipo']} · linha de base {m['linha_de_base']['erros']} erros · "
                  f"gatilhos: {', '.join(g['tipo'] for g in m['gatilhos'])}")
        Path(a.registro).write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    if a.registrar:
        reg, alarmes = registrar(ler_registro(a.registro),
                                 json.loads(Path(a.registrar).read_text(encoding="utf-8"))["entradas"])
        erros = conferir(reg)
        if erros:
            print("NÃO REGISTRA:\n  " + "\n  ".join(erros))
            return 1
        Path(a.registro).write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"registrado: {len(reg['itens'])} memória(s) no catálogo")
        for x in alarmes:
            print(f"  ALARME  {x} — leve ao pesquisador")
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
