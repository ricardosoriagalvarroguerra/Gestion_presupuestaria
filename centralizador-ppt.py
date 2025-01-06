import streamlit as st
import pandas as pd
import io

# =============================================================================
# 1. FUNCIONES DE CÁLCULO
# =============================================================================
def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula totales para tablas de Misiones, de acuerdo con las columnas base:
    - cant_funcionarios, costo_pasaje, dias, alojamiento, perdiem_otros, movilidad.
    - total_pasaje = cant_funcionarios * costo_pasaje
    - total_alojamiento = cant_funcionarios * dias * alojamiento
    - total_perdiem_otros = cant_funcionarios * dias * perdiem_otros
    - total_movilidad = cant_funcionarios * movilidad
    - total = suma de los anteriores
    """
    df_calc = df.copy()
    cols_base = ["cant_funcionarios", "costo_pasaje", "dias",
                 "alojamiento", "perdiem_otros", "movilidad"]
    for col in cols_base:
        if col not in df_calc.columns:
            df_calc[col] = 0

    df_calc["total_pasaje"] = df_calc["cant_funcionarios"] * df_calc["costo_pasaje"]
    df_calc["total_alojamiento"] = (
        df_calc["cant_funcionarios"] * df_calc["dias"] * df_calc["alojamiento"]
    )
    df_calc["total_perdiem_otros"] = (
        df_calc["cant_funcionarios"] * df_calc["dias"] * df_calc["perdiem_otros"]
    )
    df_calc["total_movilidad"] = df_calc["cant_funcionarios"] * df_calc["movilidad"]
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
    - total = cantidad_funcionarios * cantidad_meses * monto_mensual
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
    """
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    return df.style.format("{:,.2f}", subset=numeric_cols, na_rep="")

