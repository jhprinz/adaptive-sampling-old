# Adaptive Sampling Framwork Layout

Adaptive Sampling MD (AMD) is the concept of collecting short MD simultions in an a guided way dependend on the history of collected sampled, i.e. simulated trajectories.

This immediately induces three basic components to make this happen:

#### 1. The Adaptive Sampling Strategy "the brain"

The theory and implementation on how to decide on the next simulation conditions for future runs.

#### 2. A system to run MD simulations "the engine"

This basically boils down to a wrapper that allows easy dispatching of simulation jobs in parallel on multiple computers or a cluster. 

This engine should work indpendently of the brain and be used as a standalone queue to run MD simulations. It will require a storage solution to some extent because the idea of issuing a bunch of simulation usually implies that you do not want to actively wait for the simulations to finish, but rather later access the results or got status updates.

#### 3. The bookkeeping "the storage"

The place where all generated information is kept for easy access to the brain. Everything that the engine generates is stored or referenced here. At best, also the brain will store all issued simulation and generated models that were used to make decisions about the progress. The storage should also run independently and allow to store data without using an engine or adaptive sampling. Similar to an extended trajectory format.


## The Components

In the following we will take a brief look at how an possible use of the components might look like.

### Queueing System for MD

Allow MD simulations to be scheduled

```py
orchestrator = ClusterQueueingSystem(
    storage=ClusterStorage(),
    config_file,
    [options])

simulation_task = SimulateNFramesMDTask(
    engine = my_gromacs_engine,
    start_frame = my_last_frame,
    n_frames = 100
)

# do this 100 times
orchestrator.append([simulation_task] * 100)

print orchestrator.currently_running_tasks
```

There are several ways to implement this and we should keep specific aspects in mind:

1. We do not know, if (a) python will run on the cluster and (b) the cluster can connect to the internet
2. You want to run on your local machine for testing and with little changes on a cluster
3. You might want to use workers that pull a job from a list or put jobs in a queue. 
4. We want to be able to use different simulation engines: Gromacs, AceMD, OpenMM, ...

To keep it simple for a user we should create a simple API to instantiate a `QueueingSystem` which only a few options. This QS can be adapted to all sorts of other clusters by subclassing. The main point is that the QS can 

1. accept new tasks to run
2. add the result of the tasks to a storage
3. report on the status of task execution
4. controle the execution, i.e., abort gracefully, remove tasks, etc...

all the rest is handled by the specific QS instance. The QS should be responsibe for the distribution and execution, and if desired also the setup of necessary workers or initial preparations, etc.

##### Example 1

Assume you want to use workers on a cluster, then you need to run the server that workers can connect to and place the worker in the cue.

##### Example 2

Placing jobs in a cue might not require any additional preparations beside monitoring the cue and see if you can place new jobs in the cue or when a job is finished doing some cleaning up and registering the result in the DB.

#### Storing

After a task is finished its results need to be registered in the DB. Either you store a pointer to the files 

```py
storage.trajectories.save(ExternalMDTrajectory('file0001.xtc'))
```

or save it as a full trajectory object in the DB copying all frames with it

```py
storage.trajectories.save(Trajectory(iterator_of_frames))
```

Still, the QS is responsible to do that with whatever the worker returned. If it returned the file location then you might reference it (i.e. Gromacs), if it returns a stream of a pickled trajectory store it (i.e. OpenMM).

#### Persistance

The QS should (not necessary) run independent of the main task and be able to be stopped or continued. The idea is that the actual jobs to be done and the execution are independent. The Sampler will add tasks to the queue and if you get time on a cluster you can reduce the list. As long as you have not run these you can still clear the queue or add more jobs. For the MSM Adaptive Scheme we usually do not have dependent tasks and it does never matter in which order we run the tasks or if we skip some. If we pick good candidated we will converge faster, but we will not converge to a wrong solution (within the bounds of the projection error or course).

#### Additional features

- add automatic retries, if a simulation should crash or is aborted.

The main routine that combines all aspects.

