"""Entrada única da third: analisar, inventariar, validar ou conferir.

analisar: gera resultados do Parquet, perfis opcionais; não aprova memória.
inventariar: só proveniência/organização, não lê payloads da fonte.
validar: testes sintéticos e AST; não executa análise real.
conferir: análise real + conferência Arrow, perfis e smoke Python; não Jupyter.
painel: MD com as tabelas e as figuras de uma rodada já gerada (só contagens).
taxas: taxas e custo com o denominador do pedido A (as contagens), só se a junção com a fonte conferir.
relatorio: painel + taxas consolidados num relatório único (<rodada>/relatorio/relatorio.md).
genealogia: o censo do sintoma e a genealogia da decisão (<rodada>/genealogia/); com --unidade, o recorte de uma unidade.

Sem comando, mostra ajuda e não executa nada. Scripts históricos não são expostos.
"""
import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="analisar aceita --extracao (v2 padrão, v1), --fonte, --referencia-sha256, --perfil, --perfil-investigacao e --saida; "
               "painel aceita --rodada; taxas e relatorio aceitam --rodada, --contagens e --fonte; "
               "genealogia aceita --rodada, --unidade e --saida.")
    parser.add_argument("comando", nargs="?", choices=["analisar", "inventariar", "validar", "conferir", "painel", "taxas", "relatorio",
                                                       "genealogia"])
    args, rest = parser.parse_known_args(argv)
    if args.comando is None:
        parser.print_help()
        return 0
    if args.comando in {"analisar", "inventariar"}:
        from execucao.executar_observada import main as execute
        return execute((["--inventario-only"] if args.comando == "inventariar" else []) + rest)
    if args.comando == "painel":
        from execucao.painel import main as panel
        return panel(rest)
    if args.comando == "taxas":
        from execucao.taxas import main as rates
        return rates(rest)
    if args.comando == "genealogia":
        from execucao.figuras_genealogia import main as genealogy
        return genealogy(rest)
    if args.comando == "relatorio":
        from execucao.relatorio import main as report
        return report(rest)
    if rest:
        parser.error("validar/conferir não aceitam argumentos adicionais nesta versão")
    if args.comando == "validar":
        from validacao.validar_observada import main as validate
        return validate()
    from validacao.conferir_rodada_observada import main as verify
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
