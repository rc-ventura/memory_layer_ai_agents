# -*- coding: utf-8 -*-
"""
Metadados dos steps em volta de cada erro "resposta sem bloco de código" (Etapa 10b) — só números e sim/não.

    python metadados_steps.py <papel> [<quantos steps>]

Lê os casos que `python drill_down.py protocolo --casos <papel> ...` gravou em
resultados/evidencia/protocolo/erro_<papel>_*.txt (o exec_id sai da linha 1 de cada arquivo) e, para cada caso,
imprime os primeiros steps do papel naquela execução:

    step · tamanho do texto do modelo · tamanho do código · erro? (P = erro de parse do <code>) ·
    finish_reason da API · tokens de entrada/saída/raciocínio · filtro de conteúdo acionado?

Mostra os primeiros <quantos> steps (padrão 4) e, sempre, até o step seguinte ao último erro de parse.
E, sobre a tarefa que o papel recebeu (a mensagem "New task:"), só sim/não: menciona "não foi possível"?
traz o molde `fluxo_encerramento`? Mais: se o papel foi chamado mais de uma vez na execução (step 1 repetido).

Serve para a pergunta do grupo B do RoteadorCivel (base 2): o step 1 veio vazio por quê — orçamento de tokens
gasto em raciocínio (finish=length, reasoning alto), filtro de conteúdo, ou o modelo parou sem gerar nada?

A saída não tem texto de caso nem exec_id (o caso é o número do arquivo): pode ser fotografada na máquina 2.
Os arquivos erro_*.txt continuam com o caso em claro — não copiar para fora.
"""
import glob, json, os, re, sys

import drill_down as d

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados", "evidencia", "protocolo")
FALHA = re.compile(r"n[ãa]o foi poss[íi]vel|could not|unable to", re.I)   # estreito: "erro" casa com os documentos


def _tokens(s):
    """(entrada, saída, raciocínio) — do token_usage do smolagents e, se houver, do usage cru da API."""
    tu = s.get("token_usage") or {}
    raw = (s.get("model_output_message") or {}).get("raw") or {}
    us = raw.get("usage") or {}
    det = us.get("completion_tokens_details") or us.get("output_tokens_details") or {}
    ent = tu.get("input_tokens", us.get("prompt_tokens"))
    sai = tu.get("output_tokens", us.get("completion_tokens"))
    return ent, sai, det.get("reasoning_tokens")


def _finish_e_filtro(s):
    raw = (s.get("model_output_message") or {}).get("raw") or {}
    ch = (raw.get("choices") or [{}])[0] or {}
    cfr = ch.get("content_filter_results") or {}
    filtro = any(isinstance(v, dict) and v.get("filtered") for v in cfr.values())
    return ch.get("finish_reason"), filtro


def _tarefa(s):
    """Texto da mensagem 'New task:' do step (a tarefa que o papel recebeu), ou ''."""
    for m in s.get("model_input_messages") or []:
        if m.get("role") != "user":
            continue
        c = m.get("content")
        txt = " ".join(p.get("text", "") for p in c if isinstance(p, dict)) if isinstance(c, list) else str(c or "")
        if "New task" in txt:
            return txt
    return ""


def main(papel, quantos=4):
    arqs = sorted(glob.glob(os.path.join(PASTA, f"erro_{papel}_*.txt")))
    if not arqs:
        print(f"nenhum erro_{papel}_*.txt em {os.path.relpath(PASTA)} — rode antes: "
              f"python drill_down.py protocolo --casos {papel} 7")
        return
    df = d.load()
    for a in arqs:
        cab = open(a, encoding="utf-8").readline()
        m = re.search(r"exec_id (\S+)", cab)
        caso = os.path.basename(a)[len("erro_"):-len(".txt")]
        idx = re.search(r"idx (\d+)", cab)
        print(f"\n=== {caso}  (idx do erro no arquivo: {idx.group(1) if idx else '?'})")
        if not m:
            print("  sem exec_id na linha 1"); continue
        row = df[df["cod_idef_exeo"] == m.group(1)]
        if row.empty:
            print("  exec_id não encontrado no trace"); continue
        steps = [s for s in json.loads(row.iloc[0]["txt_etap_memo"]).get(papel, [])
                 if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
        nums = [s.get("step_number") for s in steps]
        print(f"  steps do papel: {len(steps)} · papel chamado {max(1, nums.count(1))}x na execução "
              f"(step 1 aparece {nums.count(1)}x)")
        parse = [i for i, s in enumerate(steps) if "regex pattern" in str((s.get("error") or {}).get("message", ""))]
        # a tarefa da chamada em que caiu o 1º erro de parse (o step 1 mais recente antes dele)
        ini = max([i for i, n in enumerate(nums) if n == 1 and (not parse or i <= parse[0])] or [0])
        t = _tarefa(steps[ini]) if steps else ""
        print(f"  tarefa (da chamada {nums[:ini + 1].count(1) or 1} do papel, a do 1º erro de parse): "
              f"{'encontrada' if t else 'não encontrada'} · menciona 'não foi possível'/'could not': "
              f"{'sim' if FALHA.search(t) else 'não'} · traz 'fluxo_encerramento': "
              f"{'sim' if 'fluxo_encerramento' in t else 'não'} · {len(t)} caracteres")
        print(f"  {'step':>4} {'len_texto':>9} {'len_código':>10} {'erro':>4} {'finish':>14} "
              f"{'tok_entrada':>11} {'tok_saída':>9} {'tok_raciocínio':>14} {'filtro':>6}")
        for s in steps[:max([quantos] + [i + 2 for i in parse])]:   # sempre até o step seguinte ao último P
            e = s.get("error") or {}
            erro = "P" if "regex pattern" in str(e.get("message", "")) else ("sim" if e else "não")
            fin, filtro = _finish_e_filtro(s)
            ent, sai, rac = _tokens(s)
            print(f"  {s.get('step_number')!s:>4} {len(str(s.get('model_output') or '')):>9} "
                  f"{len(str(s.get('code_action') or '')):>10} {erro:>4} {fin!s:>14} {ent!s:>11} {sai!s:>9} "
                  f"{rac!s:>14} {'sim' if filtro else 'não':>6}")
    print("\nerro: P = erro de parse do <code> (resposta sem bloco de código). Sem texto de caso nem exec_id nesta saída.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4)
