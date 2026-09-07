"""Web development configuration."""
import os

OUTPUT_DIR = os.getenv("WEB_OUTPUT_DIR", "output/web_development")
DB_PATH = os.getenv("WEB_DB_PATH", f"{OUTPUT_DIR}/department.db")
