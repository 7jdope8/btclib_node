from dataclasses import dataclass, field
from typing import Dict

from btclib.tx import Tx


@dataclass
class Mempool:
    transactions: Dict[str, Tx] = field(default_factory=lambda: {})

    def get_missing(self, transactions):
        missing = []
        for tx in transactions:
            if tx not in self.transactions:
                missing.append(tx)
        return missing

    def add_tx(self, tx):
        self.transactions[tx.txid] = tx
