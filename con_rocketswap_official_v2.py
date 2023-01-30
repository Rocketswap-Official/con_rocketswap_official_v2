I = importlib

v1_state = ForeignHash(foreign_contract='con_rocketswap_official_v1_1', foreign_name='state')
v1_discount = ForeignHash(foreign_contract='con_rocketswap_official_v1_1', foreign_name='discount')

token_interface = [I.Func('transfer', args=('amount', 'to')), I.Func(
    'approve', args=('amount', 'to')), I.Func('transfer_from', args=(
    'amount', 'to', 'main_account'))]

base = Variable()
pairs = Hash()
prices = Hash()
lp_points = Hash()
reserves = Hash(default_value=[0, 0])
state = Hash()

@construct
def init(base_contract: str):
    base.set(base_contract)
    state['OWNER'] = ctx.caller

@export
def create_market(contract: str, base_amount: float=0, token_amount:
    float=0):
    assert contract != base.get(), 'Cannot create a market for the base token!'
    assert pairs[contract] is None, 'Market already exists!'
    assert contract != v1_state['TOKEN_CONTRACT'], 'Only operator can create this market!'
    assert base_amount > 0 and token_amount > 0, 'Must provide base amount and token amount!'
    
    base_token = I.import_module(base.get())
    token = I.import_module(contract)
    assert I.enforce_interface(base_token, token_interface
        ), 'Invalid token interface!'
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'

    real_base_amount = balance_difference(base_token, contract=base.get(), 
        amount=base_amount)

    real_token_amount = balance_difference(token, contract=contract, 
        amount=token_amount)

    prices[contract] = real_base_amount / real_token_amount
    pairs[contract] = True
    lp_points[contract, ctx.caller] = 100
    lp_points[contract] = 100
    reserves[contract] = [real_base_amount, real_token_amount]
    return True

@export
def liquidity_balance_of(contract: str, account: str):
    return lp_points[contract, account]

@export
def add_liquidity(contract: str, base_amount: float=0):
    assert pairs[contract] is True, 'Market does not exist!'
    assert base_amount > 0
    base_token = I.import_module(base.get())
    token = I.import_module(contract)
    assert I.enforce_interface(base_token, token_interface
        ), 'Invalid token interface!'
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'

    token_amount = base_amount / prices[contract]

    # v2_base_balance_1 = base_balance[ctx.this]
    # base_token.transfer_from(amount=base_amount, to=ctx.this,
    #     main_account=ctx.caller)
    # v2_base_balance_2 = base_balance[ctx.this]
    # real_base_amount = v2_base_balance_2 - v2_base_balance_1

    real_base_amount = balance_difference(base_token, contract=base.get(), amount=base_amount)

    # v2_token_balance_1 = token_balance[ctx.this]
    # token.transfer_from(amount=token_amount, to=ctx.this, main_account=ctx.
    #     caller)
    # v2_token_balance_2 = token_balance[ctx.this]
    # real_token_amount = v2_token_balance_2 - v2_token_balance_1

    real_token_amount = balance_difference(token, contract=contract, amount=token_amount)

    total_lp_points = lp_points[contract]
    base_reserve, token_reserve = reserves[contract]
    points_per_base = total_lp_points / base_reserve
    lp_to_mint = points_per_base * real_base_amount
    lp_points[contract, ctx.caller] += lp_to_mint
    lp_points[contract] += lp_to_mint
    reserves[contract] = [base_reserve + real_base_amount, 
        token_reserve + real_token_amount]
    return lp_to_mint

@export
def remove_liquidity(contract: str, amount: float=0):
    assert pairs[contract] is True, 'Market does not exist!'
    assert amount > 0, 'Must be a positive LP point amount!'
    assert lp_points[contract, ctx.caller
        ] >= amount, 'Not enough LP points to remove!'
    base_token = I.import_module(base.get())
    token = I.import_module(contract)
    assert I.enforce_interface(base_token, token_interface
        ), 'Invalid token interface!'
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'
    lp_percentage = amount / lp_points[contract]
    base_reserve, token_reserve = reserves[contract]
    base_amount = base_reserve * lp_percentage
    token_amount = token_reserve * lp_percentage
    base_token.transfer(to=ctx.caller, amount=base_amount)
    token.transfer(to=ctx.caller, amount=token_amount)
    lp_points[contract, ctx.caller] -= amount
    lp_points[contract] -= amount
    assert lp_points[contract] > 1, 'Not enough remaining liquidity!'
    new_base_reserve = base_reserve - base_amount
    new_token_reserve = token_reserve - token_amount
    assert new_base_reserve > 0 and new_token_reserve > 0, 'Not enough remaining liquidity!'
    reserves[contract] = [new_base_reserve, new_token_reserve]
    return base_amount, token_amount

