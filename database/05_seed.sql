-- ============ SEED - dados minimos para teste ============

-- Regra de manutencao: troca de oleo a cada 10.000 km
INSERT INTO tipo_manutencao (descricao, intervalo_km) VALUES
    ('Troca de oleo', 10000);

-- Motoristas: um com CNH D (dirige tudo), um com CNH B (nao dirige caminhao)
INSERT INTO motorista (cpf, nome, categoria_cnh) VALUES
    ('11111111111', 'Joao Motorista D', 'D'),
    ('22222222222', 'Maria Motorista B', 'B');

-- Veiculos: um carro e um caminhao.
-- O carro comeca com km_atual = 9800 (perto do limite de 10.000, para testar o alerta)
INSERT INTO veiculo (placa, modelo, ano, tipo, km_atual) VALUES
    ('ABC1234', 'Fiat Uno',    2020, 'CARRO',    9800),
    ('CAM0001', 'Volvo FH',    2019, 'CAMINHAO', 5000);

-- Uma viagem ABERTA para o carro (id_veiculo=1), motorista D (id_motorista=1),
-- comecando em 9800 (coerente com o km_atual do veiculo)
INSERT INTO viagem (id_motorista, id_veiculo, data_hora_saida, km_inicial) VALUES
    (1, 1, CURRENT_TIMESTAMP, 9800);