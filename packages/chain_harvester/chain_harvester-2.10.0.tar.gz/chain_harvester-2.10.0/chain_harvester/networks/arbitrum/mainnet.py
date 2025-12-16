from chain_harvester.chain import Chain
from chain_harvester.mixins import EtherscanMixin


class ArbitrumMainnetChain(EtherscanMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="arbitrum", network="mainnet", **kwargs)
