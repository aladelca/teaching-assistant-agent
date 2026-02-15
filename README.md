# MVP Agente de Corrección (Notebooks)

**Qué hace**
- Lee un notebook `.ipynb`, un enunciado y una rúbrica.
- Genera nota final (0–20) y feedback con evidencia.
- Produce salidas listas para modo “sin admin” (CSV + textos).

**Estructura**
- `mvp_agent/`: código del agente.
- `inputs/`: insumos (sílabos, enunciados, etc.).
- `outputs/`: resultados por ejecución.

**Requisitos**
- Python 3.10+
- `uv` (https://docs.astral.sh/uv/getting-started/installation/)
- Opcional para proveedor Codex auth: `codex` CLI

**Instalación directa sin clonar (tipo `curl | bash`)**
```bash
curl -fsSL https://raw.githubusercontent.com/aladelca/teaching-assistant-agent/master/scripts/install.sh | bash
```

Opcional:
- Instalar extras adicionales: `MVP_AGENT_EXTRAS='exec,agents,ui,browser' ...`
- Instalar también Codex CLI: `MVP_AGENT_INSTALL_CODEX=1 ...`

Ejemplo:
```bash
MVP_AGENT_EXTRAS='exec,agents' MVP_AGENT_INSTALL_CODEX=1 \
curl -fsSL https://raw.githubusercontent.com/aladelca/teaching-assistant-agent/master/scripts/install.sh | bash
```

Después de instalar:
```bash
mvp-agent --help
mvp-agent-batch --help
```

**Setup rápido con uv (recomendado)**
```bash
./scripts/bootstrap.sh
```
Si quieres incluir extras desde el inicio:
```bash
./scripts/bootstrap.sh agents ui browser
```

**Setup manual con uv**
```bash
uv sync --extra dev --extra exec
cp .env.example .env
```

**Extras opcionales**
- PDF texto: `uv sync --extra pdf`
- OCR (PDF escaneado): `uv sync --extra ocr`
- Ejecutar notebooks: `uv sync --extra exec`
- Agents SDK: `uv sync --extra agents`
- UI de revisión: `uv sync --extra ui`
- Browser Assist: `uv sync --extra browser`

Puedes combinar extras en un solo comando, por ejemplo:
```bash
uv sync --extra dev --extra exec --extra agents --extra ui
```

**Configuración de entorno y secretos**
1. Copia `.env.example` a `.env`.
2. Completa las variables según tu proveedor:
   - HTTP: `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_PAYLOAD_MODE`, `LLM_RESPONSE_PATH`
   - Agents SDK: `OPENAI_API_KEY`
   - Codex CLI (OpenAI Auth): `CODEX_MODEL` (opcional), `CODEX_REASONING_EFFORT` (opcional)
3. Nunca subas `.env` al repositorio.

Para GitHub Actions (CI/release), usa `Settings -> Secrets and variables -> Actions`:
- `OPENAI_API_KEY` (si tus tests/workflows lo requieren)
- `LLM_API_KEY` (si aplica)
- `PYPI_API_TOKEN` (opcional, solo si publicarás en PyPI)

Ver también:
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `docs/open-source-readiness-plan.md`
- `docs/release-checklist.md`
- `docs/release-ownership.md`
- `docs/operational-security.md`
- `docs/openclaw-integration.md`

**Personalización completa (prompts, flags y entorno)**

Para ver todas las opciones en tiempo real:
```bash
mvp-agent --help
mvp-agent-batch --help
syllabus-extract --help
review-ui --help
browser-assist --help
```

**1) Personalizar prompt de corrección**

Plantilla por defecto:
- `mvp_agent/prompts/evaluator_prompt.txt`

Variables disponibles en el prompt de corrección:
- `{student_id}`
- `{rubric_json}`
- `{assignment}`
- `{materials}`
- `{notebook_text}`
- `{execution_report}`

Ejemplo con prompt custom:
```bash
mvp-agent \
  --llm-provider codex \
  --model gpt-5 \
  --prompt /ruta/mi_evaluator_prompt.txt \
  --notebook /ruta/entrega.ipynb \
  --rubric /ruta/rubric.json \
  --assignment /ruta/assignment.txt \
  --materials /ruta/materials.txt \
  --student-id alumno@correo.com
```

