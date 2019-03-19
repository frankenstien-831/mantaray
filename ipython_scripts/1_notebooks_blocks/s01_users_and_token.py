# %% [markdown]
# # Getting Underway - wallets, passwords and tokens
#
# To interact in Ocean Protocol, you will need an account, which you will fund with Token to access the assets
# in the network.
#
# In this notebook, we will demonstrate this behaviour with pre-loaded accounts.
#
# To use Ocean, a User requires
# - A user account address
# - A password
# - Ocean Token

# %% [markdown]
# ### Section 0: Import modules, and setup logging
#%%
# Standard imports
import logging
import random
from pprint import pprint

# Import mantaray and the Ocean API (squid)
# mantaray_utilities is an extra helper library to simulate interactions with the Ocean API.
import squid_py
from squid_py.ocean.ocean import Ocean
from squid_py.config import Config
import mantaray_utilities as manta_utils
# Setup logging to a higher level and not flood the console with debug messages
manta_utils.logging.logger.setLevel('INFO')
logging.info("Squid API version: {}".format(squid_py.__version__))
print("squid-py Ocean API version:", squid_py.__version__)
#%%
# Get the configuration file path for this environment
# You can specify your own configuration file at any time, and pass it to the Ocean class.
logging.critical("Deployment type: {}".format(manta_utils.config.get_deployment_type()))
CONFIG_INI_PATH = manta_utils.config.get_config_file_path()
logging.critical("Configuration file selected: {}".format(CONFIG_INI_PATH))

# %% [markdown]
# ## Section 1: Examine the configuration object
#%%
# The API can be configured with a file or a dictionary.
# In this case, we will instantiate from file, which you may also inspect.
# The configuration is a standard library [configparser.ConfigParser()](https://docs.python.org/3/library/configparser.html) object.
print("Configuration file:", CONFIG_INI_PATH)
configuration = Config(CONFIG_INI_PATH)
pprint(configuration._sections)

# %% [markdown]
# Let's look at the 2 parameters that define your identity
# The 20-byte 'parity.address' defines your account address
# 'parity.password' is used to decrypt your private key and securely sign transactions
#%%
user1_address = configuration['keeper-contracts']['parity.address']
user1_pass = configuration['keeper-contracts']['parity.password']
print("Currently selected address:", user1_address)
print("Associated password:", user1_pass)

# %% [markdown]
# Alternatively, for the purposes of these demos, a list of passwords for local and cloud testing are available.
# Several utility functions have been created to manage these passwords for testing multiple users.

#%%
# Load the passwords file
path_passwords = manta_utils.config.get_project_path() / 'passwords.csv'
passwords = manta_utils.user.load_passwords(path_passwords)
user1_pass = manta_utils.user.password_map(user1_address, passwords)

# %% [markdown]
# ## Section 2: Instantiate the Ocean API class with this configuration
# The Ocean API has an attribute listing all created (simulated) accounts in your local node
# %%
ocn = Ocean(configuration)
logging.critical("Ocean smart contract node connected ".format())

# %% [markdown]
# An account has a balance of Ocean Token, Ethereum, and requires a password to sign any transactions. Similar to
# Ethereum, Ocean Tokens are divisible into the smallest unit of 10^18 of 1 token.

# %%
# List the accounts in the network
print(len(ocn.accounts.list()), "accounts exist")

# Print a simple table listing accounts and balances
print("{:<5} {:<45} {:<20} {:<12} {}".format("","Address", "Ocean Token Balance", "Password?", "ETH balance"))
for i, acct in enumerate(ocn.accounts.list()):
    acct_balance = ocn.accounts.balance(acct)
    acct.password = manta_utils.user.password_map(acct.address, passwords)
    if acct.password:
        flg_password_exists = True
    else:
        flg_password_exists = False
    print("{:<5} {:<45} {:<20.0f} {:<12} {:0.0f}".format(i,acct.address, acct_balance.ocn/10**18, flg_password_exists, acct_balance.eth/10**18))

# %%
# Randomly select an account with a password
main_account = random.choice([acct for acct in ocn.accounts.list() if manta_utils.user.password_map(acct.address, passwords)])

# %% [markdown]
# ### It is never secure to send your password over an unsecured HTTP connection, this is for demonstration only!
# To interact with Ocean Protocol, use a wallet provider or the MetaMask browser extension.
# See our documentation page for setting up your Ethereum accounts!
#
# Most of your interaction with the Ocean Protocol blockchain smart contracts will require your Password.

# %% [markdown]
# ## Requesting tokens
# For development and testing, we have a magical function which will give you free testnet Ocean Token!
#
# Your balance should be increased by 1 - but only after the block has been mined! Try printing your balance
# multiple times until it updates.
# %%
print("Starting Ocean balance: {:0.2f}".format(ocn.accounts.balance(main_account).ocn/10**18))
success = ocn.accounts.request_tokens(main_account, 1)
# The result will be true or false
assert success

#%%
# Execute this after some time has passed to see the update!
print("Updated Ocean balance: {:0.2f}".format(ocn.accounts.balance(main_account).ocn/10**18))

# %% [markdown]
# ## Asynchronous interactions
# Many methods in the API will include a call to
# [.waitForTransactionReceipt(transaction_hash)](https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.waitForTransactionReceiptj),
# which explicitly pauses execution until the transaction has been mined. This will return the Transaction Receipt. When interacting
# with the blockchain, things my take some time to execute!
