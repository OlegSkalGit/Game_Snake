"""
3D Snake Adventure - Root Launch Proxy.
Ensures seamless execution whether run from repository root or via direct python command.
Redirects execution to scripts/main.py with all paths and assets configured.
"""
import sys
import runpy
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    main_script = SCRIPTS_DIR / "main.py"
    runpy.run_path(str(main_script), run_name="__main__")
