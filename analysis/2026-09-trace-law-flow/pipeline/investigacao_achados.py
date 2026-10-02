# -*- coding: utf-8 -*-
"""Investigação dos achados abertos da base 2 (revisão de 02/10/2026; plano-atual §1 e itens do §4).

Roda em qualquer base (de dentro de `pipeline/`, depois do notebook da esteira, que grava `resultados/erros_mecanismo.csv`
e `resultados/criticos.csv`). Seis perguntas, uma seção cada:

  A. Colar o print do retorno (`U_repr_colado`) no balde VISÍVEL: em que ferramenta o literal colado está? É a mesma do
     canal silencioso (`busca_obf`)? → se for, a mesma lição nos dois canais.
  B. "Nome usado sem ter sido definido" (`U_nome_inventado`): o nome nunca existiu, foi definido antes (e se perdeu),
     foi definido numa CHAMADA ANTERIOR do papel, é nome de ferramenta, vem depois de um erro de protocolo? Por papel,
     mês e modelo. → o que é a maior candidata da base 2.
  C. "Campo inexistente no retorno" (`U_campo_inexistente`): qual chave foi pedida, quais chaves o retorno tinha, de
     que ferramenta, e se a chave pedida aparece no system prompt (o prompt induz o nome errado — a essência da base 1).
  D. O erro crítico, chamada por chamada: erros, falhas silenciosas (e se o motivo é `'DEFAULT'`), se o pensamento logo
     depois menciona a falha, se a ferramenta é chamada de novo, se a chamada termina com `final_answer`.
  E. O desfecho dos candidatos a sucesso falso, pelo estado final das variáveis (`txt_vrvl_locl`): a variável que
     recebeu o erro ainda o guarda no fim? Ela é usada no `final_answer`? A resposta declara a falha?
  F. As versões da declaração do `busca_obf` (hash, sem o texto) × as falhas silenciosas por mês.

SAÍDA: só contagens, nomes de papel/ferramenta/modelo/unidade, hashes, sim/não e — na seção C — nomes de CAMPO do
contrato (chaves, nunca valores). Nenhum exec_id, nenhuma mensagem de erro, nenhum texto de caso, nenhum código.
Pode ser fotografada na máquina 2.

    python investigacao_achados.py            # todas as seções
    python investigacao_achados.py B D        # só algumas
"""
import json, os, re, sys, hashlib
from collections import Counter, defaultdict
import pandas as pd

import drill_down as dd                      # stdout em UTF-8 e os helpers de prompt/modelo
from base_pipeline import (carregar_trace, falhas_silenciosas, sucesso_falso_candidato, GRUPOS_FALHA_REAL,
                           MOTIVO_REGRAS, MODULOS, linha_rejeitada, linha_do_codigo)

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
SECOES = [a.upper() for a in sys.argv[1:]] or list("ABCDEF")
DECLARA_FALHA = re.compile(r"n[ãa]o (foi|é) poss[ií]vel|n[ãa]o consegu|indispon[ií]vel|falh|erro\b|error|unable|"
                           r"failed|could not|n[ãa]o (h[áa]|existe)m? (dados|resultado)", re.I)


def titulo(t):
    print(f"\n{'=' * 100}\n{t}\n{'=' * 100}")


def tabela(cont, cab, n=15):
    print(f"  {cab}")
    for k, v in cont.most_common(n):
        print(f"  {v:>5}  " + " · ".join(str(x) for x in (k if isinstance(k, tuple) else (k,))))
    if len(cont) > n:
        print(f"  … e mais {len(cont) - n} combinações ({sum(v for _, v in cont.most_common()[n:])} casos)")


# ------------------------------------------------------------------ dados comuns
df = carregar_trace().drop_duplicates("cod_idef_exeo").set_index("cod_idef_exeo")
EM = pd.read_csv(os.path.join(RES, "erros_mecanismo.csv"), dtype={"exec_id": str})
EM["idx"] = EM["idx"].astype(int)
UNID = {(r.exec_id, r.role, r.idx): r.unidade for r in EM.itertuples()}


