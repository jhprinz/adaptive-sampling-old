# adaptive-sampling
A Python framework to run adaptive Markov state model (MSM) simulation on HPC resources

The generation of MSMs requires a huge amount of trajectory data to be analyzed. In most cases
this leads to an enhanced understanding of the dynamics of the system which can be used to
make decision about collection more data to achieve a desired accuracy or level of detail in
the generated MSM. This alternating process between simulation/actively generating new observations 
and analysis is currently difficult and involves lots of human decision along the path.

This framework aim to automate this process with the following goals:

1. Ease of use: Simple system setup once an HPC has been added.
2. Flexibility: Modular setup, attach to multiple HPCs and different simulation engines
3. Automatism: Create an user-defined adaptive strategy that is executed
4. Compatibility: Build in analysis tools and export to known formats
