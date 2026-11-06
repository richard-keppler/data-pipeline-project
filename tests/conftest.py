import os
import sys

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "taxi_pipeline")
if PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PACKAGE_DIR)
