# Toy workload for Adaptive Sampling usecase


## Requirement on client machine

* python >= 2.7 (< 3.0)
* python-pip
* python-virtualenv
* git

## Installation

* The instructions in this document are relative to $HOME, feel free to pick your own data locations.

* You will first need to create a virtual environment. This is to avoid conflict between packages required for this example and local system packages. 

```bash
virtualenv $HOME/myenv
source $HOME/myenv/bin/activate
```

* You now need to install specific branches of [radical.pilot](https://github.com/radical-cybertools/radical.pilot) and [radical.ensemblemd](https://github.com/radical-cybertools/radical.ensemblemd). Some of the features required for this project are in the development branch and would be released soon.


Radical pilot installation:

```bash
cd $HOME
git clone https://github.com/radical-cybertools/radical.pilot.git
cd radical.pilot
git checkout usecase/vivek
pip install .
```

Ensemble toolkit installation:

```bash
cd $HOME
git clone https://github.com/radical-cybertools/radical.ensemblemd.git
cd radical.ensemblemd
git checkout usecase/adap_sampling
pip install .
```

## Description of toy example

With reference to the [workflow diagram](https://github.com/markovmodel/adaptive-sampling/blob/master/resources/figs/adaptive_sampling_scheme.pdf), the understanding is to have multiple independent simulation pipelines and an analysis task that at certain intervals (or some other trigger) operates on the data produced by the simulations to generate a new set of starting parameters. These starting parameters are updated in a queue and picked up by the simulations in their next iterations.

The queue either contains new starting parameters or if they are not ready, contains the old starting parameters. Therefore, the simulations do not wait for the analysis task to complete.

(Please correct me if my understanding is incorrect/incomplete).

In this toy example, we try to mimic the workflow with toy/trivial workload. We have an ensemble of pipelines each of which sleep for a certain duration and then write text to a file. These pipelines are meant to mimic the simulation tasks as the duration to sleep is picked up by the values in a queue(right now a list).

We add an additional pipeline (ensemble size + 1) which mimics the analysis task (=brain). This task regularly looks for specific data from the simulation tasks, if they exist they are pulled (staged-in) and can be operated over. The output of the analysis task is an integer value (random integer < 20) which is pushed to the queue and becomes the new starting parameter for any of the simulation pipelines.


## Executing the toy example

```bash
cd $HOME
cd radical.ensemblemd/examples/usecase_adap_sampling
RADICAL_ENTK_VERBOSE=info python runme.py
```

I have added comments to the source code for explanations. Please create an issue/ping me if clarification is required.


## Moving towards real example

* This would require compiling/building any of the simulation, analysis tools on the remote machine of interest.

* Some testing and configuration might be required for any new machine or local clusters/grids.

* We replace the "kernel plugins" for the toy kernels in this example with those for real kernels (e.g. gromacs, pyemma, etc.). This would mainly involve deciding the parameters to assign and specifying the executing environment (environment variables, modules to be loaded, etc).

* Once we can validate results for a small example, we can then work with larger scales.