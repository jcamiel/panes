panes
=====

Configure [iTerm 2][] panes on OSX ([more information here][]).

```bash
usage: panes.py [-h] [-c] [config]

positional arguments:
  config        name of the iTerm 2 config in ~/.panesrc directory (config=django will use ~/.panesrc/django.conf)

optional arguments:
  -h, --help    show this help message and exit
```
  
`panes.py` is a Python 2.7+ script to configure an [iTerm 2][] window.
`panes.py` reads a configuration file inside ~/.panesrc directory and creates a new iTerm 2 window. Configuration file can be organized \` à la \` Apache: if you want to open the config named django, `panes.py` will look for ~/.panesrc/django.conf.

Based on the configuration file, `panes.py` creates additional horizontal or vertical split panes inside this window and can launch additional commands at the startup of the shell pane.

The configuration file uses a MySQL-like configuration file. Each configuration is described in its own file inside the ~/.panesrc directory.
 
For instance, a default config file is:

```
[Pane 1]

# cmds can be multi-line and commented.
# For each shell command, prefer single quote instead of double quote (will be corrected soon)/
cmds = 
	echo 'pane 1'
	ls -ltr
	
split = vertical

[Pane 2]

cmds = 
	echo 'pane 2'
	ls -ltr
	
split = horizontal

[Pane 3]

cmds = 
	echo 'pane 3'
	ls -ltr
	
split = horizontal


```

To launch this config, simply type `panes.py default` or `panes.py`. This will create a new iTerm 2 window with three panes labeled 'Pane 1', 'Pane 2' and 'Pane 3'. Each pane will launch an `echo` command followed by a `ls -ltr` command. For instance, you can use it to ssh to your server and output some logs in a pane.

![iTerm 2 example](https://raw.github.com/manbolo/panes/master/panes.png)

You can add another configuration by adding a new file inside `~/.panesrc`, for instance prod.conf:

```
[Pane 1]

cmds = 
	ssh prod.example.com
	tail -f /var/log/example.log

```

And launch your prod environment like this: `panes.py prod`.


`panes.py` works by creating a temporary AppleScript script to pilot [iTerm 2][]. This script is totally based on [Luis Martin Gil][] [iTerm 2][] scripts that you can have at <https://github.com/luismartingil/per.scripts/blob/master/iterm_launcher02.applescript>. Kudos to Luis for mastering AppleScript which I have not the courage to do!

## Contact

Feedback are welcomed at contact@manbolo.com.

[iTerm 2]: http://www.iterm2.com/
[Luis Martin Gil]: http://www.luismartingil.com/
[more information here]: http://blog.manbolo.com/2013/11/29/configuring-iterm-2-with-python
