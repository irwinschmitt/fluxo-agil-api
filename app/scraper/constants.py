# URLs

base_url = "https://sigaa.unb.br/sigaa/public"
default_language = "pt_BR"

graduation_programs_link = base_url + "/curso/lista.jsf?nivel=G&aba=p-graduacao"
components_link = f"{base_url}/componentes/busca_componentes.jsf"


graduation_courses_link = base_url + "/curso/portal.jsf"
graduation_curricula_link = base_url + "/curso/curriculo.jsf"

department_base_url = f"{base_url}/departamento"
department_base_presentation_url = f"{department_base_url}/portal.jsf"
department_base_components_url = f"{department_base_url}/componentes.jsf"

programs_base_url = f"{base_url}/curso"
programs_list_base_url = f"{programs_base_url}/lista.jsf"
graduation_programs_url = f"{programs_list_base_url}?nivel=G&aba=p-graduacao"

curricula_list_base_url = f"{programs_base_url}/curriculo.jsf"


# Page functions

ELEMENT_INNER_TEXT = "(element) => element.innerText"
ELEMENT_PREVIOUS_SIBLINGS = "(element) => element.previousSiblings()"
FIND_ELEMENT_WITHOUT_CLASS = ".find((element) => element.classList.length === 0)"
TABLE_CONTENT_ROW_SELECTOR = "tr.linhaPar, tr.linhaImpar"

# Programs

program_degree_map = {
    "BACHAREL": "BACHELOR",
    "LICENCIADO": "LICENTIATE",
}

program_shift_map = {
    "DIURNO": "DAY",
    "NOTURNO": "NIGHT",
}
