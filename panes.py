#!/usr/bin/env python
import os
import sys
import subprocess
import tempfile
import ConfigParser
import argparse

# A refactoring of Manbolo's panes.py
# This configures iTerm2 from a simple configuration file (see example at bottom).

code_template = '''
tell application "iTerm2"
	set myterm to (create window with default profile)
    %s
end tell
return
'''


def get_pane_snippet(index, cmds, name, split):
    txt = '''
        tell item %d of sessions of current tab of myterm
            select
        end tell
        tell current session of myterm
        ''' % index

    txt += 'set name to "%s"\n' % name

    for cmd in cmds:
        txt += 'write text "%s"\n' % cmd

    if split:
        txt += '''split %s with default profile
    ''' % ("vertically" if split.startswith('v') else "horizontally")

    txt += 'end tell\n'

    return txt


def get_apple_script(config):
    index = 0
    panes_str = ''
    # Construct the Applescript for each section of the config file.
    for section in config.sections():
        index += 1
        name = section
        cmds = []
        split = None

        if config.has_option(section, 'cmds'):
            cmds = config.get(section, 'cmds')
            cmds = [cmd for cmd in cmds.split('\n') if cmd]

        if config.has_option(section, 'split'):
            split = config.get(section, 'split')

        panes_str += get_pane_snippet(index, cmds, name, split)

    # Inject the AppleScript command in the code template
    return code_template % panes_str


def launch_apple_script(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    body = get_apple_script(config)

    # Create temporary Apple script file and launch it.
    print body
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(body)
    temp.close()
    cmd = "osascript {0}".format(temp.name)
    subprocess.call(cmd, shell=True)
    os.unlink(temp.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config', nargs='?', help='name of the iTerm 2 config in ~/.panesrc directory (e.g. config=django will uses ~/.panesrc/djanog.conf)', default='default')
    args = parser.parse_args()

    config_path = os.path.expanduser('~/.panesrc/{}.conf'.format(args.config))

    if not os.path.exists(config_path):
        print("No config file at {0}".format(config_path))
        sys.exit(0)

    launch_apple_script(config_path)


if __name__ == '__main__':
    main()

"""
    Example of a configuration file:

    [Project]

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
