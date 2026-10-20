"""O degrau 2 da validação (conferida): as cinco checagens de cada memória do catálogo contra o ambiente e o prompt.

    python conferir_memorias.py --prompts <prompts.jsonl> [--registro <memorias.json>] [--monitoramento <monitoramento.json>]
                                [--id <id> ...] [--base <BASE_ID>] [--saida <conferencia.json>] [--registrar]

A escada e as checagens estão no doc de validação das memórias da análise (`17-validacao-memorias.md`). Este script
não lê trace nem caso: lê o catálogo (`analysis/registros/memorias.json`), o monitoramento e um JSONL com o prompt de
cada papel, uma linha por versão (`{role, versao, meses, execucoes, prompt}`), que um script da pasta da análise extrai
do trace. Os nomes que cada memória manda usar ou evitar vêm do campo estruturado `nomes` da entrada (esquema da
memória 0.4, `validation.nomes`): `importar`, `usar`, `nao_importar`, `nao_usar`. Sem `nomes`, as checagens 1 a 3 saem
"não verificável".

  1 ambiente      cada módulo de `importar` está na lista de imports autorizados do prompt do papel; cada nome de
                  `usar` é ferramenta declarada no prompt (os `def`), atributo de um módulo autorizado (`json.loads`) ou
                  função do Python (esta, "não verificável": o prompt não lista as funções permitidas); nenhum módulo de
                  `nao_importar` está na lista autorizada (a memória proibiria o que o ambiente permite)
  2 conflito      o prompt cita, em forma de código (`nome`, nome(, import nome), um nome que a memória proíbe — é
                  instrução contrária ou proibição repetida, a ler; ou o prompt traz uma instrução registrada no
                  monitoramento (`instrucao_prompt`) que induz um nome que a memória proíbe (`nomes_induzidos`)
  3 repete        o conteúdo da memória já está no prompt: os módulos de `nao_importar` ficam fora da lista autorizada
                  que o prompt declara; o prompt já manda `import <módulo>` de `importar`; o prompt já cita os nomes de
                  `usar`. "falha" se tudo se repete, "parcial" se parte
  4 recorrência   a régua de memória rara do monitoramento (execuções ≥ n e meses ≥ m), sobre `occurrences`
  5 uma causa só  a memória não junta causas diferentes: só verificável se a entrada traz `causas` (a classificação
                  de uso que o script específico grava); sem ela, "não verificável"

Por papel: o da memória (`scope.role`) ou, numa memória global, todos os papéis do JSONL. Um papel sem prompt no
JSONL é "não verificável". Uma checagem falha num papel se falha em alguma versão do prompt dele. Na memória: as
checagens 1 e 2 falham se falham em algum papel; a 3 é "falha" se todo papel verificável repete, "parcial" se algum.
O resultado diz qual JSONL usou (nome, hash, papéis, versões): numa base sem prompt, o prompt vem de outra base e é
aproximação.

--registrar grava em cada entrada do catálogo a `conferencia` (o resultado de cada checagem) e o `degrau`: 2 se as
cinco passam, 1 se não. Imprime só nomes, contagens e hashes. Sai com 0. Só biblioteca padrão.
"""
import argparse
import builtins
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

RAIZ = Path(__file__).resolve().parents[4]
REGISTRO = RAIZ / "analysis" / "registros" / "memorias.json"
MONITORAMENTO = RAIZ / "analysis" / "registros" / "monitoramento.json"

LISTA = re.compile(r"only from the following list of modules:\s*\[([^\]]*)\]")
DEF = re.compile(r"^def (\w+)\(", re.M)
CHECAGENS = ("1_ambiente", "2_conflito", "3_repete", "4_recorrencia", "5_uma_causa")
PASSA, FALHA, PARCIAL, NV = "passa", "falha", "parcial", "não verificável"
FUNCOES_DO_PYTHON = set(dir(builtins))


def _sha16(caminho):
    txt = Path(caminho).read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]


def ler_prompts(caminho):
    """{papel: [versões]} do JSONL."""
    papeis = {}
    with open(caminho, encoding="utf-8") as fh:
        for linha in fh:
            if linha.strip():
                r = json.loads(linha)
                papeis.setdefault(r["role"], []).append(r)
    return papeis


def autorizados(prompt):
    """O conjunto da lista de imports autorizados do prompt, ou None se o prompt não a declara."""
    m = LISTA.search(prompt or "")
    if not m:
        return None
    return {x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()}


def declaradas(prompt):
    return set(DEF.findall(prompt or ""))


def citado(prompt, nome):
    """O prompt cita o nome em forma de código: `nome`, nome(, import nome, from nome."""
    n = re.escape(nome)
    return bool(re.search(rf"`{n}`|(?<![\w.]){n}\s*\(|\bimport\s+{n}\b|\bfrom\s+{n}\b", prompt or ""))


