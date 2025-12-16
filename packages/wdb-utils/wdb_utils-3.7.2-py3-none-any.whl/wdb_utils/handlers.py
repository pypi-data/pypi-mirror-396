from .connections import ( # Import your classes from the new connections file
    DatabaseConnection,
    OracleConnection,
    PostgresConnection,
    SnowflakeConnection
)
import pandas as pd
import os
import yaml
from pathlib import Path

def get_db_handler(db_key: str, config_file: str):
    """
    Factory function to return the correct DatabaseConnection handler.

    Args:
        db_key (str): The key for the database type (e.g., 'postgres', 'oracle').
        config_file (str): The path to the database configuration YAML file.

    Returns:
        DatabaseConnection: An instance of the correct database handler class.

    Raises:
        ValueError: If an unsupported database key is provided.
    """
    db_handlers = {
        'postgres': PostgresConnection,
        'oracle': OracleConnection,
        'snowflake': SnowflakeConnection,
    }

    if db_key not in db_handlers:
        raise ValueError(f"Unsupported database type: '{db_key}'. "
                         f"Supported types are: {', '.join(db_handlers.keys())}")

    if pd.isnull(config_file):
        config_file = os.path.join(Path.home(), 'configs', 'config-default.yml')

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found at '{config_file}'")

    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, yaml.FullLoader)

    return db_handlers[db_key](config, db_key)


# Backwards compatible global functions

def run_query_oracle(q, config=None):
    handler = get_db_handler('oracle', config)
    return handler.run_query(q)


def run_command_oracle(command, config=None):
    handler = get_db_handler('oracle', config)
    handler.run_command(command)


def load_data_oracle(data, schema, tablename, config=None):
    handler = get_db_handler('oracle', config)
    handler.load_dataframe(data, schema, tablename)


def run_query_snowflake(q, config=None):
    handler = get_db_handler('snowflake', config)
    return handler.run_query(q)


def run_command_snowflake(command, config=None):
    handler = get_db_handler('snowflake', config)
    handler.run_command(command)


def load_data_snowflake(data, schema, tablename, config=None):
    handler = get_db_handler('snowflake', config)
    handler.load_dataframe(data, schema, tablename)


def run_query_postgres(q, config=None):
    handler = get_db_handler('postgres', config)
    return handler.run_query(q)


def run_command_postgres(command, config=None):
    handler = get_db_handler('postgres', config)
    handler.run_command(command)


def load_data_postgres(data, schema, tablename, config=None):
    handler = get_db_handler('postgres', config)
    handler.load_dataframe(data, schema, tablename)


def replace_data_postgres(data, schema, tablename, config=None):
    """Replace data using PostgreSQL COPY command for optimal performance"""
    handler = get_db_handler('postgres', config)
    handler.replace_data(data, schema, tablename)


# Original generic functions for backwards compatibility
def run_query(q, config=None):
    return run_query_oracle(q, config)


def run_command(q, config=None):
    return run_command_oracle(q, config)


def load_data(data, schema, tablename, config=None):
    return load_data_oracle(data, schema, tablename, config)