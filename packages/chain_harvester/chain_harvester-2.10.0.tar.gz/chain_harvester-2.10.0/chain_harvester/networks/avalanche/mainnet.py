from chain_harvester.chain import Chain
from chain_harvester.mixins import RoutescanMixin


class AvalancheMainnetChain(RoutescanMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="avalanche", network="mainnet", **kwargs)
