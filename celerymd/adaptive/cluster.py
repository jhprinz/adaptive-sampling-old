import radical.pilot as rp


class MDCluster(object):
    """
    Class to handle the status of a list of MD simulations in RP

    We agree that

    1. the initial configuration is stored as `{system}-{uid}.pdb`
    2. the resulting trajectory is stored as `{system}-{uid}.xtc
    3. the used conf file is stored as `{system}-{uid}.conf

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

    def add_resource(self, pdesc):
        self.report.header('submit pilots')
        self.pilot = self.umgr.add_pilots(pdesc)
        self.umgr.register_callback(self.unit_callback)

        self.report.info('stage shared data from engine')
        self.pilot.stage_in(self.engine.get_staging())

    def to_filename(self, uid, ext):
        return '{system}-{uid}.{ext}'.format(
            system=self.system, uid=id, ext=ext)

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

    def unit_callback(self, unit, status):
        """
        The callback for simulation units

        This will update the list of finished jobs and existing trajectories

        Parameters
        ----------
        unit
        status

        Returns
        -------

        """
        pass

    def pilot_callback(self, pilot, state):
        """

        Parameters
        ----------
        pilot
        state

        Returns
        -------

        """
        pass


class Resource(object):
    pass


def AllegroCluster(runtime, queue, cores):
    # question: This splitting in resource does not make sense to me
    # I would say that these should be coupled with the resource definition

    pd = {
        'resource': 'fub.allegro',
        'runtime': runtime,
        'exit_on_error': True,
        'project': None,
        'queue': queue,
        'access_schema': 'ssh',
        'cores': cores,
    }
    return rp.ComputePilotDescription(pd)


def LocalCluster(runtime, cores):
    pd = {
        'resource': 'local.localhost',
        'runtime': runtime,
        'exit_on_error': True,
        'project': None,
        'queue': None,
        'access_schema': 'local',
        'cores': cores,
    }
    return rp.ComputePilotDescription(pd)
