#!python3

import pi
import sys, getopt

def print_market_data(market, sorter="nameasc", excel_ready=False):
    client = pi.PredictIt()
    contracts = client.get_market_contracts(client.get_market_data(market), sort=sorter)
    risk = client.calculate_negative_risk(contracts, visible=True, ignoreNone=True, limited_display=excel_ready)
    if risk[4] > 1:
        print(f"Potentially hard to buy: {risk[4]} contracts not available")


def argparse(argv):
    market = None
    sorter = "NAMEASC"
    excel_ready = False

    try:
        opts, args = getopt.getopt(argv, "hm:s:x", ["market=", "sort=","excel"])
    except getopt.GetoptError:
        print('negrisk.py -m <market id> -s <sorter>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('negrisk.py -m <market id> -s <sorter>')
            sys.exit()
        elif opt in ("-m", "--market"):
            market = arg
        elif opt in ("-s", "--sort"):
            sorter=arg.upper()
        elif opt in ("-x", "--excel"):
            excel_ready = True

    if market:
        print_market_data(market, sorter, excel_ready)
    else:
        print('No market ID specified. Use negrisk.py -m <market id>')

if __name__ == '__main__':
    argparse(sys.argv[1:])

