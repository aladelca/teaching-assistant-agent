**Objetivo**
Diseñar un agente que corrija prácticas calificadas en notebooks, asigne nota final y genere feedback de alta calidad, consistente y riguroso. El feedback se publica solo tras aprobación docente.

**Alcance**
- Entradas: notebooks de prácticas calificadas.
- Salidas: nota final, feedback por criterio, evidencias citadas (celdas específicas), y resumen para el docente.
- Publicación: siempre con revisión y aprobación previa.

**Insumos**
- Sílabo en PDF por curso (formato variable).
- Carpeta sugerida para carga: `inputs/silabos/`.

**Principios de Calidad**
- Consistencia: la misma rúbrica produce resultados equivalentes ante casos similares.
- Rigurosidad: el puntaje se respalda con evidencia y pruebas ejecutables cuando aplique.
- Transparencia: cada criterio incluye razones y referencia a celdas del notebook.

**Decisiones Clave**
- El agente no publica automáticamente; requiere aprobación docente.
- La nota final se calcula con rúbrica y evidencia cuantitativa cuando sea posible.
- Se prioriza la calidad del feedback, aunque implique más pasos de validación.
- Escala de calificación fija: 0–20.

**Flujo de Trabajo Propuesto**
1. Ingesta del notebook
2. Normalización y extracción
3. Evaluación automática
4. Evaluación semántica por rúbrica
5. Generación de feedback con evidencias
6. Revisión docente
7. Publicación en Blackboard o Teams

**Arquitectura Simple (2 Agentes + 1 Validador)**
- Extractor de contexto
  - Lee: enunciado, rúbrica, material del curso, ejemplos buenos/malos y entrega del alumno.
  - Devuelve un “paquete” limpio: objetivos, criterios, restricciones, escala 0–20 y texto del estudiante.
- Evaluador
  - Por criterio: puntaje, explicación, evidencia (citas), errores típicos y mejora concreta.
- Validador de seguridad/calidad
  - Chequea: tono respetuoso, no inventar reglas, coherencia puntajes‑comentarios, citas reales y ausencia de alucinación.

**Estrategia de Evaluación**
- Rúbrica con criterios y pesos explícitos
- Rúbrica derivada del sílabo con verificación docente (si faltan pesos, se proponen y se marcan como “pendiente de confirmación”)
- Evidencias concretas por criterio (celdas, outputs, gráficas, funciones)
- Validación con pruebas automáticas cuando haya código
- Registro de incertidumbre: el agente marca criterios con baja confianza

**Formatos de Feedback (Preferencias de Estudiantes)**
- Resumen 3 líneas: “Qué está bien / Qué falta / Prioridad #1”.
- Top 5 mejoras con ejemplos cortos (“Cambia X por Y”).
- Comentarios anclados: “Celda 12, línea 3” o cita breve del fragmento.
- Mini‑rúbrica visible: tabla con criterios y puntajes.
- Preguntas guía (2–3) para reflexión.

**Perfiles de Corrección (Intención del Profesor)**
- Estricto con citas
- Prioriza argumentación
- Más suave con gramática
- Enfoque en metodología
- Ajuste de pesos por criterio (contenido, claridad, formato, etc.).
- Banderas: plagio sospechoso, falta de fuentes, contradicciones, no responde al enunciado.


**Componentes Técnicos**
- Ingesta
  - Lectura de `.ipynb` y metadatos
  - Mapeo de celdas a identificadores estables
- Ingesta de sílabo (PDF)
  - Extracción de texto, tablas y secciones (objetivos, evaluación, criterios, escala)
  - Detección de PDFs escaneados y uso de OCR si aplica
  - Normalización de lenguaje y secciones inconsistentes
- Normalización
  - Extracción de texto, código y outputs
  - Limpieza de ruido y ordenamiento por ejecución
- Evaluación Automática
  - Pruebas unitarias o validaciones de resultados
  - Chequeos de formato, completitud y estilo
