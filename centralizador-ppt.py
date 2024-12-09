import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.set_page_config(
    page_title="Gestión Presupuestaria",
    page_icon="📊",
    layout="wide"
)

# Credenciales de acceso para la app
app_credentials = {
    "username": "luciana_botafogo",
    "password": "fonplata"
}

# Contraseñas para cada página (excepto Principal)
page_passwords = {
    "Principal": None,  # No se requiere contraseña para Principal después del login
    "PRE": "pre456",
    "VPE": "vpe789",
    "VPD": "vpd101",
    "VPO": "vpo112",
    "VPF": "vpf131",
    "Actualización": "update2023",
    "Consolidado": "consolidado321",
    "Tablero": "tablero654"
}

# Definir las subpáginas para cada página principal
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
    ]
}

# Función para cargar datos desde Excel
@st.cache_data
def load_data(filepath, sheet_name):
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None

# Ruta al archivo Excel (ajusta la ruta según la ubicación de tu archivo)
excel_file = "main_bdd.xlsx"

# Inicializar el estado de autenticación en session_state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Inicializar el diccionario de autenticación por página
if "page_authenticated" not in st.session_state:
    st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}

# Función genérica para cargar y mostrar datos con opcionalmente Value Boxes adicionales
def mostrar_subpagina(sheet_name, misiones_PRE=0, misiones_VPO=0, misiones_VPD=0, misiones_VPF=0, download_filename='', mostrar_boxes=True):
    data = load_data(excel_file, sheet_name)

    if data is not None:
        # Título de la tabla basado en el nombre de la hoja
        tabla_nombre = sheet_name.split('_')[-1].replace('_', ' ').title()
        st.subheader(f"Tabla de {tabla_nombre}")

        # Verificar si la columna 'total' existe
        if "total" in data.columns:
            # Asegurarse de que la columna 'total' es numérica
            if pd.api.types.is_numeric_dtype(data["total"]):
                total_sum = data["total"].sum()
                # Mostrar el total en un Value Box
                st.metric(label="Total", value=f"${total_sum:,.2f}")
            else:
                st.warning("La columna 'total' no es de tipo numérico.")
        else:
            st.warning("La columna 'total' no está presente en los datos.")

        # Mostrar la tabla de manera interactiva
        st.dataframe(data)

        # Si se solicitan Value Boxes adicionales, mostrarlos
        if mostrar_boxes:
            st.markdown("### Resumen de Misiones de Servicio")

            # Calcular el Total + Montos cargados a otras VPs
            total_misiones = misiones_PRE + misiones_VPO + misiones_VPD + misiones_VPF
            total_plus_montos = total_sum + total_misiones

            # Crear dos columnas para organizar los Value Boxes
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Misiones de Servicio cargadas a PRE", f"${misiones_PRE:,.0f}")
                st.metric("Misiones de Servicio cargadas a VPF", f"${misiones_VPF:,.0f}")

            with col2:
                st.metric("Misiones de Servicio cargadas a VPD", f"${misiones_VPD:,.0f}")
                st.metric("Misiones de Servicio cargadas a VPO", f"${misiones_VPO:,.0f}")

            # Agregar el Value Box del Total
            st.metric("Total + Montos cargados a otras VPs", f"${total_plus_montos:,.2f}")

        # Permitir descargar la tabla como CSV
        if download_filename:
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar datos como CSV",
                data=csv,
                file_name=download_filename,
                mime='text/csv',
            )
    else:
        st.warning(f"No se pudo cargar la tabla de {sheet_name.split('_')[-1].replace('_', ' ')}.")

