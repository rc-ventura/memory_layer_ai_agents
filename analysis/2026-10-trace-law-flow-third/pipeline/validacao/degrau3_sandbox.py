"""Base 3: o degrau 3 das memórias do sandbox sem cota de IA na máquina — contagens por regra e casos mascarados.

O degrau 3 (revisada: a causa é a que a memória supõe?) seria lido por dois leitores automáticos na máquina da base. Sem
cota lá (até 30/10), o Rafael decidiu em 26/10 (dossiê do sandbox §2h, 30): (1) as **regras contadas** sobre a população
inteira de cada memória, que só imprimem números e categorias; (2) **10 casos por memória**, mascarados, fotografados e
lidos aqui — só o código e as mensagens de erro (técnicos, podem sair pela regra de sigilo de 16/10), com todo texto entre
aspas, todo comentário e todo número trocados por `<texto>`, `# <comentário>` e `<n>`; sem a saída do modelo nem as
observações (conteúdo de cliente). A saída passa pelos padrões do `varrer_pii.py` antes de ser impressa: se achar algo,
não imprime.

    python degrau3_sandbox.py contar --fonte <parquet v2> [--mineracao <pasta da mineração do sandbox>]
    python degrau3_sandbox.py casos <memoria_id> --fonte <parquet v2> [--n 10] [--amostra <casos.csv>]

`contar`, por memória (C, C.JoogleAnalytics, E; a população é o `erros_lidos.csv` da mineração):
  - C e C.JoogleAnalytics: a linha que falhou usa o nome direto (`json.`, `pd.`…) ou não (função auxiliar, linha cortada);
    o passo seguinte importa o módulo? e o erro que vem depois, pela assinatura mascarada (as 12 mais comuns) — a pergunta
    aberta da C.JoogleAnalytics (77% com outro erro depois do import);
  - E: por nome, onde está a chamada barrada na linha que falhou: dentro de `print(...)`, numa atribuição, numa condição,
    num `return`, outra.
`casos`: os primeiros `--n` da amostra do degrau 3 (`resultados/evidencia/inv_candidata_<memoria>_base3/casos.csv`, já
escolhida por regra fixa), em forma compacta: a mensagem de erro, a linha que falhou e as vizinhas no código do passo, o
passo anterior e o seguinte (importou? que erro?).

Uso, da raiz, na máquina da base:
    uv run analysis/2026-10-trace-law-flow-third/pipeline/validacao/degrau3_sandbox.py contar --fonte analysis/2026-10-trace-law-flow-third/data/base_erros_minerados_full_v2.parquet
"""
import argparse
from collections import Counter
import csv
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import sys

import pyarrow.parquet as pq

AQUI = Path(__file__).resolve().parent
PIPELINE = AQUI.parent
RAIZ = PIPELINE.parents[2]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(PIPELINE))
from contar_modulo_sem_import_papel import LINHA_FALHA, importa  # noqa: E402
from mineracao_observada import caminho_io  # noqa: E402

MEMORIAS = ("U_sandbox.C", "U_sandbox.C.JoogleAnalytics", "U_sandbox.E")
MODULO = {"json": "json", "re": "re", "datetime": "datetime", "pd": "pandas"}   # o nome usado → o módulo do import
COLUNAS = ["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos", "mes_execucao", "error_message", "error_code_action",
           "prev_code_action", "prev_error_type", "next_code_action", "next_error_type", "next_error_message"]
TRIPLA = re.compile(r'(?s)[rRbBfFuU]{0,2}("""|\'\'\').*?\1')
SIMPLES = re.compile(r'''[rRbBfFuU]{0,2}("|')(?:\\.|(?!\1)[^\\\n])*\1''')
TRIPLA_ABERTA = re.compile(r'(?s)[rRbBfFuU]{0,2}("""|\'\'\').*')   # abre e não fecha no trecho: mascara até o fim
COMENTARIO = re.compile(r"#.*")
NUMERO = re.compile(r"\b\d+(?:[.,]\d+)*\b")
# uma linha que, mesmo mascarada, parece texto corrido ou markdown não sai (proteção a mais: pode omitir código legítimo)
TEXTO_CORRIDO = re.compile(r"(?:\b[^\W\d_]{2,}\b[ ,;:]+){6,}|^\s*(?:\||\*\*|-{3,})|\*\*")


def _padroes_pii():
    """Os padrões do varredor do kit (`.claude/skills/` ou `.github/skills/`, na máquina da base)."""
    for pasta in (".claude", ".github", ".copilot"):
        arq = RAIZ / pasta / "skills" / "mineracao-base" / "scripts" / "varrer_pii.py"
        if arq.exists():
            spec = spec_from_file_location("varrer_pii", arq)
            m = module_from_spec(spec)
            spec.loader.exec_module(m)
            return m.PADROES
    sys.exit("varrer_pii.py não encontrado nas pastas de skills: sem ele, os casos não saem")


