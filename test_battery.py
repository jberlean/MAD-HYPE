import sys
import itertools as it

import numpy as np

from solver_Lee import solve as solve_Lee
from solver_440 import solve as solve_440
from seq_data import SequencingData as SD
from seq_generator import SequencingGenerator as SG

def run_tests(tests):
  ## tests is a list describing a set of runs to perform
  ## Each element of tests is of the following form:
  ##  (<num_reps>,
  ##   <seq_generator_func>,
  ##   <seq_generator_func_args>,
  ##   ((<solver1>, <solver1_args>, <solver1_stats_func>),
  ##    (<solver2>, <solver2_args>, <solver2_stats_func>),
  ##    ...)
  ##  )
  results = []
  for num_reps, seq_gen_func, seq_gen_args, solver_list in tests:
    test_results = []
    for i in range(num_reps):
      data = seq_gen_func(**seq_gen_args)
      rep_results = []
      for solver, args, stats_func in solver_list:
        res = solver(data, **args)
        stats = stats_func(data, res)
        rep_results.append(stats)
      test_results.append(rep_results)
    results.append(test_results)

  return results

def save_test_results(results, path):
  import json
  f = open(path, 'w')
  json.dump(results, f)
      

def run_Lee(data, **solver_kwargs):
  print "Running Lee et al. solver with the following optional arguments:"

  for k,v in solver_kwargs.iteritems():
    print "  {0}: {1}".format(k,v)

  return solve_Lee(data, **solver_kwargs)
def run_440(data, **solver_kwargs):
  print "Running 440 solver with the following optional arguments:"
  for k,v in solver_kwargs.iteritems():
    print "  {}: {}".format(k,v)

  return solve_440(data, **solver_kwargs)

