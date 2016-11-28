import openpathsampling as p
import tasks as t
from openpathsampling.engines.openmm import create_simple_openmm_from_pdb
from tqdm import tqdm

engine, template = create_simple_openmm_from_pdb('../examples/AD_initial_frame.pdb')

total_trajs = 20

trajs = [t.generate.delay(
        engine, template, p.LengthEnsemble(50), init_args=['CPU']
    ) for x in range(total_trajs)]

running = True

progress_bar = tqdm(total=total_trajs)

finished = 0

while running:
    running = False

    cc = 0
    for traj in trajs:

        if not traj.state == 'SUCCESS':
            running = True
        else:
            cc += 1

    if cc > finished:
        progress_bar.update(cc - finished)
        finished = cc

progress_bar.close()

for traj in trajs:
    print traj.result

print 'DONE!'
