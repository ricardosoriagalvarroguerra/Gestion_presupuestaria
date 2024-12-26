import streamlit as st
import pandas as pd

# =============================================================================
# 1. FUNCIONES DE CÁLCULO
# =============================================================================
def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Para tablas de Misiones (DPP 2025):
      total_pasaje = cant_funcionarios * costo_pasaje
      total_alojamiento = dias * cant_funcionarios * alojamiento
      total_perdiem_otros = dias * cant_funcionarios * perdiem_otros
      total_movilidad = cant_funcionarios * movilidad
      total = suma de las anteriores
    """
    df_calc = df.copy()
    cols_base = ["cant_funcionarios", "costo_pasaje", "dias", 
                 "alojamiento", "perdiem_otros", "movilidad"]
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
    """
    Para tablas de Consultorías (DPP 2025):
      total = cantidad_funcionarios * cantidad_meses * monto_mensual
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
# 2. FUNCIÓN PARA FORMATEAR SOLO COLUMNAS NUMÉRICAS A DOS DECIMALES
# =============================================================================
def two_decimals_only_numeric(df: pd.DataFrame):
    """
    Aplica "{:,.2f}" solo a columnas numéricas (float, int),
    evitando errores si hay texto o fechas.
    """
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    return df.style.format("{:,.2f}", subset=numeric_cols, na_rep="")

