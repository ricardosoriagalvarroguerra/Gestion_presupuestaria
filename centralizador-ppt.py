import io
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Configuración de la página en Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Aplicación Completa Presupuesto 2025",
    page_icon="📝",
    layout="wide"
)

# =============================================================================
# 1. FUNCIONES DE CÁLCULO
# =============================================================================

def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula totales para tablas de Misiones, de acuerdo con las columnas base:
    - cant_funcionarios, costo_pasaje, dias, alojamiento, perdiem_otros, movilidad.
    
    Se generan nuevas columnas:
    - total_pasaje
    - total_alojamiento
    - total_perdiem_otros
    - total_movilidad
    - total (suma de las cuatro anteriores)
    
    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada que contiene las columnas necesarias (o no; si no existen,
        se crean con valor cero).
        
    Retorna
    -------
    pd.DataFrame
        DataFrame con las columnas totales calculadas.
    """
    df_calc = df.copy()
    cols_base = ["cant_funcionarios", "costo_pasaje", "dias",
                 "alojamiento", "perdiem_otros", "movilidad"]
    
    # Asegura que existan las columnas base, si no, las crea en cero
    for col in cols_base:
        if col not in df_calc.columns:
            df_calc[col] = 0

    # Cálculos de las columnas totales
    df_calc["total_pasaje"] = df_calc["cant_funcionarios"] * df_calc["costo_pasaje"]
    df_calc["total_alojamiento"] = (
        df_calc["cant_funcionarios"] * df_calc["dias"] * df_calc["alojamiento"]
    )
    df_calc["total_perdiem_otros"] = (
        df_calc["cant_funcionarios"] * df_calc["dias"] * df_calc["perdiem_otros"]
    )
    df_calc["total_movilidad"] = df_calc["cant_funcionarios"] * df_calc["movilidad"]
    
    # Suma total
    df_calc["total"] = (
        df_calc["total_pasaje"]
        + df_calc["total_alojamiento"]
        + df_calc["total_perdiem_otros"]
        + df_calc["total_movilidad"]
    )
    
    return df_calc


def calcular_consultores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula totales para tablas de Consultorías, de acuerdo a:
    - cantidad_funcionarios, cantidad_meses, monto_mensual.

    Se genera la columna 'total' como:
    cantidad_funcionarios * cantidad_meses * monto_mensual

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada con las columnas base (si no existen, se crean en cero).

    Retorna
    -------
    pd.DataFrame
        DataFrame con la columna 'total' calculada.
    """
    df_calc = df.copy()
    cols_base = ["cantidad_funcionarios", "cantidad_meses", "monto_mensual"]
    
    for col in cols_base:
        if col not in df_calc.columns:
            df_calc[col] = 0

    df_calc["total"] = (
        df_calc["cantidad_funcionarios"]
        * df_calc["cantidad_meses"]
        * df_calc["monto_mensual"]
    )
    
    return df_calc


# =============================================================================
# 2. FUNCIÓN PARA FORMATEAR COLUMNAS NUMÉRICAS A DOS DECIMALES
# =============================================================================

def two_decimals_only_numeric(df: pd.DataFrame):
    """
    Aplica formato "{:,.2f}" únicamente a columnas numéricas (float, int).
    Retorna un objeto Styler que puede mostrarse con st.table() o st.dataframe().

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame a formatear.

    Retorna
    -------
    Styler
        Objeto Styler con las columnas numéricas formateadas.
    """
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    return df.style.format("{:,.2f}", subset=numeric_cols, na_rep="")


# =============================================================================
# 3. FUNCIÓN PARA MOSTRAR UN "VALUE BOX" CON HTML/CSS
# =============================================================================

