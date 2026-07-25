from dataclasses import dataclass

ESTADO_NO_APLICA = 0
ESTADO_PENDIENTE = 1
ESTADO_ATENDIDO = 2
ESTADO_CADUCADO = 3

PRIORIDAD_ALTA = 1
PRIORIDAD_REGULAR = 2

EDADES_ALTA_PRIORIDAD = frozenset({"0-2", "2-7", "7-12"})


@dataclass(slots=True)
class ExpedienteRecord:
    dias_espera: int = 0
    prioridad: int = PRIORIDAD_REGULAR
    fallo_administrativo: bool = False
    salud: int = ESTADO_NO_APLICA
    prot: int = ESTADO_NO_APLICA

    def esta_completado(self) -> bool:
        return ESTADO_PENDIENTE not in (self.salud, self.prot)

    def avanzar_dia(self) -> None:
        if self.esta_completado():
            return

        self.dias_espera += 1
        if self.dias_espera <= 30:
            return

        self.fallo_administrativo = True
        if self.salud == ESTADO_PENDIENTE:
            self.salud = ESTADO_CADUCADO
        if self.prot == ESTADO_PENDIENTE:
            self.prot = ESTADO_CADUCADO


def crear_expediente(edad: str, naturaleza: str, ruta_requerida: dict[str, bool]) -> ExpedienteRecord:
    es_alta = edad in EDADES_ALTA_PRIORIDAD or naturaleza == "Violencia Sexual"
    return ExpedienteRecord(
        prioridad=PRIORIDAD_ALTA if es_alta else PRIORIDAD_REGULAR,
        salud=ESTADO_PENDIENTE if ruta_requerida.get("Salud Mental") else ESTADO_NO_APLICA,
        prot=ESTADO_PENDIENTE if ruta_requerida.get("Proteccion") else ESTADO_NO_APLICA,
    )


def procesar_cola_servicio(
    cola: list[ExpedienteRecord],
    capacidad: int,
    servicio: str,
) -> None:
    atendidos = 0
    while atendidos < capacidad and cola:
        expediente = cola.pop(0)
        if servicio == "Salud Mental":
            expediente.salud = ESTADO_ATENDIDO
        else:
            expediente.prot = ESTADO_ATENDIDO
        atendidos += 1
