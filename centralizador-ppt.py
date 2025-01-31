import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import pandas as pd
import io
import os
import bcrypt  # Para hashear contraseñas manualmente
from openpyxl import load_workbook

########################################
# 1) Funciones para leer/escribir config.yaml
########################################
def cargar_config_desde_yaml(ruta_yaml="config.yaml"):
    """
    Lee el archivo config.yaml y retorna un dict con la estructura 
    que usa streamlit_authenticator.
    """
    if not os.path.exists(ruta_yaml):
        raise FileNotFoundError(f"No se encontró el archivo {ruta_yaml}")
    with open(ruta_yaml, "r", encoding="utf-8") as file:
        return yaml.load(file, Loader=SafeLoader)

def guardar_config_a_yaml(config: dict, ruta_yaml="config.yaml"):
    """
    Sobrescribe config.yaml con el dict 'config'.
    """
    with open(ruta_yaml, "w", encoding="utf-8") as file:
        yaml.dump(config, file, default_flow_style=False)

########################################
# 2) Registro de nuevos usuarios
########################################
def registrar_nuevo_usuario(
    username,
    first_name,
    last_name,
    email,
    password_plano,
    role_asignado="viewer",
    area_asignada="PRE",
    ruta_yaml="config.yaml"
):
    """
    Crea un nuevo usuario en config.yaml:
     - Hashea la contraseña con bcrypt
     - Usa el rol 'role_asignado' (admin,editor,viewer)
     - Usa el área 'area_asignada' (VPD, VPO, VPF, VPE, PRE)
    Retorna (exito: bool, mensaje: str).
    """
    config = cargar_config_desde_yaml(ruta_yaml)

    # Verificar si el usuario ya existe
    if username in config["credentials"]["usernames"]:
        return False, f"El usuario '{username}' ya existe."

    # Hashear la contraseña con bcrypt
    hashed_bytes = bcrypt.hashpw(password_plano.encode("utf-8"), bcrypt.gensalt())
    hashed_pass  = hashed_bytes.decode("utf-8")

    # Agregar al diccionario
    config["credentials"]["usernames"][username] = {
        "first_name": first_name,
        "last_name":  last_name,
        "email":      email,
        "password":   hashed_pass,
        "role":       role_asignado,
        "area":       area_asignada
    }

    guardar_config_a_yaml(config, ruta_yaml)
    return True, f"Usuario '{username}' creado exitosamente con rol '{role_asignado}' y área '{area_asignada}'."


def formulario_crear_usuario():
    """
    Muestra un formulario para crear un usuario (admin, editor o viewer).
    Incluye nueva opción para escoger Área.
    """
    st.subheader("Crear Nuevo Usuario")

    col1, col2 = st.columns(2)
    with col1:
        nuevo_username = st.text_input("Nombre de Usuario")
        nuevo_first    = st.text_input("Nombre")
        rol_elegido    = st.selectbox("Rol del usuario", ["admin","editor","viewer"])
        area_elegida   = st.selectbox("Área del usuario", ["PRE","VPD","VPO","VPF","VPE"])
    with col2:
        nuevo_last     = st.text_input("Apellido")
        nuevo_email    = st.text_input("Email (opcional)")

    pass1 = st.text_input("Contraseña", type="password")
    pass2 = st.text_input("Repite Contraseña", type="password")

    if st.button("Registrar Usuario"):
        if pass1 != pass2:
            st.error("Las contraseñas no coinciden.")
            return
        if not nuevo_username.strip():
            st.error("El campo 'Nombre de Usuario' es obligatorio.")
            return

        exito, msg = registrar_nuevo_usuario(
            username=nuevo_username.strip(),
            first_name=nuevo_first.strip(),
            last_name=nuevo_last.strip(),
            email=nuevo_email.strip(),
            password_plano=pass1,
            role_asignado=rol_elegido,
            area_asignada=area_elegida
        )
        if exito:
            st.success(msg)
            st.info("Ahora ya puedes loguearte con tu nuevo usuario.")
        else:
            st.error(msg)


########################################
# 3) Funciones de Cálculo y Formato
########################################
def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    df_calc = df.copy()
    cols_base = ["cant_funcionarios","costo_pasaje","dias","alojamiento","perdiem_otros","movilidad"]
    for col in cols_base:
        if col not in df_calc.columns:
            df_calc[col] = 0

    df_calc["total_pasaje"] = df_calc["cant_funcionarios"] * df_calc["costo_pasaje"]
    df_calc["total_alojamiento"] = df_calc["cant_funcionarios"] * df_calc["dias"] * df_calc["alojamiento"]
    df_calc["total_perdiem_otros"] = df_calc["cant_funcionarios"] * df_calc["dias"] * df_calc["perdiem_otros"]
    df_calc["total_movilidad"] = df_calc["cant_funcionarios"] * df_calc["movilidad"]
    df_calc["total"] = (
        df_calc["total_pasaje"]
        + df_calc["total_alojamiento"]
        + df_calc["total_perdiem_otros"]
        + df_calc["total_movilidad"]
    )
    return df_calc

