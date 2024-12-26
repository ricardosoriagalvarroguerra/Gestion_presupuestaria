import streamlit as st

def main():
    st.set_page_config(page_title="Aplicación multi-página", layout="wide")

    # Barra lateral para la navegación principal
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
    eleccion_principal = st.sidebar.selectbox(
        "Selecciona una sección:",
        menu_principal
    )

    # ----------------------------------------------------------------------------
    # 1. Página Principal
    # ----------------------------------------------------------------------------
    if eleccion_principal == "Página Principal":
        st.title("Página Principal")
        st.write("Bienvenido a la Página Principal. Aquí puedes colocar la información introductoria.")

    # ----------------------------------------------------------------------------
    # 2. VPD (página principal -> VPD)
    # ----------------------------------------------------------------------------
    elif eleccion_principal == "VPD":
        st.title("Sección VPD")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPD (Misiones, Otras Consultorías)
        menu_sub_vpd = ["Misiones", "Otras Consultorías"]
        eleccion_vpd = st.sidebar.selectbox("Selecciona la sub-sección de VPD:", menu_sub_vpd)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpd = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpd = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpd)

        # Lógica según subpágina y sub-subpágina
        if eleccion_vpd == "Misiones":
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Misiones > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Misiones** en VPD.")
            else:
                st.subheader("VPD > Misiones > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Misiones** en VPD.")

        else:  # Otras Consultorías
            if eleccion_sub_sub_vpd == "Requerimiento de Personal":
                st.subheader("VPD > Otras Consultorías > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Otras Consultorías** en VPD.")
            else:
                st.subheader("VPD > Otras Consultorías > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Otras Consultorías** en VPD.")

    # ----------------------------------------------------------------------------
    # 3. VPO (página principal -> VPO)
    # ----------------------------------------------------------------------------
    elif eleccion_principal == "VPO":
        st.title("Sección VPO")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPO (Misiones, Otras Consultorías)
        menu_sub_vpo = ["Misiones", "Otras Consultorías"]
        eleccion_vpo = st.sidebar.selectbox("Selecciona la sub-sección de VPO:", menu_sub_vpo)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpo = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpo = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpo)

        # Lógica según subpágina y sub-subpágina
        if eleccion_vpo == "Misiones":
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Misiones > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Misiones** en VPO.")
            else:
                st.subheader("VPO > Misiones > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Misiones** en VPO.")

        else:  # Otras Consultorías
            if eleccion_sub_sub_vpo == "Requerimiento de Personal":
                st.subheader("VPO > Otras Consultorías > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Otras Consultorías** en VPO.")
            else:
                st.subheader("VPO > Otras Consultorías > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Otras Consultorías** en VPO.")

    # ----------------------------------------------------------------------------
    # 4. VPF (página principal -> VPF)
    # ----------------------------------------------------------------------------
    elif eleccion_principal == "VPF":
        st.title("Sección VPF")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPF (Misiones, Otras Consultorías)
        menu_sub_vpf = ["Misiones", "Otras Consultorías"]
        eleccion_vpf = st.sidebar.selectbox("Selecciona la sub-sección de VPF:", menu_sub_vpf)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpf = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpf = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpf)

        # Lógica según subpágina y sub-subpágina
        if eleccion_vpf == "Misiones":
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Misiones > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Misiones** en VPF.")
            else:
                st.subheader("VPF > Misiones > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Misiones** en VPF.")

        else:  # Otras Consultorías
            if eleccion_sub_sub_vpf == "Requerimiento de Personal":
                st.subheader("VPF > Otras Consultorías > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Otras Consultorías** en VPF.")
            else:
                st.subheader("VPF > Otras Consultorías > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Otras Consultorías** en VPF.")

    # ----------------------------------------------------------------------------
    # 5. VPE (página principal -> VPE)
    # ----------------------------------------------------------------------------
    elif eleccion_principal == "VPE":
        st.title("Sección VPE")
        st.write("Selecciona las subpáginas en la barra lateral para explorar los contenidos.")

        # Subpáginas de VPE (Misiones, Otras Consultorías)
        menu_sub_vpe = ["Misiones", "Otras Consultorías"]
        eleccion_vpe = st.sidebar.selectbox("Selecciona la sub-sección de VPE:", menu_sub_vpe)

        # Sub-subpáginas (Requerimiento de Personal, DPP 2025)
        menu_sub_sub_vpe = ["Requerimiento de Personal", "DPP 2025"]
        eleccion_sub_sub_vpe = st.sidebar.selectbox("Selecciona el tema:", menu_sub_sub_vpe)

        # Lógica según subpágina y sub-subpágina
        if eleccion_vpe == "Misiones":
            if eleccion_sub_sub_vpe == "Requerimiento de Personal":
                st.subheader("VPE > Misiones > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Misiones** en VPE.")
            else:
                st.subheader("VPE > Misiones > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Misiones** en VPE.")

        else:  # Otras Consultorías
            if eleccion_sub_sub_vpe == "Requerimiento de Personal":
                st.subheader("VPE > Otras Consultorías > Requerimiento de Personal")
                st.write("Contenido de **Requerimiento de Personal** para **Otras Consultorías** en VPE.")
            else:
                st.subheader("VPE > Otras Consultorías > DPP 2025")
                st.write("Contenido de **DPP 2025** para **Otras Consultorías** en VPE.")

    # ----------------------------------------------------------------------------
    # 6. Actualización
    # ----------------------------------------------------------------------------
    elif eleccion_principal == "Actualización":
        st.title("Actualización")
        st.write("Aquí puedes incluir información o formularios para la actualización de datos.")

    # ----------------------------------------------------------------------------
    # 7. Consolidado
    # ----------------------------------------------------------------------------
    elif eleccion_principal == "Consolidado":
        st.title("Consolidado")
        st.write("Aquí puedes mostrar la información consolidada de todas las secciones.")

if __name__ == "__main__":
    main()
