from chain_harvester.chain import Chain
from chain_harvester.mixins import BlockscoutMixin


class ModeMainnetChain(BlockscoutMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="mode",
            network="mainnet",
            blockscout_url="https://explorer.mode.network",
            **kwargs,
        )
