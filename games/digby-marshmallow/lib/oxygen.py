import actor

class Oxygen(actor.Actor):
    extra_keys = ['capacity', 'pipe_length', 'is_initial']
    def __init__(self, *args, **kwargs):
        super(Oxygen, self).__init__(*args, **kwargs)
        self.capacity = kwargs.get('capacity', 3000)
        self.contained = self.capacity
        self.pipe_length = kwargs.get('pipe_length', 5000)
        self.is_initial = kwargs.get('is_initial', False)
    def tick(self):
        if self.contained == 0:
            self.world.dispatch_event("on_suffocate")
