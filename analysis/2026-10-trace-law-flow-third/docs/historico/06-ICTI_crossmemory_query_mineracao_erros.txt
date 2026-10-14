-- TRANSCRIÇÃO das fotos da query `ICTI_crossmemory_query_mineracao_erros` (máquina 2), 09/10/2026.
-- Fiel às fotos; onde a foto não deixou ler, `-- [linhas N–M não visíveis]`.
-- Registro histórico da extração v1 da base 3 — não é a query de um pedido novo (ver ../05-pedido-queries.md).
-- Lacunas: linhas 146–147 e 805–816 (o limite e o alias de `action_output` não aparecem nas fotos).
-- Lido até aqui: a query inteira (linhas 1–1015, fotos IMG_5276 a IMG_5306 e IMG_5395). Lacunas marcadas no texto: linhas 146–147 e 805–816.

WITH source_raw AS (

    SELECT
        cod_idef_aget,
        cod_idef_exeo,
        cod_idef_stat_exeo_aget,
        cod_idef_cvsa_asnc,
        dat_hor_encm_exeo,
        txt_vrvl_locl,
        txt_rspa_fina,
        dat_hor_inio_exeo,
        cod_vers_aget,
        txt_etap_memo,
        anomesdia,

        -- ROW_NUMBER() OVER (
        --     PARTITION BY
        --         cod_idef_exeo,
        --         cod_idef_aget
        --     ORDER BY
        --         anomesdia DESC
        -- ) AS rn
        ROW_NUMBER() OVER (
            PARTITION BY cod_idef_exeo, cod_idef_aget
            ORDER BY
                anomesdia DESC,
                CASE
                    WHEN dat_hor_encm_exeo IS NOT NULL
                    AND TRIM(dat_hor_encm_exeo) <> ''
                    THEN 1
                    ELSE 0
                END DESC,
                LENGTH(txt_etap_memo) DESC
        ) AS rn

    FROM db_corp_juridico_joogle_sor_01.tbnm9100_exeo_aget

    -- ==================================================================
    -- IMPORTANTE:
    --
    -- limite sempre as partições lidas.
    --
    -- Se uma única partição recente já contém todo o snapshot
    -- histórico, prefira:
    --
    --     WHERE anomesdia = 202609XX
    --
    -- Se precisar juntar várias:
    -- ==================================================================

    WHERE anomesdia BETWEEN 20250801 AND 20260930

        AND txt_etap_memo IS NOT NULL
        AND TRIM(txt_etap_memo) <> ''
        AND (length(txt_vrvl_locl) + length(txt_rspa_fina) + length(txt_etap_memo) < 30000000)
),


-- ==================================================================
-- Mantém apenas a versão mais recente da execução dentro do intervalo
-- analisado e tenta converter a memória em:
--
-- MAP<
--     papel,
--     ARRAY<step>
-- >
--
-- TRY protege tanto JSON inválido quanto estrutura inesperada.
-- ==================================================================

base AS (

    SELECT
        cod_idef_aget,
        cod_idef_exeo,
        cod_idef_stat_exeo_aget,
        cod_idef_cvsa_asnc,
        dat_hor_encm_exeo,
        dat_hor_inio_exeo,
        cod_vers_aget,
        anomesdia,

        CASE
            WHEN txt_vrvl_locl IS NOT NULL
            AND TRIM(txt_vrvl_locl) <> ''
            THEN 1
            ELSE 0
        END AS has_final_locals,

        CASE
            WHEN txt_rspa_fina IS NOT NULL
            AND TRIM(txt_rspa_fina) <> ''
            THEN 1
            ELSE 0
        END AS has_persisted_response,

        TRY(
            CAST(
                JSON_PARSE(txt_etap_memo)
                AS MAP(VARCHAR, ARRAY(JSON))
            )
        ) AS trace_map

    FROM source_raw

    WHERE rn = 1
),


-- ==================================================================
-- Explode:
--
-- {
--   "managerAgent": [...],
--   "ConversationAgent": [...],
--   ...
-- }
--
-- em uma linha por papel.
-- ==================================================================

roles AS (

    SELECT
        b.cod_idef_aget,
        b.cod_idef_exeo,
        b.cod_idef_stat_exeo_aget,
        b.cod_idef_cvsa_asnc,
        b.dat_hor_encm_exeo,
        b.dat_hor_inio_exeo,
        b.cod_vers_aget,
        b.anomesdia,
        b.has_final_locals,
        b.has_persisted_response,

        COALESCE(
            NULLIF(TRIM(papel), ''),
            '<SEM_PAPEL>'
        ) AS papel,

        steps

    FROM base b

    CROSS JOIN UNNEST(b.trace_map)
    -- [linhas 146–147 não visíveis nas fotos]
    WHERE b.trace_map IS NOT NULL
),


