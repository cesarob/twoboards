"""
Quick'n dirty way to fix all warnings caused on tests because of magic mamba functions that cannot be imported.
See https://github.com/nestorsalceda/mamba/issues/85
"""


class description:
    def __init__(self, *args):
        pass


class describe:
    def __init__(self, *args):
        pass


class before:
    def __init__(self, *args):
        pass

    def each(self, *args):
        pass

    def all(self, *args):
        pass


class after:
    def __init__(self, *args):
        pass

    def each(*args):
        pass

    def all(*args):
        pass


class it:
    def __init__(self, *args):
        pass


class context:
    def __init__(self, *args):
        pass


class self:
    def __init__(self, *args):
        pass
