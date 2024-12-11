import streamlit as st
import pandas as pd
from mitosheet.streamlit.v1 import spreadsheet

# Configuración de la aplicación
st.set_page_config(
    page_title="Gestión Presupuestaria",
    page_icon="📊",
    layout="wide"
)

# Credenciales globales de acceso a la app
app_credentials = {
    "username": "luciana_botafogo",
    "password": "fonplata"
}

# Contraseñas para cada página
page_passwords = {
    "Principal": None,
    "PRE": "pre456",
    "VPE": "vpe789",
    "VPD": "vpd101",
    "VPO": "vpo112",
    "VPF": "vpf131",
    "Actualización": "update2023",
    "Consolidado": "consolidado321",
    "Tablero": "tablero654"
}

# Subpáginas por página principal
subpages = {
    "PRE": [
        "Misiones Personal",
        "Misiones Consultores",
        "Servicios Profesionales",
        "Gastos Centralizados"
    ],
    "VPD": [
        "Misiones",
        "Consultores",
        "Gastos Centralizados"
    ],
    "Actualización": [],
    "Consolidado": []
}

@st.cache_data
def load_data(filepath, sheet_name):
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return None

excel_file = "main_bdd.xlsx"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page_authenticated" not in st.session_state:
    st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}

def mostrar_subpagina(sheet_name, download_filename='', mostrar_boxes=False):
    data = load_data(excel_file, sheet_name)
    if data is not None:
        st.subheader(f"Tabla de {sheet_name}")
        if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
            total_sum = data["total"].sum()
            st.metric(label="Total", value=f"${total_sum:,.2f}")
        else:
            st.warning("No se encontró una columna 'total' numérica en la tabla.")
        st.dataframe(data)

        if mostrar_boxes:
            st.markdown("### Resumen de Misiones de Servicio")
            total_sum = data["total"].sum() if ("total" in data.columns and pd.api.types.is_numeric_dtype(data["total"])) else 0
            st.metric("Total Misiones", f"${total_sum:,.2f}")

        if download_filename:
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar datos como CSV",
                data=csv,
                file_name=download_filename,
                mime='text/csv',
            )
    else:
        st.warning("No se pudo cargar la tabla especificada.")

def mostrar_dpp_2025():
    st.header("DPP 2025 - Misiones")
    st.write("Edite los valores en la hoja de cálculo a continuación:")

    data = load_data(excel_file, "VPD_Misiones")
    if data is not None:
        edited_data, code = spreadsheet(data)
        st.session_state.dpp_2025_data = edited_data
        st.session_state.dpp_2025_data['total'] = (
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['costo_pasaje'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['dias'] * st.session_state.dpp_2025_data['alojamiento'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['dias'] * st.session_state.dpp_2025_data['perdiem_otros'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['movilidad']
        )

        total_sum = st.session_state.dpp_2025_data['total'].sum()
        monto_deseado = 168000
        diferencia = monto_deseado - total_sum

        st.markdown("### Resultados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total 💰", f"${total_sum:,.2f}")
        with col2:
            st.metric("Monto Deseado 🎯", f"${monto_deseado:,.2f}")
        with col3:
            st.metric("Diferencia ➖", f"${diferencia:,.2f}")
    else:
        st.warning("No se pudo cargar la tabla VPD_Misiones para DPP 2025.")

def mostrar_dpp_2025_consultores():
    st.header("DPP 2025 - Consultores")
    st.write("Edite los valores en la hoja de cálculo a continuación:")

    data = load_data(excel_file, "VPD_Consultores")
    if data is not None:
        edited_data, code = spreadsheet(data)
        st.session_state.dpp_2025_consultores_data = edited_data
        st.session_state.dpp_2025_consultores_data['total'] = (
            st.session_state.dpp_2025_consultores_data['cantidad_funcionarios'] *
            st.session_state.dpp_2025_consultores_data['monto_mensual'] *
            st.session_state.dpp_2025_consultores_data['cantidad_meses']
        )

        total_sum = st.session_state.dpp_2025_consultores_data['total'].sum()
        monto_deseado = 130000
        diferencia = monto_deseado - total_sum

        st.markdown("### Resultados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total 💰", f"${total_sum:,.2f}")
        with col2:
            st.metric("Monto Deseado 🎯", f"${monto_deseado:,.2f}")
        with col3:
            st.metric("Diferencia ➖", f"${diferencia:,.2f}")
    else:
        st.warning("No se pudo cargar la tabla VPD_Consultores para DPP 2025.")

def main():
    if not st.session_state.authenticated:
        st.title("Gestión Presupuestaria")
        username_input = st.text_input("Usuario", key="login_username")
        password_input = st.text_input("Contraseña", type="password", key="login_password")
        login_button = st.button("Ingresar", key="login_button")

        if login_button:
            if username_input == app_credentials["username"] and password_input == app_credentials["password"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    else:
        pages = list(page_passwords.keys())
        selected_page = st.sidebar.selectbox("Selecciona una página", pages)

        if selected_page == "Principal":
            st.title("Página Principal")
            st.write("Bienvenido a la página principal de la app.")
        else:
            if not st.session_state.page_authenticated[selected_page]:
                st.sidebar.markdown("---")
                password_input = st.sidebar.text_input("Ingresa la contraseña", type="password", key=f"page_password_{selected_page}")
                verify_button = st.sidebar.button("Verificar", key=f"verify_{selected_page}")

                if verify_button:
                    if password_input == page_passwords[selected_page]:
                        st.session_state.page_authenticated[selected_page] = True
                        st.rerun()
                    else:
                        st.sidebar.error("Contraseña incorrecta.")
            else:
                if selected_page == "VPD":
                    st.title("VPD")
                    subpage_options = ["Misiones", "Consultores"]
                    selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)
                    if selected_subpage == "Misiones":
                        mostrar_dpp_2025()
                    elif selected_subpage == "Consultores":
                        mostrar_dpp_2025_consultores()
                elif selected_page == "PRE":
                    st.title("PRE")
                    subpage_options = subpages[selected_page]
                    selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)
                    mostrar_subpagina(selected_subpage, download_filename=f"{selected_subpage}.csv")
                else:
                    st.title(f"Página {selected_page}")
                    st.write("Contenido aún no implementado.")

if __name__ == "__main__":
    main()
