"""Paleta compartilhada das figuras do trace — uma língua de cor para os erros, presa ao NOME.

Módulo só de apresentação (a espinha computacional continua em base_pipeline.py). Toda figura que pinta erros usa a
mesma regra (`COR_ERRO`, via `base_pipeline.categoria_do_erro`): a cor é a da **família** do erro; o **resíduo**
(nenhuma regra reconheceu a causa) é sempre roxo; as famílias de **plataforma** (harness/infra — não é erro do
agente, não vira memória) são cinzas; "outros" agrupados são cinza-claro. O mesmo erro tem a mesma cor no 8.8, no
9.3 e na genealogia, em qualquer base.

    from paleta import *

Nome sem cor fixa cai no cinza e avisa (`cor`): uma família nova aparece como pendência, em vez de herdar em
silêncio a cor de alguém. Método e conferências: 03-procedimento-validacao.md §1.14.
"""

__all__ = ["SURFACE", "INK", "INK2", "MUTED", "GRID", "BASE", "BLUE", "ORANGE", "CINZA", "RESIDUO",
           "COR_ERRO", "NOME_ERRO", "cor"]

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE, BLUE, ORANGE = "#e1e0d9", "#c3c2b7", "#2a78d6", "#eb6834"
CINZA = "#9a988f"      # sem cor fixa
RESIDUO = "#4a3aa7"    # roxo: nenhuma regra reconheceu a causa

COR_ERRO = {
    # famílias de erro do agente
    "Geração de código": BLUE,
    "Contrato de retorno da ferramenta": ORANGE,
    "Convenção de chamada de ferramenta": "#1baf7a",   # verde-água
    "Ambiente & sandbox": "#e87ba4",                   # rosa
    "Suposição sobre estado": "#008300",               # verde
    "Suposição sobre dados": "#e34948",                # vermelho
    # plataforma — não é erro do agente, não vira memória
    "Protocolo do harness": INK2,                      # cinza-escuro
    "Infra / LLM upstream": MUTED,                     # cinza-médio
    # reservadas
    "Resíduo": RESIDUO,
    "Sintoma não reconhecido": RESIDUO,                # família de quem nem o sintoma é reconhecido: é resíduo
    "Outros": BASE,                                    # cinza-claro: o resto, agrupado
}

# nome legível de cada submecanismo (o "erro" que o agente cometeu), para as figuras
NOME_ERRO = {
    "texto_em_literal": "Texto longo dentro de literal",
    "texto_solto_no_codigo": "Explicação solta no código",
    "dict_indexado_por_posicao": "Retorno dict indexado por posição",
    "dict_iterado_como_lista": "Retorno dict iterado como lista",
    "campo_inexistente_no_retorno": "Campo inexistente no retorno",
    "tipo_real_do_retorno": "Retorno veio como string",
    "argumento_posicional": "Argumento posicional (só aceita nomeado)",
    "inventario_sandbox": "Função/import bloqueado (sandbox)",
    "modulo_sem_import": "Módulo usado sem import",
    "next_sobre_gerador": "next() sobre gerador",
    "nome_nunca_definido": "Nome nunca definido",
    "nome_de_step_que_falhou": "Nome de um step que falhou",
    "repr_colado": "Retorno impresso colado no código",
    "harness_bloco_code": "Resposta sem bloco de código",
    "infra_llm": "Falha do LLM upstream",
    "codigo_mal_escrito": "Código Python mal escrito",
    "causa_sem_regra": "Erro conhecido, causa sem regra",
    "sintoma_nao_reconhecido": "Sintoma não reconhecido",
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
