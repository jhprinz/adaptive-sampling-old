## Celery MD

A usecase to run MD simulations on a (suitable) cluster using the celery framework

### Summary

[CeleryProject](http://www.celeryproject.org) is 

> ... an asynchronous task queue/job queue based on distributed message passing.	It is focused on real-time operation, but supports scheduling as well.
> 
> The execution units, called tasks, are executed concurrently on a single or more worker servers using multiprocessing, Eventlet,	or gevent. Tasks can execute asynchronously (in the background) or synchronously (wait until ready).

It is based on python and thus suitable for distrbution of python work to worker tasks and retrieve the results.

The framework uses a so-called message broker to collect tasks and results and redistribute or return these. It handles error messages and logging which are passed back to the master process and can handle failed tasks. 

> The recommended message broker is RabbitMQ, but support for Redis, Beanstalk, MongoDB, CouchDB, and databases (using SQLAlchemy or the Django ORM) is also available.

For now I have decided to use a Redis server that can be installed easily using conda.

### How does this work in practice

Similarly to EnsembleTK you need the broker (or simple database) run outside on some computer the whole time. This should have a good network connection to the workers but it depends on the load of data you want to send. I still have something like `SiegeTank` in mind where you can basically add any computer you have available to contribute to computations. This is not the focus right now but can be added later easily since the concept is exactly the same.

Once the broker is running it will take care of distributing work. It does not need to know the workers or the master process that wants to run tasks. It is merely the connection. Every other part needs to connect to the broker. 

Workers will consume tasks, run them and return the result or (like potentially in our case) return information necessary to retrieve the result later from a cluster

Any master can now dispatch tasks to the broker and retrieve results once they are done. This can be done completely asynchroneous which means you can dispatch 1000 tasks. Then attach some workers and once some results are finished in whatever order, they can be retrieved. In the meantime they will be cached by the database. If we want to return the full trajectory this is also possible, but requires a later database like MongoDB etc to run this efficiently. But this can be done. 

In general I think this scheme has some similarity to Folding@Home but running locally on a cluster.

### Example code

Assume we want to run this even in an interactive session in an `ipython notebook` then this would work
and we defined a python function in `tasks.py` like this

```py
### import Celery framework
from celery import Celery
server_str = 'redis://localhost:6379/0'
app = Celery('tasks', backend=server_str, broker=server_str)

### logging
import logging
logger = logging.get_logger(__name__)

# something simple

import os.path

@app.task
def directory(mypath):
    return os.path.listdir(mypath)


### define some simplified trajectory run
import simtk.openmm
import simtk.openmm.app
import mdtraj as md

@app.task
def generate(dcd_filename, steps, system_xml, integrator_xml, initial_pdb, platform, properties):
    # fix to send pdb file as string and not file
    pdb=md.load(Turn_Str_to_stream(initial_pdb))
    
    simulation = simtk.openmm.app.Simulation(
        topology=pdb.topology.to_openmm(),
        system=simtk.openmm.XmlSerializer.deserialize(system_xml),
        integrator=simtk.openmm.XmlSerializer.deserialize(integrator_xml),
        platform=simtk.openmm.Platform.getPlatformByName(platform),
        platformProperties=properties
    )    
    simulation.reporters.append(app.DCDReporter(dcd_filename, 1000))
    simulation.step(steps)    
    
    return {'Results': 'something'}
```

In practice you just write a function that should be executable. Of couse the necessary packages need to be installed on the node where the worker is run.

Then you open the same file on your master machine

```py
# import the function that runs on a worker
from tasks directory, generate

# this is kind of pointless since you don't know while machine you will run on
result = directory.delay('.')

# this will wait for the result and return it
# errors are handled as well
print result.get()

# now run openmm
system_xml = ...
integrator_xml = ...
pdb = ...

result = generate.delay(
    'scratch/testfile1.dcd', 
    1000, 
    system_xml,
    integrator_xml,
    pdb,
    platform='CUDA',
    properties={'CudaPrecision': 'mixed'})

result.ready
>>> False

# dispatch a whole set of trajectories
tasks = [ generate.delay(...) for i in range(1000)]

# you can store the task ids if you want and retrieve the status later, 
# but for now we keep them in memory

from celery import group
all_jobs = group(tasks)

# wait for all results
rs = all_jobs.get()

```

### This still looks too complicated

Agreed. To pickle the trajectories to transfer these is cumbersome but doable. However this can be simplified. Internally `celery` uses JSON pickling which can be overridden by your own pickling. E.g. Martin implemented pickling for pyemma objects so you could simply transfer pyemma objects to your worker and let them run a featurization.

### Usecases

I can basically see two usecases:

1. distribute python scripts that generate trajectories. Here OpenMM is destined to be used by of course also bash scripts can be executed (using python) and hence other simulation tools like gromacs. This will potentially not work on a super HPC like Titan but it might be the most flexible solution to be used on more open clusters like _Allegro_ or _hal_. The advantages are obvious. It is really extremely easy to run trajectories in parallel. 

    We still need to make it easier to store trajectories on the cluster and retrieve them somehow, but these are cluster specific problems. If we pickle the resulting trajectory (or the parts we need, say no water + precalculated features), we might not have to worry about that and keep the trajectories only for later in case we want to redo some work.
    
2. distribute pyemma work to the cluster. This might be easy to distribute computation of features to multiple nodes and get results much faster. This could even be complementary to the trajectory generation with EnsembleTK.

### Install celery

Add the (inofficial) conda tools repo that contains lots of useful conda packages that are not (yet) part of conda itself.

```
conda config add channels conda-forge
```

and then install as usual

```
conda install celery
```

### Setup the Redis Server

This is easily done using conda and is part of the official conda packages

```
conda install redis
```

### Run the redis server

just starting, no configuration necessary. The purpose of this server is not to restrict access, but to delegate messages and remove them afterwards. The security is done by usind SSH connections. To start the server run or start it in the backgroud

```
redis-server
```

### Run a single worker

We assume that our project is called `tasks` and in file `tasks.py`

```
celery worker -A tasks -l INFO
```

the option `-A {projname}` is required. `-l INFO` will set logging to INFO level and report all that is happening on the workers.

### How to solve the connection problem

Celery is originally meant for real-time processing of tasks and used a lot for webservers where you need to process thousands of incoming requests and distribute the work to nodes to stay responsive to requests.
This is usually the case where you have the server and the nodes in one network so connection to a broker on the same network is easy. This real-time feature is not, what we need. And in general we cannot assume that the nodes are on the same network as the broker or the master is not. 

To solve this we wrapped the connection to port 6379 of the broker on its machine with an SSH tunnel. This costs connection performance but on a local network should still be comparable to disk write speeds.

The ssh connection is currently setup once a worker is started and uses the `sshtunnel` package which is also part of `conda-forge` to set this up. This approach provides ultimate connection flexibility. One example is to run the broker on a desktop machine. 

The cases I have tests was to run a worker on the head of allegro and on my laptop while the broker and ipython were both running on my desktop machine.

The ssh tunnel is part of the worker execution and a user would have to use the basic setup file of celery to 

### Useful simplifications

OPS has already all pickling for all openmm objects, trajectories, etc implemented so this gives an even simpler way to run trajectories in case you want to directly return the trajectory. 

If there are concerns about speed, the pickling of a 1000 frame 1651 atom system of Alanine including the complete openmm setup took less than a second and produced a 200MB stream. This can be send in a few seconds over local SSH and unpickle under a second. This is still not optimized for the handling of numpy arrays and can be improved. Compared to the full running time this is short and comparable to doing an `scp` from the remove machine.

Still, this approach is potentially not useful for large production runs so consider it a prove of concept.

The function in `tasks.py` looks like this if you want to use the fastest platform available

```py
@app.task
def generate(engine, template, steps):
    engine.initialize()
    engine.current_snapshot = template
    traj = engine.generate_n_steps(steps)
    return traj
    
```

then call it like

```py
# create a PyEmmaFeaturizer
feat = pyemma.coordinates.featurizer('my_protein.pdb') 
feat.add_backbone_torsions() 

cv = PyEMMAFeaturizerCV('pyemma', feat, initial.topology)
traj_task = generate.delay(myengine, initial, 1000)
traj = traj_task.get()

featurizer(traj)
>>> ...
```

or run PyEmma on the node directly

```py
@app.task
def featurize(cv, trajectory):
    return cv(trajectory)
```

```py
feat_task = featurizer.delay(pyemma_cv, traj)
print feat_task.get() 

# or for many trajectories in parallel
tasks = group([featurizer.delay(pyemma_cv, t) for t in trajs])

# get all featurized trajectories
festures = tasks.get() 
```

Remember that this approach does all in memory. No reading of files, but of course this could be done, too.

### How to run this on a cluster

1. the broker: You first setup the broker just running. You might even keep this in the background. In our case the load on the broker should be moderate and only require some work when a simulation is finished.

2. Start your scheme that will create jobs and process them. Make sure it has access to the broker by using a potential SSH connection/tunnel.

3. Place as many workers in your cue for a time that you deem resonable. The more workers you have, the faster you tasks will be done. This is flexible. A single worker supports concurrent jobs and usually uses the number of available cores as default -- a simple flag `--concurrency=[#n]` can change the number of subprocesses used. It is always possible to ask celery to kill a worker if you think it is not needed anymore. 

##### Example

As an example I was able to run a worker with 4 child processes on my laptop which lead to an overall speedup of a factor of 2 considering all the overhead with pickling for the alanine system with no diskwriting, all in memory.

Interestingly you do not need to worry too much about the queueing system. Just place as many workers as you deem reasonable and it will run. You can add workers from anywhere as long as they can connect to your broker. 

### Other related topics

#### Monitor performance

There exists a real-time monitor web-server called `celery flower`. You can install it using

```
conda install flower
```

Then start the server using

```
flower -A proj --port=5555
```

this runs a webserver at port 5555 to allow you to monitor what is happening on your workers. See [Screenshots](http://flower.readthedocs.io/en/latest/screenshots.html) for an idea.

All it needs is to access the broker.

#### What else is good (and bad) about celery

1. It is very nice extentable, like adding the ssh support. 
2. It uses _heart-beats_ to monitor if workers are still responding.
3. Can handle fails (what we probably do not need. If a worker fails we just don't use the trajectory)
4. is used world wide in production so it is well maintained and stable
5. based on python 
6. You can control/kill workers remotely

### Alternatives

I only consider things that could replace Celery, EnsembleTK has a wider and more speific usecase and should be implemented anyway. 

##### PyParallel

This is more focussed on parallel execution on an HPC of python code. This could be useful for running pyEmma in parallel, but it is at alpha stage and not yet ready.

### Useful things

