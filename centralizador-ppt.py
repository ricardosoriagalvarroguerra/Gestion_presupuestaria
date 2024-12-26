import streamlit as st
import pandas as pd

# =============================================================================
# FUNCIONES DE CÁLCULO
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
    base_cols = ["cant_funcionarios", "costo_pasaje", "dias",
                 "alojamiento", "perdiem_otros", "movilidad"]
    for col in base_cols:
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
    Para tablas de Consultorías (DPP 2025):
      total = cantidad_funcionarios * cantidad_meses * monto_mensual
    """
    df_calc = df.copy()
    base_cols = ["cantidad_funcionarios", "cantidad_meses", "monto_mensual"]
    for col in base_cols:
        if col not in df_calc.columns:
            df_calc[col] = 0

    df_calc["total"] = (
        df_calc["cantidad_funcionarios"]
        * df_calc["cantidad_meses"]
        * df_calc["monto_mensual"]
    )
    return df_calc

# =============================================================================
# FUNCIÓN PARA MOSTRAR "VALUE BOX" (HTML/CSS)
# =============================================================================
def value_box(label: str, value, bg_color: str = "#6c757d"):
    """
    Genera un recuadro (value box) con fondo de color y texto en blanco.
    - label: texto descriptivo
    - value: valor a mostrar
    - bg_color: color de fondo (ej. "#fb8500" o "green")
    """
    st.markdown(f"""
    <div style="display:inline-block; background-color:{bg_color}; 
                padding:10px; margin:5px; border-radius:5px; color:white; font-weight:bold;">
        <div style="font-size:14px;">{label}</div>
        <div style="font-size:20px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# APLICACIÓN PRINCIPAL (Versión A: Botón "Recalcular" = Guardar en Excel)