def value_box(label: str, value, bg_color: str = "#6c757d"):
    """
    Muestra un pequeño recuadro (value box) con un color de fondo y texto blanco.

    Parámetros
    ----------
    label : str
        Etiqueta o título que se mostrará en la parte superior del recuadro.
    value : Any
        Valor que se mostrará en la parte inferior del recuadro.
    bg_color : str, opcional
        Color de fondo en formato hexadecimal. Por defecto: "#6c757d".
    """
    st.markdown(f"""
    <div style="
        display:inline-block; 
        background-color:{bg_color}; 
        padding:10px; 
        margin:5px; 
        border-radius:5px; 
        color:white; 
        font-weight:bold;">
        <div style="font-size:14px;">{label}</div>
        <div style="font-size:20px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 3.1. FUNCIÓN AUXILIAR PARA MOSTRAR VALUE BOXES POR ÁREA DE IMPUTACIÓN
# =============================================================================

def mostrar_value_boxes_por_area(df: pd.DataFrame, col_area: str = "area_imputacion"):
    """
    Muestra 4 value boxes (VPD, VPO, VPF, PRE) en columnas, 
    calculando la suma de la columna 'total' para cada área.
    
    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con la información de misiones o consultorías.
    col_area : str, opcional
        Nombre de la columna que indica el área de imputación. 
        Por defecto "area_imputacion".
    """
    areas_imputacion = ["VPD", "VPO", "VPF", "PRE"]
    cols = st.columns(len(areas_imputacion))
    
    for i, area in enumerate(areas_imputacion):
        if col_area in df.columns and "total" in df.columns:
            total_area = df.loc[df[col_area] == area, "total"].sum()
        else:
            total_area = 0
        with cols[i]:
            value_box(area, f"{total_area:,.2f}")


# =============================================================================
# 4. FUNCIÓN PARA COLOREAR LA DIFERENCIA
# =============================================================================

def color_diferencia(val) -> str:
    """
    Retorna un estilo de color para celdas, en función del valor (val).

    - Si val == 0: fondo verde y texto blanco.
    - Si val != 0: fondo naranja y texto blanco.

    Parámetros
    ----------
    val : float o int
        Valor numérico que se evalúa.

    Retorna
    -------
    str
        Estilo CSS para la celda.
    """
    if val == 0:
        return "background-color: green; color:white"
    else:
        return "background-color: #fb8500; color:white"


# =============================================================================
# 5. FUNCIÓN PARA GUARDAR DATOS EN EXCEL (REEMPLAZANDO UNA HOJA)
# =============================================================================

def guardar_en_excel(
    df: pd.DataFrame, 
    sheet_name: str, 
    excel_file: str = "main_bdd.xlsx"
):
    """
    Guarda el DataFrame df en la hoja 'sheet_name' del archivo excel_file,
    reemplazando esa hoja y manteniendo las demás.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame a guardar.
    sheet_name : str
        Nombre de la hoja (sheet) en el archivo Excel.
    excel_file : str, opcional
        Ruta o nombre del archivo Excel donde se guardará. 
        Por defecto "main_bdd.xlsx".
    """
    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


# =============================================================================
# 6. FUNCIÓN PARA DESCARGAR UN DataFrame COMO EXCEL (BOTÓN)
# =============================================================================

def descargar_excel(
    df: pd.DataFrame, 
    file_name: str = "descarga.xlsx"
) -> None:
    """
    Genera un archivo Excel en memoria y lo ofrece para descargar con un botón de Streamlit.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame a exportar como archivo Excel.
    file_name : str, opcional
        Nombre de archivo con extensión .xlsx. 
        Por defecto "descarga.xlsx".
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


# =============================================================================
# 7. FUNCIONES PARA ACTUALIZAR AUTOMÁTICAMENTE LAS TABLAS DE "ACTUALIZACIÓN"
# =============================================================================

def actualizar_misiones(unit: str, req_area: float, monto_dpp: float):
    """
    Actualiza (o crea) la fila correspondiente a `unit` en 'actualizacion_misiones'
    con los valores (requerimiento, monto dpp, diferencia) y guarda en Excel.

    Parámetros
    ----------
    unit : str
        Identificador de la Unidad Organizacional.
    req_area : float
        Monto de requerimiento del área.
    monto_dpp : float
        Monto DPP asignado para esa unidad.
    """
    if "actualizacion_misiones" not in st.session_state:
        st.session_state["actualizacion_misiones"] = pd.DataFrame(
            columns=["Unidad Organizacional", "Requerimiento del Área", "Monto DPP 2025", "Diferencia"]
        )

    df_act = st.session_state["actualizacion_misiones"].copy()
    mask = df_act["Unidad Organizacional"] == unit
    diferencia = monto_dpp - req_area

    if mask.any():
        df_act.loc[mask, "Requerimiento del Área"] = req_area
        df_act.loc[mask, "Monto DPP 2025"] = monto_dpp
        df_act.loc[mask, "Diferencia"] = diferencia
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
    """
    Actualiza (o crea) la fila correspondiente a `unit` en 'actualizacion_consultorias'
    con los valores (requerimiento, monto dpp, diferencia) y guarda en Excel.

    Parámetros
    ----------
    unit : str
        Identificador de la Unidad Organizacional.
    req_area : float
        Monto de requerimiento del área.
    monto_dpp : float
        Monto DPP asignado para esa unidad.
    """
    if "actualizacion_consultorias" not in st.session_state:
        st.session_state["actualizacion_consultorias"] = pd.DataFrame(
            columns=["Unidad Organizacional", "Requerimiento del Área", "Monto DPP 2025", "Diferencia"]
        )

    df_act = st.session_state["actualizacion_consultorias"].copy()
    mask = df_act["Unidad Organizacional"] == unit
    diferencia = monto_dpp - req_area

    if mask.any():
        df_act.loc[mask, "Requerimiento del Área"] = req_area
        df_act.loc[mask, "Monto DPP 2025"] = monto_dpp
        df_act.loc[mask, "Diferencia"] = diferencia
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


# MONTOS DPP PARA VPD, VPO, VPF, VPE (la unidad PRE se maneja abajo).
DPP_VALORES = {
    "VPD": {"misiones": 168000, "consultorias": 130000},
    "VPO": {"misiones": 434707, "consultorias": 250000},
    "VPF": {"misiones": 138600, "consultorias": 200000},
    "VPE": {"misiones": 28244,  "consultorias": 179446},
    "PRE": {"misiones": 0,      "consultorias": 0},
}

# DPP ESPECÍFICOS PARA "GC" (Gastos Centralizados) -- OPCIONALES
DPP_GC_MIS_PER = {
    "VPD": 36960,
    "VPO": 48158,
    "VPF": 40960
}
DPP_GC_MIS_CONS = {
    "VPD": 24200,
    "VPO": 13160,
    "VPF": 24200
}
DPP_GC_CONS = {
    "VPD": 24200,
    "VPO": 13160,
    "VPF": 24200
}


# =============================================================================
# 8. FUNCIÓN PARA SINCRONIZAR AUTOMÁTICAMENTE LA TABLA DE ACTUALIZACIÓN AL INICIAR
# =============================================================================

def sincronizar_actualizacion_al_iniciar():
    """
    Sincroniza y actualiza las tablas de 'actualizacion_misiones' y 
    'actualizacion_consultorias' al iniciar la aplicación.

    1) Actualiza VPD, VPO, VPF, VPE con sus DPP habituales en Misiones y Consultorías.
    2) Actualiza PRE dividiéndolo en:
       - PRE - Misiones - Personal
       - PRE - Misiones - Consultores
       - PRE - Consultorías
    3) También se calculan las filas "VPD - Consultorías", "VPO - Consultorías",
       "VPF - Consultorías" a partir de la hoja 'pre_consultores' (filtrando por area_imputacion).
    4) Incluye Gastos Centralizados (GC) si son necesarios, etc.
    """

    # A) VPD, VPO, VPF, VPE
    unidades = ["VPD", "VPO", "VPF", "VPE"]  # Excluimos 'PRE' en este bucle
    for unidad in unidades:
        # MISIONES
        df_misiones_key = f"{unidad.lower()}_misiones"
        if df_misiones_key in st.session_state:
            df_temp = st.session_state[df_misiones_key].copy()
            # Para VPE no se recalculan las fórmulas, se respeta la data
            if unidad != "VPE":
                df_temp = calcular_misiones(df_temp)
            total_misiones = df_temp["total"].sum() if "total" in df_temp.columns else 0
            dpp_misiones = DPP_VALORES[unidad]["misiones"]
            actualizar_misiones(unidad, total_misiones, dpp_misiones)

        # CONSULTORIAS
        df_consult_key = f"{unidad.lower()}_consultores"
        if df_consult_key in st.session_state:
            df_temp = st.session_state[df_consult_key].copy()
            if unidad != "VPE":
                df_temp = calcular_consultores(df_temp)
            total_cons = df_temp["total"].sum() if "total" in df_temp.columns else 0
            dpp_cons = DPP_VALORES[unidad]["consultorias"]
            actualizar_consultorias(unidad, total_cons, dpp_cons)

    # B) PRE
    if "pre_misiones_personal" in st.session_state:
        df_personal = st.session_state["pre_misiones_personal"].copy()
        df_personal = calcular_misiones(df_personal)
        total_personal = df_personal.loc[df_personal["area_imputacion"] == "PRE", "total"].sum()
    else:
        total_personal = 0

    if "pre_misiones_consultores" in st.session_state:
        df_mis_cons = st.session_state["pre_misiones_consultores"].copy()
        df_mis_cons = calcular_misiones(df_mis_cons)
        total_misiones_cons = df_mis_cons.loc[df_mis_cons["area_imputacion"] == "PRE", "total"].sum()
    else:
        total_misiones_cons = 0

    if "pre_consultores" in st.session_state:
        df_cons = st.session_state["pre_consultores"].copy()
        df_cons = calcular_consultores(df_cons)
    else:
        df_cons = pd.DataFrame(columns=["area_imputacion", "total"])

    total_consultorias_PRE = df_cons.loc[df_cons["area_imputacion"] == "PRE", "total"].sum()

    dpp_pre_personal     = 80248
    dpp_pre_mis_cons     = 30872
    dpp_pre_consultorias = 307528

    actualizar_misiones("PRE - Misiones - Personal",    total_personal,      dpp_pre_personal)
    actualizar_misiones("PRE - Misiones - Consultores", total_misiones_cons, dpp_pre_mis_cons)
    actualizar_consultorias("PRE - Consultorías",       total_consultorias_PRE, dpp_pre_consultorias)

    # C) Filas: VPD - Consultorías, VPO - Consultorías, VPF - Consultorías
    sum_vpd = df_cons.loc[df_cons["area_imputacion"] == "VPD", "total"].sum()
    sum_vpo = df_cons.loc[df_cons["area_imputacion"] == "VPO", "total"].sum()
    sum_vpf = df_cons.loc[df_cons["area_imputacion"] == "VPF", "total"].sum()

    dpp_vpd_consultorias = 193160
    dpp_vpo_consultorias = 33160
    dpp_vpf_consultorias = 88480

    actualizar_consultorias("VPD - Consultorías", sum_vpd, dpp_vpd_consultorias)
    actualizar_consultorias("VPO - Consultorías", sum_vpo, dpp_vpo_consultorias)
    actualizar_consultorias("VPF - Consultorías", sum_vpf, dpp_vpf_consultorias)

    # D) GASTOS CENTRALIZADOS (GC) - OPCIONALES
    df_gc_personal = st.session_state.get("pre_misiones_personal", pd.DataFrame())
    df_gc_personal = calcular_misiones(df_gc_personal)

    df_gc_miscons = st.session_state.get("pre_misiones_consultores", pd.DataFrame())
    df_gc_miscons = calcular_misiones(df_gc_miscons)

    # 1) GC - Misiones Personal
    for unidad in ["VPD", "VPO", "VPF"]:
        total_unidad = df_gc_personal.loc[df_gc_personal["area_imputacion"] == unidad, "total"].sum()
        dpp_gc = DPP_GC_MIS_PER[unidad]
        label_gc = f"{unidad} - GC Misiones Personal"
        actualizar_misiones(label_gc, total_unidad, dpp_gc)

    # 2) GC - Misiones Consultores
    for unidad in ["VPD", "VPO", "VPF"]:
        total_unidad = df_gc_miscons.loc[df_gc_miscons["area_imputacion"] == unidad, "total"].sum()
        dpp_gc = DPP_GC_MIS_CONS[unidad]
        label_gc = f"{unidad} - GC Misiones Consultores"
        actualizar_misiones(label_gc, total_unidad, dpp_gc)

    # 3) GC - Consultorías (VPD, VPO, VPF) -- Comentado para no sobreescribir
    # ...


# =============================================================================
# 9. FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """
    Función principal de la aplicación. Muestra la interfaz de usuario, 
    gestiona la lógica de login y organiza la navegación por secciones.
    """
    # A) LOGIN
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.title("Login - Presupuesto 2025")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión"):
            valid_users = ["mcalvino", "ajustinianon", "vgonzales", "vmoreira"]
            valid_password = "2025presupuesto"
            if username in valid_users and password == valid_password:
                st.session_state["logged_in"] = True
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        return
    else:
        st.sidebar.success("Sesión iniciada.")

    # B) LECTURA DE DATOS DESDE EXCEL A session_state
    excel_file = "main_bdd.xlsx"

    # -- VPD
    if "vpd_misiones" not in st.session_state:
        st.session_state["vpd_misiones"] = pd.read_excel(excel_file, sheet_name="vpd_misiones")
    if "vpd_consultores" not in st.session_state:
        st.session_state["vpd_consultores"] = pd.read_excel(excel_file, sheet_name="vpd_consultores")

    # -- VPO
    if "vpo_misiones" not in st.session_state:
        st.session_state["vpo_misiones"] = pd.read_excel(excel_file, sheet_name="vpo_misiones")
    if "vpo_consultores" not in st.session_state:
        st.session_state["vpo_consultores"] = pd.read_excel(excel_file, sheet_name="vpo_consultores")

    # -- VPF
    if "vpf_misiones" not in st.session_state:
        st.session_state["vpf_misiones"] = pd.read_excel(excel_file, sheet_name="vpf_misiones")
    if "vpf_consultores" not in st.session_state:
        st.session_state["vpf_consultores"] = pd.read_excel(excel_file, sheet_name="vpf_consultores")

    # -- VPE
    if "vpe_misiones" not in st.session_state:
        st.session_state["vpe_misiones"] = pd.read_excel(excel_file, sheet_name="vpe_misiones")
    if "vpe_consultores" not in st.session_state:
        st.session_state["vpe_consultores"] = pd.read_excel(excel_file, sheet_name="vpe_consultores")

    # -- PRE
    if "pre_misiones_personal" not in st.session_state:
        st.session_state["pre_misiones_personal"] = pd.read_excel(excel_file, sheet_name="pre_misiones_personal")
    if "pre_misiones_consultores" not in st.session_state:
        st.session_state["pre_misiones_consultores"] = pd.read_excel(excel_file, sheet_name="pre_misiones_consultores")
    if "pre_consultores" not in st.session_state:
        st.session_state["pre_consultores"] = pd.read_excel(excel_file, sheet_name="pre_consultores")

    # -- COM (Comunicaciones)
    if "com" not in st.session_state:
        try:
            st.session_state["com"] = pd.read_excel(excel_file, sheet_name="COM")
        except Exception:
            st.warning("No se encontró la hoja 'COM'. Se crea un DataFrame vacío.")
            st.session_state["com"] = pd.DataFrame()

    # Otros cuadros y centralizados
    if "cuadro_9" not in st.session_state:
        st.session_state["cuadro_9"] = pd.read_excel(excel_file, sheet_name="cuadro_9")
    if "cuadro_10" not in st.session_state:
        st.session_state["cuadro_10"] = pd.read_excel(excel_file, sheet_name="cuadro_10")
    if "cuadro_11" not in st.session_state:
        st.session_state["cuadro_11"] = pd.read_excel(excel_file, sheet_name="cuadro_11")
    if "consolidado_df" not in st.session_state:
        st.session_state["consolidado_df"] = pd.read_excel(excel_file, sheet_name="consolidado")

    if "gastos_centralizados" not in st.session_state:
        st.session_state["gastos_centralizados"] = pd.read_excel(excel_file, sheet_name="gastos_centralizados")

    # Inicialización de tablas "actualizacion_misiones" y "actualizacion_consultorias"
    try:
        act_misiones = pd.read_excel(excel_file, sheet_name="actualizacion_misiones")
    except Exception:
        act_misiones = pd.DataFrame(
            columns=["Unidad Organizacional","Requerimiento del Área","Monto DPP 2025","Diferencia"]
        )
    try:
        act_consultorias = pd.read_excel(excel_file, sheet_name="actualizacion_consultorias")
    except Exception:
        act_consultorias = pd.DataFrame(
            columns=["Unidad Organizacional","Requerimiento del Área","Monto DPP 2025","Diferencia"]
        )

    if "actualizacion_misiones" not in st.session_state:
        st.session_state["actualizacion_misiones"] = act_misiones
    if "actualizacion_consultorias" not in st.session_state:
        st.session_state["actualizacion_consultorias"] = act_consultorias

    # C) SINCRONIZA AUTOMÁTICAMENTE
    sincronizar_actualizacion_al_iniciar()

    # D) MENÚ PRINCIPAL
    st.sidebar.title("Navegación principal")
    secciones = [
        "Página Principal",
        "VPD",
        "VPO",
        "VPF",
        "VPE",
        "PRE",
        "Actualización",
        "Consolidado"
    ]
    eleccion_principal = st.sidebar.selectbox("Selecciona una sección:", secciones)

    # -------------------------------------------------------------------------
    # 1) PÁGINA PRINCIPAL
    # -------------------------------------------------------------------------
    if eleccion_principal == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la Página Principal.")

    # -------------------------------------------------------------------------
    # 2) VPD
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD")

        sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", sub_vpd)

        sub_sub_vpd = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Tema:", sub_sub_vpd)

        # VPD > Misiones
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Misiones > Requerimiento del Área")
                df_req = st.session_state["vpd_misiones"]
                sum_total = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                st.dataframe(df_req)

            else:  # DPP 2025 (Misiones)
                st.subheader("VPD > Misiones > DPP 2025")
                df_base = st.session_state["vpd_misiones"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 168000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"

                # Value boxes
                col1, col2, col3 = st.columns(3)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)

                # Tabla de sumas SOLO para Misiones
                sum_dict = {}
                for col in [
                    "total_pasaje",
                    "total_alojamiento",
                    "total_perdiem_otros",
                    "total_movilidad",
                    "total"
                ]:
                    sum_dict[col] = df_base[col].sum() if col in df_base.columns else 0

                st.markdown("#### Suma de columnas (Misiones)")
                st.dataframe(pd.DataFrame([sum_dict]))

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpd_misiones_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPD Misiones)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_misiones(df_subido)
                        st.session_state["vpd_misiones"] = df_subido
                        guardar_en_excel(df_subido, "vpd_misiones")
                        st.success("¡Tabla de VPD Misiones reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpd_misiones_dpp2025",
                    column_config={
                        "total_pasaje": st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad": st.column_config.NumberColumn(disabled=True),
                        "total": st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                # Botones finales
                if st.button("Recalcular y Guardar (VPD Misiones)"):
                    st.session_state["vpd_misiones"] = df_final
                    guardar_en_excel(df_final, "vpd_misiones")
                    st.success("Datos guardados en 'vpd_misiones'!")

                if st.button("Descargar tabla (VPD Misiones)"):
                    descargar_excel(df_final, file_name="vpd_misiones_modificada.xlsx")

        # VPD > Consultorías
        else:
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Consultorías > Requerimiento del Área")
                df_req = st.session_state["vpd_consultores"]
                sum_total = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                st.dataframe(df_req)

            else:  # DPP 2025 (Consultorías)
                st.subheader("VPD > Consultorías > DPP 2025")
                df_base = st.session_state["vpd_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 130000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"

                # Value boxes
                col1, col2, col3 = st.columns(3)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)

                # Subir archivo para reemplazar
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpd_consultores_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPD Consultorías)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_consultores(df_subido)
                        st.session_state["vpd_consultores"] = df_subido
                        guardar_en_excel(df_subido, "vpd_consultores")
                        st.success("¡Tabla de VPD Consultorías reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpd_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular y Guardar (VPD Consultorías)"):
                    st.session_state["vpd_consultores"] = df_final
                    guardar_en_excel(df_final, "vpd_consultores")
                    st.success("¡Guardado en 'vpd_consultores'!")

    # -------------------------------------------------------------------------
    # 3) VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")

        sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", sub_vpo)

        sub_sub_vpo = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", sub_sub_vpo)

        # VPO > Misiones
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Misiones > Requerimiento del Área")
                df_req = st.session_state["vpo_misiones"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)

            else:
                st.subheader("VPO > Misiones > DPP 2025")
                df_base = st.session_state["vpo_misiones"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 434707
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"

                # Value boxes
                col1, col2, col3 = st.columns(3)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)

                # Tabla de sumas SOLO para Misiones
                sum_dict = {}
                for col in [
                    "total_pasaje",
                    "total_alojamiento",
                    "total_perdiem_otros",
                    "total_movilidad",
                    "total"
                ]:
                    sum_dict[col] = df_base[col].sum() if col in df_base.columns else 0

                st.markdown("#### Suma de columnas (Misiones)")
                st.dataframe(pd.DataFrame([sum_dict]))

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpo_misiones_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPO Misiones)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_misiones(df_subido)
                        st.session_state["vpo_misiones"] = df_subido
                        guardar_en_excel(df_subido, "vpo_misiones")
                        st.success("¡Tabla de VPO Misiones reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpo_misiones_dpp2025",
                    column_config={
                        "total_pasaje": st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad": st.column_config.NumberColumn(disabled=True),
                        "total": st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                if st.button("Recalcular y Guardar (VPO Misiones)"):
                    st.session_state["vpo_misiones"] = df_final
                    guardar_en_excel(df_final, "vpo_misiones")
                    st.success("Guardado en 'vpo_misiones'!")

        # VPO > Consultorías
        else:
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Consultorías > Requerimiento del Área")
                df_req = st.session_state["vpo_consultores"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)

            else:
                st.subheader("VPO > Consultorías > DPP 2025")
                df_base = st.session_state["vpo_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 250000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"

                # Value boxes
                col1, col2, col3 = st.columns(3)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpo_consultores_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPO Consultorías)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_consultores(df_subido)
                        st.session_state["vpo_consultores"] = df_subido
                        guardar_en_excel(df_subido, "vpo_consultores")
                        st.success("¡Tabla de VPO Consultorías reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpo_consultores_dpp2025",
                    column_config={"total": st.column_config.NumberColumn(disabled=True)}
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular y Guardar (VPO Consultorías)"):
                    st.session_state["vpo_consultores"] = df_final
                    guardar_en_excel(df_final, "vpo_consultores")
                    st.success("Guardado en 'vpo_consultores'!")

    # -------------------------------------------------------------------------
    # 4) VPF
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF")

        sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Sub-sección de VPF:", sub_vpf)

        sub_sub_vpf = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Tema:", sub_sub_vpf)

        # VPF > Misiones
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Misiones > Requerimiento del Área")
                df_req = st.session_state["vpf_misiones"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)

            else:
                st.subheader("VPF > Misiones > DPP 2025")
                df_base = st.session_state["vpf_misiones"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 138600
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"

                # Value boxes
                col1, col2, col3 = st.columns(3)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)

                # Tabla de sumas SOLO para Misiones
                sum_dict = {}
                for col in [
                    "total_pasaje",
                    "total_alojamiento",
                    "total_perdiem_otros",
                    "total_movilidad",
                    "total"
                ]:
                    sum_dict[col] = df_base[col].sum() if col in df_base.columns else 0

                st.markdown("#### Suma de columnas (Misiones)")
                st.dataframe(pd.DataFrame([sum_dict]))

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpf_misiones_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPF Misiones)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_misiones(df_subido)
                        st.session_state["vpf_misiones"] = df_subido
                        guardar_en_excel(df_subido, "vpf_misiones")
                        st.success("¡Tabla de VPF Misiones reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpf_misiones_dpp2025",
                    column_config={
                        "total_pasaje":      st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad":   st.column_config.NumberColumn(disabled=True),
                        "total":             st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                if st.button("Recalcular y Guardar (VPF Misiones)"):
                    st.session_state["vpf_misiones"] = df_final
                    guardar_en_excel(df_final, "vpf_misiones")
                    st.success("Guardado en 'vpf_misiones'!")

        # VPF > Consultorías
        else:
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Consultorías > Requerimiento del Área")
                df_req = st.session_state["vpf_consultores"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)

            else:
                st.subheader("VPF > Consultorías > DPP 2025")
                df_base = st.session_state["vpf_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 200000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"

                # Value boxes
                col1, col2, col3 = st.columns(3)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpf_consultores_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPF Consultorías)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_consultores(df_subido)
                        st.session_state["vpf_consultores"] = df_subido
                        guardar_en_excel(df_subido, "vpf_consultores")
                        st.success("¡Tabla de VPF Consultorías reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpf_consultores_dpp2025",
                    column_config={"total": st.column_config.NumberColumn(disabled=True)}
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular y Guardar (VPF Consultorías)"):
                    st.session_state["vpf_consultores"] = df_final
                    guardar_en_excel(df_final, "vpf_consultores")
                    st.success("Guardado en 'vpf_consultores'!")

    # -------------------------------------------------------------------------
    # 5) VPE (EXCLUIDO del recálculo automático de sus filas de total)
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")

        sub_vpe = ["Misiones", "Consultorías"]
        eleccion_vpe_ = st.sidebar.selectbox("Sub-sección de VPE:", sub_vpe)

        sub_sub_vpe = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpe = st.sidebar.selectbox("Tema:", sub_sub_vpe)

        # VPE > Misiones
        if eleccion_vpe_ == "Misiones":
            if eleccion_sub_sub_vpe == "Requerimiento del Área":
                st.subheader("VPE > Misiones > Requerimiento del Área (Solo lectura)")
                df_req = st.session_state["vpe_misiones"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)
            else:
                st.subheader("VPE > Misiones > DPP 2025 (Editable sin fórmulas)")
                df_base = st.session_state["vpe_misiones"].copy()

                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpe_misiones_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPE Misiones)"):
                        df_subido = pd.read_excel(uploaded_file)
                        st.session_state["vpe_misiones"] = df_subido
                        guardar_en_excel(df_subido, "vpe_misiones")
                        st.success("¡Tabla de VPE Misiones reemplazada con éxito!")
                        st.experimental_rerun()

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpe_misiones_dpp2025"
                )

                if st.button("Guardar cambios (VPE Misiones)"):
                    st.session_state["vpe_misiones"] = df_editado
                    guardar_en_excel(df_editado, "vpe_misiones")
                    st.success("Datos guardados en 'vpe_misiones' (sin fórmulas).")

                if st.button("Descargar tabla (VPE Misiones)"):
                    descargar_excel(df_editado, file_name="vpe_misiones_modificada.xlsx")

        # VPE > Consultorías
        else:
            if eleccion_sub_sub_vpe == "Requerimiento del Área":
                st.subheader("VPE > Consultorías > Requerimiento del Área (Solo lectura)")
                df_req = st.session_state["vpe_consultores"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)

            else:
                st.subheader("VPE > Consultorías > DPP 2025 (Editable sin fórmulas)")
                df_base = st.session_state["vpe_consultores"].copy()

                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="vpe_consultores_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (VPE Consultorías)"):
                        df_subido = pd.read_excel(uploaded_file)
                        st.session_state["vpe_consultores"] = df_subido
                        guardar_en_excel(df_subido, "vpe_consultores")
                        st.success("¡Tabla de VPE Consultorías reemplazada con éxito!")
                        st.experimental_rerun()

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpe_consultores_dpp2025"
                )

                if st.button("Guardar cambios (VPE Consultorías)"):
                    st.session_state["vpe_consultores"] = df_editado
                    guardar_en_excel(df_editado, "vpe_consultores")
                    st.success("Datos guardados en 'vpe_consultores' (sin fórmulas).")

                if st.button("Descargar tabla (VPE Consultorías)"):
                    descargar_excel(df_editado, file_name="vpe_consultores_modificada.xlsx")

    # -------------------------------------------------------------------------
    # 6) PRE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "PRE":
        st.title("Sección PRE")

        menu_pre = [
            "Misiones Personal", 
            "Misiones Consultores", 
            "Consultorías", 
            "Comunicaciones", 
            "Gastos Centralizados"
        ]
        eleccion_pre = st.sidebar.selectbox("Sub-sección de PRE:", menu_pre)

        # A) PRE > Misiones Personal
        if eleccion_pre == "Misiones Personal":
            sub_sub_pre_mp = ["Requerimiento del Área", "DPP 2025"]
            eleccion_sub_sub_pre_mp = st.sidebar.selectbox("Tema (Misiones Personal):", sub_sub_pre_mp)

            if eleccion_sub_sub_pre_mp == "Requerimiento del Área":
                st.subheader("PRE > Misiones Personal > Requerimiento del Área (Solo lectura)")
                df_pre = st.session_state["pre_misiones_personal"]
                sum_total = df_pre["total"].sum() if "total" in df_pre.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                mostrar_value_boxes_por_area(df_pre, col_area="area_imputacion")
                st.dataframe(df_pre)

            else:  # DPP 2025 (Misiones Personal)
                st.subheader("PRE > Misiones Personal > DPP 2025")
                df_base = st.session_state["pre_misiones_personal"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")

                # Tabla de sumas (Misiones)
                sum_dict = {}
                for col in [
                    "total_pasaje",
                    "total_alojamiento",
                    "total_perdiem_otros",
                    "total_movilidad",
                    "total"
                ]:
                    sum_dict[col] = df_base[col].sum() if col in df_base.columns else 0

                st.markdown("#### Suma de columnas (Misiones Personal)")
                st.dataframe(pd.DataFrame([sum_dict]))

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "Cargar un archivo Excel para reemplazar esta tabla",
                    type=["xlsx"],
                    key="pre_misiones_personal_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (PRE Misiones Personal)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_misiones(df_subido)
                        st.session_state["pre_misiones_personal"] = df_subido
                        guardar_en_excel(df_subido, "pre_misiones_personal")
                        st.success("¡Tabla de PRE Misiones Personal reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="pre_misiones_personal_dpp2025",
                    column_config={
                        "total_pasaje":      st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad":   st.column_config.NumberColumn(disabled=True),
                        "total":             st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                st.markdown("### Totales por Área de Imputación")
                mostrar_value_boxes_por_area(df_final, col_area="area_imputacion")

                if st.button("Recalcular y Guardar (PRE Misiones Personal)"):
                    st.session_state["pre_misiones_personal"] = df_final
                    guardar_en_excel(df_final, "pre_misiones_personal")
                    st.success("¡Datos guardados en 'pre_misiones_personal'!")

                if st.button("Descargar tabla (PRE Misiones Personal)"):
                    descargar_excel(df_final, file_name="pre_misiones_personal_modificada.xlsx")

        # B) PRE > Misiones Consultores
        elif eleccion_pre == "Misiones Consultores":
            sub_sub_pre_mc = ["Requerimiento del Área", "DPP 2025"]
            eleccion_sub_sub_pre_mc = st.sidebar.selectbox("Tema (Misiones Consultores):", sub_sub_pre_mc)

            if eleccion_sub_sub_pre_mc == "Requerimiento del Área":
                st.subheader("PRE > Misiones Consultores > Requerimiento del Área (Solo lectura)")
                df_pre = st.session_state["pre_misiones_consultores"]
                sum_total = df_pre["total"].sum() if "total" in df_pre.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                mostrar_value_boxes_por_area(df_pre, col_area="area_imputacion")
                st.dataframe(df_pre)

            else:  # DPP 2025
                st.subheader("PRE > Misiones Consultores > DPP 2025")
                df_base = st.session_state["pre_misiones_consultores"].copy()
                df_base = calcular_misiones(df_base)
                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")

                # Tabla de sumas (Misiones)
                sum_dict = {}
                for col in [
                    "total_pasaje",
                    "total_alojamiento",
                    "total_perdiem_otros",
                    "total_movilidad",
                    "total"
                ]:
                    sum_dict[col] = df_base[col].sum() if col in df_base.columns else 0

                st.markdown("#### Suma de columnas (Misiones Consultores)")
                st.dataframe(pd.DataFrame([sum_dict]))

                # Reemplazar tabla
                uploaded_file = st.file_uploader(
                    "...", type=["xlsx"], key="pre_misiones_consultores_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (PRE Misiones Consultores)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_misiones(df_subido)
                        st.session_state["pre_misiones_consultores"] = df_subido
                        guardar_en_excel(df_subido, "pre_misiones_consultores")
                        st.success("¡Tabla de PRE Misiones Consultores reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="pre_misiones_consultores_dpp2025",
                    column_config={
                        "total_pasaje":      st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad":   st.column_config.NumberColumn(disabled=True),
                        "total":             st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                st.markdown("### Totales por Área de Imputación")
                mostrar_value_boxes_por_area(df_final, col_area="area_imputacion")

                if st.button("Recalcular y Guardar (PRE Misiones Consultores)"):
                    st.session_state["pre_misiones_consultores"] = df_final
                    guardar_en_excel(df_final, "pre_misiones_consultores")
                    st.success("¡Datos guardados en 'pre_misiones_consultores'!")

                if st.button("Descargar tabla (PRE Misiones Consultores)"):
                    descargar_excel(df_final, file_name="pre_misiones_consultores_modificada.xlsx")

        # C) PRE > Consultorías
        elif eleccion_pre == "Consultorías":
            sub_sub_pre_co = ["Requerimiento del Área", "DPP 2025"]
            eleccion_sub_sub_pre_co = st.sidebar.selectbox("Tema (Consultorías):", sub_sub_pre_co)

            if eleccion_sub_sub_pre_co == "Requerimiento del Área":
                st.subheader("PRE > Consultorías > Requerimiento del Área (Solo lectura)")
                df_pre = st.session_state["pre_consultores"]
                if "total" in df_pre.columns:
                    df_pre["total"] = pd.to_numeric(df_pre["total"], errors="coerce")

                sum_total = df_pre["total"].sum() if "total" in df_pre.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                mostrar_value_boxes_por_area(df_pre, col_area="area_imputacion")
                st.dataframe(df_pre)

            else:  # DPP 2025 (Consultorías)
                st.subheader("PRE > Consultorías > DPP 2025")
                df_base = st.session_state["pre_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")

                # Subir archivo
                uploaded_file = st.file_uploader(
                    "...", type=["xlsx"], key="pre_consultores_file"
                )
                if uploaded_file is not None:
                    if st.button("Reemplazar tabla (PRE Consultorías)"):
                        df_subido = pd.read_excel(uploaded_file)
                        df_subido = calcular_consultores(df_subido)
                        st.session_state["pre_consultores"] = df_subido
                        guardar_en_excel(df_subido, "pre_consultores")
                        st.success("¡Tabla de PRE Consultorías reemplazada con éxito!")
                        st.experimental_rerun()

                # Edición en línea
                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="pre_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)

                st.markdown("### Totales por Área de Imputación")
                mostrar_value_boxes_por_area(df_final, col_area="area_imputacion")

                if st.button("Recalcular y Guardar (PRE Consultorías)"):
                    st.session_state["pre_consultores"] = df_final
                    guardar_en_excel(df_final, "pre_consultores")
                    st.success("¡Datos guardados en 'pre_consultores'!")

                if st.button("Descargar tabla (PRE Consultorías)"):
                    descargar_excel(df_final, file_name="pre_consultores_modificada.xlsx")

        # D) PRE > Comunicaciones
        elif eleccion_pre == "Comunicaciones":
            st.subheader("PRE > Comunicaciones (COM)")
            df_com = st.session_state["com"]
            st.dataframe(df_com)
            st.info("Tabla de Comunicaciones (COM) mostrada aquí.")

        # E) PRE > Gastos Centralizados (mostrando copias DPP)
        else:
            st.subheader("PRE > Gastos Centralizados (DPP 2025)")

            st.write("### Copia: Misiones Personal (cálculo DPP)")
            df_mp = calcular_misiones(st.session_state["pre_misiones_personal"].copy())
            st.dataframe(df_mp)

            st.write("### Copia: Misiones Consultores (cálculo DPP)")
            df_mc = calcular_misiones(st.session_state["pre_misiones_consultores"].copy())
            st.dataframe(df_mc)

            st.write("### Copia: Consultorías (cálculo DPP)")
            df_c = calcular_consultores(st.session_state["pre_consultores"].copy())
            st.dataframe(df_c)

    # -------------------------------------------------------------------------
    # 7) ACTUALIZACIÓN
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización")
        st.write("Estas tablas se sincronizan automáticamente al iniciar la app.")

        st.write("### Tabla de Misiones")
        df_misiones = st.session_state["actualizacion_misiones"]
        st.dataframe(
            df_misiones
            .style
            .format("{:,.2f}", subset=["Requerimiento del Área", "Monto DPP 2025", "Diferencia"])
            .applymap(color_diferencia, subset=["Diferencia"])
        )

        st.write("### Tabla de Consultorías")
        df_cons = st.session_state["actualizacion_consultorias"]
        st.dataframe(
            df_cons
            .style
            .format("{:,.2f}", subset=["Requerimiento del Área", "Monto DPP 2025", "Diferencia"])
            .applymap(color_diferencia, subset=["Diferencia"])
        )

        st.info("Se actualizan al iniciar la app y cada vez que recalculas o cargas datos en DPP 2025.")

    # -------------------------------------------------------------------------
    # 8) CONSOLIDADO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")

        st.write("#### Gasto en personal 2024 Vs 2025 (Cuadro 9)")
        df_9 = st.session_state["cuadro_9"]
        st.table(two_decimals_only_numeric(df_9))

        st.write("---")
        st.write("#### Análisis de Cambios en Gastos de Personal 2025 vs. 2024 (Cuadro 10)")
        df_10 = st.session_state["cuadro_10"]
        st.table(two_decimals_only_numeric(df_10))

        st.write("---")
        st.write("#### Gastos Operativos propuestos para 2025 y montos aprobados para 2024 (Cuadro 11)")
        df_11 = st.session_state["cuadro_11"]
        st.table(two_decimals_only_numeric(df_11))

        st.write("---")
        st.write("#### DPP 2025 (Consolidado)")
        df_cons2 = st.session_state["consolidado_df"]
        st.table(two_decimals_only_numeric(df_cons2))


# -----------------------------------------------------------------------------
# 10. EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
