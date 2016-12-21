# Decide what to do with the current model

import random


class Brain(object):
    def __init__(self, cluster):
        self.cluster = cluster

    def analyze(self):
        """
        Update the model and trigger necessary tasks

        """
        _ = self.cluster

    def get_initial_configurations(self, num):
        """
        Create n pdb with initial configurations

        Parameters
        ----------
        num : int
            number of initial configurations to be drawn

        Returns
        -------
        list of str
            the list of filenames
        """

        # pick at random

        trajectories = self.cluster.trajectories

        frames = []

        for n in range(num):
            traj = random.choice(trajectories)
            frame = random.randint(len(traj))

            frames.append(traj[frame])

        return frames

    def get_simulation_cu(self, num):
        if self.cluster.trajectories:
            # seems we have at least on trajectory available

            frames = self.get_initial_configurations(num)
            cuds = []
            for frame in frames:
                target = self.cluster.get_new_trajectory_name()
                cuds.append(
                    self.cluster.engine.get_cmd_trajectory_frame(
                        frame.location, frame, target)
                )
                self.cluster.trajectories_stages[target] = frame

            return cuds
        else:
            cuds = []
            for run in range(num):
                target = self.cluster.engine.get_new_trajectory_name()
                cuds.append(
                    self.cluster.engine.get_cmd_run_initial(target)
                )

            return cuds
