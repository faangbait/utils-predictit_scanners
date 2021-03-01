import requests
import json
from prettytable import PrettyTable


class PredictIt:

    def get_all_market_data(self):
        """
        Queries all market data from PI.

        Returns:
            active_markets (list): A list of market dictionaries
        """

        api_url = "https://www.predictit.org/api/marketdata/all/"
        r = requests.get(api_url, verify=True)
        active_markets = json.loads(r.text)
        return active_markets.get("markets")

    def get_market_data(self, market):
        """
        Queries market data from PI.

        Args:
            market (str or int) - the market ID

        Returns:
            active_market (dict) - the market's data
        """
        api_url = "https://www.predictit.org/api/marketdata/markets/" + str(market)
        r = requests.get(api_url, verify=True)
        active_market = json.loads(r.text)
        return active_market

    def get_market_contracts(self, market, sort="NAMEASC"):
        """
        Gets contracts from a market.

        Args:
            market (dict): an active_market dict from PI
            sort (string): a key indicating the sorter function to use

        returns:
            contracts (list): a list of dictionaries reflecting each individual contract on the market
        """

        contracts = market["contracts"]
        if sort == "DISPLAYORDER":
            return sorted(contracts, key=lambda i: i["displayOrder"])
        else:
            return sorted(contracts, key=lambda i: i["name"])

    def calculate_negative_risk(self, contracts, visible=False, ignoreNone=False, prettyprint=True, limited_display=False):
        """
        Calculate the negative risk of a set of contracts

        Args:
            contracts (list): A list of contract dictionaries
            visible (boolean): Print extra data about markets
            ignoreNone (boolean): Treat N/As as unbuyable
            prettyprint (boolean): Print using Pretty Table
            limited_display (boolean): Print less data (for excel import)


        Returns:
            risk (tuple): Total cost of nos, total contract fees, number of contracts, and the profit per share set, count of "Nones" [hard to buy market]
        """

        if visible:
            if prettyprint:
                results = PrettyTable()
                if limited_display:
                    from prettytable import PLAIN_COLUMNS
                    results.set_style(PLAIN_COLUMNS)
            else:
                print("Contract\tNos\t\tUpside\tFees\tWinnings")

        contract_data=[]
        nones = 0

        # Generate contract data into a organized list
        for contract in contracts:
            if contract['bestBuyNoCost']: # not a None
                contract_data += [{
                    "name" : contract["name"],
                    "shares": 1,
                    "no_cost": contract['bestBuyNoCost'],
                    "contract_upside": 1-contract['bestBuyNoCost'],
                    "contract_fees": (1-contract['bestBuyNoCost'])/10,
                    "winnings": 0
                }]
            else:
                nones += 1
                if ignoreNone:
                    contract_data+=[{
                        "name": contract["name"],
                        "shares": 0,
                        "no_cost": 0,
                        "contract_upside": 0,
                        "contract_fees": 0,
                        "winnings": 0
                    }]
                else:
                    contract_data += [{
                        "name": contract["name"],
                        "shares": 1,
                        "no_cost": .99,
                        "contract_upside": .01,
                        "contract_fees": .001,
                        "winnings": 0
                    }]

        total_shares = sum(d['shares'] for d in contract_data)
        total_no_cost = sum(d['no_cost'] for d in contract_data)
        total_contract_upside = sum(d['contract_upside'] for d in contract_data)
        total_contract_fees = sum(d['contract_fees'] for d in contract_data)
        total_cost_basis = sum(d["shares"] * d["no_cost"] for d in contract_data)

        pretty_names=[]
        pretty_positions=[]
        pretty_shares=[]
        pretty_price=[]
        pretty_false=[]
        pretty_true=[]
        pretty_gainloss=[]

        # calculate gain/loss and fill pretty-tables
        for contract in contract_data:
            pretty_names += [contract['name']]
            pretty_positions += ["NO"]
            pretty_shares += [1]
            pretty_price += [contract['no_cost']]
            pretty_false += [(1 - contract['no_cost']) * .9] # upside - fees
            pretty_true += [-1 * contract['no_cost']] # lose cost of contract
            pretty_gainloss += [(-1 * contract['no_cost']) + (total_contract_upside * .9) - (contract['contract_upside'] * .9)]

        minimum_winnings = min(pretty_gainloss)

        # Iterate through list to calculate winnings
        for contract in contract_data:
            contract["winnings"] = total_shares - contract["shares"]
            contract["winnings"] -= total_contract_fees
            contract["winnings"] += contract["contract_fees"]
            contract["winnings"] -= total_no_cost

            if visible:
                if not prettyprint:
                    print(f"{contract['name'][:10]}\t{contract['no_cost']:.2f}\t{contract['contract_upside']:.2f}\t{contract['contract_fees']:.2f}\t{contract['winnings']:.3f}")

        #display results
        if visible:
            if prettyprint:
                results.add_column("Contract", pretty_names)
                results.add_column("Positions", pretty_positions)
                results.add_column("Shares", pretty_shares)
                results.add_column("Price", pretty_price)
                if not limited_display:
                    results.add_column("False", pretty_false)
                    results.add_column("True", pretty_true)
                    results.add_column("G/L", pretty_gainloss)
                results.float_format = ".2"
                print(results)

            print("")
            print(f"COUNT OF CONTRACTS: \t{len(contract_data)}")
            print(f"MINIMUM WINNINGS: \t{minimum_winnings:.2f}")

        return total_no_cost, total_contract_fees, len(contract_data), minimum_winnings, nones


    def deprecated_calculate_negative_risk(self, contracts, visible=False, ignoreNone=False):
        """
        Calculate the negative risk of a set of contracts

        Args:
            contracts (list): A list of contract dictionaries
            visible (boolean): Print extra data about markets
            ignoreNone (boolean): Treat N/As as unbuyable

        Returns:
            risk (tuple): Total cost of nos, total contract fees, number of contracts, and the profit per share set, count of "Nones" [hard to buy market]
        """
        if visible:
            print("Contract\t\tNos\t\t\tUpside\t\tFees")

        total_no_cost = 0
        total_contract_fees = 0
        total_upside = 0
        nones=0
        contract_data=[]
        for contract in contracts:
            if type(contract['bestBuyNoCost']) == type(0.01): # if we have a float
                no_cost = contract['bestBuyNoCost']
                contract_upside = 1-no_cost
            else:
                nones+=1
                if ignoreNone:
                    no_cost = 0
                    contract_upside = 0
                else:
                    no_cost = .99
                    contract_upside = 1 - no_cost

            total_no_cost += no_cost
            contract_fees = contract_upside / 10
            total_contract_fees += contract_fees
            total_upside += contract_upside

            contract_data += [{
                "no_cost": no_cost,
                "contract_upside": contract_upside,
                "contract_fees": contract_fees,
                "winnings": 0
            }]


            if visible:
                print(f"{contract['name'][:10]}\t\t{no_cost:.2f}\t\t{contract_upside:.2f}\t\t{contract_fees:.2f}")

        available_contracts = len(contracts)

        if ignoreNone:
            available_contracts -= nones

        # SUM($B$2:$B$11)-B2-SUM($E$2:$E$11)-SUM($F$2:$F$11)+E2
        # sum of shares, minus shares of "losing" bet, minus sum of fees, plus fees for "winning" bet (ignored), minus cost basis (no price)
        winnings = available_contracts - 1 - total_contract_fees-total_no_cost

        #minimum winnings
        for contract in contract_data:
            contract["winnings"] += len(contract_data)-1
            contract["winnings"] -= total_contract_fees
            contract["winnings"] -= total_no_cost
            contract["winnings"] += contract["no_cost"]

        winnings = sorted(contract_data, key=lambda i: i["winnings"])[0]["winnings"]

        return total_no_cost, total_contract_fees, available_contracts, winnings, nones