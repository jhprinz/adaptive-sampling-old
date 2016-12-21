# Create compute units for various simulation tools

import radical.pilot as rp

from bash import BashCommand

import os


class Engine(object):
    def __init__(self, cluster=None):
        self.cluster = cluster

    def get_initial_staging(self):
        """
        Create the necessary staging commands to get all files to the node

        Returns
        -------

        """
        return []

    def get_cud(self, pdb_file):
        """
        Create a compute unit description to be run

        Parameters
        ----------

        Returns
        -------

        """
        return rp.ComputeUnitDescription()


class ACEMDEngine(Engine):
    executable = 'acemd'
    trajectory_ext = '.xtc'

    def __init__(self, conf_file, pdb_file):
        super(ACEMDEngine, self).__init__()
        self.conf_file = conf_file
        self.pdb_file = pdb_file

        # names in the staging area
        self.pdb_file_link = 'staging://' + os.path.basename(self.pdb_file)
        self.conf_file_link = 'staging://' + os.path.basename(self.conf_file)

    def get_initial_staging(self):
        cmd = self.cluster.copy(self.pdb_file, self.pdb_file_link)

        return cmd.input_staging

    def get_cmd_run_initial(self, target):
        """
        Create a compute unit description to be run

        Parameters
        ----------
        target : str
            location of the created target trajectory

        Returns
        -------

        """
        cmd  = self.cluster.link(self.conf_file_link)
        cmd += self.cluster.link(self.pdb_file_link)

        cmd += BashCommand(
            'acemd',
            [
                self.conf_file
            ])

        cmd += self.cluster.move('output.xtc', target)

        return cmd

    def get_cmd_pdb(self, pdb_file):
        """
        Create a compute unit description to be run

        Parameters
        ----------

        Returns
        -------

        """
        cmd  = self.cluster.link(self.conf_file)
        cmd += self.cluster.copy(pdb_file)

        cmd += BashCommand(
            'acemd',
            [
                self.conf_file
            ])

        return cmd

    def get_cmd_trajectory_frame(self, source, frame, target):
        """
        Create a command that runs from a fram in a trajectory

        Parameters
        ----------
        source : str
            location of the input trajectory, usually starts with `shared://`
            and lists the location on the shared space
        frame : int
            the integer index starting from 0 in the input trajectory
        target : str
            location of the target trajectory, usually starts with `shared://`

        Returns
        -------
        Command
        """

        # todo: add the extraction of a single frame using a little python tool
        # question: how to run multiple commands with MPU

        cmd  = self.cluster.link(self.conf_file_link)
        cmd += self.cluster.link(self.pdb_file_link)
        cmd += self.cluster.link(source, 'input.xtc')

        # might use mdconvert from mdtraj for now
        cmd += BashCommand(
            'mdconvert',
            [
                '-o', 'initial.pdb',
                '-i', '%d' % frame,
                'input.xtc',
                self.pdb_file,
            ])

        cmd += BashCommand(
            'acemd',
            [
                self.conf_file
            ])
        cmd += self.cluster.move('output.xtc', target)

        return cmd
