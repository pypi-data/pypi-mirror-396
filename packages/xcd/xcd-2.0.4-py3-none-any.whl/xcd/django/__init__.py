# xcd/__init__.py

# Drž tenhle soubor ultra-malý, žádné importy z xcd.core apod.
__all__ = ["__version__", "XCD_VERSION"]

# a) ruční fallback (můžeš přepsat číslo) 
DEFAULT_VER = "dev"

# b) pokus o načtení z balíčku (funguje, když je nainstalováno přes pip/poetry)
try:
    from importlib.metadata import version as _pkg_version  # Py3.8+
    __version__ = _pkg_version("xcd")
except Exception:
    __version__ = DEFAULT_VER

# c) export alias
XCD_VERSION = __version__
