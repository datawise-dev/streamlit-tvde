import streamlit as st
from services.driver_service import DriverService

st.title("Adicionar Motorista")

# if existing_data is None:
existing_data = dict()

with st.form("driver_form"):
    
    st.subheader("Informação Pessoal")

    display_name = st.text_input(
        "Display Name *", 
        value=existing_data.get('display_name', ''),
        help="Nome único para identificação do motorista"
    )

    col1, col2 = st.columns(2)

    with col1:
        first_name =  st.text_input(
            "First Name",
            value=existing_data.get('first_name', '')
        )

    with col2:
        last_name =  st.text_input(
            "Last Name *",
            value=existing_data.get('last_name', '')
        )
    
    col1, col2 = st.columns(2)

    with col1:   
        nif = st.text_input(
            "NIF", 
            value=existing_data.get('nif', ''),
            help="Tax identification number"
        )

    with col2:
        niss = st.text_input(
            "NISS",
            value=existing_data.get('niss', ''),
            help="Social security number"
        )

    # Address information
    st.subheader("Morada")
    address_line1 = st.text_input(
        "Address Line 1 *",
        value=existing_data.get('address_line1', '')
    )
    
    address_line2 = st.text_input(
        "Address Line 2",
        value=existing_data.get('address_line2', '')
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        postal_code = st.text_input(
            "Postal Code *",
            value=existing_data.get('postal_code', ''),
            placeholder="XXXX-XXX"
        )
    
    with col2:
        location = st.text_input(
            "Location *",
            value=existing_data.get('location', '')
        )

    # Form submission
    st.markdown("**Campos obrigatórios*")
    submit_button = st.form_submit_button("Submit", use_container_width=True)

    if submit_button:
        
        if not all([display_name]):
            st.error("Todos os campos obrigatórios devem ser preenchidos")
            st.stop()

        driver_data = {
            'display_name': display_name,
            'first_name': first_name,
            'last_name': last_name,
            'nif': nif,
            'address_line1': address_line1,
            'address_line2': address_line2,
            'postal_code': postal_code,
            'location': location
        }

        try:
            driver_id = existing_data.get('id', None)
            if driver_id:
                if DriverService.update_driver(driver_id, driver_data):
                    st.success("Motorista atualizado com sucesso!")
            else:
                if DriverService.insert_driver(driver_data):
                    st.success("Motorista adicionado com sucesso!")

        except Exception as e:
            st.error(str(e))