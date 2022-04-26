from web3 import Web3
from eth_account.account import LocalAccount
from typing import Optional
import json
import requests
from pycoingecko import CoinGeckoAPI



WETH_CONTRACT = "0xC9BdeEd33CD01541e1eeD10f90519d2C06Fe3feB"
NEAR_CONTRACT = "0xC42C30aC6Cc15faC9bD938618BcaA1a1FaE8501d"
WETH_NEAR_LP_TOKEN = "0xc57ecc341ae4df32442cf80f34f41dc1782fe067"
BRL_TOKEN = "0x12c87331f086c3C926248f964f8702C0842Fd77F"

class Auroraswap:
    def __init__(self):
        self.w3: Optional[Web3] = None
        self.contract_abi: Optional[str] = None
        self.account: Optional[LocalAccount] = None
        self.contract = None
        self.aurora_tokens = None

        self.connect()
        self.import_abi()

    def connect(self):
        print("Connecting to aurora")
        provider: Web3.HTTPProvider = Web3.HTTPProvider("https://mainnet.aurora.dev:443")
        provider.middlewares.clear()
        self.w3 = Web3(provider)
        self.account = self.w3.eth.account.create("aurora_acc")

    def import_abi(self):
        with open("aurora_reader_core/abi/auroraswap_abi.txt") as abi_txt:
            abi_data = abi_txt.readline()
            self.contract_abi = str(abi_data)


    def calculate_rewards(self):
        current_block = self.w3.eth.get_block('latest')
        current_block_number = current_block.number
        self.contract = self.w3.eth.contract("0x35CC71888DBb9FfB777337324a4A60fdBAA19DDE", abi=self.contract_abi)
        multiplier = self.contract.functions.getMultiplier(current_block_number, current_block_number + 1).call()
        total_rewards_per_week = self.contract.functions.BRLPerBlock().call() / 1e18 * multiplier * 604800 / 1.1

        token_prices = CoinGeckoAPI().get_price(ids='weth,near,borealis', vs_currencies='usd')
        weth_price = token_prices['weth']['usd']
        near_price = token_prices['near']['usd']
        brl_price = token_prices['borealis']['usd']

        pool_size = self.contract.functions.poolLength().call()

        """
        pretty pointless part, since we don't need to parse through all
        pools and can just use a hardcoded address for this case.
        nevertheless, i'm leaving it here intentionally. 
        """
        for i in range(pool_size):
            pool_info = self.contract.functions.poolInfo(i).call()
            brl_per_week = total_rewards_per_week * (pool_info[1] / 10**3)
            weth_token_req = requests.get("https://api.aurorascan.dev/api?module=account&action=" +
                         f"tokenbalance&contractaddress={WETH_CONTRACT}" +
                         f"&address={pool_info[0]}&tag=latest&apikey=YourApiKeyToken")
            near_token_req = requests.get("https://api.aurorascan.dev/api?module=account&action=" +
                                      f"tokenbalance&contractaddress={NEAR_CONTRACT}" +
                                      f"&address={pool_info[0]}&tag=latest&apikey=YourApiKeyToken")

            weth_token_amount = float(int(json.loads(weth_token_req.content)["result"]) / 10**18)
            near_token_amount = float(int(json.loads(near_token_req.content)["result"]) / 10**24)

            if weth_token_amount > 0 and near_token_amount > 0:
                staked_lp_token_req = requests.get("https://api.aurorascan.dev/api?module=account&action=" +
                                      f"tokenbalance&contractaddress={WETH_NEAR_LP_TOKEN}" +
                                      f"&address=0x35CC71888DBb9FfB777337324a4A60fdBAA19DDE&tag=latest&apikey=YourApiKeyToken")
                staked_lp_token_amount = float(int(json.loads(staked_lp_token_req.content)["result"]) / 10**18)
                total_weth_near_lp_value = (near_price * near_token_amount +
                                            weth_price * weth_token_amount) / 2
                weekly_apr = brl_per_week * brl_price / total_weth_near_lp_value * 100
                yearly_apr = weekly_apr * 52
                data_for_api = {
                    "weekly_apr": weekly_apr,
                    "staked_lp_token_amount": staked_lp_token_amount,
                    "total_weth_near_lp_value": total_weth_near_lp_value,
                    "yearly_apr": yearly_apr,
                    "brl_per_week" : brl_per_week
                }
                return data_for_api
