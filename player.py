import random
from math import sqrt, floor
X = 0
Y = 1
Z = 2
axes = [X, Y, Z]
from world import tilewidth

class Entity:
    # We want the player to be 0.8 of a tile in width, but that must be
    # rounded to the nearest pixel using the construct you see below
    size = 1.0 * int(tilewidth * 0.8) / tilewidth
    size = 1
    #position, maxspeed, diagspeed, accel, friction all set by subclass - differ for each npc/player
    
    @property
    def destination(self):
        # Returns the next-frame position given our current speed
        return [self.position[axis] + self.speed[axis] for axis in axes]

    def collide(self, world):
        # A collision en route to a self.destination alters speed, 
        # as a collision on an axis reduces speed on that axis to 0

        # For the sake of physics (ie non-weapon collisions) all objects are
        # square, so the axis on which the colliding object is farthest on is
        # the axis on which speed is set to 0

        # Typing is hard
        position = self.position

        # Check the distance we're going to travel on each axis. This will
        # allow us to limit the list of objects we test collision against
        xdist = abs(position[0] - self.destination[0])
        ydist = abs(position[1] - self.destination[1])
        zdist = abs(position[2] - self.destination[2])
        traveldist = [abs(position[axis] - self.destination[axis]) for axis in axes]

        # Get the collision entity shortlist
        shortlist = []
        for entity in world.entities:
            valid = True
            entitydist = [abs(position[axis] - entity.position[axis]) for axis in axes]
            for axis in axes:
                # Do a cheap axial distance test.
                if entitydist[axis] > (traveldist[axis] + self.size / 2 + entity.size / 2):
                    valid = False
                    break
            if valid:
                # Eugh, pythagoras is expensive, but its critical that we identify the closest entity!
                # The number of entities that make it to this stage should only be a few anyway
                lineardist = sqrt(pow(entitydist[0], 2) + pow(entitydist[1], 2) + pow(entitydist[2], 2))
                shortlist.append((lineardist, entity))

        # Always check in order of proximity, closest first. 
        # Sort the shortlist by proximity
        shortlist.sort(key=lambda item:item[0])
        collider = None
        for distance, entity in shortlist:
            valid = True
            for axis in axes:
                # "top" and "bottom" are purely terms of convenience here, as
                # these calculations are performed on all axes.
                them_top = entity.postion[axis] - entity.size / 2
                us_bottom = self.destination[axis] + self.size / 2
                if them_top < us_bottom:
                    valid = False
                    break

                them_bottom = entity.position[axis] + entity.size / 2
                us_top = self.destination[axis] - self.size / 2                
                if us_top < them_bottom:
                    valid = False
                    break

            if valid == True:
                # Intersection on all axes - this is a collision!
                collider = entity
                break

        # Check if they're going to collide with terrain
        self.collide_terrain(world)

        self.destination_tile = world.get(*[int(value) for value in self.destination])

        if collider:
            self.collide_entity(entity)


    def collide_terrain(self, world):
        # Test collision with the terrain. Test on one axis at a time, then pairs, then all three
        # You laugh, but it is simple, fast and robust.

        half_size = self.size / 2.0

        # One axis at a time, check if we've crossed a tile border
        for axis in axes:
            if not self.speed[axis]:
                continue

            direction = self.speed[axis] / abs(self.speed[axis])
            if floor(self.position[axis] + half_size * direction) != floor(self.destination[axis] + half_size * direction):
                # We have crossed a tile border! Time to check what we're running into
                direction = self.speed[axis] / abs(self.speed[axis])
                
                other_axis1 = (axis + 1) % 3
                other_axis2 = (axis + 2) % 3
                isolated_destination = self.position[:]
                isolated_destination[axis] = self.destination[axis]

                # Get the tiles we're about to enter for all four corners of our hitbox on that face
                for i in range(4):
                    corner_point = isolated_destination[:]
                    corner_point[axis] += direction * half_size # All points on this face share the same coordinate on the collision axis
                    corner_point[other_axis1] += half_size * (1 + -2 * (i % 2))
                    corner_point[other_axis2] += half_size * (1 + -2 * ((i / 2) % 2))

                    destination_tile = world.get(*[int(floor(coord)) for coord in corner_point])
                    if destination_tile.collision:
                        print "COLLISION HAPPEN: %s" % corner_point
                        print self.position
                        print [int(coord) for coord in corner_point]
                        self.speed[axis] = 0
                        break


    # FUTURE JAMES: Consider the case where we have size != 1 entities!
    # Suddenly the who-is-closest code stops working. Maybe look at that one
    # day when it breaks and not a moment before
    def collide_entity(self, entity):
        # Alter the players speed based on a collision with an object  
        centrepoint = entity.position
        width = entity.size
        for plane_axis in axes:
            print self.speed[plane_axis]
            # Make sure we actually movin'
            if not self.speed[plane_axis]:
                print "Nope? continuing"
                continue

            # Determine the point at which the players trajectory intersects the plane
            intersection = [None for axis in axes]
            tile_centre = floor(self.destination[plane_axis])
            direction = self.speed[plane_axis] / abs(self.speed[plane_axis])
            print "Axis: %s" % plane_axis
            intersection[plane_axis] = tile_centre + (width / 2.0) - (width * direction / 2.0)
            t = (floor(self.destination[plane_axis]) - self.position[plane_axis]) / self.speed[plane_axis]
            for other_axis in [(plane_axis + 1) % 3, (plane_axis + 2) % 3]:
                print "other axis %s: t=%s position=%s" % (other_axis, t, self.destination[plane_axis])
                intersection[other_axis] = self.speed[other_axis] * t + self.destination[other_axis]
            print "Intersection: %s" % intersection

            # Test whether our intersection point is within the square that defines the edge of the tile
            valid = True
            for other_axis in [(plane_axis + 1) % 3, (plane_axis + 2) % 3]:

                tile_bottom = floor(self.destination[other_axis])
                tile_top = tile_bottom + 1
                print "Testing axis: %s" % other_axis
                print tile_bottom, intersection[other_axis], tile_top
                if not tile_bottom <= intersection[other_axis] <= tile_top:
                    valid = False
                    print "INVALID: %s %s" % (intersection[other_axis], other_axis)
                    break

            if valid:
                # We have found the face we are colliding with. Set speed on that axis to 0
                self.speed[plane_axis] = 0
                return

        # This function must be passed a cube we're actually going to collide with :|
        raise Exception("what the FUCK are you doing?")


