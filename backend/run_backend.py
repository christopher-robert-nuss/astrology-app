import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn
import main

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(main.app, host="127.0.0.1", port=port)
