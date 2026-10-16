"""Duas rodadas da mesma fonte, artefato a artefato: o código novo mudou algum número? (roadmap b3 #42)

Lê os dois `manifesto.json` e compara os SHA-256 dos artefatos. O que tem o mesmo hash é igual e não se abre. Um CSV com
hash diferente é aberto como texto e classificado: só colunas novas, só a ordem das linhas, ou conteúdo diferente (aí
diz quantas linhas mudaram, nunca quais). A genealogia muda de forma de propósito (a decisão D4 de 16/10 juntou as
colunas unidade e destino), então nela se confere a conservação: o total de erros de cada etapa e os erros por família.
As figuras só se listam: o desenho muda quando o código do gráfico muda.

Depois confere as duas tabelas da rodada nova contra a própria rodada: o gasto por unidade e papel
(`consolidacao_unidade_papel_tokens.csv`) somado por unidade = a triagem, os sem unidade = os pendentes, o total = o
resumo; o que vem depois do erro (`consolidacao_depois_unidade.csv`) somado = todos os erros. Com a fonte (--fonte, ou a
v2 em data/ se existir), também o gasto por papel contra os tokens dos passos com erro na fonte (o hash da fonte tem de
ser o do manifesto).

Imprime só nomes de arquivo e de coluna, contagens, nomes de unidade e de papel — nenhum identificador de execução nem
texto de caso. Sai com 0 se nenhum número mudou e as conferências fecham; com 1, e a lista do que não fechou, se não.

Uso, da raiz (a pasta da rodada, ou só o identificador dela em pipeline/resultados/):
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/comparar_rodadas.py \\
        --antes 609c947b15295c84 --depois 96958e65cb7e615a [--fonte <parquet>] [--listar-iguais]
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
RESULTADOS = PIPELINE / "resultados"
FONTE_PADRAO = PIPELINE.parent / "data" / "base_erros_minerados_full_v2.parquet"  # o bp.TRACE (a v2)
CONCLUIDA = "concluida_tecnicamente_sem_aprovacao_semantica"
SEM_UNIDADE = "sem unidade (pendente)"  # o mesmo rótulo de mineracao_observada.SEM_UNIDADE
# Colunas que identificam a rodada e por isso sempre diferem; ficam fora da comparação de conteúdo.
IGNORADAS = {"rodada_id"}
GENEALOGIA = "genealogia_arestas.csv"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _pasta(arg):
    p = Path(arg)
    if p.is_dir():
        return p.resolve()
    for nome in (arg, "observada_" + arg):
        if (RESULTADOS / nome).is_dir():
            return (RESULTADOS / nome).resolve()
    raise SystemExit(f"rodada não encontrada: {arg}")


def _manifesto(pasta):
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    if m.get("estado") != CONCLUIDA:
        raise SystemExit(f"{pasta.name}: rodada não concluída (estado {m.get('estado')!r})")
    return m


def _plano(d, prefixo=""):
    """Resumo aninhado em chaves 'a.b' para listar só o que difere."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_plano(v, f"{prefixo}{k}."))
        else:
            out[prefixo + k] = v
    return out


def _csv(path):
    # Como texto: compara o que foi gravado, sem arredondar nem converter tipos.
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def comparar_csv(a, b):
    """Classifica a diferença de dois CSVs com hash diferente. Devolve (situação, detalhe, mudou_numero)."""
    novas = [c for c in b.columns if c not in a.columns and c not in IGNORADAS]
    removidas = [c for c in a.columns if c not in b.columns and c not in IGNORADAS]
    comuns = [c for c in a.columns if c in b.columns and c not in IGNORADAS]
    if removidas:
        return "colunas removidas", ", ".join(removidas), True
    la = Counter(map(tuple, a[comuns].itertuples(index=False)))
    lb = Counter(map(tuple, b[comuns].itertuples(index=False)))
    if la != lb:
        so_a, so_b = sum((la - lb).values()), sum((lb - la).values())
        return ("conteúdo diferente",
                f"{len(a)} → {len(b)} linhas; {so_a} só na antes, {so_b} só na depois (nas colunas em comum)", True)
    if novas:
        return "só colunas novas", ", ".join(novas), False
    if list(a.columns) != list(b.columns):
        return "só a ordem das colunas", "", False
    if a[comuns].equals(b[comuns]):
        return "igual nas colunas comparadas", "difere só em " + ", ".join(sorted(IGNORADAS & set(a.columns))), False
    return "só a ordem das linhas", "", False


