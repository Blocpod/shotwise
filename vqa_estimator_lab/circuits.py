from __future__ import annotations

import numpy as np

class Circuit:
    '''
    Lightweight declarative circuit.

    Gate names are intentionally simple and can be exported to an OpenQASM-like
    representation by adapters.py. Matrix execution is left to callers/backends.
    '''
    def __init__(self, num_qubits: int):
        self.num_qubits = int(num_qubits)
        self.operations = []

    def add(self, name: str, qubits, params=None):
        if isinstance(qubits, int):
            qubits = [qubits]
        self.operations.append({
            "name": str(name).lower(),
            "qubits": [int(q) for q in qubits],
            "params": [] if params is None else [float(x) for x in params],
        })
        return self

    def ry(self, theta: float, q: int):
        return self.add("ry", [q], [theta])

    def rx(self, theta: float, q: int):
        return self.add("rx", [q], [theta])

    def x(self, q: int):
        return self.add("x", [q])

    def h(self, q: int):
        return self.add("h", [q])

    def cz(self, q0: int, q1: int):
        return self.add("cz", [q0, q1])

    def to_dict(self):
        return {
            "num_qubits": self.num_qubits,
            "operations": list(self.operations),
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(int(data["num_qubits"]))
        for op in data["operations"]:
            c.add(op["name"], op["qubits"], op.get("params", []))
        return c
