import importlib

from .exceptions import ChainlinkMissingAsset, ChainlinkMissingChain, ChainlinkMissingMapping


def get_usd_price_feed_for_asset_symbol(symbol, chain, network):
    symbol = symbol.upper()

    try:
        module = importlib.import_module(f".chainlink.mappings.{chain}", package="chain_harvester")
    except ModuleNotFoundError as e:
        raise ChainlinkMissingChain(f"Missing Chainlink mapping for chain: {chain}") from e

    attr = f"{network}_USD".upper()
    try:
        feed = getattr(module, attr)
    except AttributeError as e:
        raise ChainlinkMissingMapping(f"Missing Chainlink mapping for network: {network}") from e

    mapping_attr = f"{network}_ASSET_MAPPING".upper()
    if hasattr(module, mapping_attr):
        mapped_symbol = getattr(module, mapping_attr).get(symbol)
        if mapped_symbol:
            symbol = mapped_symbol

    feed_data = feed.get(symbol)
    if not feed_data:
        raise ChainlinkMissingAsset(f"Missing Chainlink USD price feed for asset: {symbol}")

    # If proxy is set, return proxy, otherwise contract address
    return feed_data["proxy_address"] or feed_data["contract_address"]
