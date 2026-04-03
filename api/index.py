import sys
import traceback
from fastapi import FastAPI

# Create app FIRST so Vercel can detect it
app = FastAPI()

try:
    from app.main import app as real_app
    app = real_app
    print("App imported successfully", file=sys.stderr)

except Exception as e:
    print(f"Error importing app: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)

    @app.get("/")
    def error_root():
        return {
            "error": "App failed to load",
            "details": str(e)
        }