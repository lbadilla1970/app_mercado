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
