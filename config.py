"""Constantes globales de marca y metadatos de SIMVEG."""

APP_NAME_SHORT = "SIMVEG"
APP_NAME_FULL = (
    "SIMVEG - Sistema de Simulación y Modelado de Violencias con Énfasis en Género"
)
APP_DESCRIPTION = "Sistema de Simulación y Modelado de Violencias con Énfasis en Género"
APP_REGION = "Departamento de Antioquia, Colombia"


def get_page_title(section: str) -> str:
    """Título de pestaña del navegador: '<Sección> | SIMVEG'."""
    return f"{section} | {APP_NAME_SHORT}"
