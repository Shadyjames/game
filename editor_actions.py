import sys
from pympler import tracker
tr = tracker.SummaryTracker()

class Quit:
    def go(self, key_event, **kwargs):
        sys.exit()

#Its unnecessary to do this location detection shit every time we do a pan
#It would be much more efficient to have a different action, that simply determins
#which world to pan, if any, via whether we're greater or less than a 0.7 * xpixels, or whatever
class LeftActivate:
    def go(self, button_event, screenregions=None, mpos=None, **kwargs):
        event = "MBUTTON_1"
        #Ascertain which region we have clicked within
        for region in screenregions:
            if event in region.events:
                if region.rect[0] < mpos[0] < (region.rect[0] + region.rect[2]) and\
                region.rect[1] < mpos[1] < (region.rect[1] + region.rect[3]):
                    region.doEvent(event, button_event=button_event, mpos=mpos)

class RightActivate:
    def go(self, button_event, screenregions=None, mpos=None, **kwargs):
        #Fuck you pygame
        event = "MBUTTON_3"
        #Ascertain which region we have clicked within
        for region in screenregions:
            if event in region.events:
                if region.rect[0] < mpos[0] < (region.rect[0] + region.rect[2]) and\
                region.rect[1] < mpos[1] < (region.rect[1] + region.rect[3]):
                    region.doEvent(event, button_event=button_event, mpos=mpos)

class MemorySummary:
    def go(self, key_event, **kwargs):
        tr.print_diff()

class Copy:
    def go(self, key_event, **kwargs):
        print "Dicks!"