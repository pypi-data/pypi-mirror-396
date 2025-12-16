from chain_harvester.chain import Chain
from chain_harvester.mixins import BlockscoutMixin


class HemiMainnetChain(BlockscoutMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="hemi",
            network="mainnet",
            blockscout_url="https://explorer.hemi.xyz",
            **kwargs,
        )
