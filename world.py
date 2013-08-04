from math import floor
import math
import os
import sys

class World:
    def __init__(self, x, y, z, chunksize=3):
        self.x = x
        self.y = y
        self.z = z
        self.x_chunks = x/chunksize
        self.y_chunks = y/chunksize
        self.chunkwidth = chunksize
        self.chunksize = pow(self.chunkwidth, 2)
        self.chunks = self.new_chunklist()
        print self.chunks
        self.fill(2)
        self.save('test')
        self.empty()
        self.load_chunks('test', [[3, 3, 0]])
        self.load('test')

    def load(self, filename):
        path = os.path.join('save', filename + '.world')
        if os.path.exists(path):
            f = open(path, 'rb')
        else:
            raise Exception("File does not exist")

        self.x, self.y, self.z = [int(f.read(16).encode('hex'), 16) for i in range(3)]

        self.chunks = self.new_chunklist()
        for x in range(len(self.chunks)):
            for y in range(len(self.chunks[x])):
                for z in range(len(self.chunks[y])):
                    self.chunks[x][y][z] = self.chunk_from_bytes(f.read(self.chunksize))


    def load_chunks(self, filename, coords):
        #Load a list of chunks from the world file and place them in memory
        path = os.path.join('save', filename + '.world')

        if os.path.exists(path):
            f = open(path, 'rb')
        else:
            raise Exception("File does not exist")

        for coordinate in coords:
            x, y, z = coordinate
            if x >= self.x_chunks or y >= self.y_chunks or z >= self.z:
                raise Exception("Coordinates are outside of world size")
            pos = x * len(self.chunks[0][0]) * len(self.chunks[0]) * self.chunksize + y * len(self.chunks[0][0]) * self.chunksize + z * self.chunksize + 48
            f.seek(pos)
            bytes = f.read(self.chunksize)
            print pos
            print bytes
            self.chunks[x][y][z] = self.chunk_from_bytes(bytes)


    def save(self, filename):
        ###SAVE FILE FORMAT NOTES###
        '''
        begins with 16 bytes for world x, 16 bytes for world y, 16 bytes for world z
        then x*y*z bytes of data where each byte at position "pos" respresents the tile 
        type at the coordinates:
        z = ((pos-48) % (world_z*world_y*pow(chunksize, 2))) % world_y*pow(chunksize, 2)
        y = floor(((pos-48) %  (world_x*world_y*pow(chunksize, 2))) / world_z*pow(chunksize, 2))
        x = floor((pos-48) / world_z*world_y*pow(chunksize, 2)) 

        and vice versa:
        pos = x * world_z * world_y * pow(chunksize, 2) + y * world_z * pow(chunksize, 2) + z + 48

        In order to test this we need to populate a world with chunks where every 3 tiles 
        are the chunks x y z coordinates, which would make it easy to do a bunch of spastic
        reads and writes to the savefile and then programmatically confirm the data integrity

        '''

        print os.getcwd()
        print os.listdir('save')
        savepath = os.path.join('save', filename + ".world")

        if os.path.exists(savepath):
            initial = False
            f = open(savepath, 'r+b')
        else:
            initial = True
            f = open(savepath, 'w+b')

        #Write the world dimensions
        writebuffer = ''

        #It may seem excessive, but the world dimensions are 16-byte
        #lick my balls
        xstring = hex(self.x)[2:].zfill(32)
        ystring = hex(self.y)[2:].zfill(32)
        zstring = hex(self.z)[2:].zfill(32)
        writebuffer += xstring + ystring + zstring
        pants = writebuffer.decode('hex')
        f.write(writebuffer.decode('hex'))
        writebuffer = ''
        
        lastpos = 47

        #Write out the contents of each chunk
        for x in range(len(self.chunks)):
            for y in range(len(self.chunks[x])):
                for z in range(len(self.chunks[x][y])):
                    '''
                    print x
                    print len(self.chunks)
                    print y
                    print len(self.chunks[x])
                    print z
                    print len(self.chunks[x][y])
                    '''
                    chunk = self.chunks[x][y][z]
                    
                    #WHY NOT ASSERT DATA INTEGRITY!?!?
                    pos = x * len(self.chunks[x][y]) * len(self.chunks[x]) + y * len(self.chunks[x][y]) + z + 48
                    if pos != lastpos + 1:
                        print pos
                        print "SHIT SHIT SHIT"
                        sys.exit()
                    lastpos = pos

                    if chunk is not None:
                        for chunk_x in range(self.chunkwidth):
                            for chunk_y in range(self.chunkwidth):
                                tile_type = chunk.get(chunk_x, chunk_y).type
                                writebuffer += hex(tile_type)[2:].zfill(2)
                    elif initial:
                        writebuffer = ''.zfill(self.chunksize * 2)
                    f.write(writebuffer.decode('hex'))
                    writebuffer = ''


    def new_chunklist(self):
        #rofl list comprehension
        return [[[None for a in range(self.z)] for b in range(int(math.ceil(float(self.y) / float(self.chunkwidth))))] for c in range(int(math.ceil(float(self.x) / float(self.chunkwidth))))]

    def empty(self):
        self.chunks = self.new_chunklist()

    def purge(self, player_x, player_y, chunk_span):
        #Remove all the chunks from memory but the ones near the player
        #Criterion is delta_x + delta_y < chunk_span
        #A good chunk_span is a number like 3-5.
        pass

    def get(self, x, y, z=0):
        local_x = x % self.chunkwidth
        local_y = y % self.chunkwidth
        chunk_x = (x - local_x) / self.chunkwidth
        chunk_y = (y - local_y) / self.chunkwidth
        try:
            chunk = self.chunks[chunk_x][chunk_y][z]
        except IndexError:
            #print "WARNING: Attempted to get tile that was outside the map. Returning grass"
            return Tile(1)
        if chunk:
            tile = chunk.get(local_x, local_y)
        else:
            print "WARNING: Attempted to get tile that was not in loaded chunk. Returning grass"
            return Tile(1)
        return tile

    def set(self, newtile, x, y, z=0):
        local_x = x % self.chunkwidth
        local_y = y % self.chunkwidth
        chunk_x = (x - local_x) / self.chunkwidth
        chunk_y = (y - local_y) / self.chunkwidth
        chunk = self.chunks[chunk_x][chunk_y][z]
        if chunk is None:
            chunk = Chunk(self.chunkwidth)
            self.chunks[chunk_x][chunk_y][z] = chunk

        chunk.set(newtile, local_x, local_y)

    def coordinate_fill(self):
        for x in range(len(self.chunks)):
            for y in range(len(self.chunks[x])):
                for z in range(len(self.chunks[x][y])):
                    output = [x, y, z, 0]
                    #print "Writing in " + str(output)
                    mod = 0
                    self.chunks[x][y][z] = Chunk(self.chunkwidth)
                    for chunk_x in range(self.chunkwidth):
                        for chunk_y in range(self.chunkwidth):
                            self.chunks[x][y][z].set(Tile(output[mod]), chunk_x, chunk_y)
                            mod = (mod + 1) % 4

    def fill(self, type):
        for x in range(self.x):
            for y in range(self.y):
                for z in range(self.z):
                    self.set(Tile(type), x, y, z)

    def chunk_from_bytes(self, bytes):
        chunk = Chunk(self.chunkwidth)
        for index in range(len(bytes)):
            x = index % self.chunkwidth
            y = index / self.chunkwidth
            chunk.set(Tile(ord(bytes[index])), x, y)

        return chunk

class Chunk:
    def __init__(self, chunkwidth):
        self.tiles = [[Tile(1) for y in range(chunkwidth)] for x in range(chunkwidth)]

    def get(self, x, y):
        return self.tiles[x][y]

    def set(self, newtile, x, y):
        self.tiles[x][y] = newtile

class Tile:
    def __init__(self, tile_type):
        self.type = tile_type

        #Tiles may be occupied by things like chests and doors
        self.occupant = None