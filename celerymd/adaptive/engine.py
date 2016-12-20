# Create compute units for various simulation tools

import radical.pilot as rp
import os


class Engine(object):
    def get_staging(self):
        """
        Create the necessary staging commands to get all files to the node

        Returns
        -------

        """
        return []

    @property
    def arguments(self):
        return []

    @property
    def executable(self):
        return ''

    def transfer_from_stage(self, source):
        target = os.path.basename(source)
        return {
            'source': 'staging:///%s' % target,
            'target': target,
            'action': rp.TRANSFER
         }

    def transfer_to(self, source):
        target = os.path.basename(source)
        return {
            'source': 'file://%s' % source,
            'target': target,
            'action': rp.TRANSFER
         }

    def link_from_stage(self, source):
        target = os.path.basename(source)
        return {
            'source': 'staging:///%s' % target,
            'target': target,
            'action': rp.LINK
         }

    def transfer_to_stage(self, source):
        target = os.path.basename(source)
        return {
            'source': 'file://%s' % source,
            'target': 'staging:///%s' % target,
            'action': rp.TRANSFER}

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
    def __init__(self, conf_file, pdb_file):
        super(ACEMDEngine, self).__init__()
        self.conf_file = conf_file
        self.pdb_file = pdb_file

    def get_staging(self):
        return [
            self.transfer_to_stage(self.conf_file),
        ]

    @property
    def executable(self):
        # use bash for multiple commands
        return 'bin/bash'
        # return '/usr/bin/acemd'

    @property
    def arguments(self):
        return ['-l', '-c']

    def get_cud_pdb(self, pdb_file):
        """
        Create a compute unit description to be run

        Parameters
        ----------

        Returns
        -------

        """
        cud = rp.ComputeUnitDescription()
        cud.executable = self.executable
        cud.arguments = self.arguments + [os.path.basename(self.conf_file)]
        cud.input_staging = [
            self.link_from_stage(self.conf_file),
            self.transfer_to(pdb_file)
        ]

        return cud

    def get_cud_trajectory_frame(self, trajectory_file, frame):
        """
        Create a compute unit description to be run

        Parameters
        ----------

        Returns
        -------

        """

        # todo: add the extraction of a single frame using a little python tool
        # question: how to run multiple commands with MPU

        # might use mdconvert from mdtraj for now
        args = [
            'mdconvert'
            '-o', 'initial.pdb',
            '-i', '%d' % frame,
            trajectory_file,
            self.pdb_file,
        ]

        # and
        args += ['&&']

        # acemd run
        args += [
            'acemd',
            self.conf_file
        ]

        cud = rp.ComputeUnitDescription()
        cud.executable = self.executable
        cud.arguments = args + self.arguments + [os.path.basename(self.conf_file)]
        cud.input_staging = [
            self.link_from_stage(self.conf_file),
            self.link_from_stage(self.pdb_file),
            self.transfer_to(trajectory_file)
        ]

        return cud