@export
def transfer_liquidity(contract: str, to: str, amount: float):
    assert amount > 0, 'Must be a positive LP point amount!'
    assert lp_points[contract, ctx.caller
        ] >= amount, 'Not enough LP points to transfer!'
    lp_points[contract, ctx.caller] -= amount
    lp_points[contract, to] += amount

@export
def approve_liquidity(contract: str, to: str, amount: float, ctx_to_signer: bool=False):
    assert amount > 0, 'Cannot send negative balances!'
    if ctx_to_signer is True:
        lp_points[contract, ctx.signer, to] += amount
    else:
        lp_points[contract, ctx.caller, to] += amount

@export
def transfer_liquidity_from(contract: str, to: str, main_account: str,
    amount: float):
    assert amount > 0, 'Cannot send negative balances!'
    assert lp_points[contract, main_account, ctx.caller
        ] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'.format(
        lp_points[main_account, ctx.caller], amount)
    assert lp_points[contract, main_account
        ] >= amount, 'Not enough coins to send!'
    lp_points[contract, main_account, ctx.caller] -= amount
    lp_points[contract, main_account] -= amount
    lp_points[contract, to] += amount

@export
def buy(contract: str, base_amount: float, minimum_received: float=0,
    token_fees: bool=False):
    assert pairs[contract] is True, 'Market does not exist!'
    assert base_amount > 0, 'Must provide base amount!'
    base_token = I.import_module(base.get())
    token = I.import_module(contract)
    amm_token = I.import_module(v1_state['TOKEN_CONTRACT'])
    assert I.enforce_interface(base_token, token_interface
        ), 'Invalid token interface!'
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'

    if contract == v1_state['TOKEN_CONTRACT']:
        real_base_amount = balance_difference(base_token, contract=base.get(), 
            amount=base_amount)

        tokens_purchased = internal_buy(contract=v1_state['TOKEN_CONTRACT'
             ], base_amount=real_base_amount)

        token.transfer(amount=tokens_purchased, to=ctx.caller)
        return tokens_purchased

    real_base_amount = balance_difference(base_token, contract=base.get(), 
        amount=base_amount)

    if isinstance(real_base_amount, int):
        real_base_amount = decimal(f'{real_base_amount}')

    base_reserve, token_reserve = reserves[contract]
    k = base_reserve * token_reserve
    new_base_reserve = base_reserve + real_base_amount
    new_token_reserve = k / new_base_reserve
    tokens_purchased = token_reserve - new_token_reserve
    fee_percent = v1_state['FEE_PERCENTAGE'] * v1_discount[ctx.caller]
    fee = tokens_purchased * fee_percent
    
    if token_fees is True:
        fee = fee * v1_state['TOKEN_DISCOUNT']
        rswp_k = base_reserve * token_reserve
        rswp_new_token_reserve = token_reserve + fee
        rswp_new_base_reserve = rswp_k / rswp_new_token_reserve
        rswp_base_purchased = base_reserve - rswp_new_base_reserve
        rswp_base_purchased += rswp_base_purchased * fee_percent
        rswp_base_reserve_2, rswp_token_reserve_2 = reserves[v1_state['TOKEN_CONTRACT']]
        rswp_k_2 = rswp_base_reserve_2 * rswp_token_reserve_2
        rswp_new_base_reserve_2 = (rswp_base_reserve_2 +
            rswp_base_purchased)
        rswp_new_base_reserve_2 += rswp_base_purchased * fee_percent
        rswp_new_token_reserve_2 = rswp_k_2 / rswp_new_base_reserve_2
        sell_amount = rswp_token_reserve_2 - rswp_new_token_reserve_2
        #assert 5 < 1, f'{type(v1_state["BURN_PERCENTAGE"])}' 
        sell_amount_with_fee = sell_amount * v1_state['BURN_PERCENTAGE']
        amm_token.transfer_from(amount=sell_amount, to=ctx.this,
            main_account=ctx.caller)
        base_received = internal_sell(contract=v1_state['TOKEN_CONTRACT'], 
            token_amount=sell_amount_with_fee)
        amm_token.transfer(amount=sell_amount - sell_amount_with_fee, to=
            v1_state['BURN_ADDRESS'])
        token_received = internal_buy(contract=contract, base_amount=
            base_received)
        
        new_base_reserve += reserves[contract][0] - base_reserve #int = d.decimal - int
        new_token_reserve += reserves[contract][1] - token_reserve #float  =  d.decimal - int
        new_token_reserve = new_token_reserve + token_received
    else: 
        tokens_purchased = tokens_purchased - fee
        burn_amount = internal_buy(contract=v1_state['TOKEN_CONTRACT'], base_amount=
            internal_sell(contract=contract, token_amount=fee - fee * v1_state['BURN_PERCENTAGE']))
        new_base_reserve += reserves[contract][0] - base_reserve
        new_token_reserve += reserves[contract][1] - token_reserve
        new_token_reserve = new_token_reserve + fee * v1_state['BURN_PERCENTAGE']
        amm_token.transfer(amount=burn_amount, to=v1_state['BURN_ADDRESS'])
     
    if minimum_received != None:
        assert tokens_purchased >= minimum_received, 'Only {} tokens can be purchased, \
            which is less than your minimum, which is {} tokens.'.format(
            tokens_purchased, minimum_received)
    assert tokens_purchased > 0, 'Token reserve error!'
       
    token.transfer(amount=tokens_purchased, to=ctx.caller)
    reserves[contract] = [new_base_reserve, new_token_reserve]
    prices[contract] = new_base_reserve / new_token_reserve
    return tokens_purchased

