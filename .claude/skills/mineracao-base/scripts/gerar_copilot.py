"""Gera as cópias do kit de mineração para o GitHub Copilot, a partir da fonte, que é o próprio `.claude/` do
repositório (versionado). Só o Copilot precisa de cópia: as skills ele lê de `.claude/skills/`.

    python .claude/skills/mineracao-base/scripts/gerar_copilot.py <raiz-do-repo>

  agentes  .claude/agents/<nome>.md     -> .github/agents/<nome>.agent.md
  prompts  .claude/commands/<nome>.md   -> .github/prompts/<nome>.prompt.md   ($ARGUMENTS -> ${input:argumentos};
                                                                               cabeçalho com `mode: agent`)
As cópias são git-ignored: edite sempre a fonte em `.claude/` e gere de novo. Rodar de novo sobrescreve. Só biblioteca
padrão.
"""

import os, re, sys

# as peças do kit (os outros arquivos de .claude/ não são do kit e não vão para o Copilot)
AGENTES = ["auditor-independente", "investigador", "segundo-leitor", "validador-de-notebook"]
PROMPTS = ["rodada-silenciosas", "rodada-protocolo", "rodada-candidata", "investigar", "propor-notebook"]


def cabecalho_e_corpo(txt):
    m = re.match(r"---\n(.*?)\n---\n(.*)", txt, re.S)
    return (m.group(1), m.group(2)) if m else ("", txt)


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    raiz = os.path.abspath(sys.argv[1])
    claude, github = os.path.join(raiz, ".claude"), os.path.join(raiz, ".github")
    versao = open(os.path.join(claude, "skills", "mineracao-base", "VERSAO"), encoding="utf-8").read().strip()
    gerados = []
    for nome in AGENTES:
        txt = open(os.path.join(claude, "agents", f"{nome}.md"), encoding="utf-8").read()
        destino = os.path.join(github, "agents", f"{nome}.agent.md")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        open(destino, "w", encoding="utf-8").write(txt)
        gerados.append(destino)
    for nome in PROMPTS:
        cab, corpo = cabecalho_e_corpo(open(os.path.join(claude, "commands", f"{nome}.md"), encoding="utf-8").read())
        destino = os.path.join(github, "prompts", f"{nome}.prompt.md")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        open(destino, "w", encoding="utf-8").write(
            f"---\n{cab}\nmode: agent\n---\n{corpo.replace('$ARGUMENTS', '${input:argumentos}')}")
        gerados.append(destino)
    print(f"kit de mineração {versao}: cópias do Copilot geradas a partir de .claude/")
    for p in gerados:
        print("  ", os.path.relpath(p, raiz))


if __name__ == "__main__":
    main()
