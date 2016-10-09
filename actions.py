import sys
import pygame
from math import floor
from pympler import tracker
tr = tracker.SummaryTracker()

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
    def go(self, key_event, app):
        player = app.player
        if key_event == 'down':
            player.movestates[3] = 1
            player.movestates[2] = 0
        elif key_event == 'up':
            player.movestates[3] = 0
        elif key_event == 'held' and player.movestates[2] == 0:
            player.movestates[3] = 1
class Player_MoveUp:
    cooldown = 0
    def go(self, key_event, app):
        player = app.player
        if key_event == 'down':
            player.movestates[2] = 1
            player.movestates[3] = 0
        elif key_event == 'up':
            player.movestates[2] = 0
        elif key_event == 'held' and player.movestates[3] == 0:
            player.movestates[2] = 1
class Player_MoveRight:
    cooldown = 0
    def go(self, key_event, app):
        player = app.player
        if key_event == 'down':
            player.movestates[1] = 1
            player.movestates[0] = 0
        elif key_event == 'up':
            player.movestates[1] = 0
        elif key_event == 'held' and player.movestates[0] == 0:
            player.movestates[1] = 1
class Player_MoveLeft:
    cooldown = 0
    def go(self, key_event, app):
        player = app.player
        if key_event == 'down':
            player.movestates[0] = 1
            player.movestates[1] = 0
        elif key_event == 'up':
            player.movestates[0] = 0
        elif key_event == 'held' and player.movestates[1] == 0:
            player.movestates[0] = 1

class Quit:
    def go(self, key_event, app):
        print "Quit activated"
        app.running = False

class LeftActivate:
    def go(self, button_event, app):
        #Ascertain which region we have clicked within
        for region in reversed(app.screenregions):
            if region.rect[0] < app.mpos[0] < (region.rect[0] + region.rect[2])\
            and region.rect[1] < app.mpos[1] < (region.rect[1] + region.rect[3])\
            and region.clickable:
                region.signal(1, app.mpos, button_event)
                break

class RightActivate:
    def go(self, button_event, app):
        #Ascertain which region we have clicked within
        for region in reversed(app.screenregions):
            if region.rect[0] < app.mpos[0] < (region.rect[0] + region.rect[2])\
            and region.rect[1] < app.mpos[1] < (region.rect[1] + region.rect[3])\
            and region.clickable:
                #Fuck up pygame, RMB is not mouse3
                region.signal(3, app.mpos, button_event)
                break

class MemorySummary:
    def go(self, button_event, app):
        tr.print_diff()

class Copy:
    def go(self, button_event, app):
        app.copy_buffer = app.active_world.get_rect(app.active_world.selection_rect, 
                                                    app.active_world.selection_z,
                                                    debug=True)

class Paste:
    def go(self, button_event, app):
        app.active_world.set_rect(  [int(floor(value)) for value in app.active_world.selection_start], 
                                    app.copy_buffer, 
                                    app.active_world.selection_z)

class Fill:
    def go(self, button_event, app):
        if app.active_world and app.active_world.selection_end and button_event == "down":
            print app.active_world.selection_rect
            app.active_world.fill_rect( app.active_world.selection_rect, 
                                        app.selected_tile_type, 
                                        app.active_world.selection_z)
