#!/usr/bin/env python

import argparse
from os import environ
import json
import sys
import csv
from getpass import getpass

# From: https://church-of-jesus-christ-api.readthedocs.io/en/latest/index.html
from church_of_jesus_christ_api import ChurchOfJesusChristAPI

def print_CSV(households, units, file):
    """ Print a CSV of the households
    """
    unitNames = {}
    for unit in units:
        unitNames[unit['unitNumber']] = unit['name']

    houses_seen = {} # Keep track of which houses we've seen by UUID so we don't duplicate
    members_seen = {} # Keep track of which members we've seen by UUID so we don't duplicate
    writer = csv.writer(file)
    writer.writerow(["Name","Household","Unit","Address","Phone","Email","Birthdate","Positions"])
    for house in households:
        if house['uuid'] in houses_seen:
            continue
        else:
            houses_seen[house['uuid']] = True

        for member in house['members']:
            if member['uuid'] in members_seen:
                continue
            else:
                members_seen[member['uuid']] = True

            positions : list = []
            if 'positions' in member:
                for pos in member['positions']:
                    positions.append(pos['name'])
            writer.writerow([
                member['preferredName'],
                house['displayName'],
                unitNames[house['unitNumber']],
                house['address'] if 'address' in house else '',
                member['phone'] if 'phone' in member else '',
                member['email'] if 'email' in member else '',
                member['birthDate'] if 'birthDate' in member else '',
                ",\n".join(positions) if positions else ''
            ])

def get_self_info(username : str, password : str) -> json:
    """ Get the Member information, Use Cache file if it exists, otherwise query api
    """
    CACHE_FILE='self.json'
    try:
        with open(CACHE_FILE, 'r') as cache:
            return json.load(cache)
    except OSError:
        #  Ensure the username and password is s
        assert username, "Please set your username with the -u arg or CJC_USERNAME environment variable"
        if not password:
            password = getpass(prompt="Please enter your Church Password: ")
            
        api = ChurchOfJesusChristAPI(username, password)

        #print(f"Mobile sync data: {api.get_mobile_sync_data()}")
        info = api.user_details

        with open(CACHE_FILE, 'w') as cache:
          cache.write(json.dumps(info, indent=2))
        return info

def get_households(username : str, password : str) -> json:
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

        #print(f"Mobile sync data: {api.get_mobile_sync_data()}")
        households = api.get_directory()

        with open(CACHE_FILE, 'w') as cache:
          cache.write(json.dumps(households, indent=2))
        return households

def get_units(username : str, password : str) -> json:
    """ Get Unit information for the wards in the Stake
     of the user. Use Cache file if it exists, otherwise query api
    """
    CACHE_FILE='units.json'
    try:
        with open(CACHE_FILE, 'r') as cache:
            return json.load(cache)
    except OSError:
        #  Ensure the username and password is s
        assert username, "Please set your username with the -u arg or CJC_USERNAME environment variable"
        if not password:
            password = getpass(prompt="Please enter your Church Password: ")
            
        api = ChurchOfJesusChristAPI(username, password)

        #print(f"Mobile sync data: {api.get_mobile_sync_data()}")
        units = api.get_units(parent_unit = api.user_details['parentUnits'][0])

        with open(CACHE_FILE, 'w') as cache:
          cache.write(json.dumps(units, indent=2))
        return units


def main():
    """ Use Args to get member list form church API
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', default=environ.get("CHURCH_USERNAME", None))
    parser.add_argument('-p', '--password', default=environ.get("CHURCH_PASSWORD", None))
    parser.add_argument('-f', '--file', help="Save output csv to file", default=sys.stdout)
    parser.add_argument('-s', '--self', help="Show info on self", action='store_true')
    parser.add_argument('-w', '--ward', help="Show info on wards in stake", action='store_true')
    parser.add_argument('-l', '--household_list', help="Show info on households in stake (default)", action='store_true')

    args = parser.parse_args()
    info : json
    if args.self:
        info = get_self_info(args.username, args.password)
        print(f"{json.dumps(info, indent=2)}")
    elif args.ward:
        info = get_units(args.username, args.password)
        print(f"{json.dumps(info, indent=2)}")
    else:
        info = get_households(args.username, args.password)
        units : json = get_units(args.username, args.password)

        print(f"got {len(info)} Households")
        if args.file != sys.stdout:
            args.file = open(args.file, "w")
        print_CSV(info, units["childUnits"], args.file)
        args.file.close()



if __name__ == "__main__":
    main()
