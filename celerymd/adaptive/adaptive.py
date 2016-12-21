#!/usr/bin/env python

import os
import sys

# set default verbose level
verbose = os.environ.get('RADICAL_PILOT_VERBOSE', 'REPORT')
os.environ['RADICAL_PILOT_VERBOSE'] = verbose

# set default URL to IMP Mongo DB
path_to_db = os.environ.get(
    'RADICAL_PILOT_DBURL', "mongodb://ensembletk.imp.fu-berlin.de:27017/rp")
os.environ['RADICAL_PILOT_DBURL'] = path_to_db

import radical.pilot as rp
import radical.utils as ru

# import components

from engine import ACEMDEngine
from brain import Brain
from cluster import MDCluster
from resource import AllegroCluster, LocalCluster


if __name__ == '__main__':

    # we use a reporter class for nicer output
    report = ru.LogReporter(name='radical.pilot', level=verbose)
    report.title('Getting Started (RP version %s)' % rp.version)

    # use the resource specified as argument, fall back to localhost
    if len(sys.argv) > 2:
        report.exit('Usage:\t%s [resource]\n\n' % sys.argv[0])
    elif len(sys.argv) == 2:
        resource = sys.argv[1]
    else:
        resource = 'local.localhost'

    # --------------------------------------------------------------------------
    # SETUP SIMULATION
    # --------------------------------------------------------------------------

    if True:
        cluster = LocalCluster(15, 2)
    else:
        cluster = AllegroCluster(15, 'big', 4)

    cluster = MDCluster(
        system='ntl9',
        engine=ACEMDEngine('ntl9.conf', 'initial.pdb'),
        resource=cluster,
        report=report)

    brain = Brain(cluster)

    with cluster:
        report.ok('>>ok\n')

        report.header('submit units')

        # Register the ComputePilot in a UnitManager object.
        running = True

        # we now enter the main adaptive loop

        # Parameters

        min_stack_size = 20
        simulation_chunk_size = 10

        # 1. refill simulation stack from current model / brain
        # 2. check if enough new data has been acquired
        # 3. submit an analysis job
        while running:
            # 1. refill simulation stack from current model / brain
            if len(brain.simulation_cus) < min_stack_size:
                # add new simulations
                cu_descs = brain.get_simulation_cu(simulation_chunk_size)
                simulation_cus += umgr.submit_units(cu_descs)

            if brain.new_trajectories > 300:  # run_analysis_threshold
                # submit analysis job
                brain.analyze()
                umgr.cancel_units({'not-started-units'})

        # report.info('create %d unit description(s)\n\t' % n)
        # report.progress()
        # report.ok('>>ok\n')

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.

        report.header('gather results')
        # umgr.wait_units()

        report.info('\n')
        # for unit in units:
        #     report.plain('  * %s: %s, exit: %3s, out: %s\n'
        #                  % (unit.uid, unit.state[:4],
        #                     unit.exit_code, unit.stdout.strip()[:35]))

    report.header()


# -------------------------------------------------------------------------------

