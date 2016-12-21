import radical.pilot as rp
import os

from bash import SingleCommand


class AddSharedFileCommand(SingleCommand):
    def __init__(self, executable, args, input_staging=None, output_staging=None):
        super(AddSharedFileCommand, self).__init__(executable, args)
        self.executable = executable
        self.args = args
        if input_staging is None:
            self._input_staging = []
        else:
            self._input_staging = input_staging

        if output_staging is None:
            self._output_staging = []
        else:
            self._output_staging = output_staging

    def __iter__(self):
        return iter([self.executable] + list(self.args))

    @property
    def input_staging(self):
        return self._input_staging

    @property
    def output_staging(self):
        return self._output_staging


class Resource(object):

    resource = None
    access_schema = None
    exit_on_error = True

    def __init__(self, runtime, cores):
        # question: This splitting in resource does not make sense to me
        # I would say that these should be coupled with the resource definition
        self.runtime = runtime
        self.cores = cores
        self.path_to_shared = None
        self.queue = None
        self.project = None

    def cp_to_shared(self, source_file, target_path):
        source = source_file
        target_main = os.path.join(target_path, os.path.basename(source_file))
        target = os.path.join(self.path_to_shared, target_main)
        return SingleCommand('cp', [source, target])

    def cp_from_shared(self, source_file, target_path):
        source = os.path.join(self.path_to_shared, source_file)
        target = os.path.join(target_path, os.path.basename(source))
        return SingleCommand('cp', [source, target])

    def rm_from_shared(self, source_file):
        source = os.path.join(self.path_to_shared, source_file)
        os.remove(source)

    def mv_to_shared(self, source_file, target_path):
        source = source_file
        target_main = os.path.join(target_path, os.path.basename(source_file))
        target = os.path.join(self.path_to_shared, target_main)
        return SingleCommand('mv', [source, target])

    def mv_from_shared(self, source_file, target_path):
        source = os.path.join(self.path_to_shared, source_file)
        target = os.path.join(target_path, os.path.basename(source))
        return SingleCommand('mv', [source, target])

    @property
    def desc(self):
        # question: This splitting in resource does not make sense to me
        # I would say that these should be coupled with the resource definition
        pd = {
            'resource': self.resource,
            'runtime': self.runtime,
            'exit_on_error': self.exit_on_error,
            'project': self.project,
            'queue': self.queue,
            'access_schema': self.access_schema,
            'cores': self.cores,
        }
        return rp.ComputePilotDescription(pd)


class AllegroCluster(Resource):

    resource = 'fub.allegro'
    access_schema = 'ssh'

    def __init__(self, runtime, cores, queue):
        super(AllegroCluster, self).__init__(runtime, cores)
        self.queue = queue
        self.path_to_shared = os.path.join('$HOME', 'NO_BACKUP')


class LocalCluster(Resource):

    def __init__(self, runtime, cores):
        super(LocalCluster, self).__init__(runtime, cores)
        self.path_to_shared = '$WORK/data/'

    resource = 'local.localhost'
    access_schema = 'local'
