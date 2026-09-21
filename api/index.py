import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent / 'expense'
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense.settings')

from expense.wsgi import application

app = application