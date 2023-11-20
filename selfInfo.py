#!/usr/bin/env python

import argparse
from os import environ
import json
import sys
import csv
from getpass import getpass

# From: https://church-of-jesus-christ-api.readthedocs.io/en/latest/index.html
from church_of_jesus_christ_api import ChurchOfJesusChristAPI

def print_CSV(households, file):
    """ Print a CSV of the households
    """
    writer = csv.writer(file)
    writer.writerow(["Name","Household","UnitNumber","Address","Phone","Email","Birthdate","Positions"])
    for house in households:
        for member in house['members']:
            positions : list = []
            if 'positions' in member:
                for pos in member['positions']:
                    positions.append(pos['name'])
            writer.writerow([
                member['preferredName'],
                house['displayName'],
                house['unitNumber'],
                house['address'] if 'address' in house else '',
                member['phone'] if 'phone' in member else '',
                member['email'] if 'email' in member else '',
                member['birthDate'] if 'birthDate' in member else ''
                "\n".join(positions) if positions else ''
            ])


def get_self_info_and_households(username : str, password : str) -> json:
    """ Get the Member information, Use Cache file if it exists, otherwise query api
    """
    CACHE_FILE='households.json'
    try:
        with open(CACHE_FILE, 'r') as cache:
            return json.load(cache)
    except OSError:
        #  Ensure the username and password is s
        assert username, "Please set your username with the -u arg or CJC_USERNAME environment variable"
        if not password:
            password = getpass(prompt="Please enter your Church Password: ")
            
        api = ChurchOfJesusChristAPI(username, password)
        print(f"{api.user_details}")

        #print(f"Mobile sync data: {api.get_mobile_sync_data()}")
        households = api.get_directory()

        with open(CACHE_FILE, 'w') as cache:
          cache.write(json.dumps(households, indent=2))
        return households

def main():
    """ Use Args to get member list form church API
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', default=environ.get("CJC_USERNAME", None))
    parser.add_argument('-p', '--password', default=environ.get("CJC_PASSWORD", None))
    parser.add_argument('-f', '--file', help="Save output csv to file", default=sys.stdout)

    args = parser.parse_args()
    self_info : json
    households = get_self_info_and_households(args.username, args.password)

    # Store a dictionary of households, using uuid to dedup
    entries = {}
    for hh in households:
        entries[f"{hh['displayName']}{hh['uuid']}"] = hh

    print(f"got {len(entries)} Households")
    if args.file != sys.stdout:
        args.file = open(args.file, "w")
    print_CSV(entries.values(), args.file)


if __name__ == "__main__":
    main()
