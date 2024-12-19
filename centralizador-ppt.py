import streamlit as st
import pandas as pd
import openpyxl
import os

# Configuración de la aplicación
st.set_page_config(
    page_title="Gestión Presupuestaria",
    page_icon="📊",
    layout="wide"
)

# Credenciales globales de acceso a la app (actualizado para múltiples usuarios)
app_credentials = {
    "luciana_botafogo": "fonplata",
    "mcalvino": "2025presupuesto",
    "ajustinianon": "2025presupuesto"
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
    """Carga datos de una hoja de Excel sin usar caché."""
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return None

def save_data(filepath, sheet_name, df):
    """Guarda el DataFrame en una hoja específica de un archivo Excel existente,
    reemplazando sólo esa hoja y conservando las demás."""
    try:
        if not os.path.exists(filepath):
            df.to_excel(filepath, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")

excel_file = "main_bdd.xlsx"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page_authenticated" not in st.session_state:
    st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}

def mostrar_requerimiento_area(sheet_name):
    st.header(f"Requerimiento de Área - {sheet_name}")
    data = load_data(excel_file, sheet_name)
    if data is not None:
        if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
            total_sum = data["total"].sum(numeric_only=True)
            st.metric("Total Requerido", f"${total_sum:,.0f}")
        st.dataframe(data)
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def mostrar_dpp_2025_editor(sheet_name, monto_dpp):
    st.header(f"DPP 2025 - {sheet_name}")

    session_key = f"dpp_2025_{sheet_name}_data"
    if session_key not in st.session_state:
        data = load_data(excel_file, sheet_name)
        if data is None:
            st.warning(f"No se pudo cargar la tabla para {sheet_name}.")
            return
        st.session_state[session_key] = data

    edited_df = st.data_editor(st.session_state[session_key], key=f"editor_{sheet_name}", num_rows="dynamic")

    # Cálculo automático para la hoja VPD_Consultores
    if sheet_name == "VPD_Consultores":
        required_cols = ["cantidad_funcionarios", "monto_mensual", "cantidad_meses"]
        if all(col in edited_df.columns for col in required_cols):
            edited_df["cantidad_funcionarios"] = pd.to_numeric(edited_df["cantidad_funcionarios"], errors="coerce").fillna(0)
            edited_df["monto_mensual"] = pd.to_numeric(edited_df["monto_mensual"], errors="coerce").fillna(0)
            edited_df["cantidad_meses"] = pd.to_numeric(edited_df["cantidad_meses"], errors="coerce").fillna(0)
            edited_df["total"] = edited_df["cantidad_funcionarios"] * edited_df["monto_mensual"] * edited_df["cantidad_meses"]
        else:
            st.warning("No se encontraron las columnas necesarias (cantidad_funcionarios, monto_mensual, cantidad_meses) para calcular el total.")

    if st.button("Guardar Cambios", key=f"guardar_{sheet_name}"):
        edited_df.columns = edited_df.columns.str.strip().str.lower()
        st.session_state[session_key] = edited_df
        save_data(excel_file, sheet_name, edited_df)
        st.success("Cambios guardados en el archivo Excel.")
        st.cache_data.clear()

    current_df = st.session_state[session_key]
    if "total" in current_df.columns:
        try:
            current_df["total"] = pd.to_numeric(current_df["total"], errors="coerce")
            total_sum = current_df["total"].sum(numeric_only=True)
            diferencia = total_sum - monto_dpp

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Monto DPP 2025", value=f"${monto_dpp:,.0f}")
            with col2:
                st.metric(label="Suma de Total", value=f"${total_sum:,.0f}")
            with col3:
                st.metric(label="Diferencia", value=f"${diferencia:,.0f}")

            # Métricas adicionales según el sheet_name
            # VPD
            if "VPD_Misiones" in sheet_name:
                st.metric("Gastos Centralizados VPD", "$35,960")
            if "VPD_Consultores" in sheet_name:
                st.metric("Gastos Centralizados VPD", "$193,160")

            # VPO
            if "VPO_Misiones" in sheet_name:
                st.metric("Gastos Centralizados VPO", "$48,158")
            if "VPO_Consultores" in sheet_name:
                st.metric("Gastos Centralizados VPO", "$33,160")

            # VPF
            if "VPF_Misiones" in sheet_name:
                st.metric("Gastos Centralizados VPF", "$40,960")
            if "VPF_Consultores" in sheet_name:
                st.metric("Gastos Centralizados VPF", "$88,460")

        except Exception as e:
            st.warning(f"No se pudo convertir la columna 'total' a un formato numérico: {e}")
    else:
        st.error("No se encontró una columna 'total' en los datos.")

def calcular_actualizacion_tabla(vicepresidencias, tipo):
    filas = []
    for vpe, montos in vicepresidencias.items():
        requerimiento_key = f"dpp_2025_{vpe}_{tipo}_data"
        requerimiento = 0
        if requerimiento_key in st.session_state:
            data = st.session_state[requerimiento_key]
            if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
                requerimiento = data["total"].sum(numeric_only=True)

        dpp = montos[tipo]
        diferencia = requerimiento - dpp

        filas.append({
            "Unidad Organizacional": vpe,
            "Requerimiento Área": int(requerimiento),
            "DPP 2025": int(dpp),
            "Diferencia": int(diferencia)
        })

    df = pd.DataFrame(filas)
    return df

def aplicar_estilos(df):
    def resaltar_diferencia(val):
        if val == 0:
            return "background-color: green; color: white;"
        else:
            return "background-color: yellow; color: black;"
    styled_df = df.style.applymap(resaltar_diferencia, subset=["Diferencia"])
    return styled_df

def mostrar_actualizacion():
    st.title("Actualización - Resumen Consolidado")
    st.write("Estas tablas muestran el monto requerido, DPP 2025, y la diferencia para cada área.")

    vicepresidencias = {
        "VPD": {"Misiones": 168000, "Consultores": 130000},
        "VPF": {"Misiones": 138600, "Consultores": 170000},
        "VPO": {"Misiones": 434707, "Consultores": 547700},
        "VPE": {"Misiones": 28244, "Consultores": 179446},
    }

    st.subheader("Misiones")
    misiones_df = calcular_actualizacion_tabla(vicepresidencias, "Misiones")
    styled_misiones_df = aplicar_estilos(misiones_df)
    st.write(styled_misiones_df, unsafe_allow_html=True)

    st.subheader("Consultores")
    consultores_df = calcular_actualizacion_tabla(vicepresidencias, "Consultores")
    styled_consultores_df = aplicar_estilos(consultores_df)
    st.write(styled_consultores_df, unsafe_allow_html=True)

def mostrar_consolidado():
    st.title("Consolidado")

    def mostrar_tabla_formato_dos_decimales(df):
        if df is not None:
            # Seleccionamos sólo las columnas numéricas
            numeric_cols = df.select_dtypes(include=["number"]).columns
            # Aplicamos el formato sólo a las columnas numéricas
            styled_df = df.style.format("{:.2f}", subset=numeric_cols)
            st.write(styled_df, unsafe_allow_html=True)
        else:
            st.warning("No se pudo cargar la tabla.")

    st.header("Cuadro 9.")
    data_cuadro_9 = load_data(excel_file, "Cuadro_9")
    if data_cuadro_9 is not None:
        data_cuadro_9 = data_cuadro_9.reset_index(drop=True)
        mostrar_tabla_formato_dos_decimales(data_cuadro_9)
    else:
        st.warning("No se pudo cargar la hoja 'Cuadro_9'.")

    st.header("Cuadro 10.")
    data_cuadro_10 = load_data(excel_file, "Cuadro_10")
    if data_cuadro_10 is not None:
        data_cuadro_10 = data_cuadro_10.reset_index(drop=True)
        mostrar_tabla_formato_dos_decimales(data_cuadro_10)
    else:
        st.warning("No se pudo cargar la hoja 'Cuadro_10'.")

    st.header("Cuadro 11.")
    data_cuadro_11 = load_data(excel_file, "Cuadro_11")
    if data_cuadro_11 is not None:
        data_cuadro_11 = data_cuadro_11.reset_index(drop=True)
        mostrar_tabla_formato_dos_decimales(data_cuadro_11)
    else:
        st.warning("No se pudo cargar la hoja 'Cuadro_11'.")

    st.header("Consolidado DPP 2025")
    data_consolidado = load_data(excel_file, "Consolidado")
    if data_consolidado is not None:
        data_consolidado = data_consolidado.reset_index(drop=True)
        mostrar_tabla_formato_dos_decimales(data_consolidado)
    else:
        st.warning("No se pudo cargar la hoja 'Consolidado'.")

def main():
    if not st.session_state.authenticated:
        st.title("Gestión Presupuestaria")
        username_input = st.text_input("Usuario", key="login_username")
        password_input = st.text_input("Contraseña", type="password", key="login_password")
        login_button = st.button("Ingresar", key="login_button")

        if login_button:
            if username_input in app_credentials and password_input == app_credentials[username_input]:
                st.session_state.authenticated = True
                st.session_state.current_user = username_input
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    else:
        pages = list(page_passwords.keys())
        selected_page = st.sidebar.selectbox("Selecciona una página", pages)

        if selected_page == "Principal":
            st.title("Página Principal - Gestión Presupuestaria")
            st.write("Bienvenido a la aplicación de Gestión Presupuestaria.")
        elif selected_page == "Actualización":
            if not st.session_state.page_authenticated["Actualización"]:
                password = st.text_input("Contraseña para Actualización", type="password")
                if st.button("Ingresar"):
                    if password == page_passwords["Actualización"]:
                        st.session_state.page_authenticated["Actualización"] = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
            else:
                mostrar_actualizacion()

        elif selected_page in ["VPD", "VPF", "VPO", "VPE"]:
            if not st.session_state.page_authenticated[selected_page]:
                password = st.text_input(f"Contraseña para {selected_page}", type="password")
                if st.button("Ingresar"):
                    if password == page_passwords[selected_page]:
                        st.session_state.page_authenticated[selected_page] = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
            else:
                subpage_options = ["Misiones", "Consultorías"]
                selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

                montos = {
                    "VPD": {"Misiones": 168000, "Consultores": 130000},
                    "VPF": {"Misiones": 138600, "Consultores": 170000},
                    "VPO": {"Misiones": 434707, "Consultores": 547700},
                    "VPE": {"Misiones": 28244, "Consultores": 179446},
                }

                if selected_page == "VPD":
                    if selected_subpage == "Misiones":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPD_Misiones")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPD_Misiones", montos["VPD"]["Misiones"])

                    elif selected_subpage == "Consultorías":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPD_Consultores")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPD_Consultores", montos["VPD"]["Consultores"])

                elif selected_page == "VPO":
                    if selected_subpage == "Misiones":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPO_Misiones")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPO_Misiones", montos["VPO"]["Misiones"])

                    elif selected_subpage == "Consultorías":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPO_Consultores")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPO_Consultores", montos["VPO"]["Consultores"])

                elif selected_page == "VPF":
                    if selected_subpage == "Misiones":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPF_Misiones")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPF_Misiones", montos["VPF"]["Misiones"])

                    elif selected_subpage == "Consultorías":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPF_Consultores")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPF_Consultores", montos["VPF"]["Consultores"])

                else:
                    # VPE
                    if selected_subpage == "Misiones":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPE_Misiones")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPE_Misiones", montos["VPE"]["Misiones"])

                    elif selected_subpage == "Consultorías":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area("VPE_Consultores")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor("VPE_Consultores", montos["VPE"]["Consultores"])

        elif selected_page == "PRE":
            if not st.session_state.page_authenticated["PRE"]:
                password = st.text_input("Contraseña para PRE", type="password")
                if st.button("Ingresar"):
                    if password == page_passwords["PRE"]:
                        st.session_state.page_authenticated["PRE"] = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
            else:
                st.title("PRE")
                subpage_options = ["Misiones Personal", "Misiones Consultores", "Servicios Profesionales", "Gastos Centralizados"]
                selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

                if selected_subpage == "Misiones Personal":
                    mostrar_requerimiento_area("PRE_Misiones_personal")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Gasto Centralizados VPD", "$35,960")
                    with col2:
                        st.metric("Gasto Centralizados VPO", "$48,158")

                    col3, _ = st.columns([1,1])
                    with col3:
                        st.metric("Gasto Centralizados VPF", "$40,960")

                elif selected_subpage == "Misiones Consultores":
                    mostrar_requerimiento_area("PRE_Misiones_consultores")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Gasto Centralizados VPD", "$13,160")
                    with col2:
                        st.metric("Gasto Centralizados VPO", "$13,160")

                    col3, _ = st.columns([1,1])
                    with col3:
                        st.metric("Gasto Centralizados VPF", "$13,160")

                elif selected_subpage == "Servicios Profesionales":
                    mostrar_requerimiento_area("PRE_servicios_profesionales")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Gasto Centralizados VPD", "$180,000")
                    with col2:
                        st.metric("Gasto Centralizados VPO", "$144,000")

                    col3, _ = st.columns([1,1])
                    with col3:
                        st.metric("Gasto Centralizados VPF", "$140,000")

                elif selected_subpage == "Gastos Centralizados":
                    st.write("Sube un archivo para Gastos Centralizados.")
                    uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
                    if uploaded_file:
                        data = pd.read_excel(uploaded_file, engine="openpyxl")
                        st.write("Archivo cargado:")
                        st.dataframe(data)

        elif selected_page == "Consolidado":
            if not st.session_state.page_authenticated["Consolidado"]:
                password = st.text_input("Contraseña para Consolidado", type="password")
                if st.button("Ingresar"):
                    if password == page_passwords["Consolidado"]:
                        st.session_state.page_authenticated["Consolidado"] = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
            else:
                mostrar_consolidado()

if __name__ == "__main__":
    main()