def calcular_consultores(df: pd.DataFrame) -> pd.DataFrame:
    df_calc = df.copy()
    cols_base = ["cantidad_funcionarios","cantidad_meses","monto_mensual"]
    for col in cols_base:
        if col not in df_calc.columns:
            df_calc[col] = 0

    df_calc["total"] = (
        df_calc["cantidad_funcionarios"]
        * df_calc["cantidad_meses"]
        * df_calc["monto_mensual"]
    )
    return df_calc

def two_decimals_only_numeric(df: pd.DataFrame):
    """
    Función previa para formatear con 2 decimales y dejar celdas nulas vacías.
    Si quieres un approach diferente, usa 'show_table_no_na' más abajo.
    """
    numeric_cols = df.select_dtypes(include=["float","int"]).columns
    return df.style.format("{:,.2f}", na_rep="", subset=numeric_cols)


#################### NUEVA FUNCIÓN DE STYLER ####################
def show_table_no_na(df: pd.DataFrame):
    """
    Crea un Styler que muestra:
      - Columnas numéricas con {:,.2f} y celdas nulas en blanco.
      - Columnas no numéricas con {} y celdas nulas en blanco.
    Luego se puede llamar con st.dataframe(show_table_no_na(df)).
    """
    numeric_cols = df.select_dtypes(include=["float","int","number"]).columns
    all_cols = df.columns
    non_numeric_cols = list(set(all_cols) - set(numeric_cols))

    styler = df.style
    # Formatear columnas numéricas
    styler = styler.format("{:,.2f}", na_rep="", subset=numeric_cols)
    # Formatear columnas no numéricas
    styler = styler.format("{}", na_rep="", subset=non_numeric_cols)
    return styler
################################################################

def color_diferencia(val):
    return "background-color: #fb8500; color:white" if val != 0 else "background-color: green; color:white"

