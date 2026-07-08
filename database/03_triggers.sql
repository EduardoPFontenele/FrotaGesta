-- valida a compatibilidade CNH x tipo de veiculo ao abrir uma viagem
CREATE TRIGGER trg_valida_cnh
    BEFORE INSERT ON viagem
    FOR EACH ROW
    EXECUTE FUNCTION fn_valida_cnh();

-- gera alerta de manutencao quando o odometro do veiculo cruza o limite
CREATE TRIGGER trg_alerta_manutencao
    AFTER UPDATE OF km_atual ON veiculo
    FOR EACH ROW
    EXECUTE FUNCTION fn_gera_alerta_manutencao();