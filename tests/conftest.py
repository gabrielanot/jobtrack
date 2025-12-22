from pathlib import Path
import sys

# ensure project root is on sys.path so tests can import app module
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app import Base, engine  # adjust import based on your codebase

def setup_module(module):
    Base.metadata.create_all(bind=engine)  # creates tables