class Control:
    state = False
    time_to_ready = 0
    def __init__(self, action):
        self.action = action