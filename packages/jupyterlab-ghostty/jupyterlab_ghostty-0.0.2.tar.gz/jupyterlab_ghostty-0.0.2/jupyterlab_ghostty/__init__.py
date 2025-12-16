"""JupyterLab terminal extension using ghostty-web (libghostty WASM)."""

try:
    from ._version import __version__
except ImportError:
    __version__ = "dev"


def _jupyter_labextension_paths():
    """Return the paths to the JupyterLab extension."""
    return [{"src": "labextension", "dest": "jupyterlab-ghostty"}]
