import argparse
import json
import os
from datetime import datetime

from flask import Flask, redirect, render_template_string, request, url_for


TEMPLATE_INDEX = """
<!doctype html>
<html>
  <head>
    <title>Revision de Feedback</title>
  </head>
  <body>
    <h1>Revision de Feedback</h1>
    <ul>
    {% for run in runs %}
      <li><a href="{{ url_for('review', run_id=run) }}">{{ run }}</a></li>
    {% endfor %}
    </ul>
  </body>
</html>
"""


TEMPLATE_REVIEW = """
<!doctype html>
<html>
  <head>
    <title>Revisar {{ run_id }}</title>
    <style>
      textarea { width: 100%; height: 180px; }
      input[type=text] { width: 100%; }
      .box { margin-bottom: 16px; }
    </style>
  </head>
  <body>
    <h1>Revisar {{ run_id }}</h1>
    <div class="box">
      <strong>Nota final:</strong> {{ final_score }}
    </div>
    <form method="post" action="{{ url_for('approve', run_id=run_id) }}">
      <div class="box">
        <label>Override de nota (opcional)</label>
        <input type="text" name="final_score_override" value="{{ final_score }}">
      </div>
      <div class="box">
        <label>Feedback estudiante</label>
        <textarea name="feedback_student">{{ feedback_student }}</textarea>
      </div>
      <div class="box">
        <label>Feedback docente</label>
        <textarea name="feedback_instructor">{{ feedback_instructor }}</textarea>
      </div>
      <div class="box">
        <label>Aprobado por</label>
        <input type="text" name="approved_by" value="">
      </div>
      <button type="submit">Aprobar y guardar</button>
    </form>
    <p><a href="{{ url_for('index') }}">Volver</a></p>
  </body>
</html>
"""


def _read_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_app(outputs_dir):
    app = Flask(__name__)

    @app.route("/")
    def index():
        if not os.path.exists(outputs_dir):
            runs = []
        else:
            runs = sorted(
                [
                    name
                    for name in os.listdir(outputs_dir)
                    if os.path.isdir(os.path.join(outputs_dir, name))
                ],
                reverse=True,
            )
        return render_template_string(TEMPLATE_INDEX, runs=runs)

    @app.route("/review/<run_id>")
    def review(run_id):
        run_path = os.path.join(outputs_dir, run_id)
        evaluation = _read_json(os.path.join(run_path, "evaluation.json"))
        feedback_student = _read_text(os.path.join(run_path, "feedback_student.txt"))
        feedback_instructor = _read_text(
            os.path.join(run_path, "feedback_instructor.txt")
        )
        return render_template_string(
            TEMPLATE_REVIEW,
            run_id=run_id,
            final_score=evaluation.get("final_score", 0),
            feedback_student=feedback_student,
            feedback_instructor=feedback_instructor,
        )

    @app.route("/approve/<run_id>", methods=["POST"])
    def approve(run_id):
        run_path = os.path.join(outputs_dir, run_id)
        approved = {
            "approved_at": datetime.utcnow().isoformat() + "Z",
            "approved_by": request.form.get("approved_by") or "unknown",
            "final_score_override": request.form.get("final_score_override"),
            "feedback_student": request.form.get("feedback_student", ""),
            "feedback_instructor": request.form.get("feedback_instructor", ""),
        }
        with open(os.path.join(run_path, "approved.json"), "w", encoding="utf-8") as f:
            json.dump(approved, f, ensure_ascii=False, indent=2)
        return redirect(url_for("review", run_id=run_id))

    return app


def main():
    ap = argparse.ArgumentParser(description="UI simple para revision y aprobacion")
    ap.add_argument("--outputs-dir", default="outputs", help="Directorio de salidas")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()

    app = create_app(args.outputs_dir)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
