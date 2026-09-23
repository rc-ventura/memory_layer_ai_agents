"""Paleta compartilhada das figuras do trace — cor por NOME, nunca por posição.

Módulo só de apresentação (a espinha computacional continua em base_pipeline.py). Existe para
que a mesma unidade/família tenha a mesma cor em qualquer run: quando a cor seguia a posição
da coluna (8.8) ou o ranking por volume (Sankey), uma unidade ausente num recorte ou uma
ordem de volume diferente noutra base deslocava todas as cores seguintes.

    from paleta import *

As cores são as que a base 1 já usava — as figuras dela não mudam. Nome sem cor fixa cai
no cinza e avisa (`cor`): uma família nova de outra base aparece como pendência, em vez de
herdar em silêncio a cor de alguém.
"""

__all__ = ["SURFACE", "INK", "INK2", "MUTED", "GRID", "BASE", "BLUE", "BLUE_DK", "ORANGE",
           "GREEN", "YELLOW", "PINK", "CINZA", "PALETTE", "CAT_U", "COR_UNIDADE", "COR_FAMILIA", "cor"]

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE, BLUE, BLUE_DK, ORANGE = "#e1e0d9", "#c3c2b7", "#2a78d6", "#1c5cab", "#eb6834"
GREEN, YELLOW, PINK = "#1baf7a", "#eda100", "#e87ba4"
CINZA = "#9a988f"

# paleta categórica, ordem fixa (validate_palette.js: PASS) — a ordem só importa para quem a
# consulta por índice; as figuras abaixo consultam pelos dicionários de nome
PALETTE = [BLUE, ORANGE, GREEN, YELLOW, PINK, "#008300", "#4a3aa7", "#e34948"]

# as 5 unidades destacadas no 8.8 — FIXAS (as maiores da base 1), não recalculadas por run:
# recalcular trocaria o destaque de base para base e a comparação entre runs se perderia
CAT_U = ["U_texto_literal", "U_contrato_dict", "U_tipo_retorno", "U_arg_nomeado", "U_campo_inexistente"]

COR_UNIDADE = {
    "U_texto_literal": BLUE,
    "U_contrato_dict": ORANGE,
    "U_tipo_retorno": GREEN,
    "U_arg_nomeado": YELLOW,
    "U_campo_inexistente": PINK,
    "Outras candidatas": BASE,     # cinza claro = candidata também, fora do destaque
    "Não vira memória": MUTED,     # cinza escuro = harness/infra/reprovada na triagem
}

# a cor que cada família já tinha na base 1 (ranking por volume de lá aplicado ao PALETTE),
# agora presa ao nome
COR_FAMILIA = {
    "Geração de código": PALETTE[0],
    "Contrato de retorno da ferramenta": PALETTE[1],
    "Convenção de chamada de ferramenta": PALETTE[2],
    "Protocolo do harness": PALETTE[3],
    "Ambiente & sandbox": PALETTE[4],
    "Suposição sobre estado": PALETTE[5],
    "Infra / LLM upstream": PALETTE[6],
    "Suposição sobre dados": PALETTE[7],
    "Sintoma não reconhecido": CINZA,
}

_avisados = set()


def cor(dic, nome, fallback=CINZA):
    """Cor fixa de `nome` em `dic`; sem entrada → `fallback` e um aviso (uma vez por nome)."""
    if nome in dic:
        return dic[nome]
    if nome not in _avisados:
        _avisados.add(nome)
        print(f"[paleta] sem cor fixa: {nome!r} → cinza. Dar uma cor a ele em paleta.py.")
    return fallback