class Player(Entity):
    #Movestates: left, right, up, down
    movestates = [0, 0, 0, 0]

    def __init__(self, position, config):
        self.position = position[:]
        self.maxspeed = float(config.get('player', 'speed'))
        self.diagspeed = sqrt(pow(self.maxspeed, 2) / 2)
        self.accel = float(config.get('player', 'accel'))
        self.friction = float(config.get('player', 'friction'))
        self.speed = [0, 0, 0]

    def update(self, time_since_last_frame, world):
        #self.movestates has TOO MANY LETTERS IN IT
        a = self.movestates

        #assert (not a[0] and not a[1]) or (a[0] != a[1])
        #assert (not a[2] and not a[3]) or (a[2] != a[3])
        assert not (a[0] and a[1])
        assert not (a[2] and a[3])

        if (a[0] or a[1]) and (a[2] or a[3]):
            #We are travelling diagonally
            xdelta = self.diagspeed - abs(self.speed[X]) 
            xdelta = 0 if xdelta < 0 else xdelta
            ydelta = self.diagspeed - abs(self.speed[Y]) 
            ydelta = 0 if ydelta < 0 else ydelta
            if a[0]:
                self.speed[X] -= xdelta * self.accel
            else:
                self.speed[X] += xdelta * self.accel
            if a[2]:
                self.speed[Y] -= ydelta * self.accel
            else:
                self.speed[Y] += ydelta * self.accel
        else:
            xdelta = self.maxspeed - abs(self.speed[X]) 
            xdelta = 0 if xdelta < 0 else xdelta
            ydelta = self.maxspeed - abs(self.speed[Y]) 
            ydelta = 0 if ydelta < 0 else ydelta
            if a[0]:
                self.speed[X] -= xdelta * self.accel
            elif a[1]:
                self.speed[X] += xdelta * self.accel
            elif a[2]:
                self.speed[Y] -= ydelta * self.accel
            elif a[3]:
                self.speed[Y] += ydelta * self.accel

        #Apply friction
        for i in range(2):
            if self.speed[i]:    
                friction = time_since_last_frame * self.friction
                direction = self.speed[i] / abs(self.speed[i])
                if self.speed[i] * direction < friction:
                    self.speed[i] = 0
                else:
                    self.speed[i] -= friction * direction 
        
        self.collide(world)
        # Finally, set the new position
        self.position = self.destination
        
    x = property(lambda self:self.position[0], lambda self, x:self._setpos(0, x))
    y = property(lambda self:self.position[1], lambda self, y:self._setpos(1, y))
    z = property(lambda self:self.position[2], lambda self, z:self._setpos(2, z))