import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="Aplicación multi-página", layout="wide")

    # -------------------------------------------------------------------------
    # LECTURA DE DATOS DESDE EXCEL
    # -------------------------------------------------------------------------
    df_vpd_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
    df_vpd_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")

    df_vpo_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
    df_vpo_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")

    df_vpf_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
    df_vpf_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")

    # Si tuvieras sheets para VPE, podrías leerlos aquí:
    # df_vpe_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_misiones")
    # df_vpe_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_consultores")

    # -------------------------------------------------------------------------
    # BARRA LATERAL - MENÚ PRINCIPAL
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
    # FUNCIONES AUXILIARES PARA CÁLCULO DE FÓRMULAS
    # -------------------------------------------------------------------------
    def calcular_misiones(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula las columnas derivadas para Misiones, en base a:
          total_pasaje = cant_funcionarios * costo_pasaje
          total_alojamiento = dias * cant_funcionarios * alojamiento
          total_perdiem_otros = dias * cant_funcionarios * perdiem_otros
          total_movilidad = cant_funcionarios * movilidad
          total = suma de las anteriores
        Devuelve un DataFrame con las columnas calculadas.
        """
        df_calc = df.copy()
        # Nos aseguramos de que las columnas existan antes de multiplicar
        columnas_base = ["cant_funcionarios", "costo_pasaje", "dias", "alojamiento",
                         "perdiem_otros", "movilidad"]
        for col in columnas_base:
            if col not in df_calc.columns:
                df_calc[col] = 0  # crea la columna si no existe

        df_calc["total_pasaje"] = df_calc["cant_funcionarios"] * df_calc["costo_pasaje"]
        df_calc["total_alojamiento"] = (
            df_calc["dias"] * df_calc["cant_funcionarios"] * df_calc["alojamiento"]
        )
        df_calc["total_perdiem_otros"] = (
            df_calc["dias"] * df_calc["cant_funcionarios"] * df_calc["perdiem_otros"]
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
        Para Consultorías en DPP 2025:
          total = cantidad_funcionarios * cantidad_meses * monto_mensual
        """
        df_calc = df.copy()
        # Verificamos que las columnas base existan
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

    # -------------------------------------------------------------------------
    # 1. PÁGINA PRINCIPAL
    # -------------------------------------------------------------------------
    if eleccion_principal == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la Página Principal. Aquí puedes colocar la información introductoria.")

    # -------------------------------------------------------------------------
    # 2. SECCIÓN VPD
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPD
        menu_sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Selecciona la sub-sección de VPD:", menu_sub_vpd)

        # Sub-subpáginas
        menu_sub_sub_vpd = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpd)

        # ---------------- VPD > MISIONES ----------------
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                # Tabla en modo lectura
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.dataframe(df_vpd_misiones)
            else:
                # Tabla editable + fórmulas
                st.subheader("VPD > Misiones > DPP 2025")
                st.write("**Edita los valores base y se recalcularán las columnas de Totales.**")

                # 1) Editor
                df_edit = st.data_editor(
                    df_vpd_misiones,
                    key="vpd_misiones_dpp2025_editor",
                    use_container_width=True
                )
                # 2) Cálculo de columnas
                df_calc = calcular_misiones(df_edit)
                # 3) Mostrar el resultado con totales recalculados
                st.write("**Resultado con columnas calculadas:**")
                st.dataframe(df_calc, use_container_width=True)

        # ---------------- VPD > CONSULTORÍAS ----------------
        else:  # "Consultorías"
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Consultorías > Requerimiento de Personal")
                st.dataframe(df_vpd_consultores)
            else:
                st.subheader("VPD > Consultorías > DPP 2025")
                st.write("**Edita los valores base y se recalculará la columna total.**")

                # 1) Editor
                df_edit = st.data_editor(
                    df_vpd_consultores,
                    key="vpd_consultores_dpp2025_editor",
                    use_container_width=True
                )
                # 2) Cálculo de columnas
                df_calc = calcular_consultores(df_edit)
                # 3) Mostrar el resultado
                st.write("**Resultado con columna total calculada:**")
                st.dataframe(df_calc, use_container_width=True)

    # -------------------------------------------------------------------------
    # 3. SECCIÓN VPO
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        menu_sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Selecciona la sub-sección de VPO:", menu_sub_vpo)

        menu_sub_sub_vpo = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpo)

        # ---------------- VPO > MISIONES ----------------
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Misiones > Requerimiento de Personal")
                st.dataframe(df_vpo_misiones)
            else:
                st.subheader("VPO > Misiones > DPP 2025")
                st.write("**Edita los valores base y se recalcularán las columnas de Totales.**")

                df_edit = st.data_editor(
                    df_vpo_misiones,
                    key="vpo_misiones_dpp2025_editor",
                    use_container_width=True
                )
                df_calc = calcular_misiones(df_edit)
                st.dataframe(df_calc, use_container_width=True)

        # ---------------- VPO > CONSULTORÍAS ----------------
        else:  # "Consultorías"
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Consultorías > Requerimiento de Personal")
                st.dataframe(df_vpo_consultores)
            else:
                st.subheader("VPO > Consultorías > DPP 2025")
                st.write("**Edita los valores base y se recalculará la columna total.**")

                df_edit = st.data_editor(
                    df_vpo_consultores,
                    key="vpo_consultores_dpp2025_editor",
                    use_container_width=True
                )
                df_calc = calcular_consultores(df_edit)
                st.dataframe(df_calc, use_container_width=True)

    # -------------------------------------------------------------------------
    # 4. SECCIÓN VPF
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        menu_sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Selecciona la sub-sección de VPF:", menu_sub_vpf)

        menu_sub_sub_vpf = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpf)

        # ---------------- VPF > MISIONES ----------------
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Misiones > Requerimiento de Personal")
                st.dataframe(df_vpf_misiones)
            else:
                st.subheader("VPF > Misiones > DPP 2025")
                st.write("**Edita los valores base y se recalcularán las columnas de Totales.**")

                df_edit = st.data_editor(
                    df_vpf_misiones,
                    key="vpf_misiones_dpp2025_editor",
                    use_container_width=True
                )
                df_calc = calcular_misiones(df_edit)
                st.dataframe(df_calc, use_container_width=True)

        # ---------------- VPF > CONSULTORÍAS ----------------
        else:  # "Consultorías"
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Consultorías > Requerimiento de Personal")
                st.dataframe(df_vpf_consultores)
            else:
                st.subheader("VPF > Consultorías > DPP 2025")
                st.write("**Edita los valores base y se recalculará la columna total.**")

                df_edit = st.data_editor(
                    df_vpf_consultores,
                    key="vpf_consultores_dpp2025_editor",
                    use_container_width=True
                )
                df_calc = calcular_consultores(df_edit)
                st.dataframe(df_calc, use_container_width=True)

    # -------------------------------------------------------------------------
    # 5. SECCIÓN VPE
    # -------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")
        st.write("Aquí podrías agregar la lógica de lectura/edición de tu Excel si tuvieras las hojas correspondientes para VPE.")
        # Podrías replicar exactamente la misma estructura de VPD, VPO y VPF
        # si en 'main_bdd.xlsx' tuvieras sheets como 'vpe_misiones' o 'vpe_consultores'.

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

# Punto de entrada
if __name__ == "__main__":
    main()
