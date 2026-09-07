"""Security configuration."""
import os

OUTPUT_DIR = os.getenv("SECURITY_OUTPUT_DIR", "output/security")
DB_PATH = os.getenv("SECURITY_DB_PATH", f"{OUTPUT_DIR}/department.db")