def mascarar(texto):
    """Troca texto entre aspas, comentários e números: o que pode carregar conteúdo de cliente."""
    t = TRIPLA.sub('"<texto>"', str(texto or ""))
    t = TRIPLA_ABERTA.sub('"<texto…>"', t)
    t = SIMPLES.sub('"<texto>"', t)
    t = COMENTARIO.sub("# <comentário>", t)
    return NUMERO.sub("<n>", t)


def instrucao_que_falhou(msg):
    """A instrução que falhou, inteira (pode ter várias linhas, como um texto longo entre aspas triplas). Sem máscara:
    só para as regras; o que se imprime passa por `mascarar`."""
    f = LINHA_FALHA.search(str(msg or ""))
    return f.group(1).strip() if f else ""


def linha_que_falhou(msg):
    i = instrucao_que_falhou(msg)
    return i.splitlines()[0].strip() if i else ""


def linhas_seguras(codigo):
    """O código mascarado inteiro (as aspas triplas atravessam linhas) e quebrado em linhas; a que ainda parece texto
    corrido sai como omitida."""
    return ["<linha omitida: parece texto>" if TEXTO_CORRIDO.search(l) else l
            for l in mascarar(codigo).splitlines()]


def assinatura(msg):
    """O último trecho da mensagem (depois de "due to:"), mascarado e curto: o tipo do erro e o padrão."""
    if not str(msg or "").strip():
        return "(sem erro)"
    t = str(msg).rsplit("due to:", 1)[-1].strip()
    # o nome da função barrada é técnico: fica (o resto entre aspas é mascarado)
    t = re.sub(r"(Forbidden function evaluation: )'(\w+)'", r"\1FUNCAO_\2", t)
    t = re.sub(r"\s+", " ", mascarar(t)).replace("FUNCAO_", "")
    return t[:90]


def lugar_na_linha(linha):
    """Onde está a chamada na linha que falhou (para a E)."""
    s = linha.strip()
    if not s:
        return "linha não vista"
    if "print(" in s:
        return "dentro de print(...)"
    if re.match(r"(if|elif|while|assert)\b", s):
        return "numa condição"
    if s.startswith("return"):
        return "num return"
    if re.match(r"[\w\.\[\]\"'<>, ]+=(?!=)", s):
        return "numa atribuição"
    return "outra"


def ler_populacao(pasta, memorias):
    with open(caminho_io(Path(pasta) / "erros_lidos.csv"), encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r.get("memoria_id") in memorias]


def ler_fonte(fonte, chaves):
    """{(exec, agente, papel, posição): linha da fonte} só das chaves pedidas."""
    t = pq.read_table(caminho_io(fonte), columns=COLUNAS).to_pylist()
    return {k: r for r in t if (k := (str(r["cod_idef_exeo"]), str(r["cod_idef_aget"]), str(r["papel"]),
                                      str(int(r["step_pos"])))) in chaves}


def chave(r):
    return (str(r["exec_id"]), str(r["agente"]), str(r["role"]), str(int(float(r["step_pos"]))))


def contar(populacao, fonte):
    """{memoria: medidas} — só números e categorias."""
    saida = {}
    for mem in MEMORIAS:
        P = [r for r in populacao if r["memoria_id"] == mem]
        M = {"erros": len(P), "achados_na_fonte": 0}
        if mem == "U_sandbox.E":
            por = Counter()
            for r in P:
                linha = fonte.get(chave(r))
                if linha is None:
                    continue
                M["achados_na_fonte"] += 1
                por[(r["nome"], lugar_na_linha(linha_que_falhou(linha["error_message"])))] += 1
            M["por_nome_e_lugar"] = por
        else:
            uso, depois, sig = Counter(), Counter(), Counter()
            for r in P:
                linha = fonte.get(chave(r))
                if linha is None:
                    continue
                M["achados_na_fonte"] += 1
                nome = r["nome"]
                mod = MODULO.get(nome, nome)
                falhou = instrucao_que_falhou(linha["error_message"])
                uso["o nome aparece na instrução que falhou" if re.search(rf"\b{re.escape(nome)}\s*[\.\(\[]", falhou)
                    else "o nome não aparece na instrução (função auxiliar?)"] += 1
                importou = importa(linha.get("next_code_action"), mod)
                erro = str(linha.get("next_error_type") or "").strip()
                depois[("importa" if importou else "não importa") + (" · com erro" if erro else " · sem erro")] += 1
                if importou and erro:
                    sig[assinatura(linha.get("next_error_message"))] += 1
            M.update({"uso": uso, "depois": depois, "erro_seguinte": sig})
        saida[mem] = M
    return saida


