# wdb_utils
Utilities for querying an Oracle, Snowflake, or Postgres database. Gradually expanding to more database types.

All the methods in this package require a yaml config file. For convenience, we assume this file is located in /Users/username/configs/config-default.yml.

### Installation

```
pip install wdb_utils
```

### Usage

```
import wdb_utils as db

# Assuming your config file is located at /Users/myname/configs/config-default.yml

# Pull all the data from an Oracle database table into a data frame
df = db.run_query_oracle('select * from my_table')

# Pull all the data from a Snowflake database table into a data frame
df = db.run_query_snowflake('select * from other_table')

# Pull all the data from a Postgres database table into a data frame
df = db.run_query_postgres('select * from third_table')

# Delete all the data in those same tables
db.run_command_oracle('delete from my_table')
db.run_command_snowflake('delete from other_table')
db.run_command_postgres('delete from third_table')

# Put all the data back into the table
# Be aware that record order is not guaranteed to be preserved here
# Trying to decide if that's enough of a problem to fix it
db.load_data_oracle(df, 'my_schema', 'my_table')
db.load_data_snowflake(df, 'another_schema', 'other_table')
db.load_data_postgres(df, 'third_schema', 'third_table')
```

### Backward compatibility
Because this package was initially only for Oracle databases, I've also aliased the following methods to keep working:

* run_query is an alias for run_query_oracle
* run_command is an alias for run_command_oracle
* load_data is an alias for load_data_oracle
