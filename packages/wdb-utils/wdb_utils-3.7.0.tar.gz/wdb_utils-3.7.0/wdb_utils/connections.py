import abc
import getpass
from contextlib import contextmanager
import pandas as pd
from importlib import import_module

class DatabaseConnection(abc.ABC):
    """Abstract base class for all database connection handlers."""

    def __init__(self, config: dict, db_key: str):
        self.config = config
        self.db_key = db_key
        self.db_config = self.config.get(db_key, {})

    @abc.abstractmethod
    def _create_connection(self):
        """Creates a database-specific connection object."""
        pass

    @contextmanager
    def connect(self):
        """A context manager to manage database connections."""
        connection = None
        try:
            connection = self._create_connection()
            yield connection
        except Exception as e:
            raise ConnectionError(f"Error creating database connection for '{self.db_key}': {e}") from e
        finally:
            if connection:
                connection.close()

    def run_query(self, query: str, fetch_ct: int = 1000000) -> pd.DataFrame:
        """Runs a SQL query and returns the results as a Pandas DataFrame."""
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query)
                results = []
                while True:
                    rows = cursor.fetchmany(fetch_ct)
                    if not rows:
                        break
                    results.extend(rows)

                if not cursor.description:
                    return pd.DataFrame()

                cols = [col[0] for col in cursor.description]
                return pd.DataFrame(results, columns=cols)
            except Exception as e:
                raise RuntimeError(f"Database query failed: {e}") from e

    def run_command(self, command: str):
        """Runs a SQL command and commits the changes."""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(command)
                except Exception as e:
                    connection.rollback()
                    raise RuntimeError(f"Database command failed: {e}") from e
                connection.commit()

    @abc.abstractmethod
    def load_dataframe(self, data: pd.DataFrame, schema: str, tablename: str):
        """Loads a Pandas DataFrame into a database table."""
        pass


class OracleConnection(DatabaseConnection):
    def __init__(self, config: dict, db_key: str):
        super().__init__(config, db_key)
        self.oracledb = import_module('oracledb')
        self.oracledb.defaults.fetch_lobs = False
        if self.db_config.get('mode', 'thin') == 'thick':
            self.oracledb.init_oracle_client()

    def _create_connection(self):
        pwd = self.db_config.get('password') or getpass.getpass('Database password: ')
        return self.oracledb.connect(
            user=self.db_config['username'],
            password=pwd,
            dsn=self.db_config['host']
        )

    def load_dataframe(self, data: pd.DataFrame, schema: str, tablename: str):
        inserted_data = [[None if pd.isnull(v) else v for v in row] for row in data.values.tolist()]
        sql = (f'INSERT INTO {schema}.{tablename} ({", ".join(data.columns)}) '
               f'VALUES ({", ".join([f":{i}" for i in range(1, len(data.columns) + 1)])})')

        with self.connect() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.executemany(sql, inserted_data)
                    connection.commit()
                except self.oracledb.DatabaseError as e:
                    connection.rollback()
                    raise RuntimeError(f"Oracle data load failed: {e}") from e


class SnowflakeConnection(DatabaseConnection):
    def __init__(self, config: dict, db_key: str):
        super().__init__(config, db_key)
        self.snow_connect = import_module('snowflake.connector')
        self.snow_connect.paramstyle = 'numeric'

    def _create_connection(self):
        pwd = self.db_config.get('password') or getpass.getpass('Database password: ')
        return self.snow_connect.connect(
            user=self.db_config['username'],
            password=pwd,
            account=self.db_config['account'],
            database=self.db_config['database'],
            schema=self.db_config['schema']
        )

    def load_dataframe(self, data: pd.DataFrame, schema: str, tablename: str):
        from snowflake.connector.pandas_tools import write_pandas
        data.columns = map(str.upper, data.columns)
        with self.connect() as connection:
            try:
                write_pandas(connection, data, tablename, schema=schema)
            except Exception as e:
                raise RuntimeError(f"Snowflake data load failed: {e}") from e


