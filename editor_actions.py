import sys

class Quit:
    def go(self, key_event, **kwargs):
        sys.exit()

class Activate:
    def go(self, mouse_event, button_num=None, screenregions=None, mpos=None, **kwargs):
        #Ascertain which region we have clicked within
        event_string = 'MBUTTON_' + str(button_num)
        for region in screenregions:
            if event_string in region.events:
                if region.location[0] < mpos[0] < (region.location[0] + region.size[0]) and\
                region.location[1] < mpos[1] < (region.location[1] + region.size[1]):
                    region.doEvent(event_string, [mouse_event])
