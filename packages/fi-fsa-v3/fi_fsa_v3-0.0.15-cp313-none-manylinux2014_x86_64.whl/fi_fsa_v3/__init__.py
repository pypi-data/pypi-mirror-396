import sys
import os
import importlib.util
import glob


_pkg_dir = os.path.dirname(__file__)

if sys.platform.startswith("linux"):
    pattern = os.path.join(
        _pkg_dir, f"fi_fsa_v3.cpython-{sys.version_info.major}{sys.version_info.minor}*.so")
elif sys.platform.startswith("win"):
    pattern = os.path.join(
        _pkg_dir, f"fi_fsa_v3.cp{sys.version_info.major}{sys.version_info.minor}*.pyd")

_candidates = glob.glob(pattern)
if not _candidates:
    raise ImportError(
        f"Cannot find fi_fsa_v3 extension for Python {sys.version_info.major}.{sys.version_info.minor}")
_so_path = _candidates[0]

spec = importlib.util.spec_from_file_location("fi_fsa_v3", _so_path)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

globals().update(vars(_mod))
