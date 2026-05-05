import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vqa_estimator_lab import encode_hamiltonian_dense, compress_encoded_hamiltonian
from vqa_estimator_lab.grouping import greedy_qwc_groups
from vqa_estimator_lab.commutation import greedy_commuting_groups, validate_commuting_groups

H = [
    (1.0, {0: "X", 1: "X"}),
    (1.0, {0: "Y", 1: "Y"}),
    (1.0, {0: "Z", 1: "Z"}),
    (0.5, {0: "Z"}),
]

def main():
    coeffs, codes = encode_hamiltonian_dense(H, 2)
    coeffs, codes = compress_encoded_hamiltonian(coeffs, codes)

    qwc, qwc_bases = greedy_qwc_groups(coeffs, codes)
    general = greedy_commuting_groups(coeffs, codes)

    print("QWC groups:", qwc)
    print("QWC bases:", [b.tolist() for b in qwc_bases])
    print("General commuting groups:", general)
    print("General groups valid:", validate_commuting_groups(codes, general))

if __name__ == "__main__":
    main()
