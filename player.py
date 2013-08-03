from math import sqrt
X = 0
Y = 1
Z = 2
class Player:
	speed = [0, 0, 0]
	
	#Movestates: left, right, up, down
	movestates = [0, 0, 0, 0]

	def __init__(self, position, config):
		self.position = position[:]
		self.maxspeed = float(config.get('player', 'speed'))
		self.diagspeed = sqrt(pow(self.maxspeed, 2) / 2)
		self.accel = float(config.get('player', 'accel'))
		self.friction = float(config.get('player', 'friction'))

	def update(self):
		#self.movestates has TOO MANY LETTERS IN IT
		a = self.movestates

		print a
		assert (not a[0] and not a[1]) or (a[0] != a[1])
		assert (not a[2] and not a[3]) or (a[2] != a[3])

		if (a[0] or a[1]) and (a[2] or a[3]):
			print "DIAGONAL MOTHERFUCKERS"
			#We are travelling diagonally
			if a[0]:
				self.speed[X] -= abs(abs(self.speed[X]) - self.diagspeed) * self.accel
			else:
				self.speed[X] += abs(abs(self.speed[X]) - self.diagspeed) * self.accel
			if a[2]:
				self.speed[Y] -= abs(abs(self.speed[Y]) - self.diagspeed) * self.accel
			else:
				self.speed[Y] += abs(abs(self.speed[Y]) - self.diagspeed) * self.accel
		elif a[0]:
			self.speed[X] -= abs(abs(self.speed[X]) - self.maxspeed) * self.accel
		elif a[1]:
			self.speed[X] += abs(abs(self.speed[X]) - self.maxspeed) * self.accel
		elif a[2]:
			self.speed[Y] -= abs(abs(self.speed[Y]) - self.maxspeed) * self.accel
		elif a[3]:
			self.speed[Y] += abs(abs(self.speed[Y]) - self.maxspeed) * self.accel
		self.position = [self.position[i] + self.speed[i] for i in range(3)]

		#Apply friction
		for i in range(2):
			if abs(self.speed[i]) < self.friction:
				self.speed[i] = 0
			else:
				self.speed[i] -= self.friction * self.speed[i] / abs(self.speed[i])

	x = property(lambda self:self.position[0], lambda self, x:self._setpos(0, x))
	y = property(lambda self:self.position[1], lambda self, y:self._setpos(1, y))
	z = property(lambda self:self.position[2], lambda self, z:self._setpos(2, z))