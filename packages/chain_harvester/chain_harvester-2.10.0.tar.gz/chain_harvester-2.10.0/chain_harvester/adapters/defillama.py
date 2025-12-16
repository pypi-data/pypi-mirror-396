from decimal import Decimal

from chain_harvester.http import retry_get_json
from chain_harvester.utils import chunks

LLAMA_COINS_API_URL = "https://coins.llama.fi/"


def fetch_current_price(coins):
    """
    Fetches current prices for given coins from DefiLlama API.

    Args:
        coins (list): List of coins in format 'network:address'

    Returns:
        dict: Price data for requested coins
    """
    url = "prices/current/{}".format(",".join(coins))
    data = retry_get_json(f"{LLAMA_COINS_API_URL}{url}?searchWidth=12h")
    return data["coins"]


def get_current_prices(addresses, network="ethereum"):
    """
    Gets current prices for multiple token addresses on specified network.

    Args:
        addresses (list): List of token addresses
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        dict: Price data for requested tokens
    """
    coins = [f"{network}:{address}" for address in addresses]
    data = fetch_current_price(coins)
    return data


def get_price_for_timestamp(address, timestamp, network="ethereum"):
    """
    Gets historical price for a single token address at specific timestamp.

    Args:
        address (str): Token address
        timestamp (int): Unix timestamp
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        Decimal: Token price at timestamp, returns 0 if price not found
    """
    prices = get_prices_for_timestamp([address], timestamp, network)
    if price := prices.get(address):
        return Decimal(str(price))
    return Decimal(0)


def fetch_price_for_timestamp(timestamp, coins):
    """
    Fetches historical prices for given coins at specific timestamp from DefiLlama API.

    Args:
        timestamp (int): Unix timestamp
        coins (list): List of coins in format 'network:address'

    Returns:
        dict: Historical price data for requested coins
    """
    url = "prices/historical/{}/{}".format(int(timestamp), ",".join(coins))
    data = retry_get_json(f"{LLAMA_COINS_API_URL}{url}?searchWidth=12h")
    return data["coins"]


def get_prices_for_timestamp(addresses, timestamp, network="ethereum"):
    """
    Gets historical prices for multiple token addresses at specific timestamp.

    Args:
        addresses (list): List of token addresses
        timestamp (int): Unix timestamp
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        dict: Mapping of token addresses to their prices at timestamp
    """
    coins = [f"{network}:{address}" for address in addresses]
    data = fetch_price_for_timestamp(timestamp, coins)
    result = {}
    if not data:
        return result
    for key, item in data.items():
        if network == "solana":
            address = key.split(":")[1]
        else:
            address = key.split(":")[1].lower()
        result[address] = Decimal(str(item["price"]))
    return result


def get_token_prices(addresses, timestamp, network="ethereum"):
    """
    Gets historical prices for a large list of token addresses, processing them in chunks.

    Args:
        addresses (list): List of token addresses
        timestamp (int): Unix timestamp
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        dict: Mapping of token addresses to their prices at timestamp
    """
    prices = {}
    for chunk in chunks(addresses, 100):
        results = get_prices_for_timestamp(
            chunk,
            timestamp,
            network=network,
        )
        prices.update(results)
    return prices
