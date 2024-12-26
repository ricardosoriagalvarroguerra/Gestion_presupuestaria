import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# FUNCIONES DE CÁLCULO
# -----------------------------------------------------------------------------
def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Para las tablas de Misiones (DPP 2025):
      total_pasaje = cant_funcionarios * costo_pasaje
      total_alojamiento = dias * cant_funcionarios * alojamiento
      total_perdiem_otros = dias * cant_funcionarios * perdiem_otros
      total_movilidad = cant_funcionarios * movilidad
      total = suma de las anteriores
    """
    df_calc = df.copy()
    # Aseguramos las columnas base para evitar errores si no existen:
    cols_base = ["cant_funcionarios", "costo_pasaje", "dias", "alojamiento", "perdiem_otros", "movilidad"]
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
    Para las tablas de Consultorías (DPP 2025):
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

# -----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Aplicación multi-página", layout="wide")

    # -------------------------------------------------------------------------
    # LECTURA DE EXCEL
    # -------------------------------------------------------------------------
    # Nota: Si tu archivo no está en la misma carpeta, ajusta la ruta
    df_vpd_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
    df_vpd_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")

    df_vpo_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
    df_vpo_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")

    df_vpf_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
    df_vpf_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")

    # Si tuvieras hojas para VPE, podrías leerlas aquí:
    # df_vpe_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_misiones")
    # df_vpe_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_consultores")

    # -------------------------------------------------------------------------
    # GUARDADO EN SESSION_STATE
    # -------------------------------------------------------------------------
    # Inicializamos en session_state cada DF que usaremos en modo editable,
    # solo si todavía no existe (así no se reescribe en cada recarga).
    if "vpd_misiones" not in st.session_state:
        st.session_state["vpd_misiones"] = df_vpd_misiones.copy()
    if "vpd_consultores" not in st.session_state:
        st.session_state["vpd_consultores"] = df_vpd_consultores.copy()

    if "vpo_misiones" not in st.session_state:
        st.session_state["vpo_misiones"] = df_vpo_misiones.copy()
    if "vpo_consultores" not in st.session_state:
        st.session_state["vpo_consultores"] = df_vpo_consultores.copy()

    if "vpf_misiones" not in st.session_state:
        st.session_state["vpf_misiones"] = df_vpf_misiones.copy()
    if "vpf_consultores" not in st.session_state:
        st.session_state["vpf_consultores"] = df_vpf_consultores.copy()

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
        st.title("Página Principal")
        st.write("Bienvenido a la Página Principal. Aquí puedes colocar la información introductoria.")

    # -------------------------------------------------------------------------
    # 2. VPD
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        menu_sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", menu_sub_vpd)

        menu_sub_sub_vpd = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Tema:", menu_sub_sub_vpd)

        # ------------------- VPD > MISIONES -------------------
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                # Modo lectura
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpd_misiones"])
            else:
                # DPP 2025: una sola tabla con columnas base editables y columnas calculadas
                st.subheader("VPD > Misiones > DPP 2025")

                # 1) Tomamos DF de session_state
                df_temp = st.session_state["vpd_misiones"].copy()
                # 2) Recalculamos
                df_temp = calcular_misiones(df_temp)
                # 3) Mostramos en data_editor, deshabilitando columnas de fórmula
                df_editado = st.data_editor(
                    df_temp,
                    use_container_width=True,
                    key="vpd_misiones_dpp2025",
                    column_config={
                        "total_pasaje":      st.column_config.NumberColumn("Total Pasaje", disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn("Total Alojamiento", disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn("Total PerDiem/Otros", disabled=True),
                        "total_movilidad":   st.column_config.NumberColumn("Total Movilidad", disabled=True),
                        "total":             st.column_config.NumberColumn("TOTAL", disabled=True),
                    },
                )
                # 4) Guardamos en session_state para no perder los cambios
                st.session_state["vpd_misiones"] = df_editado

                # (Opcional) Botón para guardar en Excel
                if st.button("Guardar cambios en Excel (VPD Misiones)"):
                    df_final = calcular_misiones(st.session_state["vpd_misiones"])
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_misiones", index=False)
                    st.success("¡Datos guardados en la hoja vpd_misiones!")

        # ------------------- VPD > CONSULTORÍAS -------------------
        else:  # "Consultorías"
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpd_consultores"])
            else:
                st.subheader("VPD > Consultorías > DPP 2025")

                df_temp = st.session_state["vpd_consultores"].copy()
                df_temp = calcular_consultores(df_temp)
                df_editado = st.data_editor(
                    df_temp,
                    use_container_width=True,
                    key="vpd_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn("TOTAL", disabled=True),
                    }
                )
                st.session_state["vpd_consultores"] = df_editado

                if st.button("Guardar cambios en Excel (VPD Consultorías)"):
                    df_final = calcular_consultores(st.session_state["vpd_consultores"])
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_consultores", index=False)
                    st.success("¡Datos guardados en la hoja vpd_consultores!")

    # -------------------------------------------------------------------------
    # 3. VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        menu_sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", menu_sub_vpo)

        menu_sub_sub_vpo = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", menu_sub_sub_vpo)

        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpo_misiones"])
            else:
                st.subheader("VPO > Misiones > DPP 2025")

                df_temp = st.session_state["vpo_misiones"].copy()
                df_temp = calcular_misiones(df_temp)
                df_editado = st.data_editor(
                    df_temp,
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
                st.session_state["vpo_misiones"] = df_editado

                if st.button("Guardar cambios en Excel (VPO Misiones)"):
                    df_final = calcular_misiones(st.session_state["vpo_misiones"])
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_misiones", index=False)
                    st.success("¡Datos guardados en la hoja vpo_misiones!")

        else:  # "Consultorías"
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpo_consultores"])
            else:
                st.subheader("VPO > Consultorías > DPP 2025")

                df_temp = st.session_state["vpo_consultores"].copy()
                df_temp = calcular_consultores(df_temp)
                df_editado = st.data_editor(
                    df_temp,
                    use_container_width=True,
                    key="vpo_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                st.session_state["vpo_consultores"] = df_editado

                if st.button("Guardar cambios en Excel (VPO Consultorías)"):
                    df_final = calcular_consultores(st.session_state["vpo_consultores"])
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpo_consultores", index=False)
                    st.success("¡Datos guardados en la hoja vpo_consultores!")

    # -------------------------------------------------------------------------
    # 4. VPF
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        menu_sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Sub-sección de VPF:", menu_sub_vpf)

        menu_sub_sub_vpf = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Tema:", menu_sub_sub_vpf)

        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Misiones > Requerimiento de Personal")
                st.dataframe(st.session_state["vpf_misiones"])
            else:
                st.subheader("VPF > Misiones > DPP 2025")

                df_temp = st.session_state["vpf_misiones"].copy()
                df_temp = calcular_misiones(df_temp)
                df_editado = st.data_editor(
                    df_temp,
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
                st.session_state["vpf_misiones"] = df_editado

                if st.button("Guardar cambios en Excel (VPF Misiones)"):
                    df_final = calcular_misiones(st.session_state["vpf_misiones"])
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_misiones", index=False)
                    st.success("¡Datos guardados en la hoja vpf_misiones!")

        else:  # "Consultorías"
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Consultorías > Requerimiento de Personal")
                st.dataframe(st.session_state["vpf_consultores"])
            else:
                st.subheader("VPF > Consultorías > DPP 2025")

                df_temp = st.session_state["vpf_consultores"].copy()
                df_temp = calcular_consultores(df_temp)
                df_editado = st.data_editor(
                    df_temp,
                    use_container_width=True,
                    key="vpf_consultores_dpp2025",
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    }
                )
                st.session_state["vpf_consultores"] = df_editado

                if st.button("Guardar cambios en Excel (VPF Consultorías)"):
                    df_final = calcular_consultores(st.session_state["vpf_consultores"])
                    df_final.to_excel("main_bdd.xlsx", sheet_name="vpf_consultores", index=False)
                    st.success("¡Datos guardados en la hoja vpf_consultores!")

    # -------------------------------------------------------------------------
    # 5. VPE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")
        st.write("Aquí podrías incluir la lógica de lectura/edición de las hojas de VPE en tu Excel.")

    # -------------------------------------------------------------------------
    # 6. ACTUALIZACIÓN
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización")
        st.write("Aquí puedes incluir información o formularios para la actualización de datos.")

    # -------------------------------------------------------------------------
    # 7. CONSOLIDADO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")
        st.write("Aquí puedes mostrar la información consolidada de todas las secciones.")


# -----------------------------------------------------------------------------
# EJECUCIÓN DEL PROGRAMA
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
