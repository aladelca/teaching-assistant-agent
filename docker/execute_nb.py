import sys


def execute(input_path, output_path, timeout_sec):
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(input_path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=timeout_sec,
        allow_errors=False,
        kernel_name="python3",
        resources={"metadata": {"path": "/work"}},
    )
    client.execute()
    nbformat.write(nb, output_path)


def main():
    if len(sys.argv) < 4:
        raise SystemExit("Usage: execute_nb.py <input> <output> <timeout>")
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    timeout_sec = int(sys.argv[3])
    execute(input_path, output_path, timeout_sec)


if __name__ == "__main__":
    main()