def stats_Lee(data, results):
  def separate_top_tail_clones(fraction = 0.5):
    sorted_freqs, sorted_clones = zip(*sorted(zip(data.metadata['generated_data']['cell_frequencies'], data.metadata['cells']), reverse=True))
    idx_cutoff = len(filter(lambda f: f<fraction, np.cumsum(sorted_freqs)))
    top = sorted_clones[:idx_cutoff]
    tail = sorted_clones[idx_cutoff:]
    return top, tail

  def clones_to_pairings(clones):
    pairings = set()
    for alist,blist in clones:
      pairings |= set(it.product(alist,blist))
    return pairings
    

  true_clones = data.metadata['cells']
  true_pairings = clones_to_pairings(true_clones)
  true_top_clones, true_tail_clones = separate_top_tail_clones()

  true_dual_clones = [c for c in true_clones if len(c[0])>1 or len(c[1])>1]
  true_top_dual_clones = [c for c in true_top_clones if len(c[0])>1 or len(c[1])>1]
  true_tail_dual_clones = [c for c in true_tail_clones if len(c[0])>1 or len(c[1])>1]

  all_alphas, all_betas = zip(*true_clones)
  all_alphas,all_betas = set([a for alist in all_alphas for a in alist]), set([b for blist in all_betas for b in blist])
  obs_alphas, obs_betas = zip(*data.well_data)
  obs_alphas, obs_betas = set(sum(obs_alphas, [])), set(sum(obs_betas, []))

  clones = results['cells']
  dual_clones = [c for c in clones if len(c[0])>1]
  pairings = clones_to_pairings(clones)

  correct_clones = [c for c in clones if c in true_clones]
  correct_top_clones = [c for c in clones if c in true_top_clones]
  correct_tail_clones = [c for c in clones if c in true_tail_clones]

  candidate_dual_clones = [c for c in dual_clones if all([p in pairings for p in it.product(*c)]) and c in true_dual_clones]
  candidate_top_dual_clones = [c for c in candidate_dual_clones if c in true_top_dual_clones]
  candidate_tail_dual_clones = [c for c in candidate_dual_clones if c in true_tail_dual_clones]
  correct_dual_clones = [c for c in dual_clones if c in true_dual_clones]
  correct_top_dual_clones = [c for c in dual_clones if c in correct_top_clones]
  correct_tail_dual_clones = [c for c in dual_clones if c in correct_tail_clones]

  correct_pairings = [p for p in pairings if p in true_pairings]
  incorrect_pairings = [p for p in pairings if p not in true_pairings]

  clone_freqs = results['cell_frequencies']
  clone_freqs_CI = results['cell_frequencies_CI']
  clone_true_freqs = [data.metadata['generated_data']['cell_frequencies'][true_clones.index(c)] if c in true_clones else 0.0 for c in clones]

  #print "", correct_pairings
  #print "", [c for c in clones if c not in correct_clones]

  stats = {
    'num_cells': len(true_clones),
    'num_dual_alpha_cells': len(filter(lambda c: len(c[0])>1, true_clones)),
    'num_dual_beta_cells': len(filter(lambda c: len(c[1])>1, true_clones)),
    'num_alphas': len(all_alphas),
    'num_betas': len(all_betas),
    'num_alphas_obs': len(obs_alphas),
    'num_betas_obs': len(obs_betas),
    'num_top_clones': len(true_top_clones),
    'num_tail_clones': len(true_tail_clones),
    'num_top_dual_clones': len(true_top_dual_clones),
    'num_tail_dual_clones': len(true_tail_dual_clones),
    'num_pred_pairs': len(pairings),
    'num_pred_pairs_correct': len(correct_pairings),
    'num_pred_pairs_incorrect': len(incorrect_pairings),
    'num_pred_clones': len(clones),
    'num_pred_clones_correct': len(correct_clones),
    'num_pred_clones_incorrect': len(clones)-len(correct_clones),
    'num_pred_dual_clones': len(dual_clones),
    'num_pred_dual_clones_correct': len(correct_dual_clones),
    'num_pred_dual_clones_incorrect': len(dual_clones)-len(correct_dual_clones),
    'false_negative_pairs': 1. - float(len(correct_pairings))/len(true_pairings) if len(true_pairings)>0 else float('nan'),
    'false_negative_clones': 1. - float(len(correct_clones))/len(true_clones) if len(true_clones)>0 else float('nan'),
    'false_negative_top_clones': 1. - float(len(correct_top_clones))/len(true_top_clones) if len(true_top_clones)>0 else float('nan'),
    'false_negative_tail_clones': 1. - float(len(correct_tail_clones))/len(true_tail_clones) if len(true_tail_clones)>0 else float('nan'),
    'false_negative_dual_clones': 1. - float(len(correct_dual_clones))/len(true_dual_clones) if len(true_dual_clones)>0 else float('nan'),
    'false_negative_top_dual_clones': 1. - float(len(correct_top_dual_clones))/len(true_top_dual_clones) if len(true_top_dual_clones)>0 else float('nan'),
    'false_negative_tail_dual_clones': 1. - float(len(correct_tail_dual_clones))/len(true_tail_dual_clones) if len(true_tail_dual_clones)>0 else float('nan'),
    'false_negative_dual_clones_adj': 1. - float(len(correct_dual_clones))/len(candidate_dual_clones) if len(candidate_dual_clones)>0 else float('nan'),
    'false_negative_top_dual_clones_adj': 1. - float(len(correct_top_dual_clones))/len(candidate_top_dual_clones) if len(candidate_top_dual_clones)>0 else float('nan'),
    'false_negative_tail_dual_clones_adj': 1. - float(len(correct_tail_dual_clones))/len(candidate_tail_dual_clones) if len(candidate_tail_dual_clones)>0 else float('nan'),
    'false_discovery_pairs': float(len(incorrect_pairings))/len(pairings) if len(pairings)>0 else float('nan'),
    'false_discovery_clones': 1. - float(len(correct_clones))/len(clones) if len(clones)>0 else float('nan'),
    'false_discovery_dual_clones': 1. - float(len(correct_dual_clones))/len(dual_clones) if len(dual_clones)>0 else float('nan'),
    'freq_mse': np.mean([(f1-f2)**2 for f1,f2 in zip(clone_true_freqs, clone_freqs)]),
    'freq_ci_accuracy': np.mean([(f>=f_min and f<=f_max) for f,(f_min,f_max) in zip(clone_true_freqs, clone_freqs_CI)]),
  }

  print "Solution statistics:"
  print "  Total cells (in system):", stats['num_cells']
  print "  # clones in top 50%:", stats['num_top_clones']
  print "  # clones in bottom 50% (tail):", stats['num_tail_clones']
  print "  Total number of dual-alpha cells:", stats['num_dual_alpha_cells']
  print "  Total number of dual-beta cells:", stats['num_dual_beta_cells']
  print "  Number of alpha chains (in system):", stats['num_alphas']
  print "  Number of beta chains (in system):", stats['num_betas']
  print "  Number of alpha chains (observed):", stats['num_alphas_obs']
  print "  Number of beta chains (observed):", stats['num_betas_obs']
  print "  Total pairs identified:", stats['num_pred_pairs']
  print "  Correct pairs identified: {0} ({1}%)".format(stats['num_pred_pairs_correct'], 100*(1 - stats['false_negative_pairs']))
  print "  Incorrect pairs identified: {0}".format(stats['num_pred_pairs_incorrect'])
  print "  False discovery rate (over pairings): {0}%".format(100*stats['false_discovery_pairs'])
  print "  Total clones identified:", stats['num_pred_clones']
  print "  Correct clones identified: {} ({}%)".format(stats['num_pred_clones_correct'], 100*(1-stats['false_negative_clones']))
  print "  Incorrect clones identified:", stats['num_pred_clones_incorrect']
  print "  False discovery rate (over clonotypes): {0}%".format(100*stats['false_discovery_clones'])
  print "  Total dual clones identified:", stats['num_pred_dual_clones']
  print "  Correct dual clones identified: {} ({}%)".format(stats['num_pred_dual_clones_correct'], 100*(1-stats['false_negative_dual_clones']))
  print "  Incorrect dual clones identified:", stats['num_pred_dual_clones_incorrect']
  print "  False discovery rate (over dual-chain clonotypes): {0}%".format(100*stats['false_discovery_dual_clones'])
  print "  Overall depth (over pairs):", 100.*(1-stats['false_negative_pairs'])
  print "  Overall depth (over clones):", 100.*(1-stats['false_negative_clones'])
  print "  Depth of top clones:", 100.*(1-stats['false_negative_top_clones'])
  print "  Depth of tail clones:", 100.*(1-stats['false_negative_tail_clones'])
  print "  Depth of dual clones:", 100.*(1-stats['false_negative_dual_clones'])
  print "  Depth of top dual clones:", 100.*(1-stats['false_negative_top_dual_clones'])
  print "  Depth of tail dual clones:", 100.*(1-stats['false_negative_tail_dual_clones'])
  print "  Depth of dual clones (adj.):", 100.*(1-stats['false_negative_dual_clones_adj'])
  print "  Depth of top dual clones (adj.):", 100.*(1-stats['false_negative_top_dual_clones_adj'])
  print "  Depth of tail dual clones (adj.):", 100.*(1-stats['false_negative_tail_dual_clones_adj'])
  print "  False dual rate:", 100.*stats['false_discovery_dual_clones']

  print "  Mean squared error of frequency guesses: {0}".format(stats['freq_mse'])
  print "  Percent of frequencies within confidence interval: {0}%".format(100.*stats['freq_ci_accuracy'])

  print

  return stats
