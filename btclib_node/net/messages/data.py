from dataclasses import dataclass
from typing import List, Tuple

from btclib import varint
from btclib.blocks import Block, BlockHeader
from btclib.tx import _Tx
from btclib.utils import bytesio_from_binarydata

from btclib_node.net.messages import add_headers


@dataclass
class Tx:
    tx: _Tx

    def serialize(self):
        data = self.tx.serialize()
        return add_headers("tx", data)


@dataclass
class Block:
    block: Block

    def serialize(self):
        data = self.block.serialize()
        return add_headers("block", data)


@dataclass
class Headers:
    headers: List[BlockHeader]

    @classmethod
    def deserialize(cls, data):
        stream = bytesio_from_binarydata(data)
        headers_num = varint.decode(stream)
        headers = []
        for x in range(headers_num):
            header = BlockHeader.deserialize(stream)
            stream.read(1)
            headers.append(header)
        return cls(headers)

    def serialize(self):
        payload = varint.encode(len(self.headers))
        for header in self.headers:
            payload += header.serialize()
            payload += b"\x00"
        return add_headers("headers", payload)


@dataclass
class Blocktxn:
    blockhash: str
    transactions: List[_Tx]

    @classmethod
    def deserialize(cls, data):
        stream = bytesio_from_binarydata(data)
        blockhash = stream.read(32)[::-1].hex()
        num_transactions = varint.decode(stream)
        transactions = []
        for x in range(num_transactions):
            transactions.append(Tx.deserialize(stream))
        return cls(blockhash=blockhash, transactions=transactions)

    def serialize(self):
        payload = bytes.fromhex(self.blockhash)[::-1]
        payload += varint.encode(len(self.transactions))
        for tx in self.transacions:
            payload += tx.serialize()
        return add_headers("blocktxn", payload)


@dataclass
class Inv:
    inventory: List[Tuple[int, str]]

    @classmethod
    def deserialize(cls, data):
        stream = bytesio_from_binarydata(data)
        inventory_length = varint.decode(stream)
        inventory = []
        for x in range(inventory_length):
            item_type = int.from_bytes(stream.read(4), "little")
            item_hash = stream.read(32)[::-1].hex()
            inventory.append((item_type, item_hash))
        return cls(inventory)

    def serialize(self):
        payload = varint.encode(len(self.inventory))
        for item in self.inventory:
            payload += item[0].to_bytes(4, "little")
            payload += bytes.fromhex(item[1])[::-1]
        return add_headers("inv", payload)
