import streamlit as st
import pandas as pd

# Funciones de cálculo
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
    # Creamos las columnas base si no existen, para evitar errores
    for col in ["cant_funcionarios", "costo_pasaje", "dias",
                "alojamiento", "perdiem_otros", "movilidad"]:
        if col not in df_calc.columns:
            df_calc[col] = 0

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
    Para tablas de Consultorías:
      total = cantidad_funcionarios * cantidad_meses * monto_mensual
    """
    df_calc = df.copy()
    for col in ["cantidad_funcionarios", "cantidad_meses", "monto_mensual"]:
        if col not in df_calc.columns:
            df_calc[col] = 0

    df_calc["total"] = (
        df_calc["cantidad_funcionarios"]
        * df_calc["cantidad_meses"]
        * df_calc["monto_mensual"]
    )
    return df_calc

def main():
    st.set_page_config(page_title="Demo Recalculo en una sola tabla", layout="wide")

    # Lee tus DataFrames desde Excel
    df_vpd_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
    df_vpd_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")
    df_vpo_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
    df_vpo_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")
    df_vpf_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
    df_vpf_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")

    # Opcional: si tuvieras VPE, también lo leerías aquí

    # Menú principal
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

    if eleccion_principal == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la página principal.")

    elif eleccion_principal == "VPD":
        st.title("Sección VPD")
        menu_sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Sub-sección de VPD:", menu_sub_vpd)

        # “Requerimiento de Personal” (solo lectura) o “DPP 2025” (editable con fórmulas)
        menu_sub_sub_vpd = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpd)

        # ----------------- VPD > MISIONES -----------------
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                # Solo lectura
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.dataframe(df_vpd_misiones)
            else:
                # Editable con las fórmulas en una sola tabla
                st.subheader("VPD > Misiones > DPP 2025")
                st.write("Edita los valores y las columnas 'total_*' se recalculan en la misma tabla.")

                # 1) Recalcular antes de mostrar (por si había datos por defecto)
                df_vpd_misiones_calc = calcular_misiones(df_vpd_misiones)

                # 2) Mostrar en data_editor:
                #    - Las columnas calculadas las marcamos como deshabilitadas, para que no sean editables
                edited_misiones = st.data_editor(
                    df_vpd_misiones_calc,
                    use_container_width=True,
                    column_config={
                        "total_pasaje": st.column_config.NumberColumn(
                            "Total Pasaje", disabled=True
                        ),
                        "total_alojamiento": st.column_config.NumberColumn(
                            "Total Alojamiento", disabled=True
                        ),
                        "total_perdiem_otros": st.column_config.NumberColumn(
                            "Total Perdiem/Otros", disabled=True
                        ),
                        "total_movilidad": st.column_config.NumberColumn(
                            "Total Movilidad", disabled=True
                        ),
                        "total": st.column_config.NumberColumn(
                            "Total", disabled=True
                        ),
                    },
                    key="vpd_misiones_dpp2025"
                )

                # 3) Volver a recalcular en base a los cambios del usuario
                recalculated_misiones = calcular_misiones(edited_misiones)

                # 4) Mostrar la tabla final (en la misma sección) para que el usuario vea los valores actualizados
                st.write("Tabla con las fórmulas actualizadas:")
                st.data_editor(
                    recalculated_misiones,
                    use_container_width=True,
                    disabled=True,  # Aquí si deseas que ya no se siga editando.
                    key="vpd_misiones_resultado"
                )

        # ----------------- VPD > CONSULTORÍAS -----------------
        else:  # "Consultorías"
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Consultorías > Requerimiento de Personal")
                st.dataframe(df_vpd_consultores)
            else:
                st.subheader("VPD > Consultorías > DPP 2025")
                st.write("Edita los valores y la columna 'total' se recalcula en la misma tabla.")

                df_vpd_consultores_calc = calcular_consultores(df_vpd_consultores)
                edited_consultores = st.data_editor(
                    df_vpd_consultores_calc,
                    use_container_width=True,
                    column_config={
                        "total": st.column_config.NumberColumn("Total", disabled=True),
                    },
                    key="vpd_consultores_dpp2025"
                )

                recalculated_consultores = calcular_consultores(edited_consultores)

                st.write("Tabla con las fórmulas actualizadas:")
                st.data_editor(
                    recalculated_consultores,
                    use_container_width=True,
                    disabled=True,
                    key="vpd_consultores_resultado"
                )

    elif eleccion_principal == "VPO":
        st.title("Sección VPO")
        menu_sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Sub-sección de VPO:", menu_sub_vpo)

        menu_sub_sub_vpo = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Tema:", menu_sub_sub_vpo)

        # ----------------- VPO > MISIONES -----------------
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Misiones > Requerimiento de Personal")
                st.dataframe(df_vpo_misiones)
            else:
                st.subheader("VPO > Misiones > DPP 2025")
                st.write("Tabla única con columnas base editables y totales recalculados.")

                df_vpo_misiones_calc = calcular_misiones(df_vpo_misiones)
                edited_misiones = st.data_editor(
                    df_vpo_misiones_calc,
                    use_container_width=True,
                    column_config={
                        "total_pasaje": st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad": st.column_config.NumberColumn(disabled=True),
                        "total": st.column_config.NumberColumn(disabled=True),
                    },
                    key="vpo_misiones_dpp2025"
                )
                recalculated_misiones = calcular_misiones(edited_misiones)
                st.data_editor(
                    recalculated_misiones,
                    use_container_width=True,
                    disabled=True,
                    key="vpo_misiones_resultado"
                )

        # ----------------- VPO > CONSULTORÍAS -----------------
        else:  # "Consultorías"
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Consultorías > Requerimiento de Personal")
                st.dataframe(df_vpo_consultores)
            else:
                st.subheader("VPO > Consultorías > DPP 2025")
                df_vpo_consultores_calc = calcular_consultores(df_vpo_consultores)
                edited_consultores = st.data_editor(
                    df_vpo_consultores_calc,
                    use_container_width=True,
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    },
                    key="vpo_consultores_dpp2025"
                )
                recalculated_consultores = calcular_consultores(edited_consultores)
                st.data_editor(
                    recalculated_consultores,
                    use_container_width=True,
                    disabled=True,
                    key="vpo_consultores_resultado"
                )

    elif eleccion_principal == "VPF":
        st.title("Sección VPF")
        menu_sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Sub-sección de VPF:", menu_sub_vpf)

        menu_sub_sub_vpf = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Tema:", menu_sub_sub_vpf)

        # ----------------- VPF > MISIONES -----------------
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Misiones > Requerimiento de Personal")
                st.dataframe(df_vpf_misiones)
            else:
                st.subheader("VPF > Misiones > DPP 2025")
                df_vpf_misiones_calc = calcular_misiones(df_vpf_misiones)
                edited_misiones = st.data_editor(
                    df_vpf_misiones_calc,
                    use_container_width=True,
                    column_config={
                        "total_pasaje": st.column_config.NumberColumn(disabled=True),
                        "total_alojamiento": st.column_config.NumberColumn(disabled=True),
                        "total_perdiem_otros": st.column_config.NumberColumn(disabled=True),
                        "total_movilidad": st.column_config.NumberColumn(disabled=True),
                        "total": st.column_config.NumberColumn(disabled=True),
                    },
                    key="vpf_misiones_dpp2025"
                )
                recalculated_misiones = calcular_misiones(edited_misiones)
                st.data_editor(
                    recalculated_misiones,
                    use_container_width=True,
                    disabled=True,
                    key="vpf_misiones_resultado"
                )

        # ----------------- VPF > CONSULTORÍAS -----------------
        else:
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Consultorías > Requerimiento de Personal")
                st.dataframe(df_vpf_consultores)
            else:
                st.subheader("VPF > Consultorías > DPP 2025")
                df_vpf_consultores_calc = calcular_consultores(df_vpf_consultores)
                edited_consultores = st.data_editor(
                    df_vpf_consultores_calc,
                    use_container_width=True,
                    column_config={
                        "total": st.column_config.NumberColumn(disabled=True)
                    },
                    key="vpf_consultores_dpp2025"
                )
                recalculated_consultores = calcular_consultores(edited_consultores)
                st.data_editor(
                    recalculated_consultores,
                    use_container_width=True,
                    disabled=True,
                    key="vpf_consultores_resultado"
                )

    elif eleccion_principal == "VPE":
        st.title("Sección VPE")
        st.write("Aquí podrías agregar tu lógica de lectura/edición si tuvieras las hojas correspondientes para VPE.")

    elif eleccion_principal == "Actualización":
        st.title("Actualización")
        st.write("Aquí podrías colocar la lógica para actualizar datos en el Excel, etc.")

    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")
        st.write("Vista general de todo el contenido.")

if __name__ == "__main__":
    main()