- Evaluación Semántica
  - LLM guiado por rúbrica
  - Comparación con ejemplos de referencia
- Integración OpenAI (opcional pero recomendada)
  - Uso del OpenAI Agents SDK para evaluación semántica y extracción estructurada
  - Moderación de contenido y filtros de seguridad
  - Control de costos y límites de tasa
- Ensamblado de Nota
  - Suma ponderada por criterio
  - Ajustes por pruebas fallidas o faltas críticas
- Aprobación
  - Vista previa editable con control de cambios

**Rúbrica Base (Ejemplo)**
- Correctitud técnica
- Razonamiento y justificación
- Calidad del análisis y conclusiones
- Presentación y claridad
- Reproducibilidad

**Evidencias**
- Cada comentario debe señalar al menos una evidencia específica
- Estructura recomendada: Criterio + Evidencia + Impacto + Mejora

**Métricas de Éxito**
- Consistencia inter‑evaluador (agente vs. docente)
- Reducción de tiempo de corrección
- Calidad percibida del feedback
- Tasa de correcciones docentes mínimas

**Plan de Implementación (MVP a Producción)**
1. Ingesta de sílabo y derivación de rúbrica (con validación docente)
2. Prototipo de extracción y normalización de notebooks
3. Motor de evaluación automática (pruebas básicas)
4. Evaluación semántica con LLM y plantilla de feedback
5. Interfaz de revisión docente con “aprobar/publicar”
6. Integración inicial con Blackboard o Teams
7. Piloto con un curso y calibración
8. Endurecer seguridad, registros y auditoría

**Entregables Iniciales**
- Documento de rúbrica y pesos
- Plantilla de feedback con ejemplos
- Pipeline de evaluación automatizada
- UI de revisión y aprobación
- Conectores básicos a Blackboard y Teams

**Riesgos y Mitigaciones**
- Riesgo: inconsistencia en la nota
  - Mitigación: calibración con ejemplos y pruebas de regresión
- Riesgo: feedback demasiado genérico
  - Mitigación: forzar evidencias y referencias a celdas
- Riesgo: fallos de ejecución
  - Mitigación: entorno controlado y límites de recursos
- Riesgo: “reescribir” el trabajo del alumno
  - Mitigación: limitar a sugerencias breves y ejemplos puntuales
- Riesgo: acusaciones infundadas de IA/plagio
  - Mitigación: solo marcar como “revisar”, nunca afirmar con certeza

**Prompt Robusto para LLM (Sílabo Variable)**
- Objetivo del prompt: extraer rúbrica, criterios, pesos, escala y políticas de evaluación desde un PDF heterogéneo.
- Estrategia de robustez:
  - Forzar salida estructurada en JSON con campos obligatorios y opcionales.
  - Exigir citas internas (fragmento corto del texto fuente) por cada criterio.
  - Marcar incertidumbre y vacíos como `needs_confirmation: true`.
  - Detectar inconsistencias entre secciones y listarlas.
  - Proponer pesos solo si no aparecen; siempre marcarlos como sugeridos.
- Salida mínima esperada:
  - `course_name`, `scale_min`, `scale_max`
  - `criteria[]` con `name`, `weight`, `evidence`, `confidence`
  - `policies[]` (retrasos, penalidades, requisitos mínimos)
  - `open_questions[]` para el docente

**Plantilla de Prompt (Resumen)**
```text
Tarea: Analiza el sílabo y extrae criterios de evaluación y escala de calificación.
Devuelve SOLO JSON con el esquema definido.
Si un dato no aparece, usa null y agrega una pregunta en open_questions.
Incluye evidencia textual corta para cada criterio.
Marca conflictos entre secciones en inconsistencies.
No inventes información.
```

**Lectura de Sílabo (Texto vs. Imagen)**
- Si el PDF tiene texto embebido, se usa extracción directa (sin OCR).
- Si es escaneado o el texto es vacío, se usa OCR o un modelo con visión para extraer contenido.
- Siempre se guarda el texto extraído para auditoría y trazabilidad.