def lista_do_papel(eid, role):
    """(ActionSteps do papel, chamada de cada um): a chamada = quantos TaskStep vêm antes do step."""
    acts, cham, n = [], [], 0
    for s in json.loads(df.loc[eid, "txt_etap_memo"]).get(role) or []:
        if not isinstance(s, dict): continue
        if s.get("__class__") == "TaskStep": n += 1
        elif s.get("__class__") == "ActionStep": acts.append(s); cham.append(n)
    return acts, cham


def declaradas(st):
    return set(re.findall(r"def\s+(\w+)\s*\(", dd.system_prompt(st))) - {"final_answer"}


def chamadas_no(code, decl):
    return sorted(t for t in decl if re.search(rf"\b{t}\s*\(", code or ""))


def msg(st):
    return str((st.get("error") or {}).get("message") or "")


def estado_final(eid, role):
    try:
        return (json.loads(df.loc[eid, "txt_vrvl_locl"]) or {}).get(role) or {}
    except Exception:
        return None


print(f"Investigação dos achados abertos — {len(df)} execuções distintas, {len(EM)} erros no balde visível")

# ------------------------------------------------------------------ A. colar o print — o canal visível
if "A" in SECOES:
    titulo("A · Colar o print do retorno (U_repr_colado), canal VISÍVEL: em que ferramenta está o literal colado?")
    x = EM[EM["unidade"] == "U_repr_colado"]
    na_linha, no_bloco, papel_mes = Counter(), Counter(), Counter()
    for r in x.itertuples():
        acts, _ = lista_do_papel(r.exec_id, r.role); st = acts[r.idx]; code = str(st.get("code_action") or "")
        decl = declaradas(st)
        linha = linha_rejeitada(msg(st), linha_do_codigo(msg(st), code))   # a linha que o parser recusou
        na_linha[tuple(chamadas_no(linha, decl)) or ("(nenhuma ferramenta na linha rejeitada)",)] += 1
        no_bloco[tuple(chamadas_no(code, decl)) or ("(nenhuma)",)] += 1
        papel_mes[(r.role, r.mes)] += 1
    print(f"  {len(x)} erros · {x['exec_id'].nunique()} execuções")
    tabela(na_linha, "erros · ferramenta chamada NA LINHA que o parser rejeitou")
    tabela(no_bloco, "erros · ferramentas chamadas no bloco inteiro do step")
    tabela(papel_mes, "erros · papel · mês")
    print("  Leitura: se a linha rejeitada chama `busca_obf`, é o mesmo gesto do canal silencioso, na mesma ferramenta.")

# ------------------------------------------------------------------ B. nome usado sem ter sido definido
if "B" in SECOES:
    titulo("B · Nome usado sem ter sido definido (U_nome_inventado): o que é?")
    x = EM[EM["unidade"] == "U_nome_inventado"]
    tipo, forma, por_papel, por_modelo, apos_prot, pos_chamada = (Counter() for _ in range(6))
    for r in x.itertuples():
        acts, cham = lista_do_papel(r.exec_id, r.role); st = acts[r.idx]; m = msg(st)
        nm = (re.search(r"variable `(\w+)`", m) or re.search(r"'(\w+)' is not among", m)
              or re.search(r"Forbidden function evaluation: '(\w+)'", m) or re.search(r"name '(\w+)' is not defined", m))
        forma[("variável não definida" if "is not defined" in m else
               "fora das ferramentas permitidas" if "is not among" in m else
               "função proibida" if "Forbidden function" in m else "outra")] += 1
        nome = nm.group(1) if nm else None
        antes = [(i, str(a.get("code_action") or "")) for i, a in enumerate(acts[:r.idx])]
        def_re = (rf"(^|\n)\s*(def\s+{nome}\s*\(|{nome}\s*(,\s*\w+\s*)*=(?!=)|for\s+{nome}\s+in|"
                  rf"import\s+.*\b{nome}\b|as\s+{nome}\b)") if nome else None
        def_antes = [i for i, c in antes if def_re and re.search(def_re, c)]
        def_depois = nome and any(re.search(def_re, str(a.get("code_action") or "")) for a in acts[r.idx + 1:])
        if not nome: t = "nome não extraído da mensagem"
        elif nome in declaradas(st): t = "é ferramenta declarada no prompt"
        elif nome in MODULOS: t = "é módulo (import faltando)"
        elif def_antes and any(cham[i] != cham[r.idx] for i in def_antes) and not any(cham[i] == cham[r.idx] for i in def_antes):
            t = "definido numa CHAMADA ANTERIOR do papel"
        elif def_antes:
            t = "definido antes, na mesma chamada (perdeu-se)"
        elif def_depois: t = "definido só depois"
        else: t = "nunca definido no papel"
        tipo[t] += 1
        por_papel[(r.role, r.mes)] += 1
        por_modelo[(r.role, dd._modelo_do_step(st))] += 1
        prot = any(UNID.get((r.exec_id, r.role, j)) == "H_bloco_code" for j in range(max(0, r.idx - 3), r.idx))
        apos_prot["sim" if prot else "não"] += 1
        pos_chamada["1º step da chamada" if r.idx == 0 or cham[r.idx - 1] != cham[r.idx] else "depois do 1º step"] += 1
    print(f"  {len(x)} erros · {x['exec_id'].nunique()} execuções · {x['mes'].nunique()} meses · {x['role'].nunique()} papéis")
    tabela(tipo, "erros · o nome…")
    tabela(forma, "erros · forma da mensagem")
    tabela(pos_chamada, "erros · posição na chamada do papel")
    tabela(apos_prot, "erros · houve 'resposta sem bloco de código' nos 3 steps anteriores?")
    tabela(por_modelo, "erros · papel · modelo que respondeu")
    tabela(por_papel, "erros · papel · mês")

