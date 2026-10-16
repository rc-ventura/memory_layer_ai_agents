"""Minera uma candidata a memória numa rodada da base 3: os 9 passos do procedimento 06, com o porquê no racional 07.

    uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/minerar.py <unidade> --rodada <id|pasta>
        [--passo N] [--fonte <parquet>] [--saida <pasta>]

Sem `--passo`, roda de 1 a 9 e para no primeiro problema (saída 1, o motivo numa linha). Com `--passo N`, roda só
aquele passo, lendo o que os anteriores gravaram em `<saida>` (padrão: `pipeline/resultados/mineracao/<unidade>/`).

  1 conferir a rodada · 2 monitoramento · 3 parte genérica · 4 parte específica · 5 confiança · 6 destino ·
  7 auditoria independente e encontro · 8 arquivo final · 9 saída (manifesto, relatório, varredura, resumo)

A parte específica é o módulo `mineracao_<unidade>.py` (a interface está no docstring dele), escolhido pela linha da
lição no funil do procedimento: o aprovado, em `pipeline/especificas/`, ou, antes da aprovação, a proposta em
`propostas/<unidade>/` (o resumo e o manifesto dizem qual). A auditoria é o `audit/scripts/audit_candidata_base3.py`, que não
importa nada daqui. Este arquivo fica fora do hash do código da rodada: rodar ou mudar a mineração não troca o
identificador da rodada. Determinístico, sem LLM.
"""
import argparse
import datetime
import glob
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import subprocess
import sys

PIPELINE = Path(__file__).resolve().parents[1]
ANALISE = PIPELINE.parent
RAIZ = ANALISE.parents[1]
SKILLS = RAIZ / ".claude" / "skills"
AUDITORIA = ANALISE / "audit" / "scripts" / "audit_candidata_base3.py"
ESQUEMA = RAIZ / "analysis" / "registros" / "esquema-memoria.json"
sys.path.insert(0, str(PIPELINE))
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import base_pipeline as bp
import mineracao_observada as mo

PASSOS = {1: "conferir a rodada", 2: "monitoramento", 3: "parte genérica", 4: "parte específica", 5: "confiança",
          6: "destino", 7: "auditoria e encontro", 8: "arquivo final", 9: "saída"}
TABELAS = ["erros_lidos", "inventario", "inventario_papel", "inventario_mes", "imports_autorizados"]


class Parada(Exception):
    """Um passo parou a mineração; a mensagem é o motivo, numa linha, sem dado de caso."""


def _sha(path):
    return mo.sha256(path)


def _json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _ler_json(path):
    if not Path(path).exists():
        raise Parada(f"falta {Path(path).name}: rode o passo anterior")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _markdown(df):
    linhas = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    linhas += ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(linhas)


def pasta_rodada(arg):
    p = Path(arg)
    if p.is_dir():
        return mo.caminho_io(p.resolve())
    for nome in (arg, "observada_" + arg):
        if (PIPELINE / "resultados" / nome).is_dir():
            return mo.caminho_io((PIPELINE / "resultados" / nome).resolve())
    raise Parada(f"rodada não encontrada: {arg}")


def linha_do_funil(u):
    docs = glob.glob(str(ANALISE / "docs" / "*procedimento-mineracao-candidatas*.md"))
    if not docs:
        raise Parada("a análise não tem procedimento de mineração com o funil")
    txt = Path(docs[0]).read_text(encoding="utf-8")
    bloco = txt.split("<!-- funil", 1)[-1].split("<!-- /funil -->", 1)[0]
    m = re.search(rf"^\|\s*`{re.escape(u)}`\s*\|\s*`([^`]+)`", bloco, re.M)
    if not m:
        raise Parada(f"{u} fora do funil: registre a lição na tabela do procedimento")
    return m.group(1)


