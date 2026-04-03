import sys
import traceback

try:
    from app.main import app
    print("App imported successfully", file=sys.stderr)
except Exception as e:
    print(f"Error importing app: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

# Vercel expects the app to be named 'app'
# This is the entry point for the serverless function