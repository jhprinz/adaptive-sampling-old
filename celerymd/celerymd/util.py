# This will force each child process to have a seperate INSTANCE_UUID
# only necessary if you fork your processes in which case python
# will reuse exising variables that _seem_ untouched and the ops package
# import will not be executed again
# on remote machine this should actually not be necessary


# it is ops specific to reuse objects

def _redo_uuid(**kwargs):
    import logging
    import openpathsampling.netcdfplus as npl

    logger = logging.getLogger(__name__)

    npl.StorableObject.initialize_uuid()
    logger.info('NEW UUID `%s`' % npl.StorableObject.INSTANCE_UUID)
