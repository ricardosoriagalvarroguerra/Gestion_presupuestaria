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

def mostrar_requerimiento_area(sheet_name):
    """Muestra una tabla estática de Requerimiento de Área o PRE con un Value Box de Total."""
    st.header(f"Requerimiento de Área - {sheet_name}")

    data = load_data(excel_file, sheet_name)
    if data is not None:
        if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
            total_sum = data["total"].sum()
            st.metric("Total Requerido", f"${total_sum:,.2f}")
        st.dataframe(data)
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def mostrar_dpp_2025_mito(sheet_name, monto_dpp):
    """Muestra y edita datos de DPP 2025 usando MITO, con Value Boxes para suma de 'total', monto DPP 2025 y diferencia."""
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
                    diferencia = total_sum - monto_dpp

                    # Mostrar Value Boxes
                    col1, col2, col3 = st.columns(3)  # Alinear los Value Boxes
                    with col1:
                        st.metric(label="Monto DPP 2025", value=f"${monto_dpp:,.2f}")
                    with col2:
                        st.metric(label="Suma de Total", value=f"${total_sum:,.2f}")
                    with col3:
                        st.metric(label="Diferencia", value=f"${diferencia:,.2f}")

                except Exception as e:
                    st.warning(f"No se pudo convertir la columna 'total' a un formato numérico: {e}")
            else:
                st.error("No se encontró una columna llamada 'total' en los datos después de la normalización.")
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def calcular_actualizacion_tabla(vicepresidencias, tipo):
    """Calcula la tabla de Actualización para Misiones o Consultores."""
    filas = []
    for vpe, montos in vicepresidencias.items():
        requerimiento_key = f"dpp_2025_{vpe}_{tipo}_data"
        requerimiento = 0

        if requerimiento_key in st.session_state:
            data = st.session_state[requerimiento_key]
            if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
                requerimiento = data["total"].sum()

        dpp = montos[tipo]
        diferencia = requerimiento - dpp

        filas.append({
            "Unidad Organizacional": vpe,
            "Requerimiento Área": requerimiento,
            "DPP 2025": dpp,
            "Diferencia": diferencia
        })

    df = pd.DataFrame(filas)
    return df

def aplicar_estilos(df):
    """Aplica estilos condicionales a la columna Diferencia."""
    def resaltar_diferencia(val):
        if val == 0:
            return "background-color: green; color: white;"
        else:
            return "background-color: yellow; color: black;"

    styled_df = df.style.applymap(resaltar_diferencia, subset=["Diferencia"])
    return styled_df

def mostrar_actualizacion():
    """Muestra la página de Actualización con tablas consolidadas."""
    st.title("Actualización - Resumen Consolidado")
    st.write("Estas tablas muestran el monto requerido, DPP 2025, y la diferencia para cada área.")

    vicepresidencias = {
        "VPD": {"Misiones": 168000, "Consultores": 130000},
        "VPF": {"Misiones": 138600, "Consultores": 170000},
        "VPO": {"Misiones": 434707, "Consultores": 547700},
        "VPE": {"Misiones": 80168, "Consultores": 338372},
    }

    st.subheader("Misiones")
    misiones_df = calcular_actualizacion_tabla(vicepresidencias, "Misiones")
    styled_misiones_df = aplicar_estilos(misiones_df)
    st.write(styled_misiones_df, unsafe_allow_html=True)

    st.subheader("Consultores")
    consultores_df = calcular_actualizacion_tabla(vicepresidencias, "Consultores")
    styled_consultores_df = aplicar_estilos(consultores_df)
    st.write(styled_consultores_df, unsafe_allow_html=True)

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
            subpage_options = ["Misiones", "Consultorías"]
            selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

            montos = {
                "VPD": {"Misiones": 168000, "Consultores": 130000},
                "VPF": {"Misiones": 138600, "Consultores": 170000},
                "VPO": {"Misiones": 434707, "Consultores": 547700},
                "VPE": {"Misiones": 80168, "Consultores": 338372},
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
                    mostrar_dpp_2025_mito(f"{selected_page}_Consultores", montos[selected_page]["Consultores"])
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