class PostgresConnection(DatabaseConnection):
    def __init__(self, config: dict, db_key: str):
        super().__init__(config, db_key)
        self.pg_mod = import_module('psycopg2')
        self.pg_mod_sql = import_module('psycopg2.sql')

    def _create_connection(self):
        pwd = self.db_config.get('password') or getpass.getpass('Database password: ')
        conn = self.pg_mod.connect(
            user=self.db_config['username'],
            password=pwd,
            host=self.db_config['host'],
            dbname=self.db_config['database'],
            port=self.db_config['port']
        )
        from psycopg2 import extensions
        dec2_float = extensions.new_type(extensions.DECIMAL.values, 'DEC2FLOAT',
                                        lambda v, cur: None if v is None else float(v))
        extensions.register_type(dec2_float, conn)
        return conn

    def load_dataframe(self, data: pd.DataFrame, schema: str, tablename: str):
        inserted_data = [[None if pd.isnull(v) else v for v in row] for row in data.values.tolist()]
        columns = self.pg_mod_sql.SQL(', ').join(self.pg_mod_sql.Identifier(col) for col in data.columns)
        placeholders = self.pg_mod_sql.SQL(', ').join(self.pg_mod_sql.Placeholder() for _ in data.columns)
        insert_stmt = self.pg_mod_sql.SQL('INSERT INTO {}.{} ({}) VALUES ({})').format(
            self.pg_mod_sql.Identifier(schema),
            self.pg_mod_sql.Identifier(tablename),
            columns,
            placeholders
        )

        with self.connect() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.executemany(insert_stmt, inserted_data)
                    conn.commit()
                except self.pg_mod.DatabaseError as e:
                    conn.rollback()
                    raise RuntimeError(f"Postgres data load failed: {e}") from e

    def replace_data(self, data: pd.DataFrame, schema: str, table: str):
        """Replace table data using PostgreSQL COPY command for optimal performance"""
        from io import StringIO
        
        temp_table_name = f"{table}_temp"
        with self.connect() as conn:
            with conn.cursor() as cur:
                try:
                    # Create temp table
                    cur.execute(self.pg_mod_sql.SQL("DROP TABLE IF EXISTS {temp}").format(
                        temp=self.pg_mod_sql.Identifier(temp_table_name)))
                    cur.execute(
                        self.pg_mod_sql.SQL("CREATE TEMP TABLE {temp} (LIKE {schema}.{table} INCLUDING ALL)").format(
                            temp=self.pg_mod_sql.Identifier(temp_table_name), 
                            schema=self.pg_mod_sql.Identifier(schema),
                            table=self.pg_mod_sql.Identifier(table)))
                    
                    # Use COPY to load data into temp table (much faster than INSERT)
                    buffer = StringIO()
                    data.to_csv(buffer, index=False, header=False, na_rep='\\N')
                    buffer.seek(0)
                    
                    columns = self.pg_mod_sql.SQL(', ').join(
                        self.pg_mod_sql.Identifier(c) for c in data.columns)
                    copy_sql = self.pg_mod_sql.SQL("COPY {temp} ({cols}) FROM STDIN WITH CSV NULL '\\N'").format(
                        temp=self.pg_mod_sql.Identifier(temp_table_name),
                        cols=columns)
                    
                    cur.copy_expert(copy_sql, buffer)
                    
                    # Replace data in target table
                    cur.execute(self.pg_mod_sql.SQL("DELETE FROM {schema}.{table}").format(
                        schema=self.pg_mod_sql.Identifier(schema), 
                        table=self.pg_mod_sql.Identifier(table)))
                    cur.execute(
                        self.pg_mod_sql.SQL("INSERT INTO {schema}.{table} ({cols}) SELECT {cols} FROM {temp}").format(
                            schema=self.pg_mod_sql.Identifier(schema), 
                            table=self.pg_mod_sql.Identifier(table),
                            cols=columns, 
                            temp=self.pg_mod_sql.Identifier(temp_table_name)))
                    
                    cur.execute(self.pg_mod_sql.SQL("DROP TABLE IF EXISTS {temp}").format(
                        temp=self.pg_mod_sql.Identifier(temp_table_name)))
                    conn.commit()
                except self.pg_mod.DatabaseError as e:
                    conn.rollback()
                    raise RuntimeError(f"Postgres data replacement failed: {e}") from e