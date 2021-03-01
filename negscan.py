#!/bin/python3

import pi
import sys,getopt

def scan_all_markets(quiet=False):
    """
    Scans all PI markets for potential profitable negative risk arbitrage.

    Args:
         quiet (boolean) - Suppresses output of negative return markets
    """
    client = pi.PredictIt()
    active_markets = client.get_all_market_data()
    for market in active_markets:
        contracts = client.get_market_contracts(market)
        risk = client.calculate_negative_risk(contracts, ignoreNone=True)
        market["risk"] = risk[3]
        market["nones"] = risk[4]
    active_markets = sorted(active_markets, key=lambda i: i["risk"])

    for market in active_markets:
        if len(market['contracts']) > 1: # Hide contracts with just one market
            if len(market['contracts']) / 2 > market['nones']: # Hide contracts with more than 50% N/A
                if quiet:
                    if market['risk']>0.01:
                        print(f"{market['risk']:.2f}\t\thttps://www.predictit.org/markets/detail/{market['id']}\t\t{market['shortName']}")
                else:
                    print(
                        f"{market['risk']:.2f}\t\thttps://www.predictit.org/markets/detail/{market['id']}\t\t{market['shortName']}")

def argparse(argv):
    quiet = False

    try:
        opts, args = getopt.getopt(argv, "hq",["quiet"])
    except getopt.GetoptError:
        print('negscan.py (use -q for quiet)')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('negscan.py (use -q for quiet)')
            sys.exit()
        elif opt in ("-q", "--quiet"):
            quiet=True

    scan_all_markets(quiet)

if __name__ == '__main__':
    argparse(sys.argv[1:])
