import os
import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from models import Base, Role, Company, User, Data
from utils.licitaciones import initial_load
from passlib.hash import bcrypt
from database import engine, SessionLocal


def init_db():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        # Roles por defecto
        for rname in ['Usuario', 'Administrador']:
            if not db.query(Role).filter_by(name=rname).first():
                db.add(Role(name=rname))
        db.commit()

        # Empresas base
        ecoscom = db.query(Company).filter_by(name='Ecoscom').first()
        if not ecoscom:
            ecoscom = Company(name='Ecoscom')
            db.add(ecoscom)
            db.commit()
            db.refresh(ecoscom)

        indoor = db.query(Company).filter_by(name='Indoor').first()
        if not indoor:
            indoor = Company(name='Indoor')
            db.add(indoor)
            db.commit()

        # Datos de ejemplo
        if not db.query(Data).first():
            np.random.seed(42)
            df = pd.DataFrame({
                'category': np.random.choice(['A', 'B', 'C', 'D'], size=200),
                'value': np.random.randint(10, 100, size=200),
                'date': pd.date_range(start='2023-01-01', periods=200, freq='D'),
                'group': np.random.choice(['X', 'Y'], size=200)
            })
            for _, row in df.iterrows():
                db.add(Data(category=row['category'], value=int(row['value']),
                            date=row['date'].date(), group=row['group'],
                            company_id=ecoscom.id))
            db.commit()

        # Usuario administrador por env vars
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        if admin_email and admin_password:
            admin = db.query(User).filter_by(email=admin_email).first()
            admin_role = db.query(Role).filter_by(name='Administrador').first()
            if not admin:
                hashed = bcrypt.hash(admin_password)
                admin = User(email=admin_email, password_hash=hashed,
                             company_id=ecoscom.id, role_id=admin_role.id)
                db.add(admin)
                db.commit()

        # Carga inicial de licitaciones
        initial_load(db)
    finally:
        db.close()
