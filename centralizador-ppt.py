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

@st.cache_data
def load_data(filepath, sheet_name):
    """Carga datos de una hoja de Excel."""
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

def mostrar_requerimiento_area(sheet_name):
    """Muestra datos de Requerimiento de Área sin editar."""
    st.header(f"Requerimiento de Área - {sheet_name}")
    st.write("Vista de datos de Requerimiento de Área (solo lectura).")

    data = load_data(excel_file, sheet_name)
    if data is not None:
        st.dataframe(data)
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def mostrar_dpp_2025_mito(sheet_name):
    """Muestra y edita datos de DPP 2025 usando MITO."""
    st.header(f"DPP 2025 - {sheet_name}")
    st.write("Edite los valores en la hoja de cálculo a continuación:")

    data = load_data(excel_file, sheet_name)
    if data is not None:
        edited_data, code = spreadsheet(data)
        st.session_state[f"dpp_2025_{sheet_name}_data"] = edited_data

        if "total" in edited_data.columns and pd.api.types.is_numeric_dtype(edited_data["total"]):
            total_sum = edited_data["total"].sum()
            st.metric("Total Calculado", f"${total_sum:,.2f}")
        else:
            st.warning("No se encontró una columna 'total' válida en los datos.")
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def main():
    """Estructura principal de la aplicación."""
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
        elif selected_page == "VPD":
            st.title("VPD")
            subpage_options = ["Misiones", "Consultorías"]
            selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

            if selected_subpage == "Misiones":
                st.subheader("Misiones")
                subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)

                if selected_subsubpage == "Requerimiento de Área":
                    mostrar_requerimiento_area("VPD_Misiones")
                elif selected_subsubpage == "DPP 2025":
                    mostrar_dpp_2025_mito("VPD_Misiones")

            elif selected_subpage == "Consultorías":
                st.subheader("Consultorías")
                subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)

                if selected_subsubpage == "Requerimiento de Área":
                    mostrar_requerimiento_area("VPD_Consultores")
                elif selected_subsubpage == "DPP 2025":
                    mostrar_dpp_2025_mito("VPD_Consultores")
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
                st.title(f"Página {selected_page}")
                st.write("Contenido aún no implementado.")

if __name__ == "__main__":
    main()
