import radical.pilot as rp


class Command(object):
    bash_exec = '/bin/bash'
    bash_args = ['-c', '-l']

    def __mul__(self, other):
        if isinstance(other, int):
            return RepeatCommand(self, other)
        else:
            raise ValueError('multiplication only with integers')

    def __str__(self):
        return ' '.join(self)

    def __call__(self, *args, **kwargs):
        """
        A command can also do something in the application

        """
        pass

    @property
    def bash(self):
        return self.bash_exec + list(self)

    @property
    def bash_str(self):
        return ' '.join(self.bash_exec + list(self))

    def __iter__(self):
        return iter([])

    def __add__(self, other):
        if isinstance(other, Command):
            return ChainCommand(self, other)
        elif isinstance(other, list):
            return list(self) + other
        elif other is None:
            return list(self)
        else:
            raise NotImplemented

    def __radd__(self, other):
        if isinstance(other, list):
            return other + list(self)
        else:
            raise NotImplemented

    @property
    def input_staging(self):
        return []

    @property
    def output_staging(self):
        return []

    def to_cud(self):
        cud = rp.ComputeUnitDescription()
        cud.executable = self.bash_exec
        cud.arguments = self.bash_args + list(self)
        cud.input_staging = self.input_staging
        cud.output_staging = self.output_staging


class StagingCommand(Command):
    def __init__(self, staging, mode=rp.STAGING_INPUT):
        super(StagingCommand, self).__init__()

        self.mode = mode
        self.staging = staging

        if mode not in [rp.STAGING_INPUT, rp.STAGING_OUTPUT]:
            raise ValueError('Can only use rp.STAGING_INPUT or rp.STAGING_OUTPUT.')

    @property
    def source(self):
        return self.staging['source']

    @property
    def target(self):
        return self.staging['target']

    @property
    def action(self):
        return self.staging['action']

    @property
    def input_staging(self):
        if self.mode == rp.STAGING_INPUT:
            return self.staging
        else:
            return []

    @property
    def output_staging(self):
        if self.mode == rp.STAGING_OUTPUT:
            return self.staging
        else:
            return []


class BashCommand(Command):
    def __init__(self, executable, args):
        super(BashCommand, self).__init__()
        self.executable = executable
        self.args = args

    def __iter__(self):
        return iter([self.executable] + list(self.args))


class RepeatCommand(Command):
    def __init__(self, command, multiplication):
        super(RepeatCommand, self).__init__()
        self.command = command
        self.multiplication = multiplication

    def __iter__(self):
        return iter(((list(self.command) + ['&&']) * self.multiplication)[:-1])

    @property
    def input_staging(self):
        return self.command.input_staging

    @property
    def output_staging(self):
        return self.command.output_staging


class ChainCommand(Command):
    def __init__(self, command1, command2):
        super(ChainCommand, self).__init__()
        self.command1 = command1
        self.command2 = command2

    def __iter__(self):
        c1 = list(self.command1)
        c2 = list(self.command2)
        if c1 and c2:
            return iter(c1 + ['&&'] + c2)
        else:
            return iter(c1 + c2)

    @property
    def input_staging(self):
        return self.command1.input_staging + self.command2.input_staging

    @property
    def output_staging(self):
        return self.command1.output_staging + self.command2.output_staging
