# based on https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Follows-Lookup/followers_lookup.py
# follows lookup docs: https://developer.twitter.com/en/docs/twitter-api/users/follows/quick-start/follows-lookup
# user object docs: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user

import requests
import json
import sys
import time
import re

from resolve_ens import resolve_ENS

TWITTER_URL_SHORTENER_PREFIX = "https://t.co/"

verbose = False

def log(string):
    if verbose:
        print(string, file=sys.stderr, flush=True)


def resolve_redirect(url):
    response = requests.get(url, allow_redirects=False)

    if response.status_code == 404:
        return None

    if response.status_code not in [301, 302]:
        raise Exception(
            "Unexpected response for {}: {} {}".format(
                url, response.status_code, response.text
            )
        )

    final_url = response.headers['location']
    log(f"Resolved {url} to {final_url}")

    # time.sleep(0.1)
    return final_url


# some people write their name like "My Name (myaddress.eth)" so we want to split on things like "(" and ")"
def derive_eth_name_from_string(string, string_kind, follow_redirects=True):
    if string is None:
        return None

    for word in re.split('[^a-zA-Z0-9\.:/]', string):
        if follow_redirects and word.startswith(TWITTER_URL_SHORTENER_PREFIX):
            word = resolve_redirect(word) or ''

        if word.lower().endswith('.eth'):
            log(f"Found {word} in {string_kind} '{string}'")
            return word

    return None


def is_ens_name(maybe_ens_name):
    try:
        address = resolve_ENS(maybe_ens_name)
        if address:
            return True
    except:
        pass

    log(f'Attempted {maybe_ens_name} but it does not resolve to an address')
    return False



# takes a user object as returned by the Twitter API and tries to extract an ENS name from:
# - the name
# - the description
# - the url
# - the location
# If an ENS name can't be found in any of these fields, this tries to derive it from the name
#
# user object docs: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
def derive_eth_name(user, use_heuristics=True):
    for key in ['name', 'description', 'location', 'url']:
        eth_name = derive_eth_name_from_string(user.get(key), key)
        if eth_name:
            return eth_name

    # if we couldn't find an exact match and heuristics are disabled, we're done
    if not use_heuristics:
        return None

    # for Twitter user @joenormal, we try 'joenormal.eth'
    maybe_ens_name = user.get('username') + '.eth'
    if is_ens_name(maybe_ens_name):
        return maybe_ens_name

    # if everything else fails, assume that the user's screen name + .eth is their eth name
    # e.g. it turns "Joe Normal" into "JoeNormal.eth"
    # not that there is a good chance that this will be wrong
    maybe_ens_name = ''.join(user.get('name').split()) + '.eth'
    if is_ens_name(maybe_ens_name):
        return maybe_ens_name

    return None


# expects a json filename as the first argument, containing a list of user objects
def main():
    global verbose
    if '--verbose' in sys.argv:
        verbose = True

    followers = json.loads(open(sys.argv[1], "r").read())
    for follower in followers:
        eth_name = derive_eth_name(follower) or ''
        follower['derived_eth_name'] = eth_name

        if follower.get('eth_address') is None:
            follower['eth_address'] = resolve_ENS(eth_name) or ''

    print(json.dumps(followers, indent=2))

if __name__ == "__main__":
    main()