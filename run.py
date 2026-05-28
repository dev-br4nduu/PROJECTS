#!/usr/bin/env python3
"""Script para rodar o Jarvis"""

from jarvis.app import app
from jarvis.config import Config

if __name__ == "__main__":
    print(f"🤖 Starting Jarvis on {Config.HOST}:{Config.PORT}")
    print(f"📡 Visit http://localhost:{Config.PORT} in your browser")

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
