#!/usr/bin/env python

import argparse
from os import environ
import json
import sys
from getpass import getpass

# From: https://church-of-jesus-christ-api.readthedocs.io/en/latest/index.html
from church_of_jesus_christ_api import ChurchOfJesusChristAPI

def print_CSV(households, file):
    """ Print the member information to a comma seperated file
        Surround each field with quotes so that internal commas and newlines don't break them
    """
    print("Name,Household,Address,Phone,Email,Birthdate", file=file)
    for house in households:
        for member in house['members']:
            print("\"{NAME}\",\"{HOUSEHOLD}\",\"{ADDRESS}\",\"{PHONE}\",\"{EMAIL}\",\"{BIRTHDATE}\"".format(
                    NAME=member['preferredName'],
                    HOUSEHOLD=house['displayName'],
                    ADDRESS=house['address'],
                    PHONE=member['phone'],
                    EMAIL=member['email'],
                    BIRTHDATE=member['birthDate'],
                    )
                                    , file=file)


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
        entries[f"{hh['displayName']}{hh['uuid']}"] = hh['displayName']

    print(f"got {len(entries)} Households")
    if args.file != sys.stdout:
        args.file = open(args.file, "w")
    print_CSV(entries.values(), args.file)


if __name__ == "__main__":
    main()
