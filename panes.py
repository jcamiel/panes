#!/usr/bin/python2.7
import os
import sys
import subprocess
import tempfile
from string import Template
import ConfigParser
import ast
import argparse

# iTerm 2 AppleScript scripts adapted from 
# https://github.com/luismartingil/per.scripts/blob/master/iterm_launcher02.applescript
# Author: Luis Martin Gil
# Website: http://www.luismartingil.com/

code_template = '''
-- Applescript to launch iterm2 terminals/tabs with configurable:
-- ~ List of commands <cmds>
-- ~ Color <color>
-- ~ Name <name>
-- ~ Transparency <trans>
-- ~ Zoom out <zoomout>
-- ~ Split behavior horizontal(h) or vertical(v) <split> :: (h, v)
--
-- Run from terminal with `osascript` or just ./<<script>>
-- Dont unfocus with the mouse/keyboard while executing. the script.
-- Recomended to go full screen (CMD + Enter) if <zoomout> attributes used.
-- Change myTermWindow and myPane(s) as desired.
--
--
-- Author: Luis Martin Gil http://www.luismartingil.com
-- Year : 2013

tell application "iTerm"

    set myPane to {}
    $items

    set myTermWindow to {myPane}

    set myterm to (make new terminal)

    tell myterm
        repeat with n from 1 to count of myTermWindow
            launch session n
            repeat with i from 1 to count of (item n of myTermWindow)
                tell the last session
                    -- Lets set the properties of the actual tab
                    set name to name of (item i of (item n of myTermWindow))
                    -- set background color to color of (item i of (item n of myTermWindow))
                    -- set transparency to trans of (item i of (item n of myTermWindow))
                    -- Some commands might require more columns to be readable
                    repeat zoomout of (item i of (item n of myTermWindow)) times
                        tell i term application "System Events" to keystroke "-" using command down
                    end repeat
                    -- Lets execute the commands for the tab
                    repeat with cmd in cmds of (item i of (item n of myTermWindow))
                        write text cmd
                    end repeat
                    -- Split the pane in a "D" (vertical) or "d" (horizontal) way
                    if i is less than (count of (item n of myTermWindow)) then
                        if "h" is split of (item i of (item n of myTermWindow)) then
                            set split_str to "D"
                        else if "v" is split of (item i of (item n of myTermWindow)) then
                            set split_str to "d"
                        else
                            error
                            return
                        end if
                        tell i term application "System Events" to keystroke split_str using command down
                        delay 1
                    end if
                end tell
            end repeat
        end repeat
    end tell
end tell
'''


def get_pane_snippet(cmds=None, name="Default", split=None):
    """Returns the AppleScript snippet for creating an iTerm 2 pane.
    
    Keyword arguments:
    cmds -- the list of bash commands to execute at the start of the shell. (default None)
    name -- the name of the pane. (default "Default")
    split -- the format of the next split pane: "h" for horizontal, "v" for vertical. (default None)
    """
    # Compute the cmds string
    cmds_str = '","'.join(cmds)
    cmds_str = '{{"{0}"}}'.format(cmds_str)

    pane_snippet = '''
    set myPane to myPane & {{color:"black", cmds:$cmds, name:"$name", trans:"1.0", zoomout:0, split:"$split"}}
    '''
    pane = Template(pane_snippet)
    pane = pane.substitute(name=name, cmds=cmds_str, split=split)
    return pane


def get_apple_script(panes_cfg):
    """Returns the AppleScript script to configure iTerm 2.""" 
    body = Template(code_template)
    items_list = [get_pane_snippet(name=pane.get("name", "Default"),
                                   cmds=pane.get("cmds", ['pwd']),
                                   split=pane.get("split", "v"))
                  for pane in panes_cfg]
    items = "".join(items_list)
    body = body.substitute(items=items)
    return body


def launch_apple_script(panes_cfg):
    """Launch the AppleScript script to configure iTerm 2."""
    body = get_apple_script(panes_cfg)

    # Create temporary Apple script file and launch it.
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(body)
    temp.close()
    cmd = "osascript {0}".format(temp.name)
    subprocess.call(cmd, shell=True)
    os.unlink(temp.name)


default_config = """
[Default]

panes: [
    {
    "name": "Pane 1",
    "split": "v",
    "cmds": [
        "echo pane 1",
        "ls -ltr",
        ],
    },
    {
    "name": "Tab 2",
    "split": "h",
    "cmds": [
        "echo pane 2",
        "ls -ltr",
        ],
    },
    {
    "name": "Pane 3",
    "split": "h",
    "cmds": [
        "echo pane 3",
        "ls -ltr",
        ],
    },
    ]
"""
def create_default_config_file():
    file = os.path.expanduser('~/.panes')
    try:
        with open(file) as f:
            print("A config file for panes.py already exist in {0}.".format(file))
            print("Delete it before running panes.py -c again to recreate the default ones.")
    except IOError:
        with open(file, 'w') as f:
            f.write(default_config)
 
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='?', help='name of the iTerm 2 config in ~/.panes file', default="Default")
    parser.add_argument('-c', '--create', help='create a default config file in ~/.panes.',
                    action='store_true')
    args = parser.parse_args()

    if args.create:
        create_default_config_file()
    else:
        config_path = os.path.expanduser('~/.panes')

        if not os.path.exists(config_path):
            print("No config file at {0}".format(config_path))
            print("You can create a defaut one by running panes.py -c")
            sys.exit(0)
            
        # Try to parse config file at ~/.panes
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        try:
            panes_section = config.get(args.config, 'panes')
            panes_cfg = ast.literal_eval(panes_section )
            launch_apple_script(panes_cfg)
        except ConfigParser.NoOptionError:
            print("No panes defined in config {0}".format(args.config))
            pass
        except ConfigParser.NoSectionError:
            print("No config named {0} in ~/.panes".format(args.config))
            print("Possible configs are: {0}".format(", ".join(config.sections())))
            pass



