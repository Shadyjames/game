import ConfigParser
import actions
import pygame

class Control:
    state = False
    time_to_ready = 0
    def __init__(self, action):
        self.action = action

#Pure bindings means one binding per key, no ctrl/alt/shift modifiers
def load_controls(heading, pure=False):
    bindings = ConfigParser.ConfigParser()
    bindings.optionxform = str
    bindings.read("bindings.cfg")
    
    controls = {}
    print bindings.items(heading)
    for key, binding in bindings.items(heading):
        #Add a Control object with Control.action = actionname, to the dictionary of bound controls
        #The flags, from left to right, represent ctrl, alt, shift
        control = Control(getattr(actions, binding)())
        if pure:
                if item.startswith('K_'):
                    key = getattr(pygame, item)
                elif item.startswith('MBUTTON_'):
                    #we treat mouse buttons as keys. Don't know why thats so much to ask.
                    key = int(item[-1]) + len(pygame.key.get_pressed()) - 1
                controls[key] = control
        else:
            mod_list = [False, False, False]
            if '+' in key:
                keys = key.split('+')
                mods = keys[:-1]
                key = keys[-1]
                mod_list[0] = 'CTRL' in mods
                mod_list[1] = 'ALT' in mods
                mod_list[2] = 'SHIFT' in mods
            
            mod_list = tuple(mod_list)
            #Convert the button string into its integer key
            if key.startswith('K_'):
                key = getattr(pygame, key)
            elif key.startswith('MBUTTON_'):
                #we treat mouse buttons as keys. Don't know why thats so much to ask.
                key = int(key[-1]) + len(pygame.key.get_pressed()) - 1

            if mod_list not in controls:
                controls[mod_list] = {}
            controls[mod_list][key] = control
    return controls
