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
                        if "horizontal" is split of (item i of (item n of myTermWindow)) then
                            set split_str to "D"
                        else if "vertical" is split of (item i of (item n of myTermWindow)) then
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
    """Returns the AppleScript snippet to create an iTerm 2 pane.
    
    Keyword arguments:
    cmds -- the list of bash commands to execute at the start of the shell. (default None)
    name -- the name of the pane. (default "Default")
    split -- the format of the next split pane: "horizontal" for horizontal, "vertical" for vertical. (default None)
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


def get_apple_script(config):
    """Returns the AppleScript script to configure iTerm 2.

    Keyword arguments:
    config -- ConfigParser instance to transform into AppleScript.
    """
    body = Template(code_template)
    panes_str = ''

    # For each section of the config file, construct an AppleScript
    # command.
    for section in config.sections():
        name = section
        cmds = None
        split = None

        if config.has_option(section, 'cmds'):
            cmds = config.get(section, 'cmds')
            cmds = [cmd for cmd in cmds.split('\n') if cmd]

        if config.has_option(section, 'split'):
            split = config.get(section, 'split')

        panes_str += get_pane_snippet(cmds, name, split)

    # Inject the AppleScript command in the code template
    body = body.substitute(items=panes_str)
    return body


def launch_apple_script(conf_file):
    """Launch the AppleScript script to configure iTerm 2.

    Keyword arguments:
    conf_file -- path of the configuration file.
    
    Example of a configuration file:
    
    [Projet]

    cmds =
        export DJANGO_SETTINGS_MODULE=example.settings.local
        source ~/Documents/Dev/example.com/venvs/bin/activate
        cd ~/Documents/Dev/example.com

    split = vertical

    [Remote]

    cmds =
        ssh dev.example.com
        cd ~/example.com/
        export DJANGO_SETTINGS_MODULE=example.settings.remote
        source ~/venvs/python2.7/bin/activate

    split = horizontal
    
    [Apache logs]

    cmds =
        ssh dev.example.com
        tail -f /example.com/access.log

    """
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    body = get_apple_script(config)

    # Create temporary Apple script file and launch it.
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(body)
    temp.close()
    cmd = "osascript {0}".format(temp.name)
    subprocess.call(cmd, shell=True)
    os.unlink(temp.name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='?', help='name of the iTerm 2 config in ~/.panesrc directory (config=django will uses ~/.panesrc/djanog.conf)', default='default')
    args = parser.parse_args()

    config_path = os.path.expanduser('~/.panesrc/{}.conf'.format(args.config))

    if not os.path.exists(config_path):
        print("No config file at {0}".format(config_path))
        sys.exit(0)

    launch_apple_script(config_path)