def regua(monitoramento):
    """A régua de memória rara: o gatilho `regua` do monitoramento (tem de ser uma só)."""
    vistas = {(g.get("execucoes", 3), g.get("meses", 2)) for it in monitoramento.get("itens", [])
              for g in it.get("gatilhos", []) if g.get("tipo") == "regua"}
    if len(vistas) != 1:
        sys.exit(f"o monitoramento tem {len(vistas)} réguas diferentes ({sorted(vistas)}): esperava uma só")
    e, m = vistas.pop()
    return {"execucoes": e, "meses": m}


def instrucoes(monitoramento):
    """[(id, regex, nomes induzidos)] dos itens do monitoramento que registram uma instrução do prompt."""
    return [(it["id"], re.compile(it["instrucao_prompt"]), set(it.get("nomes_induzidos", [])))
            for it in monitoramento.get("itens", []) if it.get("instrucao_prompt")]


# ---- as checagens numa versão do prompt: (resultado, motivos) ----

def ambiente(nomes, prompt):
    lista, defs, motivos, nv, verificados = autorizados(prompt), declaradas(prompt), [], [], 0
    sem_lista = lista is None
    for mod in nomes.get("importar", []):
        if sem_lista:
            nv.append(f"importar {mod}: o prompt não declara a lista de imports")
            continue
        verificados += 1
        if mod not in lista:
            motivos.append(f"importar {mod}: fora da lista autorizada")
    for nome in nomes.get("usar", []):
        if "." in nome and sem_lista:
            nv.append(f"usar {nome}: o prompt não declara a lista de imports")
        elif "." in nome:
            verificados += 1
            if nome.split(".")[0] not in lista:
                motivos.append(f"usar {nome}: o módulo {nome.split('.')[0]} está fora da lista autorizada")
        elif nome in defs:
            verificados += 1
        elif nome in FUNCOES_DO_PYTHON:
            nv.append(f"usar {nome}: função do Python (o prompt não lista as permitidas)")
        else:
            verificados += 1
            motivos.append(f"usar {nome}: não é ferramenta declarada no prompt")
    for mod in nomes.get("nao_importar", []):
        if sem_lista:
            nv.append(f"não importar {mod}: o prompt não declara a lista de imports")
            continue
        verificados += 1
        if mod in lista:
            motivos.append(f"não importar {mod}: está na lista autorizada")
    if motivos:
        return FALHA, motivos
    return (PASSA, nv) if verificados else (NV, nv or ["a memória não manda usar nem evitar módulo ou ferramenta"])


def conflito(nomes, prompt, instr):
    proibidos = list(nomes.get("nao_importar", [])) + list(nomes.get("nao_usar", []))
    motivos = [f"o prompt cita {n} (instrução contrária ou proibição repetida: ler)" for n in proibidos if citado(prompt, n)]
    for ident, rx, induzidos in instr:
        comuns = sorted(induzidos & set(nomes.get("nao_usar", [])))
        if comuns and rx.search(prompt or ""):
            motivos.append(f"o prompt traz a instrução registrada em {ident}, que induz {', '.join(comuns)}")
    return (FALHA, motivos) if motivos else (PASSA, [])


def repete(nomes, prompt):
    lista, conteudo, repetidos = autorizados(prompt), [], []
    for mod in nomes.get("nao_importar", []):
        conteudo.append(mod)
        if lista is not None and mod not in lista:
            repetidos.append(f"não importar {mod}: o prompt já limita os imports a uma lista sem ele")
    for mod in nomes.get("importar", []):
        conteudo.append(mod)
        if re.search(rf"\bimport\s+{re.escape(mod)}\b", prompt or ""):
            repetidos.append(f"importar {mod}: o prompt já manda importar")
    for nome in nomes.get("usar", []):
        conteudo.append(nome)
        if citado(prompt, nome):
            repetidos.append(f"usar {nome}: o prompt já cita")
    for nome in nomes.get("nao_usar", []):
        conteudo.append(nome)
        if citado(prompt, nome):
            repetidos.append(f"não usar {nome}: o prompt já cita")
    if not conteudo:
        return NV, ["a memória não declara nomes"]
    if not repetidos:
        return PASSA, []
    return (FALHA if len(repetidos) == len(conteudo) else PARCIAL), repetidos


# ---- por papel e por memória ----

def por_papel(f, versoes):
    """Uma checagem sobre todas as versões do prompt de um papel: falha se falha em alguma; o pior resultado."""
    ordem = {FALHA: 0, PARCIAL: 1, PASSA: 2, NV: 3}
    res = [(v["versao"], v.get("execucoes", 0)) + f(v["prompt"]) for v in versoes]
    pior = min((r[2] for r in res), key=ordem.get)
    falham = [r for r in res if r[2] in (FALHA, PARCIAL)]
    motivos = sorted({m for r in res if r[2] == pior for m in r[3]})
    return {"resultado": pior, "versoes": len(res), "versoes_que_falham": len(falham),
            "execucoes_que_falham": sum(r[1] for r in falham), "motivos": motivos}


