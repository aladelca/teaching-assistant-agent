# MVP Agente de Corrección (Notebooks)

**Qué hace**
- Lee un notebook `.ipynb`, un enunciado y una rúbrica.
- Genera nota final (0–20) y feedback con evidencia.
- Produce salidas listas para modo “sin admin” (CSV + textos).

**Estructura**
- `mvp_agent/`: código del agente.
- `inputs/`: insumos (sílabos, enunciados, etc.).
- `outputs/`: resultados por ejecución.

**Setup rápido (recomendado)**
```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

**Extras opcionales**
- PDF texto: `.venv/bin/pip install '.[pdf]'`
- OCR (PDF escaneado): `.venv/bin/pip install '.[ocr]'`
- Ejecutar notebooks: `.venv/bin/pip install '.[exec]'`
- Agents SDK: `.venv/bin/pip install '.[agents]'`
- UI de revisión: `.venv/bin/pip install '.[ui]'`

**Rúbrica (JSON)**
```json
{
  "course": "Curso X",
  "scale": {"min": 0, "max": 20},
  "criteria": [
    {"name": "Correctitud técnica", "weight": 0.4, "description": "Resultados correctos"},
    {"name": "Razonamiento", "weight": 0.3, "description": "Explicaciones claras"},
    {"name": "Análisis", "weight": 0.2, "description": "Conclusiones sólidas"},
    {"name": "Presentación", "weight": 0.1, "description": "Orden y claridad"}
  ],
  "policies": {"late_penalty": "5% por día"}
}
```

**Ejecutar en modo mock (sin LLM)**
```bash
python3 -m mvp_agent.cli \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

**Ejecutar con LLM (HTTP)**
Requiere variables de entorno:
- `LLM_API_URL`
- `LLM_API_KEY` (si aplica)
- `LLM_MODEL`
- `LLM_PAYLOAD_MODE` (`messages` o `input`)
- `LLM_RESPONSE_PATH` (ruta al texto en la respuesta JSON)

Ejemplo:
```bash
export LLM_API_URL="https://tu-endpoint"
export LLM_MODEL="tu-modelo"
export LLM_PAYLOAD_MODE="messages"
export LLM_RESPONSE_PATH="choices.0.message.content"

python3 -m mvp_agent.cli \
  --llm-provider http \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

**Ejecutar con OpenAI Agents SDK**
Requiere instalar el SDK oficial:
```bash
.venv/bin/pip install '.[agents]'
```

Ejemplo:
```bash
export OPENAI_API_KEY="tu_key"
python3 -m mvp_agent.cli \
  --llm-provider agents \
  --model gpt-4.1 \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

**Ejecutar notebook antes de evaluar**
```bash
python3 -m mvp_agent.cli \
  --execute-notebook \
  --execution-timeout 120 \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

**Ejecución de notebooks en contenedor (Docker)**
1. Construir imagen:
```bash
docker build -t mvp-notebook-exec:latest docker
```

2. Ejecutar evaluación con Docker:
```bash
python3 -m mvp_agent.cli \
  --execute-notebook \
  --exec-mode docker \
  --docker-image mvp-notebook-exec:latest \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

**Extraer rúbrica desde sílabo PDF**
```bash
python3 -m mvp_agent.syllabus_cli \
  --syllabus-pdf inputs/silabos/mi_silabo.pdf \
  --output inputs/rubric.json \
  --llm-provider agents \
  --model gpt-4.1 \
  --diagnostics outputs/syllabus_diagnostics.json
```

**Salidas**
- `context_package.json`
- `evaluation.json`
- `validation.json`
- `feedback_student.txt`
- `feedback_instructor.txt`
- `gradebook_updates.csv`
- `flags.csv` (si aplica)

## Corrección por lote (carpetas `apellidos_nombres`)
Estructura esperada:
```bash
submissions/
  perez_juan/
    entrega.ipynb
  garcia_maria/
    notebook.ipynb
```

Ejecutar lote (mock):
```bash
python3 -m mvp_agent.batch_cli \
  --submissions-root submissions \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --output-dir outputs_batch
```

Resultados de lote:
- `outputs_batch/gradebook_summary.csv` (resumen consolidado)
- `outputs_batch/batch_report.json` (métricas de ejecución)
- carpetas individuales por alumno con evidencias completas (igual que `mvp_agent.cli`)

## Procesamiento por correo (IMAP + SMTP)
Flujo soportado:
1. Lee correos no leídos del buzón.
2. Descarga adjuntos.
3. Detecta insumos opcionales por nombre de archivo:
   - `rubric.json` (sobrescribe rúbrica por defecto)
   - `assignment.txt` o `enunciado.txt` (sobrescribe enunciado)
   - `materials.txt` o `materiales.txt` (sobrescribe materiales)
   - `students.csv` / `roster.csv` / `alumnos.csv` (mapeo alumno↔archivo)
4. Procesa entregas en `.zip` y/o `.ipynb`.
5. Ejecuta corrección por lote.
6. Responde al remitente con `gradebook_summary.csv` adjunto.

Sugerencia de asunto para override de enunciado:
- `Entrega parcial [assignment:ruta/o/url/del/enunciado]`

Formato recomendado para roster CSV:
```csv
student_id,student_name,expected_filename
2026001,Juan Perez,perez_juan_tarea1.ipynb
2026002,Maria Garcia,garcia_maria_tarea1.ipynb
```

Variables de entorno mínimas:
- `EMAIL_IMAP_HOST`
- `EMAIL_IMAP_USER`
- `EMAIL_IMAP_PASSWORD`
- `EMAIL_SMTP_HOST`
- `EMAIL_SMTP_PORT` (default 465)
- `EMAIL_SMTP_USER`
- `EMAIL_SMTP_PASSWORD`

Ejemplo:
```bash
export EMAIL_IMAP_HOST="imap.gmail.com"
export EMAIL_IMAP_USER="agent@example.com"
export EMAIL_IMAP_PASSWORD="app_password"
export EMAIL_SMTP_HOST="smtp.gmail.com"
export EMAIL_SMTP_PORT="465"
export EMAIL_SMTP_USER="agent@example.com"
export EMAIL_SMTP_PASSWORD="app_password"

python3 -m mvp_agent.email_cli \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --output-dir outputs_email
```

Para habilitar parseo del texto del correo con LLM:
```bash
python3 -m mvp_agent.email_cli \
  --llm-provider http \
  --model tu-modelo \
  --email-body-llm-parse \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --output-dir outputs_email
```

**Tests**
```bash
.venv/bin/python -m pytest
```

**UI simple de revisión**
```bash
python3 -m mvp_agent.review_ui --outputs-dir outputs
```

**Browser Assist (sin credenciales)**
Este modo NO maneja contraseñas. Abre el navegador, tú inicias sesión y el script
ayuda a pegar feedback o subir el CSV.

Requiere Playwright:
```bash
.venv/bin/pip install '.[browser]'
.venv/bin/playwright install
```

Ejemplo Blackboard (subir CSV):
```bash
python3 -m mvp_agent.browser_assist \
  --config examples/blackboard_steps.json \
  --output-dir outputs/estudiante@correo.com_20250211T000000Z
```

Ejemplo Teams (pegar feedback):
```bash
python3 -m mvp_agent.browser_assist \
  --config examples/teams_steps.json \
  --output-dir outputs/estudiante@correo.com_20250211T000000Z
```

Puedes ajustar los selectores en los archivos JSON según la UI real.
