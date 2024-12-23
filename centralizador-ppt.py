import streamlit as st
import pandas as pd
import openpyxl
import os
import io

# Configuración de la aplicación
st.set_page_config(
    page_title="Gestión Presupuestaria",
    page_icon="📊",
    layout="wide"
)

logo_path = "estrellafon_transparente.png"

def titulo_con_logo(titulo):
    col1, col2 = st.columns([0.1, 1])
    with col1:
        st.image(logo_path, width=50)
    with col2:
        st.title(titulo)

# Credenciales globales
app_credentials = {
    "luciana_botafogo": "fonplata",
    "mcalvino": "2025presupuesto",
    "ajustinianon": "2025presupuesto"
}

# Contraseñas por página
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
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return None

def save_data(filepath, sheet_name, df):
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
    area_key = f"req_area_data_{sheet_name}"
    if area_key not in st.session_state:
        data = load_data(excel_file, sheet_name)
        st.session_state[area_key] = data
    else:
        data = st.session_state[area_key]

    if data is not None:
        if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
            total_sum = data["total"].sum(numeric_only=True)
            st.metric("Total Requerido", f"${total_sum:,.0f}")
        st.dataframe(data)
    else:
        st.warning(f"No se pudo cargar la tabla para {sheet_name}.")

def recalcular_formulas(sheet_name, df):
    # Para VPD_Consultores y VPO_Consultores (como ejemplo de fórmula)
    if sheet_name in ["VPD_Consultores", "VPO_Consultores"]:
        required_cols = ["cantidad_funcionarios", "monto_mensual", "cantidad_meses"]
        if all(col in df.columns for col in required_cols):
            df["cantidad_funcionarios"] = pd.to_numeric(df["cantidad_funcionarios"], errors="coerce").fillna(0)
            df["monto_mensual"] = pd.to_numeric(df["monto_mensual"], errors="coerce").fillna(0)
            df["cantidad_meses"] = pd.to_numeric(df["cantidad_meses"], errors="coerce").fillna(0)
            df["total"] = df["cantidad_funcionarios"] * df["monto_mensual"] * df["cantidad_meses"]
    return df

