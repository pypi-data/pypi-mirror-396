class PostFork:
    """
    Mock for uwsgi postfork
    """

    def __init__(self, func):
        if callable(func):
            self.func = func
        else:
            self.func = None

    # pylint: disable=R1710
    def __call__(self, *args, **kwargs):
        if self.func:
            return self.func()
        self.func = args[0]
