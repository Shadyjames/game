import sys

#To be an action, it must have a go() method and a cooldown
class Quit:
	cooldown = 0
	def go(self, key_event, **kwargs):
		sys.exit()


'''
This may seem complicated, but the design goals for controlling movement this way is: 
A: It provides simultaneity for application of the direction of the players movement
to the players speed, so that we can recognise when they travel diagonally	
B: I wanted to be able to manage contradictory directional commands in such a way that
a player who is making a quick directional change who holds both opposing keys for a few 
frames is not penalised by not accellerating for those frames
This way, the more recent of two opposing directional commands will take precedence.
'''
class Player_MoveDown:
	cooldown = 0
	def go(self, key_event, player=None, **kwargs):
		if key_event == 'down':
			player.movestates[3] = 1
			player.movestates[2] = 0
		elif key_event == 'up':
			player.movestates[3] = 0
		elif key_event == 'held' and player.movestates[2] == 0:
			player.movestates[3] = 1
class Player_MoveUp:
	cooldown = 0
	def go(self, key_event, player=None, **kwargs):
		if key_event == 'down':
			player.movestates[2] = 1
			player.movestates[3] = 0
		elif key_event == 'up':
			player.movestates[2] = 0
		elif key_event == 'held' and player.movestates[3] == 0:
			player.movestates[2] = 1
class Player_MoveRight:
	cooldown = 0
	def go(self, key_event, player=None, **kwargs):
		if key_event == 'down':
			player.movestates[1] = 1
			player.movestates[0] = 0
		elif key_event == 'up':
			player.movestates[1] = 0
		elif key_event == 'held' and player.movestates[0] == 0:
			player.movestates[1] = 1
class Player_MoveLeft:
	cooldown = 0
	def go(self, key_event, player=None, **kwargs):
		if key_event == 'down':
			player.movestates[0] = 1
			player.movestates[1] = 0
		elif key_event == 'up':
			player.movestates[0] = 0
		elif key_event == 'held' and player.movestates[1] == 0:
			player.movestates[0] = 1