-- ==================================================================
-- Explode cada lista de steps.
--
-- WITH ORDINALITY preserva a ordem REAL do trace.
-- ==================================================================

raw_steps AS (

    SELECT
        cod_idef_aget,
        cod_idef_exeo,
        cod_idef_stat_exeo_aget,
        cod_idef_cvsa_asnc,
        dat_hor_encm_exeo,
        dat_hor_inio_exeo,
        cod_vers_aget,
        anomesdia,

        has_final_locals,
        has_persisted_response,

        papel,

        CAST(step_pos AS INTEGER)
            AS step_pos,

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.__class__'
        ) AS step_class,

        TRY_CAST(
            JSON_EXTRACT_SCALAR(
                step_json,
                '$.step_number'
            )
            AS INTEGER
        ) AS step_number,


        -- ----------------------------------------------------------
        -- Conteúdo do ActionStep
        -- ----------------------------------------------------------

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.model_output'
        ) AS model_output,

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.code_action'
        ) AS code_action,

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.observations'
        ) AS observations,

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.action_output'
        ) AS action_output,


        -- ----------------------------------------------------------
        -- Erro estruturado
        -- ----------------------------------------------------------

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.error.type'
        ) AS error_type,

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.error.message'
        ) AS error_message,


        -- ----------------------------------------------------------
        -- Finalização
        -- ----------------------------------------------------------

        TRY_CAST(
            JSON_EXTRACT_SCALAR(
                step_json,
                '$.is_final_answer'
            )
            AS BOOLEAN
        ) AS is_final_answer,


        -- ----------------------------------------------------------
        -- Tokens
        -- ----------------------------------------------------------

        TRY_CAST(
            JSON_EXTRACT_SCALAR(
                step_json,
                '$.token_usage.input_tokens'
            )
            AS BIGINT
        ) AS input_tokens,

        TRY_CAST(
            JSON_EXTRACT_SCALAR(
                step_json,
                '$.token_usage.output_tokens'
            )
            AS BIGINT
        ) AS output_tokens,

        TRY_CAST(
            JSON_EXTRACT_SCALAR(
                step_json,
                '$.token_usage.total_tokens'
            )
            AS BIGINT
        ) AS total_tokens,


        -- ----------------------------------------------------------
        -- Timing
        -- ----------------------------------------------------------

        TRY_CAST(
            JSON_EXTRACT_SCALAR(
                step_json,
                '$.timing.duration'
            )
            AS DOUBLE
        ) AS duration_seconds,


        -- ----------------------------------------------------------
        -- Ferramenta chamada
        --
        -- Mantemos o nome da primeira tool separadamente.
        -- É muito mais barato de analisar depois do que o JSON inteiro.
        -- ----------------------------------------------------------

        JSON_EXTRACT_SCALAR(
            step_json,
            '$.tool_calls[0].function.name'
        ) AS tool_name,

        JSON_FORMAT(
            JSON_EXTRACT(
                step_json,
                '$.tool_calls'
            )
        ) AS tool_calls

    FROM roles

    CROSS JOIN UNNEST(steps)
        WITH ORDINALITY AS s(step_json, step_pos)
),


-- ==================================================================
-- Apenas ActionSteps.
--
-- Assim:
--
-- n-1 / n+1 / n+2
--
-- representam ações do agente, e não TaskStep/PlanningStep.
-- ==================================================================

action_steps AS (

    SELECT
        *

    FROM raw_steps

    WHERE step_class = 'ActionStep'
),


-- ==================================================================
-- Sinais de erro
--
-- structured_error:
--     erro marcado oficialmente no campo error
--
-- observation_suspect:
--     error = null, porém observations contém uma assinatura forte
--     de falha.
--
-- IMPORTANTE:
-- observation_suspect NÃO deve ser misturado nas métricas oficiais
-- da taxonomia sem validação.
-- ==================================================================

classified AS (

    SELECT
        *,

        CASE
            WHEN error_type IS NOT NULL
            THEN 1
            ELSE 0
        END AS structured_error,


        CASE
            WHEN error_type IS NULL

            AND REGEXP_LIKE(
                COALESCE(observations, ''),
                '(?i)'
                || 'input validation error'
                || '|code execution failed'
                || '|interpretererror'
                || '|agentexecutionerror'
                || '|validationerror'
                || '|traceback \(most recent call last\)'
            )

            THEN 1
            ELSE 0
        END AS observation_suspect

    FROM action_steps
),


flags AS (

    SELECT
        *,

        CASE
            WHEN structured_error = 1
            OR observation_suspect = 1
            THEN 1
            ELSE 0
        END AS error_like

    FROM classified
),


