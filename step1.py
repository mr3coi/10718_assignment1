import os
import argparse
import json
from tqdm import tqdm
import yaml

# Directory containing downloaded & preprocessed data
# (Step 2 will access this directory to fetch the data)
DATA_DIR = "./data"

# Specified as global in case to be used by other modules via import
VARIABLES = [
    "NAME",
    "B01001A_002E",  # White-Male
    "B01001A_017E",  # White-Female
    "B01001B_002E",  # AA-Male
    "B01001B_017E",  # AA-Female
    "B01001C_002E",  # NA-Male
    "B01001C_017E",  # NA-Female
    "B01001D_002E",  # Asian-Male
    "B01001D_017E",  # Asian-Female
    "B05002_002E",   # Born in the US
    "B05002_003E",   # Born in state of residence
    "B05002_014E",   # Born outside US, naturalized
    "B07101_002E",   # Non-movers
    "B08013_001E",   # Agg. travel time to work
    "B08014_002E",   # Workers w/o vehicles
    "B08301_003E",   # Means of transportation to work (drove alone)
    "B08301_004E",   # Means of transportation to work (carpooled)
    "B08301_010E",   # Means of transportation to work (public transportation)
    "B08301_017E",   # Means of transportation to work (motorcycle)
    "B08301_018E",   # Means of transportation to work (bicycle)
    "B08301_019E",   # Means of transportation to work (walk)
    "B08301_021E",   # Means of transportation to work (WFH)
    "B08203_002E",   # Num. of workers in household, no vehicle
    "B09018_002E",   # Own child
]

# ArgumentParser for cmdline input
parser = argparse.ArgumentParser(description="Download U.S. Census Bureau data in JSON format")
parser.add_argument("-d", "--dataset", nargs='*', type=str, default=["acs", "acs5"],
                    help="Target dataset to download, specify all hierarchy as space-separated list")
parser.add_argument("-y", "--year", type=int, default=2018, help="Target year of the dataset to download")
parser.add_argument("-s", "--state", type=int, default=12,
                    help="FIPS code for state of interest (default: Florida (12))")
parser.add_argument("--credentials", type=str, default="./credentials.yaml",
                    help="Path to credentials file (contains API key issued by U.S. Census API Data Service")
parser.add_argument("-t", "--test-query", dest="execute", action="store_false",
                    help="Only output the built query and not run it, for test purposes")


def compile_county_list(data, yr, state_FIPS, key=None):
    '''Return a list of FIPS codes of all county within the state of interest.

    :data: list of strings that specify dataset of interest
    :yr: target year
    :state_FIPS: The FIPS code for the state of interest
    :key: Key issued by U.S. census bureau for making multiple queries
    :returns: List of strings, each string being county FIPS code
    '''
    # Send a dummy query with a row per each county in target state
    variables = ["NAME"]
    predicates=["for=county:*", f"in=state:{state_FIPS}"]
    query_link = build_api_query(data, yr, variables, predicates, key)
    out_name = f"{'_'.join(args.dataset)}_{args.year}_state{state_FIPS}_counties.json"
    execute_query(query_link, out_name)

    # Parse resulting json data
    with open(out_name, 'r') as resultfile:
        try:
            result = json.load(resultfile)
        except json.decoder.JSONDecodeError:
            print("[ERROR] Bad Request - check dataset, year, and state FIPS number")
            return

    # Clean up
    os.remove(out_name)

    # Exclude header, return county FIPS codes only
    return [item[-1] for item in result[1:]]


def build_api_query(data, yr, variables, predicates, key=None):
    '''Build a query string for U.S. census bureau data API.

    :data: list of strings that specify dataset of interest
    :yr: target year
    :variables: List of variables to query
    :predicates: List of predicates to filter the query
    :key: Key issued by U.S. census bureau for making multiple queries
    :returns: Query link string
    '''
    query_link = os.path.join("https://api.census.gov/data", str(yr), *data)
    query_link += f"?get={','.join(variables)}"
    if len(predicates) > 0:
        query_link += f"&{'&'.join(predicates)}"
    if key is not None:
        query_link += f"&key={key}"
    return query_link


def execute_query(query_link, out_name):
    '''Execute the given query link and download result as json.

    :query_link: Compiled query link
    :out_name: Name of output JSON file
    :returns: None
    '''
    if not os.path.exists(out_name):
        shell_cmd = f"wget -O {out_name} \"{query_link}\""
        os.system(shell_cmd)
    else: print(f">>> {out_name}: already downloaded")


if __name__ == "__main__":
    args = parser.parse_args()
    
    # Retrieve API key from credentials
    with open(args.credentials, 'r') as c:
        args.key = yaml.safe_load(c.read())["web_resource"]["api_key"]

    # Create directory to collect downloaded data
    try:
        os.makedirs(DATA_DIR)
    except FileExistsError:
        if not os.path.isdir(DATA_DIR):
            raise OSError(f"ERROR: {DATA_DIR} already exists and is not a directory")

    # Generate list of counties in specified state
    county_list = compile_county_list(args.dataset, args.year, args.state, args.key)
    county_list.sort()

    # Download data for each county
    for county in tqdm(county_list):
        predicates = [
            "for=block group:*",
            f"in=state:{args.state}",
            f"in=county:{county}",
            #"in=tract:*",
        ]
        query_link = build_api_query(args.dataset, args.year, VARIABLES, predicates, key=args.key)
        if args.execute:
            out_name = os.path.join(DATA_DIR, f"{'_'.join(args.dataset)}_{args.year}_{args.state}_{county}.json")
            execute_query(query_link, out_name)
        else:
            print(f">>> Total: {len(county_list)} queries, target dir: {DATA_DIR}")
            print(">>> Sample query:", query_link)
            break
