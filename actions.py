import sys
#To be an action, it must have a go() method and a cooldown
class Action_Quit:
	cooldown = 0
	def go(self, key_event):
		sys.exit()