def stats_440(data, results):
  results['cells'] = [((a,),(b,)) for a,b in results['cells']]
  return stats_Lee(data, results)



def generate_sequencing_data(num_cells, **seq_gen_args):
  gen = SG(**seq_gen_args)
  #gen.cells = SG.generate_cells(num_cells, alpha_dual_prob=0.3, beta_dual_prob=0.06)
  gen.cells = SG.generate_cells(num_cells, alpha_dual_prob=0.0, beta_dual_prob=0.00)
  #gen.set_cell_frequency_distribution(distro_type='explicit', frequencies=generate_cell_freqs(len(gen.cells),50))

  print "Generated data with the following parameters:"
  print "  Number of wells: {0}".format(gen.num_wells)
  print "  Cells/well distribution: {0} ({1})".format(gen.cells_per_well_distribution, gen.cells_per_well_distribution_params)
  
  alphas, betas = zip(*gen.cells)
  alphas,betas = set(alphas),set(betas)
  adeg = float(len(gen.cells))/len(alphas)
  bdeg = float(len(gen.cells))/len(betas)

  print "  Number of cells: {0}".format(len(gen.cells))
  print "  Number of unique alpha chains: {0}".format(len(alphas))
  print "  Number of unique beta chains: {0}".format(len(betas))
  print "  Average sharing of alpha chains: {0}".format(adeg)
  print "  Average sharing of beta chains: {0}".format(bdeg)

  print "  Chain deletion probability: {0}".format(gen.chain_deletion_prob)
  print "  Chain misplacement probability: {0}".format(gen.chain_misplacement_prob)
  print

  return gen.generate_data()
  

tests = [
  (10, 
   generate_sequencing_data,
   {'num_cells': 2100,
    'chain_deletion_prob': 0.15,
    'num_wells': 96*5,
    'cells_per_well_distribution': 'constant',
    'cells_per_well_distribution_params': {'cells_per_well': 50},
    'cell_frequency_distribution': 'Lee',
    'cell_frequency_distribution_params': {'n_s': 50}
   },
   ((run_Lee, {'pair_threshold': 0.3, 'iters':50}, stats_Lee),)
#    (run_Lee, {'pair_threshold': 0.6}, stats_Lee),
#    (run_Lee, {'pair_threshold': 0.3}, stats_Lee),
#    (run_440, {'pair_threshold': 0.90}, stats_440))
  )
]
        
results = run_tests(tests)
#data=tests[0][1](**tests[0][2])
#res=tests[0][3][0][0](data, **tests[0][3][0][1])
#tests[0][3][0][2](data, res)
