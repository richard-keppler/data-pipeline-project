import os
import sys

# Die Pipeline-Module importieren sich gegenseitig mit "from extract import ...".
# Damit das auch aus tests/ heraus klappt, kommt der Package-Ordner auf den Suchpfad.
PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "taxi_pipeline")
if PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PACKAGE_DIR)
