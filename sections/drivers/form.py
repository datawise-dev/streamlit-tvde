import streamlit as st
from utils.error_handlers import handle_streamlit_error
from utils.form_builder import FormBuilder
from utils.validators import validate_nif, validate_postal_code


@handle_streamlit_error()
def driver_form(existing_data=None):
    """Display form for driver data with error handling using FormBuilder."""

    form = FormBuilder("driver_form")

    # --- Basic Driver Information ---
    form.create_section("Informação Pessoal")
    form.create_field(
        key="display_name",
        label="Nome de Exibição",
        type="text",
        required=True,
        help="Nome único para identificação do motorista"
    )

    # --- First Name and Last Name ---
    form.create_columns(2)
    form.create_field(
        key="first_name",
        label="Nome",
        type="text",
        required=True,
    )
    form.create_field(
        key="last_name",
        label="Apelido",
        type="text",
        required=True,
    )
    form.end_columns()

    # --- NIF and NISS ---
    form.create_columns(2)
    form.create_field(
        key="nif",
        label="NIF",
        type="text",
        required=True,
        help="Número de Identificação Fiscal",
        validator=validate_nif
    )
    form.create_field(
        key="niss",
        label="NISS",
        type="text",
        required=False,
        help="Número de Identificação de Segurança Social"
    )
    form.end_columns()

    # --- Address Information ---
    form.create_section("Morada")
    form.create_field(
        key="address_line1",
        label="Linha de Endereço 1",
        type="text",
        required=False,
    )
    
    form.create_field(
        key="address_line2",
        label="Linha de Endereço 2",
        type="text",
        required=False,
    )

    # --- Postal Code and Location ---
    form.create_columns(2)
    form.create_field(
        key="postal_code",
        label="Código Postal",
        type="text",
        required=False,
        placeholder="XXXX-XXX",
        validator=validate_postal_code,
    )
    form.create_field(
        key="location",
        label="Localidade",
        type="text",
        required=False,
    )
    form.end_columns()

    # --- Status Information (only for existing drivers) ---
    if existing_data:
        form.create_section("Estado")
        form.create_field(
            key="is_active",
            label="Ativo",
            type="checkbox",
            help="Indica se este motorista está atualmente ativo"
        )
    # For new drivers, default to active
    else:
        form.data["is_active"] = True

    # Required fields notice
    form.create_section(None, "**Campos obrigatórios*")

    return form