"""Converte um relatório mensal em Markdown (docs/reports/relatorio-mensal-AAAA-MM.md) no texto puro que se cola no
formulário da instituição: o formulário não renderiza Markdown, e negrito e títulos viram texto emendado
("... (Sub 2.2).Consolidou-se ..."). Aqui o título de cada frente fica em linha própria e nada de `**`, crase ou `#` sobra.

    python3 gerar_texto_formulario.py docs/reports/relatorio-mensal-AAAA-MM.md [--saida <arquivo.txt>]

Grava `relatorio-mensal-AAAA-MM-envio.txt` ao lado do .md (ou em --saida) e imprime o caminho e o tamanho de cada campo.
Só biblioteca padrão. Derivado e regenerável: o .md é a fonte.
"""
import argparse
import re
import sys
from pathlib import Path

CAMPOS = [("Número do relatório", "NÚMERO DO RELATÓRIO"), ("Mês de competência", "MÊS DE COMPETÊNCIA"),
          ("Atividades previstas para o mês", "AS ATIVIDADES PREVISTAS PARA ESSE MÊS FORAM")]
SECOES = [("## Desenvolvimento das atividades no período", "DESENVOLVIMENTO DAS ATIVIDADES NO PERÍODO"),
          ("## Observações/comentários", "OBSERVAÇÕES/COMENTÁRIOS")]
TITULO = re.compile(r"^\*\*(.+?)\*\*\s*(.*)$", re.S)


def limpar(t):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)             # [texto](link) → texto
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.S)         # negrito
    t = re.sub(r"(?<!\*)\*(?!\*)([^*\n]+?)\*(?!\*)", r"\1", t)  # itálico
    return t.replace("`", "").strip()


def secao(linhas, cabecalho):
    """Os parágrafos da seção: do cabeçalho até o próximo `## ` ou `---`; sem a dica em itálico."""
    try:
        i = linhas.index(cabecalho)
    except ValueError:
        sys.exit(f"seção não encontrada: {cabecalho!r}")
    corpo = []
    for ln in linhas[i + 1:]:
        if ln.startswith("## ") or ln.strip() == "---":
            break
        corpo.append(ln)
    paragrafos = [p.strip() for p in "\n".join(corpo).split("\n\n") if p.strip()]
    return [p for p in paragrafos if not (p.startswith("*(") and p.endswith(")*"))]


def converter(texto):
    linhas = texto.splitlines()
    out = []
    for rotulo, nome in CAMPOS:
        m = re.search(rf"^- \*\*{re.escape(rotulo)}:\*\*\s*(.+)$", texto, re.M)
        if m:
            out.append(f"{nome}: {limpar(m.group(1))}")
    tamanhos = {}
    for cab, nome in SECOES:
        blocos = []
        for p in secao(linhas, cab):
            p = " ".join(p.split())                              # um parágrafo = uma linha
            m = TITULO.match(p)
            if m and m.group(2):
                blocos += [limpar(m.group(1)), limpar(m.group(2))]
            else:
                blocos.append(limpar(p))
        corpo = "\n\n".join(blocos)
        tamanhos[nome] = len(corpo)
        out += ["", nome, "", corpo]
    return "\n".join(out).strip() + "\n", tamanhos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("relatorio", type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    texto, tamanhos = converter(a.relatorio.read_text(encoding="utf-8"))
    saida = a.saida or a.relatorio.with_name(a.relatorio.stem + "-envio.txt")
    saida.write_text(texto, encoding="utf-8")
    print(f"→ {saida}")
    for nome, n in tamanhos.items():
        print(f"  {nome}: {n:,} caracteres".replace(",", "."))
    sobras = [s for s in ("**", "`", "\n#") if s in texto]
    if sobras:
        print("  aviso: sobrou marcação de Markdown:", sobras)


if __name__ == "__main__":
    main()
