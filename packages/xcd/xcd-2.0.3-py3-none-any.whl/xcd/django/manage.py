import os
import sys

# === Dynamicky najdi cestu ke "core" ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CORE_DIR = os.path.join(BASE_DIR, 'core')

# Přidej BASE_DIR i CORE_DIR do sys.path
for path in [BASE_DIR, CORE_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Ujisti se, že reloader i podprocesy znají PYTHONPATH
os.environ["PYTHONPATH"] = os.pathsep.join([BASE_DIR, CORE_DIR, os.environ.get("PYTHONPATH", "")])

# === Django standard ===
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcdweb.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()