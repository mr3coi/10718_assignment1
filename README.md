# 10718\_assignment1

Assignment 1 (Data Collection &amp; ETL) submission for CMU 10-718 (Data Analysis), Fall 2020.

Queries for block-group-level statistics for a specific state,
from datasets provided by U.S. Census Bureau
(default: ACS 5-Year, 2018; state: Florida).

### How to run

1. Execution

Run the master script: `sh master.sh`

2. Update query configuration

For configs other than survey variables, update the script variables within master script.

To change the list of survey variables, update the list stored in `step1.py` script.

### TODOs

- Move the list of survey variables to master script, or a separate config file
