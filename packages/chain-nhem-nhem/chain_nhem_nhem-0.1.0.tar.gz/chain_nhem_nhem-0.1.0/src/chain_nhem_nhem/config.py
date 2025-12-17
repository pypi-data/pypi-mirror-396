import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()

        self.DRIVER = os.getenv("DRIVER", "gemini")

        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

        self.LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", "INFO").upper()

        self.APP_TOOLS_PATH = os.getenv("APP_TOOLS_PATH")
        self.APP_DRIVERS_PATH = os.getenv("APP_DRIVERS_PATH")

        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.MODEL = os.getenv("MODEL", "gemini-2.5-flash")


settings = Settings()
