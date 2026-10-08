"""Validação da implementação sem dados reais; não executa Jupyter/Athena.

Grava suite/log, AST das regras históricas e estado da fonte/inventário. Fonte
inválida é bloqueio de execução real, nunca motivo para reutilizar CSV antigo.
"""
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import base_pipeline as bp
import mineracao_observada as mo

ROOT = mo.HERE.parents[2]
OUT = mo.HERE / "resultados" / "validacao_observada_2026-10-07"


def objetos_ast(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8-sig"))
    names = {"classify", "submecanismo", "sinais_de_parsing", "linha_do_codigo", "linha_rejeitada",
             "montar_unidades", "triagem", "triagem_por_papel", "medir_sucesso"}
    catalogs = {"SUB2UNI", "UNI", "DESTINO_MINERACAO"}
    result = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            result[node.name] = ast.dump(node, include_attributes=False)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in catalogs:
                    result[target.id] = ast.dump(node.value, include_attributes=False)
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    validation = {"estado": "em_execucao", "execucao_real": "não realizada",
                  "jupyter_confirmado": False, "auditoria_semantica_independente": False,
                  "gerado_em": datetime.now(timezone.utc).isoformat()}
    path = OUT / "validacao.json"
    path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    suite = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "analysis/tests",
                            "-p", "test_*.py", "-v"], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    (OUT / "testes.txt").write_text(suite.stdout + suite.stderr, encoding="utf-8")
    validation["suite_passou"] = suite.returncode == 0
    count = re.search(r"Ran (\d+) tests", suite.stderr)
    validation["testes"] = int(count.group(1)) if count else None
    baseline = json.loads((mo.HERE / "resultados/etapa7_2026-10-07/baseline.json").read_text(encoding="utf-8"))
    old_code = baseline["notebook"]
    # O baseline guarda o notebook; as células raw anteriores são o registro
    # versionado da regra. Comparar também catálogo com second, sem minerar dados.
    old_pipeline = ROOT / "analysis/2026-09-trace-law-flow-second/pipeline/base_pipeline.py"
    current = objetos_ast(mo.HERE / "base_pipeline.py")
    reference = objetos_ast(old_pipeline)
    equal = {name: current.get(name) == reference.get(name) for name in reference}
    # Guard de montar_unidades/medir_sucesso existe só na third; não tratar
    # proteção de contratos como alteração de taxonomia da second.
    for name in ["montar_unidades", "medir_sucesso"]:
        equal.pop(name, None)
    validation["regras_e_catalogos_ast_second"] = equal
    validation["baseline_notebook_celulas"] = len(old_code["cells"])
    validation["codigo"] = mo.versoes_codigo()
    inventory = mo.inventariar()
    inventory.to_csv(OUT / "inventario.csv", index=False)
    validation["inventario_estados"] = inventory.estado.value_counts().to_dict()
    source = {"sha256": mo.sha256(bp.TRACE), "tamanho_bytes": Path(bp.TRACE).stat().st_size}
    historical = json.loads((mo.HERE / "resultados/validacao_fechamento_2026-10-07/validacao.json").read_text(encoding="utf-8"))
    source["igual_validacao_historica"] = source["sha256"] == historical.get("fonte_sha256")
    try:
        source.update(mo.conferir_fonte(bp.TRACE))
        source["parquet_abre"] = True
    except bp.AnaliseNaoIntegrada:
        source["parquet_abre"] = False
    validation["fonte_intake"] = source
    validation["execucao_real"] = "bloqueada_restaurar_ou_validar_fonte" if not source["parquet_abre"] else "não realizada nesta validação"
    validation["estado"] = "implementacao_validada_sinteticamente" if suite.returncode == 0 and all(equal.values()) else "falhou"
    path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ["estado", "testes", "execucao_real", "regras_e_catalogos_ast_second"]},
                     ensure_ascii=False, indent=2))
    return 0 if validation["estado"] == "implementacao_validada_sinteticamente" else 1


if __name__ == "__main__":
    raise SystemExit(main())