@export
def sell(contract: str, token_amount: float, minimum_received: float=0,
    token_fees: bool=False):
    assert pairs[contract] is True, 'Market does not exist!'
    assert token_amount > 0, 'Must provide base amount and token amount!'
    base_token = I.import_module(base.get())
    token = I.import_module(contract)
    amm_token = I.import_module(v1_state['TOKEN_CONTRACT'])
    assert I.enforce_interface(base_token, token_interface
        ), 'Invalid token interface!'
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'

    if contract == v1_state['TOKEN_CONTRACT']:
        real_token_amount = balance_difference(token, contract=contract, 
            amount=token_amount)
        
        base_purchased = internal_sell(contract=v1_state['TOKEN_CONTRACT'], 
            token_amount=real_token_amount)
        base_token.transfer(amount=base_purchased, to=ctx.caller)
        return base_purchased

    real_token_amount = balance_difference(token, contract=contract, 
        amount=token_amount)

    if isinstance(real_token_amount, int):
        real_token_amount = decimal(f'{real_token_amount}')

    base_reserve, token_reserve = reserves[contract]
    k = base_reserve * token_reserve
    new_token_reserve = token_reserve + real_token_amount
    new_base_reserve = k / new_token_reserve
    base_purchased = base_reserve - new_base_reserve
    fee_percent = v1_state['FEE_PERCENTAGE'] * v1_discount[ctx.caller]
    fee = base_purchased * fee_percent
    if token_fees is True:
        fee = fee * v1_state['TOKEN_DISCOUNT']
        rswp_base_reserve, rswp_token_reserve = reserves[v1_state['TOKEN_CONTRACT']]
        rswp_k = rswp_base_reserve * rswp_token_reserve
        rswp_new_base_reserve = rswp_base_reserve + fee
        rswp_new_base_reserve += fee * fee_percent
        rswp_new_token_reserve = rswp_k / rswp_new_base_reserve
        sell_amount = rswp_token_reserve - rswp_new_token_reserve
        sell_amount_with_fee = sell_amount * v1_state['BURN_PERCENTAGE']
        amm_token.transfer_from(amount=sell_amount, to=ctx.this,
            main_account=ctx.caller)
        base_received = internal_sell(contract=v1_state['TOKEN_CONTRACT'], 
            token_amount=sell_amount_with_fee)
        amm_token.transfer(amount=sell_amount - sell_amount_with_fee, to=
            v1_state['BURN_ADDRESS'])
        new_base_reserve = new_base_reserve + base_received
    else:
        base_purchased = base_purchased - fee
        burn_amount = fee - fee * v1_state['BURN_PERCENTAGE']
        new_base_reserve = new_base_reserve + fee * v1_state['BURN_PERCENTAGE']
        token_received = internal_buy(contract=v1_state['TOKEN_CONTRACT'],
            base_amount=burn_amount)
        amm_token.transfer(amount=token_received, to=v1_state['BURN_ADDRESS'])
    if minimum_received != None:
        assert base_purchased >= minimum_received, 'Only {} TAU can be purchased, which is less than your minimum, which is {} TAU.'.format(
            base_purchased, minimum_received)
    assert base_purchased > 0, 'Token reserve error!'
    
    base_token.transfer(amount=base_purchased, to=ctx.caller)
    reserves[contract] = [new_base_reserve, new_token_reserve]
    prices[contract] = new_base_reserve / new_token_reserve
    return base_purchased