def imprimir_contagens(med):
    for mem, M in med.items():
        print(f"\n== {mem}: {M['erros']} erros na mineração · {M['achados_na_fonte']} achados na fonte")
        if "por_nome_e_lugar" in M:
            print(f"   {'nome':14} {'onde, na linha que falhou':28} {'erros':>6}")
            for (nome, lugar), k in sorted(M["por_nome_e_lugar"].items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"   {nome:14} {lugar:28} {k:>6}")
            continue
        for titulo, c in (("a linha que falhou", M["uso"]), ("o passo seguinte", M["depois"])):
            print(f"   {titulo}:")
            for k, v in c.most_common():
                print(f"     {k:44} {v:>5}")
        print("   o erro depois do import (assinatura mascarada, as 12 mais comuns):")
        for k, v in M["erro_seguinte"].most_common(12):
            print(f"     {v:>5}  {k}")


def bloco_caso(i, r, linha, mod):
    """O caso em forma compacta e mascarada (texto pronto para checar no varredor e imprimir)."""
    falhou = linha_que_falhou(linha["error_message"])
    bruto = str(linha.get("error_code_action") or "").splitlines()
    pos = next((j for j, l in enumerate(bruto) if falhou and l.strip() == falhou), None)
    seguro = linhas_seguras("\n".join(bruto))
    ini = max(0, pos - 3) if pos is not None else 0
    fim = pos + 2 if pos is not None else 5
    L = [f"── caso {i} · {r['role']} · {r.get('mes', '')} · exec {str(r['exec_id'])[:8]} · posição {r['step_pos']}",
         f"   erro: {assinatura(linha['error_message'])}",
         f"   linha que falhou: {(linhas_seguras(falhou) or ['(não vista)'])[0][:110]}",
         "   código em volta:"]
    L += [f"   {'>>' if j == pos else '  '} {l[:110]}" for j, l in enumerate(seguro[ini:fim], ini)]
    ant, seg = str(linha.get("prev_code_action") or ""), str(linha.get("next_code_action") or "")
    imp = (lambda c: f"importou {mod}? {'sim' if importa(c, mod) else 'não'} · ") if mod else (lambda c: "")
    L.append(f"   passo anterior: {imp(ant)}erro: {str(linha.get('prev_error_type') or '—').strip() or '—'}")
    L.append(f"   passo seguinte: {imp(seg)}erro: {assinatura(linha.get('next_error_message'))}")
    L += [f"      {l[:110]}" for l in linhas_seguras(seg)[:4]]
    return "\n".join(L)


def casos(mem, amostra, fonte, n, populacao):
    with open(caminho_io(amostra), encoding="utf-8", newline="") as fh:
        A = list(csv.DictReader(fh))[:n]
    nomes = {chave(r): r["nome"] for r in populacao}
    blocos = []
    for i, r in enumerate(A, 1):
        r = {**r, "step_pos": r.get("step_pos") or r.get("idx")}
        linha = fonte.get(chave(r))
        if linha is None:
            blocos.append(f"── caso {i}: não achado na fonte")
            continue
        nome = nomes.get(chave(r), "")
        blocos.append(bloco_caso(i, r, linha, MODULO.get(nome, nome) if mem != "U_sandbox.E" else ""))
    return "\n".join(blocos)


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome in ("contar", "casos"):
        s = sub.add_parser(nome)
        s.add_argument("--fonte", required=True, type=Path, help="o parquet da base 3 (a v2, em data/)")
        s.add_argument("--mineracao", type=Path, default=PIPELINE / "resultados" / "mineracao" / "U_sandbox")
        if nome == "casos":
            s.add_argument("memoria", choices=MEMORIAS)
            s.add_argument("--n", type=int, default=10)
            s.add_argument("--amostra", type=Path, help="o casos.csv da amostra (padrão: a evidência do degrau 3)")
    a = p.parse_args(argv)
    memorias = MEMORIAS if a.cmd == "contar" else (a.memoria,)
    pop = ler_populacao(a.mineracao, memorias)
    if a.cmd == "contar":
        imprimir_contagens(contar(pop, ler_fonte(a.fonte, {chave(r) for r in pop})))
        return 0
    amostra = a.amostra or PIPELINE / "resultados" / "evidencia" / f"inv_candidata_{a.memoria}_base3" / "casos.csv"
    with open(caminho_io(amostra), encoding="utf-8", newline="") as fh:
        chaves = {chave({**r, "step_pos": r.get("step_pos") or r.get("idx")}) for r in csv.DictReader(fh)}
    texto = casos(a.memoria, amostra, ler_fonte(a.fonte, chaves), a.n, pop)
    achados = {tipo: len(re.findall(rx, texto)) for tipo, rx in _padroes_pii().items()}
    if any(achados.values()):
        print("BLOQUEADO: o varredor achou " + ", ".join(f"{k}× {t}" for t, k in achados.items() if k)
              + " — os casos não saem")
        return 1
    print(f"{a.memoria} · {texto.count('── caso')} casos (mascarados; varredor limpo)\n{texto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