# ------------------------------------------------------------------ C. campo inexistente no retorno
if "C" in SECOES:
    titulo("C · Campo inexistente no retorno (U_campo_inexistente): chave pedida × chaves do retorno × ferramenta")
    x = EM[EM["unidade"] == "U_campo_inexistente"]
    combo, no_prompt, ferr = Counter(), Counter(), Counter()
    for r in x.itertuples():
        acts, _ = lista_do_papel(r.exec_id, r.role); st = acts[r.idx]; m = msg(st); code = str(st.get("code_action") or "")
        k = (re.search(r"with '([A-Za-z_]\w{0,59})'\s*$", m.strip()) or re.search(r"KeyError: '([A-Za-z_]\w{0,59})'", m)
             or re.search(r"with '([A-Za-z_]\w{0,59})'", m))
        pedida = k.group(1) if k else "(não extraída)"
        # as chaves que o retorno TINHA: só do dict que a mensagem diz não conseguir indexar (nunca do código citado)
        dic = re.search(r"Could not index (\{.*?\}) with '", m, re.S)
        presentes = sorted(set(re.findall(r"'([A-Za-z_]\w{0,40})'\s*:", dic.group(1))))[:6] if dic else []
        sysp = dd.system_prompt(st)
        no_prompt["a chave pedida aparece no system prompt" if pedida in sysp else "não aparece no prompt"] += 1
        var = re.search(rf"(\w+)\s*(\[\s*['\"]{re.escape(pedida)}['\"]|\.get\(\s*['\"]{re.escape(pedida)}['\"])", code)
        origem = "(variável não achada)"
        if var:
            for a in acts[:r.idx + 1][::-1]:
                o = re.search(rf"\b{var.group(1)}\s*=\s*(\w+)\s*\(", str(a.get("code_action") or ""))
                if o: origem = o.group(1); break
        if not presentes and var:                      # sem dict na mensagem: o estado final da variável indexada
            est = estado_final(r.exec_id, r.role) or {}
            val = est.get(var.group(1))
            if isinstance(val, str):
                try: val = json.loads(val)
                except Exception: pass
            presentes = sorted(val)[:6] if isinstance(val, dict) else []
        combo[(r.role, pedida, "chaves do retorno: " + (", ".join(presentes) or "—"))] += 1
        ferr[(r.role, origem)] += 1
    print(f"  {len(x)} erros · {x['exec_id'].nunique()} execuções · papéis: {', '.join(sorted(x['role'].unique()))}")
    tabela(combo, "erros · papel · chave pedida · chaves que o retorno tinha (só nomes de campo)")
    tabela(ferr, "erros · papel · ferramenta que devolveu o retorno indexado")
    tabela(no_prompt, "erros · o prompt menciona a chave pedida? (base 1: o prompt induzia o nome errado)")

