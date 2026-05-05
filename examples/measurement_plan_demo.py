import sys
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
from vqa_estimator_lab import encode_hamiltonian_dense, compress_encoded_hamiltonian
from vqa_estimator_lab.commutation import best_commuting_groups
from vqa_estimator_lab.measurement_planning import joint_measurement_plan, summarize_measurement_plan
H=[(1.0,{0:"X",1:"X"}),(1.0,{0:"Y",1:"Y"}),(1.0,{0:"Z",1:"Z"}),(0.5,{0:"Z"})]
coeffs,codes=encode_hamiltonian_dense(H,2); coeffs,codes=compress_encoded_hamiltonian(coeffs,codes)
groups,meta=best_commuting_groups(coeffs,codes)
plan=joint_measurement_plan(coeffs,codes,groups)
print("Best grouping metadata:",meta)
print("Plan summary:",summarize_measurement_plan(plan))
for item in plan: print(item)
