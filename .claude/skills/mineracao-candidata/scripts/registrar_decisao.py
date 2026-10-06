"""Registra a decisão do pesquisador no gate de uma lição — por script, com as palavras dele, sem ninguém editar JSON
à mão. O painel (valor_da_licao.py) lê este registro e deixa de mostrar "aguardando" para a situação decidida.

    python registrar_decisao.py <pasta-da-analise> <unidade> --etapa lista|situacao --situacao "<situação do painel>"
                                --opcao "<a opção escolhida>" --porque "<o porquê, nas palavras do pesquisador>"
                                [--licao "<a lição aprovada ou reescrita>"]

--etapa lista     o gate da leitura aberta: o pesquisador aprova (ou edita) a lista de lições e causas que vai para a
                  leitura fechada. Use --situacao "lista" e, em --opcao, "aprovada" ou "editada".
--etapa situacao  o gate do painel, depois da leitura fechada (as situações com opções no valor_da_licao.py).
Grava em pipeline/resultados/mineracao/<unidade>/decisoes.json (acrescenta; nunca apaga). Só biblioteca padrão.
"""

import argparse, datetime, json, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("unidade")
    ap.add_argument("--etapa", choices=["lista", "situacao"], required=True)
    ap.add_argument("--situacao", required=True); ap.add_argument("--opcao", required=True)
    ap.add_argument("--porque", required=True); ap.add_argument("--licao")
    x = ap.parse_args()
    arq = os.path.join(os.path.abspath(x.pasta), "pipeline", "resultados", "mineracao", x.unidade, "decisoes.json")
    d = json.load(open(arq, encoding="utf-8")) if os.path.exists(arq) else []
    item = {"data": datetime.date.today().isoformat(), "etapa": x.etapa, "situacao": x.situacao, "opcao": x.opcao,
            "porque": x.porque}
    if x.licao:
        item["licao"] = x.licao
    d.append(item)
    with open(arq, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    print(f"decisão registrada ({x.etapa}: {x.situacao} → {x.opcao}) em {arq}")


if __name__ == "__main__":
    main()
