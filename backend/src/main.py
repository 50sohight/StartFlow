import sys
from pathlib import Path
from src.config import settings

sys.path.append(str(Path(__file__).parent.parent))


if "__main__" == __name__:
    print(settings.DB_URL)