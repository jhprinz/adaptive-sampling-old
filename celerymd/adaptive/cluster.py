import radical.pilot as rp

from util import get_type


class Trajectory(object):
    """
    Represents a trajectory file on the cluster
    """
    def __init__(self, resource, location, length, extension=None, unit=None):
        self.resource = resource
        self.location = location
        if format is None:
            self.extension = location.split('.')[-1]
        else:
            self.extension = extension

        self.format = self.format.lower()
        self.length = length
        self.unit = unit

    def path_on_resource(self):
        lt = get_type(self.location)
        if lt in ['unit', 'shared']:
            return self.location.replace('shared://', self.resource.path_to_shared)

    def __len__(self):
        return self.length


class MDCluster(object):
    """
    Class to handle the status of a list of MD simulations in RP

    We agree that

    1. the initial configuration is stored as `{system}-{uid}.pdb`
    2. the resulting trajectory is stored as `{system}-{uid}.xtc
    3. the used conf file is stored as `{system}-{uid}.conf

    A cluster has various places to put a file, we have

    1. the location at the application level
    2. the location at the shared file system
    3. the location at the node in the working directory


    """
    def __init__(self, system, engine=None, resource=None, report=None):
        self.report = report
        self.system = system

        self.pmgr = None
        self.umgr = None
        self.pilot = None

        self.engine = engine

        # cu that create trajectory
        self.cus = dict()  # {uid : ComputeUnit}

        self.cus_pending = set()
        self.cus_running = set()
        self.cus_finished = set()
        self.cus_failed = set()

        self.resource = resource

        self.trajectories = dict()

        if resource is not None:
            self.add_resource(resource)

    def __enter__(self):
        # create the managers
        self.session = rp.Session()

        self.pmgr = rp.PilotManager(session=self.session)
        self.umgr = rp.UnitManager(session=self.session)

    def __exit__(self, exc_type, exc_val, exc_tb):
        fail = True
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            self.report.warn('exit requested\n')
        elif issubclass(exc_type, Exception):
            self.report.error('caught exception: %s\n' % exc_type)
            fail = False

        self.report.header('finalize')
        self.session.close()

        return fail

    def add_resource(self, resource):
        self.report.header('submit pilots')
        self.pilot = self.umgr.add_pilots(resource.desc)
        self.umgr.register_callback(self.unit_callback)

        self.report.info('stage shared data from engine')
        self.pilot.stage_in(self.engine.get_initial_staging())

    def to_filename(self, uid, ext):
        return '{system}-{uid}.{ext}'.format(
            system=self.system, uid=uid, ext=ext)

    def get_all_trajectories(self):
        pass

    @property
    def pending(self):
        return self.cus_pending

    @property
    def running(self):
        return self.cus_running

    @property
    def finished(self):
        return self.cus_finished

    def unit_callback(self, unit, state):
        """
        The callback for simulation units

        This will update the list of finished jobs and existing trajectories

        Parameters
        ----------
        unit
        state

        Returns
        -------

        """

        print "[Callback]: unit %s on %s: %s." % (
            unit.uid, unit.pilot_id, state)

        self.cus.add(unit)

        if not unit:
            return

        if state in [rp.FAILED, rp.CANCELED]:
            print "* unit %s (%s) state %s (%s) %s - %s, out/err: %s / %s" \
                  % (unit.uid,
                     unit.execution_locations,
                     unit.state,
                     unit.exit_code,
                     unit.start_time,
                     unit.stop_time,
                     unit.stdout,
                     unit.stderr)
        elif state in [rp.DONE]:
            # seems we have a new trajectory. Let's bookmark it

            location = 0
            length = 0
            t = Trajectory(
                self.resource, location=location, length=length, unit=unit)

            self.trajectories[location] = t