#!/usr/bin/env python3
""" Get a person's email by knowing the onyen.
    Invocable from python or command line """

import argparse
import requests

def get_email(onyen):
    ''' Given a UNC onyen, return the user's email'''

    api_url = f'https://dir.unc.edu/api/search/{onyen}'
    response = requests.get(api_url)
    output = response.json()
    if not response.ok:
        print(f'The request to {api_url} returned a status_code of {response.status_code}')
        return None
    if (not isinstance(output, list) or
            len(output) == 0 or
            'mailIterator' not in output[0] or
            not isinstance(output[0]['mailIterator'], list)):
        print(f'Onyen {onyen} does not have a registered email')
        return None

    return output[0]['mailIterator'][0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--onyen', help="Onyen of the user who's email is to be looked up",
                        type=str, required=True)
    args = parser.parse_args()

    print(get_email(args.onyen))
