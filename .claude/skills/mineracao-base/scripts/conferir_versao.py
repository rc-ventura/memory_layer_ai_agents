"""Confere se o código de uma pasta de análise é o mesmo para o qual o kit de mineração foi escrito.

    python conferir_versao.py <pasta-da-analise>            # compara com o manifesto.json ao lado da skill
    python conferir_versao.py <pasta-da-analise> --gerar    # reescreve o manifesto a partir dessa pasta

O hash não depende do ambiente nem da base:
  - fim de linha normalizado (CRLF -> LF): o mesmo arquivo dá o mesmo hash em qualquer sistema;
  - no `base_pipeline.py`, as atribuições de `TRACE` e `BASE_ID` são mascaradas antes do hash — são a camada da base,
    não do método (achadas pela AST, valem em uma ou várias linhas);
  - num notebook, só o código das células entra (as saídas mudam a cada execução).

Sai com 0 se tudo bate; 1 se algum arquivo difere ou falta. Só biblioteca padrão.
"""

import ast, hashlib, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MANIFESTO = os.path.join(AQUI, "..", "manifesto.json")

# relativos à pasta da análise; os dois primeiros são compartilhados por todas as análises (ficam em analysis/)
ARQUIVOS = [
    "../leitor_trace.py",
    "../base_utils.py",
    "pipeline/base_pipeline.py",
    "pipeline/checklist.py",
    "pipeline/drill_down.py",
    "pipeline/metadados_steps.py",
    "pipeline/analise_trace_esteira_juridica.ipynb",
    "pipeline/mineracao_generica.ipynb",
    "pipeline/mineracao_unidades_n2_n10.ipynb",
    "pipeline/falhas_silenciosas.ipynb",
    "pipeline/consolidacao_unidades.ipynb",
    "audit/scripts/audit_recompute6.py",
    "audit/scripts/audit_recompute9.py",
    "audit/scripts/audit_recompute10.py",
]
CAMADA_DA_BASE = {"TRACE", "BASE_ID"}


def _texto(caminho):
    with open(caminho, "rb") as fh:
        return fh.read().decode("utf-8").replace("\r\n", "\n")


def _sem_camada_da_base(txt):
    linhas = txt.split("\n")
    for no in ast.parse(txt).body:
        if isinstance(no, ast.Assign) and any(getattr(t, "id", None) in CAMADA_DA_BASE for t in no.targets):
            nome = next(t.id for t in no.targets if getattr(t, "id", None) in CAMADA_DA_BASE)
            linhas[no.lineno - 1] = f"{nome} = <camada da base>"
            for i in range(no.lineno, no.end_lineno):
                linhas[i] = None
    return "\n".join(l for l in linhas if l is not None)


def _codigo_do_notebook(txt):
    nb = json.loads(txt)
    return "\n\n".join(f"# [{c['cell_type']}]\n" + "".join(c["source"]) for c in nb["cells"])


def assinatura(caminho):
    txt = _texto(caminho)
    if caminho.endswith("base_pipeline.py"):
        txt = _sem_camada_da_base(txt)
    elif caminho.endswith(".ipynb"):
        txt = _codigo_do_notebook(txt)
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(2)
    pasta = os.path.abspath(args[0])
    atual = {a: assinatura(os.path.join(pasta, a)) if os.path.exists(os.path.join(pasta, a)) else None
             for a in ARQUIVOS}
    if "--gerar" in sys.argv:
        faltam = [a for a, h in atual.items() if h is None]
        if faltam:
            print("não gera: faltam", ", ".join(faltam)); sys.exit(1)
        with open(MANIFESTO, "w", encoding="utf-8") as fh:
            json.dump({"arquivos": atual}, fh, indent=2, ensure_ascii=False); fh.write("\n")
        print(f"manifesto gerado com {len(atual)} arquivos"); return
    esperado = json.load(open(MANIFESTO, encoding="utf-8"))["arquivos"]
    difere = 0
    for a in ARQUIVOS:
        h, e = atual.get(a), esperado.get(a)
        estado = "FALTA" if h is None else ("ok" if h == e else "DIFERE")
        difere += estado != "ok"
        print(f"  {estado:6}  {h or '-':16}  {a}")
    print(f"\nversão do código: {'IGUAL ao manifesto' if not difere else f'{difere} arquivo(s) fora do manifesto — PARAR'}")
    sys.exit(1 if difere else 0)


if __name__ == "__main__":
    main()
