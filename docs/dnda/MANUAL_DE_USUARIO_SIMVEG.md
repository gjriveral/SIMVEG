# MANUAL DE USUARIO

## SIMVEG — Sistema de Simulación y Modelado de Violencias con Énfasis en Género

| Campo | Detalle |
|-------|---------|
| **Versión del documento** | 1.0 |
| **Versión del software** | 1.0 |
| **Fecha** | Julio de 2026 |
| **Titular** | UNAD — Universidad Nacional Abierta y a Distancia |
| **Tipo de software** | Aplicación web analítica (Python / Streamlit) |
| **Ámbito geográfico** | Departamento de Antioquia, Colombia |

---

## 1. Introducción

### 1.1 Título del software

**SIMVEG — Sistema de Simulación y Modelado de Violencias con Énfasis en Género**

### 1.2 Objeto del manual

Este documento describe el propósito, los requisitos, la instalación, la operación e interpretación de resultados de SIMVEG. Está dirigido a investigadores, formuladores de política pública, funcionarios de salud, equipos de protección y usuarios técnicos que requieran pronosticar casos de violencia y evaluar la capacidad institucional de respuesta.

### 1.3 Descripción general y propósito del sistema

SIMVEG es una plataforma web de apoyo a la toma de decisiones en materia de violencias con énfasis en género. Integra dos capacidades analíticas:

1. **Módulo de Pronóstico:** utiliza series temporales históricas provenientes de SIVIGILA (Sistema Nacional de Vigilancia en Salud Pública de Colombia), procesadas para el departamento de Antioquia, y aplica el modelo estadístico **Prophet** para estimar la evolución futura de casos según filtros sociodemográficos y de modalidad de violencia.

2. **Módulo de Auditoría Operativa:** recibe la proyección diaria del pronóstico y ejecuta una **simulación basada en agentes** que representa expedientes de víctimas, colas de atención en Salud Mental y Protección (Comisarías), triage por vulnerabilidad y restricciones de capacidad institucional, incluyendo reducción operativa en fines de semana.

**Propósito técnico:** cuantificar tendencias, escenarios futuros y cuellos de botella institucionales.

**Propósito social:** aportar evidencia para la planificación de recursos, la priorización de casos de alta vulnerabilidad (menores de edad y violencia sexual) y la identificación de fallos administrativos (expedientes con más de 30 días sin resolución).

### 1.4 Arquitectura funcional

| Componente | Función |
|-----------|---------|
| `simveg.py` | Punto de entrada; módulo de pronóstico |
| `pages/1_Simulador_Auditoria.py` | Módulo de auditoría operativa |
| `config.py` | Metadatos y constantes de marca |
| `ui/branding.py` | Elementos visuales de identidad SIMVEG |
| `src/agent_based_simulation/` | Motor de simulación (agentes, modelo, ejecutor) |
| `data/processed/SerieMensual.csv` | Serie histórica consolidada para pronóstico |

---

## 2. Requisitos del sistema

### 2.1 Requisitos de hardware (mínimos recomendados)

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| Procesador | 2 núcleos | 4 núcleos o más |
| Memoria RAM | 4 GB | 8 GB o más |
| Almacenamiento | 500 MB libres | 1 GB o más |
| Resolución de pantalla | 1280 × 720 px | 1920 × 1080 px |

### 2.2 Requisitos de software

| Componente | Versión |
|------------|---------|
| Sistema operativo | Windows 10/11, Linux o macOS |
| Python | 3.11 o superior |
| Navegador web | Google Chrome, Mozilla Firefox o Microsoft Edge (versiones recientes) |
| Conexión a red | Solo requerida para instalación de dependencias |

### 2.3 Dependencias principales (Python)

| Librería | Propósito |
|----------|-----------|
| `streamlit` | Interfaz web interactiva |
| `pandas` | Manipulación de datos |
| `prophet` | Modelo de pronóstico temporal |
| `plotly` | Gráficos interactivos |
| `openpyxl` | Exportación a Excel |
| `numpy`, `scipy` | Cálculos numéricos |
| `mesa` | Referencia en simulación de agentes |

La instalación completa se realiza mediante el archivo `requirements.txt` ubicado en la raíz del proyecto.

---

## 3. Instalación y ejecución

### 3.1 Obtención del software

