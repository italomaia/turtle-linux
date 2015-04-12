import actor

class Swag(actor.Actor):
    goal = False
    extra_keys = ['value']
    def __init__(self, *args, **kwargs):
        super(Swag, self).__init__(*args, **kwargs)    
        self.value = kwargs.get('value', 100)
                
    def tick(self):
        pass
        
class Goal(Swag):
    goal = True