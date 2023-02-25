# Symbolic solver
# todo 1. is_symbolic attribute for passives so that either the symbol or the numeric value can be used for this analysis. '''
# todo 2. for filling matrix with impedances, I am going node by node. But for indep sources I am going source by source. Uniformity in logic would be good. (node by node is more logical but computationally much less efficient)

from analysis_helper import solve

def main():
    solve(verbose=False)

if __name__ == "__main__":
    main()