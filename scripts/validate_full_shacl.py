"""Optional independent SHACL validation: pip install pyshacl, then run this file.
Not required by the default offline teaching lab; not verified in the build environment.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
    from pyshacl import validate
except ImportError:
    raise SystemExit('Optional dependency missing: install an approved pyshacl version first.')
from backend.build import load_dataset, ROOT
conforms,report,text=validate(load_dataset(),shacl_graph=str(ROOT/'ontology'/'shapes.ttl'),inference='none')
print(text)
raise SystemExit(0 if conforms else 1)  # Baseline intentionally exits 1 (missing channel unit).
