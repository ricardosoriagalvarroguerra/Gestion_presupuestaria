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

def convertir_a_dataframe(edited_data):
    """Convierte los datos editados por Mito a un pandas DataFrame de manera robusta."""
    if isinstance(edited_data, pd.DataFrame):
        return edited_data
    elif isinstance(edited_data, dict):
        key = list(edited_data.keys())[0]  # Tomar la primera clave del diccionario (e.g., 'df1')
        return pd.DataFrame(edited_data[key])
    else:
        st.error("El formato de los datos editados no es compatible.")
        return None

def mostrar_dpp_2025_mito(sheet_name, monto_dpp):
    """Muestra y edita datos de DPP 2025 usando MITO, con Value Boxes para suma de 'total' y monto DPP 2025."""
    st.header(f"DPP 2025 - {sheet_name}")

    data = load_data(excel_file, sheet_name)
    if data is not None:
        edited_data, code = spreadsheet(data)

        # Extraer el DataFrame correcto desde el diccionario devuelto por Mito
        edited_df = convertir_a_dataframe(edited_data)

        if edited_df is not None:
            # Normalizar nombres de columnas
            edited_df.columns = edited_df.columns.str.strip().str.lower()

            # Guardar datos en el estado de sesión
            st.session_state[f"dpp_2025_{sheet_name}_data"] = edited_df

            # Intentar convertir la columna 'total' a numérica y calcular la suma
            if "total" in edited_df.columns:
                try:
                    edited_df["total"] = pd.to_numeric(edited_df["total"], errors="coerce")
                    total_sum = edited_df["total"].sum()

                    # Mostrar Value Boxes arriba de la tabla
                    col1, col2, col3 = st.columns([1, 2, 1])  # Alinear los Value Boxes en el centro
                    with col1:
                        st.metric(label="Monto DPP 2025", value=f"${monto_dpp:,.2f}")
                    with col3:
                        st.metric(label="Suma de Total", value=f"${total_sum:,.2f}")

                    # Mostrar la tabla editada
                    st.write("Edite los datos en la tabla a continuación:")
                    st.dataframe(edited_df)
                except Exception as e:
                    st.warning(f"No se pudo convertir la columna 'total' a un formato numérico: {e}")
            else:
                st.error("No se encontró una columna llamada 'total' en los datos después de la normalización.")
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

        # Lógica para cada página
        if selected_page == "Principal":
            st.title("Página Principal")
            st.write("Bienvenido a la página principal de la app.")
        elif selected_page in ["VPD", "VPF", "VPO", "VPE"]:
            st.title(selected_page)
            subpage_options = ["Misiones", "Consultorías"]
            selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

            montos = {
                "VPD": {"Misiones": 168000, "Consultorías": 130000},
                "VPF": {"Misiones": 138600, "Consultorías": 170000},
                "VPO": {"Misiones": 434707, "Consultorías": 547700},
                "VPE": {"Misiones": 80168, "Consultorías": 338372},
            }

            if selected_subpage == "Misiones":
                mostrar_dpp_2025_mito(f"{selected_page}_Misiones", montos[selected_page]["Misiones"])
            elif selected_subpage == "Consultorías":
                mostrar_dpp_2025_mito(f"{selected_page}_Consultores", montos[selected_page]["Consultorías"])
        elif selected_page == "PRE":
            st.title("PRE")
            subpage_options = ["Misiones Personal", "Misiones Consultores", "Servicios Profesionales", "Gastos Centralizados"]
            selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

            if selected_subpage == "Misiones Personal":
                mostrar_dpp_2025_mito("PRE_Misiones_personal", 0)  # Define el monto correspondiente si aplica
            elif selected_subpage == "Misiones Consultores":
                mostrar_dpp_2025_mito("PRE_Misiones_consultores", 0)  # Define el monto correspondiente si aplica
            elif selected_subpage == "Servicios Profesionales":
                mostrar_dpp_2025_mito("PRE_servicios_profesionales", 0)  # Define el monto correspondiente si aplica
            elif selected_subpage == "Gastos Centralizados":
                st.write("Sube un archivo para Gastos Centralizados.")
                uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
                if uploaded_file:
                    data = pd.read_excel(uploaded_file, engine="openpyxl")
                    st.write("Archivo cargado:")
                    st.dataframe(data)
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
