"""Confere o arquivo final de uma mineração de candidata contra o esquema da memória da análise — e, com --converter,
transforma o registro que um notebook específico grava no formato desse esquema.

    python validar_memoria.py <esquema-memoria.json> <memoria_<u>_<base>.json>
    python validar_memoria.py <esquema-memoria.json> --converter <registro.json> --unidade <u> --base <BASE_ID>
                              --parte-especifica notebook:<nome> --comando "<o que reproduz o registro>" --saida <arquivo>

Os campos e a versão vêm do esquema (analysis/esquema-memoria.json), nunca deste script: mudar a estrutura da memória
é mudar só o esquema. A conferência:
  - a versão carimbada no arquivo é a do esquema;
  - todo campo obrigatório existe no registro e tem o tipo do esquema;
  - todo campo do registro tem origem (checado | hipotese | pendente); checado exige o comando que o reproduz;
  - campo não obrigatório do esquema que falta no registro vira PENDÊNCIA (não reprova): é assim que um campo novo do
    esquema aparece na próxima mineração sem mudar código.
Sai com 0 se aprovado, 1 se reprovado. Imprime só nomes de campo e contagens. Só biblioteca padrão.
"""

import argparse, datetime, json, sys

TIPOS = {"texto": str, "objeto": dict, "lista": list}


def tipo_ok(valor, tipo):
    if tipo == "nulo-ou-texto":
        return valor is None or isinstance(valor, str)
    return isinstance(valor, TIPOS.get(tipo, object))


def validar(esquema, arq):
    erros, pendencias = [], []
    if arq.get("esquema") != esquema["versao"]:
        erros.append(f"versão do arquivo {arq.get('esquema')!r} ≠ versão do esquema {esquema['versao']!r}")
    mem, origem = arq.get("memoria") or {}, arq.get("origem") or {}
    for chave in ("unidade", "base", "parte_especifica"):
        if not arq.get(chave):
            erros.append(f"cabeçalho sem `{chave}`")
    for campo, regra in esquema["campos"].items():
        if campo not in mem:
            (erros if regra.get("obrigatorio") else pendencias).append(f"campo `{campo}` ausente")
            continue
        if not tipo_ok(mem[campo], regra["tipo"]):
            erros.append(f"campo `{campo}`: tipo {type(mem[campo]).__name__}, o esquema pede {regra['tipo']}")
        o = origem.get(campo)
        if not o or o.get("tipo") not in ("checado", "hipotese", "pendente"):
            erros.append(f"campo `{campo}` sem origem (checado | hipotese | pendente)")
        elif o["tipo"] == "checado" and not o.get("comando"):
            erros.append(f"campo `{campo}` marcado checado sem o comando que o reproduz")
    extras = [c for c in mem if c not in esquema["campos"]]
    return erros, pendencias, extras


def converter(esquema, registro, a):
    """Um registro no formato do 06 §9 Passo 8 (o que o notebook da nº2/nº10 grava) → o arquivo do esquema. Tudo o que
    o notebook produziu é determinístico: checado, com o comando do notebook; impact fica pendente (decisão do 06)."""
    mem = {c: registro[c] for c in esquema["campos"] if c in registro}
    origem = {c: {"tipo": "checado", "comando": a.comando} for c in mem}
    if "impact" in mem and mem["impact"] is None:
        origem["impact"] = {"tipo": "pendente", "nota": "null por decisão (06 §9 Passo 8): pendente do juiz calibrado"}
    return {"esquema": esquema["versao"], "unidade": a.unidade, "base": a.base,
            "gerado_em": datetime.date.today().isoformat(), "parte_especifica": a.parte_especifica,
            "memoria": mem, "origem": origem}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("esquema"); ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--converter"); ap.add_argument("--unidade"); ap.add_argument("--base")
    ap.add_argument("--parte-especifica"); ap.add_argument("--comando"); ap.add_argument("--saida")
    ap.add_argument("--indice", type=int, help="com --converter: qual registro da lista (o notebook grava uma lista)")
    a = ap.parse_args()
    esquema = json.load(open(a.esquema, encoding="utf-8"))

    if a.converter:
        reg = json.load(open(a.converter, encoding="utf-8"))
        if isinstance(reg, list):
            alvo = [r for r in reg if a.unidade and a.unidade in json.dumps(r.get("validation", {}), ensure_ascii=False)
                    + str(r.get("category", ""))] if a.indice is None else [reg[a.indice]]
            if len(alvo) != 1:
                sys.exit(f"--converter: {len(alvo)} registros para a unidade; use --indice")
            reg = alvo[0]
        arq = converter(esquema, reg, a)
        with open(a.saida, "w", encoding="utf-8") as fh:
            json.dump(arq, fh, ensure_ascii=False, indent=2)
        print(f"convertido para o esquema {esquema['versao']} → {a.saida}")
        a.arquivo = a.saida

    arq = json.load(open(a.arquivo, encoding="utf-8"))
    erros, pendencias, extras = validar(esquema, arq)
    print(f"esquema {esquema['versao']} · unidade {arq.get('unidade')} · base {arq.get('base')} · "
          f"parte específica {arq.get('parte_especifica')}")
    origem = arq.get("origem") or {}
    tipos = {}
    for c, o in origem.items():
        tipos.setdefault(o.get("tipo"), []).append(c)
    for t in ("checado", "hipotese", "pendente"):
        if tipos.get(t):
            print(f"  {t:9}: {', '.join(sorted(tipos[t]))}")
    for p in pendencias:
        print(f"  PENDÊNCIA  {p}")
    for x in extras:
        print(f"  aviso      campo `{x}` não está no esquema")
    for e in erros:
        print(f"  REPROVA    {e}")
    print(f"\n{'aprovado' if not erros else f'reprovado ({len(erros)})'}" + (f" · {len(pendencias)} pendência(s)" if pendencias else ""))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
