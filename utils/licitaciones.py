import pandas as pd
from models import Licitacion, LicitacionEmpresa, Company

HEADER_ROW = 7

# Column names in the final dataframe that map directly to the fields of the
# ``Licitacion`` model.  These are derived from ``COLUMN_MAP`` plus the extra
# columns ``col3`` and ``col8`` that appear in the spreadsheet.
LICITACION_FIELDS = [
    'numero_adquisicion',
    'tipo_adquisicion',
    'col3',
    'nombre_adquisicion',
    'descripcion',
    'organismo',
    'region_compradora',
    'col8',
    'fecha_publicacion',
    'fecha_cierre',
    'descripcion_producto',
    'codigo_onu',
    'unidad_medida',
    'cantidad',
    'generico',
    'nivel1',
    'nivel2',
    'nivel3',
]

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
    df = pd.read_excel(path, header=HEADER_ROW, engine='openpyxl', dtype=str)
    # Normalize column names and ensure they are strings
    df.columns = [str(c).strip() for c in df.columns]
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
    if 'Unnamed: 7' in df.columns:
        df = df.rename(columns={'Unnamed: 7': 'col8'})
    # Remove any other leftover Excel index columns like 'Unnamed: 1'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    if 'col3' not in df.columns:
        df['col3'] = ''
    if 'col8' not in df.columns:
        df['col8'] = ''
    for col in COLUMN_MAP.values():
        if col not in df.columns:
            df[col] = ''
    # Drop any columns not used by the model to avoid unexpected keyword
    # arguments when creating ``Licitacion`` objects.
    df = df.reindex(columns=LICITACION_FIELDS, fill_value='')
    # Ensure all values are stored as strings so they can be inserted
    # consistently into the database and later rendered by Streamlit
    df = df.astype(str)
    # Remove duplicates based on the acquisition number to avoid integrity
    # errors when inserting into the database.  ``keep='first'`` retains the
    # first occurrence and drops the rest.
    df = df.drop_duplicates(subset=['numero_adquisicion'], keep='first')
    return df


def initial_load(db):
    if db.query(Licitacion).first():
        return
    df = _read_excel()
    first = df.iloc[:50]
    second = df.iloc[50:100]
    for _, row in pd.concat([first, second]).iterrows():
        data = {k: row[k] for k in LICITACION_FIELDS}
        db.add(Licitacion(**data))
    db.commit()
    for _, row in first.iterrows():
        data = {k: row[k] for k in LICITACION_FIELDS}
        db.add(LicitacionEmpresa(empresa='Ecoscom', **data))
    for _, row in second.iterrows():
        data = {k: row[k] for k in LICITACION_FIELDS}
        db.add(LicitacionEmpresa(empresa='Indoor', **data))
    db.commit()


def sync_from_excel(db):
    df = _read_excel()
    excel_nums = set(df['numero_adquisicion'])
    for rec in db.query(Licitacion).all():
        if rec.numero_adquisicion not in excel_nums:
            db.delete(rec)
    db.commit()
    for _, row in df.iterrows():
        data = {k: row[k] for k in LICITACION_FIELDS}
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
            data = {k: row[k] for k in LICITACION_FIELDS}
            lic = db.query(LicitacionEmpresa).filter_by(empresa=empresa,
                                                       numero_adquisicion=data['numero_adquisicion']).first()
            if not lic:
                db.add(LicitacionEmpresa(empresa=empresa, **data))
            else:
                for k, v in data.items():
                    setattr(lic, k, v)
    db.commit()