# Función específica para la sub-subpágina DPP 2025
def mostrar_dpp_2025():
    st.header("DPP 2025")
    st.write("Edite los valores en la tabla a continuación:")

    # Cargar los datos desde la hoja VPD_Misiones
    data = load_data(excel_file, "VPD_Misiones")

    if data is not None:
        # Verificar que las columnas necesarias existen
        required_columns = ['pais', 'operacion', 'vpd_area', 'cant_funcionarios', 'dias', 'costo_pasaje', 'alojamiento', 'perdiem_otros', 'movilidad', 'total']
        if not all(col in data.columns for col in required_columns):
            st.error(f"Las columnas requeridas {required_columns} no están todas presentes en la hoja VPD_Misiones.")
            return

        # Inicializar el dataframe editable en session_state si no existe
        if 'dpp_2025_data' not in st.session_state:
            st.session_state.dpp_2025_data = data.copy()

        # Mostrar la tabla editable
        edited_data = st.experimental_data_editor(
            st.session_state.dpp_2025_data,
            num_rows="dynamic",
            use_container_width=True,
            key="dpp_2025_table",
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

        # Actualizar el dataframe en session_state con los datos editados
        st.session_state.dpp_2025_data = edited_data

        # Recalcular la columna 'total' según la fórmula proporcionada
        st.session_state.dpp_2025_data['total'] = (
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['costo_pasaje'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['dias'] * st.session_state.dpp_2025_data['alojamiento'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['dias'] * st.session_state.dpp_2025_data['perdiem_otros'] +
            st.session_state.dpp_2025_data['cant_funcionarios'] * st.session_state.dpp_2025_data['movilidad']
        )

        # Mostrar la tabla actualizada
        st.dataframe(st.session_state.dpp_2025_data)

        # Calcular los Value Boxes
        total_sum = st.session_state.dpp_2025_data['total'].sum()
        monto_deseado = 168000
        diferencia = total_sum - monto_deseado

        # Mostrar los Value Boxes
        st.markdown("### Resultados")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total 💰", f"${total_sum:,.2f}")
        with col2:
            st.metric("Monto Deseado 🎯", f"${monto_deseado:,.2f}")
        with col3:
            st.metric("Diferencia ➖", f"${diferencia:,.2f}")
    else:
        st.warning("No se pudo cargar la tabla de Misiones para DPP 2025.")

# Verificar si el usuario está autenticado globalmente
if not st.session_state.authenticated:
    st.title("Gestión Presupuestaria")
    username_input = st.text_input("Usuario", key="login_username")
    password_input = st.text_input("Contraseña", type="password", key="login_password")
    login_button = st.button("Ingresar", key="login_button")

    if login_button:
        if username_input == app_credentials["username"] and password_input == app_credentials["password"]:
            st.session_state.authenticated = True
            st.session_state.current_page = "Principal"
            st.rerun()  # Actualizar la página automáticamente
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    # Menú desplegable en la barra lateral
    pages = list(page_passwords.keys())
    selected_page = st.sidebar.selectbox("Selecciona una página", pages)

    # Solicitar contraseña solo para páginas distintas a Principal y no autenticadas
    if selected_page == "Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la página principal de la app.")
    else:
        # Verificar si la página ya ha sido autenticada
        if not st.session_state.page_authenticated[selected_page]:
            st.sidebar.markdown("---")
            st.sidebar.write("**Autenticación por página**")
            password_input = st.sidebar.text_input("Ingresa la contraseña", type="password", key=f"page_password_{selected_page}")

            # Botón para verificar la contraseña
            verify_button = st.sidebar.button("Verificar", key=f"verify_{selected_page}")

            if verify_button:
                if password_input == page_passwords[selected_page]:
                    st.session_state.page_authenticated[selected_page] = True
                    st.rerun()  # Actualizar la página automáticamente
                else:
                    st.sidebar.error("Contraseña incorrecta.")
        else:
            # Si la página está autenticada, mostrar el contenido directamente
            if selected_page in subpages:
                st.title(selected_page)
                st.write(f"Contenido relacionado con {selected_page}.")

                # Obtener las subpáginas correspondientes
                current_subpages = subpages[selected_page]

                # Expander para Subpáginas en el Sidebar
                with st.sidebar.expander(f"Subpáginas de {selected_page}"):
                    selected_subpage = st.selectbox("Selecciona una subpágina", current_subpages, key=f"{selected_page}_subpage")

                # Lógica para cada subpágina
                if selected_page == "PRE":
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
                        # Para "Servicios Profesionales", solo se requiere un Value Box arriba de la tabla
                        data = load_data(excel_file, "PRE_servicios_profesionales")

                        if data is not None:
                            st.subheader("Tabla de Servicios Profesionales")

                            # Verificar si la columna 'total' existe
                            if "total" in data.columns:
                                if pd.api.types.is_numeric_dtype(data["total"]):
                                    total_sum = data["total"].sum()
                                    st.metric(label="Total", value=f"${total_sum:,.2f}")
                                else:
                                    st.warning("La columna 'total' no es de tipo numérico.")
                            else:
                                st.warning("La columna 'total' no está presente en los datos.")

                            # Mostrar la tabla de manera interactiva
                            st.dataframe(data)

                            # Permitir descargar la tabla como CSV
                            csv = data.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Descargar datos como CSV",
                                data=csv,
                                file_name='PRE_servicios_profesionales.csv',
                                mime='text/csv',
                            )
                        else:
                            st.warning("No se pudo cargar la tabla de Servicios Profesionales.")

                    elif selected_subpage == "Gastos Centralizados":
                        mostrar_subpagina(
                            sheet_name="PRE_Gastos_Centralizados",
                            misiones_PRE=0,  # Asumiendo que no hay valores predefinidos
                            misiones_VPO=0,
                            misiones_VPD=0,
                            misiones_VPF=0,
                            download_filename='PRE_Gastos_Centralizados.csv',
                            mostrar_boxes=False  # No se muestran Value Boxes adicionales
                        )

                elif selected_page == "VPD":
                    if selected_subpage == "Misiones":
                        # Dentro de "VPD" -> "Misiones", añadir una selección para "Requerimiento del Área" y "DPP 2025"
                        with st.expander("Selecciona una opción dentro de Misiones"):
                            misiones_options = ["Requerimiento del Área", "DPP 2025"]
                            selected_misiones_option = st.selectbox("Selecciona una opción", misiones_options, key="vpd_misiones_option")

                        if selected_misiones_option == "Requerimiento del Área":
                            mostrar_subpagina(
                                sheet_name="VPD_Misiones",
                                download_filename='VPD_Misiones.csv',
                                mostrar_boxes=False  # Solo el Value Box arriba de la tabla
                            )
                        elif selected_misiones_option == "DPP 2025":
                            mostrar_dpp_2025()
                        else:
                            st.warning("Opción no reconocida.")

                    elif selected_subpage == "Consultores":
                        mostrar_subpagina(
                            sheet_name="VPD_Consultores",
                            download_filename='VPD_Consultores.csv',
                            mostrar_boxes=False  # Solo el Value Box arriba de la tabla
                        )
                    elif selected_subpage == "Gastos Centralizados":
                        mostrar_subpagina(
                            sheet_name="VPD_Gastos_Centralizados",
                            download_filename='VPD_Gastos_Centralizados.csv',
                            mostrar_boxes=False  # Solo el Value Box arriba de la tabla
                        )
                else:
                    st.warning("Subpágina no reconocida.")
            else:
                # Manejo de otras páginas que no están en el diccionario de subpáginas
                st.title(f"Página de {selected_page}")
                st.write(f"Contenido relacionado con {selected_page}.")

    # Botón de logout
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.authenticated = False
        # Reiniciar la autenticación por página
        st.session_state.page_authenticated = {page: False for page in page_passwords if page_passwords[page]}
        st.rerun()  # Regresar al login

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.write("**Desarrollado por FONPLATA - Efectividad para el Desarrollo**")