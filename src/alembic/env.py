from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Load .env if using environment variables
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Add app to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ✅ Import your models here so Alembic can detect them
from after_us import models  # ensures all models are loaded into SQLModel.metadata

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ SQLModel metadata
target_metadata = SQLModel.metadata


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Important for detecting column type changes
        )

        with context.begin_transaction():
            context.run_migrations()
