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

def calcular_actualizacion_tabla_unificada(areas, montos):
    """Consolida los datos de todas las unidades organizacionales en una sola tabla."""
    data_unificada = []

    for unidad, subareas in areas.items():
        for subarea, tipo in subareas.items():
            # Cargar datos de Requerimiento de Área
            sheet_name = f"{unidad}_{subarea}"
            data = load_data(excel_file, sheet_name)

            # Calcular monto requerido del área
            monto_requerido = 0
            if data is not None and "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
                monto_requerido = data["total"].sum()

            # Obtener monto DPP 2025 configurado
            dpp_2025 = montos[unidad][tipo]

            # Calcular diferencia
            diferencia = dpp_2025 - monto_requerido

            # Agregar fila a la tabla consolidada
            data_unificada.append({
                "Unidad Organizacional": unidad,
                "Monto Requerido del Área": monto_requerido,
                "Monto DPP 2025": dpp_2025,
                "Diferencia": diferencia
            })

    # Convertir a DataFrame
    return pd.DataFrame(data_unificada)

def aplicar_formato_condicional(df):
    """Aplica formato condicional a la columna Diferencia."""
    # Convertir DataFrame a HTML con estilos condicionales
    def estilo_filas(val):
        if val == 0:
            return 'background-color: #d4edda; color: #155724;'  # Verde
        else:
            return 'background-color: #fff3cd; color: #856404;'  # Amarillo

    return df.style.applymap(estilo_filas, subset=["Diferencia"])

def mostrar_actualizacion():
    """Muestra la página de Actualización consolidada."""
    st.title("Actualización - Consolidado")
    st.write("Tabla única consolidada para Misiones y Consultores.")

    # Configuración de las áreas y montos DPP 2025
    areas = {
        "PRE": {"Misiones_personal": "Misiones", "Misiones_consultores": "Consultorías", "Servicios_profesionales": "Consultorías"},
        "VPE": {"Misiones": "Misiones", "Consultores": "Consultorías"},
        "VPF": {"Misiones": "Misiones", "Consultores": "Consultorías"},
        "VPD": {"Misiones": "Misiones", "Consultores": "Consultorías"},
        "VPO": {"Misiones": "Misiones", "Consultores": "Consultorías"}
    }

    montos = {
        "VPD": {"Misiones": 168000, "Consultorías": 130000},
        "VPF": {"Misiones": 138600, "Consultorías": 170000},
        "VPO": {"Misiones": 434707, "Consultorías": 547700},
        "VPE": {"Misiones": 80168, "Consultorías": 338372},
        "PRE": {"Misiones": 0, "Consultorías": 0}  # Ajustar si aplica
    }

    # Calcular tabla consolidada
    tabla_unificada = calcular_actualizacion_tabla_unificada(areas, montos)

    # Mostrar tabla consolidada con formato condicional
    st.subheader("Tabla Consolidada")
    st.dataframe(aplicar_formato_condicional(tabla_unificada))

def mostrar_requerimiento_area(sheet_name):
    """Muestra una tabla estática de Requerimiento de Área con un Value Box de Total."""
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
        edited_df = pd.DataFrame(edited_data[list(edited_data.keys())[0]]) if isinstance(edited_data, dict) else edited_data

        if edited_df is not None:
            # Normalizar nombres de columnas
            edited_df.columns = edited_df.columns.str.strip().str.lower()

            # Intentar convertir la columna 'total' a numérica y calcular la suma
            if "total" in edited_df.columns:
                try:
                    edited_df["total"] = pd.to_numeric(edited_df["total"], errors="coerce")
                    total_sum = edited_df["total"].sum()
                    diferencia = total_sum - monto_dpp

                    # Mostrar Value Boxes
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Monto DPP 2025", value=f"${monto_dpp:,.2f}")
                    with col2:
                        st.metric(label="Suma de Total", value=f"${total_sum:,.2f}")
                    with col3:
                        st.metric(label="Diferencia", value=f"${diferencia:,.2f}")
                except Exception as e:
                    st.warning(f"No se pudo convertir la columna 'total' a numérico: {e}")
            else:
                st.error("No se encontró una columna llamada 'total'.")
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def main():
    """Estructura principal de la aplicación."""
    pages = ["Principal", "Actualización", "PRE", "VPE", "VPF", "VPD", "VPO"]
    selected_page = st.sidebar.selectbox("Selecciona una página", pages)

    if selected_page == "Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la página principal de la app.")
    elif selected_page == "Actualización":
        mostrar_actualizacion()
    else:
        # Requerimiento de Área o DPP 2025
        subpage_options = ["Misiones", "Consultorías"]
        selected_subpage = st.sidebar.radio("Selecciona una subpágina", subpage_options)

        montos = {
            "VPD": {"Misiones": 168000, "Consultorías": 130000},
            "VPF": {"Misiones": 138600, "Consultorías": 170000},
            "VPO": {"Misiones": 434707, "Consultorías": 547700},
            "VPE": {"Misiones": 80168, "Consultorías": 338372},
            "PRE": {"Misiones": 0, "Consultorías": 0}
        }

        if subpage_options == "Misiones":
            mostrar_requerimiento_area(f"{selected_page}_Misiones")
            mostrar_dpp_2025_mito(f"{selected_page}_Misiones", montos[selected_page]["Misiones"])
        elif subpage_options == "Consultorías":
            mostrar_requerimiento_area(f"{selected_page}_Consultores")
            mostrar_dpp_2025_mito(f"{selected_page}_Consultores", montos[selected_page]["Consultorías"])

if __name__ == "__main__":
    main()
