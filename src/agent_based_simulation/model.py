import random
from typing import Callable, Optional

import numpy as np
import pandas as pd

from .agents import (
    ESTADO_PENDIENTE,
    PRIORIDAD_ALTA,
    crear_expediente,
    procesar_cola_servicio,
)


class AuditoriaOperativaModel:
    def __init__(
        self,
        df_prophet: pd.DataFrame,
        sim_params: dict,
        matriz_markov: dict,
        capacidades: dict[str, int],
        pct_fin_semana: float,
    ):
        df = df_prophet.reset_index(drop=True)
        df["Fecha"] = pd.to_datetime(df["Fecha"])

        self.casos_diarios = np.round(
            np.maximum(0, df["Casos Pronosticados"].to_numpy(dtype=float))
        ).astype(np.int32)
        self.es_fin_semana = (df["Fecha"].dt.weekday.to_numpy() >= 5).astype(bool)
        self.total_dias = int(sim_params["dias"])

        self.matriz_markov = matriz_markov
        self.capacidades = capacidades
        self.pct_fin_semana = float(pct_fin_semana)
        self._markov_default = {"Salud Mental": 0.3, "Proteccion": 0.5}

        self._nats = list(sim_params["dist_naturaleza"].keys())
        self._p_nats = np.asarray(
            list(sim_params["dist_naturaleza"].values()), dtype=float
        )
        self._edades = list(sim_params["dist_edad"].keys())
        self._p_edades = np.asarray(list(sim_params["dist_edad"].values()), dtype=float)

        if self._p_nats.sum() > 0:
            self._p_nats /= self._p_nats.sum()
        if self._p_edades.sum() > 0:
            self._p_edades /= self._p_edades.sum()

        self._rng = random.Random()

        self.activos: list = []
        self.pendientes_por_servicio = {servicio: [] for servicio in capacidades}

        self._completados_total = 0
        self._fallos_administrativos = 0
        self._hist_dias: list[int] = []
        self._hist_prioridad: list[int] = []

        self.metricas_diarias: list[dict] = []

    def set_seed(self, seed: int) -> None:
        self._rng.seed(seed)

    def _crear_expedientes_dia(self, cantidad: int) -> None:
        if cantidad <= 0:
            return

        naturalezas = (
            self._rng.choices(self._nats, weights=self._p_nats, k=cantidad)
            if self._nats
            else ["Sin Dato"] * cantidad
        )
        edades = (
            self._rng.choices(self._edades, weights=self._p_edades, k=cantidad)
            if self._edades
            else ["Sin Dato"] * cantidad
        )

        for naturaleza, edad in zip(naturalezas, edades):
            probs = self.matriz_markov.get(naturaleza, self._markov_default)
            ruta_requerida = {
                "Salud Mental": self._rng.random() < probs.get("Salud Mental", 0),
                "Proteccion": self._rng.random() < probs.get("Proteccion", 0),
            }
            expediente = crear_expediente(edad, naturaleza, ruta_requerida)
            self.activos.append(expediente)

            for servicio in self.pendientes_por_servicio:
                estado = (
                    expediente.salud
                    if servicio == "Salud Mental"
                    else expediente.prot
                )
                if estado == ESTADO_PENDIENTE:
                    self.pendientes_por_servicio[servicio].append(expediente)

    def _procesar_servicios(self, es_fin_semana: bool) -> None:
        for servicio, capacidad_base in self.capacidades.items():
            cola = self.pendientes_por_servicio[servicio]
            if not cola:
                continue

            cola.sort(key=lambda exp: (exp.prioridad, -exp.dias_espera))
            capacidad = (
                int(capacidad_base * self.pct_fin_semana)
                if es_fin_semana
                else capacidad_base
            )
            procesar_cola_servicio(cola, capacidad, servicio)

    def _avanzar_dia_activos(self) -> None:
        if not self.activos:
            return

        pendientes: list = []
        for expediente in self.activos:
            expediente.avanzar_dia()
            if expediente.esta_completado():
                self._completados_total += 1
                self._hist_dias.append(expediente.dias_espera)
                self._hist_prioridad.append(expediente.prioridad)
                if expediente.fallo_administrativo:
                    self._fallos_administrativos += 1
            else:
                pendientes.append(expediente)

        self.activos = pendientes

    def _sincronizar_pendientes(self) -> None:
        for servicio in self.pendientes_por_servicio:
            if servicio == "Salud Mental":
                self.pendientes_por_servicio[servicio] = [
                    exp for exp in self.activos if exp.salud == ESTADO_PENDIENTE
                ]
            else:
                self.pendientes_por_servicio[servicio] = [
                    exp for exp in self.activos if exp.prot == ESTADO_PENDIENTE
                ]

    def _registrar_metricas(self, nuevos_casos_hoy: int) -> None:
        self.metricas_diarias.append(
            {
                "Nuevos Casos (Prophet)": nuevos_casos_hoy,
                "Casos Completados": self._completados_total,
                "Backlog Total": len(self.activos),
                "Backlog Salud Mental": len(
                    self.pendientes_por_servicio.get("Salud Mental", [])
                ),
                "Backlog Proteccion": len(
                    self.pendientes_por_servicio.get("Proteccion", [])
                ),
            }
        )

    def run(
        self,
        progress_callback: Optional[Callable[[float], None]] = None,
        progress_every: int = 25,
    ) -> None:
        total = min(self.total_dias, len(self.casos_diarios))

        for dia in range(total):
            nuevos_casos_hoy = int(self.casos_diarios[dia])
            es_fin_semana = bool(self.es_fin_semana[dia])

            self._crear_expedientes_dia(nuevos_casos_hoy)
            self._procesar_servicios(es_fin_semana)
            self._avanzar_dia_activos()
            self._sincronizar_pendientes()
            self._registrar_metricas(nuevos_casos_hoy)

            if progress_callback and (dia % progress_every == 0 or dia == total - 1):
                progress_callback((dia + 1) / total)

    def get_results_dataframe(self, df_prophet: pd.DataFrame) -> pd.DataFrame:
        resultados = pd.DataFrame(self.metricas_diarias)
        resultados["Fecha"] = pd.to_datetime(df_prophet["Fecha"]).values[
            : len(resultados)
        ]
        return resultados

    def get_histogram_dataframe(self) -> tuple[pd.DataFrame, int]:
        if not self._hist_dias:
            return pd.DataFrame(), self._fallos_administrativos

        df_hist = pd.DataFrame(
            {
                "Dias Espera": self._hist_dias,
                "Grupo Prioritario": [
                    (
                        "Alta Prioridad (Menores/Sexual)"
                        if prioridad == PRIORIDAD_ALTA
                        else "Prioridad Regular"
                    )
                    for prioridad in self._hist_prioridad
                ],
            }
        )
        return df_hist, self._fallos_administrativos

    def get_histogram_bins(self, nbins: int = 30) -> dict:
        if not self._hist_dias:
            return {"alta": None, "regular": None}

        dias = np.asarray(self._hist_dias, dtype=np.int32)
        prioridades = np.asarray(self._hist_prioridad, dtype=np.int8)

        alta = dias[prioridades == PRIORIDAD_ALTA]
        regular = dias[prioridades != PRIORIDAD_ALTA]

        if alta.size == 0 and regular.size == 0:
            return {"alta": None, "regular": None}

        max_dia = int(dias.max()) if dias.size else 1
        bin_edges = np.linspace(0, max(max_dia, 1), nbins + 1)

        return {
            "alta": np.histogram(alta, bins=bin_edges) if alta.size else None,
            "regular": np.histogram(regular, bins=bin_edges) if regular.size else None,
            "bin_edges": bin_edges,
        }
