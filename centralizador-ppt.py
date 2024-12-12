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

excel_file = "/mnt/data/main_bdd.xlsx"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page_authenticated" not in st.session_state:
    st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}

def calcular_actualizacion_unificada(areas, montos):
    """Calcula una única tabla de Actualización para Misiones y otra para Consultores."""
    misiones_data = []
    consultores_data = []

    for area, subareas in areas.items():
        for subarea, subarea_type in subareas.items():
            # Cargar datos de Requerimiento de Área
            sheet_name = f"{area}_{subarea}"
            data = load_data(excel_file, sheet_name)

            # Calcular total requerido del área
            monto_requerido = 0
            if data is not None and "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
                monto_requerido = data["total"].sum()

            # Obtener el monto DPP 2025 configurado
            dpp_2025 = montos[area][subarea_type]

            # Calcular diferencia
            diferencia = dpp_2025 - monto_requerido

            # Agregar a la tabla correspondiente
            fila = {
                "Área": area,
                "Monto Requerido del Área": monto_requerido,
                "DPP 2025": dpp_2025,
                "Diferencia": diferencia
            }
            if subarea_type == "Misiones":
                misiones_data.append(fila)
            elif subarea_type == "Consultorías":
                consultores_data.append(fila)

    # Convertir listas a DataFrames
    misiones_df = pd.DataFrame(misiones_data)
    consultores_df = pd.DataFrame(consultores_data)

    return misiones_df, consultores_df

def mostrar_actualizacion():
    """Muestra la página de Actualización con tablas consolidadas para Misiones y Consultores."""
    st.title("Actualización - Resumen Consolidado")
    st.write("Estas tablas muestran el monto requerido, DPP 2025, y la diferencia para Misiones y Consultores.")

    # Definir las áreas y subáreas
    areas = {
        "PRE": {"Misiones_personal": "Misiones", "Misiones_consultores": "Consultorías", "Servicios_profesionales": "Consultorías"},
        "VPE": {"Misiones": "Misiones", "Consultores": "Consultorías"},
        "VPF": {"Misiones": "Misiones", "Consultores": "Consultorías"},
        "VPD": {"Misiones": "Misiones", "Consultores": "Consultorías"},
        "VPO": {"Misiones": "Misiones", "Consultores": "Consultorías"}
    }

    # Montos DPP 2025 configurados
    montos = {
        "VPD": {"Misiones": 168000, "Consultorías": 130000},
        "VPF": {"Misiones": 138600, "Consultorías": 170000},
        "VPO": {"Misiones": 434707, "Consultorías": 547700},
        "VPE": {"Misiones": 80168, "Consultorías": 338372},
        "PRE": {"Misiones": 0, "Consultorías": 0}  # Ajustar según corresponda
    }

    # Calcular tablas
    misiones_df, consultores_df = calcular_actualizacion_unificada(areas, montos)

    # Mostrar tablas
    st.subheader("Misiones")
    st.dataframe(misiones_df)

    st.subheader("Consultorías")
    st.dataframe(consultores_df)

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
        elif selected_page == "Actualización":
            mostrar_actualizacion()
        elif selected_page in ["VPD", "VPF", "VPO", "VPE"]:
            # Misiones y Consultorías para cada área
            subpage_options = ["Misiones", "Consultorías"]
            selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

            montos = {
                "VPD": {"Misiones": 168000, "Consultorías": 130000},
                "VPF": {"Misiones": 138600, "Consultorías": 170000},
                "VPO": {"Misiones": 434707, "Consultorías": 547700},
                "VPE": {"Misiones": 80168, "Consultorías": 338372},
            }

            if selected_subpage == "Misiones":
                subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)
                if selected_subsubpage == "Requerimiento de Área":
                    mostrar_requerimiento_area(f"{selected_page}_Misiones")
                elif selected_subsubpage == "DPP 2025":
                    mostrar_dpp_2025_mito(f"{selected_page}_Misiones", montos[selected_page]["Misiones"])

            elif selected_subpage == "Consultorías":
                subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)
                if selected_subsubpage == "Requerimiento de Área":
                    mostrar_requerimiento_area(f"{selected_page}_Consultores")
                elif selected_subsubpage == "DPP 2025":
                    mostrar_dpp_2025_mito(f"{selected_page}_Consultores", montos[selected_page]["Consultorías"])
        elif selected_page == "PRE":
            st.title("PRE")
            subpage_options = ["Misiones Personal", "Misiones Consultores", "Servicios Profesionales", "Gastos Centralizados"]
            selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

            if selected_subpage == "Misiones Personal":
                mostrar_requerimiento_area("PRE_Misiones_personal")
            elif selected_subpage == "Misiones Consultores":
                mostrar_requerimiento_area("PRE_Misiones_consultores")
            elif selected_subpage == "Servicios Profesionales":
                mostrar_requerimiento_area("PRE_servicios_profesionales")
            elif selected_subpage == "Gastos Centralizados":
                st.write("Sube un archivo para Gastos Centralizados.")
                uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
                if uploaded_file:
                    data = pd.read_excel(uploaded_file, engine="openpyxl")
                    st.write("Archivo cargado:")
                    st.dataframe(data)

if __name__ == "__main__":
    main()
