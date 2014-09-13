import sys
from pympler import tracker
tr = tracker.SummaryTracker()

class Quit:
    def go(self, key_event, **kwargs):
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

class Copy:
    def go(self, button_event, app, rect=None, z=None):
        copy_buffer = worlds[active_world].copy_selected(rect, z)
        worlds[-1] = copy_buffer

class SetTest:
    def go(self, button_event, app):
        if app.active_world and app.active_world.selection_end and button_event == "down":
            rect = app.active_world.selection_start + app.active_world.selection_end
            app.active_world.fill_rect(rect, 1, app.active_world.selection_z)