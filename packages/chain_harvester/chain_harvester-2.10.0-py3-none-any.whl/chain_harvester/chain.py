import json
import logging
import os
from collections import defaultdict

import boto3
import eth_abi
import requests
from botocore.exceptions import ClientError
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from web3 import Web3
from web3._utils.rpc_abi import RPC
from web3.exceptions import ContractLogicError, Web3RPCError
from web3.middleware import ExtraDataToPOAMiddleware, validation

from chain_harvester.adapters import sink
from chain_harvester.chainlink import get_usd_price_feed_for_asset_symbol
from chain_harvester.constants import CHAINS, MULTICALL3_ADDRESSES, NULL_ADDRESS
from chain_harvester.decoders import (
    AnonymousEventLogDecoder,
    EventLogDecoder,
    EventRawLogDecoder,
    MissingABIEventDecoderError,
)
from chain_harvester.exceptions import ChainException
from chain_harvester.multicall import Call, Multicall
from chain_harvester.utils.codes import get_code_name

log = logging.getLogger(__name__)

# Disable chain id validation on eth_call method as we're always just fetching data
# and under current assumption we never run any important queries that modify
# the chain
validation.METHODS_TO_VALIDATE = set(validation.METHODS_TO_VALIDATE) - {RPC.eth_call}


