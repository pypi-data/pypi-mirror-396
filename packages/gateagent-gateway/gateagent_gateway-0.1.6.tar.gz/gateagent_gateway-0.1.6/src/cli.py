# gate/ext/cli.py

"""Command-line entrypoints for the GateAgent gateway.

After installing the package, users can run:

    gateagent run

which starts the FastAPI backend on http://0.0.0.0:5001 and serves the
bundled web UI (if present in the installed package).
"""

import sys
from pathlib import Path

import uvicorn


def _ensure_local_modules_on_path() -> None:
    """Ensure sibling modules (server, routes, etc.) are importable.

    When installed as a package, our Python modules live under the same
    directory as this file (e.g. site-packages/src). Adding that directory
    to sys.path lets us import `server`, `routes`, etc. consistently in
    both development (repo checkout) and installed environments.
    """

    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))


def start() -> None:
    """Start the gateway backend (and serve the bundled UI if available)."""

    _ensure_local_modules_on_path()

    # Import after adjusting sys.path so this works for both `pip install`
    # and running directly from the repo checkout.
    from server import app  # type: ignore[import]

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        reload=False,
    )


def main() -> None:
    """CLI entrypoint for the ``gateagent`` command.

    Usage::

        gateagent run
    """

    args = sys.argv[1:]
    cmd = args[0] if args else "run"

    if cmd in {"run", "start", "serve"}:
        start()
    elif cmd in {"-h", "--help", "help"}:
        print("Usage: gateagent [run]", file=sys.stdout)
        print("\nStarts the GateAgent backend and bundled UI (if available).", file=sys.stdout)
    else:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Usage: gateagent [run]", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
