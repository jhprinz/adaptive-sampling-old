# Decide what to do with the current model

import radical.pilot as rp


class Brain(object):
    def __init__(self, engine, modeller):
        self.engine = engine
        pass

    def get_simulation_cu(self, n):


        cu = rp.ComputeUnitDescription({

        })

        return [cu] * n
