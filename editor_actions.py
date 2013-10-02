import sys

class Quit:
    def go(self, key_event, **kwargs):
        sys.exit()

#Its unnecessary to do this location detection shit every time we do a pan
#It would be much more efficient to have a different action, that simply determins
#which world to pan, if any, via whether we're greater or less than a 0.7 * xpixels, or whatever
class Activate:
    def go(self, mouse_event, button_num=None, screenregions=None, mpos=None, **kwargs):
        #Ascertain which region we have clicked within
        event_string = 'MBUTTON_' + str(button_num)
        for region in screenregions:
            if event_string in region.events:
                if region.rect[0] < mpos[0] < (region.rect[0] + region.rect[2]) and\
                region.rect[1] < mpos[1] < (region.rect[1] + region.rect[3]):
                    region.doEvent(event_string, button_event=mouse_event, mpos=mpos)
