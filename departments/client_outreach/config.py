"""Client outreach configuration."""
import os

OUTPUT_DIR = os.getenv("OUTREACH_OUTPUT_DIR", "output/client_outreach")
DB_PATH = os.getenv("OUTREACH_DB_PATH", f"{OUTPUT_DIR}/department.db")
