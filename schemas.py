from pydantic import BaseModel
from typing import List
from datetime import date

class RolBase(BaseModel):
    nombre_rol: str

class Rol(RolBase):
    id_rol: int
    class Config:
        orm_mode = True

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    correo: str
    fecha_registro: date

class UsuarioCreate(UsuarioBase):
    roles: List[RolBase]  # lista de roles base

class Usuario(UsuarioBase):
    id_usuario: int
    roles: List[Rol]
    class Config:
        orm_mode = True
