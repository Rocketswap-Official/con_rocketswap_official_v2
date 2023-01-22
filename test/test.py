import unittest

from contracting.client import ContractingClient
from contracting.stdlib.bridge.time import Datetime
from contracting.stdlib.bridge.decimal import ContractingDecimal


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.c = ContractingClient()
        self.c.flush()

        with open('basic-token.py') as f:
            code = f.read()
            self.c.submit(code, name='currency', constructor_args={'vk': 'sys'})
            self.c.submit(code, name='con_rswp_lst001', constructor_args={'vk': 'sys'}) 
            self.c.submit(code, name='con_lusd_lst001', constructor_args={'vk': 'sys'})
            self.c.submit(code, name='con_marmite100_contract', constructor_args={'vk': 'sys'})
            self.c.submit(code, name='con_spange_lst001', constructor_args={'vk': 'sys'})
              

        self.currency = self.c.get_contract('currency')
        self.rswp = self.c.get_contract('con_rswp_lst001')
        self.marmite = self.c.get_contract('con_marmite100_contract')
        self.lusd = self.c.get_contract('con_lusd_lst001')
        self.spange = self.c.get_contract('con_spange_lst001')

         # Deploy rocketswap v1
         # we need v1 states for v2
        with open('../con_rocketswap_official_v1_1.py') as f:
            code = f.read()
            self.c.submit(code, name='con_rocketswap_official_v1_1')

        self.dex_v1 = self.c.get_contract('con_rocketswap_official_v1_1')

        # Deploy rocketswap v2 for different base pair markets
        with open('../con_rocketswap_official_v2.py') as f:
            code = f.read()
            self.c.submit(code, name='con_dex_currency', 
                constructor_args={'base_contract': 'currency'})
            self.c.submit(code, name='con_dex_lusd', 
                constructor_args={'base_contract': 'con_lusd_lst001'})
            self.c.submit(code, name='con_dex_marmite', 
                constructor_args={'base_contract': 'con_marmite100_contract'})
            self.c.submit(code, name='con_dex_spange', 
                constructor_args={'base_contract': 'con_spange_lst001'})

        self.dex_currency = self.c.get_contract('con_dex_currency')
        self.dex_lusd = self.c.get_contract('con_dex_lusd')
        self.dex_marmite = self.c.get_contract('con_dex_marmite')
        self.dex_spange = self.c.get_contract('con_dex_spange')

        with open('non_lst001.py') as f:
            code = f.read()
            self.c.submit(code, name='con_non_lst001')
        
        self.setupToken()

    def setupToken(self):
        # Approvals
        self.rswp.approve(signer='sys', amount=999999999, to='con_rocketswap_official_v1_1')
        self.rswp.approve(signer='benji', amount=999999999, to='con_rocketswap_official_v1_1')
        self.rswp.approve(signer='marvin', amount=999999999, to='con_rocketswap_official_v1_1')

        self.currency.approve(signer='sys', amount=999999999, to='con_dex_currency')
        self.lusd.approve(signer='sys', amount=999999999, to='con_dex_currency')
        self.rswp.approve(signer='sys', amount=999999999, to='con_dex_currency')
        self.marmite.approve(signer='sys', amount=999999999, to='con_dex_currency')
        self.spange.approve(signer='sys', amount=999999999, to='con_dex_currency')

        self.currency.approve(signer='sys', amount=999999999, to='con_dex_lusd')
        self.lusd.approve(signer='sys', amount=999999999, to='con_dex_lusd')
        self.rswp.approve(signer='sys', amount=999999999, to='con_dex_lusd')
        self.marmite.approve(signer='sys', amount=999999999, to='con_dex_lusd')
        self.spange.approve(signer='sys', amount=999999999, to='con_dex_lusd')

        self.currency.approve(signer='sys', amount=999999999, to='con_dex_marmite')
        self.lusd.approve(signer='sys', amount=999999999, to='con_dex_marmite')
        self.rswp.approve(signer='sys', amount=999999999, to='con_dex_marmite')
        self.marmite.approve(signer='sys', amount=999999999, to='con_dex_marmite')
        self.spange.approve(signer='sys', amount=999999999, to='con_dex_marmite')

        self.currency.approve(signer='sys', amount=999999999, to='con_dex_spange')
        self.lusd.approve(signer='sys', amount=999999999, to='con_dex_spange')
        self.rswp.approve(signer='sys', amount=999999999, to='con_dex_spange')
        self.marmite.approve(signer='sys', amount=999999999, to='con_dex_spange')
        self.spange.approve(signer='sys', amount=999999999, to='con_dex_spange')

        self.currency.approve(signer='benji', amount=999999999, to='con_dex_currency')
        self.lusd.approve(signer='benji', amount=999999999, to='con_dex_currency')
        self.rswp.approve(signer='benji', amount=999999999, to='con_dex_currency')
        self.marmite.approve(signer='benji', amount=999999999, to='con_dex_currency')
        self.spange.approve(signer='benji', amount=999999999, to='con_dex_currency')

        self.currency.approve(signer='benji', amount=999999999, to='con_dex_lusd')
        self.lusd.approve(signer='benji', amount=999999999, to='con_dex_lusd')
        self.rswp.approve(signer='benji', amount=999999999, to='con_dex_lusd')
        self.marmite.approve(signer='benji', amount=999999999, to='con_dex_lusd')
        self.spange.approve(signer='benji', amount=999999999, to='con_dex_lusd')

        self.currency.approve(signer='benji', amount=999999999, to='con_dex_marmite')
        self.lusd.approve(signer='benji', amount=999999999, to='con_dex_marmite')
        self.rswp.approve(signer='benji', amount=999999999, to='con_dex_marmite')
        self.marmite.approve(signer='benji', amount=999999999, to='con_dex_marmite')
        self.spange.approve(signer='benji', amount=999999999, to='con_dex_marmite')

        self.currency.approve(signer='benji', amount=999999999, to='con_dex_spange')
        self.lusd.approve(signer='benji', amount=999999999, to='con_dex_spange')
        self.rswp.approve(signer='benji', amount=999999999, to='con_dex_spange')
        self.marmite.approve(signer='benji', amount=999999999, to='con_dex_spange')
        self.spange.approve(signer='benji', amount=999999999, to='con_dex_spange')

        self.currency.approve(signer='marvin', amount=999999999, to='con_dex_currency')
        self.lusd.approve(signer='marvin', amount=999999999, to='con_dex_currency')
        self.rswp.approve(signer='marvin', amount=999999999, to='con_dex_currency')
        self.marmite.approve(signer='marvin', amount=999999999, to='con_dex_currency')
        self.spange.approve(signer='marvin', amount=999999999, to='con_dex_currency')

        self.currency.approve(signer='marvin', amount=999999999, to='con_dex_lusd')
        self.lusd.approve(signer='marvin', amount=999999999, to='con_dex_lusd')
        self.rswp.approve(signer='marvin', amount=999999999, to='con_dex_lusd')
        self.marmite.approve(signer='marvin', amount=999999999, to='con_dex_lusd')
        self.spange.approve(signer='marvin', amount=999999999, to='con_dex_lusd')

        self.currency.approve(signer='marvin', amount=999999999, to='con_dex_marmite')
        self.lusd.approve(signer='marvin', amount=999999999, to='con_dex_marmite')
        self.rswp.approve(signer='marvin', amount=999999999, to='con_dex_marmite')
        self.marmite.approve(signer='marvin', amount=999999999, to='con_dex_marmite')
        self.spange.approve(signer='marvin', amount=999999999, to='con_dex_marmite')

        self.currency.approve(signer='marvin', amount=999999999, to='con_dex_spange')
        self.lusd.approve(signer='marvin', amount=999999999, to='con_dex_spange')
        self.rswp.approve(signer='marvin', amount=999999999, to='con_dex_spange')
        self.marmite.approve(signer='marvin', amount=999999999, to='con_dex_spange')
        self.spange.approve(signer='marvin', amount=999999999, to='con_dex_spange')

        # Transfers
        self.currency.transfer(signer='sys', amount=1000, to='marvin')
        self.rswp.transfer(signer='sys', amount=20_000, to='marvin')
        self.marmite.transfer(signer='sys', amount=3_000_000, to='marvin')
        self.lusd.transfer(signer='sys', amount=850, to='marvin')
        self.spange.transfer(signer='sys', amount=1_000_000, to='marvin')

        self.currency.transfer(signer='sys', amount=5000, to='benji')
        self.rswp.transfer(signer='sys', amount=200_000, to='benji')
        self.marmite.transfer(signer='sys', amount=2_000_000, to='benji')
        self.lusd.transfer(signer='sys', amount=1500, to='benji')
        self.spange.transfer(signer='sys', amount=1_000_000, to='benji')

        # Create LUSD-RSWP market
        # must exist for RSWP burning and token fees 
        self.dex_lusd.create_rswp_market(signer='sys', base_amount=1000, token_amount=1000)
        

    def tearDown(self):
        self.c.flush()

    # CREATING MARKETS
    
    def test_01_creating_marktets_of_different_pairs_should_pass(self):
        # Create LUSD-TAU marktet
        self.dex_lusd.create_market(signer='sys', contract='currency', base_amount=14_000, 
            token_amount=2_000_000)
        # Create MARMITE-SPANGE marktet
        self.dex_marmite.create_market(signer='sys', contract='con_spange_lst001', base_amount=50_000_000, 
            token_amount=2_000_000)
        # Create SPANGE-TAU marktet
        self.dex_spange.create_market(signer='sys', contract='currency', base_amount=1_000_000, 
            token_amount=2_000_000)

        # Check reserves        
        self.assertEqual(self.dex_lusd.reserves['currency'], [14_000, 2_000_000])
        self.assertEqual(self.dex_marmite.reserves['con_spange_lst001'], [50_000_000, 2_000_000])
        self.assertEqual(self.dex_spange.reserves['currency'], [1_000_000, 2_000_000])
        # Check pairs
        self.assertTrue(self.dex_lusd.pairs['currency'])
        self.assertTrue(self.dex_marmite.pairs['con_spange_lst001'])
        self.assertTrue(self.dex_spange.pairs['currency'])

    def test_02_creating_market_with_base_token_should_fail(self):
        # Create TAU-TAU marktet
        with self.assertRaises(AssertionError):
            self.dex_currency.create_market(signer='sys', contract= 'currency', 
                base_amount=1_000_000, token_amount=2_000_000)

        # Create LUSD-LUSD marktet
        with self.assertRaises(AssertionError):
            self.dex_lusd.create_market(signer='sys', contract= 'con_lusd_lst001', 
                base_amount=14_000, token_amount=2_000_000)

        # Create MARMITE-MARMITE marktet
        with self.assertRaises(AssertionError):
            self.dex_marmite.create_market(signer='sys', contract= 'con_marmite100_contract', 
                base_amount=50_000, token_amount=2_000_000)

    def test_03_owner_creating_RSWP_marktet_should_pass(self):
        OWNER = 'sys'
        # Create TAU-RSWP marktet
        self.dex_currency.create_rswp_market(signer=OWNER, base_amount=1_000_000, token_amount=2_000_000)
        # Create MARMITE-RSWP marktet
        self.dex_marmite.create_rswp_market(signer=OWNER, base_amount=50_000, token_amount=2_000_000)

        self.assertEqual(self.dex_currency.reserves['con_rswp_lst001'], [1_000_000, 2_000_000])
        self.assertEqual(self.dex_marmite.reserves['con_rswp_lst001'], [50_000, 2_000_000])
        self.assertTrue(self.dex_currency.pairs['con_rswp_lst001'])
        self.assertTrue(self.dex_marmite.pairs['con_rswp_lst001'])

    def test_04_user_creating_RSWP_marktet_should_fail(self):
        # Create TAU-RSWP marktet
        with self.assertRaises(AssertionError):
            self.dex_currency.create_market(signer='benji', contract= 'con_rswp_lst001', 
                base_amount=1_000_000, token_amount=2_000_000)

        # Create LUSD-RSWP marktet
        with self.assertRaises(AssertionError):
            self.dex_lusd.create_market(signer='benji', contract= 'con_rswp_lst001', 
                base_amount=14_000, token_amount=2_000_000)

        # Create MARMITE-RSWP marktet
        with self.assertRaises(AssertionError):
            self.dex_marmite.create_market(signer='marvin', contract='con_rswp_lst001', 
                base_amount=50_000, token_amount=2_000_000)

    def test_05_creating_pair_for_nonexisting_token_should_fail(self):

        with self.assertRaises(ImportError):
            self.dex_lusd.create_market(signer='sys', contract='con_nonexisting_lst001', 
                    base_amount=50_000, token_amount=30_000)

    def test_06_create_market_fails_bad_interface(self):
        with self.assertRaises(AssertionError):
            self.dex_lusd.create_market(contract='con_non_lst001', 
                base_amount=1, token_amount=1)

    def test_07_create_market_fails_zeros_for_amounts(self):
        with self.assertRaises(AssertionError):
            self.dex_lusd.create_market(contract='con_spange_lst001', 
                base_amount=0, token_amount=1)

        with self.assertRaises(AssertionError):
            self.dex_lusd.create_market(contract='con_spange_lst001', 
                base_amount=1, token_amount=-1)

    def test_08_create_market_sends_coins_to_dex(self):
        from_lusd_rswp_pair_created_in_setup = 1000

        # Create LUSD-TAU pair
        self.dex_lusd.create_market(signer='sys', contract='currency', base_amount=14_000, 
            token_amount=2_000_000)

        self.assertEqual(self.currency.balances['con_dex_lusd'], 2_000_000)
        self.assertEqual(self.lusd.balances['con_dex_lusd'], 14_000 + from_lusd_rswp_pair_created_in_setup)


    def test_09_create_market_mints_100_lp_points(self):

        self.dex_lusd.create_market(signer='sys', contract='currency', base_amount=14_000, 
            token_amount=2_000_000)

        self.assertEqual(self.dex_lusd.lp_points['currency', 'sys'], 100)

    def test_10_create_market_sets_price_accurately(self):

        self.dex_lusd.create_market(signer='sys', contract='currency', base_amount=14_000, 
            token_amount=2_000_000)

        reserves = self.dex_lusd.reserves['currency']
        base_reserve, token_reserve = reserves
        price = base_reserve/token_reserve

        self.assertEqual(self.dex_lusd.prices['currency'], price)

    def test_11_create_market_twice_throws_assertion(self):

        self.dex_lusd.create_market(signer='sys', contract='currency', base_amount=14_000, 
            token_amount=2_000_000)


        with self.assertRaises(AssertionError):
            self.dex_lusd.create_market(signer='sys', contract='currency', base_amount=14_000, 
            token_amount=2_000_000)

    # BUYING 

    def test_12__buying_from_different_markets_should_pass(self):
        # Create TAU-RSWP market
        self.dex_currency.create_rswp_market(signer='sys', base_amount=1_000_000, 
            token_amount=2_000_000)
        # Create LUSD-TAU market
        self.dex_lusd.create_market(signer='sys', contract='currency', 
            base_amount=14_000, token_amount=2_000_000)
        # Create LUSD-MARMITE market
        self.dex_lusd.create_market(signer='sys', contract='con_marmite100_contract',
            base_amount=50_000_000, token_amount=2_000_000)

        benji_balance_rswp = self.rswp.balances['benji']
        benji_balance_tau = self.currency.balances['benji']
        marvin_balance_marmite = self.marmite.balances['marvin']

        # Buy RSWP from TAU-RSWP pair
        rswp_purchased = self.dex_currency.buy(signer='benji',contract='con_rswp_lst001', base_amount=2500)
        # Buy TAU from LUSD-TAU pair
        tau_purchased = self.dex_lusd.buy(signer='benji', contract='currency', base_amount=300)
        # Buy MARMITE from LUSD-MARMITE pair
        marmite_purchased = self.dex_lusd.buy(signer='marvin', contract='con_marmite100_contract', base_amount=100)

        reserves_rswp = self.dex_currency.reserves['con_rswp_lst001']
        reserves_tau = self.dex_lusd.reserves['currency']
        reserves_marmite = self.dex_lusd.reserves['con_marmite100_contract']

        base_reserve_tau, token_reserve_rswp = reserves_rswp
        base_reserve_lusd_1, token_reserve_tau = reserves_tau
        base_reserve_lusd_2, token_reserve_marmite = reserves_marmite

        price_rswp = base_reserve_tau/token_reserve_rswp
        price_tau = base_reserve_lusd_1/token_reserve_tau
        price_marmite = base_reserve_lusd_2/token_reserve_marmite 

        self.assertEqual(self.rswp.balances['benji'], benji_balance_rswp+rswp_purchased)
        self.assertEqual(self.currency.balances['benji'], benji_balance_tau+tau_purchased-2500)
        self.assertEqual(self.marmite.balances['marvin'], marvin_balance_marmite+marmite_purchased)
        self.assertEqual(self.dex_currency.prices['con_rswp_lst001'], price_rswp)
        self.assertEqual(self.dex_lusd.prices['currency'], price_tau)
        self.assertEqual(self.dex_lusd.prices['con_marmite100_contract'], price_marmite)

    # SELLING

    def test_13_selling_to_different_markets_should_pass(self):
        # Create TAU-RSWP market
        self.dex_currency.create_rswp_market(signer='sys', base_amount=1_000_000, 
            token_amount=2_000_000)
        # Create LUSD-TAU market
        self.dex_lusd.create_market(signer='sys', contract='currency', 
            base_amount=14_000, token_amount=2_000_000)
        # Create LUSD-MARMITE market
        self.dex_lusd.create_market(signer='sys', contract='con_marmite100_contract',
            base_amount=50_000_000, token_amount=2_000_000)

        benji_balance_rswp = self.rswp.balances['benji']
        benji_balance_tau = self.currency.balances['benji']
        marvin_balance_marmite = self.marmite.balances['marvin']

        # Sell RSWP to TAU-RSWP pair
        tau_purchased = self.dex_currency.sell(signer='benji',contract='con_rswp_lst001', token_amount=2500)
        # Sell TAU to LUSD-TAU pair
        self.dex_lusd.sell(signer='benji', contract='currency', token_amount=300)
        # Sell MARMITE to LUSD-MARMITE pair
        self.dex_lusd.sell(signer='marvin', contract='con_marmite100_contract', token_amount=6000)

        reserves_rswp = self.dex_currency.reserves['con_rswp_lst001']
        reserves_tau = self.dex_lusd.reserves['currency']
        reserves_marmite = self.dex_lusd.reserves['con_marmite100_contract']

        base_reserve_tau, token_reserve_rswp = reserves_rswp
        base_reserve_lusd_1, token_reserve_tau = reserves_tau
        base_reserve_lusd_2, token_reserve_marmite = reserves_marmite

        price_rswp = base_reserve_tau/token_reserve_rswp
        price_tau = base_reserve_lusd_1/token_reserve_tau
        price_marmite = base_reserve_lusd_2/token_reserve_marmite 

        self.assertEqual(self.rswp.balances['benji'], benji_balance_rswp - 2500)
        self.assertEqual(self.currency.balances['benji'], benji_balance_tau + tau_purchased - 300)
        self.assertEqual(self.marmite.balances['marvin'], marvin_balance_marmite - 6000)
        self.assertEqual(self.dex_currency.prices['con_rswp_lst001'], price_rswp)
        self.assertEqual(self.dex_lusd.prices['currency'], price_tau)
        self.assertEqual(self.dex_lusd.prices['con_marmite100_contract'], price_marmite)


if __name__ == '__main__':
    unittest.main()


