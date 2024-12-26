import streamlit as st
import pandas as pd

# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================
def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Para tablas de Misiones:
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
    Para tablas de Consultorías:
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
# PEQUEÑA FUNCIÓN PARA CREAR "VALUE BOX" CON HTML
# =============================================================================
def value_box(label: str, value, bg_color: str = "#6c757d"):
    """
    Crea un 'cajón' de valor (value box) con un color de fondo y texto en blanco.
    - label: nombre o descripción de la métrica
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
# APLICACIÓN PRINCIPAL (VERSIÓN A: BOTÓN "RECALCULAR")
# =============================================================================
def main():
    st.set_page_config(page_title="App Versión A + Value Boxes", layout="wide")

    # -------------------------------------------------------------------------
    # LECTURA DE EXCEL SOLO SI NO ESTÁ EN SESSION_STATE
    # -------------------------------------------------------------------------
    if "vpd_misiones" not in st.session_state:
        df = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
        st.session_state["vpd_misiones"] = df.copy()
    if "vpd_consultores" not in st.session_state:
        df = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")
        st.session_state["vpd_consultores"] = df.copy()
    if "vpo_misiones" not in st.session_state:
        df = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
        st.session_state["vpo_misiones"] = df.copy()
    if "vpo_consultores" not in st.session_state:
        df = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")
        st.session_state["vpo_consultores"] = df.copy()
    if "vpf_misiones" not in st.session_state:
        df = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
        st.session_state["vpf_misiones"] = df.copy()
    if "vpf_consultores" not in st.session_state:
        df = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")
        st.session_state["vpf_consultores"] = df.copy()
    # Si tuvieras VPE, lo añades de forma similar

    # -------------------------------------------------------------------------
    # MENÚ PRINCIPAL
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
        st.write("Bienvenido a la Página Principal. Aquí puedes colocar la información introductoria.")

    # -------------------------------------------------------------------------
    # 2. VPD
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD (Versión A)")
        menu_sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", menu_sub_vpd)

        menu_sub_sub_vpd = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Tema:", menu_sub_sub_vpd)

        # =================== VPD > MISIONES ===================
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpd_misiones"])

            else:  # DPP 2025
                st.subheader("VPD > Misiones > DPP 2025 (Botón llamado 'Recalcular')")

                # 1) Tomamos el DF previo en session_state
                df_old = st.session_state["vpd_misiones"].copy()
                # 2) Lo recalculamos para que parta con fórmulas actualizadas
                df_recalc = calcular_misiones(df_old)
                # 3) Lo mostramos en data_editor
                df_editado = st.data_editor(
                    df_recalc,
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
                # 4) Volvemos a recalcular (el usuario pudo cambiar columnas base)
                df_final = calcular_misiones(df_editado)
                # 5) Guardamos en session_state
                st.session_state["vpd_misiones"] = df_final

                # -----------------------------------------------------------------
                # BLOQUE DE VALUE BOXES
                # -----------------------------------------------------------------
                #  Suma del total
                sum_total = df_final["total"].sum() if "total" in df_final.columns else 0
                #  Monto DPP 2025
                monto_dpp = 168000
                #  Diferencia (color #fb8500 por defecto, verde si es 0)
                diferencia = monto_dpp - sum_total
                diff_color = "#fb8500"
                if diferencia == 0:
                    diff_color = "green"
                #  Gasto Centralizado
                gasto_centralizado = 35960
                #  Total + Gasto Centralizado
                total_gasto_central = sum_total + gasto_centralizado

                # Usamos columns para alinear estos value boxes en la misma fila:
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

                # -----------------------------------------------------------------
                # BOTÓN renombrado a "Recalcular", PERO REALMENTE GUARDA EN EXCEL
                # -----------------------------------------------------------------
                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_misiones", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

        # =================== VPD > CONSULTORÍAS ===================
        else:  # "Consultorías"
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpd_consultores"])
            else:
                st.subheader("VPD > Consultorías > DPP 2025 (Botón 'Recalcular')")
                df_old = st.session_state["vpd_consultores"].copy()
                df_recalc = calcular_consultores(df_old)
                df_editado = st.data_editor(
                    df_recalc,
                    use_container_width=True,
                    key="vpd_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)
                st.session_state["vpd_consultores"] = df_final

                # (En este ejemplo, solo pediste value boxes para “VPD > Misiones > DPP 2025”,
                #  pero podrías replicarlos aquí si deseas.)

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_consultores", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

    # -------------------------------------------------------------------------
    # 3. VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO (Versión A)")
        menu_sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", menu_sub_vpo)

        menu_sub_sub_vpo = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", menu_sub_sub_vpo)

        # VPO > MISIONES
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpo_misiones"])
            else:
                st.subheader("VPO > Misiones > DPP 2025 (Botón 'Recalcular')")
                df_old = st.session_state["vpo_misiones"].copy()
                df_recalc = calcular_misiones(df_old)
                df_editado = st.data_editor(
                    df_recalc,
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

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_misiones", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

        # VPO > CONSULTORÍAS
        else:
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpo_consultores"])
            else:
                st.subheader("VPO > Consultorías > DPP 2025 (Botón 'Recalcular')")
                df_old = st.session_state["vpo_consultores"].copy()
                df_recalc = calcular_consultores(df_old)
                df_editado = st.data_editor(
                    df_recalc,
                    use_container_width=True,
                    key="vpo_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)
                st.session_state["vpo_consultores"] = df_final

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_consultores", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

    # -------------------------------------------------------------------------
    # 4. VPF
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF (Versión A)")
        menu_sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Sub-sección de VPF:", menu_sub_vpf)

        menu_sub_sub_vpf = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Tema:", menu_sub_sub_vpf)

        # VPF > MISIONES
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpf_misiones"])
            else:
                st.subheader("VPF > Misiones > DPP 2025 (Botón 'Recalcular')")
                df_old = st.session_state["vpf_misiones"].copy()
                df_recalc = calcular_misiones(df_old)
                df_editado = st.data_editor(
                    df_recalc,
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

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_misiones", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

        # VPF > CONSULTORÍAS
        else:
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpf_consultores"])
            else:
                st.subheader("VPF > Consultorías > DPP 2025 (Botón 'Recalcular')")
                df_old = st.session_state["vpf_consultores"].copy()
                df_recalc = calcular_consultores(df_old)
                df_editado = st.data_editor(
                    df_recalc,
                    use_container_width=True,
                    key="vpf_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                df_final = calcular_consultores(df_editado)
                st.session_state["vpf_consultores"] = df_final

                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_consultores", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

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
        st.write("Aquí puedes implementar lógica adicional para actualizar datos.")

    # -------------------------------------------------------------------------
    # 7. CONSOLIDADO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado (Versión A)")
        st.write("Aquí puedes mostrar la información consolidada.")

# -----------------------------------------------------------------------------
# EJECUCIÓN DE LA APP
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