1. The queueing system
2. A place to store objects
3. The logic to build models
4. The application of the adaptive strategy

Once you have created all these parts you can create the sampler and run it. The QS and the ST should exist independently

### The use of celery

This is a first working implementation and not yet so well documented. Celery is a python based worker scheduler. You can create python based worker that provide certain commands which can then be executed from a master task completely independently on a cluster or distributed computers. Celery takes care of all the connections and also the persistance of returned data until they are collected. 

An example is to write a worker (see REPO) that can execute an MD simulation and returns a reference to the generated MD file or even the trajectory as a stream, s.t. no file is left of the worker machine (if so desired). 

The given example will run 20 trajectories on 4 core and collect the results in the order they are finished (not in the order they are started!)

Patrick Grinaway (choderalab) has already ran workers on the CBIO cluster at MSKCC and we can adapt this to our cluster. All that we have to do is to start and stop the workers and celery does the rest. 

Benefits are that we can write the workers in python. Downside is that we have to write the worker in python. So Python needs to run on the cluster. For message passing there exists a so called BROKER, a simple DB that is connected to over a simple network connection. For result persistance the same. This is extremely easy to setup.

more to come ... (see example)

### Connections to existing software

#### HTMD

HTMD should be of great help here to solve the problem of adding jobs to a queue.
In case we want to use the worker approach it can be use to dispatch workers to the queue. It has SLURM support built-in

#### pySLURM

A Python package that allows direct access to slurm. The latest version is tested for SLURM 16 while on our cluster it still runs v14


#### OPS

OPS will need a scheduler and in addition the possibility to convert the MoveTree into a TaskGenerator. We might use the existing `Storage` as an option for a single-file based storage solution

### Projects benefiting from this

#### Adaptive Sampling

#### YANK

#### Ensemblr

#### HTMD

#### OPS


## Code Examples

## The "brain"

In its simplest it could look like this

```py
storage = MongoDBStorage('alanine_adaptive')
queue = WorkerCeleryQS(storage=storage)
strategy = RespawnAtOneOverC()
sampler = AdaptiveSampling(storage, queue, strategy)
sampler.start()
```



### PyEmma (build MSMs)

Construct an MSM from given data in the DB

```py
storage = MongoDBStorage('alanine_adaptive')

storage.trajectories.save(last_trajectory)

print len(storage.trajectories)

# return a PyEMMA source iterator object to iterate all trajectories
source = storage.trajectories.source

```

### The "Storage" ResultDB

Store all data / results from the queueing system, model builder, etc.

The database is some kind of repository that does the bookkeeping. This does not necessarily involve storing all trajetory files, but all existing files should be mentioned in the database. The same should be true for all models, tasks, clusterings, etc. All objects that might be of later value and we want to access easily.

Since there are several ways to do that we should just provide an API and do several implementations for different purposes. 

I propose either to 

1. adopt the netCDF+ approach, which is basically a NoSQL DB in a single file and extend it to point to external files (a PR already exists, but needs to be updates),
2. to use a MongoDB instead which is the more general approach, but require a MongoDB server to be running.
3. use a special directory and store one file per object which a specific naming scheme

But all will share the same API which I would adopt from what we use with OPS. 

The first two are more elegant and provide the additional benefit of easier search and access as well as reusing existing objects. In this case it is also important to use strictly immutable objects, ob objects where only non-essential attributes are mutable.

If objects are immutable we can safely use pointers to existing objects without the danger that these might change in the future. This will simplify storage immensely.

The most important point is that the storage is persisting and will not disappear once a job is finished or the main simulation crashed. It should also be suited to restart a simulation either after crashing or if more simulation is needed. Lastly it can also serve as the starting point for further simulations and analysis.

A DB is best suited to remain consistant, whereas the file based approaches can suffer if the simulation crashes at the wrong moment.

For the purely filebased approach we need to write functions that parse the directory tree and return the appropriate objects.

