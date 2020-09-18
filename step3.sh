#!/bin/bash

CSV_NAME=$1
SCHEMA=$2
TABLE=$3
INSTRUCTIONS=${4:-instructions.sql}
CREDENTIALS=${5:-./credentials.yaml}

# Parse credentials YAML file
CREDENTIALS=`cat $CREDENTIALS`
HOST_PT='host: ([A-Za-z0-9._]+)'
DBNAME_PT='dbname: ([A-Za-z0-9._]+)'
USER_PT='user: ([A-Za-z0-9_]+)'
[[ $CREDENTIALS =~ $HOST_PT ]]   && HOST="${BASH_REMATCH[1]}"
[[ $CREDENTIALS =~ $DBNAME_PT ]] && DBNAME="${BASH_REMATCH[1]}"
[[ $CREDENTIALS =~ $USER_PT ]]   && USER="${BASH_REMATCH[1]}"

# Set role as $USER
sql_set_role="SET ROLE $USER;"
echo "$sql_set_role" > $INSTRUCTIONS

# Create schema if not yet exists
sql_create_schema="CREATE SCHEMA IF NOT EXISTS $SCHEMA;"
echo "$sql_create_schema" >> $INSTRUCTIONS

# Create table to add data to
sql_create_tbl=`head -n 1000 $CSV_NAME | csvsql -i postgresql --db-schema $SCHEMA --tables $TABLE`
echo "$sql_create_tbl" \
         | sed 's/BOOLEAN/INT/g' \
         | sed 's/DECIMAL/INT/g' \
         >> $INSTRUCTIONS

# Copy data over from CSV
echo "\\COPY $SCHEMA.$TABLE from '$CSV_NAME' WITH CSV HEADER;" >> $INSTRUCTIONS

# Run generated SQL script
psql -h $HOST -U $USER $DBNAME -f $INSTRUCTIONS

# Remove SQL script after run
rm -f $INSTRUCTIONS
