import streamlit as st
import pandas as pd

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
    """
    Carga datos desde un archivo Excel.
    """
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error al cargar la hoja '{sheet_name}': {e}")
        return None

# Ruta al archivo Excel
excel_file = "main_bdd.xlsx"

def get_vpd_consultores_data():
    """
    Devuelve un DataFrame con los datos codificados para VPD_Consultores.
    """
    data = {
        "cargo": [
            "Consultores Nivel Analistas",
            "Consultores Nivel Analista",
            "Consultores Nivel Analista"
        ],
        "vpd_area": [
            "EEE",
            "EED",
            "AIE"
        ],
        "cantidad_funcionarios": [2, 2, 1],
        "monto_mensual": [4500, 4500, 4500],
        "cantidad_meses": [10, 10, 10]
    }
    df = pd.DataFrame(data)
    df['total'] = df['cantidad_funcionarios'] * df['monto_mensual'] * df['cantidad_meses']
    return df

def mostrar_subpagina(sheet_name, misiones_PRE=0, misiones_VPO=0, misiones_VPD=0, misiones_VPF=0, download_filename='', mostrar_boxes=True):
    """
    Muestra una subpágina con una tabla específica cargada desde Excel.
    """
    data = load_data(excel_file, sheet_name)
    if data is not None:
        # Ajustar el subheader según la hoja
        if sheet_name == "PRE_Misiones_personal":
            subheader_text = "Tabla Misiones Personal"
        elif sheet_name == "PRE_Misiones_consultores":
            subheader_text = "Tabla Misiones Consultores"
        else:
            # Para otros casos, lógica original
            tabla_nombre = sheet_name.split('_')[-1].replace('_', ' ').title()
            subheader_text = f"Tabla de {tabla_nombre}"

        st.subheader(subheader_text)

        # Mostrar métrica total si existe la columna 'total'
        if "total" in data.columns:
            if pd.api.types.is_numeric_dtype(data["total"]):
                total_sum = data["total"].sum()
                st.metric(label="Total", value=f"${total_sum:,.2f}")
            else:
                st.warning("La columna 'total' no es numérica.")
        else:
            st.warning("No existe la columna 'total' en la hoja.")

        # Mostrar la tabla de datos
        st.dataframe(data)

        # Mostrar métricas adicionales si `mostrar_boxes` es True
        if mostrar_boxes:
            st.markdown("### Resumen de Misiones de Servicio")
            total_sum = data["total"].sum() if ("total" in data.columns and pd.api.types.is_numeric_dtype(data["total"])) else 0
            total_misiones = misiones_PRE + misiones_VPO + misiones_VPD + misiones_VPF
            total_plus_montos = total_sum + total_misiones

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Misiones de Servicio cargadas a PRE", f"${misiones_PRE:,.0f}")
                st.metric("Misiones de Servicio cargadas a VPF", f"${misiones_VPF:,.0f}")
            with col2:
                st.metric("Misiones de Servicio cargadas a VPD", f"${misiones_VPD:,.0f}")
                st.metric("Misiones de Servicio cargadas a VPO", f"${misiones_VPO:,.0f}")

            st.metric("Total + Montos cargados a otras VPs", f"${total_plus_montos:,.2f}")

        # Botón de descarga si se especifica un nombre de archivo
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
    """
    Muestra la página DPP 2025 - Misiones con una tabla editable.
    """
    st.header("DPP 2025 - Misiones")
    st.write("Edite los valores en la tabla a continuación:")

    data = load_data(excel_file, "VPD_Misiones")
    if data is not None:
        required_columns = ['pais', 'operacion', 'vpd_area', 'cant_funcionarios', 'dias', 'costo_pasaje', 'alojamiento', 'perdiem_otros', 'movilidad', 'total']
        if not all(col in data.columns for col in required_columns):
            st.error(f"Faltan columnas en VPD_Misiones. Se requieren: {required_columns}")
            return

        if 'dpp_2025_data' not in st.session_state:
            st.session_state.dpp_2025_data = data.copy()

        edited_data = st.data_editor(
            st.session_state.dpp_2025_data,
            num_rows="dynamic",
            use_container_width=True,
            key="dpp_2025_table_misiones",
            column_config={
                "pais": st.column_config.TextColumn("País"),
                "operacion": st.column_config.TextColumn("Operación"),
                "vpd_area": st.column_config.TextColumn("VPD Área"),
                "cant_funcionarios": st.column_config.NumberColumn("Cantidad de Funcionarios", step=1, format="%d"),
                "dias": st.column_config.NumberColumn("Días", step=1, format="%d"),
                "costo_pasaje": st.column_config.NumberColumn("Costo Pasaje por Funcionario", step=100.0, format="$%.2f"),
                "alojamiento": st.column_config.NumberColumn("Alojamiento por Día por Funcionario", step=50.0, format="$%.2f"),
                "perdiem_otros": st.column_config.NumberColumn("Perdiem Otros por Día por Funcionario", step=20.0, format="$%.2f"),
                "movilidad": st.column_config.NumberColumn("Costo de Movilidad por Funcionario", step=30.0, format="$%.2f"),
                "total": st.column_config.NumberColumn("Total", disabled=True, format="$%.2f")
            }
        )

        # Actualizar el estado con los datos editados
        st.session_state.dpp_2025_data = edited_data

        # Recalcular la columna 'total'
        st.session_state.dpp_2025_data['total'] = (
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['costo_pasaje'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['dias'] * st.session_state.dpp_2025_data['alojamiento'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['dias'] * st.session_state.dpp_2025_data['perdiem_otros'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['movilidad']
        )

        # Cálculo de métricas adicionales
        total_sum = st.session_state.dpp_2025_data['total'].sum()
        monto_deseado = 168000
        diferencia = monto_deseado - total_sum
        diff_sign = "+" if diferencia >= 0 else "-"
        diff_value = f"{diff_sign}${abs(diferencia):,.2f}"

        st.markdown("### Resultados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total 💰", f"${total_sum:,.2f}")
        with col2:
            st.metric("Monto Deseado 🎯", f"${monto_deseado:,.2f}")
        with col3:
            st.metric("Diferencia ➖", diff_value)
    else:
        st.warning("No se pudo cargar la tabla VPD_Misiones para DPP 2025.")

def mostrar_dpp_2025_consultores():
    st.header("DPP 2025 - Consultores")
    st.write("Edite los valores en la tabla a continuación:")

    # Cargar datos sólo si no existen en session_state
    if "dpp_2025_consultores_data" not in st.session_state:
        st.session_state.dpp_2025_consultores_data = get_vpd_consultores_data()

    # Mostrar la tabla editable
    edited_data = st.data_editor(
        st.session_state.dpp_2025_consultores_data,
        num_rows="dynamic",
        use_container_width=True,
        key="dpp_2025_consultores_table",
        column_config={
            "cargo": st.column_config.TextColumn("Cargo"),
            "vpd_area": st.column_config.TextColumn("VPD Área"),
            "cantidad_funcionarios": st.column_config.NumberColumn("Cantidad de Funcionarios", step=1, format="%d"),
            "monto_mensual": st.column_config.NumberColumn("Monto Mensual", step=100.0, format="$%.2f"),
            "cantidad_meses": st.column_config.NumberColumn("Cantidad de Meses", step=1, format="%d"),
            "total": st.column_config.NumberColumn("Total", disabled=True, format="$%.2f")
        }
    )

    # Actualizar session_state con los datos editados
    st.session_state.dpp_2025_consultores_data = edited_data

    # Recalcular la columna 'total'
    st.session_state.dpp_2025_consultores_data['total'] = (
        st.session_state.dpp_2025_consultores_data['cantidad_funcionarios'] *
        st.session_state.dpp_2025_consultores_data['monto_mensual'] *
        st.session_state.dpp_2025_consultores_data['cantidad_meses']
    )

    # Cálculo de métricas adicionales
    total_sum = st.session_state.dpp_2025_consultores_data['total'].sum()
    monto_deseado = 130000
    diferencia = monto_deseado - total_sum
    diff_sign = "+" if diferencia >= 0 else "-"
    diff_value = f"{diff_sign}${abs(diferencia):,.2f}"

    st.markdown("### Resultados")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total 💰", f"${total_sum:,.2f}")
    with col2:
        st.metric("Monto Deseado 🎯", f"${monto_deseado:,.2f}")
    with col3:
        st.metric("Diferencia ➖", diff_value)
def pagina_actualizacion():
    """
    Muestra la página de Actualización con comparaciones entre requerimientos y DPP 2025.
    """
    st.title("Actualización")

    uos = ["VPE", "VPD", "VPO", "VPF"]

    misiones_dpp_fijo = 168000
    consultores_dpp_fijo = 130000

    misiones_rows = []
    consultores_rows = []

    for uo in uos:
        # Misiones
        if uo == "VPD" and 'dpp_2025_data' in st.session_state:
            req_misiones = st.session_state.dpp_2025_data['total'].sum()
        else:
            req_misiones = get_requerimiento(f"{uo}_Misiones")

        dpp_misiones_valor = misiones_dpp_fijo
        diff_misiones = req_misiones - dpp_misiones_valor
        misiones_rows.append([uo, req_misiones, dpp_misiones_valor, diff_misiones])

        # Consultores
        if uo == "VPD" and 'dpp_2025_consultores_data' in st.session_state:
            req_consultores = st.session_state.dpp_2025_consultores_data['total'].sum()
        else:
            req_consultores = get_requerimiento(f"{uo}_Consultores")

        dpp_consultores_valor = consultores_dpp_fijo
        diff_consultores = req_consultores - dpp_consultores_valor
        consultores_rows.append([uo, req_consultores, dpp_consultores_valor, diff_consultores])

    def color_diff(val):
        if val == 0:
            return 'background-color: green; color: white;'
        return ''

    st.subheader("Actualización - Misiones")
    misiones_df = pd.DataFrame(misiones_rows, columns=["Unidad Organizacional", "Requerimiento", "DPP 2025", "Diff"])
    misiones_styled = (misiones_df.style
                       .format({"Requerimiento": "${:,.2f}", "DPP 2025": "${:,.2f}", "Diff": "${:,.2f}"})
                       .applymap(color_diff, subset=["Diff"]))
    st.dataframe(misiones_styled, use_container_width=True)

    st.subheader("Actualización - Consultores")
    consultores_df = pd.DataFrame(consultores_rows, columns=["Unidad Organizacional", "Requerimiento", "DPP 2025", "Diff"])
    consultores_styled = (consultores_df.style
                          .format({"Requerimiento": "${:,.2f}", "DPP 2025": "${:,.2f}", "Diff": "${:,.2f}"})
                          .applymap(color_diff, subset=["Diff"]))
    st.dataframe(consultores_styled, use_container_width=True)

def pagina_consolidado():
    """
    Muestra la página de Consolidado con resúmenes generales y totales presupuestarios.
    """
    st.write("**Resumen General**")

    data_consolidado = load_data(excel_file, "consolidado_general")
    if data_consolidado is not None:
        def highlight_last(row):
            if row.name == data_consolidado.index[-1]:
                return ['background-color: #c1121f; color: white; border:1px solid black;' for _ in row]
            else:
                return ['' for _ in row]

        numeric_cols = data_consolidado.select_dtypes(include='number').columns
        consolidado_styled = (data_consolidado.style
                              .format("{:,.0f}", subset=numeric_cols)
                              .apply(highlight_last, axis=1))
        st.dataframe(consolidado_styled, use_container_width=True)
    else:
        st.warning("No se pudo cargar la hoja 'consolidado_general'.")

    st.write("**Total Presupuesto**")

    data_total = load_data(excel_file, "consolidado_total")
    if data_total is not None:
        # Filas específicas para resaltar
        grey_rows = [0, 6, 14, 20, 28, 36]
        red_rows = [4, 13, 19, 27, 35, 41, 42]

        def highlight_consolidado_total(row):
            if row.name in grey_rows:
                return ['background-color: #adb5bd; color:black; border:1px solid black;' for _ in row]
            elif row.name in red_rows:
                return ['background-color: #c1121f; color: white; border:1px solid black;' for _ in row]
            return ['' for _ in row]

        numeric_cols_total = data_total.select_dtypes(include='number').columns
        total_styled = (data_total.style
                        .format("{:,.0f}", subset=numeric_cols_total)
                        .apply(highlight_consolidado_total, axis=1))

        st.dataframe(total_styled, use_container_width=True)
    else:
        st.warning("No se pudo cargar la hoja 'consolidado_total'.")

def get_requerimiento(sheet_name):
    """
    Obtiene el requerimiento total desde una hoja específica.
    """
    data = load_data(excel_file, sheet_name)
    if data is not None and "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
        return data["total"].sum()
    return 0

def main():
    # Inicializar variables de estado si no existen
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "page_authenticated" not in st.session_state:
        st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}

    if not st.session_state.authenticated:
        # Pantalla de inicio de sesión
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
        # Navegación de páginas
        pages = list(page_passwords.keys())
        selected_page = st.sidebar.selectbox("Selecciona una página", pages)

        if selected_page == "Principal":
            # Contenido de la página principal
            st.title("Página Principal")
            st.write("Bienvenido a la página principal de la app.")
            st.write("**Instrucciones para el uso de la aplicación:**")
            st.write("- En la barra lateral izquierda, selecciona una página para navegar entre las distintas secciones.")
            st.write("- Algunas páginas requieren contraseña, introdúcela cuando se te solicite.")
            st.write("- En las páginas de DPP 2025 (Misiones y Consultores de VPD) puedes editar los datos directamente en las tablas. Los cambios se reflejarán en la página de Actualización.")
            st.write("- En la página de Consolidado puedes ver un resumen general y el total del presupuesto con diferentes colores y estilos para resaltar filas especiales.")
            st.write("- Usa los botones de descarga en las tablas para obtener los datos en formato CSV si lo deseas.")
        else:
            # Autenticación por página si es necesario
            if page_passwords[selected_page] is not None and not st.session_state.page_authenticated[selected_page]:
                st.sidebar.markdown("---")
                st.sidebar.write("**Autenticación por página**")
                password_input = st.sidebar.text_input("Ingresa la contraseña", type="password", key=f"page_password_{selected_page}")
                verify_button = st.sidebar.button("Verificar", key=f"verify_{selected_page}")

                if verify_button:
                    if password_input == page_passwords[selected_page]:
                        st.session_state.page_authenticated[selected_page] = True
                        st.rerun()
                    else:
                        st.sidebar.error("Contraseña incorrecta.")
            else:
                # Mostrar contenido de la página seleccionada
                if selected_page in subpages:
                    if selected_page not in ["Consolidado", "Actualización"]:
                        st.title(selected_page)
                        st.write(f"Contenido relacionado con {selected_page}.")

                    current_subpages = subpages[selected_page]

                    if selected_page == "Actualización":
                        pagina_actualizacion()
                    elif selected_page == "Consolidado":
                        pagina_consolidado()
                    elif selected_page == "PRE":
                        # Manejo de subpáginas de PRE
                        with st.sidebar.expander(f"Subpáginas de {selected_page}"):
                            selected_subpage = st.selectbox("Selecciona una subpágina", current_subpages, key=f"{selected_page}_subpage")

                        if selected_subpage == "Misiones Personal":
                            mostrar_subpagina(
                                sheet_name="PRE_Misiones_personal",
                                misiones_PRE=60168,
                                misiones_VPO=48158,
                                misiones_VPD=35960,
                                misiones_VPF=40960,
                                download_filename='PRE_Misiones_personal.csv',
                                mostrar_boxes=True
                            )
                        elif selected_subpage == "Misiones Consultores":
                            mostrar_subpagina(
                                sheet_name="PRE_Misiones_consultores",
                                misiones_PRE=30872,
                                misiones_VPO=13160,
                                misiones_VPD=13160,
                                misiones_VPF=13160,
                                download_filename='PRE_Misiones_consultores.csv',
                                mostrar_boxes=True
                            )
                        elif selected_subpage == "Servicios Profesionales":
                            data = load_data(excel_file, "PRE_servicios_profesionales")
                            if data is not None:
                                st.subheader("Tabla de Servicios Profesionales")
                                if "total" in data.columns and pd.api.types.is_numeric_dtype(data["total"]):
                                    total_sum = data["total"].sum()
                                    st.metric("Total", f"${total_sum:,.2f}")
                                elif "total" not in data.columns:
                                    st.warning("La columna 'total' no está en los datos.")
                                else:
                                    st.warning("La columna 'total' no es numérica.")
                                st.dataframe(data)
                                csv = data.to_csv(index=False).encode('utf-8')
                                st.download_button("Descargar datos como CSV", csv, 'PRE_servicios_profesionales.csv', 'text/csv')
                            else:
                                st.warning("No se pudo cargar la tabla de Servicios Profesionales.")

                        elif selected_subpage == "Gastos Centralizados":
                            mostrar_subpagina(
                                sheet_name="PRE_Gastos_Centralizados",
                                misiones_PRE=0,
                                misiones_VPO=0,
                                misiones_VPD=0,
                                misiones_VPF=0,
                                download_filename='PRE_Gastos_Centralizados.csv',
                                mostrar_boxes=False
                            )

                    elif selected_page == "VPD":
                        # Manejo de subpáginas de VPD
                        with st.sidebar.expander(f"Subpáginas de {selected_page}"):
                            selected_subpage = st.selectbox("Selecciona una subpágina", current_subpages, key=f"{selected_page}_subpage")

                        if selected_subpage == "Misiones":
                            misiones_options = ["Requerimiento del Área", "DPP 2025"]
                            selected_misiones_option = st.selectbox("Selecciona opción para Misiones", misiones_options, key="vpd_misiones_option")

                            if selected_misiones_option == "Requerimiento del Área":
                                mostrar_subpagina(
                                    sheet_name="VPD_Misiones",
                                    download_filename='VPD_Misiones.csv',
                                    mostrar_boxes=False
                                )
                            elif selected_misiones_option == "DPP 2025":
                                mostrar_dpp_2025()

                        elif selected_subpage == "Consultores":
                            consultores_options = ["Requerimiento del Área", "DPP 2025"]
                            selected_consultores_option = st.selectbox("Selecciona opción para Consultores", consultores_options, key="vpd_consultores_option")

                            if selected_consultores_option == "Requerimiento del Área":
                                mostrar_subpagina(
                                    sheet_name="VPD_Consultores",
                                    download_filename='VPD_Consultores.csv',
                                    mostrar_boxes=False
                                )
                            elif selected_consultores_option == "DPP 2025":
                                mostrar_dpp_2025_consultores()

                        elif selected_subpage == "Gastos Centralizados":
                            mostrar_subpagina(
                                sheet_name="VPD_Gastos_Centralizados",
                                download_filename='VPD_Gastos_Centralizados.csv',
                                mostrar_boxes=False
                            )
                        else:
                            st.warning("Subpágina no reconocida.")
                    else:
                        # Otras páginas no modificadas
                        pass
                else:
                    st.title(f"Página de {selected_page}")
                    st.write(f"Contenido relacionado con {selected_page}")

        # Botón de Cerrar Sesión en la barra lateral
        if st.sidebar.button("Cerrar sesión"):
            st.session_state.authenticated = False
            st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}
            st.rerun()

        # Elementos adicionales en la barra lateral
        st.sidebar.markdown("---")
        st.sidebar.image("estrellafon_transparent.png", width=100)

if __name__ == "__main__":
    main()