Si instalaste sin clonar, puedes descargar el prompt base y editarlo:
```bash
curl -fsSL https://raw.githubusercontent.com/aladelca/teaching-assistant-agent/master/mvp_agent/prompts/evaluator_prompt.txt \
  -o ./mi_evaluator_prompt.txt
```

**2) Personalizar prompt de extracción de sílabo**

Plantilla por defecto:
- `mvp_agent/prompts/syllabus_prompt.txt`

Variable disponible:
- `{syllabus_text}`

Ejemplo:
```bash
syllabus-extract \
  --syllabus-pdf /ruta/silabo.pdf \
  --output /ruta/rubric.json \
  --llm-provider codex \
  --model gpt-5 \
  --prompt /ruta/mi_syllabus_prompt.txt
```

**3) Opciones configurables de `mvp-agent`**

- `--notebook` ruta al `.ipynb` (requerido).
- `--rubric` ruta a `rubric.json` (requerido).
- `--assignment` ruta a enunciado `.txt` (opcional).
- `--materials` ruta a material `.txt` (opcional).
- `--student-id` identificador del alumno (requerido).
- `--output-dir` carpeta base de salidas (default: `outputs`).
- `--gradebook-column` nombre de columna en CSV (default: `Final Score`).
- `--llm-provider` `mock|http|agents|codex`.
- `--model` modelo LLM.
- `--prompt` ruta de prompt custom de corrección.
- `--temperature` solo HTTP (default: `0.2`).
- `--max-tokens` solo HTTP (default: `1200`).
- `--execute-notebook` ejecuta antes de evaluar.
- `--exec-mode` `local|docker`.
- `--execution-timeout` timeout de ejecución en segundos.
- `--allow-exec-errors` permite errores de ejecución local.
- `--docker-image` imagen para ejecución en Docker.
- `--docker-cpus` CPUs para contenedor.
- `--docker-memory` memoria para contenedor.
- `--docker-network` red del contenedor.

**4) Opciones configurables de `mvp-agent-batch`**

- `--submissions-root` carpeta con un subdirectorio por alumno (requerido).
- `--student-key-regex` regex para validar carpeta de alumno.
- `--notebook-glob` patrón de búsqueda de notebooks por alumno.
- `--rubric`, `--assignment`, `--materials`.
- `--output-dir` carpeta de resultados de lote.
- `--summary-csv` nombre de CSV consolidado.
- `--gradebook-column` nombre de columna final.
- `--llm-provider`, `--model`, `--prompt`, `--temperature`, `--max-tokens`.
- `--execute-notebook`, `--exec-mode`, `--execution-timeout`, `--allow-exec-errors`.
- `--docker-image`, `--docker-cpus`, `--docker-memory`, `--docker-network`.

**5) Opciones configurables de `syllabus-extract`**

- `--syllabus-pdf` PDF de entrada (requerido).
- `--output` ruta de `rubric.json` (requerido).
- `--llm-provider` `agents|http|codex`.
- `--model` modelo LLM (requerido).
- `--ocr-mode` `auto|off|force`.
- `--max-pages` máximo de páginas para extracción.
- `--min-chars` mínimo de caracteres antes de activar OCR.
- `--prompt` prompt custom.
- `--diagnostics` archivo JSON con diagnóstico de extracción.

**6) Opciones configurables de `review-ui`**

- `--outputs-dir` carpeta de corridas.
- `--host` host bind (default `127.0.0.1`).
- `--port` puerto (default `5000`).
- `--auth-token-env` nombre de variable de entorno para token.

**7) Opciones configurables de `browser-assist`**

- `--config` JSON de pasos Playwright (requerido).
- `--output-dir` carpeta de outputs de una corrida (requerido).
- `--mode` `student|instructor`.
- `--headless` ejecuta sin UI.
- `--storage-state` sesión guardada de navegador.

**8) Variables de entorno configurables**

