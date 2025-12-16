from chain_harvester.adapters.alchemy import Alchemy
from chain_harvester.helpers import get_chain


def get_transactions_for_contracts(
    network, contract_addresses, from_block, to_block=None, failed=False, config=None
):
    alchemy = Alchemy(network, "mainnet", rpc=config["rpc"], api_key=config["etherscan_api_key"])
    data = alchemy.get_transactions_for_contracts(
        contract_addresses, from_block, to_block=to_block, failed=failed
    )
    return data


def get_events_for_contracts(
    network, contract_addresses, topics, from_block, to_block=None, config=None
):
    chain = get_chain(network, rpc=config["rpc"], api_key=config["etherscan_api_key"])
    return chain.get_events_for_contracts_topics(
        contract_addresses, topics, from_block, to_block=to_block
    )


def get_topics_for_contract(network, contract_address, config=None):
    chain = get_chain(network, rpc=config["rpc"], api_key=config["etherscan_api_key"])
    return chain.abi_to_event_topics(contract_address)
