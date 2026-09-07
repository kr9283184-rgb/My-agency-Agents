"""Lead generation configuration."""
import os

OUTPUT_DIR = os.getenv("LEAD_GEN_OUTPUT_DIR", "output/lead_generation")
DB_PATH = os.getenv("LEAD_GEN_DB_PATH", f"{OUTPUT_DIR}/department.db")
