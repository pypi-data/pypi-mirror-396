from setuptools import setup
setup(
    name='wdb_utils',
    version='3.7.0',
    author='Courtney Wade',
    description='Utilities for querying and loading data into an Oracle, Snowflake, or Postgres database.',
    long_description='Utilities for querying and loading data into an Oracle, Snowflake, or Postgres database. Queries return to pandas dataframes. Faster than SQLAlchemy.',
    url='https://github.com/cwade/wdb_utils',
    keywords='pandas, oracle, query',
    python_requires='>=3.7, <4',
    install_requires=[
        'oracledb>=1.2',
        'pandas>=2.0',
        'PyYAML>=6.0',
        'snowflake-connector-python>=3.15.0',
        'psycopg2-binary'
    ]
)
