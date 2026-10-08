-- Quantas execuções a query v1 perde no filtro de tamanho, e por quê. Só contagens; roda no Athena.
-- Mesmo período e mesma condição de memória da v1. Uma execução (exec + agente) "passa" se algum snapshot dela
-- passa no filtro — como no source_raw da v1, que filtra antes de escolher o snapshot.
-- No filtro, length(NULL) é NULL: a soma vira NULL e a linha sai. COALESCE(..., FALSE) reproduz isso.
WITH snapshots AS (
    SELECT
        cod_idef_exeo,
        cod_idef_aget,
        COALESCE(LENGTH(txt_vrvl_locl) + LENGTH(txt_rspa_fina) + LENGTH(txt_etap_memo) < 30000000, FALSE) AS passa,
        txt_rspa_fina IS NULL AS resposta_null,
        txt_rspa_fina IS NOT NULL AND TRIM(txt_rspa_fina) = '' AS resposta_vazia,
        txt_vrvl_locl IS NULL AS locais_null,
        txt_vrvl_locl IS NOT NULL AND TRIM(txt_vrvl_locl) = '' AS locais_vazio
    FROM db_corp_juridico_joogle_sor_01.tbnm9100_exeo_aget
    WHERE anomesdia BETWEEN 20250801 AND 20260930
      AND txt_etap_memo IS NOT NULL
      AND TRIM(txt_etap_memo) <> ''
),
execucoes AS (
    SELECT
        cod_idef_exeo,
        cod_idef_aget,
        BOOL_OR(passa) AS passa,
        BOOL_AND(resposta_null) AS resposta_sempre_null,
        BOOL_AND(locais_null) AS locais_sempre_null,
        BOOL_OR(resposta_vazia) AS alguma_resposta_vazia,
        BOOL_OR(locais_vazio) AS algum_locais_vazio
    FROM snapshots
    GROUP BY cod_idef_exeo, cod_idef_aget
)
SELECT
    COUNT(*)                                              AS execucoes_no_periodo,
    COUNT_IF(passa)                                       AS execucoes_que_passam,
    COUNT_IF(NOT passa)                                   AS execucoes_cortadas,
    COUNT_IF(NOT passa AND resposta_sempre_null)          AS cortadas_resposta_null,
    COUNT_IF(NOT passa AND locais_sempre_null)            AS cortadas_locais_null,
    COUNT_IF(NOT passa AND NOT resposta_sempre_null
             AND NOT locais_sempre_null)                  AS cortadas_outro_motivo,
    COUNT_IF(alguma_resposta_vazia)                       AS execucoes_com_resposta_vazia,
    COUNT_IF(algum_locais_vazio)                          AS execucoes_com_locais_vazio
FROM execucoes;
