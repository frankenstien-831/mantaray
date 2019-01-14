# %% [markdown]
# # Getting Underway - Publishing assets
# In this notebook, we will explore how to publish an Asset using Ocean Protocol.
# As described in the previous notebook, Publish consists of 2 aspects:
#
# 1. Uploading the DDO to Aquarius
# 1. Registering the Asset on the blockchain
#
# *Note to the reader! The current implementation is very low-level, most of the functionality will be wrapped into
# simpler Ocean.publish_dataset() style methods!*
# %% [markdown]
# ### Section 0: Import modules, and setup logging

#%%
# Standard imports
import logging
from pathlib import Path
import os

# Import mantaray and the Ocean API (squid)
import squid_py
from squid_py.ocean.ocean import Ocean
from squid_py.config import Config
# TODO: This will be removed after refactor of .request_tokens()
from squid_py.keeper.web3_provider import Web3Provider
import mantaray_utilities.config as manta_config
import mantaray_utilities.logging as manta_logging
import mantaray_utilities.user as manta_user
import mantaray_utilities.asset_pretty_print as manta_print
from pprint import pprint
# Setup logging
manta_logging.logger.setLevel('CRITICAL')
# from tests.resources.helper_functions import get_registered_access_service_template
#%%
# Get the configuration file path for this environment
# os.environ['USE_K8S_CLUSTER'] = 'true'
CONFIG_INI_PATH = manta_config.get_config_file_path()
logging.critical("Deployment type: {}".format(manta_config.get_deployment_type()))
logging.critical("Configuration file selected: {}".format(CONFIG_INI_PATH))
logging.critical("Squid API version: {}".format(squid_py.__version__))

# %% [markdown]
# ### Section 1: Instantiate a simulated User
# A 'User' in an abstract class representing a user of Ocean Protocol.
#
#%%
# Instantiate Ocean with the default configuration file.
configuration = Config(CONFIG_INI_PATH)
ocn = Ocean(configuration)
# Get the publisher account
publisher_address = configuration['keeper-contracts']['parity.address']
publisher_pass = configuration['keeper-contracts']['parity.password']
publisher_acct = [ocn.accounts[addr] for addr in ocn.accounts if addr.lower() == publisher_address.lower()][0]
publisher_acct.password = publisher_pass

# %% [markdown]
# Your account will need some Ocean Token to make real transactions
# %%
# ensure Ocean token balance
if publisher_acct.ocean_balance == 0:
    tx_hash = publisher_acct.request_tokens(1)
    Web3Provider.get_web3().eth.waitForTransactionReceipt(tx_hash)
# del ocn
#%% [markdown]
# For this tutorial, we will select one of the available unlocked accounts.
#
# In general, as a publisher, you will have your own configuration file with your personal account.

#%% [markdown]
# ### Section 2: Create your MetaData for your asset
# A more complex use case is to manually generate your metadata conforming to Ocean standard, but for demonstration purposes,
# a utility in squid-py is used to generate a sample Meta Data dictionary.

#%%
# Get a simple example of Meta Data from the library directly
metadata = squid_py.ddo.metadata.Metadata.get_example()
print('Name of asset:', metadata['base']['name'])

asset_price = 10 # Ocean Token
service_timeout = 600 # 10 Minutes

# %% [markdown]
# When publishing a dataset, you are actually publishing *access* to the dataset. Access is negotiated by the access agent, called 'Brizo'.
# %%
brizo = squid_py.brizo.brizo_provider.BrizoProvider.get_brizo()
purchase_url = brizo.get_purchase_endpoint(configuration)
service_url = brizo.get_service_endpoint(configuration)
print("To purchase the dataset, a user will call",  purchase_url)
print("To download the dataset, a user will call", service_url)

# %% [markdown]
# These purchase and download functions are packaged into a Service Descriptor.
# In the general case, a dataset is just a type of Asset. An Asset can be any digital asset on Ocean Protocol, including things like
# Compute services, which can have complex access methods, hence the flexibility and composability of Service Descriptors.

# %%
# template = get_registered_access_service_template(ocn, account)
template_ID = squid_py.service_agreement.service_types.ACCESS_SERVICE_TEMPLATE_ID
dataset_access = squid_py.service_agreement.service_factory.ServiceDescriptor.access_service_descriptor
dataset_access_service = dataset_access(asset_price, purchase_url, service_url, service_timeout, template_ID)
service_descriptors = [dataset_access_service]
pprint(service_descriptors)

# %% [markdown]
# The asset has been constructed, we are ready to publish to Ocean Protocol!
# %%
ddo = ocn.register_asset(metadata, publisher_acct, service_descriptors)
print("New asset registered at", ddo.did)

#%%
# Register this asset into Ocean
ddo = publisher_account.ocn.register_asset(
    metadata, publisher_account.ocn.main_account.address,
    [this_service_desc(7, purchase_endpoint, service_endpoint, 360, template_id)])
print("DDO created and registered!")
print("DID:", ddo.did)
# rcpt = publisher1.account.request_tokens(5)
# publisher1.ocn._web3.eth.waitForTransactionReceipt(rcpt)
#%%
# Inspect the new DDO
print("did:", ddo.did)
manta_print.print_ddo(ddo)