# =============================================================================
def main():
    st.set_page_config(page_title="Versión A (Requerimiento del Área)", layout="wide")

    # -------------------------------------------------------------------------
    # LECTURA DE EXCEL (SOLO UNA VEZ, GUARDADO EN session_state)
    # -------------------------------------------------------------------------
    if "vpd_misiones" not in st.session_state:
        df_vpd_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
        st.session_state["vpd_misiones"] = df_vpd_misiones.copy()

    if "vpd_consultores" not in st.session_state:
        df_vpd_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")
        st.session_state["vpd_consultores"] = df_vpd_consultores.copy()

    if "vpo_misiones" not in st.session_state:
        df_vpo_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
        st.session_state["vpo_misiones"] = df_vpo_misiones.copy()

    if "vpo_consultores" not in st.session_state:
        df_vpo_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")
        st.session_state["vpo_consultores"] = df_vpo_consultores.copy()

    if "vpf_misiones" not in st.session_state:
        df_vpf_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
        st.session_state["vpf_misiones"] = df_vpf_misiones.copy()

    if "vpf_consultores" not in st.session_state:
        df_vpf_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")
        st.session_state["vpf_consultores"] = df_vpf_consultores.copy()

    # Si tuvieras VPE, harías algo similar:
    # if "vpe_misiones" not in st.session_state:
    #     ...
    # if "vpe_consultores" not in st.session_state:
    #     ...

    # -------------------------------------------------------------------------
    # MENÚ PRINCIPAL (SIDEBAR)
    # -------------------------------------------------------------------------
    st.sidebar.title("Navegación principal")
    menu_principal = [
        "Página Principal",
        "VPD",
        "VPO",
        "VPF",
        "VPE",
        "Actualización",
        "Consolidado"
    ]
    eleccion_principal = st.sidebar.selectbox("Selecciona una sección:", menu_principal)

    # -------------------------------------------------------------------------
    # 1. PÁGINA PRINCIPAL
    # -------------------------------------------------------------------------
    if eleccion_principal == "Página Principal":
        st.title("Página Principal (Versión A)")
        st.write("Bienvenido a la Página Principal.")

    # -------------------------------------------------------------------------
    # 2. VPD
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD (Versión A)")
        sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", sub_vpd)

        sub_sub_vpd = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Tema:", sub_sub_vpd)

        # =================== VPD > MISIONES ===================
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Misiones > Requerimiento del Área (Solo lectura)")
                st.dataframe(st.session_state["vpd_misiones"])

            else:  # DPP 2025
                st.subheader("VPD > Misiones > DPP 2025 (Botón 'Recalcular')")

                df_actual = st.session_state["vpd_misiones"].copy()
                df_actual = calcular_misiones(df_actual)

                # Value boxes
                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 168000
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"

                gasto_centralizado = 35960
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}", "#6c757d")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}", "#6c757d")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", diff_color)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}", "#6c757d")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}", "#6c757d")

                st.write("")
                st.write("")

                df_editado = st.data_editor(
                    df_actual,
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
                st.session_state["vpd_misiones"] = df_final

                # Tabla de resumen de totales (solo para Misiones DPP 2025)
                st.write("**Resumen de totales**")
                df_resumen = pd.DataFrame({
                    "Total Pasaje": [df_final["total_pasaje"].sum()],
                    "Total Alojamiento": [df_final["total_alojamiento"].sum()],
                    "Total Perdiem/Otros": [df_final["total_perdiem_otros"].sum()],
                    "Total Movilidad": [df_final["total_movilidad"].sum()],
                    "Total": [df_final["total"].sum()]
                })
                st.table(df_resumen.style.format("{:,.2f}"))

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_misiones", index=False)
                    st.success("¡Recalculado y guardado en 'vpd_misiones'!")

        # =================== VPD > CONSULTORÍAS ===================
        else:
            if eleccion_sub_sub_vpd == "Requerimiento del Área":
                st.subheader("VPD > Consultorías > Requerimiento del Área (Solo lectura)")
                st.dataframe(st.session_state["vpd_consultores"])
            else:
                st.subheader("VPD > Consultorías > DPP 2025 (Botón 'Recalcular')")
                df_actual = st.session_state["vpd_consultores"].copy()
                df_actual = calcular_consultores(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 130000
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"

                gasto_centralizado = 193160
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}", "#6c757d")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}", "#6c757d")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", diff_color)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}", "#6c757d")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}", "#6c757d")

                st.write("")
                st.write("")

                df_editado = st.data_editor(
                    df_actual,
                    use_container_width=True,
                    key="vpd_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                st.session_state["vpd_consultores"] = df_editado

                # (En Consultorías no se solicitó tabla de resumen, 
                #  pero puedes agregarla si lo deseas.)

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_consultores", index=False)
                    st.success("¡Recalculado y guardado en 'vpd_consultores'!")

    # -------------------------------------------------------------------------
    # 3. VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO (Versión A)")
        menu_sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", menu_sub_vpo)

        sub_sub_vpo = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", sub_sub_vpo)

        # =================== VPO > MISIONES ===================
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Misiones > Requerimiento del Área (Solo lectura)")
                st.dataframe(st.session_state["vpo_misiones"])

            else:  # DPP 2025
                st.subheader("VPO > Misiones > DPP 2025 (Botón 'Recalcular')")

                df_actual = st.session_state["vpo_misiones"].copy()
                df_actual = calcular_misiones(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 434707
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"

                gasto_centralizado = 48158
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}", "#6c757d")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}", "#6c757d")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", diff_color)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}", "#6c757d")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}", "#6c757d")

                st.write("")
                st.write("")

                df_editado = st.data_editor(
                    df_actual,
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
                st.session_state["vpo_misiones"] = df_final

                # Tabla de resumen
                st.write("**Resumen de totales**")
                df_resumen = pd.DataFrame({
                    "Total Pasaje": [df_final["total_pasaje"].sum()],
                    "Total Alojamiento": [df_final["total_alojamiento"].sum()],
                    "Total Perdiem/Otros": [df_final["total_perdiem_otros"].sum()],
                    "Total Movilidad": [df_final["total_movilidad"].sum()],
                    "Total": [df_final["total"].sum()]
                })
                st.table(df_resumen.style.format("{:,.2f}"))

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_misiones", index=False)
                    st.success("¡Recalculado y guardado en 'vpo_misiones'!")

        # =================== VPO > CONSULTORÍAS ===================
        else:
            if eleccion_sub_sub_vpo == "Requerimiento del Área":
                st.subheader("VPO > Consultorías > Requerimiento del Área (Solo lectura)")
                st.dataframe(st.session_state["vpo_consultores"])
            else:
                st.subheader("VPO > Consultorías > DPP 2025 (Botón 'Recalcular')")
                df_actual = st.session_state["vpo_consultores"].copy()
                df_actual = calcular_consultores(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 547700
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"

                gasto_centralizado = 33160
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}", "#6c757d")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}", "#6c757d")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", diff_color)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}", "#6c757d")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}", "#6c757d")

                st.write("")
                st.write("")

                df_editado = st.data_editor(
                    df_actual,
                    use_container_width=True,
                    key="vpo_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)
                st.session_state["vpo_consultores"] = df_final

                # (En Consultorías no se solicitó tabla de resumen, 
                #  pero puedes añadirla si lo deseas.)

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_consultores", index=False)
                    st.success("¡Recalculado y guardado en 'vpo_consultores'!")

    # -------------------------------------------------------------------------
    # 4. VPF
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF (Versión A)")
        menu_sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Sub-sección de VPF:", menu_sub_vpf)

        sub_sub_vpf = ["Requerimiento del Área", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Tema:", sub_sub_vpf)

        # =================== VPF > MISIONES ===================
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Misiones > Requerimiento del Área (Solo lectura)")
                st.dataframe(st.session_state["vpf_misiones"])

            else:  # DPP 2025
                st.subheader("VPF > Misiones > DPP 2025 (Botón 'Recalcular')")

                df_actual = st.session_state["vpf_misiones"].copy()
                df_actual = calcular_misiones(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 138600
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"

                gasto_centralizado = 40960
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}", "#6c757d")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}", "#6c757d")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", diff_color)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}", "#6c757d")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}", "#6c757d")

                st.write("")
                st.write("")

                df_editado = st.data_editor(
                    df_actual,
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
                st.session_state["vpf_misiones"] = df_final

                # Tabla de resumen
                st.write("**Resumen de totales**")
                df_resumen = pd.DataFrame({
                    "Total Pasaje": [df_final["total_pasaje"].sum()],
                    "Total Alojamiento": [df_final["total_alojamiento"].sum()],
                    "Total Perdiem/Otros": [df_final["total_perdiem_otros"].sum()],
                    "Total Movilidad": [df_final["total_movilidad"].sum()],
                    "Total": [df_final["total"].sum()]
                })
                st.table(df_resumen.style.format("{:,.2f}"))

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_misiones", index=False)
                    st.success("¡Recalculado y guardado en 'vpf_misiones'!")

        # =================== VPF > CONSULTORÍAS ===================
        else:
            if eleccion_sub_sub_vpf == "Requerimiento del Área":
                st.subheader("VPF > Consultorías > Requerimiento del Área (Solo lectura)")
                st.dataframe(st.session_state["vpf_consultores"])
            else:
                st.subheader("VPF > Consultorías > DPP 2025 (Botón 'Recalcular')")
                df_actual = st.session_state["vpf_consultores"].copy()
                df_actual = calcular_consultores(df_actual)

                sum_total = df_actual["total"].sum() if "total" in df_actual.columns else 0
                monto_dpp = 170000
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"

                gasto_centralizado = 88480
                total_gasto_central = sum_total + gasto_centralizado

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    value_box("Suma del total", f"{sum_total:,.2f}", "#6c757d")
                with col2:
                    value_box("Monto DPP 2025", f"{monto_dpp:,.2f}", "#6c757d")
                with col3:
                    value_box("Diferencia", f"{diferencia:,.2f}", diff_color)
                with col4:
                    value_box("Gasto Centralizado", f"{gasto_centralizado:,.2f}", "#6c757d")
                with col5:
                    value_box("Total + Gasto Centralizado", f"{total_gasto_central:,.2f}", "#6c757d")

                st.write("")
                st.write("")

                df_editado = st.data_editor(
                    df_actual,
                    use_container_width=True,
                    key="vpf_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                st.session_state["vpf_consultores"] = df_editado

                # (En Consultorías no se solicitó tabla de resumen, 
                #  pero puedes añadirla si lo deseas.)

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_consultores", index=False)
                    st.success("¡Recalculado y guardado en 'vpf_consultores'!")

    # -------------------------------------------------------------------------
    # 5. VPE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE (Versión A)")
        st.write("Podrías replicar la misma lógica con 'vpe_misiones' y 'vpe_consultores' si tuvieras esas hojas.")

    # -------------------------------------------------------------------------
    # 6. ACTUALIZACIÓN
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización (Versión A)")
        st.write("Aquí podrías implementar lógica adicional para actualizar datos en tu Excel.")

    # -------------------------------------------------------------------------
    # 7. CONSOLIDADO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado (Versión A)")
        st.write("Aquí podrías mostrar un resumen global de todos los datos.")


# -----------------------------------------------------------------------------
# EJECUCIÓN DE LA APLICACIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
