import os
import streamlit as st
import pandas as pd
from dashboards import general, grupo, mapa
from utils.charts import kpi_card
from database import SessionLocal
from init_db import init_db
import auth
from models import User, Role, Company, Data, LicitacionEmpresa

st.set_page_config(layout="wide")
init_db()

def get_db():
    return SessionLocal()

def load_data(db, company_id):
    rows = db.query(Data).filter_by(company_id=company_id).all()
    return pd.DataFrame([
        {
            'Categoría': r.category,
            'Valor': r.value,
            'Fecha': r.date,
            'Grupo': r.group
        } for r in rows
    ])

def load_licitaciones(db, empresa):
    rows = db.query(LicitacionEmpresa).filter_by(empresa=empresa).all()
    return pd.DataFrame([
        {
            'Numero': r.numero_adquisicion,
            'Tipo': r.tipo_adquisicion,
            'Nombre': r.nombre_adquisicion,
            'Organismo': r.organismo,
            'Fecha Publicacion': r.fecha_publicacion,
            'Fecha Cierre': r.fecha_cierre,
        } for r in rows
    ])

def admin_panel(db):
    st.header('Panel de Administración')
    st.subheader('Usuarios')
    users = db.query(User).all()
    data = [
        {
            'Email': u.email,
            'Empresa': u.company.name if u.company else '',
            'Rol': u.role.name if u.role else ''
        } for u in users
    ]
    st.table(pd.DataFrame(data))
    st.subheader('Crear Usuario')
    with st.form('crear_usuario'):
        email = st.text_input('Email')
        password = st.text_input('Contraseña', type='password')
        empresa = st.text_input('Empresa')
        roles = [r.name for r in db.query(Role).all()]
        rol = st.selectbox('Rol', roles)
        submit = st.form_submit_button('Crear')
    if submit:
        company = db.query(Company).filter_by(name=empresa).first()
        if not company:
            company = Company(name=empresa)
            db.add(company)
            db.commit()
            db.refresh(company)
        role = db.query(Role).filter_by(name=rol).first()
        auth.create_user(db, email, password, company.id, role.id)
        st.success('Usuario creado')

    st.subheader('Roles')
    roles = db.query(Role).all()
    st.table(pd.DataFrame([{'id': r.id, 'name': r.name} for r in roles]))
    new_role = st.text_input('Nuevo Rol')
    if st.button('Agregar Rol') and new_role:
        if not db.query(Role).filter_by(name=new_role).first():
            db.add(Role(name=new_role))
            db.commit()
            st.success('Rol agregado')

    st.subheader('Licitaciones')
    if st.button('Actualizar desde Excel'):
        from utils.licitaciones import sync_from_excel
        sync_from_excel(db)
        st.success('Datos actualizados')

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def login_page(db):
    st.title('Iniciar Sesión')
    with st.form('login'):
        email = st.text_input('Email')
        password = st.text_input('Contraseña', type='password')
        submit = st.form_submit_button('Ingresar')
    if submit:
        user = auth.authenticate(db, email, password)
        if user:
            st.session_state.user_id = user.id
            st.session_state.page = 'app'
            st.experimental_rerun()
        else:
            st.error('Credenciales inválidas')
    if st.button('¿Olvidó su contraseña?'):
        st.session_state.page = 'forgot'
        st.experimental_rerun()

def forgot_page(db):
    st.title('Recuperar Contraseña')
    with st.form('forgot'):
        email = st.text_input('Email')
        submit = st.form_submit_button('Enviar')
    if submit:
        user = db.query(User).filter_by(email=email).first()
        if user:
            token = auth.generate_reset_token(db, user)
            auth.send_reset_email(email, token)
        st.success('Si el correo existe se enviará un token.')
    if st.button('Volver'):
        st.session_state.page = 'login'
        st.experimental_rerun()

def reset_page(db):
    st.title('Restablecer Contraseña')
    with st.form('reset'):
        email = st.text_input('Email')
        token = st.text_input('Token')
        new_pw = st.text_input('Nueva Contraseña', type='password')
        submit = st.form_submit_button('Cambiar')
    if submit:
        user = auth.verify_reset_token(db, email, token)
        if user:
            auth.change_password(db, user, new_pw)
            st.success('Contraseña actualizada')
        else:
            st.error('Token inválido')
    if st.button('Volver'):
        st.session_state.page = 'login'
        st.experimental_rerun()

def main_app(db):
    user = db.get(User, st.session_state.user_id)
    if not user:
        st.session_state.page = 'login'
        st.experimental_rerun()
    st.sidebar.write(f'Conectado como: {user.email}')
    if st.sidebar.button('Cerrar sesión'):
        st.session_state.user_id = None
        st.session_state.page = 'login'
        st.experimental_rerun()

    if user.role and user.role.name == 'Administrador':
        show_panel = st.sidebar.checkbox('Panel Administrador')
    else:
        show_panel = False

    if show_panel:
        admin_panel(db)
        return

    pagina = st.sidebar.selectbox('Seleccione una vista', [
        'Resumen General', 'Análisis por Grupo', 'Mapa', 'Licitaciones'
    ])
    df = load_data(db, user.company_id)

    if pagina == 'Resumen General':
        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card('Dotación', value='250', delta='+10 respecto al mes anterior',
                     color='#1f77b4', width=200, height=100)
        with col2:
            kpi_card('Sueldo Promedio', '$1.200.000', '-2%', '#2ca02c', width=200, height=100)
        with col3:
            kpi_card('Rotación Mensual', '3.2%', '+0.4%', '#d62728', width=200, height=100)
        general.mostrar(df)
    elif pagina == 'Análisis por Grupo':
        grupo.mostrar(df)
    elif pagina == 'Mapa':
        mapa.mostrar(df)
    elif pagina == 'Licitaciones':
        ldf = load_licitaciones(db, user.company.name)
        tipos = ['Todos'] + sorted(ldf['Tipo'].unique())
        tsel = st.selectbox('Tipo de licitacion', tipos)
        if tsel != 'Todos':
            ldf = ldf[ldf['Tipo'] == tsel]
        st.dataframe(ldf)

page_func = {
    'login': login_page,
    'forgot': forgot_page,
    'reset': reset_page,
    'app': main_app
}

def run_app():
    db = get_db()
    try:
        page_func[st.session_state.page](db)
    finally:
        db.close()

if __name__ == '__main__':
    run_app()
