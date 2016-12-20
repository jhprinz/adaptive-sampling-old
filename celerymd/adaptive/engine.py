# Create compute units for various simulation tools

import radical.pilot as rp


class Engine():
    def __init__(self, pdb):
        self.pdb = pdb
        pass

    def get_staging(self):
        """
        Create the necessary staging commands to get all files to the node

        Returns
        -------

        """
        return []

    def get_cu(self, initial):
        """
        Create a compute unit description to be run

        Parameters
        ----------

        Returns
        -------

        """
        return rp.ComputeUnitDescription(

        )