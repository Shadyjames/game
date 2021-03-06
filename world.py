from math import floor, ceil
import math
import os
import sys
tilewidth = 32

tile_properties = [
    {"collision":False, "friendly_name": "Black"},
    {"collision":False, "friendly_name": "Shit grass"},
    {"collision":False, "friendly_name": "Happyface"},
    {"collision":False, "friendly_name": "Sand"},
    {"collision":False, "friendly_name": "Green grass"},
    {"collision":True, "friendly_name": "Rock"}
]

class World:
    def __init__(self, x=12, y=12, z=1, chunkwidth=3):
        '''World(x=12, y=12, z=1, chunkwidth=3)
        x and y MUST be divisible by chunkwidth. Behaviour for (x mod chunkwidth) != 0 is undefined
        '''
        assert (x % chunkwidth) == 0
        assert (y % chunkwidth) == 0
        self.x = x
        self.y = y
        self.z = z
        self.x_chunks = x/chunkwidth
        self.y_chunks = y/chunkwidth
        self.chunkwidth = chunkwidth
        self.chunksize = pow(self.chunkwidth, 2)
        self.chunks = self.new_chunklist()
        self.fill(2)
        #self.coordinate_fill()
        self.save('test')
        '''
        self.save_chunks('test', [[3, 3, 0]])
        
        self.empty()
        self.load_chunks('test', [[3, 3, 0]]) # Load chunks not working?
        self.load('test')
        '''
        self.entities = []

    def load(self, filename):
        path = os.path.join('save', filename + '.world')
        if os.path.exists(path):
            f = open(path, 'rb')
        else:
            raise Exception("File does not exist")

        self.x, self.y, self.z = [int(f.read(16).encode('hex'), 16) for i in range(3)]
        print self.x, self.y, self.z

        self.chunks = self.new_chunklist()
        print self.chunks
        for x in range(len(self.chunks)):
            for y in range(len(self.chunks[x])):
                for z in range(len(self.chunks[x][y])):
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
                        writebuffer += self.bytes_from_chunk(chunk)
                    elif initial:
                        writebuffer = ''.zfill(self.chunksize * 2)
                    f.write(writebuffer.decode('hex'))
                    writebuffer = ''

    #This should only ever be called when a full savefile has already been created with save()
    def save_chunks(self, filename, chunks):
        savepath = os.path.join('save', filename + ".world")
        f = open(savepath, 'r+b')
        for chunk in chunks:
            x, y, z = chunk
            pos = (x * len(self.chunks[x][y]) * len(self.chunks[x]) + y * len(self.chunks[x][y]) + z) * self.chunksize + 48
            f.seek(pos)
            bytes = self.bytes_from_chunk(self.chunks[x][y][z])
            f.write(bytes.decode('hex'))

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
            if not (chunk_x >= 0 and chunk_y >= 0 and z >= 0):
                raise IndexError
            chunk = self.chunks[chunk_x][chunk_y][z]
        except IndexError:
            #print "WARNING: Attempted to get tile that was outside the map. Returning grass"
            return Tile(0)
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

    def bytes_from_chunk(self, chunk):
        bytes = ''
        for chunk_x in range(self.chunkwidth):
            for chunk_y in range(self.chunkwidth):
                tile_type = chunk.get(chunk_x, chunk_y).type
                bytes += hex(tile_type)[2:].zfill(2)
        return bytes

    @property
    def selection_rect(self):
        #app.active_world.selection_* is TOO MANY LETTERS
        #Shortern to point a, point b
        a = self.selection_start[:]
        a = (int(floor(a[0])), int(floor(a[1])))
        b = self.selection_end[:]
        b = (int(ceil(b[0])), int(ceil(b[1])))
        print a, b
        rect = [a[0] if a[0] < b[0] else b[0], 
                a[1] if a[1] < b[1] else b[1], 
                abs(a[0] - b[0]),
                abs(a[1] - b[1])]
        return rect

    #Returns a flat region of a world. Avoids chunk lookup calculations used in get()
    def get_rect(self, rect, z, debug=False):
        xorig, yorig, w, h = rect
        #print rect
        chunks_involved = [[None for y in range(int(ceil(float(h + yorig % self.chunkwidth) / self.chunkwidth)))] for x in range(int(ceil(float(w + xorig % self.chunkwidth) / self.chunkwidth)))]
        #print "chunks_involved dimensions: %s, %s" % (len(chunks_involved), len(chunks_involved[0]))
        if debug:
            print rect
        #print rect
        region = [[] for x in range(w)]
        chunks_involved = [[None for y in range(yorig / self.chunkwidth, (yorig+h-1) / self.chunkwidth + 1)] for x in range(xorig / self.chunkwidth, (xorig+w-1) / self.chunkwidth + 1)]
        for x in range(len(chunks_involved)):
            for y in range(len(chunks_involved[0])):
                xindex = x + xorig/self.chunkwidth
                yindex = y + yorig/self.chunkwidth
                if xindex < 0 or yindex < 0 or xindex >= len(self.chunks) or yindex >= len(self.chunks[xindex]):
                    chunks_involved[x][y] = None
                else:
                    chunks_involved[x][y] = self.chunks[xindex][yindex][z]


        if debug:
            print chunks_involved
        region = [[] for x in range(w)]
        for x in range(w):
            if debug:
                print "NEW X STARTED"
            x_chunk = (x + xorig % self.chunkwidth) / self.chunkwidth
            x_local = (x + xorig) % self.chunkwidth
            start = (yorig) % self.chunkwidth
            chunk = chunks_involved[x_chunk][0]
            if chunk is not None:
                region[x] += chunk.tiles[x_local][start:]
                if debug:
                    print "Added Tiles to world initial: %s" % len(chunk.tiles[x_local][start:])
            else:
                region[x] += [None for i in range(self.chunkwidth - start)]
                if debug:
                    print "Added Nones to world initial: %s" % len(region[x])
            if len(chunks_involved[x_chunk]) > 2:
                for y in range (1, len(chunks_involved[x_chunk]) - 1):
                    chunk = chunks_involved[x_chunk][y]
                    if chunk is not None:
                        region[x] += chunk.tiles[x_local]
                        if debug:
                            print "Added Tiles to world: %s" % len(chunk.tiles[x_local])
                    else:
                        region[x] += [None for i in range(self.chunkwidth)]
                        if debug:
                            print "Added Nones to world: %s" % self.chunkwidth
            if len(chunks_involved[x_chunk]) > 1:
                finish = (yorig + h) % self.chunkwidth
                if finish == 0:
                    finish = self.chunkwidth
                chunk = chunks_involved[x_chunk][-1]
                if chunk is not None:
                    region[x] += chunk.tiles[x_local][:finish]
                    if debug:
                        print "Added Tiles to world final: %s" % finish
                else:
                    region[x] += [None for i in range(finish)]
                    if debug:
                        print "Added Nones to world final: %s" % finish
            ##print "Added to world final: %s" % finish
            
        #print region
        #print len(region)
        #print [len(y) for y in region]
        if debug:
            print region
            print len(region[0])
        return region

    def fill_rect(self, rect, tile_type, z):
        #print rect
        xorig, yorig, w, h = rect
        region = [[Tile(tile_type) for y in range(h)] for x in range(w)]
        #print region
        self.set_rect([xorig, yorig], region, z)

    #Sets a flat region of a world. Avoids chunk lookup calculations used in get()
    def set_rect(self, location, region, z):
        print region
        xorig, yorig = location
        w = len(region)
        h = len(region[0])
        if xorig < 0 or yorig < 0 or w <= 0 or h <= 0 or self.x < xorig or self.y < yorig:
            # Pasting outside the map? We have no time for THAT funny business
            print xorig, yorig
            print self.x, self.y
            raise Exception("The fuck is this shit")
        if xorig + w - 1 > self.x:
            print xorig, w, self.x
            print "WARNING: region set by set_rect was truncated because part of the x dimension fell outside the world"
            region = region[:self.x - xorig + 1]
            w = len(region)
        if yorig + h - 1 > self.y:
            print "WARNING: region set by set_rect was truncated because part of the y dimension fell outside the world"
            region = [column[:self.y - yorig] for column in region]
            h = len(region[0])
        chunks_involved = [[None for y in range(int(ceil(float(h + yorig % self.chunkwidth) / self.chunkwidth)))] for x in range(int(ceil(float(w + xorig % self.chunkwidth) / self.chunkwidth)))]
        #region = [[] for x in range(w)]
        '''
        print yorig, h, self.chunkwidth
        print yorig / self.chunkwidth
        print (yorig+h - 1) / self.chunkwidth + 1
        print range(yorig/self.chunkwidth, (yorig+h-1)/ self.chunkwidth + 1)
        '''
        chunks_involved = [[None for y in range(yorig / self.chunkwidth, (yorig+h-1) / self.chunkwidth + 1)] for x in range(xorig / self.chunkwidth, (xorig+w-1) / self.chunkwidth + 1)]
        for x in range(len(chunks_involved)):
            for y in range(len(chunks_involved[0])):
                xindex = x + xorig/self.chunkwidth
                yindex = y + yorig/self.chunkwidth
                if xindex < 0 or yindex < 0 or xindex >= len(self.chunks) or yindex >= len(self.chunks[xindex]):
                    chunks_involved[x][y] = None
                else:
                    chunks_involved[x][y] = self.chunks[xindex][yindex][z]

        #print chunks_involved

        #print chunks_involved
        #region = [[] for x in range(w)]

        #For every column
        for x in range(w):
            #Determine the chunk and local x-coords for this column
            x_chunk = (x + xorig % self.chunkwidth) / self.chunkwidth
            x_local = (x + xorig) % self.chunkwidth
            #Determine the yorigins local y-coord
            start = self.chunkwidth - (yorig % self.chunkwidth)
            chunk = chunks_involved[x_chunk][0]
            #If the chunk is None
            #print chunks_involved
            if chunk is not None:
                '''
                print "INITIAL ASSIGNMENT:"
                print start
                print chunk.tiles[x_local]
                print region[x]
                print region[x][:start], region[x][start:]
                print chunk.tiles[x_local][:self.chunkwidth - start], region[x][:start], chunk.tiles[x_local][self.chunkwidth - start + len(region[x][:start]):]
                '''
                chunk.tiles[x_local] = chunk.tiles[x_local][:self.chunkwidth - start] + region[x][:start] + chunk.tiles[x_local][self.chunkwidth - start + len(region[x][:start]):]
                #print chunk.tiles[x_local]
                slice_end = start
            if len(chunks_involved[x_chunk]) > 2:
                for y_chunk in range (1, len(chunks_involved[x_chunk]) - 1):
                    chunk = chunks_involved[x_chunk][y_chunk]
                    print chunk
                    print x_chunk, y_chunk
                    if chunk is not None:
                        slice_start = start + self.chunkwidth * (y_chunk - 1)
                        slice_end = slice_start + self.chunkwidth
                        print chunk.tiles[x_local]
                        print region[x][slice_start:slice_end]
                        chunk.tiles[x_local] = region[x][slice_start:slice_end]
            if len(chunks_involved[x_chunk]) > 1:
                chunk = chunks_involved[x_chunk][-1]
                tail = region[x][slice_end:]
                if chunk is not None:
                    '''
                    print "TAIL ASSIGNMENT:"
                    print tail
                    print region
                    print region[x]
                    print region[x][slice_end:]
                    print slice_end
                    print chunk.tiles[x_local]
                    '''
                    chunk.tiles[x_local] = tail + chunk.tiles[x_local][len(tail):]
                    #print chunk.tiles[x_local]
        #print "COCKS COCKS COCKS"
        #print self.get(2, 2)
        #return region

class Chunk:
    def __init__(self, chunkwidth):
        self.tiles = [[Tile(0) for y in range(chunkwidth)] for x in range(chunkwidth)]

    def get(self, x, y):
        return self.tiles[x][y]

    def set(self, newtile, x, y):
        self.tiles[x][y] = newtile

class Tile:
    def __init__(self, tile_type):
        self.type = tile_type

        #Tiles may be occupied by things like chests and doors
        self.occupant = None

    @property
    def collision(self):
        if self.occupant and self.occupant.collision:
            return True
        else:
            return tile_properties[self.type]['collision']


    def __repr__(self):
        return "<Tile, type=%s>" % self.type