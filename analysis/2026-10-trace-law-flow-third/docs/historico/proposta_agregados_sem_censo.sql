-- PROPOSTA, não executada no Athena. Somente SELECT; nenhum destino S3/DDL.
-- Calcula denominadores no servidor sem exportar ActionSteps/payloads/IDs.
-- Preservar materialização/snapshot da query original e conferir metadados.
-- Agregação reduz transferência, não garante redução do custo de parse.
WITH entrada AS (
    SELECT cod_idef_aget, cod_idef_exeo, dat_hor_encm_exeo,
           dat_hor_inio_exeo, cod_vers_aget, txt_etap_memo,
           txt_vrvl_locl, txt_rspa_fina, anomesdia
    FROM db_corp_juridico_joogle_sor_01.tbnm9100_exeo_aget
    WHERE anomesdia BETWEEN 20250801 AND 20260930
), source_raw AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY cod_idef_exeo, cod_idef_aget
        ORDER BY anomesdia DESC,
                 CASE WHEN dat_hor_encm_exeo IS NOT NULL AND TRIM(dat_hor_encm_exeo) <> '' THEN 1 ELSE 0 END DESC,
                 LENGTH(txt_etap_memo) DESC
    ) AS rn
    FROM entrada
    WHERE txt_etap_memo IS NOT NULL AND TRIM(txt_etap_memo) <> ''
      -- Intencional: NULL exclui como no SQL produtor; não corrigir coorte aqui.
      AND (LENGTH(txt_vrvl_locl) + LENGTH(txt_rspa_fina) + LENGTH(txt_etap_memo) < 30000000)
), base AS (
    SELECT *, TRY(CAST(JSON_PARSE(txt_etap_memo) AS MAP(VARCHAR, ARRAY(JSON)))) AS trace_map
    FROM source_raw WHERE rn = 1
), roles AS (
    SELECT cod_idef_exeo, cod_idef_aget, SUBSTR(dat_hor_inio_exeo, 1, 7) AS mes_execucao,
           cod_vers_aget, COALESCE(NULLIF(TRIM(papel), ''), '<SEM_PAPEL>') AS papel, steps
    FROM base CROSS JOIN UNNEST(trace_map) AS r(papel, steps)
    WHERE trace_map IS NOT NULL
), raw_steps AS (
    SELECT cod_idef_exeo, cod_idef_aget, mes_execucao, cod_vers_aget, papel,
           JSON_EXTRACT_SCALAR(step_json, '$.__class__') AS step_class,
           JSON_EXTRACT_SCALAR(step_json, '$.error.type') AS error_type,
           JSON_EXTRACT_SCALAR(step_json, '$.observations') AS observations,
           TRY_CAST(JSON_EXTRACT_SCALAR(step_json, '$.token_usage.input_tokens') AS BIGINT) AS input_tokens,
           TRY_CAST(JSON_EXTRACT_SCALAR(step_json, '$.token_usage.output_tokens') AS BIGINT) AS output_tokens,
           TRY_CAST(JSON_EXTRACT_SCALAR(step_json, '$.token_usage.total_tokens') AS BIGINT) AS total_tokens,
           TRY_CAST(JSON_EXTRACT_SCALAR(step_json, '$.timing.duration') AS DOUBLE) AS duration_seconds
    FROM roles CROSS JOIN UNNEST(steps) WITH ORDINALITY AS s(step_json, step_pos)
), actions AS (
    SELECT *, CASE
        WHEN error_type IS NOT NULL THEN 'STRUCTURED_ERROR'
        WHEN REGEXP_LIKE(COALESCE(observations, ''), '(?i)'
             || 'input validation error|code execution failed|interpretererror|agentexecutionerror'
             || '|validationerror|traceback \(most recent call last\)') THEN 'OBSERVATION_SUSPECT'
        ELSE 'NO_ERROR_SIGNAL' END AS error_source
    FROM raw_steps WHERE step_class = 'ActionStep'
), quality AS (
    SELECT (SELECT COUNT(*) FROM entrada) AS registros_entrada_particoes,
           (SELECT COUNT(*) FROM source_raw) AS snapshots_elegiveis_antes_rank,
           COUNT(*) AS snapshots_selecionados,
           COUNT_IF(trace_map IS NULL) AS traces_incompativeis_ou_invalidos,
           (SELECT COUNT_IF(step_class = 'TaskStep') FROM raw_steps) AS tasksteps,
           (SELECT COUNT_IF(step_class = 'PlanningStep') FROM raw_steps) AS planningsteps
    FROM base
), summary AS (
    SELECT GROUPING(mes_execucao) AS agregado_mes,
           GROUPING(papel) AS agregado_papel,
           GROUPING(cod_vers_aget) AS agregado_versao,
           GROUPING(error_source) AS agregado_canal,
           mes_execucao, papel, cod_vers_aget, error_source,
           COUNT(*) AS actionsteps,
           COUNT(DISTINCT ROW(cod_idef_exeo, cod_idef_aget)) AS execucoes_representadas_no_grupo,
           SUM(input_tokens) AS input_tokens_conhecidos,
           COUNT_IF(input_tokens IS NULL) AS input_tokens_ausentes,
           SUM(output_tokens) AS output_tokens_conhecidos,
           COUNT_IF(output_tokens IS NULL) AS output_tokens_ausentes,
           SUM(total_tokens) AS total_tokens_conhecidos,
           COUNT_IF(total_tokens IS NULL) AS total_tokens_ausentes,
           SUM(duration_seconds) AS duration_seconds_conhecidos,
           COUNT_IF(duration_seconds IS NULL) AS duration_seconds_ausentes
    FROM actions
    GROUP BY GROUPING SETS ((mes_execucao, papel, cod_vers_aget, error_source), (error_source), ())
)
SELECT 'agregados_sem_censo_v1_proposta' AS extraction_contract, summary.*, quality.*
FROM summary CROSS JOIN quality;
-- As linhas GROUPING SETS se sobrepõem: não somar níveis diferentes.
-- quality é repetida: não somar suas colunas. Execuções dos canais se sobrepõem.
-- Sem mediana/Lorenz/sucesso: estes exigem agregações adicionais específicas.
