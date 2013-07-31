class Player:
	def __init__(self, position):
		self.position = position[:]

	def _getpos(self, axis):
		return self.position[axis]

	def _setpos(self, axis, value):
		self.position[axis] = value

	x = property(lambda self:self._getpos(0), lambda self, x:self._setpos(0, x))
	y = property(lambda self:self._getpos(1), lambda self, y:self._setpos(1, y))
	z = property(lambda self:self._getpos(2), lambda self, z:self._setpos(2, z))