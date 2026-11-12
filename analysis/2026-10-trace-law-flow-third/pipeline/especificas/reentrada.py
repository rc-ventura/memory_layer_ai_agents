"""Re-entrada: uma unidade já minerada mudou depois da mineração? Os erros novos estão cobertos pelas memórias?

Quando um Ajuste (ou uma fonte nova) muda a população de uma unidade que já foi minerada, a triagem e os gráficos
contam os erros novos na unidade, mas nenhuma memória do catálogo os cobre até alguém conferir. Este script confere,
por regra e sem LLM, e é idempotente: a mesma rodada com a mesma foto e o mesmo catálogo dá sempre os mesmos arquivos.
O procedimento (quando rodar e o que fazer com cada estado) está no procedimento de mineração de candidatas da base 1
(doc `16`, "Re-entrada") e no procedimento 06 desta análise.

    uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/reentrada.py <unidade> [<unidade>…]
        --rodada <id|pasta> [--fonte <parquet>] [--mineracao <pasta da mineração>] [--catalogo <memorias.json>]
        [--saida <pasta>]
    … reentrada.py --todas --rodada <id|pasta>      (toda unidade desta base que tem memória no catálogo)

Para cada unidade:
  1. **a foto:** a população no momento da mineração — o `erros_lidos.csv` da pasta da mineração
     (`resultados/mineracao/<unidade>/`, gravado pelo passo 4 do `minerar.py`: um erro por linha, com `step_ref` e
     `memoria_id`) e a rodada em que ela foi minerada (`passo1_rodada.json`);
  2. **agora:** a população da unidade na rodada pedida (conferida como no `residuo.py`: identificador, fonte e
     código), lida pela **mesma** parte específica da mineração (o `medir` do `mineracao_<unidade>.py` que o funil
     aponta), que diz o `memoria_id` de cada erro hoje;
  3. **o delta, pelo `step_ref`** (o hash do passo, que não muda entre rodadas da mesma fonte): os erros que
     **entraram**, os que **saíram** e os que ficaram mas **mudaram de parte**;
  4. **a cobertura de cada erro que entrou (ou mudou):**
       memoria_no_catalogo         a parte dele tem memória fechada no catálogo (`analysis/registros/memorias.json`)
       parte_decidida_sem_memoria  a parte já existia na foto, com destino que não é memória (harness, régua de
                                   memória rara…): já decidida
       parte_nova                  a regra dá uma parte que a foto não tinha (ex.: um papel novo numa parte por papel)
       sem_parte                   a regra não lê o erro (`memoria_id` vazio): nenhuma parte da lição o cobre
  5. **por memória:** erros na foto e agora; `revisar` quando uma memória do catálogo que está na foto varia mais que
     LIMIAR_REVISAR. Dois avisos de que a foto não é a mineração que fechou o catálogo (ex.: a unidade foi minerada de
     novo e a pasta sobrescrita): a rodada da foto não é nenhuma das do catálogo, ou uma memória do catálogo não tem
     erro na foto (`catalogo_fora_da_foto`);
  6. **o estado:** `igual` (nada entrou, saiu ou mudou), `cresceu_coberto`, `descoberto` (há `sem_parte` ou
     `parte_nova`), `encolheu`, `mudou_de_parte`, `revisar` — pode haver mais de um.

Grava em `resultados/mineracao/reentrada/<unidade>/` (sobrescreve; sem data dentro, para ser idempotente):
  delta.csv          um erro por linha que entrou, saiu ou mudou de parte (situação, memoria_id antes e agora, a
                     cobertura), com a chave para o `montar_evidencia.py`; fica no ambiente da base
  descobertos.csv    só os `sem_parte` e `parte_nova`: a população da investigação (`montar_evidencia.py --de`)
  por_memoria.csv    por memória: erros na foto, agora, a variação, se está no catálogo, `revisar`
  resumo.json        as contagens, o estado, as rodadas e o hash do catálogo

Saída: 0 se toda unidade está `igual` ou `cresceu_coberto`; 1 se alguma pede re-entrada (descoberto, encolheu, mudou de
parte, revisar); 2 se alguma não pôde ser conferida (sem foto, sem script, rodada ou fonte errada). Imprime só
contagens, ids de memória, papéis e meses. Fica fora do hash da rodada (como o `minerar.py` e o `residuo.py`).

Limites: só lê unidades mineradas por script (a foto é o `erros_lidos.csv` do passo 4); uma unidade minerada por
investigação para com saída 2. O `step_ref` muda se a fonte for outra extração: o resumo traz o `fonte_id` da foto e o
de agora, e o script avisa quando diferem (aí o delta compara populações de fontes diferentes).
"""
import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
RAIZ = PIPELINE.parents[2]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import base_pipeline as bp  # noqa: E402
import mineracao_observada as mo  # noqa: E402
import minerar as mn  # noqa: E402

