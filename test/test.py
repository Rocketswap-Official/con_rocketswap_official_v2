import unittest

from contracting.client import ContractingClient
from contracting.stdlib.bridge.time import Datetime
from contracting.stdlib.bridge.decimal import ContractingDecimal


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.c = ContractingClient()
        self.c.flush()

        with open("basic-token.py") as f:
            code = f.read()
            self.c.submit(code, name="currency", constructor_args={"vk": "sys"})
            self.c.submit(code, name="con_rswp_lst001", constructor_args={"vk": "sys"}) 
            self.c.submit(code, name="con_marmite100_contract", constructor_args={"vk": "sys"})  

        self.currency = self.c.get_contract("currency")
        self.rswp = self.c.get_contract("con_rswp_lst001")
        self.marmite = self.c.get_contract("con_marmite100_contract")

        with open("../con_rocketswap_official_v2.py") as f:
            code = f.read()
            self.c.submit(code, name="con_rocketswap_official_v2")

        self.dex = self.c.get_contract("con_rocketswap_official_v2")

        
        self.setupToken()

    def setupToken(self):
        # Approvals
        self.currency.approve(signer='sys', amount=999999999, to='con_rocketswap_official_v2')
        self.rswp.approve(signer='sys', amount=999999999, to='con_rocketswap_official_v2')
        self.marmite.approve(signer='sys', amount=999999999, to='con_rocketswap_official_v2')

        self.currency.approve(signer='marvin', amount=999999999, to='con_rocketswap_official_v2')
        self.rswp.approve(signer='marvin', amount=999999999, to='con_rocketswap_official_v2')
        self.marmite.approve(signer='marvin', amount=999999999, to='con_rocketswap_official_v2')

        self.currency.approve(signer='benji', amount=999999999, to='con_rocketswap_official_v2')
        self.rswp.approve(signer='benji', amount=999999999, to='con_rocketswap_official_v2')
        self.marmite.approve(signer='benji', amount=999999999, to='con_rocketswap_official_v2')
        
        # Create TAU-RSWP pool
        self.dex.create_market(signer="sys", contract="con_rswp_lst001", 
            currency_amount=1_000_000, token_amount=2_000_000)
        # Create TAU-MARMITE pool
        self.dex.create_market(signer="sys", contract="con_marmite100_contract", 
            currency_amount=10_000, token_amount=5_000_000)
        # Transfers
        self.currency.transfer(signer='sys', amount=1000, to='marvin')
        self.rswp.transfer(signer='sys', amount=20_000, to='marvin')
        self.marmite.transfer(signer='sys', amount=3_000_000, to='marvin')

        self.currency.transfer(signer='sys', amount=1000, to='benji')
        self.rswp.transfer(signer='sys', amount=20_000, to='benji')
        self.marmite.transfer(signer='sys', amount=3_000_000, to='benji')

    def tearDown(self):
        self.c.flush()

    def test_01_swapping_token_for_token_should_pass(self):
        benji_initial_balance_rswp = self.rswp.balances['benji']
        benji_final_balance_marmite = self.marmite.balances['benji'] - 1_000_000
        
        self.dex.swap_tokens_through_tau(signer='benji', contract_a='con_marmite100_contract', amount_a=1_000_000, 
        contract_b='con_rswp_lst001', minimum_received=0, token_fees=False)

        self.assertEqual(self.marmite.balances['benji'], benji_final_balance_marmite)
        self.assertGreater(self.rswp.balances['benji'], benji_initial_balance_rswp)
    
if __name__ == "__main__":
    unittest.main()