def conservacao_genealogia(a, b):
    """A forma da genealogia pode mudar; os erros não: total por etapa comum e erros por família iguais."""
    falhas, linhas = [], []
    for df in (a, b):
        df["erros"] = df.erros.astype(int)
    ta, tb = a.groupby("etapa").erros.sum(), b.groupby("etapa").erros.sum()
    for etapa in sorted(set(ta.index) | set(tb.index)):
        va, vb = ta.get(etapa), tb.get(etapa)
        if va is None or vb is None:
            linhas.append(f"    etapa {etapa}: só na {'depois' if va is None else 'antes'} ({va if vb is None else vb} erros)")
        elif va != vb:
            falhas.append(f"genealogia: etapa {etapa} com {va} erros na antes e {vb} na depois")
    if len(set(ta.values) | set(tb.values)) > 1:
        falhas.append(f"genealogia: as etapas não somam o mesmo número de erros ({sorted(set(ta.values) | set(tb.values))})")
    primeira = lambda df: df[df.etapa.str.startswith("familia->")].groupby("origem").erros.sum()
    fa, fb = primeira(a), primeira(b)
    if not fa.equals(fb):
        falhas.append("genealogia: erros por família diferentes")
    linhas.append(f"    {len(ta)} → {len(tb)} etapas; {int(ta.max()) if len(ta) else 0} erros em cada; "
                  f"{len(fa)} famílias com os mesmos erros: {'sim' if fa.equals(fb) else 'NÃO'}")
    return falhas, linhas


def conferir_tabelas_novas(pasta, m, fonte=None):
    """As duas tabelas de 15–16/10 da rodada nova, contra a própria rodada (e a fonte, se vier)."""
    falhas, linhas = [], []
    resumo = m["resumo"]
    arts = m["artefatos"]
    if "consolidacao_unidade_papel_tokens.csv" in arts:
        upt = pd.read_csv(pasta / "consolidacao_unidade_papel_tokens.csv")
        tri = pd.read_csv(pasta / "triagem_visivel_observada.csv").set_index("unidade")
        obs = upt[upt.unidade.ne(SEM_UNIDADE)].groupby("unidade")[["erros", "tokens_n_conhecidos"]].sum()
        j = obs.join(tri[["erros_observaveis", "tokens_n_conhecidos"]], rsuffix="_triagem", how="outer")
        dif = j[(j.erros.fillna(-1) != j.erros_observaveis.fillna(-1))
                | (j.tokens_n_conhecidos.fillna(-1) != j.tokens_n_conhecidos_triagem.fillna(-1))]
        sem = upt[upt.unidade.eq(SEM_UNIDADE)]
        checks = {
            "por unidade = triagem (erros e tokens)": (dif.empty, f"{len(j)} unidades"
                                                       + ("" if dif.empty else "; diferem: " + ", ".join(dif.index))),
            "sem unidade = pendentes do resumo": (int(sem.erros.sum()) == int(resumo["pendentes"]),
                                                  f"{int(sem.erros.sum())} × {resumo['pendentes']}"),
            "total = erros estruturados do resumo": (int(upt.erros.sum()) == int(resumo["erros_estruturados"]),
                                                     f"{int(upt.erros.sum())} × {resumo['erros_estruturados']}"),
        }
        if resumo.get("tokens_estruturados_conhecidos") is not None:
            tot = int(upt.tokens_n_conhecidos.sum())
            checks["tokens = tokens estruturados do resumo"] = (tot == int(resumo["tokens_estruturados_conhecidos"]),
                                                                f"{tot} × {resumo['tokens_estruturados_conhecidos']}")
        if fonte is not None:
            checks.update(_por_papel_na_fonte(upt, m, fonte))
        for nome, (ok, det) in checks.items():
            linhas.append(f"    {'ok ' if ok else 'NÃO'} gasto por unidade e papel: {nome} ({det})")
            if not ok:
                falhas.append(f"gasto por unidade e papel: {nome} ({det})")
    else:
        falhas.append("a rodada depois não tem consolidacao_unidade_papel_tokens.csv")
    if "consolidacao_depois_unidade.csv" in arts:
        dep = pd.read_csv(pasta / "consolidacao_depois_unidade.csv")
        ok = int(dep.erros.sum()) == int(resumo["erros_estruturados"])
        linhas.append(f"    {'ok ' if ok else 'NÃO'} o que vem depois do erro: soma = erros estruturados "
                      f"({int(dep.erros.sum())} × {resumo['erros_estruturados']})")
        if not ok:
            falhas.append("o que vem depois do erro: a soma não dá todos os erros")
    else:
        falhas.append("a rodada depois não tem consolidacao_depois_unidade.csv")
    return falhas, linhas


