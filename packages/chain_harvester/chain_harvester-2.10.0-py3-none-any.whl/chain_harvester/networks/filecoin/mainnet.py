from chain_harvester.chain import Chain
from chain_harvester.mixins import FilfoxMixin


class FilecoinMainnetChain(FilfoxMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="filecoin", network="mainnet", **kwargs)
