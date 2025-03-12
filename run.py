# homecloud/run.py
from app import create_app
from app.telegram_bot import start_tdlib, stop_tdlib # Import
import asyncio

app = create_app()

async def run_app():
    try:
        await start_tdlib()
        app.run(debug=True, host='0.0.0.0', port=8888, use_reloader=False)
    finally:
        await stop_tdlib()

if __name__ == '__main__':
    asyncio.run(run_app())