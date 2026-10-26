"""O degrau 2 da validação (conferida): as cinco checagens de cada memória do catálogo contra o ambiente e o prompt.

    python conferir_memorias.py --prompts <prompts.jsonl> [--ambiente <ambiente.json>] [--funcoes <funcoes.json>]
                                [--registro <memorias.json>] [--monitoramento <monitoramento.json>]
                                [--decisoes <decisoes.json>] [--id <id> ...] [--base <BASE_ID>]
                                [--saida <conferencia.json>] [--registrar]
    python conferir_memorias.py --prompts <prompts.jsonl> [--ambiente …] [--funcoes …] --decidir <id> <checagem>
                                --motivo "<o porquê, nas palavras do pesquisador>" [--por <quem>] [--base <BASE_ID>]

A escada e as checagens estão no doc de validação das memórias da análise (`17-validacao-memorias.md`). Este script
não lê trace nem caso: lê o catálogo (`analysis/registros/memorias.json`), o monitoramento e um JSONL com o prompt de
cada papel, uma linha por versão (`{role, versao, meses, execucoes, prompt}`), que um script da pasta da análise extrai
do trace. Os nomes que cada memória manda usar ou evitar vêm do campo estruturado `nomes` da entrada (esquema da
memória 0.4, `validation.nomes`): `importar`, `usar`, `nao_importar`, `nao_usar`. Sem `nomes`, as checagens 1 a 3 saem
"não verificável".

  1 ambiente      cada módulo de `importar` é aceito no papel; cada nome de `usar` é ferramenta declarada no prompt (os
                  `def`), atributo de um módulo aceito (`json.loads`) ou função do Python que o interpretador aceita;
                  nenhum módulo de `nao_importar` é aceito (a memória proibiria o que o ambiente permite). "Aceito" vem
                  do interpretador quando há `--ambiente` com o papel: com listas da mensagem de erro, o módulo tem de
                  estar em todas; sem lista, basta um import que rodou sem erro. Sem nada do papel no ambiente, vem da
                  lista do prompt, e o motivo diz a fonte. As funções do Python vêm de `--funcoes` (testadas no
                  interpretador); sem ele, "não verificável" (o prompt não lista as funções permitidas)
  2 conflito      o prompt cita, em forma de código (`nome`, nome(, import nome), um nome que a memória proíbe — é
                  instrução contrária ou proibição repetida, a ler; ou o prompt traz uma instrução registrada no
                  monitoramento (`instrucao_prompt`) que induz um nome que a memória proíbe (`nomes_induzidos`)
  3 repete        o conteúdo da memória já está no prompt: os módulos de `nao_importar` ficam fora da lista autorizada
                  que o prompt declara; o prompt já manda `import <módulo>` de `importar`; o prompt já cita os nomes de
                  `usar`. "falha" se tudo se repete, "parcial" se parte
  4 recorrência   a régua de memória rara do monitoramento (execuções ≥ n e meses ≥ m), sobre `occurrences`
  5 uma causa só  a memória não junta causas diferentes: só verificável se a entrada traz `causas` (a classificação
                  de uso que o script específico grava); sem ela, "não verificável"

Por papel: o da memória (`scope.role`) ou, numa memória global, todos os papéis do JSONL, menos os que o pesquisador
excluiu (`nao_vale_em` da entrada, gravado pelo `catalogar_memoria.py --excluir`; o resultado diz quais). Um papel sem prompt no
JSONL é "não verificável". Uma checagem falha num papel se falha em alguma versão do prompt dele. Na memória: as
checagens 1 e 2 falham se falham em algum papel; a 3 é "falha" se todo papel verificável repete, "parcial" se algum.
O resultado diz qual JSONL usou (nome, hash, papéis, versões): numa base sem prompt, o prompt vem de outra base e é
aproximação.

--ambiente: JSON com o que o interpretador mostrou por papel, gerado por um script da pasta da análise:
    {"fonte": {...}, "papeis": {"<papel>": {"listas": [{"modulos": [...], "meses": [...], "erros": n}],
                                            "importados": {"<módulo>": {"passos": n, "meses": [...]}}}}}
--funcoes: JSON das funções do Python testadas no interpretador: {"interpretador": "...", "funcionam": [...],
    "barradas": [...]}. Numa memória global, os papéis são os do JSONL e os do ambiente; um papel só do ambiente
    confere só a checagem 1, e sem as ferramentas (não há prompt).

Decisão do pesquisador (`--decisoes`, padrão `analysis/registros/decisoes_degrau2.json`): numa checagem que o script
não fecha (a 5 sem `causas`, um "parcial" que o pesquisador leu como ruído), o pesquisador aceita o resultado com o
motivo. `--decidir <id> <checagem> --motivo` roda a checagem e registra o resultado e os motivos que ela dá agora;
depois a checagem sai "decidido pelo pesquisador", nunca "passa", e só enquanto o script der o mesmo resultado com
motivos que a decisão cobre — se mudar, a decisão não vale e o resultado diz por quê.

--registrar grava em cada entrada do catálogo a `conferencia` (o resultado de cada checagem) e o `degrau`: 2 se as
cinco passam ou são decididas pelo pesquisador, 1 se não. Imprime só nomes, contagens e hashes. Sai com 0. Só
biblioteca padrão.
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
DECISOES = RAIZ / "analysis" / "registros" / "decisoes_degrau2.json"

LISTA = re.compile(r"only from the following list of modules:\s*\[([^\]]*)\]")
DEF = re.compile(r"^def (\w+)\(", re.M)
CHECAGENS = ("1_ambiente", "2_conflito", "3_repete", "4_recorrencia", "5_uma_causa")
PASSA, FALHA, PARCIAL, NV = "passa", "falha", "parcial", "não verificável"
DECIDIDO = "decidido pelo pesquisador"
CURTO = {DECIDIDO: "decidido"}   # na tabela impressa
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
    """O prompt cita o nome em forma de código: `nome`, nome( (sem espaço), import nome, from nome[.x] import. A prosa
    em inglês não conta: "fallback tools (actions…)" não é chamada, "the returns from tools." não é import."""
    n = re.escape(nome)
    return bool(re.search(rf"`{n}`|(?<![\w.]){n}\(|\bimport\s+{n}\b|\bfrom\s+{n}(?:\.\w+)*\s+import\b", prompt or ""))


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

def no_interpretador(mod, amb, todas=True):
    """O módulo é aceito no papel, pelo que o interpretador mostrou? (sim/não, detalhe) ou None se não mostrou nada.
    `todas`: com listas da mensagem de erro, tem de estar em todas (para mandar importar); senão, em alguma ou num
    import que rodou (para proibir: basta o ambiente aceitar uma vez)."""
    if not amb:
        return None
    listas, imp = amb.get("listas") or [], (amb.get("importados") or {}).get(mod)
    if todas and listas:
        sem = [x for x in listas if mod not in x["modulos"]]
        if not sem:
            return True, None
        meses = sorted({m for x in sem for m in x.get("meses", [])})
        return False, f"fora de {len(sem)} de {len(listas)} listas do interpretador ({', '.join(meses) or 'sem mês'})"
    if any(mod in x["modulos"] for x in listas):
        return True, "numa lista do interpretador"
    if imp:
        return True, f"importado sem erro ({imp.get('passos', 0)} passos)"
    return (False, None) if listas else None


def ambiente(nomes, prompt, amb=None, funcoes=None):
    """`prompt` None: o papel não tem prompt (só o ambiente); as ferramentas ficam não verificáveis."""
    lista, defs, motivos, nv, verificados = autorizados(prompt), declaradas(prompt), [], [], 0
    fontes = set()

    def aceito(mod, todas=True):
        r = no_interpretador(mod, amb, todas)
        if r is not None:
            fontes.add("interpretador")
            return r
        if lista is None:
            return None
        fontes.add("prompt")
        return mod in lista, None

    def fora(mod, det):
        return f"fora da lista do interpretador: {det}" if det else "fora da lista autorizada"

    for mod in nomes.get("importar", []):
        r = aceito(mod)
        if r is None:
            nv.append(f"importar {mod}: o prompt não declara a lista de imports")
            continue
        verificados += 1
        if not r[0]:
            motivos.append(f"importar {mod}: {fora(mod, r[1])}")
    for nome in nomes.get("usar", []):
        if "." in nome:
            mod = nome.split(".")[0]
            r = aceito(mod)
            if r is None:
                nv.append(f"usar {nome}: o prompt não declara a lista de imports")
                continue
            verificados += 1
            if not r[0]:
                motivos.append(f"usar {nome}: o módulo {mod} está {fora(mod, r[1])}")
        elif nome in defs:
            verificados += 1
        elif nome in FUNCOES_DO_PYTHON and funcoes:
            if nome in funcoes.get("funcionam", ()):
                verificados += 1
            elif nome in funcoes.get("barradas", ()):
                verificados += 1
                motivos.append(f"usar {nome}: função do Python barrada no interpretador")
            else:
                nv.append(f"usar {nome}: função do Python fora da lista testada")
        elif nome in FUNCOES_DO_PYTHON:
            nv.append(f"usar {nome}: função do Python (o prompt não lista as permitidas)")
        elif prompt is None:
            nv.append(f"usar {nome}: papel sem prompt (as ferramentas não se conferem)")
        else:
            verificados += 1
            motivos.append(f"usar {nome}: não é ferramenta declarada no prompt")
    for mod in nomes.get("nao_importar", []):
        r = aceito(mod, todas=False)
        if r is None:
            nv.append(f"não importar {mod}: o prompt não declara a lista de imports")
            continue
        verificados += 1
        if r[0]:
            motivos.append(f"não importar {mod}: " + (f"o interpretador aceita ({r[1]})" if r[1] else
                                                     "está na lista autorizada"))
    # com --ambiente, o motivo diz de onde veio a lista ("do prompt" quando o interpretador não mostra o papel)
    notas = [f"a lista veio do {f}" for f in sorted(fontes)] if amb is not None else []
    if motivos:
        return FALHA, motivos + notas
    if verificados:
        return PASSA, nv + notas
    return NV, (nv + notas) or ["a memória não manda usar nem evitar módulo ou ferramenta"]


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


def conferir_memoria(e, prompts, instr, rg, amb=None, funcoes=None, decisoes=None):
    """`amb`: o ambiente por papel (None sem --ambiente); `decisoes`: {(id, base, checagem): decisão}."""
    nomes = e.get("nomes")
    amb_papeis = (amb or {}).get("papeis", {})
    papel_da_memoria = (e.get("scope") or {}).get("role")
    papeis = [papel_da_memoria] if papel_da_memoria else sorted(set(prompts) | set(amb_papeis))
    # os papéis em que o pesquisador decidiu que a memória global não vale (`nao_vale_em`, catalogar_memoria.py)
    excluidos = sorted({x["papel"] for x in e.get("nao_vale_em") or []})
    papeis = [p for p in papeis if p not in excluidos]
    out = {}
    for chave, modo in (("1_ambiente", "qualquer"), ("2_conflito", "qualquer"), ("3_repete", "todos")):
        if not nomes:
            out[chave] = {"resultado": NV, "motivo": "a entrada não tem `nomes` (esquema 0.4)"}
            continue
        det = {}
        for p in papeis:
            a = None if amb is None else amb_papeis.get(p, {})
            f = {"1_ambiente": lambda t, a=a: ambiente(nomes, t, a, funcoes),
                 "2_conflito": lambda t: conflito(nomes, t, instr),
                 "3_repete": lambda t: repete(nomes, t)}[chave]
            if p in prompts:
                det[p] = por_papel(f, prompts[p])
            elif chave == "1_ambiente" and p in amb_papeis:
                det[p] = por_papel(f, [{"versao": None, "execucoes": 0, "prompt": None}])
            else:
                det[p] = {"resultado": NV, "motivos": ["papel sem prompt no JSONL"]}
        out[chave] = {"resultado": agregar(det, modo), "papeis": det}
        if excluidos:
            out[chave]["excluidos"] = excluidos
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
    for c in CHECAGENS:
        d = (decisoes or {}).get((e["id"], e.get("base"), c))
        if d:
            out[c] = aplicar_decisao(out[c], d)
    return out


def motivos_da(checagem):
    """Os motivos de uma checagem, juntando os papéis."""
    if "papeis" in checagem:
        return sorted({m for d in checagem["papeis"].values() for m in d.get("motivos", [])})
    return [checagem["motivo"]] if checagem.get("motivo") else []


def aplicar_decisao(checagem, d):
    """A decisão vale se o script dá o mesmo resultado que ela aceitou, com motivos que ela cobre."""
    novos = sorted(set(motivos_da(checagem)) - set(d.get("motivos", [])))
    if checagem["resultado"] == d["sobre"] and not novos:
        return {**checagem, "resultado": DECIDIDO, "resultado_do_script": d["sobre"], "decisao": d}
    porque = (f"o script deu '{checagem['resultado']}'" if checagem["resultado"] != d["sobre"]
              else f"motivos novos: {'; '.join(novos)}")
    return {**checagem, "decisao_nao_vale": f"a decisão de {d['em']} aceitou '{d['sobre']}'; {porque}"}


def ler_decisoes(caminho):
    """{(id, base, checagem): decisão} do registro (lista `itens`); vazio se o arquivo não existe."""
    p = Path(caminho)
    if not p.exists():
        return {}
    return {(d["id"], d.get("base"), d["checagem"]): d
            for d in json.loads(p.read_text(encoding="utf-8")).get("itens", [])}


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompts", required=True, help="o JSONL do prompt de cada papel e versão")
    p.add_argument("--ambiente", help="o JSON do que o interpretador mostrou por papel (listas e imports que rodaram)")
    p.add_argument("--funcoes", help="o JSON das funções do Python testadas no interpretador")
    p.add_argument("--registro", default=str(REGISTRO))
    p.add_argument("--monitoramento", default=str(MONITORAMENTO))
    p.add_argument("--decisoes", default=str(DECISOES), help="o registro das decisões do pesquisador no degrau 2")
    p.add_argument("--id", nargs="*", help="só estas memórias")
    p.add_argument("--base", help="só as memórias desta base")
    p.add_argument("--saida", help="onde gravar o resultado (JSON)")
    p.add_argument("--registrar", action="store_true", help="grava `conferencia` e `degrau` no catálogo")
    p.add_argument("--decidir", nargs=2, metavar=("ID", "CHECAGEM"),
                   help="registra que o pesquisador aceita o resultado que a checagem dá agora")
    p.add_argument("--motivo", help="com --decidir: o porquê, nas palavras do pesquisador")
    p.add_argument("--por", default="pesquisador", help="com --decidir: quem decidiu")
    a = p.parse_args(argv)
    if a.decidir and (not a.motivo or a.decidir[1] not in CHECAGENS):
        p.error(f"--decidir pede --motivo e uma checagem entre {', '.join(CHECAGENS)}")
    reg = json.loads(Path(a.registro).read_text(encoding="utf-8"))
    mon = json.loads(Path(a.monitoramento).read_text(encoding="utf-8"))
    prompts, instr, rg = ler_prompts(a.prompts), instrucoes(mon), regua(mon)
    amb = json.loads(Path(a.ambiente).read_text(encoding="utf-8")) if a.ambiente else None
    funcoes = json.loads(Path(a.funcoes).read_text(encoding="utf-8")) if a.funcoes else None
    decisoes = ler_decisoes(a.decisoes)
    fonte = {"arquivo": Path(a.prompts).name, "sha256_16": _sha16(a.prompts), "papeis": len(prompts),
             "versoes": sum(len(v) for v in prompts.values())}
    for nome, arq in (("ambiente", a.ambiente), ("funcoes", a.funcoes)):
        if arq:
            fonte[nome] = {"arquivo": Path(arq).name, "sha256_16": _sha16(arq)}
    if amb is not None:
        fonte["ambiente"]["papeis"] = len(amb.get("papeis", {}))
    hoje = datetime.date.today().isoformat()
    if a.decidir:
        return decidir(a, reg, prompts, instr, rg, amb, funcoes, decisoes, fonte, hoje)
    alvo = [e for e in reg.get("itens", []) if (not a.id or e["id"] in a.id) and (not a.base or e.get("base") == a.base)]
    resultado = []
    print(f"prompts: {fonte['arquivo']} · {fonte['sha256_16']} · {fonte['papeis']} papéis · {fonte['versoes']} versões"
          f" · régua {rg['execucoes']} execuções / {rg['meses']} meses")
    for nome in ("ambiente", "funcoes"):
        if nome in fonte:
            print(f"{nome}: {fonte[nome]['arquivo']} · {fonte[nome]['sha256_16']}")
    print(f"{'memória':38} " + " ".join(f"{c.split('_', 1)[1][:11]:>15}" for c in CHECAGENS))
    for e in alvo:
        ch = conferir_memoria(e, prompts, instr, rg, amb, funcoes, decisoes)
        degrau = 2 if all(c["resultado"] in (PASSA, DECIDIDO) for c in ch.values()) else 1
        resultado.append({"id": e["id"], "base": e.get("base"), "degrau": degrau, "checagens": ch})
        print(f"{e['id'][:38]:38} " + " ".join(f"{CURTO.get(ch[c]['resultado'], ch[c]['resultado']):>15}"
                                               for c in CHECAGENS))
        for c in CHECAGENS:
            if "decisao_nao_vale" in ch[c]:
                print(f"  ! {c}: {ch[c]['decisao_nao_vale']}")
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


def decidir(a, reg, prompts, instr, rg, amb, funcoes, decisoes, fonte, hoje):
    """Roda a checagem na memória e registra o resultado e os motivos de agora como aceitos pelo pesquisador."""
    ident, chave = a.decidir
    alvo = [e for e in reg.get("itens", []) if e["id"] == ident and (not a.base or e.get("base") == a.base)]
    if len(alvo) != 1:
        sys.exit(f"{ident}: {len(alvo)} entradas no catálogo (use --base para escolher uma)")
    e = alvo[0]
    sem = {k: v for k, v in decisoes.items() if k != (e["id"], e.get("base"), chave)}
    ch = conferir_memoria(e, prompts, instr, rg, amb, funcoes, sem)[chave]
    if ch["resultado"] == PASSA:
        sys.exit(f"{ident} · {chave}: o script já dá 'passa'; não há o que decidir")
    item = {"id": e["id"], "base": e.get("base"), "checagem": chave, "sobre": ch["resultado"],
            "motivos": motivos_da(ch), "por": a.por, "em": hoje, "motivo": a.motivo, "fonte": fonte}
    p = Path(a.decisoes)
    doc = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"o_que_e": O_QUE_E_DECISOES, "itens": []}
    doc["itens"] = [d for d in doc["itens"] if (d["id"], d.get("base"), d["checagem"]) != (e["id"], e.get("base"), chave)]
    doc["itens"].append(item)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"decisão registrada: {ident} · {chave} · aceito '{item['sobre']}' ({len(item['motivos'])} motivo(s)) → {p}")
    return 0


O_QUE_E_DECISOES = ("As decisões do pesquisador no degrau 2 (conferida) da validação das memórias: numa checagem que o "
                    "script não fecha, o resultado que o pesquisador aceitou, os motivos que o script dava e o porquê. "
                    "Gravado por `conferir_memorias.py --decidir`; lido pelo mesmo script, que mostra a checagem como "
                    "'decidido pelo pesquisador' enquanto o resultado e os motivos forem os aceitos.")


if __name__ == "__main__":
    raise SystemExit(main())