**Ejecución de Notebooks (Sandbox Ligero)**
- Ejecutar en carpeta temporal y registrar errores por celda.
- Timeout por ejecución y captura de trazas de error.
- El informe de ejecución alimenta el feedback y la nota.

**Sandbox en Contenedor (Docker)**
- Ejecución aislada con límites de CPU/memoria/red.
- Imagen base con dependencias mínimas y opción de imagen personalizada por curso.

**UI de Revisión Docente (Simple)**
- Listado de ejecuciones y vista de feedback.
- Edición de feedback y override de nota.
- Aprobación y registro de auditoría.

**Prompts Internos Recomendados (Estandarizados)**
- Entrada mínima:
  - Enunciado
  - Rúbrica (criterios + pesos)
  - Nivel del curso
  - Longitud esperada
  - Políticas (citas, estilo)
  - Texto/Notebook del alumno
- Salida estándar:
  - Puntajes por criterio (con evidencia)
  - Comentarios generales
  - Acciones priorizadas
  - “Para subir de X a Y, debe…”

**Integración con Blackboard (Flujo Práctico)**
- Acción “Generar feedback” en una entrega.
- Salidas:
  - Feedback listo para pegar.
  - Rúbrica sugerida compatible con Blackboard.
  - Resumen para el profe (evidencia + alertas).
- Dos versiones:
  - Estudiante: claro, motivador y accionable.
  - Docente: técnico, con evidencias y justificación de puntaje.

**Integración con Teams for Education**
- Bot/Tab “Revisión automática”.
- Comandos:
  - “/revisar estructura”
  - “/chequear rúbrica”
  - “/mejorar claridad sin cambiar contenido”
- Modo “pre‑entrega”: feedback formativo sin nota.

**Modo Sin Admin (Operación Manual)**
- Objetivo: trabajar sin permisos de administrador manteniendo consistencia y calidad.
- Blackboard Ultra:
  - Exportar gradebook a CSV.
  - Ejecutar el agente para generar nota final (0–20) y feedback por estudiante.
  - Importar el CSV actualizado con las notas.
  - Pegar feedback en comentarios del intento correspondiente.
- Teams for Education:
  - Usar el agente para producir feedback listo para pegar.
  - Pegar feedback en el campo de comentarios de la tarea.
  - Asignar la nota en la UI de Teams.
- Entregables del agente en modo manual:
  - `gradebook_updates.csv` con columnas de identificación y nota final.
  - `feedback_student.txt` (versión estudiante).
  - `feedback_instructor.txt` (versión docente).
  - `flags.csv` con alertas (plagio sospechoso, sin fuentes, no responde al enunciado).
- Convenciones mínimas:
  - Identificador único por estudiante (ID o email).
  - Mismo nombre de columna de nota en el CSV que el exportado por Blackboard.
  - Registro de fecha y versión de rúbrica en el output.

**Funcionalidades Avanzadas (Factibles)**
- Banco de errores recurrentes por curso (sin guardar contenido sensible).
- Feedback por audio (texto a voz).
- Comparación contra modelo de respuesta del profe (solo para evaluar cobertura).
- Checklist automático de requisitos (“menciona 3 autores”, “incluye tabla”, etc.).

**MVP en 2 Semanas (Realista)**
1. Cargar rúbrica + enunciado
2. Pegar texto del alumno (manual)
3. Salida: tabla de rúbrica + feedback + 3 mejoras prioritarias
4. Validaciones: tono, coherencia y evidencia
5. Exportar en formato listo para pegar en Blackboard/Teams

**Siguientes Pasos (Necesarios para continuar)**
1. Confirmar rúbrica y pesos por curso
2. Definir tipo de prácticas y criterios mínimos de aprobación
3. Definir formato de evidencias y estilo del feedback
