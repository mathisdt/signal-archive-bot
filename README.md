# Signal Archive Bot

This project makes use of [signal-cli](https://github.com/AsamK/signal-cli)
to create a service which automatically archives any media received through Signal groups
or which are sent directly to the bot.
This can come in handy if e.g. your family shares things in a Signal group and
you don't want to download everything by hand to archive it, or if you have certain media
files you want to keep permanently which you can simply forward to the bot.

### Get started

1. If you don't run [signal-cli as **system DBus service**](https://github.com/AsamK/signal-cli/wiki/DBus-service)
   yet, set it up now.
2. Checkout this project to your computer (or just copy `main.py` and `config-template.ini`).
3. Copy `config-template.ini` to `config.ini` and edit it so it contains
   the phone number and directory you want to use. The other settings can be configured
   optionally.
4. Make sure that at least Python 3.6 and the necessary libraries are installed
   (e.g. by executing `pip3 install -r requirements.txt`). You can also set up a
   [venv](https://docs.python.org/3/library/venv.html) and install the requirements
   inside it (recommended).
5. Run `main.py`, e.g. by creating a systemd service definition for it (preferably 
   with the same user account you use for running signal-cli so there won't be any
   file access problems).
   
   See the `doc` directory for an example script and service definition file.