def value_box(label: str, value, bg_color: str="#6c757d"):
    st.markdown(f"""
    <div style="display:inline-block; background-color:{bg_color}; 
                padding:10px; margin:5px; border-radius:5px; color:white; font-weight:bold;">
        <div style="font-size:14px;">{label}</div>
        <div style="font-size:20px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_value_boxes_por_area(df: pd.DataFrame, col_area: str="area_imputacion"):
    areas_imputacion = ["VPD","VPO","VPF","PRE"]
    cols = st.columns(len(areas_imputacion))
    for i, area in enumerate(areas_imputacion):
        total_area = 0
        if col_area in df.columns and "total" in df.columns:
            total_area = df.loc[df[col_area]==area,"total"].sum()
        with cols[i]:
            value_box(area, f"{total_area:,.2f}")

import io
def descargar_excel(df: pd.DataFrame, file_name: str="descarga.xlsx") -> None:
    """
    Crea un botón para descargar 'df' en formato Excel.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Hoja1", index=False)
    datos_excel = buffer.getvalue()
    st.download_button(
        label="Descargar tabla en Excel",
        data=datos_excel,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def guardar_en_excel(df: pd.DataFrame, sheet_name: str, excel_file: str="main_bdd.xlsx"):
    """
    Guarda 'df' en la hoja 'sheet_name' del archivo 'excel_file', reemplazándola.
    """
    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


########################################
# 4) Funciones para Actualización
########################################
def actualizar_misiones(unit: str, req_area: float, monto_dpp: float):
    if "actualizacion_misiones" not in st.session_state:
        st.session_state["actualizacion_misiones"] = pd.DataFrame(
            columns=["Unidad Organizacional","Requerimiento del Área","Monto DPP 2025","Diferencia"]
        )
    df_act = st.session_state["actualizacion_misiones"].copy()
    mask = df_act["Unidad Organizacional"]==unit
    diferencia = monto_dpp - req_area

    if mask.any():
        df_act.loc[mask,"Requerimiento del Área"] = req_area
        df_act.loc[mask,"Monto DPP 2025"] = monto_dpp
        df_act.loc[mask,"Diferencia"] = diferencia
    else:
        nueva_fila = {
            "Unidad Organizacional": unit,
            "Requerimiento del Área": req_area,
            "Monto DPP 2025": monto_dpp,
            "Diferencia": diferencia
        }
        df_act = pd.concat([df_act, pd.DataFrame([nueva_fila])], ignore_index=True)

    st.session_state["actualizacion_misiones"] = df_act
    guardar_en_excel(df_act, "actualizacion_misiones")

def actualizar_consultorias(unit: str, req_area: float, monto_dpp: float):
    if "actualizacion_consultorias" not in st.session_state:
        st.session_state["actualizacion_consultorias"] = pd.DataFrame(
            columns=["Unidad Organizacional","Requerimiento del Área","Monto DPP 2025","Diferencia"]
        )
    df_act = st.session_state["actualizacion_consultorias"].copy()
    mask = df_act["Unidad Organizacional"]==unit
    diferencia = monto_dpp - req_area

    if mask.any():
        df_act.loc[mask,"Requerimiento del Área"] = req_area
        df_act.loc[mask,"Monto DPP 2025"] = monto_dpp
        df_act.loc[mask,"Diferencia"] = diferencia
    else:
        nueva_fila = {
            "Unidad Organizacional": unit,
            "Requerimiento del Área": req_area,
            "Monto DPP 2025": monto_dpp,
            "Diferencia": diferencia
        }
        df_act = pd.concat([df_act, pd.DataFrame([nueva_fila])], ignore_index=True)

    st.session_state["actualizacion_consultorias"] = df_act
    guardar_en_excel(df_act, "actualizacion_consultorias")


DPP_VALORES = {
    "VPD": {"misiones":168000,"consultorias":130000},
    "VPO": {"misiones":434707,"consultorias":250000},
    "VPF": {"misiones":138600,"consultorias":200000},
    "VPE": {"misiones":28244,  "consultorias":179446},
    "PRE": {"misiones":0,      "consultorias":0},
}
DPP_GC_MIS_PER = {"VPD":36960,"VPO":48158,"VPF":40960}
DPP_GC_MIS_CONS= {"VPD":24200,"VPO":13160,"VPF":24200}
DPP_GC_CONS    = {"VPD":24200,"VPO":13160,"VPF":24200}

def sincronizar_actualizacion_al_iniciar():
    """
    Actualiza automáticamente las tablas 'actualizacion_misiones' y 'actualizacion_consultorias'
    en función de lo que haya en st.session_state.
    """
    unidades = ["VPD","VPO","VPF","VPE"]
    for unidad in unidades:
        df_misiones_key = f"{unidad.lower()}_misiones"
        if df_misiones_key in st.session_state:
            df_temp = st.session_state[df_misiones_key].copy()
            if unidad!="VPE":
                df_temp = calcular_misiones(df_temp)
            total_misiones = df_temp["total"].sum() if "total" in df_temp.columns else 0
            dpp_misiones = DPP_VALORES[unidad]["misiones"]
            actualizar_misiones(unidad, total_misiones, dpp_misiones)

        df_consult_key = f"{unidad.lower()}_consultores"
        if df_consult_key in st.session_state:
            df_temp = st.session_state[df_consult_key].copy()
            if unidad!="VPE":
                df_temp = calcular_consultores(df_temp)
            total_cons = df_temp["total"].sum() if "total" in df_temp.columns else 0
            dpp_cons = DPP_VALORES[unidad]["consultorias"]
            actualizar_consultorias(unidad, total_cons, dpp_cons)

    # PRE - Especial
    if "pre_misiones_personal" in st.session_state:
        df_personal = st.session_state["pre_misiones_personal"].copy()
        df_personal = calcular_misiones(df_personal)
        total_personal = df_personal.loc[df_personal["area_imputacion"]=="PRE","total"].sum()
    else:
        total_personal = 0

    if "pre_misiones_consultores" in st.session_state:
        df_mis_cons = st.session_state["pre_misiones_consultores"].copy()
        df_mis_cons = calcular_misiones(df_mis_cons)
        total_misiones_cons = df_mis_cons.loc[df_mis_cons["area_imputacion"]=="PRE","total"].sum()
    else:
        total_misiones_cons = 0

    if "pre_consultores" in st.session_state:
        df_cons = st.session_state["pre_consultores"].copy()
        df_cons = calcular_consultores(df_cons)
    else:
        df_cons = pd.DataFrame(columns=["area_imputacion","total"])

    total_consultorias_PRE = df_cons.loc[df_cons["area_imputacion"]=="PRE","total"].sum()

    dpp_pre_personal     = 80248
    dpp_pre_mis_cons     = 30872
    dpp_pre_consultorias = 307528

    actualizar_misiones("PRE - Misiones - Personal", total_personal, dpp_pre_personal)
    actualizar_misiones("PRE - Misiones - Consultores", total_misiones_cons, dpp_pre_mis_cons)
    actualizar_consultorias("PRE - Consultorías", total_consultorias_PRE, dpp_pre_consultorias)

    sum_vpd = df_cons.loc[df_cons["area_imputacion"]=="VPD","total"].sum()
    sum_vpo = df_cons.loc[df_cons["area_imputacion"]=="VPO","total"].sum()
    sum_vpf = df_cons.loc[df_cons["area_imputacion"]=="VPF","total"].sum()

    dpp_vpd_consultorias = 193160
    dpp_vpo_consultorias = 33160
    dpp_vpf_consultorias = 88480

    actualizar_consultorias("VPD - Consultorías", sum_vpd, dpp_vpd_consultorias)
    actualizar_consultorias("VPO - Consultorías", sum_vpo, dpp_vpo_consultorias)
    actualizar_consultorias("VPF - Consultorías", sum_vpf, dpp_vpf_consultorias)

    df_gc_personal = st.session_state.get("pre_misiones_personal", pd.DataFrame())
    df_gc_personal = calcular_misiones(df_gc_personal)
    df_gc_miscons  = st.session_state.get("pre_misiones_consultores", pd.DataFrame())
    df_gc_miscons  = calcular_misiones(df_gc_miscons)

    for unidad in ["VPD","VPO","VPF"]:
        total_unidad = df_gc_personal.loc[df_gc_personal["area_imputacion"]==unidad,"total"].sum()
        dpp_gc = DPP_GC_MIS_PER[unidad]
        label_gc = f"{unidad} - GC Misiones Personal"
        actualizar_misiones(label_gc, total_unidad, dpp_gc)

    for unidad in ["VPD","VPO","VPF"]:
        total_unidad = df_gc_miscons.loc[df_gc_miscons["area_imputacion"]==unidad,"total"].sum()
        dpp_gc = DPP_GC_MIS_CONS[unidad]
        label_gc = f"{unidad} - GC Misiones Consultores"
        actualizar_misiones(label_gc, total_unidad, dpp_gc)


########################################
# 5) Editar Tabla con Control de Rol
########################################
def editar_tabla_section(
    titulo: str,
    df_original: pd.DataFrame,
    session_key: str,
    sheet_name: str,
    calculo_fn=None,
    mostrar_sum_misiones: bool=False,
    mostrar_valuebox_area: bool=False,
    dpp_value: float=None,
    subir_archivo_label: str="Cargar un archivo Excel para reemplazar la tabla"
):
    st.subheader(titulo)

    # Aplica función de cálculo si corresponde
    if calculo_fn:
        df_calc = calculo_fn(df_original.copy())
    else:
        df_calc = df_original.copy()

    # Suma total si existe la columna 'total'
    sum_total = 0
    if "total" in df_calc.columns:
        sum_total = df_calc["total"].sum()

    # Mostrar value boxes por área (opcional)
    if mostrar_valuebox_area:
        st.markdown("### Totales por Área de Imputación")
        mostrar_value_boxes_por_area(df_calc, col_area="area_imputacion")

    # Mostrar sumas de misiones (opcional)
    if mostrar_sum_misiones and all(c in df_calc.columns for c in ["total_pasaje","total_alojamiento","total_perdiem_otros","total_movilidad"]):
        sum_dict = {}
        for col in ["total_pasaje","total_alojamiento","total_perdiem_otros","total_movilidad","total"]:
            sum_dict[col] = df_calc[col].sum() if col in df_calc.columns else 0
        st.write("#### Suma de columnas (Misiones)")
        st.dataframe(pd.DataFrame([sum_dict]))

    # Value boxes: Suma del total / Monto DPP / Diferencia
    if dpp_value is not None:
        diferencia = dpp_value - sum_total
        color_dif = "#fb8500" if diferencia != 0 else "green"
        c1, c2, c3 = st.columns(3)
        with c1:
            value_box("Suma del total", f"{sum_total:,.2f}")
        with c2:
            value_box("Monto DPP 2025", f"{dpp_value:,.2f}")
        with c3:
            value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
    else:
        value_box("Suma del total", f"{sum_total:,.2f}")

    # Ver rol del usuario (admin/editor -> can_edit)
    can_edit = False
    if "user_role" in st.session_state:
        if st.session_state["user_role"] in ["admin","editor"]:
            can_edit = True

    # Subir un Excel para reemplazar la tabla
    uploaded_file = st.file_uploader(subir_archivo_label, type=["xlsx"])
    if uploaded_file is not None:
        if can_edit:
            if st.button(f"Reemplazar tabla ({sheet_name})"):
                df_subido = pd.read_excel(uploaded_file)
                if calculo_fn:
                    df_subido = calculo_fn(df_subido)
                st.session_state[session_key] = df_subido
                guardar_en_excel(df_subido, sheet_name)
                st.success(f"¡Tabla en '{sheet_name}' reemplazada con éxito!")
                st.experimental_rerun()
        else:
            st.warning("No tienes permiso para reemplazar la tabla.")

    st.markdown("### Edición de la tabla (haz clic en las celdas para modificar)")

    # Deshabilitar columnas calculadas
    disabled_cols = {}
    if calculo_fn==calcular_misiones:
        disabled_cols = {
            "total_pasaje":        st.column_config.NumberColumn(disabled=True),
            "total_alojamiento":   st.column_config.NumberColumn(disabled=True),
            "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
            "total_movilidad":     st.column_config.NumberColumn(disabled=True),
            "total":               st.column_config.NumberColumn(disabled=True),
        }
    elif calculo_fn==calcular_consultores:
        disabled_cols = {
            "total": st.column_config.NumberColumn(disabled=True)
        }

    # Si no puede editar -> disabled=True global
    if not can_edit:
        st.warning("No tienes permiso para editar esta tabla (solo lectura).")
        df_editado = st.data_editor(
            df_calc,
            use_container_width=True,
            column_config=disabled_cols,
            disabled=True
        )
    else:
        df_editado = st.data_editor(
            df_calc,
            use_container_width=True,
            column_config=disabled_cols
        )

    # Botones "Guardar Cambios" / "Cancelar" solo si can_edit
    if can_edit:
        col_guardar, col_cancelar = st.columns(2)
        with col_guardar:
            if st.button("Guardar Cambios"):
                if calculo_fn:
                    df_final = calculo_fn(df_editado)
                else:
                    df_final = df_editado
                st.session_state[session_key] = df_final
                guardar_en_excel(df_final, sheet_name)
                st.success(f"¡Datos guardados en '{sheet_name}'!")

        with col_cancelar:
            if st.button("Cancelar / Descartar Cambios"):
                st.info("Descartando cambios y recargando la tabla original...")
                st.experimental_rerun()

    st.write("### Descargar la tabla en Excel (versión actual en pantalla)")
    descargar_excel(df_editado, file_name=f"{sheet_name}_modificada.xlsx")


########################################
# 6) Lógica de secciones permitidas según Área
########################################
def get_allowed_sections(area_user: str):
    """
    Retorna la lista de secciones que puede ver el usuario según su área.
    - PRE y VPD -> pueden ver todo
    - VPO -> solo VPO (más Página Principal y Consolidado)
    - VPF -> solo VPF (más Página Principal y Consolidado)
    - VPE -> solo VPE (más Página Principal y Consolidado)
    """
    all_sections = ["Página Principal", "VPD", "VPO", "VPF", "VPE", "PRE", "Actualización", "Consolidado"]
    if area_user in ["VPD", "PRE"]:
        # Puede ver todo
        return all_sections
    elif area_user == "VPO":
        return ["Página Principal", "VPO", "Consolidado"]
    elif area_user == "VPF":
        return ["Página Principal", "VPF", "Consolidado"]
    elif area_user == "VPE":
        return ["Página Principal", "VPE", "Consolidado"]
    else:
        # Si no coincide, solo ver Principal y Consolidado
        return ["Página Principal", "Consolidado"]


########################################
# 7) FUNCIÓN PRINCIPAL
########################################
def main():
    # Configuración de la página
    st.set_page_config(page_title="Presupuesto", layout="wide")

    st.title("Planificación presupuestaria")

    # Menú lateral: "Login" o "Crear Usuario"
    menu_lateral = st.sidebar.radio("Selecciona una Opción:", ["Login", "Crear Usuario"])

    if menu_lateral == "Crear Usuario":
        formulario_crear_usuario()
        return

    # Caso "Login"
    config = cargar_config_desde_yaml("config.yaml")
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    try:
        authenticator.login()
    except stauth.LoginError as e:
        st.error(e)

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    if st.session_state["authentication_status"] is True:
        # Usuario logueado
        st.sidebar.success(f"Sesión iniciada por: {st.session_state['name']}")
        username_log = st.session_state["username"]

        # Obtener rol
        rol_user = config["credentials"]["usernames"][username_log].get("role", "viewer")
        st.session_state["user_role"] = rol_user

        # Obtener área
        area_user = config["credentials"]["usernames"][username_log].get("area", "PRE")

        st.write(f"Bienvenido *{st.session_state['name']}*. Rol: **{rol_user}**, Área: **{area_user}**")

        # Logout
        authenticator.logout()

        # (A) Carga de datos Excel
        excel_file = "main_bdd.xlsx"

        # VPD
        if "vpd_misiones" not in st.session_state:
            st.session_state["vpd_misiones"] = pd.read_excel(excel_file, sheet_name="vpd_misiones")
        if "vpd_consultores" not in st.session_state:
            st.session_state["vpd_consultores"] = pd.read_excel(excel_file, sheet_name="vpd_consultores")

        # VPO
        if "vpo_misiones" not in st.session_state:
            st.session_state["vpo_misiones"] = pd.read_excel(excel_file, sheet_name="vpo_misiones")
        if "vpo_consultores" not in st.session_state:
            st.session_state["vpo_consultores"] = pd.read_excel(excel_file, sheet_name="vpo_consultores")

        # VPF
        if "vpf_misiones" not in st.session_state:
            st.session_state["vpf_misiones"] = pd.read_excel(excel_file, sheet_name="vpf_misiones")
        if "vpf_consultores" not in st.session_state:
            st.session_state["vpf_consultores"] = pd.read_excel(excel_file, sheet_name="vpf_consultores")

        # VPE
        if "vpe_misiones" not in st.session_state:
            st.session_state["vpe_misiones"] = pd.read_excel(excel_file, sheet_name="vpe_misiones")
        if "vpe_consultores" not in st.session_state:
            st.session_state["vpe_consultores"] = pd.read_excel(excel_file, sheet_name="vpe_consultores")

        # PRE
        if "pre_misiones_personal" not in st.session_state:
            st.session_state["pre_misiones_personal"] = pd.read_excel(excel_file, sheet_name="pre_misiones_personal")
        if "pre_misiones_consultores" not in st.session_state:
            st.session_state["pre_misiones_consultores"] = pd.read_excel(excel_file, sheet_name="pre_misiones_consultores")
        if "pre_consultores" not in st.session_state:
            st.session_state["pre_consultores"] = pd.read_excel(excel_file, sheet_name="pre_consultores")

        # Otras hojas
        if "com" not in st.session_state:
            try:
                st.session_state["com"] = pd.read_excel(excel_file, sheet_name="COM")
            except:
                st.warning("No se encontró la hoja COM. Se crea un DataFrame vacío.")
                st.session_state["com"] = pd.DataFrame()

        if "cuadro_9" not in st.session_state:
            st.session_state["cuadro_9"] = pd.read_excel(excel_file, sheet_name="cuadro_9")
        if "cuadro_10" not in st.session_state:
            st.session_state["cuadro_10"] = pd.read_excel(excel_file, sheet_name="cuadro_10")
        if "cuadro_11" not in st.session_state:
            st.session_state["cuadro_11"] = pd.read_excel(excel_file, sheet_name="cuadro_11")
        if "consolidado_df" not in st.session_state:
            st.session_state["consolidado_df"] = pd.read_excel(excel_file, sheet_name="consolidado")

        if "gastos_centralizados" not in st.session_state:
            try:
                st.session_state["gastos_centralizados"] = pd.read_excel(excel_file, sheet_name="gastos_centralizados")
            except:
                st.session_state["gastos_centralizados"] = pd.DataFrame()

        # (B) Sincroniza
        sincronizar_actualizacion_al_iniciar()

        # (C) Menú principal filtrado por área
        allowed_sections = get_allowed_sections(area_user)
        st.sidebar.title("Navegación principal")
        eleccion_principal = st.sidebar.selectbox("Selecciona una sección:", allowed_sections)

        # 1) Página Principal
        if eleccion_principal=="Página Principal":
            st.title("Página Principal")
            st.write("Bienvenido a la sección principal.")

        # 2) VPD
        elif eleccion_principal=="VPD":
            st.title("Sección VPD")
            sub_vpd = ["Misiones","Consultorías"]
            eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", sub_vpd)

            sub_sub_opciones = ["Requerimiento del Área","DPP 2025"]
            eleccion_sub_sub = st.sidebar.selectbox("Tema:", sub_sub_opciones)

            if eleccion_vpd=="Misiones":
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("VPD > Misiones > Requerimiento del Área (solo lectura)")
                    df_req = st.session_state["vpd_misiones"]
                    if "total" in df_req.columns:
                        sum_total = df_req["total"].sum()
                        value_box("Suma del total", f"{sum_total:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPD > Misiones > DPP 2025",
                        df_original=st.session_state["vpd_misiones"],
                        session_key="vpd_misiones",
                        sheet_name="vpd_misiones",
                        calculo_fn=calcular_misiones,
                        mostrar_sum_misiones=True,
                        mostrar_valuebox_area=False,
                        dpp_value=168000,
                        subir_archivo_label="Reemplazar la tabla de VPD Misiones"
                    )
            else:  # Consultorías
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("VPD > Consultorías > Requerimiento del Área (solo lectura)")
                    df_req = st.session_state["vpd_consultores"]
                    if "total" in df_req.columns:
                        sum_total = df_req["total"].sum()
                        value_box("Suma del total", f"{sum_total:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPD > Consultorías > DPP 2025",
                        df_original=st.session_state["vpd_consultores"],
                        session_key="vpd_consultores",
                        sheet_name="vpd_consultores",
                        calculo_fn=calcular_consultores,
                        mostrar_sum_misiones=False,
                        mostrar_valuebox_area=False,
                        dpp_value=130000,
                        subir_archivo_label="Reemplazar la tabla de VPD Consultorías"
                    )

        # 3) VPO
        elif eleccion_principal=="VPO":
            st.title("Sección VPO")
            sub_vpo = ["Misiones","Consultorías"]
            eleccion_vpo_ = st.sidebar.selectbox("Sub-sección de VPO:", sub_vpo)

            sub_sub_opciones = ["Requerimiento del Área","DPP 2025"]
            eleccion_sub_sub = st.sidebar.selectbox("Tema:", sub_sub_opciones)

            if eleccion_vpo_=="Misiones":
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("VPO > Misiones > Requerimiento del Área (solo lectura)")
                    df_req = st.session_state["vpo_misiones"]
                    if "total" in df_req.columns:
                        total_sum = df_req["total"].sum()
                        value_box("Suma del total", f"{total_sum:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPO > Misiones > DPP 2025",
                        df_original=st.session_state["vpo_misiones"],
                        session_key="vpo_misiones",
                        sheet_name="vpo_misiones",
                        calculo_fn=calcular_misiones,
                        mostrar_sum_misiones=True,
                        mostrar_valuebox_area=False,
                        dpp_value=434707,
                        subir_archivo_label="Reemplazar la tabla de VPO Misiones"
                    )
            else:  # Consultorías
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("VPO > Consultorías > Requerimiento del Área (solo lectura)")
                    df_req = st.session_state["vpo_consultores"]
                    if "total" in df_req.columns:
                        total_sum = df_req["total"].sum()
                        value_box("Suma del total", f"{total_sum:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPO > Consultorías > DPP 2025",
                        df_original=st.session_state["vpo_consultores"],
                        session_key="vpo_consultores",
                        sheet_name="vpo_consultores",
                        calculo_fn=calcular_consultores,
                        mostrar_sum_misiones=False,
                        mostrar_valuebox_area=False,
                        dpp_value=250000,
                        subir_archivo_label="Reemplazar la tabla de VPO Consultorías"
                    )

        # 4) VPF
        elif eleccion_principal=="VPF":
            st.title("Sección VPF")
            sub_vpf = ["Misiones","Consultorías"]
            eleccion_vpf_ = st.sidebar.selectbox("Sub-sección de VPF:", sub_vpf)

            sub_sub_opciones = ["Requerimiento del Área","DPP 2025"]
            eleccion_sub_sub = st.sidebar.selectbox("Tema:", sub_sub_opciones)

            if eleccion_vpf_=="Misiones":
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("VPF > Misiones > Requerimiento del Área (solo lectura)")
                    df_req = st.session_state["vpf_misiones"]
                    if "total" in df_req.columns:
                        total_sum = df_req["total"].sum()
                        value_box("Suma del total", f"{total_sum:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPF > Misiones > DPP 2025",
                        df_original=st.session_state["vpf_misiones"],
                        session_key="vpf_misiones",
                        sheet_name="vpf_misiones",
                        calculo_fn=calcular_misiones,
                        mostrar_sum_misiones=True,
                        mostrar_valuebox_area=False,
                        dpp_value=138600,
                        subir_archivo_label="Reemplazar la tabla de VPF Misiones"
                    )
            else:  # Consultorías
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("VPF > Consultorías > Requerimiento del Área (solo lectura)")
                    df_req = st.session_state["vpf_consultores"]
                    if "total" in df_req.columns:
                        total_sum = df_req["total"].sum()
                        value_box("Suma del total", f"{total_sum:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPF > Consultorías > DPP 2025",
                        df_original=st.session_state["vpf_consultores"],
                        session_key="vpf_consultores",
                        sheet_name="vpf_consultores",
                        calculo_fn=calcular_consultores,
                        mostrar_sum_misiones=False,
                        mostrar_valuebox_area=False,
                        dpp_value=200000,
                        subir_archivo_label="Reemplazar la tabla de VPF Consultorías"
                    )

        # 5) VPE
        elif eleccion_principal=="VPE":
            st.title("Sección VPE")
            sub_vpe = ["Misiones","Consultorías"]
            eleccion_vpe_ = st.sidebar.selectbox("Sub-sección de VPE:", sub_vpe)

            sub_sub_vpe = ["Requerimiento del Área","DPP 2025"]
            eleccion_sub_sub_vpe = st.sidebar.selectbox("Tema:", sub_sub_vpe)

            if eleccion_vpe_=="Misiones":
                if eleccion_sub_sub_vpe=="Requerimiento del Área":
                    st.subheader("VPE > Misiones > Requerimiento del Área (Solo lectura)")
                    df_req = st.session_state["vpe_misiones"]
                    if "total" in df_req.columns:
                        total_sum = df_req["total"].sum()
                        value_box("Suma del total", f"{total_sum:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPE > Misiones > DPP 2025 (Editable sin fórmulas)",
                        df_original=st.session_state["vpe_misiones"],
                        session_key="vpe_misiones",
                        sheet_name="vpe_misiones",
                        calculo_fn=None,
                        mostrar_sum_misiones=False,
                        mostrar_valuebox_area=False,
                        dpp_value=28244,
                        subir_archivo_label="Reemplazar tabla de VPE Misiones"
                    )
            else:  # Consultorías
                if eleccion_sub_sub_vpe=="Requerimiento del Área":
                    st.subheader("VPE > Consultorías > Requerimiento del Área (Solo lectura)")
                    df_req = st.session_state["vpe_consultores"]
                    if "total" in df_req.columns:
                        total_sum = df_req["total"].sum()
                        value_box("Suma del total", f"{total_sum:,.2f}")
                    st.dataframe(df_req)
                else:
                    editar_tabla_section(
                        titulo="VPE > Consultorías > DPP 2025 (Editable sin fórmulas)",
                        df_original=st.session_state["vpe_consultores"],
                        session_key="vpe_consultores",
                        sheet_name="vpe_consultores",
                        calculo_fn=None,
                        mostrar_sum_misiones=False,
                        mostrar_valuebox_area=False,
                        dpp_value=179446,
                        subir_archivo_label="Reemplazar tabla de VPE Consultorías"
                    )

        # 6) PRE
        elif eleccion_principal=="PRE":
            st.title("Sección PRE")

            menu_pre = ["Misiones Personal","Misiones Consultores","Consultorías","Comunicaciones","Gastos Centralizados"]
            eleccion_pre_ = st.sidebar.selectbox("Sub-sección de PRE:", menu_pre)

            if eleccion_pre_=="Misiones Personal":
                sub_sub = ["Requerimiento del Área","DPP 2025"]
                eleccion_sub_sub = st.sidebar.selectbox("Tema (Misiones Personal):", sub_sub)
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("PRE > Misiones Personal > Requerimiento del Área (Solo lectura)")
                    df_pre = st.session_state["pre_misiones_personal"]
                    if "total" in df_pre.columns:
                        sum_total = df_pre["total"].sum()
                        value_box("Suma del total", f"{sum_total:,.2f}")
                    mostrar_value_boxes_por_area(df_pre, col_area="area_imputacion")
                    st.dataframe(df_pre)
                else:
                    editar_tabla_section(
                        titulo="PRE > Misiones Personal > DPP 2025",
                        df_original=st.session_state["pre_misiones_personal"],
                        session_key="pre_misiones_personal",
                        sheet_name="pre_misiones_personal",
                        calculo_fn=calcular_misiones,
                        mostrar_sum_misiones=True,
                        mostrar_valuebox_area=True,
                        dpp_value=80248,
                        subir_archivo_label="Reemplazar tabla de PRE Misiones Personal"
                    )

            elif eleccion_pre_=="Misiones Consultores":
                sub_sub = ["Requerimiento del Área","DPP 2025"]
                eleccion_sub_sub = st.sidebar.selectbox("Tema (Misiones Consultores):", sub_sub)
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("PRE > Misiones Consultores > Requerimiento del Área (Solo lectura)")
                    df_pre = st.session_state["pre_misiones_consultores"]
                    if "total" in df_pre.columns:
                        sum_total = df_pre["total"].sum()
                        value_box("Suma del total", f"{sum_total:,.2f}")
                    mostrar_value_boxes_por_area(df_pre, col_area="area_imputacion")
                    st.dataframe(df_pre)
                else:
                    editar_tabla_section(
                        titulo="PRE > Misiones Consultores > DPP 2025",
                        df_original=st.session_state["pre_misiones_consultores"],
                        session_key="pre_misiones_consultores",
                        sheet_name="pre_misiones_consultores",
                        calculo_fn=calcular_misiones,
                        mostrar_sum_misiones=True,
                        mostrar_valuebox_area=True,
                        dpp_value=30872,
                        subir_archivo_label="Reemplazar tabla de PRE Misiones Consultores"
                    )

            elif eleccion_pre_=="Consultorías":
                sub_sub = ["Requerimiento del Área","DPP 2025"]
                eleccion_sub_sub = st.sidebar.selectbox("Tema (Consultorías):", sub_sub)
                if eleccion_sub_sub=="Requerimiento del Área":
                    st.subheader("PRE > Consultorías > Requerimiento del Área (Solo lectura)")
                    df_pre = st.session_state["pre_consultores"]
                    if "total" in df_pre.columns:
                        df_pre["total"] = pd.to_numeric(df_pre["total"], errors="coerce")
                        sum_total = df_pre["total"].sum()
                        value_box("Suma del total", f"{sum_total:,.2f}")
                    mostrar_value_boxes_por_area(df_pre, col_area="area_imputacion")
                    st.dataframe(df_pre)
                else:
                    editar_tabla_section(
                        titulo="PRE > Consultorías > DPP 2025",
                        df_original=st.session_state["pre_consultores"],
                        session_key="pre_consultores",
                        sheet_name="pre_consultores",
                        calculo_fn=calcular_consultores,
                        mostrar_sum_misiones=False,
                        mostrar_valuebox_area=True,
                        dpp_value=338372,
                        subir_archivo_label="Reemplazar tabla de PRE Consultorías"
                    )

            elif eleccion_pre_=="Comunicaciones":
                st.subheader("PRE > Comunicaciones (Solo lectura)")
                df_com = st.session_state["com"]
                st.dataframe(df_com)
                st.info("Tabla de Comunicaciones (COM) mostrada aquí.")

            else:
                # Gastos Centralizados
                st.subheader("PRE > Gastos Centralizados (Referencias)")
                st.write("### Copia: Misiones Personal (cálculo DPP)")
                df_mp = calcular_misiones(st.session_state["pre_misiones_personal"].copy())
                st.dataframe(df_mp)

                st.write("### Copia: Misiones Consultores (cálculo DPP)")
                df_mc = calcular_misiones(st.session_state["pre_misiones_consultores"].copy())
                st.dataframe(df_mc)

                st.write("### Copia: Consultorías (cálculo DPP)")
                df_c = calcular_consultores(st.session_state["pre_consultores"].copy())
                st.dataframe(df_c)

        # 7) Actualización
        elif eleccion_principal=="Actualización":
            st.title("Actualización")
            st.write("Estas tablas se sincronizan automáticamente al iniciar la app o recargar.")
            st.write("### Tabla de Misiones")
            df_misiones = st.session_state["actualizacion_misiones"]
            st.dataframe(
                df_misiones.style
                .format("{:,.2f}", subset=["Requerimiento del Área","Monto DPP 2025","Diferencia"], na_rep="")
                .applymap(color_diferencia, subset=["Diferencia"])
            )

            st.write("### Tabla de Consultorías")
            df_cons = st.session_state["actualizacion_consultorias"]
            st.dataframe(
                df_cons.style
                .format("{:,.2f}", subset=["Requerimiento del Área","Monto DPP 2025","Diferencia"], na_rep="")
                .applymap(color_diferencia, subset=["Diferencia"])
            )
            st.info("Se recalculan en cada carga de la app y cuando guardas datos en las secciones DPP 2025.")

        # 8) Consolidado
        elif eleccion_principal=="Consolidado":
            st.title("Consolidado")

            st.write("#### Gasto en personal 2024 Vs 2025")
            df_9 = st.session_state["cuadro_9"]
            # <--- cambio principal: usamos 'show_table_no_na' en lugar de 'two_decimals_only_numeric'
            st.dataframe(show_table_no_na(df_9))

            st.caption("Cuadro 9 - DPP 2025")

            st.write("---")
            st.write("#### Análisis de Cambios en Gastos de Personal 2025 vs. 2024")
            df_10 = st.session_state["cuadro_10"]
            # igual
            st.dataframe(show_table_no_na(df_10))
            st.caption("Cuadro 10 - DPP 2025")

            st.write("---")
            st.write("#### Gastos Operativos propuestos para 2025 vs. montos aprobados para 2024")
            df_11 = st.session_state["cuadro_11"]
            st.dataframe(show_table_no_na(df_11))
            st.caption("Cuadro 11 - DPP 2025")

            st.write("---")
            st.write("#### DPP 2025 - Consolidado")
            df_cons2 = st.session_state["consolidado_df"]
            st.dataframe(show_table_no_na(df_cons2))  # <--- de nuevo
            st.caption("Consolidado Final")

    elif st.session_state["authentication_status"] is False:
        st.error("Usuario/Contraseña incorrectos.")
    else:
        st.warning("Por favor ingresa tu usuario y contraseña.")

if __name__=="__main__":
    main()
