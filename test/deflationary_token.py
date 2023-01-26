# required, holds all account balances and allowances
balances = Hash(default_value=0)
tax = decimal('0.1')

# Optional: for minting an initial supply to an account
@construct
def seed(vk: str):
    balances[vk] = 1_000_000_000_000 # change this value to alter the inital token supply
    balances['pot'] = 0
    balances['con_dex_lusd'] = 0

# The main transfer function
@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'

    # remove amount from senders account
    balances[ctx.caller] -= amount
    # add amount to receivers account
    balances[to] += amount

# Call to allow another account the abilty to transfer an amount on your behalf
@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    # Add the amount to the callers
    balances[ctx.caller, to] += amount

# Call to spend an amount from another users account; requires prior approval by that account to you
@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    assert balances[main_account, ctx.caller] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, ctx.caller], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'

    # reduce the approval amount by the amount being spent
    balances[main_account, ctx.caller] -= amount

    # remove amount spent from the main account
    balances[main_account] -= amount - (amount * tax)
    # add the amount spent to the receivers account
    balances[to] += amount - (amount * tax)
    balances['pot'] += amount * tax