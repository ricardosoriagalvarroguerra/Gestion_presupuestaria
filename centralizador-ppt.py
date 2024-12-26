import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# FUNCIONES DE CÁLCULO
# -----------------------------------------------------------------------------
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
    # Aseguramos columnas base para evitar errores:
    base_cols = ["cant_funcionarios", "costo_pasaje", "dias", "alojamiento", "perdiem_otros", "movilidad"]
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

# -----------------------------------------------------------------------------
# APLICACIÓN PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Streamlit Cálculos en 1 sola tabla", layout="wide")

    # 1) Menú principal
    st.sidebar.title("Navegación")
    opciones = ["Página Principal", "Ejemplo VPD Misiones DPP 2025", "Ejemplo VPD Consultorías DPP 2025"]
    seleccion = st.sidebar.selectbox("Ir a:", opciones)

    # 2) Página Principal
    if seleccion == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido. Selecciona en la barra lateral el ejemplo que desees revisar.")
        return

    # -------------------------------------------------------------------------
    # LECTURA DE EXCEL SOLO UNA VEZ (o cuando no está en session_state)
    # -------------------------------------------------------------------------
    if "df_vpd_misiones" not in st.session_state:
        # Leemos la hoja y guardamos en session_state
        df_vpd_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
        st.session_state["df_vpd_misiones"] = df_vpd_misiones.copy()

    if "df_vpd_consultores" not in st.session_state:
        df_vpd_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")
        st.session_state["df_vpd_consultores"] = df_vpd_consultores.copy()

    # -------------------------------------------------------------------------
    # 3) EJEMPLO: VPD > MISIONES > DPP 2025
    # -------------------------------------------------------------------------
    if seleccion == "Ejemplo VPD Misiones DPP 2025":
        st.title("VPD > Misiones > DPP 2025")
        st.write("**Aquí puedes editar valores base y se recalcularán las columnas de fórmula en la misma tabla.**")

        # a) Tomamos el DF de session_state (versión actual, con cambios anteriores si los hubo)
        df_base = st.session_state["df_vpd_misiones"].copy()
        
        # b) Mostramos la tabla en data_editor. Ojo, las columnas calculadas se deshabilitan
        df_editado = st.data_editor(
            df_base,
            use_container_width=True,
            key="vpd_misiones_editor",
            column_config={
                "total_pasaje":      st.column_config.NumberColumn("Total Pasaje", disabled=True),
                "total_alojamiento": st.column_config.NumberColumn("Total Alojamiento", disabled=True),
                "total_perdiem_otros": st.column_config.NumberColumn("Total PerDiem/Otros", disabled=True),
                "total_movilidad":   st.column_config.NumberColumn("Total Movilidad", disabled=True),
                "total":             st.column_config.NumberColumn("Total", disabled=True),
            }
        )

        # c) Luego de la edición, recalculamos las columnas con fórmulas
        df_calculado = calcular_misiones(df_editado)

        # d) Guardamos el DF recalculado en session_state, para que la próxima recarga ya tenga esos valores
        st.session_state["df_vpd_misiones"] = df_calculado

        # e) Botón opcional para guardar en Excel:
        if st.button("Guardar cambios en Excel"):
            df_final = st.session_state["df_vpd_misiones"]
            df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_misiones", index=False)
            st.success("¡Datos guardados en la hoja vpd_misiones del main_bdd.xlsx!")

    # -------------------------------------------------------------------------
    # 4) EJEMPLO: VPD > CONSULTORÍAS > DPP 2025
    # -------------------------------------------------------------------------
    elif seleccion == "Ejemplo VPD Consultorías DPP 2025":
        st.title("VPD > Consultorías > DPP 2025")
        st.write("**Aquí puedes editar valores base y la columna 'total' se recalcula en la misma tabla.**")

        df_base = st.session_state["df_vpd_consultores"].copy()

        df_editado = st.data_editor(
            df_base,
            use_container_width=True,
            key="vpd_consultores_editor",
            column_config={
                "total": st.column_config.NumberColumn("Total", disabled=True)
            }
        )
        df_calculado = calcular_consultores(df_editado)
        st.session_state["df_vpd_consultores"] = df_calculado

        if st.button("Guardar cambios en Excel"):
            df_final = st.session_state["df_vpd_consultores"]
            df_final.to_excel("main_bdd.xlsx", sheet_name="vpd_consultores", index=False)
            st.success("¡Datos guardados en la hoja vpd_consultores del main_bdd.xlsx!")


if __name__ == "__main__":
    main()
