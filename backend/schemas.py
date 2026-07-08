from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class MotoristaCreate(BaseModel):
    cpf: str = Field(min_length=11, max_length=11)
    nome: str
    # O front envia uma ou mais categorias; o backend reduz para a maior
    # (a CNH e hierarquica: quem tem D dirige o que B dirige).
    categoria_cnh: List[str] = Field(min_length=1)


class MotoristaResponse(BaseModel):
    id_motorista: int
    cpf: str
    nome: str
    categoria_cnh: str


class VeiculoCreate(BaseModel):
    placa: str
    modelo: str
    ano: int
    tipo: str            
    km_atual: int = 0    


class VeiculoResponse(BaseModel):
    id_veiculo: int
    placa: str
    modelo: str
    ano: int
    tipo: str
    km_atual: int

class ViagemCreate(BaseModel):
    id_motorista: int
    id_veiculo: int
    km_inicial: int
    data_hora_saida: Optional[datetime] = None  # se nao vier, o banco usa CURRENT_TIMESTAMP

class ViagemEncerrar(BaseModel):
    km_final: int
    data_hora_chegada: Optional[datetime] = None  # se nao vier, o banco usa CURRENT_TIMESTAMP


class ViagemResponse(BaseModel):
    id_viagem: int
    id_motorista: int
    id_veiculo: int
    data_hora_saida: datetime
    km_inicial: int
    data_hora_chegada: Optional[datetime]   
    km_final: Optional[int]                  
    status: str

class AlertaCreate(BaseModel):
    id_veiculo: int
    id_tipo_manutencao: int

class AbastecimentoCreate(BaseModel):
    id_veiculo: int
    litros: float
    valor_total: float
    km_abastecimento: int
    data_hora: Optional[datetime] = None  # se nao vier, o banco usa CURRENT_TIMESTAMP