def _por_papel_na_fonte(upt, m, fonte):
    import pyarrow.parquet as pq
    if m.get("fonte_sha256") and _sha256(fonte) != m["fonte_sha256"]:
        return {"por papel = fonte": (False, "a fonte não é a da rodada (SHA-256 diferente do manifesto)")}
    f = pq.read_table(fonte, columns=["papel", "structured_error", "total_tokens"]).to_pandas()
    f = f[pd.to_numeric(f.structured_error).eq(1)]
    na_fonte = f.assign(t=pd.to_numeric(f.total_tokens)).groupby("papel").agg(erros=("t", "size"), tokens=("t", "sum"))
    na_rodada = upt.groupby("role").agg(erros=("erros", "sum"), tokens=("tokens_n_conhecidos", "sum"))
    j = na_rodada.join(na_fonte, rsuffix="_fonte", how="outer").fillna(0)
    d_err = (j.erros - j.erros_fonte).abs()
    d_tok = (j.tokens - j.tokens_fonte).abs()
    return {"por papel = fonte (erros)": (bool(d_err.eq(0).all()), f"{len(j)} papéis; diferença máxima {int(d_err.max())}"),
            "por papel = fonte (tokens)": (bool(d_tok.eq(0).all()), f"diferença máxima {int(d_tok.max())} tokens")}


def _fora_do_manifesto(path, esperado, gerado_em):
    """None se o arquivo tem o hash do manifesto; senão, o que aconteceu com ele (sem abrir o conteúdo na tela)."""
    if not path.is_file():
        return "ausente"
    if _sha256(path) == esperado:
        return None
    from datetime import datetime, timezone
    st = path.stat()
    quando = datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds")[:19]
    # Pistas de um editor que regravou o arquivo: só o fim de linha (CRLF) ou a marca BOM do UTF-8 mudou.
    bruto = path.read_bytes()
    pista = ""
    for nome, versao in (("só o fim de linha (CRLF → LF volta ao hash)", bruto.replace(b"\r\n", b"\n")),
                         ("só a marca BOM no começo", bruto.removeprefix(b"\xef\xbb\xbf")),
                         ("BOM e fim de linha", bruto.removeprefix(b"\xef\xbb\xbf").replace(b"\r\n", b"\n"))):
        if versao != bruto and hashlib.sha256(versao).hexdigest() == esperado:
            pista = f"; {nome}"
            break
    return (f"alterado (modificado em {quando} UTC; rodada gerada em {(gerado_em or '?')[:19]} UTC; "
            f"{st.st_size} bytes{pista or '; conteúdo diferente'})")


def _juntar_perfis(itens):
    """perfis/<unidade>/<tabela> com a mesma situação e o mesmo detalhe numa linha só (a saída cabe numa foto)."""
    vistos, ordem = {}, []
    for nome, detalhe in itens:
        partes = nome.split("/")
        chave = (f"perfis/*/{partes[2]}" if len(partes) == 3 and partes[0] == "perfis" else nome, detalhe)
        if chave not in vistos:
            ordem.append(chave)
        vistos[chave] = vistos.get(chave, 0) + 1
    return [(n if not n.startswith("perfis/*/") else f"{n} ({vistos[(n, d)]} unidades)", d) for n, d in ordem]


