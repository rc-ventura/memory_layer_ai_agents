"""Replica o Ajuste 17 no pipeline da base 2 (a pasta `pipeline/` desta análise, que só existe na máquina 2).

O pipeline da base 2 é uma cópia do da base 1 (`2026-09-trace-law-flow/pipeline/`), com outro TRACE e BASE_ID. O
Ajuste 17 (livro-razão `pipeline-entre-bases.md`) muda cinco pontos do `base_pipeline.py` e um rótulo em `paleta.py` e
em `genealogia_sankey.py`. Este script aplica exatamente o mesmo texto que entrou na base 1, procurando os mesmos
trechos. Se algum trecho não for achado (ou aparecer mais de uma vez), não grava nada e diz qual. Se o ajuste já estiver
lá, não faz nada.

Por padrão só mostra o que faria. Uso, de dentro de `analysis/2026-09-trace-law-flow-second/scripts`:
    uv run replicar_ajuste17.py            # mostra
    uv run replicar_ajuste17.py --aplicar  # grava
Depois: `executar.py validar` na base 3 tem de dar as regras e catálogos iguais aos da base 2.
"""
import argparse
from pathlib import Path
import sys

HELPER = '''# Ajuste 17 (13/10/2026): a linha que falhou é `try: nome` / `except NameError:` — a verificação de existência que o
# system prompt do ContestacaoCivel instrui e que o interpretador do sandbox não captura (um nome inexistente levanta
# InterpreterError, não NameError). A assinatura decide ANTES da posição do passo anterior: sem ela, o erro cai em estado
# perdido, nome inventado ou pendente só pela posição. Base 1: 0 de 10 erros de nome; base 2: 105 de 129; base 3:
# 5.764 de 7.178 (relatório da base 3 §7.9–7.10; pipeline-entre-bases.md, Ajuste 17).
_LINHA_QUE_FALHOU = re.compile(r"failed at line '(.*?)' due to", re.S)


def verificacao_try_nameerror(m):
    """A linha que falhou — a mensagem a traz — tem `try` com `except NameError` (sozinho ou numa tupla)?"""
    linha = _LINHA_QUE_FALHOU.search(str(m))
    return bool(linha) and re.search(r"except\\s+\\(?[^)\\n:]*\\bNameError\\b", linha.group(1)) is not None


def submecanismo('''

TROCAS = {
    "base_pipeline.py": [
        ("\ndef submecanismo(", "\n" + HELPER),
        ('''    if v:
        return "nome_nao_definido"
    return "causa_sem_regra"''', '''    if v and verificacao_try_nameerror(m):
        return "verificacao_try_nameerror"
    if v:
        return "nome_nao_definido"
    return "causa_sem_regra"'''),
        ('''    "nome_nunca_definido": "U_nome_inventado",\n''',
         '''    "nome_nunca_definido": "U_nome_inventado",\n    "verificacao_try_nameerror": "U_verificacao_try_nameerror",\n'''),
        ('''                         "Usar só variáveis e funções definidas no próprio código; 'Observation' é rótulo do harness, não variável."),\n''',
         '''                         "Usar só variáveis e funções definidas no próprio código; 'Observation' é rótulo do harness, não variável."),
    "U_verificacao_try_nameerror": ("Verificação de existência por try/except NameError", FACT,
                                    "No sandbox, um nome inexistente levanta InterpreterError, que o except NameError não captura: "
                                    "para checar se uma variável já existe, usar except Exception; se ela ainda não foi criada, chamar a "
                                    "ferramenta direto. O conserto é no prompt que instrui o except NameError (Ajuste 17)."),\n'''),
        ('''    "U_campo_inexistente": {"destino": "harness", "bases": ("base1", "base2")},\n}''',
         '''    "U_campo_inexistente": {"destino": "harness", "bases": ("base1", "base2")},
    # Ajuste 17 (13/10): base 2 — causa vista no trace inteiro (3 casos; o prompt instrui o except NameError) e
    # reproduzida no smolagents; base 3 — evidência própria do padrão (a assinatura em 5.764 de 7.178 erros de nome).
    "U_verificacao_try_nameerror": {"destino": "harness", "bases": ("base2", "base3")},
}'''),
    ],
    "paleta.py": [('''    "nome_de_step_que_falhou": "Nome de um step que falhou",\n''',
                   '''    "nome_de_step_que_falhou": "Nome de um step que falhou",\n    "verificacao_try_nameerror": "Verificação por try/except NameError",\n''')],
    "genealogia_sankey.py": [('''    "U_nome_inventado": "não inventar nomes",\n''',
                              '''    "U_nome_inventado": "não inventar nomes",\n    "U_verificacao_try_nameerror": "corrigir a verificação no prompt",\n''')],
}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--aplicar", action="store_true", help="grava as mudanças (sem isto, só mostra)")
    p.add_argument("--pasta", type=Path, default=Path(__file__).resolve().parents[1] / "pipeline",
                   help="a pasta do pipeline da base 2 (padrão: ../pipeline)")
    args = p.parse_args(argv)
    novos, problemas = {}, []
    for nome, trocas in TROCAS.items():
        arq = args.pasta / nome
        if not arq.is_file():
            problemas.append(f"{arq}: não existe"); continue
        s = arq.read_text(encoding="utf-8")
        if "verificacao_try_nameerror" in s:
            print(f"{nome}: já tem o Ajuste 17 — nada a fazer"); continue
        for velho, novo in trocas:
            if s.count(velho) != 1:
                problemas.append(f"{nome}: trecho achado {s.count(velho)} vezes (esperado 1): {velho.strip().splitlines()[0][:70]!r}")
                break
            s = s.replace(velho, novo, 1)
        else:
            novos[arq] = s
            print(f"{nome}: {len(trocas)} trecho(s) a mudar")
    if problemas:
        print("NADA FOI GRAVADO. Problemas:"); [print("  -", x) for x in problemas]
        return 1
    if not args.aplicar:
        print("Só mostrando. Para gravar: --aplicar"); return 0
    for arq, s in novos.items():
        arq.write_text(s, encoding="utf-8")
    print(f"gravado em {len(novos)} arquivo(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
