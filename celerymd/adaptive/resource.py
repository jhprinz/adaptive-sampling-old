import radical.pilot as rp
import os

from command import BashCommand, StagingCommand
from util import get_type


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

    # --------------------------------------------------------------------------
    # commands to move to and from shared
    # --------------------------------------------------------------------------

    # `file://`, `shared://`, `staging://` or `` for on unit/agent
    # rp.TRANSFER, rp.LINK, rp.MOVE, rp.COPY
    # not all combinations are possible, of course

    def copy(self, source, target=None, stage=None):
        st = get_type(source)
        tt = get_type(target)

        if target is None:
            target = ''

        if os.path.basename(target) == '':
            target = target + os.path.basename(source)

        if st in ['file'] and tt in ['staging', 'unit']:
            stage = stage or rp.STAGING_INPUT
            return StagingCommand({
                'source': source,
                'target': target,
                'action': rp.TRANSFER
            }, stage)
        elif st in ['shared', 'unit'] and tt in ['shared', 'unit']:
            source = source.replace('shared://', self.path_to_shared)
            target = target.replace('shared://', self.path_to_shared)
            return BashCommand('cp', [source, target])
        elif st in ['staging'] and tt in ['unit']:
            stage = stage or rp.STAGING_INPUT
            return StagingCommand({
                'source': source,
                'target': target,
                'action': rp.TRANSFER
            }, stage)
        elif st in ['unit'] and tt in ['staging', 'file']:
            stage = stage or rp.STAGING_OUTPUT
            return StagingCommand({
                'source': source,
                'target': target,
                'action': rp.TRANSFER
            }, stage)
        else:
            raise NotImplementedError(
                'copying from `%s` to `%s` is not implemented yet.' % (st, tt))

    def mv(self, source, target=None):
        st = get_type(source)
        tt = get_type(target)

        if target is None:
            target = ''

        if os.path.basename(target) == '':
            target = target + os.path.basename(source)

        if st in ['shared', 'unit'] and tt in ['shared', 'unit']:
            source = source.replace('shared://', self.path_to_shared)
            target = target.replace('shared://', self.path_to_shared)
            return BashCommand('cp', [source, target])
        else:
            raise NotImplementedError(
                'moving from `%s` to `%s` is not implemented yet.' % (st, tt))

    def link(self, source, target=None, stage=None):
        st = get_type(source)
        tt = get_type(target)

        if target is None:
            target = ''

        if os.path.basename(target) == '':
            target = target + os.path.basename(source)

        if st in ['shared'] and tt in ['unit']:
            source = source.replace('shared://', self.path_to_shared)
            target = target.replace('shared://', self.path_to_shared)
            return BashCommand('ln', ['-l', source, target])
        elif st in ['staging'] and tt in ['unit']:
            stage = stage or rp.STAGING_INPUT
            return StagingCommand({
                'source': source,
                'target': target,
                'action': rp.LINK
            }, stage)
        else:
            raise NotImplementedError(
                'linking from `%s` to `%s` is not implemented yet.' % (st, tt))

    def remove(self, source):
        st = get_type(source)

        if st in ['shared', 'unit']:
            source = source.replace('shared://', self.path_to_shared)
            return BashCommand('rm', [source])
        else:
            raise NotImplementedError(
                'deleting from `%s` is not implemented yet.' % st)

    def makedir(self, source):
        st = get_type(source)

        if st in ['shared', 'unit']:
            source = source.replace('shared://', self.path_to_shared)
            return BashCommand('mkdir', [source])
        else:
            raise NotImplementedError(
                'makedir in `%s` is not implemented yet.' % st)

    # def cp_to_shared(self, source, target):
    #     source = source
    #     target_main = os.path.join(target, os.path.basename(source))
    #     target = os.path.join(self.path_to_shared, target_main)
    #     return BashCommand('cp', [source, target])
    #
    # def cp_from_shared(self, source, target):
    #     source = os.path.join(self.path_to_shared, source)
    #     target = os.path.join(target, os.path.basename(source))
    #     return BashCommand('cp', [source, target])

    # def rm_from_shared(self, source_file):
    #     source = os.path.join(self.path_to_shared, source_file)
    #     os.remove(source)
    #
    # def mv_to_shared(self, source_file, target_path):
    #     source = source_file
    #     target_main = os.path.join(target_path, os.path.basename(source_file))
    #     target = os.path.join(self.path_to_shared, target_main)
    #     return BashCommand('mv', [source, target])
    #
    # def mv_from_shared(self, source_file, target_path):
    #     source = os.path.join(self.path_to_shared, source_file)
    #     target = os.path.join(target_path, os.path.basename(source))
    #     return BashCommand('mv', [source, target])

    # --------------------------------------------------------------------------
    # commands to move to and from stage / shared pilot area
    # --------------------------------------------------------------------------

    # def transfer_from_stage(self, source_file, target_path):
    #     target = os.path.basename(source_file)
    #     return StagingCommand(input_staging=[{
    #         'source': 'staging:///%s' % source_file,
    #         'target': target,
    #         'action': rp.TRANSFER
    #     }])
    #
    # def link_from_stage(self, source):
    #     target = os.path.basename(source)
    #     return StagingCommand(input_staging=[{
    #         'source': 'staging:///%s' % target,
    #         'target': target,
    #         'action': rp.LINK
    #     }])

    # def transfer_to_stage(self, source):
    #     target = os.path.basename(source)
    #     return StagingCommand(input_staging=[{
    #         'source': 'file://%s' % source,
    #         'target': 'staging:///%s' % target,
    #         'action': rp.TRANSFER
    #     }])

    # --------------------------------------------------------------------------
    # commands to move to and from application
    # --------------------------------------------------------------------------

    # def transfer_to(self, source):
    #     target = os.path.basename(source)
    #     return StagingCommand(input_staging=[{
    #         'source': 'file://%s' % source,
    #         'target': target,
    #         'action': rp.TRANSFER
    #     }])

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
