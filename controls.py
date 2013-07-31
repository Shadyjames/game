class Control:
	state = False
	time_to_ready = 0
	def __init__(self, action):
		self.action = action

	def update(self, state):
		if self.time_to_ready > 0:
			self.state = state
			return
		if self.state == False and state == True:
			print self.action
			self.action.go('down')
			self.time_to_ready  = self.downaction.cooldown
		elif self.state == True and state == False:
			self.action.go('up')
			self.time_to_ready  = self.upaction.cooldown
		elif state == True:
			self.action.go('held')
			self.time_to_ready = self.holdaction.cooldown
		self.state = state