def mostrar_dpp_2025_editor(sheet_name, monto_dpp):
    st.header(f"DPP 2025 - {sheet_name}")

    session_key = f"dpp_2025_{sheet_name}_data"
    if session_key not in st.session_state:
        data = load_data(excel_file, sheet_name)
        if data is None:
            st.warning(f"No se pudo cargar la tabla para {sheet_name}.")
            return
        st.session_state[session_key] = data

    current_df = st.session_state[session_key]

    # Editor principal
    edited_df = st.data_editor(
        current_df, 
        key=f"editor_{sheet_name}", 
        num_rows="dynamic"
    )

    # Recalcular fórmulas si aplica
    edited_df = recalcular_formulas(sheet_name, edited_df)
    st.session_state[session_key] = edited_df

    # ---------------------------------------------
    # BLOQUE PRINCIPAL PARA CALCULAR Y MOSTRAR LOS TOTALES
    # ---------------------------------------------
    if "total" in edited_df.columns:
        try:
            edited_df["total"] = pd.to_numeric(edited_df["total"], errors="coerce")
            total_sum = edited_df["total"].sum(numeric_only=True)
            diferencia = total_sum - monto_dpp

            # Primera fila de métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Monto DPP 2025", value=f"${monto_dpp:,.0f}")
            with col2:
                st.metric(label="Suma de Total", value=f"${total_sum:,.0f}")
            with col3:
                st.metric(label="Diferencia", value=f"${diferencia:,.0f}")

            # Ejemplos de gastos centralizados (si aplica):
            if "VPD_Consultores" in sheet_name:
                gcvpd = 193160
                suma_comb = gcvpd + total_sum
                colA, colB, colC = st.columns(3)
                with colA:
                    st.metric("Gastos Centralizados VPD", f"${gcvpd:,.0f}")
                with colB:
                    st.metric("GCVPD + Suma de Total", f"${suma_comb:,.0f}")

            if "VPO_Consultores" in sheet_name:
                gcvpo = 33160
                suma_comb = gcvpo + total_sum
                colA, colB, colC = st.columns(3)
                with colA:
                    st.metric("Gastos Centralizados VPO", f"${gcvpo:,.0f}")
                with colB:
                    st.metric("GCVPO + Suma de Total", f"${suma_comb:,.0f}")

            if "VPD_Misiones" in sheet_name:
                gcvpd_misiones = 35960
                suma_comb_misiones = gcvpd_misiones + total_sum
                colA, colB, colC = st.columns(3)
                with colA:
                    st.metric("Gastos Centralizados VPD", f"${gcvpd_misiones:,.0f}")
                with colB:
                    st.metric("GCVPD + Suma de Total", f"${suma_comb_misiones:,.0f}")

            if "VPO_Misiones" in sheet_name:
                gcvpo_misiones = 48158
                suma_comb_vpo_misiones = gcvpo_misiones + total_sum
                colA, colB, colC = st.columns(3)
                with colA:
                    st.metric("Gastos Centralizados VPO", f"${gcvpo_misiones:,.0f}")
                with colB:
                    st.metric("GCVPO + Suma de Total", f"${suma_comb_vpo_misiones:,.0f}")

        except Exception as e:
            st.warning(f"No se pudo convertir la columna 'total' a formato numérico: {e}")
    else:
        st.error("No se encontró una columna 'total' en los datos.")

    # ===============================================
    # === BLOQUE AGREGADO PARA TABLA DE SUMAS ===
    # ===============================================
    ### Solo queremos que aparezca si es "Misiones":
    if "Misiones" in sheet_name:
        # Definimos las columnas que deseamos sumar:
        columnas_de_suma = [
            "total_pasaje", 
            "total_alojamiento", 
            "total_perdiem_otros", 
            "total_movilidad", 
            "total"
        ]
        # Creamos un diccionario con los nombres de columna y sus sumas
        suma_dict = {}
        for col in columnas_de_suma:
            if col in edited_df.columns:
                # Convertimos a numérico con fillna(0) para evitar errores
                edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)
                suma_dict[col] = edited_df[col].sum()
            else:
                suma_dict[col] = 0

        # Convertimos en dataframe para mostrar como tabla
        suma_df = pd.DataFrame([suma_dict])
        
        st.subheader("Suma por columnas (Misiones)")
        st.dataframe(suma_df.style.format("{:,.2f}"))

    # ===============================================
    # Botón para guardar cambios
    # ===============================================
    if st.button("Guardar Cambios", key=f"guardar_{sheet_name}"):
        df_to_save = st.session_state[session_key].copy()
        # Normalizamos los nombres de columna
        df_to_save.columns = df_to_save.columns.str.strip().str.lower()
        save_data(excel_file, sheet_name, df_to_save)
        st.success("Cambios guardados en el archivo Excel.")
        # Borramos la caché para que se recarguen datos
        st.cache_data.clear()

    # Botón para descargar Excel actualizado
    df_download = st.session_state[session_key].copy()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_download.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)

    st.download_button(
        label="Descargar Excel",
        data=output.getvalue(),
        file_name=f"{sheet_name}_modificado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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
    return df.style.applymap(resaltar_diferencia, subset=["Diferencia"])

def mostrar_actualizacion():
    titulo_con_logo("Actualización - Resumen Consolidado")
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
    titulo_con_logo("Consolidado")

    def custom_formatter(value):
        if pd.isna(value):
            return ""
        elif isinstance(value, (int, float)):
            return f"{value:,.2f}"
        return str(value)

    filas_cuadro_9 = [7]
    filas_cuadro_10 = [0, 7, 14, 21, 24]

    filas_consolidado_color = [5, 15, 22, 31, 40, 47, 52]
    filas_negro = [0, 4, 6, 7, 14, 16, 21, 23, 30, 32, 39, 41, 46, 48]

    st.header("Gastos en Personal 2025 vs 2024 (Cuadro 9 - DPP 2025)")
    data_cuadro_9 = load_data(excel_file, "Cuadro_9")
    if data_cuadro_9 is not None:
        data_cuadro_9 = data_cuadro_9.reset_index(drop=True)
        styled_cuadro_9 = data_cuadro_9.style.format(custom_formatter)
        def resaltar_filas_9(row):
            if row.name in filas_cuadro_9:
                return ['background-color: #9d0208; color: white'] * len(row)
            else:
                return [''] * len(row)
        styled_cuadro_9 = styled_cuadro_9.apply(resaltar_filas_9, axis=1)
        st.write(styled_cuadro_9, unsafe_allow_html=True)
    else:
        st.warning("No se pudo cargar la hoja 'Cuadro_9'.")

    st.header("Análisis de Cambios en Gastos de Personal 2025 vs. 2024 (Cuadro 10 - DPP 2025)")
    data_cuadro_10 = load_data(excel_file, "Cuadro_10")
    if data_cuadro_10 is not None:
        data_cuadro_10 = data_cuadro_10.reset_index(drop=True)
        styled_cuadro_10 = data_cuadro_10.style.format(custom_formatter)
        def resaltar_filas_10(row):
            if row.name in filas_cuadro_10:
                return ['background-color: #9d0208; color: white'] * len(row)
            else:
                return [''] * len(row)
        styled_cuadro_10 = styled_cuadro_10.apply(resaltar_filas_10, axis=1)
        st.write(styled_cuadro_10, unsafe_allow_html=True)
    else:
        st.warning("No se pudo cargar la hoja 'Cuadro_10'.")

    st.header("Gastos Operativos propuestos para 2025 y montos aprobados para 2024 (Cuadro 11 - DPP 2025)")
    data_cuadro_11 = load_data(excel_file, "Cuadro_11")
    if data_cuadro_11 is not None:
        data_cuadro_11 = data_cuadro_11.reset_index(drop=True)
        styled_cuadro_11 = data_cuadro_11.style.format(custom_formatter)
        st.write(styled_cuadro_11, unsafe_allow_html=True)
    else:
        st.warning("No se pudo cargar la hoja 'Cuadro_11'.")

    st.header("Consolidado DPP 2025")
    data_consolidado = load_data(excel_file, "Consolidado")
    if data_consolidado is not None:
        data_consolidado = data_consolidado.reset_index(drop=True)
        styled_consolidado = data_consolidado.style.format(custom_formatter)

        def color_todas_filas(row):
            return ['color: #8d99ae;'] * len(row)

        def color_filas_negro(row):
            if row.name in filas_negro:
                return ['color: black;'] * len(row)
            else:
                return [''] * len(row)

        def resaltar_filas_consolidado(row):
            if row.name in filas_consolidado_color:
                return ['background-color: #9d0208; color: white'] * len(row)
            else:
                return [''] * len(row)

        styled_consolidado = styled_consolidado.apply(color_todas_filas, axis=1)
        styled_consolidado = styled_consolidado.apply(color_filas_negro, axis=1)
        styled_consolidado = styled_consolidado.apply(resaltar_filas_consolidado, axis=1)

        st.write(styled_consolidado, unsafe_allow_html=True)
    else:
        st.warning("No se pudo cargar la hoja 'Consolidado'.")

def main():
    if not st.session_state.authenticated:
        titulo_con_logo("Página Principal - Gestión Presupuestaria")
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

        st.write("**Instrucciones de uso:**")
        st.write("""
        1. Selecciona la página que deseas visitar desde el menú lateral.
        2. Ingresa las credenciales si la página lo requiere.
        3. En las páginas de "Requerimiento de Área" podrás visualizar el total requerido sin que éste cambie luego de modificar datos en las páginas DPP 2025.
        4. En las páginas DPP 2025 puedes editar las tablas y luego guardar los cambios. También puedes descargar el Excel modificado.
        5. La página "Actualización" muestra un resumen consolidado, mientras que "Consolidado" presenta distintos cuadros con sus cifras.
        6. Si en algún momento deseas volver a la página principal, selecciona "Principal" en el menú lateral.
        """)
        st.write("**Nota:** Asegúrate de tener las contraseñas correctas para acceder a las páginas protegidas y editar los datos.")

    else:
        pages = list(page_passwords.keys())
        selected_page = st.sidebar.selectbox("Selecciona una página", pages)

        if selected_page == "Principal":
            titulo_con_logo("Página Principal - Gestión Presupuestaria")
            st.write("**Instrucciones de uso:**")
            st.write("""
            1. Selecciona la página que deseas visitar desde el menú lateral.
            2. Ingresa las credenciales si la página lo requiere.
            3. En las páginas de "Requerimiento de Área" podrás visualizar el total requerido sin que éste cambie luego de modificar datos en las páginas DPP 2025.
            4. En las páginas DPP 2025 puedes editar las tablas y luego guardar los cambios. También puedes descargar el Excel modificado.
            5. La página "Actualización" muestra un resumen consolidado, mientras que "Consolidado" presenta distintos cuadros con sus cifras.
            6. Si en algún momento deseas volver a la página principal, selecciona "Principal" en el menú lateral.
            """)
            st.write("**Nota:** Asegúrate de tener las contraseñas correctas para acceder a las páginas protegidas y editar los datos.")

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

        elif selected_page in ["VPD", "VPF", "VPO", "VPE", "PRE", "Consolidado"]:
            if selected_page == "Consolidado":
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
                    subpage_options = ["Misiones Personal", "Misiones Consultores", "Servicios Profesionales", "Gastos Centralizados"]
                    selected_subpage = st.sidebar.selectbox("Selecciona una subpágina", subpage_options)

                    # Ejemplo de uso en PRE
                    if selected_subpage == "Misiones Personal":
                        mostrar_requerimiento_area("PRE_Misiones_personal")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Gasto Centralizados VPD", "$35,960")
                        with col2:
                            st.metric("Gasto Centralizados VPO", "$48,158")

                        col3, col4 = st.columns(2)
                        with col3:
                            st.metric("Gasto Centralizados VPF", "$40,960")
                        with col4:
                            st.metric("Gasto Centralizados PRE", "$60,168")

                    elif selected_subpage == "Misiones Consultores":
                        mostrar_requerimiento_area("PRE_Misiones_consultores")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Gasto Centralizados VPD", "$13,160")
                        with col2:
                            st.metric("Gasto Centralizados VPO", "$13,160")

                        col3, col4 = st.columns(2)
                        with col3:
                            st.metric("Gasto Centralizados VPF", "$13,160")
                        with col4:
                            st.metric("Gasto Centralizados PRE", "$30,872")

                    elif selected_subpage == "Servicios Profesionales":
                        mostrar_requerimiento_area("PRE_servicios_profesionales")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Gasto Centralizados VPD", "$180,000")
                        with col2:
                            st.metric("Gasto Centralizados VPO", "$144,000")

                        col3, col4 = st.columns(2)
                        with col3:
                            st.metric("Gasto Centralizados VPF", "$140,000")
                        with col4:
                            st.metric("Gasto Centralizados PRE", "$932,608")

                    elif selected_subpage == "Gastos Centralizados":
                        st.write("Sube un archivo para Gastos Centralizados.")
                        uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
                        if uploaded_file:
                            data = pd.read_excel(uploaded_file, engine="openpyxl")
                            st.write("Archivo cargado:")
                            st.dataframe(data)
            else:
                # VPD, VPO, VPF, VPE
                page = selected_page
                if not st.session_state.page_authenticated[page]:
                    password = st.text_input(f"Contraseña para {page}", type="password")
                    if st.button("Ingresar"):
                        if password == page_passwords[page]:
                            st.session_state.page_authenticated[page] = True
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

                    if selected_subpage == "Misiones":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Misiones", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area(f"{page}_Misiones")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor(f"{page}_Misiones", montos[page]["Misiones"])

                    elif selected_subpage == "Consultorías":
                        subsubpage_options = ["Requerimiento de Área", "DPP 2025"]
                        selected_subsubpage = st.sidebar.radio("Selecciona una subpágina de Consultorías", subsubpage_options)
                        if selected_subsubpage == "Requerimiento de Área":
                            mostrar_requerimiento_area(f"{page}_Consultores")
                        elif selected_subsubpage == "DPP 2025":
                            mostrar_dpp_2025_editor(f"{page}_Consultores", montos[page]["Consultores"])

if __name__ == "__main__":
    main()
