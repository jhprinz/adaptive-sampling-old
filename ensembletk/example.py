import sys
import os
import json

from radical.ensemblemd import Kernel
from radical.ensemblemd import PoE
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import ResourceHandle

# ------------------------------------------------------------------------------
# Set default verbosity

if not os.environ.get('RADICAL_ENTK_VERBOSE'):
    os.environ['RADICAL_ENTK_VERBOSE'] = 'REPORT'


class MyApp(PoE):
    def __init__(self, stages, instances):
        PoE.__init__(self, stages, instances)

    def stage_1(self, instance):
        k = Kernel(name="misc.hello")
        k.arguments = ["--file=output.txt"]
        return k


if __name__ == "__main__":

    # use the resource specified as argument, fall back to localhost
    if len(sys.argv) > 2:
        print 'Usage:\t%s [resource]\n\n' % sys.argv[0]
        sys.exit(1)
    elif len(sys.argv) == 2:
        resource = sys.argv[1]
    else:
        resource = 'local.localhost'

    try:

        with open('%s/config.json' % os.path.dirname(
                os.path.abspath(__file__))) as data_file:
            config = json.load(data_file)

        # Create a new resource handle with one resource and a fixed
        # number of cores and runtime.
        cluster = ResourceHandle(
            resource=resource,
            cores=config[resource]["cores"],
            walltime=15,
            # username=None,

            project=config[resource]['project'],
            access_schema=config[resource]['schema'],
            queue=config[resource]['queue'],
            database_url='mongodb://rp:rp@ds015335.mlab.com:15335/rp',
        )

        # Allocate the resources.
        cluster.allocate()

        # Set the 'instances' of the BagofTasks to 1. This means that 1 instance
        # of each BagofTasks step is executed.
        app = MyApp(stages=1, instances=1)

        cluster.run(app)

    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise  # Just raise the execption again to get the backtrace

    try:
        # Deallocate the resources. 
        cluster.deallocate()

    except:
        pass
