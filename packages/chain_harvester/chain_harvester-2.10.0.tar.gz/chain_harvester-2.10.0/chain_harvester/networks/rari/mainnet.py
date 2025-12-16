from chain_harvester.chain import Chain

from chain_harvester.mixins import BlockscoutMixin


class RariMainnetChain(BlockscoutMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="rari",
            network="mainnet",
            blockscout_url="https://rari.calderaexplorer.xyz",
            **kwargs,
        )
