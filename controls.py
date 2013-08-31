class Control:
    state = False
    time_to_ready = 0
    def __init__(self, action):
        self.action = action

    def update(self, state, **kwargs):
        if self.time_to_ready > 0:
            self.state = state
            return
        if self.state == False and state == True:
            print self.action
            self.action.go('down', **kwargs)
        elif self.state == True and state == False:
            self.action.go('up', **kwargs)
        elif state == True:
            self.action.go('held', **kwargs)
        self.time_to_ready  = getattr(self.action, 'cooldown', 0)
        self.state = state