---
name: mvp_notebook_grader
description: Grade notebooks with mvp-agent and produce evaluation artifacts (JSON, feedback, CSV).
homepage: https://github.com/aladelca/teaching-assistant-agent
metadata: {"openclaw":{"emoji":"🧪","requires":{"bins":["mvp-agent","mvp-agent-batch"]}}}
---

# MVP Notebook Grader Skill

Use this skill when the user asks to grade one notebook or a folder of notebook submissions.

## Single notebook grading

Collect these required inputs:
- notebook path
- rubric path
- student id

Optional inputs:
- assignment path
- materials path
- output dir (default `./outputs_openclaw`)
- provider (`mock`, `http`, `agents`, `codex`)
- model (required for `http`, `agents`, `codex`)
- custom prompt path
- execute notebook before grading

Run with `exec` using `mvp-agent`.

Command template:
```bash
mvp-agent \
  --llm-provider <provider> \
  --notebook "<notebook_path>" \
  --rubric "<rubric_path>" \
  --student-id "<student_id>" \
  --output-dir "<output_dir>"
```

Append optional flags only when provided:
- `--assignment "<assignment_path>"`
- `--materials "<materials_path>"`
- `--model "<model>"`
- `--prompt "<prompt_path>"`
- `--execute-notebook`
- `--exec-mode <local|docker>`
- `--execution-timeout <seconds>`
- `--allow-exec-errors`
- `--docker-image "<image>"`
- `--docker-cpus "<cpus>"`
- `--docker-memory "<memory>"`
- `--docker-network "<network>"`

After execution, report:
- final output folder from `OK: outputs in ...`
- key artifacts generated (`evaluation.json`, `feedback_student.txt`, `gradebook_updates.csv`)

## Batch grading

Collect required inputs:
- submissions root
- rubric path

Optional:
- assignment/materials
- output dir (default `./outputs_batch_openclaw`)
- provider/model/prompt

Run with `exec` using `mvp-agent-batch`.

Command template:
```bash
mvp-agent-batch \
  --submissions-root "<submissions_root>" \
  --rubric "<rubric_path>" \
  --output-dir "<output_dir>"
```

Append optional flags when provided:
- `--assignment "<assignment_path>"`
- `--materials "<materials_path>"`
- `--llm-provider <provider>`
- `--model "<model>"`
- `--prompt "<prompt_path>"`
- `--summary-csv "<filename>"`
- execution flags (`--execute-notebook`, docker flags, timeout)

## Safety and behavior

- Never invent missing file paths; ask the user.
- Quote every path argument.
- If provider is `codex` and auth fails, tell user to run `codex login --device-auth`.
- Prefer `mock` provider when user wants a dry run or has no credentials configured.
