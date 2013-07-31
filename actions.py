import sys
#To be an action, it must have a go() method and a cooldown
class Quit:
	cooldown = 0
	def go(self, key_event):
		sys.exit()