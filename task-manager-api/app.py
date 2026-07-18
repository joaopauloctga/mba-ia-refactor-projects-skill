"""Entry point. Delegates assembly to the application factory in src/app.py.

Run: `python seed.py` (once) then `python app.py`.
Config comes from environment variables — see .env.example.
"""
from src.app import create_app
from src.config.settings import settings

app = create_app()

if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
