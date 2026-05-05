from pathlib import Path
import numpy as np
from vqa_estimator_lab import StateVectorSimulator, X, givens_01_10, encode_hamiltonian_dense, compress_encoded_hamiltonian, greedy_qwc_groups
from vqa_estimator_lab.commutation import best_commuting_groups, validate_commuting_groups
from vqa_estimator_lab.measurement_planning import joint_measurement_plan, summarize_measurement_plan
from vqa_estimator_lab.covariance import allocate_group_shots_covariance_pilot
from vqa_estimator_lab.interop import parse_openfermion_text
def test_best_commuting_groups_valid():
    coeffs,codes=encode_hamiltonian_dense([(1.0,{0:"X",1:"X"}),(1.0,{0:"Y",1:"Y"}),(1.0,{0:"Z",1:"Z"}),(0.5,{0:"Z"})],2)
    groups,meta=best_commuting_groups(coeffs,codes,random_trials=1); assert validate_commuting_groups(codes,groups); assert meta["num_groups"]==len(groups)
def test_measurement_plan_marks_non_qwc_joint():
    coeffs,codes=encode_hamiltonian_dense([(1.0,{0:"X",1:"X"}),(1.0,{0:"Y",1:"Y"})],2)
    groups,_=best_commuting_groups(coeffs,codes,random_trials=1); plan=joint_measurement_plan(coeffs,codes,groups); summary=summarize_measurement_plan(plan)
    assert summary["groups"]==1 and summary["joint_groups"]==1 and plan[0]["requires_joint_measurement_compiler"] is True
def test_covariance_pilot_conserves_budget():
    h2=[(-1.052373245772859,{}),(0.39793742484318045,{0:"Z"}),(-0.39793742484318045,{1:"Z"}),(-0.01128010425623538,{0:"Z",1:"Z"}),(0.18093119978423156,{0:"X",1:"X"})]
    sim=StateVectorSimulator(2); sim.apply_gate(X,0); sim.apply_two_qubit_gate(givens_01_10(0.1117685),0,1)
    coeffs,codes=encode_hamiltonian_dense(h2,2); coeffs,codes=compress_encoded_hamiltonian(coeffs,codes); groups,bases=greedy_qwc_groups(coeffs,codes)
    alloc,diag=allocate_group_shots_covariance_pilot(sim.state,coeffs,codes,groups,bases,total_shots=2000,pilot_fraction=0.1,min_pilot_shots=20,rng=np.random.default_rng(123))
    assert int(alloc.sum())==2000 and len(diag["sigma_hats"])==len(groups)
def test_fixture_openfermion_parse():
    fixture=Path(__file__).resolve().parents[1]/"fixtures"/"h2_toy_reduced_openfermion.txt"
    coeffs,codes=parse_openfermion_text(fixture.read_text()); assert coeffs.shape[0]==5 and codes.shape==(5,2)
