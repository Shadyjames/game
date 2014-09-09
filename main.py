#Main file for mah game.
import pygame
import time
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from render import screen, draw_world, windowx, windowy
from math import floor
import actions
import os

last_time = time.clock()


class App:
    def __init__(self):
        self.running = True
        self.last_time = time.clock()
        self.config = ConfigParser.ConfigParser()
        self.config.read("settings.cfg")
        self.player = Player.Player([20, 12, 0], self.config)
        self.windowx = windowx
        self.windowy = windowy
        self.tilewidth = 32
        self.screen = screen
        
        self.world = World.World(x=int(self.config.get('world', 'x')), y=int(self.config.get('world', 'y')), z=10)
        #world.load()

        #Load control bindings
        self.bindings = ConfigParser.ConfigParser()
        self.bindings.optionxform = str
        self.bindings.read("bindings.cfg")
        self.controls = {}

        #Load tile images
        self.tile_images = {}
        self.other_images = {}
        files = os.listdir("assets/images")
        for i in files:
            if i[-4:] == ".jpg":
                try:
                    self.tile_images[int(i[:-4])] = pygame.image.load("assets/images/" + i).convert(32)
                except:
                    self.other_images[i[:-4]] = pygame.image.load("assets/images/" + i).convert(32)


    def update_control(self, control, state):
        if control.time_to_ready > 0:
            control.state = state
            return
        if control.state == False and state == True:
            print control.action
            control.action.go('down', self)
        elif control.state == True and state == False:
            control.action.go('up', self)
        elif state == True:
            control.action.go('held', self)
        control.time_to_ready  = getattr(control.action, 'cooldown', 0)
        control.state = state

class Game(App):
    def __init__(self):
        App.__init__(self)
        for binding in self.bindings.items('bindings'):
            #Add a Control object with Control.action = actionname, to the dictionary of bound controls
            self.controls[getattr(pygame, binding[0])] = Control(getattr(actions, binding[1])())

    def main(self):
        while self.running:
            #print("WOOT SDFHJSDGJHDFJKAHGHJASFCD VASFCV DGB")
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.running = False

            draw_world(self, (45, 45, 640, 480), crop=True)
            pygame.display.flip()
            self.do_input()
            self.translate()
            self.timer()
            self.collide()

        pygame.quit()

    def do_input(self):
        keypresses = pygame.key.get_pressed()
        for key, control in self.controls.iteritems():
            self.update_control(control, keypresses[key])
            ###TODO
            #control.update(keypresses[key], world=world, player=player, config=config)

    def translate(self):
        self.player.update()
        #Move everything
        #dicks
        pass

    def collide(self):
        #Check projectiles for collisions
        pass

    def timer(self):
        #Check timed objects against the global timer
        global last_time
        print str(1.0 / (time.clock() - last_time)) + " FPS"
        last_time = time.clock()

    def render(self):
        #Render the scene
        xtiles = self.windowx / self.tilewidth
        ytiles = self.windowy / self.tilewidth
        for x in range(xtiles + 1):
            for y in range(ytiles + 1):
                tile = self.world.get(int(floor(self.player.x + x - xtiles/2)), int(floor(self.player.y + y - ytiles/2)))
                self.screen.blit(self.tile_images[tile.type], ((x - player.x % 1)*tilewidth, (y - player.y % 1)*tilewidth))
        pygame.display.flip()


'''
window = etc.Window()
'''

if __name__ == "__main__":
    game = Game()
    game.main()