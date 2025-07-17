import pandas as pd
from models import Licitacion, LicitacionEmpresa, Company

HEADER_ROW = 7

COLUMN_MAP = {
    'Numero Adquisición': 'numero_adquisicion',
    'Tipo Adquisición': 'tipo_adquisicion',
    'Nombre Adquisición': 'nombre_adquisicion',
    'Descripción': 'descripcion',
    'Organismo': 'organismo',
    'Región Compradora': 'region_compradora',
    'Fecha Publicación': 'fecha_publicacion',
    'Fecha Cierre': 'fecha_cierre',
    'Descripción del producto/servicio': 'descripcion_producto',
    'Código ONU': 'codigo_onu',
    'Unidad de Medida': 'unidad_medida',
    'Cantidad': 'cantidad',
    'Genérico': 'generico',
    'Nivel 1': 'nivel1',
    'Nivel 2': 'nivel2',
    'Nivel 3': 'nivel3',
}


def _read_excel(path='datos/licitaciones.xlsx'):
    df = pd.read_excel(path, header=HEADER_ROW)
    # Normalize column names by stripping spaces
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    # Some spreadsheets might store the first column with a slightly different
    # name. Fallback to using the first column when the expected label is
    # missing.
    if 'Numero Adquisición' not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: 'Numero Adquisición'})
    df = df.dropna(subset=['Numero Adquisición'])
    df = df.fillna('')
    df = df.rename(columns=COLUMN_MAP)
    if 'Unnamed: 2' in df.columns:
        df = df.rename(columns={'Unnamed: 2': 'col3'})
    else:
        df['col3'] = ''
    if 'Unnamed: 7' in df.columns:
        df = df.rename(columns={'Unnamed: 7': 'col8'})
    else:
        df['col8'] = ''
    for col in COLUMN_MAP.values():
        if col not in df.columns:
            df[col] = ''
    return df


def initial_load(db):
    if db.query(Licitacion).first():
        return
    df = _read_excel()
    first = df.iloc[:50]
    second = df.iloc[50:100]
    for _, row in pd.concat([first, second]).iterrows():
        db.add(Licitacion(**row.to_dict()))
    db.commit()
    for _, row in first.iterrows():
        db.add(LicitacionEmpresa(empresa='Ecoscom', **row.to_dict()))
    for _, row in second.iterrows():
        db.add(LicitacionEmpresa(empresa='Indoor', **row.to_dict()))
    db.commit()


def sync_from_excel(db):
    df = _read_excel()
    excel_nums = set(df['numero_adquisicion'])
    for rec in db.query(Licitacion).all():
        if rec.numero_adquisicion not in excel_nums:
            db.delete(rec)
    db.commit()
    for _, row in df.iterrows():
        data = row.to_dict()
        lic = db.query(Licitacion).filter_by(numero_adquisicion=data['numero_adquisicion']).first()
        if not lic:
            db.add(Licitacion(**data))
        else:
            for k, v in data.items():
                setattr(lic, k, v)
    db.commit()
    companies = [c.name for c in db.query(Company).all()]
    for empresa in companies:
        for rec in db.query(LicitacionEmpresa).filter_by(empresa=empresa).all():
            if rec.numero_adquisicion not in excel_nums:
                db.delete(rec)
        db.commit()
        for _, row in df.iterrows():
            data = row.to_dict()
            lic = db.query(LicitacionEmpresa).filter_by(empresa=empresa,
                                                       numero_adquisicion=data['numero_adquisicion']).first()
            if not lic:
                db.add(LicitacionEmpresa(empresa=empresa, **data))
            else:
                for k, v in data.items():
                    setattr(lic, k, v)
    db.commit()