HTTP provider:
- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_PAYLOAD_MODE` (`messages` o `input`)
- `LLM_RESPONSE_PATH`

Agents SDK:
- `OPENAI_API_KEY`

Codex provider:
- `CODEX_MODEL`
- `CODEX_REASONING_EFFORT`

UI:
- `REVIEW_UI_TOKEN`

**9) Variables del instalador directo (`scripts/install.sh`)**

- `MVP_AGENT_PACKAGE_NAME` nombre del paquete (default `mvp-agent-correccion`).
- `MVP_AGENT_REPO_URL` URL git origen.
- `MVP_AGENT_EXTRAS` extras separados por coma (default `exec`).
- `MVP_AGENT_INSTALL_CODEX` `1` para instalar `@openai/codex` vía npm.

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
uv run python -m mvp_agent.cli \
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

uv run python -m mvp_agent.cli \
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
uv sync --extra agents
```

Ejemplo:
```bash
export OPENAI_API_KEY="tu_key"
uv run python -m mvp_agent.cli \
  --llm-provider agents \
  --model gpt-4.1 \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

**Ejecutar con Codex CLI (login OpenAI Auth, sin `OPENAI_API_KEY`)**
Requisitos:
- Tener `codex` instalado en tu máquina (`npm i -g @openai/codex`).
- Haber iniciado sesión: `codex login`.
- Si `codex login` falla por puerto local ocupado, usa: `codex login --device-auth`.

Ejemplo:
```bash
export CODEX_MODEL="gpt-5"
uv run python -m mvp_agent.cli \
  --llm-provider codex \
  --model gpt-5 \
  --notebook inputs/ejemplo.ipynb \
  --rubric examples/rubric.json \
  --assignment examples/assignment.txt \
  --materials examples/materials.txt \
  --student-id estudiante@correo.com
```

Notas:
- El proveedor `codex` usa `codex exec` internamente.
- Si no pasas `--model`, intenta `CODEX_MODEL` y luego `LLM_MODEL`.
- Por defecto fija `CODEX_REASONING_EFFORT=high` para compatibilidad.
- `OPENAI_API_KEY` sigue funcionando para el proveedor `agents`.

**Ejecutar notebook antes de evaluar**
```bash
uv run python -m mvp_agent.cli \
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
uv run python -m mvp_agent.cli \
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
uv run python -m mvp_agent.syllabus_cli \
  --syllabus-pdf inputs/silabos/mi_silabo.pdf \
  --output inputs/rubric.json \
  --llm-provider codex \
  --model gpt-5 \
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
uv run python -m mvp_agent.batch_cli \
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
uv run pytest
```

**Lint + build de paquete**
```bash
uv run ruff check .
uv run python -m build
uv run twine check dist/*
```

**Release por tag**
El workflow `release.yml` se ejecuta al crear tags `v*`:
```bash
git tag v0.1.0
git push origin v0.1.0
```
Siempre publica artefactos en GitHub Release y publica a PyPI solo si existe `PYPI_API_TOKEN`.

**UI simple de revisión**
```bash
uv run python -m mvp_agent.review_ui --outputs-dir outputs
```
Opcional: protege acceso con token:
```bash
export REVIEW_UI_TOKEN="cambia-este-token"
uv run python -m mvp_agent.review_ui --outputs-dir outputs
```
Luego usa `?token=<valor>` en la URL o header `X-Review-Token`.

**Browser Assist (sin credenciales)**
Este modo NO maneja contraseñas. Abre el navegador, tú inicias sesión y el script
ayuda a pegar feedback o subir el CSV.

Requiere Playwright:
```bash
uv sync --extra browser
uv run playwright install
```

Ejemplo Blackboard (subir CSV):
```bash
uv run python -m mvp_agent.browser_assist \
  --config examples/blackboard_steps.json \
  --output-dir outputs/estudiante@correo.com_20250211T000000Z
```

Ejemplo Teams (pegar feedback):
```bash
uv run python -m mvp_agent.browser_assist \
  --config examples/teams_steps.json \
  --output-dir outputs/estudiante@correo.com_20250211T000000Z
```

Puedes ajustar los selectores en los archivos JSON según la UI real.

## Licencia
MIT (`LICENSE`).
