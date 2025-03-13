# homecloud/run.py
from app import create_app
from app.telegram_bot import start_tdlib, stop_tdlib # Import
import asyncio
import os

app = create_app()

async def run_app():
    try:
        await start_tdlib()
        app.run(
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        host='0.0.0.0',
        port=int(os.getenv("APP_PORT", 5000)),  # Default to 5000
        use_reloader=os.getenv("USE_RELOADER", "0") == "1"
    )
    finally:
        await stop_tdlib()

if __name__ == '__main__':
    asyncio.run(run_app())