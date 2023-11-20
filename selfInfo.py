#!/usr/bin/env python

import argparse
from os import environ
import json
import sys
from getpass import getpass

# From: https://church-of-jesus-christ-api.readthedocs.io/en/latest/index.html
from church_of_jesus_christ_api import ChurchOfJesusChristAPI

def get_self_info(username : str, password : str) -> json:
    """ Get the Member information, Use Cache file if it exists, otherwise query api
    """
    CACHE_FILE='self_info.json'
    try:
        with open(CACHE_FILE, 'r') as cache:
            return json.load(cache)
    except OSError:
        #  Ensure the username and password is s
        assert username, "Please set your username with the -u arg or CJC_USERNAME environment variable"
        if not password:
            password = getpass(prompt="Please enter your Church Password: ")
            
        api = ChurchOfJesusChristAPI(username, password)
        self_info = api.user_details


        with open(CACHE_FILE, 'w') as cache:
          cache.write(json.dumps(self_info, indent=2))
        return self_info

def main():
    """ Use Args to get member list form church API
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', default=environ.get("CJC_USERNAME", None))
    parser.add_argument('-p', '--password', default=environ.get("CJC_PASSWORD", None))

    args = parser.parse_args()
    self_info : json
    self_info = get_self_info(args.username, args.password)

    print(f"{self_info}")



if __name__ == "__main__":
    main()
