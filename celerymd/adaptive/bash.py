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


class SingleCommand(Command):
    def __init__(self, executable, args, input_staging=None, output_staging=None):
        super(SingleCommand, self).__init__()
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
        return iter(list(self.command1) + ['&&'] + list(self.command2))

    @property
    def input_staging(self):
        return self.command1.input_staging + self.command2.input_staging

    @property
    def output_staging(self):
        return self.command1.output_staging + self.command2.output_staging
