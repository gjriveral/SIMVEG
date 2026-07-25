import hashlib
from typing import Callable, Optional

import pandas as pd

from .model import AuditoriaOperativaModel

MATRIZ_MARKOV_EMPIRICA = {
    "Violencia Física": {"Salud Mental": 0.25, "Proteccion": 0.57},
    "Violencia Psicológica": {"Salud Mental": 0.88, "Proteccion": 0.81},
    "Negligencia": {"Salud Mental": 0.90, "Proteccion": 0.77},
    "Violencia Sexual": {"Salud Mental": 0.85, "Proteccion": 0.90},
}


def _hashable_sim_params(sim_params: dict) -> tuple:
    return (
        sim_params["municipio"],
        sim_params["dias"],
        tuple(sorted(sim_params["dist_estrato"].items())),
        tuple(sorted(sim_params["dist_edad"].items())),
        tuple(sorted(sim_params["dist_naturaleza"].items())),
    )


def _hashable_prophet(df_prophet: pd.DataFrame) -> tuple:
    fechas = pd.to_datetime(df_prophet["Fecha"]).astype(str).tolist()
    casos = df_prophet["Casos Pronosticados"].round(6).tolist()
    return tuple(zip(fechas, casos))


def _simulation_seed(
    cap_salud: int,
    cap_prot: int,
    pct_fin_semana: float,
    sim_params: dict,
    df_prophet: pd.DataFrame,
) -> int:
    raw = "|".join(
        [
            str(cap_salud),
            str(cap_prot),
            str(pct_fin_semana),
            repr(_hashable_sim_params(sim_params)),
            repr(_hashable_prophet(df_prophet)),
        ]
    )
    return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)


def run_auditoria_simulation(
    df_prophet: pd.DataFrame,
    sim_params: dict,
    cap_salud: int,
    cap_prot: int,
    pct_fin_semana: float,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> dict:
    """Ejecuta la simulación ABM y devuelve resultados serializables."""
    modelo = AuditoriaOperativaModel(
        df_prophet=df_prophet,
        sim_params=sim_params,
        matriz_markov=MATRIZ_MARKOV_EMPIRICA,
        capacidades={"Salud Mental": cap_salud, "Proteccion": cap_prot},
        pct_fin_semana=pct_fin_semana,
    )
    modelo.set_seed(
        _simulation_seed(cap_salud, cap_prot, pct_fin_semana, sim_params, df_prophet)
    )
    modelo.run(progress_callback=progress_callback)

    df_hist, fallos_administrativos = modelo.get_histogram_dataframe()

    return {
        "resultados": modelo.get_results_dataframe(df_prophet),
        "df_hist": df_hist,
        "hist_bins": modelo.get_histogram_bins(),
        "fallos_administrativos": fallos_administrativos,
    }
