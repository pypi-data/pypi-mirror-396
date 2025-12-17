__version__ = "2.0.3"

# Allow CI/workflows to override version at runtime (does not affect setup.py parsing)
try:
    import os as _os
    _ver = _os.getenv("HLA_COMPASS_SDK_VERSION")
    if _ver:
        __version__ = _ver
except Exception:
    pass