Descomprimir o clonar el proyecto en una ruta local, por ejemplo:

```
C:\SIMVEG\
```

### 3.2 Creación del entorno virtual (recomendado)

**Windows (PowerShell):**

```powershell
cd "C:\SIMVEG"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Linux / macOS:**

```bash
cd /ruta/SIMVEG
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Ejecución local

```powershell
python -m streamlit run simveg.py
```

La aplicación quedará disponible en: **http://localhost:8501**

### 3.4 Ejecución en servidor

1. Instalar dependencias en el servidor.
2. Configurar `streamlit.toml` (puerto, modo headless).
3. Ejecutar:

```bash
python -m streamlit run simveg.py --server.port 8501 --server.headless true
```

4. Publicar el puerto mediante proxy inverso (Nginx, Apache) si se requiere acceso externo.

### 3.5 Estructura de datos requerida

El pronóstico requiere el archivo `data/processed/SerieMensual.csv`, generado a partir de datos SIVIGILA mediante los scripts ETL incluidos en `src/etl/`.

---

## 4. Descripción de la interfaz general

Al abrir SIMVEG, la interfaz presenta:

| Elemento | Descripción |
|----------|-------------|
| **Encabezado** | Marca SIMVEG, nombre completo del sistema y título del módulo activo |
| **Barra lateral (Sidebar)** | Filtros, parámetros de simulación y navegación entre páginas |
| **Área principal** | Gráficos, métricas, tablas y botones de acción |
| **Pie de página** | Identificación institucional del software |
| **Menú de páginas Streamlit** | Permite alternar entre **Pronóstico** y **Simulador de Auditoría** |

---

## 5. Guía de uso — Módulo 1: Pronóstico de Casos de Violencia

### 5.1 Objetivo del módulo

Estimar la cantidad futura de casos de violencia según criterios de análisis seleccionados por el usuario.

### 5.2 Procedimiento paso a paso

**Paso 1.** Abrir SIMVEG en el navegador (`http://localhost:8501`).

**Paso 2.** Verificar que la página principal muestre el título *Pronóstico de Casos de Violencia* y el subtítulo *Análisis predictivo para el Departamento de Antioquia, Colombia*.

**Paso 3.** Configurar filtros en la barra lateral:

| Filtro | Descripción |
|--------|-------------|
| Rango de Años (Ocurrencia) | Periodo histórico para entrenar el modelo |
| Municipio (Ocurrencia) | Municipio específico o "Todos" |
| Modalidad | Tipo de violencia (física, psicológica, etc.) |
| Tipo Violencia Sexual | Subclasificación cuando aplica |
| Rango de Edad | Grupo etario de la víctima |
| Estrato | Estrato socioeconómico |
| Sexo Víctima / Sexo Agresor | Variables demográficas |
| Meses a pronosticar | Horizonte futuro (3 a 60 meses) |

**Paso 4.** Presionar el botón **"Generar Pronóstico"**.

**Paso 5.** Seleccionar el **Nivel de detalle temporal:** Día, Mes, Trimestre, Semestre o Año.

**Paso 6.** Interpretar el gráfico principal:

| Elemento visual | Significado |
|-----------------|-------------|
| Línea histórica suavizada | Comportamiento observado en el pasado |
| Línea de pronóstico | Estimación central futura |
| Banda sombreada | Intervalo de confianza del modelo |
| Línea vertical punteada | Inicio del periodo proyectado |

**Paso 7.** Exportar resultados con **"Descargar Informe en Excel"**, que incluye:

- Hoja de pronóstico según agrupación temporal
- Parámetros matemáticos del modelo Prophet
- Filtros aplicados en la consulta

### 5.3 Requisito para el módulo de auditoría

El pronóstico debe generarse **antes** de usar el simulador de auditoría, ya que alimenta la demanda diaria proyectada y las distribuciones empíricas de estrato, edad y naturaleza del caso.

---

## 6. Guía de uso — Módulo 2: Simulador de Capacidad Institucional y Cuellos de Botella

### 6.1 Objetivo del módulo

Simular el comportamiento del sistema institucional de respuesta ante la demanda proyectada, identificando represas (backlog), desempeño global y posibles fallos administrativos.

### 6.2 Acceso al módulo

