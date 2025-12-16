from chain_harvester.adapters import defillama


def get_tokens_prices(addresses, timestamp, network="ethereum"):
    return defillama.get_token_prices(addresses, timestamp, network)
