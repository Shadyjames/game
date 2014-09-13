import sys
from pympler import tracker
tr = tracker.SummaryTracker()

class Quit:
    def go(self, key_event, app):
        sys.exit()

class LeftActivate:
    def go(self, button_event, app):
        #Ascertain which region we have clicked within
        for region in reversed(app.screenregions):
            if region.rect[0] < app.mpos[0] < (region.rect[0] + region.rect[2]) and\
            region.rect[1] < app.mpos[1] < (region.rect[1] + region.rect[3]):
                region.action1(app, button_event)
                break

class RightActivate:
    def go(self, button_event, app):
        #Ascertain which region we have clicked within
        for region in reversed(app.screenregions):
            if region.rect[0] < app.mpos[0] < (region.rect[0] + region.rect[2]) and\
            region.rect[1] < app.mpos[1] < (region.rect[1] + region.rect[3]):
                region.action2(app, button_event)
                break

class MemorySummary:
    def go(self, button_event, app):
        tr.print_diff()

###NOTE TO SELF:
#You can totally have separate Control dictionaries inside a dictionary keyed on the state of the modifier keys
#Ie make it that the tuple (0, 0, 0) represents the state of CTRL, ALT, and SHIFT respectively.
#{(0, 0, 0): <almost all the controls go here>,
# (1, 0, 0): <ctrl-based binds, ctrl+c and ctrl+v>,
# (1, 0, 1): <ctrl+shift-based binds, pretty much JUST ctrl+shift+tab if we ever do tabbing>}
class Copy:
    def go(self, button_event, app, rect=None, z=None):
        copy_buffer = worlds[active_world].copy_selected(rect, z)
        worlds[-1] = copy_buffer

class SetTest:
    def go(self, button_event, app):
        if app.active_world and app.active_world.selection_end and button_event == "down":
            #app.active_world.selection_* is TOO MANY LETTERS
            #Shortern to point a, point b
            a = app.active_world.selection_start
            b = app.active_world.selection_end
            rect = [a[0] if a[0] < b[0] else b[0], 
                    a[1] if a[1] < b[1] else b[1], 
                    abs(a[0] - b[0]) + 1,
                    abs(a[1] - b[1]) + 1]
            app.active_world.fill_rect(rect, 1, app.active_world.selection_z)