def agregar(detalhe, modo):
    verif = {p: d for p, d in detalhe.items() if d["resultado"] != NV}
    if not verif:
        return NV
    falham = [p for p, d in verif.items() if d["resultado"] in (FALHA, PARCIAL)]
    if modo == "qualquer":
        if any(d["resultado"] == FALHA for d in verif.values()):
            return FALHA
        return PARCIAL if falham else PASSA
    if not falham:
        return PASSA
    return FALHA if len(falham) == len(verif) and all(d["resultado"] == FALHA for d in verif.values()) else PARCIAL


def conferir_memoria(e, prompts, instr, rg):
    nomes = e.get("nomes")
    papeis = [e["scope"]["role"]] if (e.get("scope") or {}).get("role") else sorted(prompts)
    out = {}
    for chave, f, modo in (("1_ambiente", lambda p: ambiente(nomes, p), "qualquer"),
                           ("2_conflito", lambda p: conflito(nomes, p, instr), "qualquer"),
                           ("3_repete", lambda p: repete(nomes, p), "todos")):
        if not nomes:
            out[chave] = {"resultado": NV, "motivo": "a entrada não tem `nomes` (esquema 0.4)"}
            continue
        det = {p: (por_papel(f, prompts[p]) if p in prompts else
                   {"resultado": NV, "motivos": ["papel sem prompt no JSONL"]}) for p in papeis}
        out[chave] = {"resultado": agregar(det, modo), "papeis": det}
    occ = e.get("occurrences") or {}
    ex, me = int(occ.get("execucoes") or 0), len(occ.get("meses") or [])
    passa = ex >= rg["execucoes"] and me >= rg["meses"]
    out["4_recorrencia"] = {"resultado": PASSA if passa else FALHA,
                            "motivo": f"{ex} execuções, {me} meses (régua: ≥ {rg['execucoes']} e ≥ {rg['meses']})"}
    causas = e.get("causas")
    if causas is None:
        out["5_uma_causa"] = {"resultado": NV, "motivo": "a entrada não traz `causas` (a classificação de uso do script específico)"}
    else:
        distintas = sorted(set(causas.values()) if isinstance(causas, dict) else set(causas))
        out["5_uma_causa"] = {"resultado": PASSA if len(distintas) <= 1 else FALHA, "motivo": f"causas: {', '.join(distintas)}"}
    return out


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompts", required=True, help="o JSONL do prompt de cada papel e versão")
    p.add_argument("--registro", default=str(REGISTRO))
    p.add_argument("--monitoramento", default=str(MONITORAMENTO))
    p.add_argument("--id", nargs="*", help="só estas memórias")
    p.add_argument("--base", help="só as memórias desta base")
    p.add_argument("--saida", help="onde gravar o resultado (JSON)")
    p.add_argument("--registrar", action="store_true", help="grava `conferencia` e `degrau` no catálogo")
    a = p.parse_args(argv)
    reg = json.loads(Path(a.registro).read_text(encoding="utf-8"))
    mon = json.loads(Path(a.monitoramento).read_text(encoding="utf-8"))
    prompts, instr, rg = ler_prompts(a.prompts), instrucoes(mon), regua(mon)
    fonte = {"arquivo": Path(a.prompts).name, "sha256_16": _sha16(a.prompts), "papeis": len(prompts),
             "versoes": sum(len(v) for v in prompts.values())}
    hoje = datetime.date.today().isoformat()
    alvo = [e for e in reg.get("itens", []) if (not a.id or e["id"] in a.id) and (not a.base or e.get("base") == a.base)]
    resultado = []
    print(f"prompts: {fonte['arquivo']} · {fonte['sha256_16']} · {fonte['papeis']} papéis · {fonte['versoes']} versões"
          f" · régua {rg['execucoes']} execuções / {rg['meses']} meses")
    print(f"{'memória':38} " + " ".join(f"{c.split('_', 1)[1][:11]:>15}" for c in CHECAGENS))
    for e in alvo:
        ch = conferir_memoria(e, prompts, instr, rg)
        degrau = 2 if all(c["resultado"] == PASSA for c in ch.values()) else 1
        resultado.append({"id": e["id"], "base": e.get("base"), "degrau": degrau, "checagens": ch})
        print(f"{e['id'][:38]:38} " + " ".join(f"{ch[c]['resultado']:>15}" for c in CHECAGENS))
        if a.registrar:
            e["degrau"] = degrau
            e["conferencia"] = {"em": hoje, "prompts": fonte, "regua": rg,
                                "checagens": {c: ch[c]["resultado"] for c in CHECAGENS}}
    doc = {"gerado_em": hoje, "prompts": fonte, "regua": rg, "memorias": resultado}
    if a.saida:
        Path(a.saida).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"→ {a.saida}")
    if a.registrar:
        Path(a.registro).write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"catálogo: conferência gravada em {len(alvo)} memória(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