# ------------------------------------------------------------------ D. o erro crítico, chamada por chamada
if "D" in SECOES:
    titulo("D · Erro crítico, chamada por chamada (o 'DEFAULT' desencadeia a cascata?)")
    arq = os.environ.get("INV_CRITICOS") or os.path.join(RES, "criticos.csv")   # INV_CRITICOS: só para teste
    K = pd.read_csv(arq, dtype={"exec_id": str}) if os.path.exists(arq) else pd.DataFrame()
    if K.empty:
        print("  nenhum erro crítico nesta base.")
    F = falhas_silenciosas(df.reset_index().rename(columns={"index": "cod_idef_exeo"})) if not K.empty else None
    default_re = next(p for g, p, _ in MOTIVO_REGRAS if "default" in p)
    for kk, k in enumerate(K.itertuples(), 1):
        acts, cham = lista_do_papel(k.exec_id, k.role)
        Fk = F[(F["exec_id"] == k.exec_id) & (F["role"] == k.role)]
        print(f"\n  crítico {kk}: {k.role} · {k.mes} · {len(acts)} steps · {max(cham) if cham else 0} chamadas do papel")
        print("  chamada · steps · erros visíveis (unidades) · falhas silenciosas (ferramenta: grupo, 'DEFAULT'?) · "
              "depois da falha: pensamento menciona a falha? · chamou a ferramenta de novo? · terminou com final_answer?")
        for c in sorted(set(cham)):
            ix = [i for i, cc in enumerate(cham) if cc == c]
            us = Counter(UNID[(k.exec_id, k.role, i)] for i in ix if (k.exec_id, k.role, i) in UNID)
            sil = Fk[(Fk["idx"].isin(ix)) & (Fk["falha"] == "silenciosa")]
            desc, menc, rech = [], Counter(), Counter()
            for s in sil.itertuples():
                eh_def = bool(re.search(default_re, str(s.motivo).strip().lower()))
                desc.append(f"{s.ferramenta}: {s.grupo}{', DEFAULT' if eh_def else ''}")
                prox = acts[s.idx + 1] if s.idx + 1 < len(acts) and cham[s.idx + 1] == c else None
                if prox is not None:
                    menc["sim" if re.search(r"default|erro|error|falh|fail", str(prox.get("model_output") or ""), re.I) else "não"] += 1
                    rech["sim" if re.search(rf"\b{s.ferramenta}\s*\(", str(prox.get("code_action") or "")) else "não"] += 1
            fim = any(acts[i].get("is_final_answer") for i in ix)
            print(f"  {c:>7} · {len(ix):>5} · {sum(us.values()):>2} ({', '.join(f'{u} {n}' for u, n in us.most_common()) or '—'}) · "
                  f"{len(sil)} ({'; '.join(desc) or '—'}) · {dict(menc) or '—'} · {dict(rech) or '—'} · {'sim' if fim else 'NÃO'}")

