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
    print("Name,Address,Full Name", file=file)
    for house in households:
        print("\"{NAME}\",\"{ADDRESS}\",\"{FULL}\"".format(
                    NAME=house['familyNameLocal'],
                    ADDRESS="\n".join(house['address']['addressLines']),
                    FULL=house['directoryPreferredLocal'],
                    )
                                    , file=file)


def get_member_list(username : str, password : str) -> json:
    """ Get the Member information, Use Cache file if it exists, otherwise query api
    """
    CACHE_FILE='member_list.json'
    try:
        with open(CACHE_FILE, 'r') as cache:
            return json.load(cache)
    except OSError:
        #  Ensure the username and password is s
        assert username, "Please set your username with the -u arg or CJC_USERNAME environment variable"
        if not password:
            password = getpass(prompt="Please enter your Church Password: ")
            
        api = ChurchOfJesusChristAPI(username, password)
        print(f"Getting Ward List for {api.user_details}") 

        members = api.get_member_list()

        with open(CACHE_FILE, 'w') as cache:
          cache.write(json.dumps(members, indent=2))
        return members

def main():
    """ Use Args to get member list form church API
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', default=environ.get("CJC_USERNAME", None))
    parser.add_argument('-p', '--password', default=environ.get("CJC_PASSWORD", None))
    parser.add_argument('-f', '--file', help="Save output scv to file", default=sys.stdout)

    args = parser.parse_args()
    members : json
    members = get_member_list(args.username, args.password)

    print(f"got {len(members)} Members")

    # Store a dictionary of households, using uuid to dedup
    households = {}
    for member in members:
        households[member['householdMember']['household']['uuid']] = member['householdMember']['household']
        # households.add(member['householdMember']['household'])

    print(f"got {len(households)} Households")
    if args.file != sys.stdout:
        args.file = open(args.file, "w")
    print_CSV(households.values(), args.file)


if __name__ == "__main__":
    main()
