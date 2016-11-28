import openpathsampling as p
import tasks as t
from openpathsampling.engines.openmm import create_simple_openmm_from_pdb

engine, template = create_simple_openmm_from_pdb('../examples/AD_initial_frame.pdb')

traj = t.generate(engine, template, p.LengthEnsemble(100), init_args=['CPU'])

delayed_trajectory = t.generate.delay(engine, template, p.LengthEnsemble(100), init_args=['CPU'])

trajs = [t.generate.delay(engine, template, p.LengthEnsemble(50), init_args=['CPU']) for x in range(20)]

running = True
while running:
    running = False
    for traj in trajs:
        if not traj.successful():
            running = True


for traj in trajs:
    print traj.result