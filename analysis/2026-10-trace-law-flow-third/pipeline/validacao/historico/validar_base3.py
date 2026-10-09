"""Validação técnica da integração parcial; não minera nem aprova memórias.

Compara medidas estruturais diretamente com o Parquet, roda regressões e faz
smoke Python do trecho integrado do notebook. Não executa kernel Jupyter/Athena.
Resultados privados em resultados/; saída de console só agregados e estados.
"""
from __future__ import annotations

import ast
from collections import Counter
from contextlib import redirect_stdout
from decimal import Decimal
import hashlib
import inspect
import json
import math
from pathlib import Path
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pyarrow.parquet as pq

PIPELINE = Path(__file__).resolve().parents[2]
ROOT = PIPELINE.parents[2]
OUT = PIPELINE / "resultados" / "validacao_fechamento_2026-10-07"
sys.path.insert(0, str(PIPELINE))
import base_pipeline as bp


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_text(value):
    return None if pd.isna(value) or value == "" else str(value)


def source_flag(value):
    return source_text(value) in {"1", "1.0", "true", "True"}


def reciprocal_links(raw):
    """Recomputação direta, sem importar o adaptador ou seus helpers."""
    result = {}
    collisions = raw.groupby(["cod_idef_exeo", "papel"]).cod_idef_aget.nunique()
    collisions = set(collisions[collisions.gt(1)].index)
    maps = {"step_number": "step_number", "error_type": "error_type",
            "tool_name": "tool_name", "input_tokens": "input_tokens",
            "output_tokens": "output_tokens", "total_tokens": "total_tokens",
            "duration_seconds": "duration_seconds"}
    texts = {"model_output": ("error_model_output", 8000, 12000),
             "code_action": ("error_code_action", 8000, 12000),
             "observations": ("error_observations", 12000, 16000),
             "error_message": ("error_message", None, 20000)}
    for (eid, _, role), group in raw.sort_values("step_pos").groupby(
            ["cod_idef_exeo", "cod_idef_aget", "papel"], sort=False):
        records = list(group.iterrows())
        for (i, left), (j, right) in zip(records, records[1:]):
            if not source_flag(left.next_error_like) or not source_flag(right.prev_error_like):
                continue
            conflicts, support = 0, 0
            for prefix, slot, anchor in [("next", left, right), ("prev", right, left)]:
                for name, target in maps.items():
                    if prefix == "prev" and name not in {"step_number", "error_type"}:
                        continue
                    a, b = source_text(slot[prefix + "_" + name]), source_text(anchor[target])
                    if name == "duration_seconds" and a is not None and b is not None:
                        equal = math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-6)
                    elif name in {"step_number", "input_tokens", "output_tokens", "total_tokens"} and a is not None and b is not None:
                        # Parquet: n é inteiro; LAG/LEAD nullable podem ser double.
                        # 2 e 2.0 representam o mesmo número, não conflito textual.
                        equal = Decimal(a) == Decimal(b)
                    else:
                        equal = a == b
                    conflicts += not equal
                for name, (target, prev_cap, next_cap) in texts.items():
                    cap = prev_cap if prefix == "prev" else next_cap
                    if cap is None:
                        continue
                    a, b = source_text(slot[prefix + "_" + name]), source_text(anchor[target])
                    if a == b:
                        support += a is not None
                    elif a is not None and b is not None and len(a) == cap and b.startswith(a):
                        support += 1
                    else:
                        conflicts += 1
            numbers = [left.step_number, right.step_number, left.next_step_number, right.prev_step_number]
            missing = any(source_text(v) is None for v in numbers)
            reset = not missing and float(right.step_number) <= float(left.step_number)
            state = ("ambiguo" if (eid, role) in collisions else "conflito" if conflicts else
                     "ambiguo" if missing or not support or reset else "compativel_candidato")
            result[(int(i), int(j))] = state
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)
        if not condition:
            (OUT / "validacao.json").write_text(json.dumps(
                {"estado": "falhou", "verificacoes": checks}, ensure_ascii=False, indent=2), encoding="utf-8")
            raise AssertionError("Validação falhou: " + name)

    (OUT / "validacao.json").write_text('{"estado": "em_execucao"}', encoding="utf-8")
    source_sha = sha(bp.TRACE)
    previous = json.loads((PIPELINE / "resultados/etapa6_2026-10-07/conferencia_sintomas.json").read_text(encoding="utf-8"))
    check("mesma_fonte_da_etapa6", source_sha == previous["fonte_sha256"])
    suite = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "analysis/tests",
                            "-p", "test_*.py", "-v"], cwd=ROOT, capture_output=True, text=True)
    (OUT / "testes.txt").write_text(suite.stdout + suite.stderr, encoding="utf-8")
    check("suite_regressao", suite.returncode == 0)
    import re
    total_tests = int(re.search(r"Ran (\d+) tests", suite.stderr).group(1))

    # Não passa pelo leitor/normalizador auditado; nenhum payload é impresso.
    raw = pq.read_table(bp.TRACE).to_pandas().reset_index(drop=True)
    structured = raw.structured_error.map(source_flag)
    suspect = raw.observation_suspect.map(source_flag)
    messages = raw.error_message.map(source_text)
    eligible = structured & messages.notna() & messages.str.len().lt(20000)
    tokens = pd.to_numeric(raw.total_tokens)
    durations = pd.to_numeric(raw.duration_seconds)
    B = bp.carregar_carga()
    A = bp.analisar_sintomas(B)
    M = bp.analisar_mecanismos_observaveis(B, A)
    check("contagens_diretas", len(B.steps) == len(raw) and len(A.E) == int(structured.sum())
          and B.resumo["suspeitas"] == int(suspect.sum()) and len(A.Ee) == int(eligible.sum()))
    check("tokens_diretos", A.E.tok_tot.sum(min_count=1) == tokens[structured].sum(min_count=1))
    check("duracoes_diretas", math.isclose(float(A.E.dur_s.sum(min_count=1)), float(durations[structured].sum(min_count=1))))
    check("sem_duplicacao_n", B.steps.step_ref.is_unique and len(B.RAW) == len(raw))
    check("denominadores_nao_inventados", B.execs[["n_steps", "tok_tot", "dur_s", "tem_final"]].isna().all().all())
    check("suspeitas_fora_taxonomia", set(M.EU.step_ref) == set(B.steps.loc[B.steps.structured_error, "step_ref"]))
    pending = M.EU.situacao_mecanismo.eq("pendente")
    check("pendencias_sem_unidade", M.EU.loc[pending, "unidade"].isna().all())
    check("conservacao_cobertura", M.tabelas["cobertura_mecanismos"].erros.sum() == len(A.E)
          and M.tabelas["cobertura_mecanismos"].tokens_n_conhecidos.sum() == tokens[structured].sum())
    check("conservacao_mecanismos", M.tabelas["mecanismos"].erros.sum() == int((~pending).sum())
          and M.tabelas["custos_mecanismos"].tokens_n_conhecidos.sum() == M.EU.loc[~pending, "tok_tot"].sum())

    direct = reciprocal_links(raw)
    actual = {(int(r.linha_origem), int(r.linha_alvo)): r.estado for r in B.vinculos.itertuples()}
    check("vinculos_recomputados_sem_adaptador", direct == actual)
    eps = M.episodios.episodios
    for definition, mask in [("estruturado", structured), ("misto", structured | suspect)]:
        selected = set(raw.index[mask])
        edges = sum(state == "compativel_candidato" and i in selected and j in selected
                    for (i, j), state in direct.items())
        subset = eps[eps.definicao.eq(definition)]
        check("componentes_diretas_" + definition, len(subset) == len(selected) - edges
              and subset.n_ancoras.sum() == len(selected))
        check("custos_componentes_" + definition,
              subset.tokens_n_conhecidos.sum() == tokens[mask].sum()
              and math.isclose(float(subset.dur_s_n_conhecida.sum()), float(durations[mask].sum())))

    original = ast.parse((ROOT / "analysis/2026-09-trace-law-flow/pipeline/base_pipeline.py").read_text(encoding="utf-8"))
    for name in ["classify", "submecanismo", "sinais_de_parsing", "linha_do_codigo", "linha_rejeitada"]:
        expected = next(n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == name)
        actual_rule = ast.parse(inspect.getsource(getattr(bp, name))).body[0]
        check("regra_preservada_" + name, ast.dump(expected) == ast.dump(actual_rule))

    # Smoke Python: lê código, omite apenas magic gráfica; não escreve notebook.
    nb = json.loads((PIPELINE / "analise_trace_esteira_juridica.ipynb").read_text(encoding="utf-8"))
    namespace = {"display": lambda table: print("Quadro agregado:", table.shape)}
    executed = []
    with (OUT / "smoke_python.txt").open("w", encoding="utf-8") as log, redirect_stdout(log):
        for number, cell in enumerate(nb["cells"], 1):
            if cell["cell_type"] != "code":
                continue
            source = cell["source"]
            # Alguns editores guardam linhas sem quebra; outros seguem nbformat.
            source = "".join(source) if any(s.endswith("\n") for s in source) else "\n".join(source)
            source = "\n".join(line for line in source.splitlines() if line.strip() != "%matplotlib inline")
            compile(source, "celula_" + str(number), "exec")
            if number <= 16:
                exec(source, namespace)
                executed.append(number)
                print("CELULA_CONCLUIDA", number)
            elif number == 18:
                try:
                    exec(source, namespace)
                except bp.AnaliseNaoIntegrada:
                    checks["gate_notebook_3_1"] = True
                    print("GATE_ESPERADO_3_1")
                else:
                    check("gate_notebook_3_1", False)
    check("smoke_trecho_integrado", executed == [2, 4, 6, 8, 10, 12, 14, 16])
    check("smoke_mesma_populacao", namespace["A_mecanismos"].resumo == M.resumo)
    check("custo_mecanismo_no_notebook", namespace["payoff_mec"].erros.sum() == len(M.EU_observavel))
    for name in ["fig_familias", "fig_custos_sintomas", "fig_episodios"]:
        check("grafico_" + name, namespace[name] is not None)
        namespace[name].savefig(OUT / (name + ".png"), dpi=120, bbox_inches="tight")
    plt.close("all")

    baseline = json.loads((PIPELINE / "resultados/etapa7_2026-10-07/baseline.json").read_text(encoding="utf-8"))["arquivos"]
    allowed = {"analysis/2026-10-trace-law-flow-third/pipeline/base_pipeline.py",
               "analysis/2026-10-trace-law-flow-third/pipeline/analise_trace_esteira_juridica.ipynb"}
    changes = [path for path, digest in baseline.items() if not (ROOT / path).is_file() or sha(ROOT / path) != digest]
    check("preservacao_arquivos_anteriores", set(changes) <= allowed)
    check("fonte_inalterada_ao_final", sha(bp.TRACE) == source_sha)
    for name, table in {**A.tabelas, **M.tabelas}.items():
        table.to_csv(OUT / (name + ".csv"), index=False)
    episode_summary = eps.groupby("definicao").agg(
        componentes=("episodio_ref", "size"), ancoras=("n_ancoras", "sum"),
        fechadas_na_definicao=("componente_fechada_na_definicao", "sum"),
        max_ancoras=("n_ancoras", "max"), tokens_n_conhecidos=("tokens_n_conhecidos", "sum"))
    episode_summary.to_csv(OUT / "componentes_agregadas.csv")
    result = {"estado": "integracao_parcial_validada_tecnicamente", "fonte_sha256": source_sha,
              "testes": total_tests, "verificacoes": checks, "sintomas": A.resumo, "mecanismos": M.resumo,
              "tokens_estruturados": int(tokens[structured].sum()),
              "tokens_mecanismos_observaveis": int(M.EU.loc[~pending, "tok_tot"].sum()),
              "tokens_mecanismos_pendentes": int(M.EU.loc[pending, "tok_tot"].sum()),
              "vinculos_diretos_por_estado": dict(Counter(direct.values())),
              "smoke_celulas": executed, "execucao_jupyter_confirmada": False,
              "auditoria_semantica_independente": False,
              "arquivos_anteriores_alterados": changes,
              "bloqueios": ["complemento_A_ou_B_validado", "traces_do_pool_no_mesmo_snapshot",
                            "demais_notebooks_e_skills", "auditoria_semantica_e_gates_do_pesquisador"]}
    (OUT / "validacao.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    print("Validador histórico da Etapa 7: o baseline é anterior à reorganização.")
    print("Não usar para validar a versão atual; use pipeline/executar.py validar ou conferir.")
    print("Reprodução integral requer restaurar o checkout histórico em ambiente separado.")
    raise SystemExit(1)