CATALOGO = RAIZ / "analysis" / "registros" / "memorias.json"
# A régua de "revisar": uma memória do catálogo cuja população variou mais que isto desde a mineração volta ao degrau 3
# (revisada). Proposta de 12/11, a confirmar pelo Rafael (decisoes.md, 12/11, re-entrada).
LIMIAR_REVISAR = 0.20
COBERTURAS = ["memoria_no_catalogo", "parte_decidida_sem_memoria", "parte_nova", "sem_parte"]
DESCOBERTAS = ("parte_nova", "sem_parte")
CHAVE = ["step_ref", "exec_id", "agente", "role", "step_pos", "mes"]
Parada = mn.Parada


def _sha(path):
    h = hashlib.sha256()
    with open(mo.caminho_io(path), "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _vazio(v):
    return v is None or (isinstance(v, float) and v != v) or (isinstance(v, str) and not v.strip())


def carregar_rodada(rodada, fonte=None):
    """(pasta, manifesto, análise) da rodada, com as conferências do `residuo.py`: concluída, do código atual, a fonte
    é a do manifesto e a análise recalculada tem o mesmo identificador."""
    pasta = mn.pasta_rodada(rodada)
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    if m.get("estado") != "concluida_tecnicamente_sem_aprovacao_semantica":
        raise Parada(f"rodada não concluída (estado {m.get('estado')!r})")
    if m.get("codigo") != mo.versoes_codigo():
        raise Parada("a rodada é de outro código: rode `executar.py analisar` (rodada nova) e confira nela")
    f = Path(fonte) if fonte else Path(bp.EXTRACOES[m.get("extracao") or "v2"])
    if not f.exists():
        raise Parada(f"fonte não encontrada ({f.name}); passe --fonte")
    if _sha(f) != m.get("fonte_sha256"):
        raise Parada("a fonte não é a da rodada (hash diferente do manifesto); passe --fonte com a certa")
    a = mo.analisar(bp.carregar_carga(f, m.get("extracao") or "v2"))
    if a.manifesto["rodada_id"] != m["rodada_id"]:
        raise Parada("a análise recalculada não é a da rodada (identificador diferente)")
    return pasta, m, a


def ler_foto(pasta):
    """(erros_lidos da mineração, ids da rodada da mineração). Para se a pasta não tem a foto."""
    pasta = Path(pasta)
    arq, rod = pasta / "erros_lidos.csv", pasta / "passo1_rodada.json"
    if not arq.exists() or not rod.exists():
        raise Parada(f"sem foto da mineração em {pasta.name}/ (faltam erros_lidos.csv ou passo1_rodada.json): a "
                     "unidade foi minerada por script nesta base? (`minerar.py <unidade> --rodada …`, passos 1 e 4)")
    F = pd.read_csv(mo.caminho_io(arq), dtype={"exec_id": str, "agente": str, "step_ref": str, "memoria_id": str})
    if "memoria_id" not in F.columns:
        raise Parada("a foto não tem `memoria_id` (mineração anterior às partes da lição): minere de novo")
    return F, json.loads(rod.read_text(encoding="utf-8"))


def memorias_do_catalogo(catalogo, unidade, base):
    """(ids das memórias fechadas desta unidade nesta base, as rodadas em que elas foram mineradas)."""
    d = json.loads(Path(catalogo).read_text(encoding="utf-8"))
    itens = [x for x in d.get("itens", []) if x.get("unidade") == unidade and x.get("base") == base]
    return {x["id"] for x in itens}, {x.get("rodada_id") for x in itens if x.get("rodada_id")}


def parte_especifica(unidade):
    """O módulo `mineracao_<unidade>.py` que o funil aponta (o mesmo que o `minerar.py` usa)."""
    linha = mn.linha_do_funil(unidade)
    if not linha.startswith("script:"):
        raise Parada(f"a linha do funil de {unidade} é {linha}: a re-entrada só lê unidades mineradas por script")
    arq, _ = mn.localizar_script(unidade, linha.split(":", 1)[1])
    spec = spec_from_file_location(arq.stem, arq)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ler_agora(mod, analise, unidade):
    """A população da unidade na rodada, lida pela parte específica: um erro por linha com `memoria_id`."""
    casos = analise.EU[analise.EU.unidade.eq(unidade)].copy()
    msgs = analise.carga.steps[["step_ref", "err_msg", "err_msg_estado"]].rename(
        columns={"err_msg": "mensagem", "err_msg_estado": "estado"})
    L = mod.medir(casos, msgs)["erros_lidos"]
    return L


def cobertura(mid, foto_ids, catalogo_ids):
    if _vazio(mid):
        return "sem_parte"
    if mid in catalogo_ids:
        return "memoria_no_catalogo"
    if mid in foto_ids:
        return "parte_decidida_sem_memoria"
    return "parte_nova"


def delta(F, A, catalogo_ids):
    """Os erros que entraram, saíram ou mudaram de parte, pelo `step_ref`, com a cobertura de cada um."""
    def norm(df):
        df = df.copy()
        for c in CHAVE:
            if c not in df.columns:
                df[c] = None
        df["memoria_id"] = df["memoria_id"].map(lambda v: None if _vazio(v) else str(v))
        df["step_ref"] = df["step_ref"].astype(str)
        return df.drop_duplicates("step_ref")
    F, A = norm(F), norm(A)
    foto_ids = {m for m in F.memoria_id if m}
    antes = dict(zip(F.step_ref, F.memoria_id))
    linhas = []
    for r in A.itertuples(index=False):
        if r.step_ref not in antes:
            sit = "entrou"
        elif antes[r.step_ref] != r.memoria_id:
            sit = "mudou_de_parte"
        else:
            continue
        linhas.append({**{c: getattr(r, c) for c in CHAVE}, "situacao": sit,
                       "memoria_id_antes": antes.get(r.step_ref), "memoria_id_agora": r.memoria_id,
                       "cobertura": cobertura(r.memoria_id, foto_ids, catalogo_ids)})
    agora = set(A.step_ref)
    for r in F[~F.step_ref.isin(agora)].itertuples(index=False):
        linhas.append({**{c: getattr(r, c) for c in CHAVE}, "situacao": "saiu", "memoria_id_antes": r.memoria_id,
                       "memoria_id_agora": None, "cobertura": ""})
    D = pd.DataFrame(linhas, columns=CHAVE + ["situacao", "memoria_id_antes", "memoria_id_agora", "cobertura"])
    return D.sort_values(["situacao", "cobertura", "step_ref"], na_position="first").reset_index(drop=True)


def por_memoria(F, A, catalogo_ids):
    """Por memória (as da foto, as de agora e as do catálogo): erros na foto, agora, a variação e `revisar`. Só
    revisa a memória do catálogo que está na foto: uma que não está (0 na foto) quer dizer que a foto não é a
    mineração que fechou o catálogo — vira o aviso `catalogo_fora_da_foto` do resumo, não variação."""
    f = F.memoria_id.dropna().astype(str).value_counts()
    a = A.memoria_id.dropna().astype(str).value_counts()
    ids = sorted(set(f.index) | set(a.index) | set(catalogo_ids))
    linhas = []
    for i in ids:
        nf, na = int(f.get(i, 0)), int(a.get(i, 0))
        var = (na - nf) / nf if nf else (float("inf") if na else 0.0)
        cat = i in catalogo_ids
        linhas.append({"memoria_id": i, "no_catalogo": cat, "erros_foto": nf, "erros_agora": na,
                       "variacao": round(var, 4) if var != float("inf") else "nova",
                       "revisar": bool(cat and nf > 0 and abs(na - nf) / nf > LIMIAR_REVISAR)})
    return pd.DataFrame(linhas, columns=["memoria_id", "no_catalogo", "erros_foto", "erros_agora", "variacao",
                                         "revisar"])


def estado(D, M):
    """Os estados da unidade (ver o docstring do módulo), em ordem fixa."""
    e = []
    entrou = D[D.situacao.eq("entrou")]
    if D.cobertura.isin(DESCOBERTAS).any():
        e.append("descoberto")
    elif len(entrou):
        e.append("cresceu_coberto")
    if D.situacao.eq("saiu").any():
        e.append("encolheu")
    if D.situacao.eq("mudou_de_parte").any():
        e.append("mudou_de_parte")
    if M.revisar.any():
        e.append("revisar")
    return e or ["igual"]


def conferir_unidade(unidade, pasta, m, analise, mineracao, catalogo, saida):
    F, foto_rodada = ler_foto(mineracao)
    cat_ids, cat_rodadas = memorias_do_catalogo(catalogo, unidade, m["base"])
    A = ler_agora(parte_especifica(unidade), analise, unidade)
    D, M = delta(F, A, cat_ids), por_memoria(F, A, cat_ids)
    est = estado(D, M)
    out = mo.caminho_io(Path(saida))
    out.mkdir(parents=True, exist_ok=True)
    D.to_csv(out / "delta.csv", index=False)
    D[D.cobertura.isin(DESCOBERTAS)].to_csv(out / "descobertos.csv", index=False)
    M.to_csv(out / "por_memoria.csv", index=False)
    conta = lambda s: int(D.situacao.eq(s).sum())  # noqa: E731
    cob = D[D.situacao.isin(["entrou", "mudou_de_parte"])].cobertura.value_counts()
    r = {"unidade": unidade, "base": m["base"], "estado": est,
         "foto": {"rodada_id": foto_rodada.get("rodada_id"), "fonte_id": foto_rodada.get("fonte_id"), "erros": len(F)},
         "agora": {"rodada_id": m["rodada_id"], "fonte_id": m["fonte_id"], "erros": len(A)},
         "mesma_fonte": foto_rodada.get("fonte_id") == m["fonte_id"],
         "entraram": conta("entrou"), "sairam": conta("saiu"), "mudaram_de_parte": conta("mudou_de_parte"),
         "cobertura": {c: int(cob.get(c, 0)) for c in COBERTURAS},
         "descobertos_por_papel": {str(k): int(v) for k, v in
                                   D[D.cobertura.isin(DESCOBERTAS)].role.value_counts().sort_index().items()},
         "descobertos_por_mes": {str(k): int(v) for k, v in
                                 D[D.cobertura.isin(DESCOBERTAS)].mes.value_counts().sort_index().items()},
         "memorias_no_catalogo": sorted(cat_ids), "revisar": sorted(M[M.revisar].memoria_id),
         "catalogo_fora_da_foto": sorted(M[M.no_catalogo & M.erros_foto.eq(0)].memoria_id),
         "foto_da_rodada_do_catalogo": (foto_rodada.get("rodada_id") in cat_rodadas) if cat_rodadas else None,
         "limiar_revisar": LIMIAR_REVISAR, "catalogo_sha256": _sha(catalogo)}
    (out / "resumo.json").write_text(json.dumps(r, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
    return out, r


def _imprimir(r, out):
    c = r["cobertura"]
    print(f"{r['unidade']} · foto {str(r['foto']['rodada_id'])[:16]} ({r['foto']['erros']} erros) → rodada "
          f"{r['agora']['rodada_id'][:16]} ({r['agora']['erros']}) · estado: {', '.join(r['estado'])}")
    if not r["mesma_fonte"]:
        print("  aviso: a foto é de outra fonte; o step_ref pode não se repetir entre as duas")
    print(f"  entraram {r['entraram']} · saíram {r['sairam']} · mudaram de parte {r['mudaram_de_parte']}")
    print(f"  cobertura (entraram + mudaram): memória no catálogo {c['memoria_no_catalogo']} · parte decidida sem "
          f"memória {c['parte_decidida_sem_memoria']} · parte nova {c['parte_nova']} · sem parte {c['sem_parte']}")
    if r["foto_da_rodada_do_catalogo"] is False or r["catalogo_fora_da_foto"]:
        print(f"  aviso: a foto não é a mineração que fechou o catálogo (rodada da foto fora das do catálogo: "
              f"{r['foto_da_rodada_do_catalogo'] is False}; memórias do catálogo fora da foto: "
              f"{len(r['catalogo_fora_da_foto'])}); a variação por memória só vale para as que estão na foto")
    if r["descobertos_por_papel"]:
        print(f"  descobertos por papel: {r['descobertos_por_papel']} · por mês: {r['descobertos_por_mes']}")
    if r["revisar"]:
        print(f"  revisar (variação > {int(r['limiar_revisar'] * 100)}%): {', '.join(r['revisar'])}")
    print(f"  → {out}")


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("unidades", nargs="*")
    p.add_argument("--todas", action="store_true", help="toda unidade desta base com memória no catálogo")
    p.add_argument("--rodada", required=True)
    p.add_argument("--fonte")
    p.add_argument("--mineracao", help="a pasta da mineração (só com uma unidade; padrão resultados/mineracao/<u>)")
    p.add_argument("--catalogo", default=str(CATALOGO))
    p.add_argument("--saida", help="a pasta de saída (só com uma unidade; padrão resultados/mineracao/reentrada/<u>)")
    a = p.parse_args(argv)
    if not a.unidades and not a.todas:
        p.error("passe uma ou mais unidades, ou --todas")
    if len(a.unidades) > 1 or a.todas:
        if a.mineracao or a.saida:
            p.error("--mineracao e --saida só valem com uma unidade")
    try:
        pasta, m, analise = carregar_rodada(a.rodada, a.fonte)
    except Parada as exc:
        print(f"PARADA: {exc}")
        return 2
    unidades = list(a.unidades)
    if a.todas:
        d = json.loads(Path(a.catalogo).read_text(encoding="utf-8"))
        unidades += sorted({x["unidade"] for x in d.get("itens", []) if x.get("base") == m["base"]} - set(unidades))
    if not unidades:
        print(f"nenhuma unidade com memória no catálogo para {m['base']}")
        return 0
    codigo = 0
    for u in unidades:
        base_res = PIPELINE / "resultados" / "mineracao"
        try:
            out, r = conferir_unidade(u, pasta, m, analise, a.mineracao or base_res / u, a.catalogo,
                                      a.saida or base_res / "reentrada" / u)
        except Parada as exc:
            print(f"{u} · NÃO CONFERIDA: {exc}")
            codigo = 2
            continue
        _imprimir(r, out)
        if r["estado"] not in (["igual"], ["cresceu_coberto"]) and codigo == 0:
            codigo = 1
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
