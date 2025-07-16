from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))

    company = relationship('Company')
    role = relationship('Role')

class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    category = Column(String)
    value = Column(Integer)
    date = Column(Date)
    group = Column(String)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship('Company')

class PasswordReset(Base):
    __tablename__ = 'password_resets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String, unique=True)
    expiry = Column(DateTime, default=datetime.utcnow)
    user = relationship('User')


class Licitacion(Base):
    __tablename__ = 'licitaciones'
    id = Column(Integer, primary_key=True)
    numero_adquisicion = Column(String, unique=True)
    tipo_adquisicion = Column(String)
    col3 = Column(String)
    nombre_adquisicion = Column(String)
    descripcion = Column(String)
    organismo = Column(String)
    region_compradora = Column(String)
    col8 = Column(String)
    fecha_publicacion = Column(String)
    fecha_cierre = Column(String)
    descripcion_producto = Column(String)
    codigo_onu = Column(String)
    unidad_medida = Column(String)
    cantidad = Column(String)
    generico = Column(String)
    nivel1 = Column(String)
    nivel2 = Column(String)
    nivel3 = Column(String)


class LicitacionEmpresa(Base):
    __tablename__ = 'licitaciones_empresas'
    id = Column(Integer, primary_key=True)
    empresa = Column(String)
    numero_adquisicion = Column(String)
    tipo_adquisicion = Column(String)
    col3 = Column(String)
    nombre_adquisicion = Column(String)
    descripcion = Column(String)
    organismo = Column(String)
    region_compradora = Column(String)
    col8 = Column(String)
    fecha_publicacion = Column(String)
    fecha_cierre = Column(String)
    descripcion_producto = Column(String)
    codigo_onu = Column(String)
    unidad_medida = Column(String)
    cantidad = Column(String)
    generico = Column(String)
    nivel1 = Column(String)
    nivel2 = Column(String)
    nivel3 = Column(String)