-- ==================================================================
-- Contexto temporal do ActionStep
--
-- IMPORTANTE:
-- LAG/LEAD são calculados ANTES de filtrar os erros.
--
-- Caso contrário:
--   LEAD() apontaria para o próximo ERRO,
-- e não para a próxima ação.
-- ==================================================================

step_context AS (

    SELECT
        *,


        -- ==========================================================
        -- n - 1
        -- ==========================================================

        LAG(step_number, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS prev_step_number,

        LAG(model_output, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS prev_model_output,

        LAG(code_action, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS prev_code_action,

        LAG(observations, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS prev_observations,

        LAG(error_type, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS prev_error_type,

        LAG(error_like, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS prev_error_like,


        -- ==========================================================
        -- n + 1
        -- ==========================================================

        LEAD(step_number, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_step_number,

        LEAD(model_output, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_model_output,

        LEAD(code_action, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_code_action,

        LEAD(observations, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_observations,

        LEAD(error_type, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_error_type,

        LEAD(error_like, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_error_like,

        LEAD(is_final_answer, 1) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next_is_final_answer,


        -- ==========================================================
        -- n + 2
        -- ==========================================================

        LEAD(step_number, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_step_number,

        LEAD(model_output, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_model_output,

        LEAD(code_action, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_code_action,

        LEAD(observations, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_observations,

        LEAD(error_type, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_error_type,

        LEAD(error_like, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_error_like,

        LEAD(is_final_answer, 2) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
            ORDER BY
                step_pos
        ) AS next2_is_final_answer,


        -- ==========================================================
        -- CUSTO / ERRO DO N + 1
        -- ==========================================================

        LEAD(error_message, 1) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next_error_message,

        LEAD(tool_name, 1) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next_tool_name,

        LEAD(input_tokens, 1) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next_input_tokens,

        LEAD(output_tokens, 1) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next_output_tokens,

        LEAD(total_tokens, 1) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next_total_tokens,

        LEAD(duration_seconds, 1) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next_duration_seconds,


        -- ==========================================================
        -- CUSTO / ERRO DO N + 2
        -- ==========================================================

        LEAD(error_message, 2) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next2_error_message,

        LEAD(tool_name, 2) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next2_tool_name,

        LEAD(input_tokens, 2) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next2_input_tokens,

        LEAD(output_tokens, 2) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next2_output_tokens,

        LEAD(total_tokens, 2) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next2_total_tokens,

        LEAD(duration_seconds, 2) OVER (
            PARTITION BY cod_idef_exeo, papel
            ORDER BY step_pos
        ) AS next2_duration_seconds,



        -- ==========================================================
        -- A execução chegou a algum final_answer depois?
        --
        -- Aqui não estamos dizendo que o erro foi corrigido;
        -- apenas que o papel conseguiu chegar a um ActionStep final.
        -- ==========================================================

        MAX(
            CASE
                WHEN is_final_answer = TRUE
                THEN 1
                ELSE 0
            END
        ) OVER (
            PARTITION BY
                cod_idef_exeo,
                papel
        ) AS execution_has_final_step

    FROM flags
),


-- ==================================================================
-- Somente episódios potencialmente relevantes para mineração.
-- ==================================================================

errors_only AS (

    SELECT
        *

    FROM step_context

    WHERE structured_error = 1
        OR observation_suspect = 1
)


SELECT

    -- ==============================================================
    -- IDENTIFICAÇÃO DA EXECUÇÃO
    -- ==============================================================

    cod_idef_exeo,
    cod_idef_aget,
    papel,

    cod_idef_stat_exeo_aget,
    cod_idef_cvsa_asnc,
    cod_vers_aget,

    dat_hor_inio_exeo,
    dat_hor_encm_exeo,

    SUBSTR(
        dat_hor_inio_exeo,
        1,
        7
    ) AS mes_execucao,


    -- ==============================================================
    -- INDICADORES DA EXECUÇÃO
    -- ==============================================================

    has_final_locals,
    has_persisted_response,
    execution_has_final_step,


    -- ==============================================================
    -- ORIGEM DO SINAL DE ERRO
    -- ==============================================================

    CASE
        WHEN structured_error = 1
        THEN 'STRUCTURED_ERROR'

        WHEN observation_suspect = 1
        THEN 'OBSERVATION_SUSPECT'
    END AS error_source,

    structured_error,
    observation_suspect,


    -- ==============================================================
    -- STEP N — ERRO
    -- ==============================================================

    step_number,
    step_pos,

    error_type,

    SUBSTR(
        error_message,
        1,
        20000
    ) AS error_message,

    tool_name,

    SUBSTR(
        tool_calls,
        1,
        12000
    ) AS tool_calls,

    SUBSTR(
        model_output,
        1,
        12000
    ) AS error_model_output,

    SUBSTR(
        code_action,
        1,
        12000
    ) AS error_code_action,

    SUBSTR(
        observations,
        1,
        20000
    ) AS error_observations,

    -- [linhas 805–816 só em parte visíveis: começa `SUBSTR(action_output, 1, …` — o limite e o alias não aparecem nas fotos]


    -- ==============================================================
    -- STEP N - 1
    -- ==============================================================

    prev_step_number,

    SUBSTR(
        prev_model_output,
        1,
        8000
    ) AS prev_model_output,

    SUBSTR(
        prev_code_action,
        1,
        8000
    ) AS prev_code_action,

    SUBSTR(
        prev_observations,
        1,
        12000
    ) AS prev_observations,

    prev_error_type,
    prev_error_like,


    -- ==============================================================
    -- STEP N + 1
    -- ==============================================================

    next_step_number,

    SUBSTR(
        next_model_output,
        1,
        12000
    ) AS next_model_output,

    SUBSTR(
        next_code_action,
        1,
        12000
    ) AS next_code_action,

    SUBSTR(
        next_observations,
        1,
        16000
    ) AS next_observations,

    next_error_type,
    next_error_like,
    next_is_final_answer,

    SUBSTR(
        next_error_message,
        1,
        20000
    ) AS next_error_message,

    next_tool_name,
    next_input_tokens,
    next_output_tokens,
    next_total_tokens,
    next_duration_seconds,


    -- ==============================================================
    -- STEP N + 2
    -- ==============================================================

    next2_step_number,

    SUBSTR(
        next2_model_output,
        1,
        12000
    ) AS next2_model_output,

    SUBSTR(
        next2_code_action,
        1,
        12000
    ) AS next2_code_action,

    SUBSTR(
        next2_observations,
        1,
        16000
    ) AS next2_observations,

    next2_error_type,
    next2_error_like,
    next2_is_final_answer,

    SUBSTR(
        next2_error_message,
        1,
        20000
    ) AS next2_error_message,

    next2_tool_name,
    next2_input_tokens,
    next2_output_tokens,
    next2_total_tokens,
    next2_duration_seconds,


    -- ==============================================================
    -- SINAL DE RECUPERAÇÃO
    --
    -- Deliberadamente conservador.
    --
    -- "sem erro no próximo step" não significa necessariamente
    -- que o problema original foi resolvido.
    -- ==============================================================

    CASE

        WHEN next_step_number IS NULL
        THEN 'NO_NEXT_ACTION'


        WHEN next_error_like = 0
        AND next_is_final_answer = TRUE
        THEN 'RECOVERED_TO_FINAL_NEXT_ACTION'


        WHEN next_error_like = 1
        AND next2_error_like = 0
        AND next2_is_final_answer = TRUE
        THEN 'RECOVERED_TO_FINAL_WITHIN_2_ACTIONS'


        WHEN next_error_like = 0
        THEN 'POSSIBLE_RECOVERY_NEXT_ACTION'


        WHEN next_error_like = 1
        AND next2_error_like = 0
        THEN 'POSSIBLE_RECOVERY_WITHIN_2_ACTIONS'


        WHEN next_error_like = 1
        AND next2_error_like = 1
        THEN 'ERROR_CASCADE'


        ELSE 'UNKNOWN'

    END AS recovery_signal,

    -- custo do step que falhou + próxima ação
    COALESCE(total_tokens, 0)
        + COALESCE(next_total_tokens, 0)
        AS tokens_error_plus_next_action,

    COALESCE(duration_seconds, 0)
        + COALESCE(next_duration_seconds, 0)
        AS seconds_error_plus_next_action,


    -- custo do erro + janela completa de recuperação observada
    COALESCE(total_tokens, 0)
        + COALESCE(next_total_tokens, 0)
        + COALESCE(next2_total_tokens, 0)
        AS tokens_error_plus_next_2_actions,

    COALESCE(duration_seconds, 0)
        + COALESCE(next_duration_seconds, 0)
        + COALESCE(next2_duration_seconds, 0)
        AS seconds_error_plus_next_2_actions,

    CASE
        WHEN next_step_number IS NULL THEN 0
        WHEN next2_step_number IS NULL THEN 1
        ELSE 2
    END AS num_actions_after_error_observed,

    CASE
        WHEN next2_step_number IS NOT NULL THEN 1
        ELSE 0
    END AS has_full_2_action_window,


    -- ==============================================================
    -- TEM QUE FICAR POR ÚLTIMO
    --
    -- Athena exige que colunas usadas em partitioned_by apareçam
    -- no fim do SELECT do CTAS.
    -- ==============================================================
    anomesdia

FROM errors_only
ORDER BY cod_idef_exeo, papel, step_pos;
