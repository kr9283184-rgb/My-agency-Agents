"""Testing department configuration."""
import os

OUTPUT_DIR = os.getenv("QA_OUTPUT_DIR", "output/testing")
DB_PATH = os.getenv("QA_DB_PATH", f"{OUTPUT_DIR}/department.db")
