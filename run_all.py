import time
t=time.time()
from pushfold.precompute import build_one, merge, STACKS, STAGES
for stage in STAGES:
    for E in STACKS:
        build_one(stage, E)
merge()
print("ALL DONE %.1fs"%(time.time()-t))
