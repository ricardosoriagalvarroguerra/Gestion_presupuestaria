import streamlit as st
import pandas as pd

# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================
def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    df_calc = df.copy()
    base_cols = ["cant_funcionarios", "costo_pasaje", "dias", 
                 "alojamiento", "perdiem_otros", "movilidad"]
    for col in base_cols:
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
# APLICACIÓN PRINCIPAL (VERSIÓN A: BOTÓN "RECALCULAR")
# =============================================================================
def main():
    st.set_page_config(page_title="App con Botón 'Recalcular'", layout="wide")

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
    # Si tuvieras VPE, replicarías aquí

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

        # VPD > MISIONES
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpd_misiones"])
            else:  # DPP 2025
                st.subheader("VPD > Misiones > DPP 2025 (Botón llamado 'Recalcular')")
                df_old = st.session_state["vpd_misiones"].copy()
                df_recalc = calcular_misiones(df_old)
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
                df_final = calcular_misiones(df_editado)
                st.session_state["vpd_misiones"] = df_final

                # Aquí, el botón se llama "Recalcular" pero sigue guardando en Excel
                if st.button("Recalcular"):
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_misiones", index=False)
                    st.success("¡Tabla recalculada y guardada en Excel!")

        # VPD > CONSULTORÍAS
        else:
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpd_consultores"])
            else:  # DPP 2025
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
        st.write("Podrías replicar la misma lógica con 'vpe_misiones' y 'vpe_consultores'.")

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

if __name__ == "__main__":
    main()