@export
def create_rswp_market(base_amount: float=0, token_amount: float=0):
    assert ctx.caller == state['OWNER'], 'Only owner can call this method!'
    assert pairs[v1_state['TOKEN_CONTRACT']] is None, 'Market already exists!'
    assert base_amount > 0 and token_amount > 0, 'Must provide base amount and token amount!'
    
    base_token = I.import_module(base.get())
    amm_token = I.import_module(v1_state['TOKEN_CONTRACT'])
    assert I.enforce_interface(base_token, token_interface
        ), 'Invalid token interface!'
    base_token.transfer_from(amount=base_amount, to=ctx.this,
        main_account=ctx.caller)
    amm_token.transfer_from(amount=token_amount, to=ctx.this, main_account=ctx.
        caller)
    prices[v1_state['TOKEN_CONTRACT']] = base_amount / token_amount
    pairs[v1_state['TOKEN_CONTRACT']] = True
    lp_points[v1_state['TOKEN_CONTRACT'], ctx.caller] = 100
    lp_points[v1_state['TOKEN_CONTRACT']] = 100
    reserves[v1_state['TOKEN_CONTRACT']] = [base_amount, token_amount]
    return True

@export
def sync_reserves(contract: str):
    assert state['SYNC_ENABLED'] is True, 'Sync is not enabled!'
    token = I.import_module(contract)
    token_balance = ForeignHash(foreign_contract=base.get(), foreign_name='balances')
    new_balance = token_balance['ctx.this']
    assert new_balance > 0, 'Cannot be a negative balance!'
    reserves[contract][1] = new_balance
    return new_balance

def balance_difference(token, contract: str, amount: float):
    token_balance = ForeignHash(foreign_contract=contract, foreign_name='balances')

    v2_balance_1 = token_balance[ctx.this]

    token.transfer_from(amount=amount, to=ctx.this, main_account=
        ctx.caller)

    v2_balance_2 = token_balance[ctx.this]

    real_amount = v2_balance_2 - v2_balance_1

    return real_amount
    
def internal_buy(contract: str, base_amount: float):
    assert pairs[contract] is True, 'RSWP Market does not exist!'
    if base_amount <= 0:
        return 0
    token = I.import_module(contract)
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'
    
    base_reserve, token_reserve = reserves[contract]
    #assert 5 < 1, f'{type(base_reserve)}' int
    k = base_reserve * token_reserve
    new_base_reserve = base_reserve + base_amount # type(base_amount) = decimal.decimal
    #assert 5 < 1, f'{type(new_base_reserve)}' decimal.decimal
    new_token_reserve = k / new_base_reserve
    tokens_purchased = token_reserve - new_token_reserve
    fee = tokens_purchased * v1_state['FEE_PERCENTAGE']
    tokens_purchased -= fee
    new_token_reserve += fee
    assert tokens_purchased > 0, 'Token reserve error!'
    reserves[contract] = [new_base_reserve, new_token_reserve]
    prices[contract] = new_base_reserve / new_token_reserve
    return tokens_purchased

def internal_sell(contract: str, token_amount: float):
    assert pairs[contract] is True, 'RSWP Market does not exist!'
    if token_amount <= 0:
        return 0
    token = I.import_module(contract)
    assert I.enforce_interface(token, token_interface
        ), 'Invalid token interface!'
    base_reserve, token_reserve = reserves[contract]
    k = base_reserve * token_reserve
    new_token_reserve = token_reserve + token_amount
    new_base_reserve = k / new_token_reserve
    base_purchased = base_reserve - new_base_reserve
    fee = base_purchased * v1_state['FEE_PERCENTAGE']
    base_purchased -= fee
    new_base_reserve += fee
    assert base_purchased > 0, 'Token reserve error!'
    reserves[contract] = [new_base_reserve, new_token_reserve]
    prices[contract] = new_base_reserve / new_token_reserve
    return base_purchased

