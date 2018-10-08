#!/bin/bash -x
#
# This script will create the local configuration file containing the contract addresses
# The docker_keeper_contracts_1 image must be running!!


CONF_TEMPLATE=config.ini
CONF_FILE=config_local.ini

# NB This script is run in the GitHub root folder

# Copy the config template to a local ignored file
cp $CONF_TEMPLATE $CONF_FILE

#PROVIDERDIR=.
#KEEPERDIR=~/Projects/keeper-contracts
#cd $KEEPERDIR

market=$(docker exec -it docker_keeper-contracts_1 python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanMarket.development.json', 'r'))['address'])")
token=$(docker exec -it docker_keeper-contracts_1 python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanToken.development.json', 'r'))['address'])")
auth=$(docker exec -it docker_keeper-contracts_1 python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanAuth.development.json', 'r'))['address'])")

#result=$(docker exec -it docker_keeper-contracts_1 truffle migrate --reset | grep -P 'OceanMarket:|OceanToken:|OceanAuth:')
#values=$(echo $result | sed 's/OceanToken: /token.address=/' | sed 's/OceanMarket: /\nmarket.address=/' | sed 's/OceanAuth: /\nauth.address=/')
#token=$(echo $values | cut -d' ' -f1)
#market=$(echo $values | cut -d' ' -f2)
#auth=$(echo $values | cut -d' ' -f3)
#cp -R $KEEPERDIR/build/contracts $PROVIDERDIR/venv/contracts
sed -i -e "/token.address =/c token.address = ${token}" $CONF_FILE
sed -i -e "/market.address =/c market.address = ${market}" $CONF_FILE
sed -i -e "/auth.address =/c auth.address = ${auth}" $CONF_FILE
#sed -i -e "/provider.address =/c provider.address=" $CONF_FILE

echo Created local configuration from template at $CONF_FILE