def comparar(antes, depois, fonte=None, detalhe_iguais=False):
    """Imprime o relatório e devolve a lista do que não fechou (vazia = nenhum número mudou)."""
    ma, mb = _manifesto(antes), _manifesto(depois)
    falhas = []
    print(f"antes:  {antes.name} (rodada {ma['rodada_id'][:16]}, gerada em {ma.get('gerado_em', '?')[:19]})")
    print(f"depois: {depois.name} (rodada {mb['rodada_id'][:16]}, gerada em {mb.get('gerado_em', '?')[:19]})")
    for campo in ("contrato", "base", "fonte_id", "extracao", "corte_texto"):
        if ma.get(campo) != mb.get(campo):
            raise SystemExit(f"{campo} diferente entre as rodadas ({ma.get(campo)!r} × {mb.get(campo)!r}): "
                             "não é a mesma fonte, a comparação não vale")
    print(f"mesma fonte: {ma['fonte_id'][:16]}… (extração {ma.get('extracao')})")
    if ma["rodada_id"] == mb["rodada_id"]:
        print("aviso: o mesmo identificador de rodada — o código que entra no identificador não mudou")
    codigo = sorted(k for k in set(ma["codigo"]) | set(mb["codigo"]) if ma["codigo"].get(k) != mb["codigo"].get(k))
    print(f"código que mudou: {len(codigo)} arquivo(s)" + "".join(f"\n    {k}" for k in codigo))

    ra, rb = _plano(ma["resumo"]), _plano(mb["resumo"])
    dif_resumo = sorted(k for k in set(ra) | set(rb) if ra.get(k) != rb.get(k))
    print(f"\nresumo do manifesto: {len(ra)} campos, {len(dif_resumo)} diferente(s)")
    for k in dif_resumo:
        print(f"    {k}: {ra.get(k)!r} → {rb.get(k)!r}")
        falhas.append(f"resumo: {k}")
    ca, cb = _plano(ma.get("capacidades", {})), _plano(mb.get("capacidades", {}))
    for k in sorted(k for k in set(ca) | set(cb) if ca.get(k) != cb.get(k)):
        print(f"    capacidade {k}: {ca.get(k)!r} → {cb.get(k)!r} (informativo)")

    # Como o painel: um arquivo fora do manifesto não é comparado (o conteúdo não vale como prova), mas o resto é.
    fora = {}
    for pasta, m in ((antes, ma), (depois, mb)):
        for nome, h in sorted(m["artefatos"].items()):
            estado = _fora_do_manifesto(pasta / nome, h, m.get("gerado_em"))
            if estado:
                fora.setdefault(nome, []).append(f"{pasta.name}: {estado}")
                falhas.append(f"{pasta.name}: {nome} {estado.split(' (')[0]} depois da rodada")
    if fora:
        print(f"\nfora do manifesto (não comparados): {len(fora)}")
        for nome, estados in fora.items():
            print(f"    {nome}" + "".join(f"\n        {e}" for e in estados))

    aa, ab = ma["artefatos"], mb["artefatos"]
    grupos = {}
    for nome in sorted(set(aa) | set(ab)):
        if nome in fora:
            continue
        if nome not in ab:
            grupos.setdefault("removido", []).append((nome, ""))
            if nome.endswith(".csv"):
                falhas.append(f"tabela removida: {nome}")
        elif nome not in aa:
            grupos.setdefault("novo", []).append((nome, ""))
        elif aa[nome] == ab[nome]:
            grupos.setdefault("igual (hash)", []).append((nome, ""))
        elif not nome.endswith(".csv"):
            grupos.setdefault("figura diferente (informativo)", []).append((nome, ""))
        elif nome == GENEALOGIA:
            f, linhas = conservacao_genealogia(_csv(antes / nome), _csv(depois / nome))
            situacao = "forma diferente, erros conservados" if not f else "forma diferente, erros NÃO conservados"
            grupos.setdefault(situacao, []).append((nome, "\n" + "\n".join(linhas)))
            falhas += f
        else:
            situacao, detalhe, mudou = comparar_csv(_csv(antes / nome), _csv(depois / nome))
            grupos.setdefault(situacao, []).append((nome, detalhe))
            if mudou:
                falhas.append(f"{nome}: {situacao} ({detalhe})")
    print(f"\nartefatos: {len(aa)} na antes, {len(ab)} na depois")
    for situacao, itens in grupos.items():
        print(f"  {situacao}: {len(itens)}")
        if situacao == "igual (hash)" and not detalhe_iguais:
            continue
        for nome, detalhe in _juntar_perfis(itens):
            print(f"    {nome}" + (f" — {detalhe}" if detalhe and not detalhe.startswith("\n") else detalhe))

    print("\ntabelas novas da rodada depois:")
    usadas = {"consolidacao_unidade_papel_tokens.csv", "triagem_visivel_observada.csv", "consolidacao_depois_unidade.csv"}
    if usadas & set(fora):
        print("    não conferidas: " + ", ".join(sorted(usadas & set(fora))) + " fora do manifesto")
    else:
        f, linhas = conferir_tabelas_novas(depois, mb, fonte)
        print("\n".join(linhas))
        falhas += f

    print(f"\nveredito: {'nenhum número mudou e as conferências fecham' if not falhas else 'NÃO FECHA'}")
    for x in falhas:
        print(f"  - {x}")
    return falhas


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--antes", required=True, help="pasta ou identificador da rodada de referência")
    p.add_argument("--depois", required=True, help="pasta ou identificador da rodada nova")
    p.add_argument("--fonte", type=Path, help="parquet da fonte, para conferir o gasto por papel "
                                              f"(padrão: data/{FONTE_PADRAO.name}, se existir)")
    p.add_argument("--listar-iguais", action="store_true", help="lista também os artefatos de hash igual")
    args = p.parse_args(argv)
    if args.fonte is None and FONTE_PADRAO.is_file():
        args.fonte = FONTE_PADRAO
    if args.fonte is not None and not args.fonte.is_file():
        raise SystemExit(f"fonte não encontrada: {args.fonte}")
    print(f"fonte para o gasto por papel: {args.fonte.name if args.fonte else 'nenhuma (essa conferência fica de fora)'}")
    return 1 if comparar(_pasta(args.antes), _pasta(args.depois), args.fonte, args.listar_iguais) else 0


if __name__ == "__main__":
    raise SystemExit(main())
