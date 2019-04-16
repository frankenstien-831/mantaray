# %% [markdown]
# # Getting Underway - Listing and searching registered assets
# In this notebook, we will explore the concept of Assets. An Asset has an ID
# (actually a 'decentralized' ID, called **DID**!).
#
# An Asset also has a document which describes the Asset and how to # authorize and gain access (i.e. purchase the asset).
# This document is called a **DDO**, the DID Document. For Data Scientists, the DDO attribute of note is the 'metadata'
# attribute. Metadata is used to describe your asset, for example the name and description of a Data Set.
#
# The DID is stored in the blockchain. The DDO is stored in a public searchable database, wrapped by the Aquarius
# component.
#
# *Note to the reader: This is a testnet: a simulated blockchain and simulated DDO store. This testnet is open to the
# public, and therefore may change state in unexpected ways (your asset might get deleted, etc.)*

# %% [markdown]
# Further reading!
#
# [W3C early draft standard 'Decentralized Identifiers (DIDs)'](https://w3c-ccg.github.io/did-spec/)
#
# [OEP 7 - Ocean Protocol standard for 'Decentralized Identifiers'](https://github.com/oceanprotocol/OEPs/tree/master/7)
#
# [OEP 7 - Ocean Protocol standard for 'Assets Metadata Ontology'](https://github.com/oceanprotocol/OEPs/tree/master/8)
#

# %% [markdown]
# ### Section 0: Import modules, and setup logging

#%%
# Standard imports
import logging

# Import mantaray and the Ocean API (squid)
import squid_py
from squid_py.ocean.ocean import Ocean
from squid_py.config import Config
import mantaray_utilities as manta_utils

# Setup logging
manta_utils.logging.logger.setLevel('INFO')
print("squid-py Ocean API version:", squid_py.__version__)
#%%
# Get the configuration file path for this environment
CONFIG_INI_PATH = manta_utils.config.get_config_file_path()
logging.critical("Deployment type: {}".format(manta_utils.config.get_deployment_type()))
logging.critical("Configuration file selected: {}".format(CONFIG_INI_PATH))
logging.critical("Squid API version: {}".format(squid_py.__version__))

#%%
# Instantiate Ocean from configuration file
configuration = Config(CONFIG_INI_PATH)
ocn = Ocean(configuration)
# %% [markdown]
# ### Section 1: Assets are stored in the Metadata store (Aquarius) as a DDO
# Anyone can search assets in the public metadata stores. Anyone can start their own metadata instance for thier
# own marketplace.

#%% [markdown]
# The Metadata store is a database wrapped with a REST API.
# The database is accessed with a driver, currently Mongo DB is implemented.
# For more details of functionality, see the documentation and our Swagger API page.
#
# (Aquarius metadata store)[https://github.com/oceanprotocol/aquarius/tree/develop/aquarius]
#
# (MongoDB driver)[https://github.com/oceanprotocol/oceandb-mongodb-driver]
#%%
print("Aquarius metadata database service URL: {}".format(configuration.aquarius_url))

# %% [markdown]
# ### Section 2: Test search
#%%
all_ddos = ocn.assets.search({'asdf'})
# %% [markdown]
# ### Section 2: Listing registered asset metadata in Aquarius
# First, we will retrieve a list of all DID's (Decentralized IDentifiers) from Aquarius using the 'exists' tag.
# This is an example of the low level MongoDB API.
#TODO: Seperate this into utils library, generally a user would not want to list all assets, could be a large list!

#%%
# Use the Query function to get all existing assets
basic_query = {"service":{"$elemMatch":{"metadata": {"$exists" : True }}}}
all_ddos = ocn.assets.query(basic_query)
assert len(all_ddos), "There are no assets registered, go to s03_publish_and_register!"
print("There are {} assets registered in the metadata store.".format(len(all_ddos)))

