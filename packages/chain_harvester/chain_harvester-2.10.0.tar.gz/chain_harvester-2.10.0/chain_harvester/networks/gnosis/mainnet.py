from chain_harvester.chain import Chain
from chain_harvester.mixins import EtherscanMixin


class GnosisMainnetChain(EtherscanMixin, Chain):
    def __init__(self, etherscan_api_key, *args, **kwargs):
        super().__init__(
            *args, chain="gnosis", network="mainnet", etherscan_api_key=etherscan_api_key, **kwargs
        )
