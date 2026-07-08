CREATE OR REPLACE PROCEDURE encerrar_viagem(
IN    p_id_viagem         INT,
IN    p_km_final          INT,
IN    p_data_hora_chegada TIMESTAMP DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_km_inicial INT;
    v_id_veiculo INT;
    v_status VARCHAR(10);
BEGIN
    -- busca os dados da viagem que sera encerrada
    SELECT km_inicial, id_veiculo, status
    INTO v_km_inicial, v_id_veiculo, v_status
    FROM viagem
    WHERE id_viagem = p_id_viagem;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Viagem % nao encontrada', p_id_viagem;
    END IF;

    IF v_status = 'CONCLUIDA' THEN
        RAISE EXCEPTION 'Viagem % ja foi encerrada', p_id_viagem;
    END IF;

    -- valida coerencia do odometro
    IF p_km_final < v_km_inicial THEN
        RAISE EXCEPTION 'Km final (%) nao pode ser menor que o inicial (%)',
            p_km_final, v_km_inicial;
    END IF;

    -- atualiza a viagem: status, km final e data de chegada
    -- (usa a data informada; se vier NULL, cai no momento atual)
    UPDATE viagem
    SET status = 'CONCLUIDA',
        km_final = p_km_final,
        data_hora_chegada = COALESCE(p_data_hora_chegada, CURRENT_TIMESTAMP)
    WHERE id_viagem = p_id_viagem;

    -- atualiza o odometro do veiculo
    UPDATE veiculo
    SET km_atual = p_km_final
    WHERE id_veiculo = v_id_veiculo;

END;
$$;