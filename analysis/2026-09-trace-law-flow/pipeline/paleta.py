"""Paleta compartilhada das figuras do trace — cor por NOME, nunca por posição.

Módulo só de apresentação (a espinha computacional continua em base_pipeline.py). Duas regras, uma por tipo de
figura, com a mesma linguagem nas duas:

- `COR_UNIDADE`: a cor de cada unidade de erro, usada no 8.8 (que só descreve que erros cada papel comete). A
  família de cor segue a natureza da unidade: tons frios = unidades factuais (fatos do ambiente), tons quentes =
  unidades de estratégia, cinzas = plataforma (harness/infra), roxos = resíduo (nenhuma regra reconheceu a causa).
- `COR_DECISAO`: a cor da decisão da triagem, usada no 9.3 e na genealogia: azul = memória factual, laranja =
  memória de estratégia, cinza escuro = não-memória, roxo = revisar, cinza claro = fora.

    from paleta import *

A cor é presa ao nome, então a mesma unidade/decisão tem a mesma cor em qualquer base e em qualquer figura. Os tons
das unidades foram escolhidos com o validador da skill de visualização de dados sobre as barras reais do 8.8 (método
e números em 03-procedimento-validacao.md §1.14). Nome sem cor fixa cai no cinza e avisa (`cor`): uma unidade nova
aparece como pendência, em vez de herdar em silêncio a cor de alguém.
"""

__all__ = ["SURFACE", "INK", "INK2", "MUTED", "GRID", "BASE", "BLUE", "ORANGE", "CINZA", "REVISAR",
           "COR_UNIDADE", "COR_DECISAO", "cor", "cor_texto_sobre"]

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE, BLUE, ORANGE = "#e1e0d9", "#c3c2b7", "#2a78d6", "#eb6834"
CINZA = "#9a988f"      # sem cor fixa / agregado
REVISAR = "#4a3aa7"    # resíduo a revisar — a fila de trabalho da taxonomia, não memória

COR_UNIDADE = {
    # unidades factuais (fatos do ambiente) — tons frios
    "U_contrato_dict": "#0f9fb0",       # azul-petróleo
    "U_arg_nomeado": BLUE,              # azul
    "U_sandbox": "#008300",             # verde
    "U_next_gerador": "#1c5cab",        # azul-escuro
    "U_campo_inexistente": "#1baf7a",   # verde-água
    # unidades de estratégia — tons quentes
    "U_texto_literal": ORANGE,          # laranja: a maior unidade leva o mesmo laranja do 9.3
    "U_tipo_retorno": "#c2185b",        # carmim
    "U_texto_solto": "#eda100",         # amarelo
    "U_nome_inventado": "#e87ba4",      # rosa
    "U_estado_perdido": "#9a5b2a",      # marrom
    "U_repr_colado": "#f08a6a",         # coral
    # plataforma (harness/infra) — cinzas
    "H_bloco_code": MUTED,
    "H_infra_llm": INK2,
    # resíduo — roxos
    "X_causa_nao_identificada": REVISAR,
    "X_sintoma_nao_reconhecido": "#9085e9",
}

# as chaves são base_pipeline.CATEGORIAS_DECISAO (categoria_decisao())
COR_DECISAO = {
    "memória · factual": BLUE,
    "memória · estratégia": ORANGE,
    "não-memória": MUTED,
    "revisar": REVISAR,
    "fora": BASE,
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


def _luminancia(hexcor):
    lin = [(c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
           for c in (int(hexcor.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def cor_texto_sobre(fundo):
    """Branco ou tinta, o que der mais contraste (WCAG) sobre `fundo` — para rótulo dentro de uma fatia."""
    lf = _luminancia(fundo)
    contraste = lambda lt: (max(lf, lt) + 0.05) / (min(lf, lt) + 0.05)
    return "#ffffff" if contraste(1.0) >= contraste(_luminancia(INK)) else INK