# =============================================================================
# 3. FUNCIÓN PARA MOSTRAR "VALUE BOX" (HTML/CSS)
# =============================================================================
def value_box(label: str, value, bg_color: str = "#6c757d"):
    """
    Genera un recuadro (value box) con fondo de color y texto en blanco.
    label: etiqueta (p.ej. "Suma del total")
    value: valor a mostrar (p.ej. "12345.67")
    bg_color: color de fondo (por defecto gris "#6c757d")
    """
    st.markdown(f"""
    <div style="display:inline-block; background-color:{bg_color}; 
                padding:10px; margin:5px; border-radius:5px; color:white; font-weight:bold;">
        <div style="font-size:14px;">{label}</div>
        <div style="font-size:20px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================
def main():
    st.set_page_config(page_title="Aplicación Completa", layout="wide")

    # -------------------------------------------------------------------------
    # A) LECTURA DE DATOS DESDE EXCEL (SOLO UNA VEZ) - SESSION_STATE
    # -------------------------------------------------------------------------
    # VPD
    if "vpd_misiones" not in st.session_state:
        st.session_state["vpd_misiones"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
    if "vpd_consultores" not in st.session_state:
        st.session_state["vpd_consultores"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")

    # VPO
    if "vpo_misiones" not in st.session_state:
        st.session_state["vpo_misiones"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
    if "vpo_consultores" not in st.session_state:
        st.session_state["vpo_consultores"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")

    # VPF
    if "vpf_misiones" not in st.session_state:
        st.session_state["vpf_misiones"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
    if "vpf_consultores" not in st.session_state:
        st.session_state["vpf_consultores"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")

    # VPE
    if "vpe_misiones" not in st.session_state:
        st.session_state["vpe_misiones"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_misiones")
    if "vpe_consultores" not in st.session_state:
        st.session_state["vpe_consultores"] = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_consultores")

    # Consolidado
    if "cuadro_9" not in st.session_state:
        st.session_state["cuadro_9"] = pd.read_excel("main_bdd.xlsx", sheet_name="cuadro_9")
    if "cuadro_10" not in st.session_state:
        st.session_state["cuadro_10"] = pd.read_excel("main_bdd.xlsx", sheet_name="cuadro_10")
    if "cuadro_11" not in st.session_state:
        st.session_state["cuadro_11"] = pd.read_excel("main_bdd.xlsx", sheet_name="cuadro_11")
    if "consolidado_df" not in st.session_state:
        st.session_state["consolidado_df"] = pd.read_excel("main_bdd.xlsx", sheet_name="consolidado")

    # PRE
    if "pre_misiones_personal" not in st.session_state:
        st.session_state["pre_misiones_personal"] = pd.read_excel("main_bdd.xlsx", sheet_name="pre_misiones_personal")
    if "pre_misiones_consultores" not in st.session_state:
        st.session_state["pre_misiones_consultores"] = pd.read_excel("main_bdd.xlsx", sheet_name="pre_misiones_consultores")
    if "pre_consultores" not in st.session_state:
        st.session_state["pre_consultores"] = pd.read_excel("main_bdd.xlsx", sheet_name="pre_consultores")

    # -------------------------------------------------------------------------
    # B) MENÚ PRINCIPAL (SIDEBAR)
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
    # 1. PÁGINA PRINCIPAL
    # -------------------------------------------------------------------------
    if eleccion_principal == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la Página Principal.")

    # -------------------------------------------------------------------------
    # 2. VPD
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD")
        sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", sub_vpd)

        sub_sub_vpd = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Tema:", sub_sub_vpd)

        # VPD > MISIONES
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Misiones > Requerimiento del Área")
                df_req_area = st.session_state["vpd_misiones"]

                # Value box “Suma del total”
                total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")

                st.dataframe(df_req_area)

            else:  # DPP 2025
                st.subheader("VPD > Misiones > DPP 2025")
                df_actual = st.session_state["vpd_misiones"].copy()
                df_actual = calcular_misiones(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 168000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_centralizado = 35960
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}")

                df_editado = st.data_editor(df_actual, use_container_width=True)
                df_final = calcular_misiones(df_editado)
                st.session_state["vpd_misiones"] = df_final

                # Resumen final
                st.write("**Resumen de totales**")
                if "total" in df_final.columns:
                    sum_final = df_final["total"].sum()
                else:
                    sum_final = 0
                st.write(f"Total final: {sum_final:,.2f}")

                if st.button("Guardar (vpd_misiones)"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_misiones", index=False)
                    st.success("¡Datos guardados en 'vpd_misiones'!")

        # VPD > CONSULTORÍAS
        else:
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Consultorías > Requerimiento del Área")
                df_req_area = st.session_state["vpd_consultores"]

                total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req_area)

            else:  # DPP 2025
                st.subheader("VPD > Consultorías > DPP 2025")
                df_actual = st.session_state["vpd_consultores"].copy()
                df_actual = calcular_consultores(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 130000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_centralizado = 193160
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}")

                df_editado = st.data_editor(df_actual, use_container_width=True)
                df_final = calcular_consultores(df_editado)
                st.session_state["vpd_consultores"] = df_final

                if st.button("Guardar (vpd_consultores)"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_consultores", index=False)
                    st.success("¡Guardado en 'vpd_consultores'!")


    # -------------------------------------------------------------------------
    # 3. VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")

        sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", sub_vpo)

        sub_sub_vpo = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", sub_sub_vpo)

        # VPO > MISIONES
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Misiones > Requerimiento del Área")
                df_req_area = st.session_state["vpo_misiones"]

                # Value box “Suma del total”
                total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")

                st.dataframe(df_req_area)

            else:  # DPP 2025
                st.subheader("VPO > Misiones > DPP 2025")
                df_actual = st.session_state["vpo_misiones"].copy()
                df_actual = calcular_misiones(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 434707
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_centralizado = 48158
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{(sum_total + gasto_centralizado):,.2f}")

                df_editado = st.data_editor(df_actual, use_container_width=True)
                df_final = calcular_misiones(df_editado)
                st.session_state["vpo_misiones"] = df_final

                # Resumen
                st.write("**Resumen de totales**")
                if "total" in df_final.columns:
                    sum_final = df_final["total"].sum()
                else:
                    sum_final = 0
                st.write(f"Total final: {sum_final:,.2f}")

                if st.button("Guardar (vpo_misiones)"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_misiones", index=False)
                    st.success("Guardado en 'vpo_misiones'.")

        # VPO > CONSULTORÍAS
        else:
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Consultorías > Requerimiento del Área")
                df_req_area = st.session_state["vpo_consultores"]

                total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req_area)

            else:
                st.subheader("VPO > Consultorías > DPP 2025")
                df_actual = st.session_state["vpo_consultores"].copy()
                df_actual = calcular_consultores(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 547700
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_centralizado = 33160
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{(sum_total + gasto_centralizado):,.2f}")

                df_editado = st.data_editor(df_actual, use_container_width=True)
                df_final = calcular_consultores(df_editado)
                st.session_state["vpo_consultores"] = df_final

                if st.button("Recalcular (vpo_consultores)"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_consultores", index=False)
                    st.success("Guardado en 'vpo_consultores'!")


    # -------------------------------------------------------------------------
    # 4. VPF
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
                df_req_area = st.session_state["vpf_misiones"]

                total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req_area)

            else:
                st.subheader("VPF > Misiones > DPP 2025")

                df_actual = st.session_state["vpf_misiones"].copy()
                df_actual = calcular_misiones(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 138600
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_centralizado = 40960
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{(sum_total + gasto_centralizado):,.2f}")

                df_editado = st.data_editor(df_actual, use_container_width=True)
                df_final = calcular_misiones(df_editado)
                st.session_state["vpf_misiones"] = df_final

                st.write("**Resumen de totales**")
                df_resumen = pd.DataFrame({
                    "Total Pasaje": [df_final["total_pasaje"].sum()],
                    "Total Alojamiento": [df_final["total_alojamiento"].sum()],
                    "Total Perdiem/Otros": [df_final["total_perdiem_otros"].sum()],
                    "Total Movilidad": [df_final["total_movilidad"].sum()],
                    "Total": [df_final["total"].sum()]
                })
                st.table(df_resumen.style.format("{:,.2f}"))

                if st.button("Recalcular (vpf_misiones)"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_misiones", index=False)
                    st.success("Guardado en 'vpf_misiones'!")

        # VPF > Consultorías
        else:
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Consultorías > Requerimiento del Área")
                df_req_area = st.session_state["vpf_consultores"]

                total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
                value_box("Suma del total", f"{total_sum:,.2f}")
                st.dataframe(df_req_area)
            else:
                st.subheader("VPF > Consultorías > DPP 2025")

                df_actual = st.session_state["vpf_consultores"].copy()
                df_actual = calcular_consultores(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 170000
                diferencia = monto_dpp - sum_total
                color_dif = "#fb8500" if diferencia != 0 else "green"
                gasto_centralizado = 88480
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", color_dif)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{(sum_total + gasto_centralizado):,.2f}")

                df_editado = st.data_editor(df_actual, use_container_width=True)
                df_final = calcular_consultores(df_editado)
                st.session_state["vpf_consultores"] = df_final

                if st.button("Recalcular (vpf_consultores)"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_consultores", index=False)
                    st.success("Guardado en 'vpf_consultores'!")


    # -------------------------------------------------------------------------
    # 7. VPE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")

        sub_vpe = ["Misiones", "Consultorías"]
        eleccion_vpe = st.sidebar.selectbox("Sub-sección de VPE:", sub_vpe)

        # Solo Requerimiento del Área
        sub_sub_vpe = ["Requerimiento del Área"]
        eleccion_sub_sub_vpe = st.sidebar.selectbox("Tema:", sub_sub_vpe)

        if eleccion_vpe == "Misiones":
            st.subheader("VPE > Misiones > Requerimiento del Área (Solo lectura)")
            df_req_area = st.session_state["vpe_misiones"]

            total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
            value_box("Suma del total", f"{total_sum:,.2f}")
            st.dataframe(df_req_area)

        else:  # "Consultorías"
            st.subheader("VPE > Consultorías > Requerimiento del Área (Solo lectura)")
            df_req_area = st.session_state["vpe_consultores"]

            total_sum = df_req_area["total"].sum() if "total" in df_req_area.columns else 0
            value_box("Suma del total", f"{total_sum:,.2f}")
            st.dataframe(df_req_area)

    # -------------------------------------------------------------------------
    # 8. PRE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "PRE":
        st.title("Sección PRE")

        menu_pre = [
            "Misiones Personal",
            "Misiones Consultores",
            "Consultorías",
            "Gastos Centralizados"
        ]
        eleccion_pre = st.sidebar.selectbox("Sub-sección de PRE:", menu_pre)

        if eleccion_pre == "Misiones Personal":
            st.subheader("PRE > Misiones Personal (Solo lectura)")
            df_pre_misiones_personal = st.session_state["pre_misiones_personal"]
            st.dataframe(df_pre_misiones_personal)

        elif eleccion_pre == "Misiones Consultores":
            st.subheader("PRE > Misiones Consultores (Solo lectura)")
            df_pre_misiones_consultores = st.session_state["pre_misiones_consultores"]
            st.dataframe(df_pre_misiones_consultores)

        elif eleccion_pre == "Consultorías":
            st.subheader("PRE > Consultorías (Solo lectura)")
            df_pre_consultores = st.session_state["pre_consultores"]
            st.dataframe(df_pre_consultores)

        else:  # "Gastos Centralizados"
            st.subheader("PRE > Gastos Centralizados")
            uploaded_file = st.file_uploader("Sube un archivo Excel con Gastos Centralizados", type=["xlsx", "xls"])
            if uploaded_file is not None:
                try:
                    df_gastos = pd.read_excel(uploaded_file)
                    st.write("Archivo subido exitosamente. Vista previa:")
                    st.dataframe(df_gastos)
                except Exception as e:
                    st.error(f"Ocurrió un error al leer el archivo: {e}")
            else:
                st.write("No se ha subido ningún archivo aún.")

    # -------------------------------------------------------------------------
    # 9. ACTUALIZACIÓN
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización")
        st.write("Aquí podrías incluir la lógica o formularios para actualizar datos en tu Excel.")

    # -------------------------------------------------------------------------
    # 10. CONSOLIDADO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")

        # CUADRO 9
        st.write("#### Gasto en personal 2024 Vs 2025")
        df_9 = st.session_state["cuadro_9"]
        st.table(two_decimals_only_numeric(df_9))
        st.caption("Cuadro 9 - DPP 2025")

        st.write("---")

        # CUADRO 10
        st.write("#### Análisis de Cambios en Gastos de Personal 2025 vs. 2024")
        df_10 = st.session_state["cuadro_10"]
        st.table(two_decimals_only_numeric(df_10))
        st.caption("Cuadro 10 - DPP 2025")

        st.write("---")

        # CUADRO 11
        st.write("#### Gastos Operativos propuestos para 2025 y montos aprobados para 2024")
        df_11 = st.session_state["cuadro_11"]
        st.table(two_decimals_only_numeric(df_11))
        st.caption("Cuadro 11 - DPP 2025")

        st.write("---")

        # CONSOLIDADO
        st.write("#### DPP 2025")
        df_cons = st.session_state["consolidado_df"]
        st.table(two_decimals_only_numeric(df_cons))


# =============================================================================
# EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    main()
