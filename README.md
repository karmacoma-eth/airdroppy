## Airdroppy

A collection of tools to:

- collect your Twitters followers in a single json file
- process the data of each Twitter user to derive an ENS name from their info
- resolve their ENS name to an address (requires web3.py)

[extract_eth_name.py](https://github.com/karmacoma-eth/airdroppy/blob/main/src/extract_eth_name.py) tries to look in a few places where people commonly put their ENS name:

- display name
- @username
- description
- location
- url

It also tries to make a best effort attempt at deriving an ENS name from the display and username, e.g.:

- for a user with display name `Joe Normal`, it will check `JoeNormal.eth`
- for a user with username `@joejoe`, it will check `joejoe.eth`


## Quick start

- `cp .env.example .env`
- set the BEARER_TOKEN variable in `.env` (get one at developer.twitter.com)
- set TWITTER_USER_ID in `.env` (get it at at https://codeofaninja.com/tools/find-twitter-id/ -- this is a numeric id, _not_ the display name)
- optionally set `WEB3_INFURA_PROJECT_ID` to resolve ENS names to addresses
- run `source .env`

Aggregate all your follower data in a single json file:

```sh
source .env
python3 src/followers_lookup.py | tee followers.json
```

Verify that the list contains the number of followers you expect:

```sh
jq 'length' followers.json
```

Derive the ENS names and addresses of users in the json file:

```sh
python3 src/extract_eth_name.py followers.json --verbose | tee followers_with_eth.json
```

Count for how many users we failed to resolve an address:

```sh
jq 'map(select(.eth_address == "")) | length' followers_with_eth.json
```

