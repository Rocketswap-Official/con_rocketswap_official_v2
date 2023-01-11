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
            self.c.submit(code, name="con_lusd_lst001", constructor_args={"vk": "sys"})  

        self.currency = self.c.get_contract("currency")
        self.rswp = self.c.get_contract("con_rswp_lst001")
        self.marmite = self.c.get_contract("con_marmite100_contract")
        self.lusd = self.c.get_contract("con_lusd_lst001")

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
        self.dex.create_market(signer="sys", token_a="con_rswp_lst001",
            token_b="currency", token_amount_a=2_000_000, token_amount_b=1_000_000,)
        # Create TAU-MARMITE pool
        self.dex.create_market(signer="sys", token_a="con_marmite100_contract", 
            token_b="currency", token_amount_a=5_000_000, token_amount_b=10_000)
        # Transfers
        self.currency.transfer(signer='sys', amount=1000, to='marvin')
        self.rswp.transfer(signer='sys', amount=20_000, to='marvin')
        self.marmite.transfer(signer='sys', amount=3_000_000, to='marvin')
        self.lusd.transfer(signer='sys', amount=850, to='marvin')

        self.currency.transfer(signer='sys', amount=1000, to='benji')
        self.rswp.transfer(signer='sys', amount=20_000, to='benji')
        self.marmite.transfer(signer='sys', amount=3_000_000, to='benji')
        self.lusd.transfer(signer='sys', amount=1500, to='benji')

    def tearDown(self):
        self.c.flush()
    
    #def test_01_swapping_token_for_token_should_pass(self):
    #    benji_initial_balance_rswp = self.rswp.balances['benji']
    #    benji_final_balance_marmite = self.marmite.balances['benji'] - 1_000_000
    #    
    #    self.dex.swap_tokens_through_tau(signer='benji', contract_a='con_marmite100_contract', amount_a=1_000_000, 
    #    contract_b='con_rswp_lst001', minimum_received=0, token_fees=False)

    #    self.assertEqual(self.marmite.balances['benji'], benji_final_balance_marmite)
    #    self.assertGreater(self.rswp.balances['benji'], benji_initial_balance_rswp)
    
    # def test_01_creating_pair_market_should_pass(self):
    #     # Create RSWP-MARMITE pool
    #     self.dex.create_market(signer="benji", token_a="con_rswp_lst001",
    #         token_b="con_marmite100_contract", token_amount_a=5_000, token_amount_b=1_000_000)

    # def test_02_creating_same_pair_market_should_fail(self):
    #     # Create RSWP-RSWP pool
    #     with self.assertRaises(AssertionError):
    #         self.dex.create_market(signer="benji", token_a="con_rswp_lst001",
    #             token_b="con_rswp_lst001", token_amount_a=5_000, token_amount_b=10_000)

    # def test_03_creating_an_inverse_pair_market_should_fail(self):
    #     # Create RSWP-MARMITE pool
    #     self.dex.create_market(signer="benji", token_a="con_rswp_lst001",
    #         token_b="con_marmite100_contract", token_amount_a=5_000, token_amount_b=1_000_000)
            
    #     # Create MARMITE-RSWP pool
    #     with self.assertRaises(AssertionError):
    #         self.dex.create_market(signer="benji", token_a="con_marmite100_contract",
    #             token_b="con_rswp_lst001", token_amount_a=5_000, token_amount_b=1_000_000)

    def test_04_swapping_tau_to_tokens_should_pass(self):

        marvin_balance_currency = self.currency.balances['marvin'] 
        marvin_balance_rswp = self.rswp.balances['marvin'] 
        initial_reserves =  self.dex.reserves['con_rswp_lst001','currency']
          
        # Swap 100 TAU for RSWP
        tokens_out = self.dex.swap_tau_to_token(signer='marvin', 
            token_contract='con_rswp_lst001', currency_amount=100)

        marvin_final_balance_currency = marvin_balance_currency - 100

        self.assertEqual(marvin_final_balance_currency, self.currency.balances['marvin'])
        self.assertEqual(marvin_balance_rswp+tokens_out, self.rswp.balances['marvin'])

    def test_05_swap_token_to_tau_should_pass(self):

        marvin_balance_currency = self.currency.balances['marvin'] 
        marvin_balance_rswp = self.rswp.balances['marvin'] 
        initial_reserves =  self.dex.reserves['con_rswp_lst001','currency']
          
        # Swap 2000 RSWP for TAU
        currency_out = self.dex.swap_token_to_tau(signer='marvin', 
            token_contract='con_rswp_lst001', token_amount=2000)

        marvin_final_balance_rswp = marvin_balance_rswp - 2000

        self.assertEqual(marvin_final_balance_rswp, self.rswp.balances['marvin'])
        self.assertEqual(marvin_balance_currency+currency_out, self.currency.balances['marvin'])

    def test_06_swap_token_to_token_when_token_token_pool_exist_should_pass(self):
        # Create RSWP-MARMITE pool
        self.dex.create_market(signer="benji", token_a="con_rswp_lst001",
            token_b="con_marmite100_contract", token_amount_a=5_000, token_amount_b=1_000_000)

        token_b_out = self.dex.swap_token_to_token(token_contract_a='con_rswp_lst001', 
            token_contract_b='con_marmite100_contract', token_amount_a=250)

        print(token_b_out)

    def test_07_swap_token_to_token_when_token_inverse_pool_exist_should_pass(self):
        # Create RSWP-MARMITE pool
        self.dex.create_market(signer="benji", token_a="con_rswp_lst001",
            token_b="con_marmite100_contract", token_amount_a=5_000, token_amount_b=1_000_000)

        token_b_out = self.dex.swap_token_to_token(token_contract_a='con_marmite100_contract', 
            token_contract_b='con_rswp_lst001', token_amount_a=5000)

        print(token_b_out)

    def test_08_swap_token_to_token_when_token_tau_pools_exist_should_pass(self):
        # TAU-RSWP and TAU-MARMITE pools were already created in setup
        
        token_b_out = self.dex.swap_token_to_token(token_contract_a='con_rswp_lst001', 
            token_contract_b='con_marmite100_contract', token_amount_a=250)

        print(token_b_out)


    def test_09_swap_token_to_token_when_token_pools_doesnt_exist_should_pass(self):
        market_statement = self.dex.swap_token_to_token(token_contract_a='con_lusd_lst001', 
            token_contract_b='con_marmite100_contract', token_amount_a=250)

        self.assertEqual(market_statement, 'Market does not exist')

         
if __name__ == "__main__":
    unittest.main()