1. Generar un pronóstico en la página principal.
2. En el menú lateral de Streamlit, seleccionar **Simulador Auditoria**.
3. Si no existe pronóstico previo, el sistema mostrará una advertencia indicando que debe generarse primero.

### 6.3 Configuración de parámetros

| Parámetro | Descripción | Rango |
|-----------|-------------|-------|
| Cupos Salud Mental (Psicólogos) | Capacidad diaria de atención en salud mental | 1 – 50 (default: 10) |
| Cupos Protección (Comisarías) | Capacidad diaria en rutas de protección | 1 – 50 (default: 15) |
| Retención Operativa Fines de Semana | Porcentaje de capacidad disponible sábados y domingos | 0.0 – 1.0 (default: 0.2) |

### 6.4 Ejecución de la simulación

1. Ajustar parámetros en la barra lateral.
2. Presionar **"Ejecutar Auditoría Operativa"**.
3. Durante el procesamiento se muestra una barra de progreso (*Simulando día a día…*).
4. Si los parámetros ya fueron simulados en la sesión, los resultados se recuperan de caché en memoria.

### 6.5 Interpretación de resultados

#### Gráfico 1: Rendimiento Global del Sistema

| Serie | Interpretación |
|-------|----------------|
| Demanda Acumulada (línea discontinua negra) | Total de casos proyectados acumulados |
| Expedientes Resueltos (área verde) | Casos atendidos acumulativamente por el sistema simulado |

Una brecha creciente entre ambas curvas indica incapacidad institucional para absorber la demanda.

#### Gráfico 2: Evolución del Backlog

| Serie | Interpretación |
|-------|----------------|
| Represa: Salud Mental (azul) | Expedientes pendientes en psicología/salud mental |
| Represa: Comisarías (naranja) | Expedientes pendientes en protección |

El patrón en "dientes de sierra" refleja acumulación en fines de semana por reducción operativa.

#### Indicadores (métricas)

| Indicador | Significado |
|-----------|-------------|
| **Total Demanda (Prophet)** | Suma de casos diarios proyectados en el horizonte simulado |
| **Expedientes Atrapados (Sin Resolver)** | Backlog total al final del periodo |
| **Fallos Administrativos (> 30 días)** | Expedientes que superaron 30 días sin resolución |

#### Gráfico 3: Distribución de Tiempos de Espera

Histograma comparativo entre **Alta Prioridad (Menores/Sexual)** y **Prioridad Regular**. Si la curva de alta prioridad se desplaza hacia tiempos elevados, el sistema está colapsado incluso para los casos más urgentes.

### 6.6 Fundamento metodológico (resumen)

- **Entrada:** pronóstico diario Prophet + distribuciones empíricas SIVIGILA
- **Modelo:** teoría de colas + cadenas de Markov (probabilidades de remisión por modalidad)
- **Triage:** prioridad 1 para menores y violencia sexual; prioridad 2 para el resto
- **Calendario:** reducción de capacidad en fines de semana según parámetro configurado

---

## 7. Solución de problemas frecuentes

| Problema | Causa probable | Solución |
|----------|----------------|----------|
| La página no carga | Streamlit no está ejecutándose | Ejecutar `python -m streamlit run simveg.py` |
| Error al pronosticar | Filtros sin datos suficientes | Ampliar rango de años o relajar filtros |
| Simulador vacío | No hay pronóstico previo | Generar pronóstico en página principal |
| Lentitud inicial | Primera carga de datos/modelo | Esperar; ejecuciones posteriores usan caché |
| Error de dependencias | Entorno virtual no activado | Activar `.venv` e instalar `requirements.txt` |

---

## 8. Propiedad intelectual y licenciamiento

El software SIMVEG se distribuye bajo licencia **MIT**. Titular del derecho de autor: **UNAD — Universidad Nacional Abierta y a Distancia** (según archivo `LICENSE` del proyecto).

---

## 9. Anexos para registro DNDA

Para el registro ante la **Dirección Nacional de Derecho de Autor (DNDA)**, adjuntar junto con este manual:

- Extracto consolidado de código fuente (`EXTRACTO_CODIGO_FUENTE_SIMVEG.txt`)
- Identificación del titular del derecho de autor
- Declaración de originalidad del software

---

*Documento generado para registro ante la DNDA — SIMVEG v1.0*
