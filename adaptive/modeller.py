# scan existing simulations and create a MSM model using python

# this will have to write python code that can be executed since we cannot
# just run python but only execute

import radical.pilot as rp


class Modeller(object):
    def __init__(self, param1, param2):
        pass

    def to_python(self):
        return 'pass'

    def to_cu(self):
        # Write the python file, stage it, run it and return the model
        cu = rp.ComputeUnitDescription({


        })

        return cu
