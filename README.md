# NAME
Streamutils
A simple, lightweight and extensible program to overlay a YouTube livestream's chat.

# SYNOPSYS
python ttsfront.py *URL*
  -C CONFIG PATH
  --log-level [*LOG LEVEL*]

NOTE: CONFIG PATH is required!

# DESCRIPTION
This program creates a window, the window is a window with a single QTextEdit containing
messages from a YouTube livechat.  The QTextEdit isn't used for editing, it's just the easiest
way for me to throw text on the screen.

The window can be configured as an overlay, removing borders, decorations and scrollbars,
and disasbling interactivity.

The program can load plugins from a directory specified in the configuration file.
Each plugin has a single python file to contain it's code and a corresponding JSON file with the same name
*(only diffrent extension)* for it's configuration.  The plugin's "name" is the name of the python file without
the extension.

The application supports multiple startup modes, including:
- *(so-called)* **"NONE" MODE**: Start the program with the video ID specified on the command line.
- **Linkui MODE**: Ignore the link on the command line and instead prompt the user to enter a video ID manually.
- **Autofetch MODE**: Start the program and attempt to automatically use the configured user's current livestream.

# SEE ALSO
- `python(1)` for allowing me to write this app
- The `pytchat` python library for making livechat fetching possible!
- The `pyqt5` python library for allowing me to create the overlay!

# AUTHORS
(C) 2025 Colton Wollinger.  All rights reserved.
