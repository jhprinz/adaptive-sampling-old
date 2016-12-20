# Decide what to do with the current model

import radical.pilot as rp


class Brain(object):
    def __init__(self, engine, modeller):
        self.engine = engine
        self.modeller = modeller
        self.simulation_pm = None
        self.analysis_pm = None
        self.initial_confs = {}

    def analyze(self):
        """
        Update the model and trigger necessary tasks

        """
        pass

    def get_initial_configurations(self, n):
        """
        Create n pdf with initial configurations

        Parameters
        ----------
        n : int
            number of initial configurations to be drawn

        Returns
        -------
        list of str
            the list of filenames
        """
        return [] * n

    def get_simulation_cu(self, n):
        files = self.get_initial_configurations(n)
        cuds = []
        for pdb_file in files:
            cuds.append(
                self.engine.get_cud(pdb_file)
            )

        return cuds


class MDStatus(object):
    """
    Class to handle the status of a list of MD simulations in RP

    We agree that

    1. the initial configuration is stored as `{system}-{uid}.pdb`
    2. the resulting trajectory is stored as `{system}-{uid}.xtc
    3. the used conf file is stored as `{system}-{uid}.conf

    """

    def __init__(self, pilot_mngr, unit_mngr):
        self.system = 'ntl9'
        self.pilot_mngr = pilot_mngr
        self.unit_mngr = unit_mngr

        self.cus = dict()   # uid : ComputeUnit

        self.cus_pending = set()
        self.cus_running = set()
        self.cus_finished = set()
        self.cus_failed = set()

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