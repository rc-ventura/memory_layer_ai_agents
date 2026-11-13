"""Testa, no interpretador do smolagents, as construções de Python do grupo "limites do interpretador" do resíduo da
base 3 (b3 #5) e os consertos propostos para cada uma.

Para cada construção (`{**x}`, `:=`, `global`, `nonlocal`, `raise` sozinho, desempacotar o que não é tupla) roda um
código sintético curto em três lugares: no Python normal (`exec`), para saber se é Python válido; no `LocalPythonExecutor`
do smolagents, para reproduzir a mensagem do trace; e, para cada conserto proposto, de novo no interpretador, para saber
se ele roda e dá o mesmo resultado que o Python normal dá ao código original.

Um caso testa a hipótese do `global` e do `raise` sem a palavra na linha que falhou: a função é definida num passo
(uma chamada do executor) e chamada no seguinte; o interpretador só avalia o corpo na chamada, e a mensagem traz a linha
da chamada.

Código sintético, nenhum dado de caso. Uso, da raiz (o smolagents não é dependência do projeto):
    uv run --no-project --with smolagents==1.26.0 python analysis/2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_construtos.py
"""
import platform
import re

import smolagents
from smolagents.local_python_executor import LocalPythonExecutor

# (construção, [código em passos], variável do resultado, [(conserto, [código em passos])])
CASOS = [
    ("{**x} num dicionário", ["a = {'x': 1}\nb = {'y': 2}\nd = {**a, 'k': 3, **b}"], "d", [
        ("dict(a) + d['k'] = v + update(b)", ["a = {'x': 1}\nb = {'y': 2}\nd = dict(a)\nd['k'] = 3\nd.update(b)"]),
        ("dict(a, k=v, **b) (** na chamada)", ["a = {'x': 1}\nb = {'y': 2}\nd = dict(a, k=3, **b)"]),
        ("a | {'k': v} | b", ["a = {'x': 1}\nb = {'y': 2}\nd = a | {'k': 3} | b"]),
    ]),
    ("{**x} na compreensão (a forma do trace)",
     ["docs = [{'h': 1, 'm': [{'n': 'p', 'v': 9}]}]\n"
      "regs = [\n    {\n        'h': d['h'],\n        **{m['n']: m['v'] for m in d['m']}\n    }\n    for d in docs\n]"],
     "regs", [
        ("laço com dict + update",
         ["docs = [{'h': 1, 'm': [{'n': 'p', 'v': 9}]}]\nregs = []\nfor d in docs:\n    r = {'h': d['h']}\n"
          "    r.update({m['n']: m['v'] for m in d['m']})\n    regs.append(r)"]),
        ("dict(..., **{...}) na compreensão",
         ["docs = [{'h': 1, 'm': [{'n': 'p', 'v': 9}]}]\n"
          "regs = [dict({'h': d['h']}, **{m['n']: m['v'] for m in d['m']}) for d in docs]"]),
    ]),
    (":= no if", ["xs = [1, 2, 3]\nr = 0\nif (n := len(xs)) > 1:\n    r = n"], "r", [
        ("atribuir antes", ["xs = [1, 2, 3]\nr = 0\nn = len(xs)\nif n > 1:\n    r = n"]),
    ]),
    (":= no ternário", ["xs = [1, 2, 3]\nr = n if (n := len(xs)) > 1 else 0"], "r", [
        ("atribuir antes", ["xs = [1, 2, 3]\nn = len(xs)\nr = n if n > 1 else 0"]),
    ]),
    (":= na compreensão", ["xs = [1, 2, 3]\nr = [y for x in xs if (y := x * 2) > 2]"], "r", [
        ("laço explícito", ["xs = [1, 2, 3]\nr = []\nfor x in xs:\n    y = x * 2\n    if y > 2:\n        r.append(y)"]),
    ]),
    ("global no mesmo passo", ["total = 0\ndef soma(v):\n    global total\n    total += v\nsoma(5)\nr = total"], "r", [
        ("a função devolve o valor", ["total = 0\ndef soma(t, v):\n    return t + v\ntotal = soma(total, 5)\nr = total"]),
        ("dicionário mutável", ["estado = {'total': 0}\ndef soma(v):\n    estado['total'] += v\nsoma(5)\n"
                                "r = estado['total']"]),
    ]),
    ("global definido num passo, chamado no seguinte",
     ["total = 0\ndef soma(v):\n    global total\n    total += v", "soma(5)\nr = total"], "r", [
        ("a função devolve o valor", ["total = 0\ndef soma(t, v):\n    return t + v", "total = soma(total, 5)\nr = total"]),
    ]),
    ("nonlocal", ["def conta():\n    n = 0\n    def mais():\n        nonlocal n\n        n += 1\n    mais()\n"
                  "    mais()\n    return n\nr = conta()"], "r", [
        ("contador num dicionário", ["def conta():\n    c = {'n': 0}\n    def mais():\n        c['n'] += 1\n"
                                     "    mais()\n    mais()\n    return c['n']\nr = conta()"]),
    ]),
    ("raise sozinho dentro do except",
     ["r = 'ok'\ntry:\n    try:\n        1 / 0\n    except ZeroDivisionError:\n        raise\n"
      "except ZeroDivisionError:\n    r = 'repassou'"], "r", [
        ("raise e", ["r = 'ok'\ntry:\n    try:\n        1 / 0\n    except ZeroDivisionError as e:\n        raise e\n"
                     "except ZeroDivisionError:\n    r = 'repassou'"]),
    ]),
    ("raise sozinho numa função chamada no except",
     ["def repassa():\n    raise", "r = 'ok'\ntry:\n    try:\n        1 / 0\n    except ZeroDivisionError:\n"
      "        repassa()\nexcept ZeroDivisionError:\n    r = 'repassou'"], "r", [
        ("raise e com a exceção passada", ["def repassa(e):\n    raise e",
                                           "r = 'ok'\ntry:\n    try:\n        1 / 0\n    except ZeroDivisionError as e:\n"
                                           "        repassa(e)\nexcept ZeroDivisionError:\n    r = 'repassou'"]),
    ]),
    # Contraste (não são deste grupo): a função barrada pelo nome (o inventário do sandbox, a verificação de existência)
    # e o idioma que o interpretador implementa diferente (a unidade do next() sobre gerador).
    ("contraste · globals(), a função (barrada pelo nome)", ["x = 1\nr = 'x' in globals()"], "r", [
        ("try/except Exception", ["x = 1\ntry:\n    x\n    r = True\nexcept Exception:\n    r = False"]),
    ]),
    ("contraste · next() sobre gerador", ["xs = [1, 2, 3]\nr = next(x for x in xs if x > 1)"], "r", [
        ("[...][0]", ["xs = [1, 2, 3]\nr = [x for x in xs if x > 1][0]"]),
    ]),
    ("desempacotar o que não é tupla",["d = {'a': 1, 'b': 2}\nr = []\nfor k, v in d:\n    r.append(k)"], "r", [
        (".items()", ["d = {'a': 1, 'b': 2}\nr = []\nfor k, v in d.items():\n    r.append(k)"]),
    ]),
]


