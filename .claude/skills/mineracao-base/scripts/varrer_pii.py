"""Bloqueia um relatório que tenha dado de caso antes de ele sair do ambiente onde o trace mora.

    python varrer_pii.py <relatório> [<outro> ...]

Procura número de processo (CNJ, formatado ou 20 dígitos seguidos), CPF, CNPJ, e-mail e UUID (o formato do
identificador de execução). Não mascara: bloqueia. Aponta arquivo, linha e o tipo do achado — nunca o trecho, para não
repetir o dado na tela. Sai com 0 se está limpo, 1 se achou algo. Só biblioteca padrão.

Não substitui a leitura: nome de pessoa e texto de documento não têm padrão fixo. A regra do que pode sair está em
`../referencias/sigilo.md`.
"""

import re, sys

PADROES = {
    "processo (CNJ)": r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b|\b\d{20}\b",
    "CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
    "CNPJ": r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
    "e-mail": r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
    "identificador de execução (UUID)": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
}


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    achados = 0
    for arq in sys.argv[1:]:
        with open(arq, encoding="utf-8", errors="replace") as fh:
            for n, linha in enumerate(fh, 1):
                for tipo, rx in PADROES.items():
                    k = len(re.findall(rx, linha))
                    if k:
                        achados += k
                        print(f"  BLOQUEADO  {arq}:{n}  {k}× {tipo}")
    print(f"\n{'limpo — pode sair' if not achados else f'{achados} achado(s) — não sai até remover'}")
    sys.exit(1 if achados else 0)


if __name__ == "__main__":
    main()
