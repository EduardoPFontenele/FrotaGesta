
INSERT INTO tipo_manutencao (descricao, intervalo_km) VALUES
    ('Troca de óleo',       10000),
    ('Pastilhas de freio',  20000),
    ('Revisão geral',       30000),
    ('Outro',              999999);

INSERT INTO motorista (cpf, nome, categoria_cnh) VALUES
    ('11122233344', 'João da Silva',         'D'),
    ('22233344455', 'Maria Oliveira',        'B'),
    ('33344455566', 'Carlos Eduardo Souza',  'E'),
    ('44455566677', 'Ana Paula Santos',      'B'),
    ('55566677788', 'Pedro Henrique Costa',  'D'),
    ('66677788899', 'Lucas Pereira Lima',    'C');

INSERT INTO veiculo (placa, modelo, ano, tipo, km_atual) VALUES
    ('JKL5678', 'Volvo FH 460',   2019, 'CAMINHAO', 45000),
    ('JKM1122', 'Scania R450',    2020, 'CAMINHAO', 98500),
    ('RST2233', 'Fiat Ducato',    2021, 'VAN',      30000),
    ('RSU4455', 'Renault Master', 2018, 'VAN',      61000),
    ('ABC1234', 'Toyota Corolla', 2022, 'CARRO',    15000),
    ('ABD5566', 'Volkswagen Gol', 2020, 'CARRO',     9800);

INSERT INTO viagem (id_motorista, id_veiculo, data_hora_saida, km_inicial,
                    data_hora_chegada, km_final, status) VALUES
    (1, 1, '2026-06-10 08:00', 40000, '2026-06-10 18:00', 45000, 'CONCLUIDA'),
    (3, 2, '2026-06-15 07:00', 95000, '2026-06-16 20:00', 98500, 'CONCLUIDA'),
    (2, 5, '2026-07-01 09:00', 14000, '2026-07-01 12:00', 15000, 'CONCLUIDA');

-- ABERTA (veiculo 3 fica "Em rota"); motorista 5 tem CNH D
INSERT INTO viagem (id_motorista, id_veiculo, data_hora_saida, km_inicial) VALUES
    (5, 3, '2026-07-08 06:30', 30000);

INSERT INTO abastecimento (id_veiculo, data_hora, litros, valor_total, km_abastecimento) VALUES
    (1, '2026-06-10 12:00', 180.00, 1080.00, 43000),
    (3, '2026-07-08 06:00',  75.50,  453.00, 29800),
    (5, '2026-06-30 17:30',  42.00,  294.00, 13800);

INSERT INTO alerta_manutencao (id_veiculo, id_tipo_manutencao, km_referencia) VALUES
    (2, 2, 98000);
