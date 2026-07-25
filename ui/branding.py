import streamlit as st

from config import APP_DESCRIPTION, APP_NAME_FULL, APP_NAME_SHORT


def render_sidebar_branding() -> None:
    """Marca SIMVEG en la barra lateral."""
    st.sidebar.markdown(f"**{APP_NAME_SHORT}**")
    st.sidebar.caption(APP_DESCRIPTION)
    st.sidebar.divider()


def render_platform_header(module_title: str, module_subtitle: str | None = None) -> None:
    """Encabezado principal de la plataforma y título del módulo."""
    st.markdown(f"## {APP_NAME_SHORT}")
    st.caption(APP_NAME_FULL)
    st.divider()
    st.title(module_title)
    if module_subtitle:
        st.markdown(module_subtitle)


def render_platform_footer() -> None:
    """Pie de página con la identidad de la plataforma."""
    st.markdown("---")
    st.caption(f"{APP_NAME_FULL} · {APP_DESCRIPTION}")
