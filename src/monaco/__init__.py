from .monaco_widget import MonacoWidget


def _pyinstaller_hooks_dir():
    from pathlib import Path
    return [str(Path(__file__).with_name("_pyinstaller").resolve())]