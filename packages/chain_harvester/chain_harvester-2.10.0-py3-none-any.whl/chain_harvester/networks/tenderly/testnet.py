from chain_harvester.chain import Chain
from chain_harvester.mixins import TenderlyMixin


class TenderlyTestNetChain(TenderlyMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="tenderly", network="testnet", **kwargs)
