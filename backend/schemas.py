

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MotoristaCreate(BaseModel):
    cpf: str = Field(min_length=11, max_length=11)
    nome: str
    categoria_cnh: str


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


class ViagemEncerrar(BaseModel):
    km_final: int


class ViagemResponse(BaseModel):
    id_viagem: int
    id_motorista: int
    id_veiculo: int
    data_hora_saida: datetime
    km_inicial: int
    data_hora_chegada: Optional[datetime]   
    km_final: Optional[int]                  
    status: str