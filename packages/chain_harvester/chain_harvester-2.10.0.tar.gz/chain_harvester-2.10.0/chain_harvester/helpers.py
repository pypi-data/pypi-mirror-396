from chain_harvester.networks.arbitrum.mainnet import ArbitrumMainnetChain
from chain_harvester.networks.avalanche.mainnet import AvalancheMainnetChain
from chain_harvester.networks.base.mainnet import BaseMainnetChain
from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from chain_harvester.networks.filecoin.mainnet import FilecoinMainnetChain
from chain_harvester.networks.gnosis.mainnet import GnosisMainnetChain
from chain_harvester.networks.optimism.mainnet import OptimismMainnetChain
from chain_harvester.networks.polygon.mainnet import PolygonMainnetChain
from chain_harvester.networks.rari.mainnet import RariMainnetChain
from chain_harvester.networks.scroll.mainnet import ScrollMainnetChain


def get_chain(network, *args, **kwargs):
    match network:
        case "ethereum":
            return EthereumMainnetChain(*args, **kwargs)
        case "polygon":
            return PolygonMainnetChain(*args, **kwargs)
        case "optimism":
            return OptimismMainnetChain(*args, **kwargs)
        case "arbitrum":
            return ArbitrumMainnetChain(*args, **kwargs)
        case "base":
            return BaseMainnetChain(*args, **kwargs)
        case "scroll":
            return ScrollMainnetChain(*args, **kwargs)
        case "filecoin":
            return FilecoinMainnetChain(*args, **kwargs)
        case "rari":
            return RariMainnetChain(*args, **kwargs)
        case "avalanche":
            return AvalancheMainnetChain(*args, **kwargs)
        case "gnosis":
            return GnosisMainnetChain(*args, **kwargs)
        case _:
            raise ValueError(f"Unknown network: {network}")
