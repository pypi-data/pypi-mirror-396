from functools import lru_cache

import requests
from eth_abi import decode, encode
from eth_utils import function_signature_to_4byte_selector
from web3 import Web3

from chain_harvester.constants import (
    MULTICALL2_ADDRESSES,
    MULTICALL3_ADDRESSES,
    MULTICALL3_BYTECODE,
    NO_STATE_OVERRIDE,
)


def split_calls(calls):
    """
    Split calls into 2 batches in case request is too large.
    """
    center = len(calls) // 2
    chunk_1 = calls[:center]
    chunk_2 = calls[center:]
    return chunk_1, chunk_2


def state_override_supported(chain_id):
    if chain_id in NO_STATE_OVERRIDE:
        return None
    return MULTICALL3_BYTECODE


class Call:
    def __init__(
        self,
        target,
        function,
        returns=None,
        block_identifier=None,
        state_override_code=None,
        _w3=None,
    ):
        self.target = Web3.to_checksum_address(target)
        self.returns = returns
        self.block_identifier = block_identifier
        self.state_override_code = state_override_code
        self.w3 = _w3

        if isinstance(function, list):
            self.function, *self.args = function
        else:
            self.function = function
            self.args = None

        self.signature = Signature(self.function)

    @property
    def data(self) -> bytes:
        return self.signature.encode_data(self.args)

    def decode_output(self, output, success=None):
        if success is None:
            apply_handler = lambda handler, value: handler(value)
        else:
            apply_handler = lambda handler, value: handler(success, value)

        if success is None or success:
            try:
                decoded = self.signature.decode_data(output)
            except:  # noqa: E722
                success, decoded = False, [None] * len(self.returns or [])
        else:
            decoded = [None] * len(self.returns)
        if self.returns:
            return {
                name: apply_handler(handler, value) if handler else value
                for (name, handler), value in zip(self.returns, decoded, strict=False)
            }
        else:
            return decoded if len(decoded) > 1 else decoded[0]

    def __call__(self, args=None):
        args = args or self.args
        calldata = self.signature.encode_data(args)

        args = [{"to": self.target, "data": calldata}, self.block_identifier]

        if self.state_override_code:
            args.append({self.target: {"code": self.state_override_code}})

        output = self.w3.eth.call(*args)

        return self.decode_output(output)


class Multicall:
    def __init__(
        self,
        calls,
        chain_id,
        block_identifier=None,
        require_success=True,
        _w3=None,
    ):
        self.calls = calls
        self.block_identifier = block_identifier
        self.require_success = require_success
        self.w3 = _w3
        self.chain_id = chain_id
        if require_success is True:
            multicall_map = (
                MULTICALL3_ADDRESSES
                if self.chain_id in MULTICALL3_ADDRESSES
                else MULTICALL2_ADDRESSES
            )
            self.multicall_sig = "aggregate((address,bytes)[])(uint256,bytes[])"
        else:
            multicall_map = (
                MULTICALL3_ADDRESSES
                if self.chain_id in MULTICALL3_ADDRESSES
                else MULTICALL2_ADDRESSES
            )
            self.multicall_sig = (
                "tryBlockAndAggregate(bool,(address,bytes)[])(uint256,uint256,(bool,bytes)[])"
            )
        self.multicall_address = multicall_map[self.chain_id]

        self.state_override_code = state_override_supported(self.chain_id)

    def __call__(self):
        result = {}
        for call, (success, output) in zip(self.calls, self.fetch_outputs(), strict=False):
            result.update(call.decode_output(output, success))
        return result

    def fetch_outputs(self, calls=None, ConnErr_retries=0):
        if calls is None:
            calls = self.calls

        aggregate = Call(
            self.multicall_address,
            self.multicall_sig,
            returns=None,
            _w3=self.w3,
            block_identifier=self.block_identifier,
            state_override_code=self.state_override_code,
        )

        try:
            args = self.get_args(calls)
            if self.require_success is True:
                _, outputs = aggregate(args)
                outputs = ((None, output) for output in outputs)
            else:
                _, _, outputs = aggregate(args)
            return outputs
        except requests.ConnectionError as e:
            if (
                "('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"
                not in str(e)
                or ConnErr_retries > 5
            ):
                raise
        except requests.HTTPError as e:
            if "request entity too large" not in str(e).lower():
                raise
        chunk_1, chunk_2 = split_calls(self.calls)
        return list(self.fetch_outputs(chunk_1, ConnErr_retries=ConnErr_retries + 1)) + list(
            self.fetch_outputs(chunk_2, ConnErr_retries=ConnErr_retries + 1)
        )

    def get_args(self, calls):
        if self.require_success is True:
            return [[[call.target, call.data] for call in calls]]
        return [self.require_success, [[call.target, call.data] for call in calls]]


def parse_typestring(typestring):
    if typestring == "()":
        return []
    parts = []
    part = ""
    inside_tuples = 0
    for character in typestring[1:-1]:
        if character == "(":
            inside_tuples += 1
        elif character == ")":
            inside_tuples -= 1
        elif character == "," and inside_tuples == 0:
            parts.append(part)
            part = ""
            continue
        part += character
    parts.append(part)
    return parts


def parse_signature(signature):
    """
    Breaks 'func(address)(uint256)' into ['func', ['address'], ['uint256']]
    """
    parts = []
    stack = []
    start = 0
    for end, character in enumerate(signature):
        if character == "(":
            stack.append(character)
            if not parts:
                parts.append(signature[start:end])
                start = end
        if character == ")":
            stack.pop()
            if not stack:
                parts.append(signature[start : end + 1])
                start = end + 1
    function = "".join(parts[:2])
    input_types = parse_typestring(parts[1])
    output_types = parse_typestring(parts[2])
    return function, input_types, output_types


get_4byte_selector = lru_cache(maxsize=None)(function_signature_to_4byte_selector)


class Signature:
    def __init__(self, signature):
        self.signature = signature
        self.function, self.input_types, self.output_types = parse_signature(signature)

    @property
    def fourbyte(self) -> bytes:
        return get_4byte_selector(self.function)

    def encode_data(self, args=None):
        return self.fourbyte + encode(self.input_types, args) if args else self.fourbyte

    def decode_data(self, output):
        return decode(self.output_types, output)
