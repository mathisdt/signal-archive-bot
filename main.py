#!/usr/bin/env python3

import configparser
import logging
import os.path
import shutil
import re
import datetime
import zoneinfo

from gi.repository import GLib
from pydbus import SystemBus

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

if not os.path.isfile("config.ini"):
    logging.error(
        "config.ini not found - maybe you didn't copy (and customize) the file config-template.ini to config.ini yet?")
    exit(1)

config = configparser.ConfigParser()
config.read("config.ini")
logging.debug("configuration read")

bus = SystemBus()
loop = GLib.MainLoop()

signal = bus.get('org.asamk.Signal', object_path=f'/org/asamk/Signal/_{config["signal"]["number"]}')


def check_and_possibly_archive_media(timestamp, source, group_id, message, attachments):
    if timestamp and group_id and attachments:
        errored = False
        try:
            logging.debug(f"received message with {len(attachments)} attachments: {message}")
            ts = datetime.datetime.fromtimestamp(timestamp // 1000, tz=zoneinfo.ZoneInfo("Europe/Berlin"))
            msg = ""
            if message is not None and len(message) > 0:
                msg = message if len(message) <= 15 else message[:15]
                msg = f"-{msg}"
            src = re.sub(r"^\+?49", "0", source)
            src = re.sub(r"[^a-zA-Z0-9]", "", src)
            for att in attachments:
                try:
                    tmpfilename = os.path.basename(att)
                    filename = f"{target_dir}{os.path.sep}{ts.strftime('%Y%m%d-%H%M%S')}-{src}{msg}-{tmpfilename}"
                    shutil.copy(att, filename)
                    logging.debug(f"saved attachment to {filename}")
                except Exception as ex:
                    logging.error(f"error copying attachment {att}: {ex}")
                    errored = True
        except Exception as ex:
            logging.error(f"error: {ex}")
            errored = True
        finally:
            if not errored:
                # green check mark
                signal.sendGroupMessageReaction("\u2705", False, source, timestamp, group_id)
            else:
                # red cross mark
                signal.sendGroupMessageReaction("\u274C", False, source, timestamp, group_id)


target_dir = config["local"]["target_dir"]
if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
    raise Exception(f"configured target path {target_dir} is not a directory")
signal.onMessageReceived = check_and_possibly_archive_media
loop.run()
