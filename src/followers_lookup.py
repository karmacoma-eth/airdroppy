# based on https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Follows-Lookup/followers_lookup.py
# follows lookup docs: https://developer.twitter.com/en/docs/twitter-api/users/follows/quick-start/follows-lookup
# user object docs: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user

import requests
import os
import json
import time

bearer_token = os.environ.get("BEARER_TOKEN")
user_id = os.environ.get("TWITTER_USER_ID")

def create_url():
    return "https://api.twitter.com/2/users/{}/followers".format(user_id)


def get_params(pagination_token):
    params = {
        "user.fields": "description,location,url",
        "max_results": 1000,
    }

    if pagination_token:
        params['pagination_token'] = pagination_token

    return params


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FollowersLookupPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def check_env():
    if not bearer_token:
        raise Exception("BEARER_TOKEN is not set")
    if not user_id:
        raise Exception(f"TWITTER_USER_ID is not set, found '{user_id}'")


def fetch_followers():
    check_env()
    url = create_url()
    followers = []
    next_token = None

    while True:
        json_response = connect_to_endpoint(url, get_params(next_token))
        followers.extend(json_response["data"])

        # keep going until we stop getting a next_token
        next_token = json_response['meta'].get('next_token')
        if not next_token:
            break

        # sleep to avoid rate limiting if you have a lot of followers
        # time.sleep(60)

    return followers


def main():
    # print the aggregated followers list
    followers = fetch_followers()
    print(json.dumps(followers, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()