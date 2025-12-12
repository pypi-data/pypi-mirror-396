class Scaffold:
    def __init__(self, context):
        self.context = context

    def init_scaffold(self, config):
        self.config = config

    @property
    def debug(self) -> bool:
        return self.context.debug

    @property
    def env(self) -> str:
        return self.context.env
