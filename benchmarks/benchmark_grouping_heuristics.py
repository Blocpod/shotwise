import sys
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
import numpy as np
from vqa_estimator_lab.hamiltonian import compress_encoded_hamiltonian
from vqa_estimator_lab.grouping import greedy_qwc_groups
from vqa_estimator_lab.commutation import greedy_commuting_groups_heuristic, best_commuting_groups, validate_commuting_groups
def random_encoded_hamiltonian(n,t,max_weight=4,seed=123):
    rng=np.random.default_rng(seed); coeffs=np.empty(t+1); codes=np.zeros((t+1,n),dtype=np.int8); coeffs[0]=rng.normal(scale=0.1)
    for k in range(1,t+1):
        coeffs[k]=rng.normal(scale=0.1); w=int(rng.integers(1,min(max_weight,n)+1)); qs=rng.choice(n,size=w,replace=False); ps=rng.integers(1,4,size=w)
        for q,p in zip(qs,ps): codes[k,int(q)]=int(p)
    return compress_encoded_hamiltonian(coeffs,codes)
for terms in [50,100,200]:
    coeffs,codes=random_encoded_hamiltonian(10,terms,seed=9000+terms); qwc,_=greedy_qwc_groups(coeffs,codes); best,meta=best_commuting_groups(coeffs,codes,random_trials=2)
    assert validate_commuting_groups(codes,best)
    print({"terms":terms,"qwc_groups":len(qwc),"best_groups":len(best),"best_heuristic":meta["heuristic"]})