```py
# return a pyemma source object
storage.trajectories.as_source  

# actually .trajectories is an iterator over all trajectories 

# [Do all the pyemma magic]

storage.models.save(model)  # should contain all references to how its created
```


## Updates to NetCDF+ for Adaptive Sampling

If we want to use netCDF+ these things can be useful

### Concepts

#### StorageState

This will remember the number of items per store at a certain point in time. If you want to store the result of a query you can simply remember the query function and the storage state to reconstruct the actual result. Very useful to keep track of new objects.

#### Special Iterators

A way to encode all trajectories of a specific type in the storage. Usually you would write

```py
stateA_trajs = [traj for traj in storage.trajectories if traj[0] in stateA]
```

we might want to simplify this into

```
all_traj_iterator = storage.trajectories
stateA_traj_iterator = storage.trajectories.filter(lambda traj: traj[0] in stateA) 
```

These queries should also be storable as well as the result as implicit

### Additional StorableObjects

#### ExternalTrajectory

Instead of saving a list of snapshots we could just save a whole trajectory as one object and reference it by filename. It would work exactly as a normal trajectory but the snapshots will be loaded specifically and iterating over a trajectory is also different. 

Not sure how to get a uuid for the snapshots then but I guess you can do that by skipping $n$ indices when saving the trajectory. Then, if the traj has id `17` and is of length 5. The frames have UUID `18 - 22`. These snapshots can be accessed from a special externalsnapshot store that can handle the requests.

#### ExternalSnapshot

These are referencing a frame number and an `MDFile`

#### ExternalFile

Referencing an external filenme with a UUID. A filename should also be unique, but this way it is unified. You can also reference other URI like websites, etc...

#### MDFile

An external file readable by MDTraj

There are some caveats to make sure this is efficient but the main point is bookkeeping and that should be possible.

#### Matrix

In general a matrix with a special purpose and references on how they were created, e.g. `CorrelationMatrix`, `TransitionMatrix`, ...

#### All PyEmma objects

I think for most of them we can use M. SCherers JSON pickling, so this is practically done.


## Strategy (The Brain)

This is still the most experimental and not clear part. We might have to try different ideas to get something that feels right.

    class Strategy(StorableMixin):
        pass    

It would be great if a user could define a strategy using simple building blocks. I presume this will be too rigid and too complicated. If we provide a ways that makes it wasy to write a little python program, that does what we want, it might be better. I could also imagine that you need to subclass a `Strategy` class and implement certain functions.

There are several ways to express a strategy by a user

1. provide high-level function with lots of options

    ```py
    strat = OneOverCAdaptiveStrategy(trajs='all', prior=1)
    ```

2. use building blocks to define a acyclic directed graph (ADC)

    ```py
    strat = {
        'traj_set': (storage.trajectories.load, slice(None, None)),
        'correlation_matrix': (pyemma.get_correlation, 'traj_set', 'featurizer'),
        'tica_proj': (pyemma.magic_tica_fnc, 'correlation_matrix', ),
        'clustering': (pyemma.magic_clustering_fnc, 'tica_proj', 'traj_set'),
        'count_matrix': (pyemma.count_fnc, 'clustering', 'traj_set'),
        'msm': (pyemma.ml_rev_msm, 'count_matrix'),
    }
    ```

3. use building blocks to create a quasi-Domain Specific Language (DSL) that expresses 2. but is better readable

    ```py
    Sequence([
        Add(
            MSM(
                trajs=Storage.trajectories)),
        Add(
            Clustering())
    ])
    ```
    
4. write python code that is translated into 2. (if possible) and gets executed using the scheduler (not sure how that would work yet)

    ```py
    
    ```
    
5. write python code that uses the schedular and has helper functions to access the existing results. This is probably the best and most flexible approach.

    ```py
    
    ```

### More ideas

We could keep the generation of the model completely separate from the decision on what to do next. So the model is basically a _deterministic_ function of the existing data. It is expensive to compute but more or less a pure function. Depending on your objective and this MSM you can make predictions on where to start new trajectories. (See Nuria)