# %% [markdown]
# Aquarius is a document store, with the key being the DID, and the document being the DDO
# (DID Document). The DDO describes the asset (metadata) and how to access it (Service Execution Agreement).
# For more information on these topics, please visit the Ocean Protocol standards;
#
# [OEP 7 - Decentralized Identifiers](https://github.com/oceanprotocol/OEPs/tree/master/7)
#
# [OEP 7 - Decentralized Identifiers](https://github.com/oceanprotocol/OEPs/tree/master/8)
#
# Let's select an asset DDO for inspection (Note, since the database is stateful, this can easily change/break,
# so try with another index or register your own asset first!)
# %%
# Select a single asset DDO from the list
this_ddo = all_ddos[-1]
print("Selected asset DID: {}".format(this_ddo.did))
print("Asset name:", this_ddo.metadata['base']['name'])
print("Asset price: {} token".format(this_ddo.metadata['base']['price']))
print("Asset description: {} token".format(this_ddo.metadata['base']['description']))

# %% [markdown]
# ### Section 4: Searching the Ocean
# Aquarius supports query search. A list of [DDO] is returned from a search call.
#
# Currently, Aquarius is running MongoDB. For detailed query documentation, see the
# [documentation](https://docs.mongodb.com/manual/reference/method/db.collection.find/)
#
# The exposed query endpoint is a subset of the full MongoDB search capability. For the documentation on the
# Current search implementation, see https://github.com/oceanprotocol/aquarius/blob/develop/docs/for_api_users/API.md

#%%
# Query syntax:
# {
#   "query": {"name_of_query":["parameters"]},
#   "sort": {"field":1},
#   "offset": 100,
#   "page": 0
# }

#%% [markdown]
# #### Select ALL assets
# To get started, the following query will return all documents with a 'price' between 0 and 20.
# The syntax for this query, is a range of integers for the registered price.
#%%
query = {"query":{"price":[0,20]}}
search_results = ocn.assets.query(query)
print("Found {} assets".format(len(search_results)))
print_match_idx = -1
for result in search_results:
    print("Selected asset: {}, price:{}, {}".format(result.metadata['base']['name'],result.metadata['base']['price'], result.did ))

#%% [markdown]
# #### Text search
# Plain text search is supported, searching in all assets
#%%
query = {"query":{"text":["Weather"]}}
search_results = ocn.assets.query(query)
print("Found {} assets".format(len(search_results)))
print_match_idx = -1
for result in search_results:
    print("Selected asset: {}, price:{}, {}".format(result.metadata['base']['name'],result.metadata['base']['price'], result.did ))


#%% [markdown]
# #### Combined search
# Multiple queries can be joined
#%%
query = {"query":{"text":["Weather"],"price":[0,11]}}
search_results = ocn.assets.query(query)
print("Found {} assets".format(len(search_results)))
print_match_idx = -1
for result in search_results:
    print("Selected asset: {}, price:{}, {}".format(result.metadata['base']['name'],result.metadata['base']['price'], result.did ))

# %% [markdown]
# ### Section 5: Cleaning the Ocean
# A DID is registered on the blockchain, and can be resolved to a DID Document (DDO) as presented above.
#
# Since the DDO exists on Aquarius and not in the blockchain, the DDO itself can be deleted. The DID trace can never be
# deleted from the blockchain.

#%%
if 0:

    # Let's count how many ddo's are registered
    all_dids = ocn.assets._get_aquarius().list_assets()
    print("there are {} assets registered in the metadata store.".format(len(all_dids)))

    # let's delete the first ddo object.
    first_did = all_dids[0]
    print("selected ddo for deletion:", first_did)
    ocn.assets._get_aquarius().retire_asset_ddo(first_did)

    # again, let's count how many ddo's are registered
    all_dids = ocn.assets._get_aquarius().list_assets()
    print("there are now {} assets registered in the metadata store.".format(len(all_dids)))

# %%
# Deleting all assets!
# Please don't delete all the assets, as other users may be testing the components!
if 0:
    all_dids = ocn.assets._get_aquarius().list_assets()
    for i, did in enumerate(all_dids):
        print("Deleting DDO {} - {}".format(i, did))
        ocn.assets._get_aquarius().retire_asset_ddo(did)
