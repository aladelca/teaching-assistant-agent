# Integración con OpenClaw (sin clonar)

Esta guía conecta `mvp-agent` con OpenClaw para que el agente de OpenClaw ejecute correcciones de notebooks usando la herramienta `exec`.

## Arquitectura (resumen)

- `mvp-agent` corre como binario en la máquina del Gateway.
- OpenClaw llama ese binario vía tool `exec`.
- Un skill (`mvp_notebook_grader`) estandariza cómo invocarlo.

## 1) Preparar este proyecto (lado `teaching_assistant`)

Instala el agente como herramienta global, sin clonar:

```bash
curl -fsSL https://raw.githubusercontent.com/aladelca/teaching-assistant-agent/master/scripts/install.sh | bash
```

Verifica:

```bash
mvp-agent --help
mvp-agent-batch --help
```

Si usarás proveedor `codex`:

```bash
npm i -g @openai/codex
codex login --device-auth
```

## 2) Habilitar herramientas en OpenClaw

Asegura que el agente pueda usar runtime + filesystem:

```bash
openclaw config set tools.profile coding
openclaw config set tools.allow '["group:runtime","group:fs","group:sessions","session_status"]'
```

## 3) Instalar el skill en workspace de OpenClaw

### Opción A: desde este repo local

```bash
WORKSPACE="$(openclaw config get agents.defaults.workspace)"
mkdir -p "$WORKSPACE/skills/mvp_notebook_grader"
cp ./openclaw/skills/mvp_notebook_grader/SKILL.md "$WORKSPACE/skills/mvp_notebook_grader/SKILL.md"
```

### Opción B: sin clonar (descarga directa)

```bash
WORKSPACE="$(openclaw config get agents.defaults.workspace)"
mkdir -p "$WORKSPACE/skills/mvp_notebook_grader"
curl -fsSL https://raw.githubusercontent.com/aladelca/teaching-assistant-agent/master/openclaw/skills/mvp_notebook_grader/SKILL.md \
  -o "$WORKSPACE/skills/mvp_notebook_grader/SKILL.md"
```

Crea una sesión nueva en OpenClaw para que tome snapshot actualizado de skills.

## 4) Aprobar ejecución de binarios (modo recomendado)

OpenClaw puede pedir aprobación para ejecutar comandos host. Permite solo lo necesario:

```bash
openclaw approvals allowlist add --gateway "$(which mvp-agent)"
openclaw approvals allowlist add --gateway "$(which mvp-agent-batch)"
openclaw approvals allowlist add --gateway "$(which codex)"
```

En OpenClaw Control, deja `exec` en modo seguro (`allowlist`) para evitar ejecución arbitraria.

## 5) Uso desde chat de OpenClaw

### Corrección individual

Prompt sugerido:

```text
Usa el skill mvp_notebook_grader.
Corrige este notebook:
- notebook: /abs/path/sample.ipynb
- rubric: /abs/path/rubric.json
- assignment: /abs/path/assignment.txt
- materials: /abs/path/materials.txt
- student_id: alumno@correo.com
- provider: codex
- model: gpt-5
- output_dir: /abs/path/outputs_openclaw
```

### Corrección por lote

```text
Usa el skill mvp_notebook_grader en modo batch.
- submissions_root: /abs/path/submissions
- rubric: /abs/path/rubric.json
- assignment: /abs/path/assignment.txt
- materials: /abs/path/materials.txt
- provider: mock
- output_dir: /abs/path/outputs_batch_openclaw
```

## 6) Troubleshooting rápido

- `command not found: mvp-agent`
  - Ejecuta `uv tool update-shell` y abre nueva terminal.
- `Codex CLI no está autenticado`
  - Ejecuta `codex login --device-auth`.
- `Permission denied` en OpenClaw
  - Revisa `tools.allow` y allowlist de approvals.
- Paths relativos no encontrados
  - Usa rutas absolutas en el prompt de OpenClaw.
