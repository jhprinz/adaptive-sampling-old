# Application workflow description

## Setup

* Queue - There exists a queue that contains starting parameters for the simulation. These parameters can be user-fed or pushed by another task.
* Simulation tasks - "N" simulations tasks execute concurrently on the target machine.
* Brain/analysis - The brain executes on trigger and operates on the output of the simulation tasks and generates starting parameters for the next set of simulations. These parameters are pushed to the Queue.
* Datastore - The datastore holds the intermediate data that is yet to be analyzed by the brain.

## Figure

![adaptive_sampling_fig](./figs/adaptive_sampling_scheme.png)

## Execution

* Initial set of simulations require starting parameters, these can be user-fed directly to the simulation or pushed to the queue so that they can be extacted by the simulations.

* The output of these simulations is stored in a datastore. This datastore can be the filesystem, database, etc. (This is still in discussion)

* The brain is executed based on a trigger (can be clock-based, data-based, etc.). The brain operates over the data in the datastore and generates a new set of starting parameters and pushes them to the queue.

* Upon completion of a simulation, the next simulation task is created and uses the starting parameter existing in the queue. 

* Important to note: The queue always contains starting parameters for simulations. These values can be output of the brain process (updated parameters) or the parameters from the previous iterations. This ensures that the simulation do not wait for starting parameters and are always running (with either updated or old parameters).

