"""Onboarding configuration."""
import os

OUTPUT_DIR = os.getenv("ONBOARDING_OUTPUT_DIR", "output/onboarding")
DB_PATH = os.getenv("ONBOARDING_DB_PATH", f"{OUTPUT_DIR}/department.db")
