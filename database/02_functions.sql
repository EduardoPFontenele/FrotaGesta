CREATE OR REPLACE FUNCTION status_veiculo(p_id_veiculo INT)
RETURNS VARCHAR AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM alerta_manutencao
               WHERE id_veiculo = p_id_veiculo AND resolvido = FALSE) THEN
        RETURN 'MANUTENCAO';
    END IF;

    IF EXISTS (SELECT 1 FROM viagem
               WHERE id_veiculo = p_id_veiculo AND status = 'ABERTA') THEN
        RETURN 'EM_ROTA';
    END IF;

    RETURN 'DISPONIVEL';
END;
$$ LANGUAGE plpgsql;

-- Funcoes utilizadas pelos triggers
CREATE OR REPLACE FUNCTION fn_valida_cnh()
RETURNS TRIGGER AS $$
DECLARE
    v_categoria VARCHAR(2);
    v_tipo      VARCHAR(10);
BEGIN

    SELECT categoria_cnh INTO v_categoria
    FROM motorista
    WHERE id_motorista = NEW.id_motorista;

    SELECT tipo INTO v_tipo
    FROM veiculo
    WHERE id_veiculo = NEW.id_veiculo;

    IF v_tipo = 'CAMINHAO' AND v_categoria NOT IN ('D', 'E') THEN
        RAISE EXCEPTION
            'Motorista com CNH categoria % nao pode dirigir CAMINHAO (exige D ou E)',
            v_categoria;
    END IF;

    RETURN NEW; 
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_gera_alerta_manutencao()
RETURNS TRIGGER AS $$
DECLARE
    v_tipo RECORD;
BEGIN

    FOR v_tipo IN SELECT id_tipo_manutencao, intervalo_km FROM tipo_manutencao
    LOOP
        IF FLOOR(NEW.km_atual / v_tipo.intervalo_km) > FLOOR(OLD.km_atual / v_tipo.intervalo_km) THEN
            -- verifica se já tem pendencia desse tipo de manutencao
            IF NOT EXISTS (
                SELECT 1 FROM alerta_manutencao
                WHERE id_veiculo = NEW.id_veiculo
                  AND id_tipo_manutencao = v_tipo.id_tipo_manutencao
                  AND resolvido = FALSE
            )
             THEN
                INSERT INTO alerta_manutencao (id_veiculo, id_tipo_manutencao, km_referencia)
                VALUES (NEW.id_veiculo, v_tipo.id_tipo_manutencao, NEW.km_atual);
            END IF;

        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;