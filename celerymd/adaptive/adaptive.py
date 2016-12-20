#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__ = 'MIT'

import os
import sys

verbose = os.environ.get('RADICAL_PILOT_VERBOSE', 'REPORT')
os.environ['RADICAL_PILOT_VERBOSE'] = verbose

import radical.pilot as rp
import radical.utils as ru

# import components

from engine import Engine
from brain import Brain
from modeller import Modeller


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

    # we need one md simulation software for a single system
    engine = Engine('initial.pdb')

    # we need a Modeller that will generate the MSM from the existing data
    modeller = Modeller('option1', 'option2')

    # we need the brain that creates new simulation jobs from the current model
    brain = Brain(engine)

    # the adaptive cycle runs as many simulations in parallel as possible
    # using the brain. Once we have gather N new transitions we trigger a
    # rebuild of the model which might involve several CUs

    # the tricky part is to use a callback to monitor the state when new
    # simulations or modelling should be triggered.

    # at best we have a stack of simulation CUs available so that the cluster
    # is always busy. When we want to analyze we just clear the stack and only
    # put in only analysis jobs. Once these are staged to the cluster we
    # refill the stack of simulation CU

    simulation_cus = []

    # it might be possible to use a second pilot and run the analysis only on
    # another cluster like rhea. In that case we need to stop running on the
    # cluster and only restart when the new model is available. But that
    # change should be easy

    # Create a new session. No need to try/except this: if session creation
    # fails, there is not much we can do anyways...

    # TODO: Enhancement for PR Make session use a with-block
    session = rp.Session()

    # all other pilot code is now tried/excepted.  If an exception is caught, we
    # can rely on the session object to exist and be valid, and we can thus tear
    # the whole RP stack down via a 'session.close()' call in the 'finally'
    # clause...


    try:

        # read the config used for resource details
        report.info('read config')
        config = ru.read_json(
            '%s/config.json' % os.path.dirname(os.path.abspath(__file__)))
        report.ok('>>ok\n')

        report.header('submit pilots')

        # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
        pmgr = rp.PilotManager(session=session)

        # Define an [n]-core local pilot that runs for [x] minutes
        # Here we use a dict to initialize the description object
        pd = {
            'resource': resource,
            'runtime': 15,  # pilot runtime (min)
            'exit_on_error': True,
            'project': config[resource]['project'],
            'queue': config[resource]['queue'],
            'access_schema': config[resource]['schema'],
            'cores': config[resource]['cores'],
        }
        pdesc = rp.ComputePilotDescription(pd)

        # Launch the pilot.
        pilot = pmgr.submit_pilots(pdesc)

        # Create a workload of char-counting a simple file.  We first create the
        # file right here, and stage it to the pilot 'shared_data' space
        os.system('hostname >  input.dat')
        os.system('date     >> input.dat')

        # Synchronously stage the data to the pilot
        report.info('stage shared data')

        # {'source': 'file://%s/input.dat' % os.getcwd(),
        #  'target': 'staging:///input.dat',
        #  'action': rp.TRANSFER}
        pilot.stage_in(engine.get_staging())

        # TODO: can you add multiple stage_ins?

        report.ok('>>ok\n')

        report.header('submit units')

        # Register the ComputePilot in a UnitManager object.
        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        umgr.register_callback(brain.callback)
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

        n = 128  # number of units to run
        report.info('create %d unit description(s)\n\t' % n)

        cuds = list()
        for i in range(0, n):
            # create a new CU description, and fill it.
            # Here we don't use dict initialization.
            cud = rp.ComputeUnitDescription()
            cud.executable = '/usr/bin/wc'
            cud.arguments = ['-c', 'input.dat']
            cud.input_staging = {'source': 'staging:///input.dat',
                                 'target': 'input.dat',
                                 'action': rp.LINK
                                 }

            cuds.append(cud)
            report.progress()

        report.ok('>>ok\n')

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.

        report.header('gather results')
        umgr.wait_units()

        report.info('\n')
        for unit in units:
            report.plain('  * %s: %s, exit: %3s, out: %s\n' \
                         % (unit.uid, unit.state[:4],
                            unit.exit_code, unit.stdout.strip()[:35]))

        # delete the sample input files
        os.system('rm input.dat')

    except Exception as e:
        # Something unexpected happened in the pilot code above
        report.error('caught Exception: %s\n' % e)
        raise

    except (KeyboardInterrupt, SystemExit) as e:
        # the callback called sys.exit(), and we can here catch the
        # corresponding KeyboardInterrupt exception for shutdown.  We also catch
        # SystemExit (which gets raised if the main threads exits for some other
        # reason).
        report.warn('exit requested\n')

    finally:
        # always clean up the session, no matter if we caught an exception or
        # not.  This will kill all remaining pilots.
        report.header('finalize')
        session.close()

    report.header()


# -------------------------------------------------------------------------------

