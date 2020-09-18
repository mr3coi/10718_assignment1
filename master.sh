#!/bin/bash

# Data Configurations
DATA='acs acs5'
YEAR=2018
STATE=12

# Output table configurations
SCHEMA=sjc
TABLE=acs5_florida_bg

# Procedural configurations
# NOTE: Step 3 must be run with bash (to use regex capture)
SHELL=bash
CREDENTIALS=./credentials.yaml
DATA_DIR=./data
CSV_DIR=./data
CSV_NAME=acs_acs5_2018_12.csv

# Step 1: Download ACS data into JSON files
echo ">>> Execute step 1: downloading data"
python3 step1.py --dataset $DATA --year $YEAR --state $STATE --data-dir $DATA_DIR

# Step 2: Parse JSON files into a single CSV file
echo ">>> Execute step 2: preprocessing data"
python3 step2.py --data-dir $DATA_DIR --csv-dir $CSV_DIR --csv-name $CSV_NAME

# Step 3: Load the CSV data onto a table
echo ">>> Execute step 3: loading onto database"
$SHELL step3.sh $CSV_DIR/$CSV_NAME $SCHEMA $TABLE

# Clean up
rm -rf $DATA_DIR
rm -f $CSV_DIR/$CSV_NAME
