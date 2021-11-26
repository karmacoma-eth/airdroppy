import sys

try:
    from web3.auto.infura import w3
    from ens import ENS
    ns = ENS.fromWeb3(w3)
except:
    print("Could not import web3 or ens, won't be able to resolve ENS names to addresses. Make sure you have web3.py installed and WEB3_INFURA_PROJECT_ID set")

def resolve_ENS(ens_name):
    if ns is not None and ns.is_valid_name(ens_name):
        return ns.address(ens_name)

    return None


def main():
    resolve_ENS(sys.argv[1])

if __name__ == "__main__":
    main()