import json
import csv
import argparse
from ohio import encode_csv
import os
import re
from tqdm import tqdm

from step1 import DATA_DIR

parser = argparse.ArgumentParser(description="Process downloaded JSON files into a single CSV")
parser.add_argument("--data-dir", type=str, help="Directory containing raw JSON data")
parser.add_argument("--csv-dir", type=str, default=".", help="Desired output CSV file directory")
parser.add_argument("--csv-name", type=str, default=None,
                    help="Desired output CSV file name (excluding extension)")

if __name__ == "__main__":
    args = parser.parse_args()

    # Retrieve list of JSON files from step 1
    json_list = [os.path.join(DATA_DIR, item) for item in os.listdir(DATA_DIR)
                                              if os.path.splitext(item)[-1] == ".json"]
    assert len(json_list) > 0, "ERROR: No downloaded JSON file to parse"

    # Set up ptr to output file
    if args.csv_name is None:
        args.csv_name = '_'.join(os.path.splitext(os.path.split(json_list[0])[-1])[0].split('_')[:-1]) + ".csv"
    args.csv_name = os.path.join(args.csv_dir, args.csv_name)
    assert not os.path.exists(args.csv_name), f"ERROR: '{args.csv_name}' already exists"
    out_fp = open(args.csv_name, 'a')

    # Parse JSONs into CSV
    line_count = 0
    for idx, filepath in enumerate(tqdm(json_list)):
        with open(filepath, 'r') as fp:
            data = encode_csv(json.load(fp)).split('\n')
        if idx > 0:
            data = data[1:]  # Discard headers other than the first one
        else:
            data[0] = data[0].replace(' ', '_')  # Remove whitespaces in column names
        out_fp.write('\n'.join(data))
        line_count += len(data)-1

    # Close output file
    out_fp.close()

    print(f">>> Output written to: {args.csv_name}, total # lines written: {line_count}")