class Chain:
    def __init__(
        self,
        chain,
        network,
        rpc=None,
        rpc_nodes=None,
        abis_path=None,
        chain_id=None,
        w3=None,
        step=None,
        s3=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.chain = chain
        self.network = network
        self.chain_id = chain_id or CHAINS[self.chain][self.network]
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.abis_path = abis_path or f"abis/{self.chain}/{self.network}/"
        # Create the abis_path if it doesn't exist yet
        os.makedirs(self.abis_path, exist_ok=True)

        self._w3 = w3

        s3_client = None
        if s3 and s3.get("bucket_name") and s3.get("dir"):
            self.s3_bucket_name = s3.get("bucket_name")
            self.s3_dir = s3.get("dir")
            s3_client = boto3.client("s3", region_name=s3.get("region", "eu-west-1"))
        self.s3 = s3_client

        self.step = step or 10_000
        self.provider = self.rpc

        self._abis = {}
        self._contracts = {}
        self.current_block = 0

    @property
    def w3(self):
        if not self._w3:
            session = requests.Session()
            retries = 3
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=0.5,
                status_forcelist=(429,),
                respect_retry_after_header=True,
                allowed_methods=frozenset(
                    {"DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE", "POST"}
                ),
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            self._w3 = Web3(
                Web3.HTTPProvider(self.rpc, request_kwargs={"timeout": 60}, session=session)
            )
            self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        return self._w3

    @property
    def eth(self):
        return self.w3.eth

    def get_block_info(self, block_number):
        return self.eth.get_block(block_number)

    def get_latest_block(self, true_latest=False):
        if true_latest:
            return self.eth.get_block_number()
        return self.eth.get_block_number() - 5

    def get_abi_from_source(self, contract_address):
        raise NotImplementedError

    def _fetch_abi_from_chain(self, contract_address, refetch_on_block=None):
        proxy_contract = self.get_implementation_address(contract_address, refetch_on_block)
        if proxy_contract != NULL_ADDRESS:
            abi = self.get_abi_from_source(proxy_contract)
        else:
            abi = self.get_abi_from_source(contract_address)
        return abi

    def _fetch_abi_from_s3(self, contract_address):
        key = f"{self.s3_dir}/{self.chain}/{self.network}/{contract_address}.json"
        resp = self.s3.get_object(Bucket=self.s3_bucket_name, Key=key)
        content = resp["Body"].read().decode()
        return json.loads(content)

    def _handle_abi_s3(self, contract_address):
        """Fetch abi from s3 if it exists, otherwise fetch from chain and upload to s3"""
        try:
            abi = self._fetch_abi_from_s3(contract_address)
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchKey":
                raise

            abi = self._fetch_abi_from_chain(contract_address)

            # upload to s3
            key = f"{self.s3_dir}/{self.chain}/{self.network}/{contract_address}.json"
            body = json.dumps(abi)
            self.s3.put_object(
                Bucket=self.s3_bucket_name, Key=key, Body=body, ContentType="application/json"
            )

        self._abis[contract_address] = abi

    def _handle_abi_local_storage(self, contract_address):
        """Fetch abi from local storage if it exists, otherwise fetch from chain and save to local
        storage"""
        file_path = os.path.join(self.abis_path, f"{contract_address}.json")
        if os.path.exists(file_path):
            with open(file_path) as f:
                self._abis[contract_address] = json.loads(f.read())
        else:
            if not os.path.isdir(self.abis_path):
                os.mkdir(self.abis_path)

            log.error(
                "ABI for %s was fetched from 3rd party service. Add it to abis folder!",
                contract_address,
            )
            abi = self._fetch_abi_from_chain(contract_address)

            with open(file_path, "w") as f:
                json.dump(abi, f)
            self._abis[contract_address] = abi

    def load_abi(self, contract_address, refetch_on_block=None, **kwargs):
        contract_address = contract_address.lower()

        # if refetch_on_block is set, we should skip storing the ABI to file as it's
        # usually only used when backpopulating stuff and storing it to the file will
        # replace the current abi with an old one
        if refetch_on_block:
            log.info("Fetching new ABI on block %s without storing it", refetch_on_block)
            return self._fetch_abi_from_chain(contract_address, refetch_on_block)

        if contract_address not in self._abis:
            if self.s3:
                self._handle_abi_s3(contract_address)
            else:
                self._handle_abi_local_storage(contract_address)

        return self._abis[contract_address]

    def get_implementation_address(self, contract_address, block_identifier=None):
        # EIP-1967 storage slot
        contract_address = Web3.to_checksum_address(contract_address)

        # Logic contract address
        slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
        impl_address = self.eth.get_storage_at(
            contract_address, int(slot, 16), block_identifier
        ).hex()
        address = Web3.to_checksum_address(impl_address[-40:])

        #  Beacon contract address
        if address == NULL_ADDRESS:
            try:
                data = self.multicall(
                    [
                        (contract_address, "implementation()(address)", ["address", None]),
                    ],
                    block_identifier=block_identifier,
                )
                address = Web3.to_checksum_address(data["address"])
            except ContractLogicError:
                pass
        return address

    def get_contract(self, contract_address, refetch_on_block=None):
        # This function can be called many, many times, so we cache already instantiated
        # contracts
        contract_address = Web3.to_checksum_address(contract_address)

        if refetch_on_block or contract_address not in self._contracts:
            abi = self.load_abi(contract_address, refetch_on_block=refetch_on_block)
            contract = self.eth.contract(
                address=contract_address,
                abi=abi,
            )
            self._contracts[contract_address] = contract

        return self._contracts[contract_address]

    def call_contract_function(self, contract_address, function_name, *args, **kwargs):
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.get_contract(contract_address)
        contract_function = contract.get_function_by_name(function_name)
        result = contract_function(*args).call(
            block_identifier=kwargs.get("block_identifier", "latest")
        )
        return result

    def get_storage_at(self, contract_address, position, block_identifier=None):
        contract_address = Web3.to_checksum_address(contract_address)
        content = self.eth.get_storage_at(
            contract_address, position, block_identifier=block_identifier
        ).hex()
        return content

    def get_code(self, address):
        address = Web3.to_checksum_address(address)
        return self.eth.get_code(address).hex()

    def is_eoa(self, address):
        return self.get_code(address) == ""

    def _yield_all_events(self, fetch_events_func, from_block, to_block):
        retries = 0
        step = self.step

        min_step = min(int(self.step), 2000)

        while True:
            end_block = min(from_block + step - 1, to_block)
            log.debug(f"Fetching events from {from_block} to {end_block} with step {step}")
            events = fetch_events_func(from_block, end_block)
            if events is None:
                break

            try:
                yield from events
                retries = 0
            except Web3RPCError as e:
                # We're catching Web3RPCError as the limit for each response is either
                # 2000 blocks or 10k logs. Since our step is bigger than 2k blocks, we
                # catch the errors, and retry with smaller step (2k blocks)

                err_code = e.rpc_response["error"]["code"]

                if err_code in [-32602, -32005, -32000]:
                    if retries > 5:
                        raise

                    step /= 5
                    step = max(int(step), min_step)
                    retries += 1
                    continue
                else:
                    raise

            if end_block >= to_block:
                break

            from_block += step
            # Reset step back to self.step in case we did a retry
            step = self.step

    def _decode_raw_log(self, contract, raw_log, mixed, anonymous):
        # In order to not always instantiate new decoder, we store it under a specific
        # key directly on contract in order to cache it
        if hasattr(contract, "_ch_decoder"):
            decoder = contract._ch_decoder
        else:
            decoder = EventRawLogDecoder(contract)
            contract._ch_decoder = decoder

        return decoder.decode_log(raw_log, mixed, anonymous)

    def _generate_fetch_events_func(
        self,
        contracts,
        from_block,
        to_block,
        topics,
        anonymous,
        mixed,
    ):
        def fetch_events_for_contracts_topics(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": contracts,
            }
            if topics:
                filters["topics"] = topics

            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                if (
                    HexBytes("0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b")
                    in raw_log["topics"]
                ):
                    log.warning("Skipping Upgraded event on proxy contract %s", raw_log["address"])
                    continue
                # TODO: Skip BeaconUpgraded event in a similar fashion to the one above

                contract = self.get_contract(raw_log["address"].lower())
                try:
                    data = self._decode_raw_log(contract, raw_log, mixed, anonymous)
                except MissingABIEventDecoderError:
                    log.warning(
                        "Contract ABI (%s) is missing an event definition. Fetching a new "
                        "ABI on block %s",
                        raw_log["address"].lower(),
                        raw_log["blockNumber"],
                    )
                    contract = self.get_contract(
                        raw_log["address"].lower(), refetch_on_block=raw_log["blockNumber"]
                    )
                    data = self._decode_raw_log(contract, raw_log, mixed, anonymous)

                yield data

        return fetch_events_for_contracts_topics

    def get_events_for_contract(self, contract_address, from_block, to_block=None, anonymous=False):
        if not to_block:
            to_block = self.get_latest_block()
        contract_address = Web3.to_checksum_address(contract_address)

        fetch_events_func = self._generate_fetch_events_func(
            contract_address, from_block, to_block, None, anonymous, False
        )

        return self._yield_all_events(fetch_events_func, from_block, to_block)

    def get_events_for_contract_topics(
        self, contract_address, topics, from_block, to_block=None, anonymous=False
    ):
        contract_address = Web3.to_checksum_address(contract_address)
        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = self.get_latest_block()

        fetch_events_func = self._generate_fetch_events_func(
            contract_address, from_block, to_block, topics, anonymous, False
        )

        return self._yield_all_events(fetch_events_func, from_block, to_block)

    def get_events_for_contracts(
        self,
        contract_addresses,
        from_block,
        to_block=None,
        anonymous=False,
        mixed=False,
    ):
        if not isinstance(contract_addresses, list):
            raise TypeError("contract_addresses must be a list")

        if not to_block:
            to_block = self.get_latest_block()

        contracts = [
            Web3.to_checksum_address(contract_address) for contract_address in contract_addresses
        ]

        fetch_events_func = self._generate_fetch_events_func(
            contracts, from_block, to_block, None, anonymous, mixed
        )

        return self._yield_all_events(fetch_events_func, from_block, to_block)

    def get_events_for_contracts_topics(
        self,
        contract_addresses,
        topics,
        from_block,
        to_block=None,
        anonymous=False,
        mixed=False,
    ):
        if not isinstance(contract_addresses, list):
            raise TypeError("contract_addresses must be a list")

        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = self.get_latest_block()

        contracts = [
            Web3.to_checksum_address(contract_address) for contract_address in contract_addresses
        ]

        fetch_events_func = self._generate_fetch_events_func(
            contracts, from_block, to_block, topics, anonymous, mixed
        )

        return self._yield_all_events(fetch_events_func, from_block, to_block)

    def get_events_for_topics(self, topics, from_block, to_block=None, anonymous=False):
        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = self.get_latest_block()

        def fetch_events_for_topics(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "topics": topics,
            }

            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                try:
                    contract = self.get_contract(raw_log["address"].lower())
                except ChainException:
                    log.warning(f"Contract not verified for {raw_log['address']}")
                    continue
                if anonymous:
                    decoder = AnonymousEventLogDecoder(contract)
                else:
                    decoder = EventLogDecoder(contract)
                yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_topics, from_block, to_block)

    def get_latest_event_before_block(self, address, topics, block_number, max_retries=5):
        current_step = self.step
        for _ in range(max_retries):
            events = self.get_events_for_contract_topics(
                address, topics, block_number - self.step + 1, to_block=block_number
            )
            items = list(events)
            if items:
                self.step = current_step
                return items[-1]
            self.step *= 2
        self.step = current_step
        return None

    def multicall(self, calls, block_identifier=None):
        multicalls = []
        for address, function, response in calls:
            multicalls.append(Call(address, function, [response]))

        multi = Multicall(multicalls, self.chain_id, _w3=self.w3, block_identifier=block_identifier)

        return multi()

    def abi_to_event_topics(self, contract_address, events=None, ignore=None):
        if events and not isinstance(events, list):
            raise TypeError("events must be a list")

        contract = self.get_contract(contract_address)
        event_abis = [
            abi
            for abi in contract.abi
            if abi["type"] == "event"
            and (events is None or abi["name"] in events)
            and (ignore is None or abi["name"] not in ignore)
        ]
        signed_abis = {f"0x{event_abi_to_log_topic(abi).hex()}": abi for abi in event_abis}
        return signed_abis

    def get_events_topics(self, contract_address, events=None, ignore=None):
        return list(self.abi_to_event_topics(contract_address, events=events, ignore=ignore).keys())

    def address_to_topic(self, address):
        stripped_address = address[2:]
        topic_format = "0x" + stripped_address.lower().rjust(64, "0")
        return topic_format

    def encode_eth_call_payload(self, contract_address, function_name, block_identifier, args):
        contract = self.get_contract(contract_address)
        output_details = {"output_types": [], "output_names": []}
        for element in contract.abi:
            if element["type"] == "function" and element["name"] == function_name:
                for i in element["outputs"]:
                    output_details["output_types"].append(i["type"])
                    output_details["output_names"].append(i["name"])

        data = contract.encode_abi(abi_element_identifier=function_name, args=args)

        if isinstance(block_identifier, int):
            block_identifier = hex(block_identifier)

        payload = {
            "jsonrpc": "2.0",
            "params": [
                {
                    "to": contract_address,
                    "data": data,
                },
                block_identifier,
            ],
            "method": "eth_call",
        }

        return payload, output_details

    def batch_eth_calls(self, data):
        headers = {"content-type": "application/json"}
        response = requests.post(self.rpc, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()

    def eth_multicall(self, calls):
        if len(calls) > 100:
            raise ValueError("Batch request limit exceeded (limit: 100)")

        outputs_details = {}
        payloads = []
        response = []
        request_id = 1
        for contract_address, function_name, block_identifier, args in calls:
            payload, names_types = self.encode_eth_call_payload(
                contract_address, function_name, block_identifier, args
            )
            payload["id"] = request_id
            payloads.append(payload)
            outputs_details[request_id] = names_types
            request_id += 1
        batch_response = self.batch_eth_calls(payloads)
        for r in batch_response:
            decoded_response = eth_abi.abi.decode(
                outputs_details[r["id"]]["output_types"], bytes.fromhex(r["result"][2:])
            )
            response.append(
                dict(
                    zip(
                        outputs_details[r["id"]]["output_names"],
                        decoded_response,
                        strict=False,
                    )
                )
            )
        return response

    def to_hex_topic(self, topic):
        return "0x" + Web3.keccak(text=topic).hex()

    def get_token_info(self, address, bytes32=False, retry=False):
        calls = []
        calls.append(
            (
                address,
                ["decimals()(uint8)"],
                ["decimals", None],
            )
        )
        if bytes32:
            calls.append(
                (
                    address,
                    ["name()(bytes32)"],
                    ["name", None],
                )
            )
        else:
            calls.append(
                (
                    address,
                    ["name()(string)"],
                    ["name", None],
                )
            )
        if bytes32:
            calls.append(
                (
                    address,
                    ["symbol()(bytes32)"],
                    ["symbol", None],
                )
            )
        else:
            calls.append(
                (
                    address,
                    ["symbol()(string)"],
                    ["symbol", None],
                )
            )
        data = self.multicall(calls)
        if data["symbol"] is None and not retry:
            data = self.get_token_info(address, bytes32=True, retry=True)
            if data["symbol"] is None:
                return data
            data["symbol"] = data["symbol"].decode("utf-8").rstrip("\x00")
            data["name"] = data["name"].decode("utf-8").rstrip("\x00")
        return data

    def get_multicall_address(self):
        return MULTICALL3_ADDRESSES[self.chain_id] if self.chain_id else None

    def create_index(self, block, tx_index, log_index):
        return "_".join((str(block).zfill(12), str(tx_index).zfill(6), str(log_index).zfill(6)))

    def chainlink_price_feed_for_asset_symbol(self, symbol):
        return get_usd_price_feed_for_asset_symbol(symbol, self.chain, self.network)

    def get_timestamp_for_block(self, block_number):
        block_info = None
        if sink.supports_chain(self.chain):
            try:
                block_info = sink.fetch_block_info(self.chain, block_number)
            except Exception:
                log.exception(
                    "Couldn't fetch block info from sink. Block number: %s chain: %s",
                    block_number,
                    self.chain,
                )
            if block_info:
                return block_info["timestamp"]
        return self.get_block_info(block_number).timestamp

    def get_block_for_timestamp(self, timestamp):
        """
        Fetches the block number for a given timestamp.

        Args:
            timestamp (int): The timestamp for which to fetch the block number.

        Returns:
            int: The block number.
        """

        # First try to fetch the block from sink.
        if sink.supports_chain(self.chain):
            try:
                return sink.fetch_nearest_block(self.chain, timestamp)
            except Exception:
                log.exception(
                    "Couldn't fetch nearest block from sink. Timestamp: %s chain: %s",
                    timestamp,
                    self.chain,
                )

        # As a fallback use etherscan or other similar apis
        nearest_block = self.get_block_for_timestamp_fallback(timestamp)
        return nearest_block

    def get_block_for_timestamp_fallback(self, timestamp):
        raise NotImplementedError

    def get_owners_for_proxies(self, addresses, code):
        code_name = get_code_name(code)
        if code_name in ["GnosisSafeProxy", "Proxy", "SafeProxy"]:
            return self.get_owners_for_gnosis_safe(addresses)
        elif code_name in ["AccountImplementation", "DSProxy", "Vault", "CenoaCustomProxy"]:
            return self.get_dsproxy_owners(addresses)
        elif code_name in ["InstaAccountV2"]:
            return self.get_insta_account_owners(addresses)
        else:
            return {}

    def get_owners_for_gnosis_safe(self, addresses):
        calls = []

        results = {}
        for address in addresses:
            calls.append(
                (
                    address,
                    ["getOwners()(address[])"],
                    [address, None],
                )
            )
            if len(calls) == 5000:
                data = self.multicall(calls)
                for address, value in data.items():
                    owners = [owner.lower() for owner in value]
                    results[address] = owners
                calls = []
        if calls:
            data = self.multicall(calls)
            for address, value in data.items():
                owners = [owner.lower() for owner in value]
                results[address] = owners
        return results

    def get_dsproxy_owners(self, addresses):
        calls = []
        results = {}
        for address in addresses:
            calls.append(
                (
                    address,
                    ["owner()(address)"],
                    [address, None],
                )
            )
            if len(calls) == 5000:
                data = self.multicall(calls)
                for address, value in data.items():
                    results[address] = [value.lower()]
                calls = []
        if calls:
            data = self.multicall(calls)
            for address, value in data.items():
                results[address] = [value.lower()]
        return results

    def get_insta_account_owners(self, addresses):
        calls = []
        accounts = {}
        for address in addresses:
            calls.append(
                (
                    "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                    ["accountID(address)(uint64)", address],
                    [f"{address}", None],
                )
            )
        data = self.multicall(calls)

        account_ids = []
        for key, value in data.items():
            account_ids.append(value)
            accounts[value] = key

        owners_mapping = {}
        calls = []
        for account_id in account_ids:
            calls.append(
                (
                    "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                    ["accountLink(uint64)((address,address,uint64))", account_id],
                    [f"{account_id}", None],
                )
            )
            data = self.multicall(calls)
            multiple_owners_insta_ids = []
            for account_id, values in data.items():
                count = values[2]
                if count > 2:
                    multiple_owners_insta_ids.append(
                        {
                            "account_id": account_id,
                            "first": values[0],
                            "last": values[1],
                            "count": count,
                        }
                    )
                else:
                    owners = []
                    for i in range(count):
                        owners.append(values[i])
                owners_mapping[int(account_id)] = owners

            for proxy in multiple_owners_insta_ids:
                count = proxy["count"]
                account_id = proxy["account_id"]
                first = proxy["first"]
                last = proxy["last"]
                owners = [proxy["first"], proxy["last"]]
                calls = []
                while len(owners) < count:
                    calls.append(
                        (
                            "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                            [
                                "accountList(uint64,address)((address,address))",
                                int(account_id),
                                first,
                            ],
                            ["first", None],
                        )
                    )
                    calls.append(
                        (
                            "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                            [
                                "accountList(uint64,address)((address,address))",
                                int(account_id),
                                last,
                            ],
                            ["last", None],
                        )
                    )
                    account_list = self.multicall(calls)

                    owners.append(account_list["first"][1])
                    owners.append(account_list["last"][0])
                    owners = list(set(owners))
                    first = account_list["first"][1]
                    last = account_list["last"][0]
                owners_mapping[int(account_id)] = owners
        results = {}
        for account_id, owners in owners_mapping.items():
            results[accounts[account_id]] = owners

        return results

    def get_erc4626_info(self, address, block_identifier=None):
        calls = [
            (
                address,
                [
                    "name()(string)",
                ],
                ["name", None],
            ),
            (
                address,
                [
                    "symbol()(string)",
                ],
                ["symbol", None],
            ),
            (
                address,
                [
                    "asset()(address)",
                ],
                ["asset", None],
            ),
            (
                address,
                [
                    "decimals()(uint8)",
                ],
                ["decimals", None],
            ),
            (
                address,
                [
                    "totalAssets()(uint256)",
                ],
                ["total_assets", None],
            ),
            (
                address,
                [
                    "totalSupply()(uint256)",
                ],
                ["total_supply", None],
            ),
            (
                address,
                [
                    "convertToAssets(uint256)(uint256)",
                    10 ** (36 - 6),
                ],
                ["convert_to_assets", None],
            ),
        ]

        data = self.multicall(calls, block_identifier=block_identifier)

        return data

    def get_multiple_erc4626_info(self, addresses, block_identifier=None):
        calls = []
        for address in addresses:
            calls.append(
                (
                    address,
                    [
                        "name()(string)",
                    ],
                    [f"{address}::name", None],
                ),
                (
                    address,
                    [
                        "symbol()(string)",
                    ],
                    [f"{address}::symbol", None],
                ),
                (
                    address,
                    [
                        "asset()(address)",
                    ],
                    [f"{address}::asset", None],
                ),
                (
                    address,
                    [
                        "decimals()(uint8)",
                    ],
                    [f"{address}::decimals", None],
                ),
                (
                    address,
                    [
                        "totalAssets()(uint256)",
                    ],
                    [f"{address}::total_assets", None],
                ),
                (
                    address,
                    [
                        "totalSupply()(uint256)",
                    ],
                    [f"{address}::total_supply", None],
                ),
            )

        data = self.multicall(calls, block_identifier=block_identifier)

        result = defaultdict(dict)
        for key, value in data.items():
            address, label = key.split("::")
            result[address][label] = value
        return result
