import numpy as np

I = np.eye(2, dtype=np.complex128)

X = np.array([
    [0, 1],
    [1, 0]
], dtype=np.complex128)

Y = np.array([
    [0, -1j],
    [1j, 0]
], dtype=np.complex128)

Z = np.array([
    [1, 0],
    [0, -1]
], dtype=np.complex128)

H = (1 / np.sqrt(2)) * np.array([
    [1, 1],
    [1, -1]
], dtype=np.complex128)

S_DAG = np.array([
    [1, 0],
    [0, -1j]
], dtype=np.complex128)

CZ = np.diag(np.array([1, 1, 1, -1], dtype=np.complex128)).astype(np.complex128)

def RX(theta: float) -> np.ndarray:
    return np.array([
        [np.cos(theta / 2), -1j * np.sin(theta / 2)],
        [-1j * np.sin(theta / 2), np.cos(theta / 2)]
    ], dtype=np.complex128)

def RY(theta: float) -> np.ndarray:
    return np.array([
        [np.cos(theta / 2), -np.sin(theta / 2)],
        [np.sin(theta / 2), np.cos(theta / 2)]
    ], dtype=np.complex128)

def RZ(theta: float) -> np.ndarray:
    return np.array([
        [np.exp(-1j * theta / 2), 0],
        [0, np.exp(1j * theta / 2)]
    ], dtype=np.complex128)

def RZZ(theta: float) -> np.ndarray:
    return np.diag([
        np.exp(-1j * theta / 2),
        np.exp(1j * theta / 2),
        np.exp(1j * theta / 2),
        np.exp(-1j * theta / 2),
    ]).astype(np.complex128)

def givens_01_10(theta: float) -> np.ndarray:
    '''
    Two-qubit single-excitation Givens rotation.

    Local basis convention:
        |q0 q1> = |00>, |01>, |10>, |11>

    The gate mixes the |01> and |10> local subspace.
    '''
    c = np.cos(theta)
    s = np.sin(theta)
    G = np.eye(4, dtype=np.complex128)
    G[1, 1] = c
    G[1, 2] = -s
    G[2, 1] = s
    G[2, 2] = c
    return G
