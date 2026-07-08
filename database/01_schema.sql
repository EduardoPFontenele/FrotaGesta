
CREATE TABLE motorista (
    id_motorista SERIAL PRIMARY KEY,
    cpf VARCHAR(11) NOT NULL UNIQUE,  
    nome VARCHAR(100) NOT NULL,
    categoria_cnh VARCHAR(2) NOT NULL
        CHECK (categoria_cnh in ('A', 'B', 'C', 'D', 'E', 'AB','AC','AD','AE') )
);

CREATE TABLE veiculo (
    id_veiculo SERIAL PRIMARY KEY,
    placa VARCHAR(7) NOT NULL UNIQUE,
    modelo VARCHAR(100) NOT NULL,
    ano SMALLINT NOT NULL CHECK(ano BETWEEN 1900 AND 2100),
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('CARRO', 'VAN', 'CAMINHAO')),
    km_atual INT NOT NULL DEFAULT 0 CHECK(km_atual >= 0)
);

CREATE TABLE viagem (
    id_viagem SERIAL PRIMARY KEY,
    id_motorista INT NOT NULL,
    id_veiculo INT NOT NULL,
    data_hora_saida TIMESTAMP NOT NULL,
    km_inicial INT NOT NULL CHECK(km_inicial >= 0),
    data_hora_chegada TIMESTAMP,
    km_final INT,
    status VARCHAR(10) NOT NULL DEFAULT 'ABERTA' CHECK( status IN ('ABERTA', 'CONCLUIDA')),
    CONSTRAINT chk_odometro CHECK(km_final IS NULL OR  km_final >= km_inicial ),
    CONSTRAINT fk_id_motorista FOREIGN KEY (id_motorista) REFERENCES motorista(id_motorista),
    CONSTRAINT fk_id_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo)
);

CREATE TABLE abastecimento (
    id_abastecimento SERIAL PRIMARY KEY,
    id_veiculo INT NOT NULL,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    litros NUMERIC(6,2) NOT NULL CHECK(litros >= 0 AND litros <= 300),
    valor_total NUMERIC(10,2) NOT NULL CHECK(valor_total >= 0),
    km_abastecimento INT NOT NULL CHECK(km_abastecimento >= 0),
    CONSTRAINT fk_id_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo)
);

CREATE TABLE tipo_manutencao (
   id_tipo_manutencao SERIAL PRIMARY KEY,
   descricao VARCHAR(100) NOT NULL,
   intervalo_km INT NOT NULL CHECK(intervalo_km > 0) 
);

CREATE TABLE alerta_manutencao(
    id_alerta SERIAL PRIMARY KEY,
    id_veiculo INT NOT NULL,
    id_tipo_manutencao INT NOT NULL,
    km_referencia INT NOT NULL,
    data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    resolvido BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_alerta_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo),
    CONSTRAINT fk_alerta_manutencao FOREIGN KEY (id_tipo_manutencao) REFERENCES tipo_manutencao(id_tipo_manutencao)
);