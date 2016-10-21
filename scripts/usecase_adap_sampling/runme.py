__author__    = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__   = "MIT"



'''
The class Test describes the application workflow. This class is of the Ensemble
of Pipelines type and thus can have concurrent independent pipelines. The parameter
ENSEMBLE_SIZE specifies the number of "simulation" tasks. In total, we have
ENSEMBLE_SIZE+1 pipelines to accomodate the analysis task which also is independent.

Once executed, ENSEMBLE_SIZE+1 instances of stage_1 are created and executed, the 
first ENSEMBLE_SIZE instances are the simulation tasks and the last is the analysis task;
thus an if-else condition. The analysis task is periodically executed (notice the sleep),
and looks for output data from our "simulation" tasks, namely output.txt. It also produces 
a value to update the parameter queue (INPUT_PAR_Q). This value is used by the "simulation"
task in its next iteration.

This example executes on localhost but can be extended to run on remote machine by specifying
the details in the resource handle.
'''

from radical.entk import EoP, AppManager, Kernel, ResourceHandle

from echo import echo_kernel
from randval import rand_kernel
from sleep import sleep_kernel
from time import sleep


ENSEMBLE_SIZE=2		# No. of simulation tasks
INPUT_PAR_Q = [20 for x in range(1, ENSEMBLE_SIZE+1)]	# Starting parameter queue
ITER = [1 for x in range(1, ENSEMBLE_SIZE+2)]		# Bookkeeping the current iteratio
													# of each pipeline as they can proceed
													# in different speeds


# Function to push to the list at the end
def push_val(val):

	global INPUT_PAR_Q

	for i in range(0, len(INPUT_PAR_Q)-1):
		INPUT_PAR_Q[i] = INPUT_PAR_Q[i+1]

	INPUT_PAR_Q[len(INPUT_PAR_Q)-1] = val


# Application workflow described by this class (of type EoP)
class Test(EoP):

	def __init__(self, ensemble_size, pipeline_size):
		super(Test,self).__init__(ensemble_size, pipeline_size)

	def stage_1(self, instance):

		global INPUT_PAR
		global ENSEMBLE_SIZE

		# "simulation" tasks
		if instance <= ENSEMBLE_SIZE:

			k1 = Kernel(name="sleep")
			k1.arguments = ["--file=output.txt","--text=simulation","--duration={0}".format(INPUT_PAR_Q[instance-1])]
			k1.cores = 1

			# File staging can be added using the following
			#k1.upload_input_data = []
			#k1.copy_input_data = []
			#k1.link_input_data = []
			#k1.copy_output_data = []
			#k1.download_output_data = []

			return k1

		# "analysis" task
		else:

			# Emulating some more analysis executin time
			sleep(10)


			# Analysis kernel produces a random integer (<20) to push into INPUT_PAR_Q
			m1 = Kernel(name="randval")
			m1.arguments = ["--upperlimit=20"]

			m1.copy_input_data = []

			# Copy simulation output data
			for inst in range(1, ENSEMBLE_SIZE+1):
				m1.copy_input_data += ['$ITER_{0}_STAGE_1_TASK_{1}/output.txt'.format(ITER[instance-1],inst)]

			return m1


	def branch_1(self, instance):

		# Run each pipeline for a max of 5 iterations
		if ITER[instance-1] != 5:
			self.set_next_stage(stage=1)
			ITER[instance-1] += 1
		else:
			# End each pipeline
			pass

		# Extraction of analysis kernel output
		if instance==ENSEMBLE_SIZE+1:

			# Get output of analysis kernel
			new_par = self.get_output(stage=1, task=ENSEMBLE_SIZE+1)
			print 'Output of analysis in stage 1 = {0}'.format(new_par)

			# Push new value into INPUT_PAR_Q
			if new_par != None:
				push_val(int(new_par))



if __name__ == '__main__':

	# Create pattern object with desired ensemble size, pipeline size
	pipe = Test(ensemble_size=ENSEMBLE_SIZE+1, pipeline_size=1)

	# Create an application manager
	app = AppManager(name='Adap_sampling')

	# Register kernels to be used
	app.register_kernels(rand_kernel)
	app.register_kernels(sleep_kernel)

	# Add workload to the application manager
	app.add_workload(pipe)
	

	# Create a resource handle for target machine
	res = ResourceHandle(resource="local.localhost",
				cores=4,
				#username=,
				#project =,
				#queue=,
				walltime=10,
				database_url='mongodb://rp:rp@ds015335.mlab.com:15335/rp')

	# Submit request for resources + wait till job becomes Active
	res.allocate(wait=True)

	# Run the given workload
	res.run(app)

	# Deallocate the resource
	res.deallocate()
	