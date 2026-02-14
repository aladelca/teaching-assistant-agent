FROM python:3.11-slim

WORKDIR /work
RUN python -m pip install --no-cache-dir nbclient nbformat ipykernel

ENTRYPOINT ["python", "/runner/execute_nb.py"]