# =============================================================================
# 3. FUNCIÓN PARA MOSTRAR UN "VALUE BOX" CON HTML/CSS
# =============================================================================
def value_box(label: str, value, bg_color: str = "#6c757d"):
    """
    Muestra un pequeño recuadro con color de fondo (bg_color) y texto en blanco.
    """
    st.markdown(f"""
    <div style="display:inline-block; background-color:{bg_color}; 
                padding:10px; margin:5px; border-radius:5px; color:white; font-weight:bold;">
        <div style="font-size:14px;">{label}</div>
        <div style="font-size:20px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 4. FUNCIÓN PARA COLOREAR LA DIFERENCIA
# =============================================================================
def color_diferencia(val):
    """
    Retorna un estilo de color distinto si val != 0, y verde si val == 0.
    """
    return "background-color: #fb8500; color:white" if val != 0 else "background-color: green; color:white"

# =============================================================================
# 5. FUNCIÓN PARA GUARDAR DATOS EN EXCEL (REEMPLAZANDO UNA HOJA)
# =============================================================================
def guardar_en_excel(df: pd.DataFrame, sheet_name: str, excel_file: str = "main_bdd.xlsx"):
    """
    Guarda el DataFrame df en la hoja 'sheet_name' del archivo excel_file,
    reemplazando esa hoja y manteniendo las demás.
    """
    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

# =============================================================================
# 6. FUNCIÓN PARA DESCARGAR UN DataFrame COMO EXCEL (BOTÓN)
# =============================================================================
def descargar_excel(df: pd.DataFrame, file_name: str = "descarga.xlsx") -> None:
    """
    Genera un archivo Excel en memoria y lo ofrece para descargar con st.download_button.
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
# 7. FUNCIÓN PRINCIPAL DE LA APLICACIÓN
# =============================================================================
def main():
    st.set_page_config(page_title="Aplicación Completa", layout="wide")

    # -------------------------------------------------------------------------
    # A) LOGIN (mantiene st.rerun)
    # -------------------------------------------------------------------------
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.title("Login - Presupuesto 2025")

        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión"):
            valid_users = ["mcalvino", "ajustinianon"]
            valid_password = "2025presupuesto"
            if username in valid_users and password == valid_password:
                st.session_state["logged_in"] = True
                st.rerun()  # Se mantiene la lógica original
            else:
                st.error("Usuario o contraseña incorrectos.")
        return
    else:
        st.sidebar.success("Sesión iniciada.")

    excel_file = "main_bdd.xlsx"

    # -------------------------------------------------------------------------
    # B) LECTURA DE DATOS DESDE EXCEL A session_state
    # -------------------------------------------------------------------------
    # Se realiza solo si aún no existen en session_state.
    if "vpd_misiones" not in st.session_state:
        st.session_state["vpd_misiones"] = pd.read_excel(excel_file, sheet_name="vpd_misiones")
    if "vpd_consultores" not in st.session_state:
        st.session_state["vpd_consultores"] = pd.read_excel(excel_file, sheet_name="vpd_consultores")

    if "vpo_misiones" not in st.session_state:
        st.session_state["vpo_misiones"] = pd.read_excel(excel_file, sheet_name="vpo_misiones")
    if "vpo_consultores" not in st.session_state:
        st.session_state["vpo_consultores"] = pd.read_excel(excel_file, sheet_name="vpo_consultores")

    if "vpf_misiones" not in st.session_state:
        st.session_state["vpf_misiones"] = pd.read_excel(excel_file, sheet_name="vpf_misiones")
    if "vpf_consultores" not in st.session_state:
        st.session_state["vpf_consultores"] = pd.read_excel(excel_file, sheet_name="vpf_consultores")

    if "vpe_misiones" not in st.session_state:
        st.session_state["vpe_misiones"] = pd.read_excel(excel_file, sheet_name="vpe_misiones")
    if "vpe_consultores" not in st.session_state:
        st.session_state["vpe_consultores"] = pd.read_excel(excel_file, sheet_name="vpe_consultores")

    if "cuadro_9" not in st.session_state:
        st.session_state["cuadro_9"] = pd.read_excel(excel_file, sheet_name="cuadro_9")
    if "cuadro_10" not in st.session_state:
        st.session_state["cuadro_10"] = pd.read_excel(excel_file, sheet_name="cuadro_10")
    if "cuadro_11" not in st.session_state:
        st.session_state["cuadro_11"] = pd.read_excel(excel_file, sheet_name="cuadro_11")
    if "consolidado_df" not in st.session_state:
        st.session_state["consolidado_df"] = pd.read_excel(excel_file, sheet_name="consolidado")

    if "pre_misiones_personal" not in st.session_state:
        st.session_state["pre_misiones_personal"] = pd.read_excel(excel_file, sheet_name="pre_misiones_personal")
    if "pre_misiones_consultores" not in st.session_state:
        st.session_state["pre_misiones_consultores"] = pd.read_excel(excel_file, sheet_name="pre_misiones_consultores")
    if "pre_consultores" not in st.session_state:
        st.session_state["pre_consultores"] = pd.read_excel(excel_file, sheet_name="pre_consultores")

    # NUEVO: leer gastos_centralizados
    if "gastos_centralizados" not in st.session_state:
        st.session_state["gastos_centralizados"] = pd.read_excel(excel_file, sheet_name="gastos_centralizados")

    # -------------------------------------------------------------------------
    # C) LECTURA/INICIALIZACIÓN DE TABLAS DE ACTUALIZACIÓN
    # -------------------------------------------------------------------------
    try:
        act_misiones = pd.read_excel(excel_file, sheet_name="actualizacion_misiones")
    except:
        act_misiones = pd.DataFrame()
    try:
        act_consultorias = pd.read_excel(excel_file, sheet_name="actualizacion_consultorias")
    except:
        act_consultorias = pd.DataFrame()

    if "actualizacion_misiones" not in st.session_state:
        st.session_state["actualizacion_misiones"] = act_misiones
    if "actualizacion_consultorias" not in st.session_state:
        st.session_state["actualizacion_consultorias"] = act_consultorias

    # -------------------------------------------------------------------------
    # D) MENÚ PRINCIPAL
    # -------------------------------------------------------------------------
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
    # E) SECCIONES
    # -------------------------------------------------------------------------
    # 1) Página Principal
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

        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Misiones > Requerimiento del Área")
                df_req = st.session_state["vpd_misiones"]
                sum_total = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                st.dataframe(df_req)
                st.session_state["requerimiento_area_vpd_misiones"] = sum_total

            else:  # DPP 2025
                st.subheader("VPD > Misiones > DPP 2025")
                df_base = st.session_state["vpd_misiones"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 168000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_cent = 35960
                total_gasto_cent = sum_total + gasto_cent

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_cent:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_cent:,.2f}")

                st.session_state["requerimiento_area_vpd_misiones"] = sum_total
                st.session_state["monto_dpp_vpd_misiones"] = monto_dpp
                st.session_state["diferencia_vpd_misiones"] = diferencia

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpd_misiones_dpp2025",
                    column_config={
                        "total_pasaje":      st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad":   st.column_config.NumberColumn(disabled=True),
                        "total":             st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                if st.button("Recalcular (VPD Misiones)"):
                    st.session_state["vpd_misiones"] = df_final
                    guardar_en_excel(df_final, sheet_name="vpd_misiones")
                    st.success("Datos guardados en 'vpd_misiones'!")

                if st.button("Descargar tabla (VPD Misiones)"):
                    descargar_excel(df_final, file_name="vpd_misiones_modificada.xlsx")

                st.write("**Sumas totales**")
                df_resumen = pd.DataFrame({
                    "Total Pasaje": [df_final["total_pasaje"].sum()],
                    "Total Alojamiento": [df_final["total_alojamiento"].sum()],
                    "Total PerDiem/Otros": [df_final["total_perdiem_otros"].sum()],
                    "Total Movilidad": [df_final["total_movilidad"].sum()],
                    "Total": [df_final["total"].sum()]
                })
                st.table(df_resumen.style.format("{:,.2f}"))

        else:  # VPD > Consultorías
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Consultorías > Requerimiento del Área")
                df_req = st.session_state["vpd_consultores"]
                sum_total = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")
                st.dataframe(df_req)
                st.session_state["requerimiento_area_vpd_consultorias"] = sum_total

            else:  # DPP 2025
                st.subheader("VPD > Consultorías > DPP 2025")
                df_base = st.session_state["vpd_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 130000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_cent = 193160
                total_gc = sum_total + gasto_cent

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_cent:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gc:,.2f}")

                st.session_state["requerimiento_area_vpd_consultorias"] = sum_total
                st.session_state["monto_dpp_vpd_consultorias"] = monto_dpp
                st.session_state["diferencia_vpd_consultorias"] = diferencia

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpd_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular (VPD Consultorías)"):
                    st.session_state["vpd_consultores"] = df_final
                    guardar_en_excel(df_final, sheet_name="vpd_consultores")
                    st.success("¡Guardado en 'vpd_consultores'!")

                if st.button("Descargar tabla (VPD Consultorías)"):
                    descargar_excel(df_final, file_name="vpd_consultores_modificada.xlsx")

                st.write("**Resumen de totales**")
                st.write(f"Total final: {df_final['total'].sum():,.2f}")

    # -------------------------------------------------------------------------
    # 3) VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")
        sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", sub_vpo)

        sub_sub_vpo = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", sub_sub_vpo)

        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Misiones > Requerimiento del Área")
                df_req = st.session_state["vpo_misiones"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)
                st.session_state["requerimiento_area_vpo_misiones"] = total_sum

            else:  # DPP 2025
                st.subheader("VPO > Misiones > DPP 2025")
                df_base = st.session_state["vpo_misiones"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 434707
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_cent = 48158
                total_gc = sum_total + gasto_cent

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_cent:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gc:,.2f}")

                st.session_state["requerimiento_area_vpo_misiones"] = sum_total
                st.session_state["monto_dpp_vpo_misiones"] = monto_dpp
                st.session_state["diferencia_vpo_misiones"] = diferencia

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpo_misiones_dpp2025",
                    column_config={
                        "total_pasaje":      st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad":   st.column_config.NumberColumn(disabled=True),
                        "total":             st.column_config.NumberColumn(disabled=True),
                    }
                )
                df_final = calcular_misiones(df_editado)

                if st.button("Recalcular (VPO Misiones)"):
                    st.session_state["vpo_misiones"] = df_final
                    guardar_en_excel(df_final, "vpo_misiones")
                    st.success("Guardado en 'vpo_misiones'!")

                if st.button("Descargar tabla (VPO Misiones)"):
                    descargar_excel(df_final, file_name="vpo_misiones_modificada.xlsx")

        else:  # VPO > Consultorías
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Consultorías > Requerimiento del Área")
                df_req = st.session_state["vpo_consultores"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)
                st.session_state["requerimiento_area_vpo_consultorias"] = total_sum

            else:  # DPP 2025
                st.subheader("VPO > Consultorías > DPP 2025")
                df_base = st.session_state["vpo_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 250000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_cent = 50000
                total_gc = sum_total + gasto_cent

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_cent:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gc:,.2f}")

                st.session_state["requerimiento_area_vpo_consultorias"] = sum_total
                st.session_state["monto_dpp_vpo_consultorias"] = monto_dpp
                st.session_state["diferencia_vpo_consultorias"] = diferencia

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpo_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular (VPO Consultorías)"):
                    st.session_state["vpo_consultores"] = df_final
                    guardar_en_excel(df_final, "vpo_consultores")
                    st.success("Guardado en 'vpo_consultores'!")

                if st.button("Descargar tabla (VPO Consultorías)"):
                    descargar_excel(df_final, file_name="vpo_consultores_modificada.xlsx")

    # -------------------------------------------------------------------------
    # 4) VPF
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF")
        sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Sub-sección de VPF:", sub_vpf)

        sub_sub_vpf = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Tema:", sub_sub_vpf)

        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Misiones > Requerimiento del Área")
                df_req = st.session_state["vpf_misiones"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)
                st.session_state["requerimiento_area_vpf_misiones"] = total_sum

            else:  # DPP 2025
                st.subheader("VPF > Misiones > DPP 2025")
                df_base = st.session_state["vpf_misiones"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 138600
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_cent = 40960
                total_gc = sum_total + gasto_cent

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_cent:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gc:,.2f}")

                st.session_state["requerimiento_area_vpf_misiones"] = sum_total
                st.session_state["monto_dpp_vpf_misiones"] = monto_dpp
                st.session_state["diferencia_vpf_misiones"] = diferencia

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

                if st.button("Recalcular (VPF Misiones)"):
                    st.session_state["vpf_misiones"] = df_final
                    guardar_en_excel(df_final, "vpf_misiones")
                    st.success("Guardado en 'vpf_misiones'!")

                if st.button("Descargar tabla (VPF Misiones)"):
                    descargar_excel(df_final, file_name="vpf_misiones_modificada.xlsx")

        else:  # VPF > Consultorías
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Consultorías > Requerimiento del Área")
                df_req = st.session_state["vpf_consultores"]
                total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req)
                st.session_state["requerimiento_area_vpf_consultores"] = total_sum

            else:  # DPP 2025
                st.subheader("VPF > Consultorías > DPP 2025")
                df_base = st.session_state["vpf_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                monto_dpp = 200000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_cent = 60000
                total_gc = sum_total + gasto_cent

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_cent:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gc:,.2f}")

                st.session_state["requerimiento_area_vpf_consultores"] = sum_total
                st.session_state["monto_dpp_vpf_consultores"] = monto_dpp
                st.session_state["diferencia_vpf_consultores"] = diferencia

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="vpf_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular (VPF Consultorías)"):
                    st.session_state["vpf_consultores"] = df_final
                    guardar_en_excel(df_final, "vpf_consultores")
                    st.success("Guardado en 'vpf_consultores'!")

                if st.button("Descargar tabla (VPF Consultorías)"):
                    descargar_excel(df_final, file_name="vpf_consultores_modificada.xlsx")

    # -------------------------------------------------------------------------
    # 5) VPE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")

        sub_vpe = ["Misiones", "Consultorías"]
        eleccion_vpe = st.sidebar.selectbox("Sub-sección de VPE:", sub_vpe)

        sub_sub_vpe = ["Requerimiento del Área"]
        eleccion_sub_sub_vpe = st.sidebar.selectbox("Tema:", sub_sub_vpe)

        if eleccion_vpe == "Misiones":
            st.subheader("VPE > Misiones > Requerimiento del Área (Solo lectura)")
            df_req = st.session_state["vpe_misiones"]
            total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
            value_box("Suma del total", f"{total_sum:,.2f}")
            st.dataframe(df_req)
            st.session_state["requerimiento_area_vpe_misiones"] = total_sum

        else:
            st.subheader("VPE > Consultorías > Requerimiento del Área (Solo lectura)")
            df_req = st.session_state["vpe_consultores"]
            total_sum = df_req["total"].sum() if "total" in df_req.columns else 0
            value_box("Suma del total", f"{total_sum:,.2f}")
            st.dataframe(df_req)
            st.session_state["requerimiento_area_vpe_consultorias"] = total_sum

    # -------------------------------------------------------------------------
    # 6) PRE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "PRE":
        st.title("Sección PRE")
        menu_pre = ["Misiones Personal", "Misiones Consultores", "Consultorías", "Gastos Centralizados"]
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
                st.dataframe(df_pre)

            else:  # "DPP 2025" => editable
                st.subheader("PRE > Misiones Personal > DPP 2025")
                df_base = st.session_state["pre_misiones_personal"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")

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

                if st.button("Recalcular (PRE Misiones Personal)"):
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
                st.dataframe(df_pre)

            else:  # "DPP 2025" => editable
                st.subheader("PRE > Misiones Consultores > DPP 2025")
                df_base = st.session_state["pre_misiones_consultores"].copy()
                df_base = calcular_misiones(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")

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

                if st.button("Recalcular (PRE Misiones Consultores)"):
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

                # --------------------------------------------------------------------------------
                # AQUI SE HACE LA CONVERSIÓN PARA EVITAR EL TypeError (string + int)
                # --------------------------------------------------------------------------------
                df_pre = st.session_state["pre_consultores"]
                if "total" in df_pre.columns:
                    df_pre["total"] = pd.to_numeric(df_pre["total"], errors="coerce")  # <-- FIX
                sum_total = df_pre["total"].sum() if "total" in df_pre.columns else 0
                # --------------------------------------------------------------------------------

                value_box("Suma del total", f"{sum_total:,.2f}")
                st.dataframe(df_pre)

            else:  # "DPP 2025" => editable
                st.subheader("PRE > Consultorías > DPP 2025")
                df_base = st.session_state["pre_consultores"].copy()
                df_base = calcular_consultores(df_base)

                sum_total = df_base["total"].sum() if "total" in df_base.columns else 0
                value_box("Suma del total", f"{sum_total:,.2f}")

                df_editado = st.data_editor(
                    df_base,
                    use_container_width=True,
                    key="pre_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)

                if st.button("Recalcular (PRE Consultorías)"):
                    st.session_state["pre_consultores"] = df_final
                    guardar_en_excel(df_final, "pre_consultores")
                    st.success("¡Datos guardados en 'pre_consultores'!")

                if st.button("Descargar tabla (PRE Consultorías)"):
                    descargar_excel(df_final, file_name="pre_consultores_modificada.xlsx")

        # D) PRE > Gastos Centralizados (Solo lectura directo desde la bdd)
        else:
            st.subheader("PRE > Gastos Centralizados (Solo lectura)")
            df_gc = st.session_state["gastos_centralizados"]
            st.dataframe(df_gc)

    # -------------------------------------------------------------------------
    # 7) ACTUALIZACIÓN
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización")

        units = ["VPE", "VPD", "VPO", "VPF"]

        st.write("### Tabla de Misiones")
        misiones_data = []
        for unit in units:
            req_key = f"requerimiento_area_{unit.lower()}_misiones"
            dpp_key = f"monto_dpp_{unit.lower()}_misiones"
            dif_key = f"diferencia_{unit.lower()}_misiones"

            req_area = st.session_state.get(req_key, 0.0)
            monto_dpp = st.session_state.get(dpp_key, 0.0)
            diferencia = st.session_state.get(dif_key, monto_dpp - req_area)

            misiones_data.append({
                "Unidad Organizacional": unit,
                "Requerimiento del Área": req_area,
                "Monto DPP 2025": monto_dpp,
                "Diferencia": diferencia
            })

        df_misiones = pd.DataFrame(misiones_data)
        st.session_state["actualizacion_misiones"] = df_misiones

        st.dataframe(
            df_misiones.style
            .format("{:,.2f}", subset=["Requerimiento del Área", "Monto DPP 2025", "Diferencia"])
            .applymap(color_diferencia, subset=["Diferencia"])
        )

        st.write("### Tabla de Consultorías")
        consultorias_data = []
        for unit in units:
            req_key = f"requerimiento_area_{unit.lower()}_consultorias"
            dpp_key = f"monto_dpp_{unit.lower()}_consultorias"
            dif_key = f"diferencia_{unit.lower()}_consultorias"

            req_area = st.session_state.get(req_key, 0.0)
            monto_dpp = st.session_state.get(dpp_key, 0.0)
            diferencia = st.session_state.get(dif_key, monto_dpp - req_area)

            consultorias_data.append({
                "Unidad Organizacional": unit,
                "Requerimiento del Área": req_area,
                "Monto DPP 2025": monto_dpp,
                "Diferencia": diferencia
            })

        df_cons = pd.DataFrame(consultorias_data)
        st.session_state["actualizacion_consultorias"] = df_cons

        st.dataframe(
            df_cons.style
            .format("{:,.2f}", subset=["Requerimiento del Área", "Monto DPP 2025", "Diferencia"])
            .applymap(color_diferencia, subset=["Diferencia"])
        )

        # Botón para guardar la tabla de Actualización en Excel
        if st.button("Guardar Actualización"):
            guardar_en_excel(st.session_state["actualizacion_misiones"], "actualizacion_misiones")
            guardar_en_excel(st.session_state["actualizacion_consultorias"], "actualizacion_consultorias")
            st.success("¡Tablas de Actualización guardadas en Excel!")

        st.info("La tabla de Actualización se guarda en 'actualizacion_misiones' y 'actualizacion_consultorias' para no reiniciarse al cerrar la app.")

    # -------------------------------------------------------------------------
    # 8) CONSOLIDADO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")

        st.write("#### Gasto en personal 2024 Vs 2025")
        df_9 = st.session_state["cuadro_9"]
        st.table(two_decimals_only_numeric(df_9))
        st.caption("Cuadro 9 - DPP 2025")

        st.write("---")
        st.write("#### Análisis de Cambios en Gastos de Personal 2025 vs. 2024")
        df_10 = st.session_state["cuadro_10"]
        st.table(two_decimals_only_numeric(df_10))
        st.caption("Cuadro 10 - DPP 2025")

        st.write("---")
        st.write("#### Gastos Operativos propuestos para 2025 y montos aprobados para 2024")
        df_11 = st.session_state["cuadro_11"]
        st.table(two_decimals_only_numeric(df_11))
        st.caption("Cuadro 11 - DPP 2025")

        st.write("---")
        st.write("#### DPP 2025")
        df_cons = st.session_state["consolidado_df"]
        st.table(two_decimals_only_numeric(df_cons))

# =============================================================================
# 8. EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    main()
