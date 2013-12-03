panes
=====

Configure [iTerm 2][] panes on OSX ([more information here][]).

```bash
usage: panes.py [-h] [-c] [config]

positional arguments:
  config        name of the iTerm 2 config in ~/.panesrc file

optional arguments:
  -h, --help    show this help message and exit
  -c, --create  create a default config file in ~/.panesrc.
```
  
`panes.py` is a Python 2.7+ script to configure an [iTerm 2][] window.
`panes.py` reads a configuration file at ~/.panesrc and creates a new iTerm 2 window.

Based on the configuration file, `panes.py` creates additional horizontal or vertical split panes inside this window and can launch additional commands at the startup of the shell pane.

The configuration file uses Microsoft Windows INI files format. Each configuration is described in the only file ~/.panesrc and each configuration is a section in this file.
 
For instance, the default config file is:

```
[default]

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
    "name": "Pane 2",
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
```

To launch this config, simply type `panes.py default`or `panes.py`. This will create a new iTerm 2 window with three panes labeled 'Pane 1', 'Pane 2' and 'Pane 3'. Each pane will launch an `echo` command followed by a `ls -ltr` command. For instance, you can use it to ssh to your server and output some logs in a pane.

You can add another configuration by adding a section to `~/.panesrc`:

```
[default]

...

[prod]

panes: [
    {
    "name": "Pane 1",
    "split": "v",
    "cmds": [
        "ssh prod.example.com",
        "tail -f /var/log/example.log",
        ],
    }
    ]
    
[preprod]

...

```

And launch your prod environment like this: `panes.py prod`.


`panes.py` works by creating a temporary AppleScript script to pilot [iTerm 2][]. This script is totally based on [Luis Martin Gil][] [iTerm 2][] scripts that you can have at <https://github.com/luismartingil/per.scripts/blob/master/iterm_launcher02.applescript>. Kudos to Luis for mastering AppleScript which I have not the courage to do!

## Contact

Feedback are welcomed at contact@manbolo.com.

[iTerm 2]: http://www.iterm2.com/
[Luis Martin Gil]: http://www.luismartingil.com/
[more information here]: http://blog.manbolo.com/2013/11/29/configuring-iterm-2-with-python