# ------------------------------------------------------------------ E. desfecho dos candidatos a sucesso falso
if "E" in SECOES:
    titulo("E · Desfecho dos candidatos a sucesso falso, pelo estado final das variáveis (txt_vrvl_locl)")
    F = falhas_silenciosas(df.reset_index().rename(columns={"index": "cod_idef_exeo"}))
    sil = F[F["falha"] == "silenciosa"]
    cand = sil[sil["grupo"].isin(GRUPOS_FALHA_REAL)][sucesso_falso_candidato(F, sil)]
    des, det, cruz, linhas = Counter(), Counter(), Counter(), []
    for s in cand.itertuples():
        acts, _ = lista_do_papel(s.exec_id, s.role)
        code = str(acts[s.idx].get("code_action") or "")
        v = re.search(rf"(\w+)\s*=\s*{s.ferramenta}\s*\(", code)
        fin = acts[int(s.idx_final_depois)]
        fin_code = str(fin.get("code_action") or ""); fin_out = str(fin.get("action_output") or "")
        declara = bool(DECLARA_FALHA.search(fin_out))
        est = estado_final(s.exec_id, s.role)
        if not v:
            usa, guarda = None, None
        else:
            var = v.group(1)
            derivadas = {var} | {d for a in acts[s.idx:int(s.idx_final_depois) + 1]
                                 for d in re.findall(rf"(\w+)\s*=(?!=)[^\n]*\b{var}\b", str(a.get("code_action") or ""))}
            fa = re.search(r"final_answer\s*\((.*)", fin_code, re.S)
            usa = bool(fa and any(re.search(rf"\b{d}\b", fa.group(1)) for d in derivadas))
            guarda = None if est is None else ("Error calling tool" in str(est.get(var, "")))
        if "Error calling tool" in fin_out: d = "a resposta repassa o texto do erro da ferramenta"
        elif usa and guarda: d = "sucesso falso provável (a resposta usa a variável que guarda o erro) — ler"
        elif declara: d = "falha declarada"
        elif usa: d = "usa a variável, mas ela não guarda o erro no fim (sobrescrita?) — ler"
        elif usa is False: d = "não dependia (a resposta não usa a variável)"
        else: d = "indeterminado (o retorno não foi atribuído a uma variável) — ler"
        des[(s.grupo, d)] += 1
        linhas.append({"exec_id": s.exec_id, "role": s.role, "idx": s.idx, "chamada": s.chamada, "ferramenta": s.ferramenta,
                       "grupo": s.grupo, "idx_final": int(s.idx_final_depois), "declara": declara, "usa": usa,
                       "guarda": guarda, "desfecho": d})
        cruz[("declara" if declara else "não declara", "usa a variável" if usa else "não usa" if usa is False else "sem variável",
              "guarda o erro" if guarda else "não guarda" if guarda is False else "sem estado")] += 1
        det[("estado final presente" if est is not None else "sem txt_vrvl_locl",
             "mesmo step da falha" if int(s.idx_final_depois) == s.idx else "final depois")] += 1
    print(f"  {len(cand)} candidatos (de {int(sil['grupo'].isin(GRUPOS_FALHA_REAL).sum())} falhas reais)")
    tabela(des, "candidatos · grupo do motivo · desfecho", n=30)
    tabela(det, "candidatos · estado final disponível? · onde está o final_answer")
    tabela(cruz, "candidatos · a resposta declara a falha? · usa a variável do retorno? · ela guarda o erro no fim?", n=20)
    pasta = os.path.join(RES, "evidencia", "silenciosas"); os.makedirs(pasta, exist_ok=True)
    pd.DataFrame(linhas).to_csv(os.path.join(pasta, "desfechos.csv"), index=False)
    print(f"  Por caso, com exec_id: {os.path.relpath(os.path.join(pasta, 'desfechos.csv'))} — não sai da máquina.")
    print("  Regra (determinística, sem LLM): 'declara' = o texto entregue tem palavras de falha (não foi possível, não "
          "consegui, indisponível, erro, falha…); 'usa' = a variável que recebeu o retorno, ou uma derivada dela, aparece "
          "no final_answer; 'guarda' = no estado final ela ainda contém 'Error calling tool'.")

# ------------------------------------------------------------------ F. declaração do busca_obf × falhas
if "F" in SECOES:
    titulo("F · Versões da declaração do busca_obf (hash do bloco, sem o texto) × falhas silenciosas por mês")
    F = falhas_silenciosas(df.reset_index().rename(columns={"index": "cod_idef_exeo"}))
    B = F[F["ferramenta"] == "busca_obf"]
    if B.empty:
        print("  nenhuma chamada do busca_obf nesta base.")
    else:
        ver = {}
        for eid, role in set(zip(B["exec_id"], B["role"])):
            acts, _ = lista_do_papel(eid, role)
            for i, a in enumerate(acts):
                bl = dd.bloco_da_ferramenta(dd.system_prompt(a), "busca_obf")
                ver[(eid, role, i)] = hashlib.sha1(bl.encode()).hexdigest()[:8] if bl else "(sem declaração)"
        B = B.assign(versao=[ver.get((e, r, i), "?") for e, r, i in zip(B["exec_id"], B["role"], B["idx"])])
        print("  mês · versão da declaração · steps com busca_obf · falhas silenciosas · % · das quais JSON inválido")
        for (mes, v), g in B.groupby(["mes", "versao"]):
            s = g[g["falha"] == "silenciosa"]
            print(f"  {mes} · {v} · {len(g):>4} · {len(s):>3} · {len(s) / len(g):>4.0%} · {int((s['grupo'] == 'json_invalido').sum())}")
        print("  Leitura: se a taxa de JSON inválido muda junto com a versão, é um experimento natural sobre a declaração.")

print(f"\n{'=' * 100}\nFim. Saída só com contagens e nomes — pode ser fotografada.")
