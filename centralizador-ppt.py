import streamlit as st
import pandas as pd

def main():
    # Configuración de la página
    st.set_page_config(page_title="Aplicación multi-página", layout="wide")

    # Lectura de la BDD (main_bdd.xlsx) y cada hoja relevante
    df_vpd_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_misiones")
    df_vpd_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpd_consultores")

    df_vpo_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_misiones")
    df_vpo_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpo_consultores")

    df_vpf_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_misiones")
    df_vpf_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpf_consultores")

    # --------------------------------------------------------------------------------
    # Barra lateral para la navegación principal
    # --------------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------------
    # 1. Página Principal
    # --------------------------------------------------------------------------------
    if eleccion_principal == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la Página Principal. Aquí puedes colocar la información introductoria.")

    # --------------------------------------------------------------------------------
    # 2. VPD
    # --------------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPD (Misiones, Consultorías)
        menu_sub_vpd = ["Misiones", "Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Selecciona la sub-sección de VPD:", menu_sub_vpd)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpd = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpd)

        # ----- VPD > Misiones -----
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.write("**Tabla (solo lectura) - Hoja: vpd_misiones**")
                st.dataframe(df_vpd_misiones)  # Tabla en modo lectura
            else:
                st.subheader("VPD > Misiones > DPP 2025")
                st.write("**Tabla editable - Hoja: vpd_misiones**")
                edited_vpd_misiones = st.data_editor(df_vpd_misiones)
                # Aquí podrías agregar la lógica para guardar los cambios si lo deseas

        # ----- VPD > Consultorías -----
        else:  # Consultorías
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Consultorías > Requerimiento de Personal")
                st.write("**Tabla (solo lectura) - Hoja: vpd_consultores**")
                st.dataframe(df_vpd_consultores)
            else:
                st.subheader("VPD > Consultorías > DPP 2025")
                st.write("**Tabla editable - Hoja: vpd_consultores**")
                edited_vpd_consultores = st.data_editor(df_vpd_consultores)
                # Aquí podrías agregar la lógica para guardar los cambios si lo deseas

    # --------------------------------------------------------------------------------
    # 3. VPO
    # --------------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPO (Misiones, Consultorías)
        menu_sub_vpo = ["Misiones", "Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Selecciona la sub-sección de VPO:", menu_sub_vpo)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpo = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpo)

        # ----- VPO > Misiones -----
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Misiones > Requerimiento de Personal")
                st.write("**Tabla (solo lectura) - Hoja: vpo_misiones**")
                st.dataframe(df_vpo_misiones)
            else:
                st.subheader("VPO > Misiones > DPP 2025")
                st.write("**Tabla editable - Hoja: vpo_misiones**")
                edited_vpo_misiones = st.data_editor(df_vpo_misiones)
                # Lógica de guardado si se desea

        # ----- VPO > Consultorías -----
        else:  # Consultorías
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Consultorías > Requerimiento de Personal")
                st.write("**Tabla (solo lectura) - Hoja: vpo_consultores**")
                st.dataframe(df_vpo_consultores)
            else:
                st.subheader("VPO > Consultorías > DPP 2025")
                st.write("**Tabla editable - Hoja: vpo_consultores**")
                edited_vpo_consultores = st.data_editor(df_vpo_consultores)
                # Lógica de guardado si se desea

    # --------------------------------------------------------------------------------
    # 4. VPF
    # --------------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPF (Misiones, Consultorías)
        menu_sub_vpf = ["Misiones", "Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Selecciona la sub-sección de VPF:", menu_sub_vpf)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpf = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpf)

        # ----- VPF > Misiones -----
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Misiones > Requerimiento de Personal")
                st.write("**Tabla (solo lectura) - Hoja: vpf_misiones**")
                st.dataframe(df_vpf_misiones)
            else:
                st.subheader("VPF > Misiones > DPP 2025")
                st.write("**Tabla editable - Hoja: vpf_misiones**")
                edited_vpf_misiones = st.data_editor(df_vpf_misiones)

        # ----- VPF > Consultorías -----
        else:  # Consultorías
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Consultorías > Requerimiento de Personal")
                st.write("**Tabla (solo lectura) - Hoja: vpf_consultores**")
                st.dataframe(df_vpf_consultores)
            else:
                st.subheader("VPF > Consultorías > DPP 2025")
                st.write("**Tabla editable - Hoja: vpf_consultores**")
                edited_vpf_consultores = st.data_editor(df_vpf_consultores)

    # --------------------------------------------------------------------------------
    # 5. VPE
    # --------------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")
        st.write("Aquí podrías agregar la lógica de lectura/edición de tu Excel si tuvieras las hojas correspondientes para VPE.")
        # Ejemplo:
        # df_vpe_misiones = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_misiones")
        # df_vpe_consultores = pd.read_excel("main_bdd.xlsx", sheet_name="vpe_consultores")
        # Y replicar la lógica anterior para Requerimiento de Personal y DPP 2025

    # --------------------------------------------------------------------------------
    # 6. Actualización
    # --------------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización")
        st.write("Aquí puedes incluir información o formularios para la actualización de datos.")

    # --------------------------------------------------------------------------------
    # 7. Consolidado
    # --------------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")
        st.write("Aquí puedes mostrar la información consolidada de todas las secciones.")

# Punto de entrada de la app
if __name__ == "__main__":
    main()