def python(passos, var):
    """Roda no Python normal: ('ok', valor) ou ('erro', 'Tipo: mensagem')."""
    ns = {}
    try:
        for p in passos:
            exec(p, ns)
        return "ok", ns.get(var)
    except Exception as e:
        return "erro", f"{type(e).__name__}: {e}"


def sandbox(passos, var):
    """Roda no LocalPythonExecutor, um passo por chamada (o estado persiste entre elas, como nos passos do agente)."""
    ex = LocalPythonExecutor(additional_authorized_imports=[])
    ex.send_tools({})
    try:
        for p in passos:
            ex(p)
        return "ok", ex.state.get(var)
    except Exception as e:
        return "erro", str(e)


def resumo_erro(msg):
    """A mensagem do interpretador sem o código: o erro e a 1ª linha da linha que falhou."""
    linha = re.search(r"failed at line '(.*?)' due to", msg, re.S)
    erro = re.sub(r"(?s).*due to: ", "", msg).strip().splitlines()[0][:90]
    return erro + (f"  [linha que falhou começa com: {linha.group(1).strip().splitlines()[0][:40]!r}]" if linha else "")


def main():
    print(f"smolagents {smolagents.__version__}, Python {platform.python_version()}\n")
    for nome, passos, var, consertos in CASOS:
        py, sb = python(passos, var), sandbox(passos, var)
        print(f"■ {nome}")
        print(f"    Python normal: {py[0]} → {py[1]!r}")
        print(f"    interpretador: {sb[0]} → {resumo_erro(sb[1]) if sb[0] == 'erro' else repr(sb[1])}")
        for cn, cp in consertos:
            c = sandbox(cp, var)
            igual = c[0] == "ok" and py[0] == "ok" and c[1] == py[1]
            if py[0] == "erro":   # o original já falha no Python normal: não há valor para comparar
                veredito = "roda (o original falha também no Python)" if c[0] == "ok" else "FALHA"
            else:
                veredito = "RESOLVE" if igual else ("roda, valor diferente" if c[0] == "ok" else "FALHA")
            det = repr(c[1]) if c[0] == "ok" else resumo_erro(c[1])
            print(f"    conserto «{cn}»: {veredito} → {det}")
        print()


if __name__ == "__main__":
    main()
