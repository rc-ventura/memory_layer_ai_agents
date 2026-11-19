"""Base 3: a tabela do resíduo de uma rodada — os padrões de erro que nenhuma regra explica, para o procedimento do
resíduo (base 1, `docs/19-procedimento-residuo.md`; o porquê em `docs/18-racionais-residuo.md`).

    uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/residuo.py --rodada <id|pasta>
        [--fonte <parquet>] [--saida <pasta>]

A rodada (`executar.py analisar`) já classifica cada erro e decide o resíduo na triagem, mas não grava os padrões: a
triagem só diz se algum padrão do balde recorre. Este script recarrega a análise da MESMA rodada (mesma fonte, mesmo
código: o identificador recalculado tem de ser o do manifesto), separa os erros observáveis das unidades `X_*` e grava
em `<saida>` (padrão: `pipeline/resultados/mineracao/residuo/`):

  residuo_padroes.csv   um padrão por linha: unidade, classe (submecanismo), padrão, erros, execuções, meses, papéis,
                        tokens, a lista de meses e de papéis, a chave (identificada × sem impressão digital) e se passa
                        na recorrência — a mesma régua da triagem desta base (`mineracao_observada._decisao`: execução
                        = (exec_id, agente), contada por erro; a chave sem impressão digital nunca passa)
  casos.csv             um erro por linha (exec_id, agente, role, idx = a posição do passo, mes, unidade, classe,
                        família, assinatura, err_type, padrão, tokens) e três colunas de formato da mensagem
                        (tem_due_to, tem_linha_error, linha_rejeitada_ok; Ajuste 1), e a mensagem inteira (para
                        contar uma regra proposta com `testar_regra.py --campo-csv mensagem`: a base 3 não tem o
                        trace inteiro que o `--campo-passo` lê). É a população do
                        `montar_evidencia.py --de mineracao/residuo/casos.csv` e do `drill_down.py caso`
  resumo.json           os totais por balde e por classe, as conferências e os identificadores da rodada e da fonte

Conferências (saída 1 se uma falhar, com o motivo numa linha):
  - o identificador da análise recalculada é o da rodada; a fonte tem o hash do manifesto; o código é o da rodada;
  - erros e execuções de cada balde = os da triagem da rodada (`triagem_visivel_observada.csv`);
  - a decisão de cada balde (prioridade × baixa) = "algum padrão passa" nesta tabela;
  - a soma dos padrões = os erros do resíduo; todo erro do resíduo tem padrão; nenhum pendente entrou.

Fora do hash do código da rodada (`mineracao_observada.versoes_codigo()`): rodar ou mudar este script não troca o
identificador da rodada. Só importa o pipeline; não muda regra nenhuma. Determinístico, sem LLM. Imprime só contagens:
os padrões já vêm mascarados, mas `casos.csv` tem identificador de execução e a mensagem sem máscara, e fica no
ambiente da base (`resultados/` é git-ignored).
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
import base_pipeline as bp  # noqa: E402
import mineracao_observada as mo  # noqa: E402

COLUNAS_CASO = ["exec_id", "agente", "role", "idx", "mes", "unidade", "submecanismo", "familia", "assinatura",
                "err_type", "padrao", "tok_tot", "step_ref"]


class Parada(Exception):
    """Uma conferência falhou: a mineração para e diz o motivo."""


def _sha(path):
    h = hashlib.sha256()
    with open(mo.caminho_io(path), "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def pasta_rodada(arg):
    p = Path(arg)
    if p.is_dir():
        return p.resolve()
    for nome in (arg, "observada_" + arg):
        if (PIPELINE / "resultados" / nome).is_dir():
            return (PIPELINE / "resultados" / nome).resolve()
    raise Parada(f"rodada não encontrada: {arg}")


def formato_da_mensagem(m):
    """As três colunas do Ajuste 1: a mensagem tem o formato que a regra de parsing espera?"""
    m = "" if m is None or (isinstance(m, float) and pd.isna(m)) else str(m)
    return {"tem_due_to": bool(re.search(r"due to: \w+", m)),
            "tem_linha_error": any(l.strip().startswith("Error:") for l in m.splitlines()),
            "linha_rejeitada_ok": bp.linha_rejeitada(m) != ""}


def residuo(EU):
    """Os erros observáveis do resíduo (unidades `X_*`). Pendentes não entram: pendente não é resíduo."""
    obs = EU[EU.situacao_mecanismo.eq("observavel")]
    return obs[obs.unidade.astype(str).str.startswith("X_")].copy()


def tabela_padroes(R, min_execs=bp.MIN_EXECS, min_meses=bp.MIN_MESES):
    """Um padrão por linha, com a régua de recorrência da triagem desta base (`mineracao_observada._decisao`)."""
    linhas = []
    for (u, sub, padrao), g in R.groupby(["unidade", "submecanismo", "padrao"], dropna=False, sort=True):
        execs = len(g[mo.CHAVE_EXEC].drop_duplicates())
        chave = bp.SEM_NOME if pd.isna(padrao) or str(padrao).startswith(bp.SEM_NOME) else "identificada"
        linhas.append({
            "unidade": u, "submecanismo": sub, "padrao": padrao, "erros": len(g), "execucoes": execs,
            "meses": g.mes.nunique(), "papeis": g.role.nunique(),
            "tokens": g.tok_tot.sum(min_count=1), "tokens_ausentes": int(g.tok_tot.isna().sum()),
            "lista_meses": " ".join(sorted(g.mes.dropna().astype(str).unique())),
            "lista_papeis": " ".join(sorted(g.role.dropna().astype(str).unique())),
            "chave": chave,
            "passa_na_recorrencia": bool(chave == "identificada" and execs >= min_execs and g.mes.nunique() >= min_meses),
        })
    t = pd.DataFrame(linhas, columns=["unidade", "submecanismo", "padrao", "erros", "execucoes", "meses", "papeis",
                                      "tokens", "tokens_ausentes", "lista_meses", "lista_papeis", "chave",
                                      "passa_na_recorrencia"])
    return t.sort_values(["passa_na_recorrencia", "execucoes", "erros"], ascending=False).reset_index(drop=True)


def tabela_casos(R):
    c = R.assign(idx=R.step_pos, mensagem=R.err_msg)[COLUNAS_CASO + ["mensagem"]].copy()
    f = pd.DataFrame([formato_da_mensagem(m) for m in R.err_msg], index=R.index)
    return pd.concat([c, f], axis=1).sort_values(["unidade", "padrao", "mes", "exec_id", "idx"]).reset_index(drop=True)


def conferir(R, P, triagem):
    """As conferências internas. Devolve a lista do que foi conferido; levanta Parada no primeiro problema."""
    feito = []
    if R.padrao.isna().any():
        raise Parada(f"{int(R.padrao.isna().sum())} erro(s) do resíduo sem padrão")
    if not R.situacao_mecanismo.eq("observavel").all():
        raise Parada("um erro pendente entrou no resíduo")
    if int(P.erros.sum()) != len(R):
        raise Parada(f"a soma dos padrões ({int(P.erros.sum())}) difere dos erros do resíduo ({len(R)})")
    feito.append("soma dos padrões = erros do resíduo; todo erro tem padrão; nenhum pendente")
    T = triagem[triagem.unidade.astype(str).str.startswith("X_")].set_index("unidade")
    for u in sorted(set(T.index) | set(R.unidade)):
        g = R[R.unidade.eq(u)]
        if u not in T.index:
            raise Parada(f"{u} tem {len(g)} erro(s) aqui e não está na triagem da rodada")
        t = T.loc[u]
        execs = len(g[mo.CHAVE_EXEC].drop_duplicates())
        if (len(g), execs, g.mes.nunique()) != (int(t.erros_observaveis), int(t.execucoes), int(t.meses)):
            raise Parada(f"{u}: erros/execuções/meses {len(g)}/{execs}/{g.mes.nunique()} ≠ triagem "
                         f"{int(t.erros_observaveis)}/{int(t.execucoes)}/{int(t.meses)}")
        passa = bool(P.loc[P.unidade.eq(u), "passa_na_recorrencia"].any())
        esperado = bp.REVISAR_PRIORIDADE if passa else bp.REVISAR_BAIXA
        if t.decisao != esperado:
            raise Parada(f"{u}: a triagem decidiu {t.decisao!r}, a tabela de padrões dá {esperado!r}")
    feito.append("cada balde: erros, execuções, meses e decisão iguais aos da triagem")
    return feito


def resumo(R, P, manifesto, conferencias):
    por = lambda cols: {" · ".join(map(str, k)) if isinstance(k, tuple) else str(k): int(v)
                        for k, v in R.groupby(cols).size().items()}
    return {
        "rodada_id": manifesto["rodada_id"], "fonte_id": manifesto["fonte_id"], "base": manifesto["base"],
        "extracao": manifesto.get("extracao"),
        "erros_residuo": len(R), "tokens_residuo": None if R.tok_tot.notna().sum() == 0 else float(R.tok_tot.sum()),
        "por_balde": por("unidade"), "por_classe": por(["unidade", "submecanismo"]),
        "padroes": len(P), "padroes_que_passam": int(P.passa_na_recorrencia.sum()),
        "padroes_sem_impressao_digital": int(P.chave.eq(bp.SEM_NOME).sum()),
        "padroes_de_uma_execucao": int(P.execucoes.eq(1).sum()),
        "regua": {"min_execucoes": bp.MIN_EXECS, "min_meses": bp.MIN_MESES, "execucao": mo.CHAVE_EXEC,
                  "contagem": "por erro (a triagem da base 3), não por ocorrência"},
        "conferencias": conferencias,
    }


def rodar(rodada, fonte=None, saida=None):
    pasta = pasta_rodada(rodada)
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    if m.get("estado") != "concluida_tecnicamente_sem_aprovacao_semantica":
        raise Parada(f"rodada não concluída (estado {m.get('estado')!r})")
    if m.get("codigo") != mo.versoes_codigo():
        raise Parada("a rodada é de outro código: rode `executar.py analisar` (rodada nova) e minere nela")
    f = Path(fonte) if fonte else Path(bp.EXTRACOES[m.get("extracao") or "v2"])
    if not f.exists():
        raise Parada(f"fonte não encontrada ({f.name}); passe --fonte")
    if _sha(f) != m.get("fonte_sha256"):
        raise Parada("a fonte não é a da rodada (hash diferente do manifesto); passe --fonte com a certa")
    a = mo.analisar(bp.carregar_carga(f, m.get("extracao") or "v2"))
    if a.manifesto["rodada_id"] != m["rodada_id"]:
        raise Parada("a análise recalculada não é a da rodada (identificador diferente)")
    triagem = mo.ler_artefato(pasta, "triagem_visivel_observada.csv", rodada_id=m["rodada_id"], fonte_id=m["fonte_id"])
    R = residuo(a.EU)
    P = tabela_padroes(R)
    conf = ["rodada: identificador, fonte e código conferidos"] + conferir(R, P, triagem)
    out = Path(saida) if saida else PIPELINE / "resultados" / "mineracao" / "residuo"
    mo.caminho_io(out).mkdir(parents=True, exist_ok=True)
    P.to_csv(mo.caminho_io(out / "residuo_padroes.csv"), index=False)
    tabela_casos(R).to_csv(mo.caminho_io(out / "casos.csv"), index=False)
    r = resumo(R, P, m, conf)
    (mo.caminho_io(out) / "resumo.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    return out, r


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", required=True)
    p.add_argument("--fonte")
    p.add_argument("--saida")
    a = p.parse_args(argv)
    try:
        out, r = rodar(a.rodada, a.fonte, a.saida)
    except Parada as exc:
        print(f"PARADA: {exc}")
        return 1
    print(f"rodada {r['rodada_id'][:16]} · resíduo: {r['erros_residuo']} erros · {r['padroes']} padrões "
          f"({r['padroes_que_passam']} passam na recorrência; {r['padroes_sem_impressao_digital']} sem impressão "
          f"digital; {r['padroes_de_uma_execucao']} de uma execução)")
    for k, v in r["por_classe"].items():
        print(f"  {k}: {v}")
    for c in r["conferencias"]:
        print(f"  ok · {c}")
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