def localizar_script(u, nome):
    """(caminho, situação) do script específico: o aprovado em pipeline/especificas/ ou a proposta em propostas/<u>/."""
    for arq, situacao in ((PIPELINE / "especificas" / f"{nome}.py", "aprovado"),
                          (ANALISE / "propostas" / u / f"{nome}.py", "proposta")):
        if arq.exists():
            return arq, situacao
    raise Parada(f"o funil aponta {nome}.py, que não existe nem em pipeline/especificas/ nem em propostas/{u}/")


class Mineracao:
    def __init__(self, u, rodada, fonte=None, saida=None):
        self.u = u
        self.rodada = pasta_rodada(rodada)
        self.fonte_arg = fonte
        self.saida = mo.caminho_io(Path(saida or PIPELINE / "resultados" / "mineracao" / u).resolve())
        self.saida.mkdir(parents=True, exist_ok=True)
        self.manifesto = json.loads((self.rodada / "manifesto.json").read_text(encoding="utf-8"))
        self.ids = {"rodada_id": self.manifesto["rodada_id"], "fonte_id": self.manifesto["fonte_id"]}
        self.registro = {}   # passo -> "ok" | "não conferido: …" | o motivo da parada

    def ler(self, nome):
        return mo.ler_artefato(self.rodada, nome, **self.ids)

    def modulo(self):
        parte = linha_do_funil(self.u)
        if not parte.startswith("script:"):
            raise Parada(f"a linha do funil é {parte}: a lição segue a investigação (procedimento 16)")
        arq, self.situacao_script = localizar_script(self.u, parte.split(":", 1)[1])
        spec = spec_from_file_location(arq.stem, arq)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, arq

    def tabelas(self):
        faltam = [t for t in TABELAS if not (self.saida / f"{t}.csv").exists()]
        if faltam:
            raise Parada(f"faltam as tabelas da parte específica ({', '.join(faltam)}): rode o passo 4")
        return {t: pd.read_csv(self.saida / f"{t}.csv", dtype={"exec_id": str, "step_ref": str})
                for t in TABELAS}

    def fonte(self):
        f = Path(self.fonte_arg) if self.fonte_arg else Path(bp.EXTRACOES[self.manifesto.get("extracao") or "v2"])
        if not f.exists():
            raise Parada(f"fonte não encontrada ({f.name}); passe --fonte")
        if _sha(f) != self.manifesto.get("fonte_sha256"):
            raise Parada("a fonte não é a da rodada (hash diferente do manifesto); passe --fonte com a certa")
        return f

    # ── 1 · conferir a rodada ──────────────────────────────────────────────────────────────────────────────
    def passo1(self):
        m = self.manifesto
        if m.get("estado") != "concluida_tecnicamente_sem_aprovacao_semantica":
            raise Parada(f"rodada não concluída (estado {m.get('estado')!r})")
        if m.get("codigo") != mo.versoes_codigo():
            raise Parada("a rodada é de outro código: rode `executar.py analisar` (rodada nova) e minere nela")
        fora = [n for n, h in m["artefatos"].items() if not (self.rodada / n).is_file() or _sha(self.rodada / n) != h]
        if fora:
            raise Parada(f"{len(fora)} artefato(s) fora do manifesto (ex.: {fora[0]})")
        tri = self.ler("triagem_visivel_observada.csv")
        linha = tri[tri.unidade.eq(self.u)]
        if linha.empty or linha.decisao.iloc[0] != mo.CANDIDATO:
            raise Parada(f"{self.u} não é candidata na triagem desta rodada")
        for t in ("perfil", "casos"):
            if f"perfis/{self.u}/{t}.csv" not in m["artefatos"]:
                raise Parada(f"sem perfil de {self.u} na rodada: `executar.py analisar --perfil {self.u}`")
        _json(self.saida / "passo1_rodada.json", {**self.ids, "base": m["base"], "extracao": m.get("extracao"),
                                                   "artefatos_conferidos": len(m["artefatos"])})
        return f"rodada {self.ids['rodada_id'][:16]} · {len(m['artefatos'])} artefatos no manifesto"

    # ── 2 · monitoramento ──────────────────────────────────────────────────────────────────────────────────
    def passo2(self):
        r = subprocess.run([sys.executable, str(SKILLS / "mineracao-base" / "scripts" / "monitorar.py"), str(ANALISE)],
                           capture_output=True, text=True, encoding="utf-8")
        (self.saida / "passo2_monitoramento.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode == 1:
            raise Parada("alerta do monitoramento: a lição volta ao pesquisador (passo2_monitoramento.txt)")
        if r.returncode == 2:
            return "não conferido: o monitoramento não tem as tabelas desta base (passo2_monitoramento.txt)"
        return "sem alerta"

    # ── 3 · parte genérica ─────────────────────────────────────────────────────────────────────────────────
    def passo3(self):
        perfil = self.ler(f"perfis/{self.u}/perfil.csv").iloc[0].to_dict()
        gen = {"perfil": perfil}
        for t in ("antes", "depois", "sub_unidades", "estabilidade", "proximo_final"):
            nome = f"perfis/{self.u}/{t}.csv"
            if nome in self.manifesto["artefatos"]:
                gen[t] = self.ler(nome).to_dict(orient="records")
        _json(self.saida / "passo3_generica.json", gen)
        return (f"{int(perfil['erros_observaveis'])} erros · {int(perfil['execucoes'])} execuções · "
                f"{int(perfil['meses'])} meses · {int(perfil['papeis'])} papéis")

    # ── 4 · parte específica ───────────────────────────────────────────────────────────────────────────────
    def passo4(self):
        mod, _ = self.modulo()
        fonte = self.fonte()
        carga = bp.carregar_carga(fonte, self.manifesto.get("extracao") or "v2")
        msgs = carga.steps[["step_ref", "err_msg", "err_msg_estado"]].rename(
            columns={"err_msg": "mensagem", "err_msg_estado": "estado"})
        casos = self.ler(f"perfis/{self.u}/casos.csv")
        t = mod.medir(casos, msgs)
        for nome in TABELAS:
            t[nome].to_csv(self.saida / f"{nome}.csv", index=False)
        return f"script {self.situacao_script} · {len(t['erros_lidos'])} erros lidos · {len(t['inventario'])} nomes"

    # ── 5 · confiança ──────────────────────────────────────────────────────────────────────────────────────
    def passo5(self):
        mod, _ = self.modulo()
        c = mod.confianca(self.tabelas())
        _json(self.saida / "passo5_confianca.json", c)
        txt = f"{c['medida']} {c['valor']:.1%} (limiar {c['limiar']:.0%})"
        if not c["passa"]:
            raise Parada(f"{txt}: abaixo do limiar do racional; a lição volta à investigação")
        return txt

    # ── 6 · destino ────────────────────────────────────────────────────────────────────────────────────────
    def passo6(self):
        mod, _ = self.modulo()
        d = mod.destino(self.tabelas())
        _json(self.saida / "passo6_destino.json", d)
        return " · ".join(f"{k} {v}" for k, v in d.items())

    # ── 7 · auditoria independente e encontro ──────────────────────────────────────────────────────────────
    def passo7(self):
        mod, _ = self.modulo()
        aud_json = self.saida / "auditoria.json"
        r = subprocess.run([sys.executable, str(AUDITORIA), self.u, "--fonte", str(self.fonte()),
                            "--json", str(aud_json)], capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise Parada(f"a auditoria não rodou (saída {r.returncode}): {(r.stdout + r.stderr).strip()[-200:]}")
        aud = json.loads(aud_json.read_text(encoding="utf-8"))
        scr = mod.para_encontro(self.tabelas())
        perfil = _ler_json(self.saida / "passo3_generica.json")["perfil"]
        linhas = []
        for bloco in ("populacao", "cobertura", "inventario", "listas_autorizadas"):
            a, s = aud.get(bloco, {}), scr.get(bloco, {})
            for k in sorted(set(a) | set(s)):
                if bloco == "cobertura" and k not in s:
                    continue  # o detalhe do sem_nome é informativo
                linhas.append({"medida": f"{bloco}.{k}", "mineracao": s.get(k), "auditoria": a.get(k),
                               "igual": s.get(k) == a.get(k)})
        for k, kp in (("erros", "erros_observaveis"), ("execucoes", "execucoes"), ("meses", "meses"),
                      ("papeis", "papeis")):
            linhas.append({"medida": f"perfil da rodada.{k}", "mineracao": int(perfil[kp]),
                           "auditoria": aud["populacao"][k], "igual": int(perfil[kp]) == aud["populacao"][k]})
        _json(self.saida / "passo7_encontro.json", linhas)
        dif = [l["medida"] for l in linhas if not l["igual"]]
        if dif:
            raise Parada(f"o encontro diverge em {len(dif)} medida(s) ({', '.join(dif[:4])}): a divergência é o achado")
        return f"{len(linhas)} medidas iguais"

    # ── 8 · arquivo final ──────────────────────────────────────────────────────────────────────────────────
    def passo8(self):
        mod, arq = self.modulo()
        t = self.tabelas()
        perfil = _ler_json(self.saida / "passo3_generica.json")["perfil"]
        conf = _ler_json(self.saida / "passo5_confianca.json")
        dest = _ler_json(self.saida / "passo6_destino.json")
        _ler_json(self.saida / "passo7_encontro.json")
        mem = mod.memoria(perfil, t, conf, dest, self.ids)
        esquema = json.loads(ESQUEMA.read_text(encoding="utf-8"))
        comando = (f"uv run python {Path(__file__).relative_to(RAIZ).as_posix()} {self.u} "
                   f"--rodada {self.ids['rodada_id'][:16]}")
        origem = {c: {"tipo": "checado", "comando": comando} for c in mem}
        origem["impact"] = {"tipo": "pendente", "nota": "null por decisão: pendente do juiz calibrado"}
        origem["validation"]["nota"] = "destino em aberto até a decisão do pesquisador"
        doc = {"esquema": esquema["versao"], "unidade": self.u, "base": self.manifesto["base"],
               "gerado_em": datetime.date.today().isoformat(), "parte_especifica": f"script:{arq.stem}",
               "memoria": mem, "origem": origem}
        destino = self.saida / f"memoria_{self.u}_{self.manifesto['base']}.json"
        _json(destino, doc)
        spec = spec_from_file_location("validar_memoria", SKILLS / "mineracao-candidata" / "scripts" / "validar_memoria.py")
        vm = module_from_spec(spec)
        spec.loader.exec_module(vm)
        erros, pend, _ = vm.validar(esquema, doc)
        if erros:
            raise Parada(f"o validar_memoria reprova ({len(erros)}): {erros[0]}")
        return f"{destino.name} aprovado no esquema {esquema['versao']}" + (f" · {len(pend)} pendência(s)" if pend else "")

    # ── 9 · saída ──────────────────────────────────────────────────────────────────────────────────────────
    def passo9(self):
        mod, arq = self.modulo()
        rel = self.saida / f"relatorio_{self.u}.md"
        rel.write_text(self.relatorio(), encoding="utf-8")
        arquivos = sorted(p for p in Path(self.saida).iterdir() if p.is_file() and p.name != "manifesto_mineracao.json")
        r = subprocess.run([sys.executable, str(SKILLS / "mineracao-base" / "scripts" / "varrer_pii.py"), str(rel),
                            str(self.saida / f"memoria_{self.u}_{self.manifesto['base']}.json")],
                           capture_output=True, text=True, encoding="utf-8")
        (self.saida / "passo9_varredura.txt").write_text(r.stdout, encoding="utf-8")
        if r.returncode != 0:
            raise Parada("o varredor achou dado pessoal no relatório ou na memória (passo9_varredura.txt)")
        codigo = {Path(p).relative_to(RAIZ).as_posix(): _sha(p) for p in (Path(__file__), arq, AUDITORIA, ESQUEMA)}
        _json(self.saida / "manifesto_mineracao.json",
              {"unidade": self.u, **self.ids, "fonte_sha256": self.manifesto.get("fonte_sha256"),
               "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(), "codigo": codigo,
               "script_especifico": self.situacao_script,
               "passos": self.registro, "artefatos": {p.name: _sha(p) for p in arquivos}})
        return f"{len(arquivos)} arquivos no manifesto · varredura limpa"

    def relatorio(self):
        L = [f"# Mineração de `{self.u}` — rodada `{self.ids['rodada_id'][:16]}`", "",
             f"Gerado em {datetime.date.today().isoformat()} pelo `minerar.py` (procedimento 06; porquê no 07; "
             f"racional da lição em `propostas/{self.u}/racional.md`).", "", "## Passos", ""]
        L += [f"- **{n} · {PASSOS[n]}:** {self.registro.get(n, '—')}" for n in PASSOS if n < 9]
        try:
            t = self.tabelas()
            for nome in ("inventario", "imports_autorizados"):
                L += ["", f"## {nome}", "", _markdown(t[nome])]
            mem = _ler_json(self.saida / f"memoria_{self.u}_{self.manifesto['base']}.json")["memoria"]
            L += ["", "## A memória proposta", "", f"- **category:** {mem['category']}",
                  f"- **description:** {mem['description']}", f"- **correction_guidance:** {mem['correction_guidance']}",
                  f"- **destino:** {mem['validation']['destino']}"]
        except Parada:
            pass
        return "\n".join(L) + "\n"

    def resumo(self):
        print(f"\n{'─' * 72}\nmineração {self.u} · rodada {self.ids['rodada_id'][:16]}")
        for n in PASSOS:
            if n in self.registro:
                print(f"  {n} {PASSOS[n]:<22} {self.registro[n]}")
        try:
            t = self.tabelas()
            print("\ninventário (tipo · nome · erros · execuções · papéis · meses):")
            for r in t["inventario"].itertuples(index=False):
                print(f"  {r.tipo:<18} {r.nome:<22} {r.erros:>6} {r.execucoes:>6} {r.papeis:>4} {r.meses:>4}")
            print(f"\nimports autorizados: {len(t['imports_autorizados'])} lista(s)")
            for r in t["imports_autorizados"].itertuples(index=False):
                print(f"  {r.erros:>5} erros · papéis: {r.papeis}\n        [{r.lista_autorizada}]")
        except Parada:
            pass
        print("─" * 72)

    def rodar(self, so=None):
        for n in ([so] if so else PASSOS):
            try:
                self.registro[n] = getattr(self, f"passo{n}")()
            except Parada as p:
                self.registro[n] = f"PAROU: {p}"
                self.resumo()
                return 1
        self.resumo()
        return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("unidade")
    p.add_argument("--rodada", required=True, help="identificador (ou prefixo da pasta observada_…) ou caminho da rodada")
    p.add_argument("--passo", type=int, choices=sorted(PASSOS), help="roda só este passo")
    p.add_argument("--fonte", help="parquet da fonte (padrão: o da extração da rodada); conferido pelo hash do manifesto")
    p.add_argument("--saida", help="pasta de saída (padrão: pipeline/resultados/mineracao/<unidade>/)")
    a = p.parse_args(argv)
    try:
        m = Mineracao(a.unidade, a.rodada, a.fonte, a.saida)
    except Parada as e:
        print(f"PAROU: {e}")
        return 1
    return m.rodar(a.passo)


if __name__ == "__main__":
    raise SystemExit(main())
