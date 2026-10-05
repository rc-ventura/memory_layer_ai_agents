"""Instala o kit de mineração num repositório, para o Claude Code ou para o GitHub Copilot.

    python kit-mineracao/instalar.py <raiz-do-repo> --para claude|copilot [--skills-em <dir>]

  skills   -> <raiz>/.claude/skills/<nome>/            (os dois agentes leem dali; --skills-em muda, ex. .github/skills)
  agentes  -> claude:  <raiz>/.claude/agents/<nome>.md
              copilot: <raiz>/.github/agents/<nome>.agent.md
  prompts  -> claude:  <raiz>/.claude/commands/<nome>.md          ({{argumentos}} -> $ARGUMENTS)
              copilot: <raiz>/.github/prompts/<nome>.prompt.md    ({{argumentos}} -> ${input:argumentos})

Grava a versão instalada em <skills>/.kit-mineracao-versao e a lista do que instalou em
<skills>/.kit-mineracao-instalado; uma reinstalação apaga antes o que a anterior instalou (nada mais). Só biblioteca
padrão.
"""

import argparse, os, re, shutil

KIT = os.path.dirname(os.path.abspath(__file__))


def cabecalho_e_corpo(txt):
    m = re.match(r"---\n(.*?)\n---\n(.*)", txt, re.S)
    return (m.group(1), m.group(2)) if m else ("", txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raiz"); ap.add_argument("--para", required=True, choices=["claude", "copilot"])
    ap.add_argument("--skills-em", default=".claude/skills")
    a = ap.parse_args()
    raiz = os.path.abspath(a.raiz)
    dir_skills = os.path.join(raiz, a.skills_em)
    lista = os.path.join(dir_skills, ".kit-mineracao-instalado")

    if os.path.exists(lista):                                     # desfaz a instalação anterior, só o que ela pôs
        for p in open(lista, encoding="utf-8").read().split("\n"):
            alvo = os.path.join(raiz, p) if p else None
            if alvo and os.path.isdir(alvo): shutil.rmtree(alvo)
            elif alvo and os.path.exists(alvo): os.remove(alvo)

    instalados = []
    for nome in sorted(os.listdir(os.path.join(KIT, "skills"))):
        destino = os.path.join(dir_skills, nome)
        shutil.copytree(os.path.join(KIT, "skills", nome), destino,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        instalados.append(destino)

    for arq in sorted(os.listdir(os.path.join(KIT, "agentes"))):
        nome = arq[:-3]
        destino = (os.path.join(raiz, ".claude", "agents", f"{nome}.md") if a.para == "claude"
                   else os.path.join(raiz, ".github", "agents", f"{nome}.agent.md"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copyfile(os.path.join(KIT, "agentes", arq), destino)
        instalados.append(destino)

    for arq in sorted(os.listdir(os.path.join(KIT, "prompts"))):
        nome = arq[:-3]
        cab, corpo = cabecalho_e_corpo(open(os.path.join(KIT, "prompts", arq), encoding="utf-8").read())
        if a.para == "claude":
            destino = os.path.join(raiz, ".claude", "commands", f"{nome}.md")
            corpo = corpo.replace("{{argumentos}}", "$ARGUMENTS")
        else:
            destino = os.path.join(raiz, ".github", "prompts", f"{nome}.prompt.md")
            cab += "\nmode: agent"
            corpo = corpo.replace("{{argumentos}}", "${input:argumentos}")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(f"---\n{cab}\n---\n{corpo}")
        instalados.append(destino)

    versao = open(os.path.join(KIT, "VERSAO"), encoding="utf-8").read().strip()
    with open(os.path.join(dir_skills, ".kit-mineracao-versao"), "w", encoding="utf-8") as fh:
        fh.write(versao + "\n")
    with open(lista, "w", encoding="utf-8") as fh:
        fh.write("\n".join(os.path.relpath(p, raiz).replace(os.sep, "/") for p in instalados) + "\n")
    print(f"kit de mineração {versao} instalado para {a.para} em {raiz}:")
    for p in instalados:
        print("  ", os.path.relpath(p, raiz))


if __name__ == "__main__":
    main()
