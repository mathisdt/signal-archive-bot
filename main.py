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
        exception = None
        group_name = None
        try:
            logging.debug(f"received message with {len(attachments)} attachments: {message}")
            ts = datetime.datetime.fromtimestamp(timestamp // 1000, tz=zoneinfo.ZoneInfo("Europe/Berlin"))
            msg = ""
            if message is not None and len(message) > 0:
                msg = message if len(message) <= 15 else message[:15]
                msg = f"-{msg}"
            src = re.sub(r"^\+?49", "0", source)
            src = re.sub(r"[^a-zA-Z0-9]", "", src)
            group_name = signal.getGroupName(group_id)
            if group_name is not None and len(group_name) > 0:
                src = f"{re.sub(r'[^-_.,a-zA-ZäöüÄÖÜß0-9]', '_', group_name)}-{src}"
            src_name = signal.getContactName(source)
            if src_name is not None and len(src_name) > 0:
                src = f"{src}_{re.sub(r'[^-_.,a-zA-ZäöüÄÖÜß0-9]', '_', src_name)}"
            for att in attachments:
                filename = None
                try:
                    tmpfilename = os.path.basename(att)
                    filename = f"{target_dir}{os.path.sep}{ts.strftime('%Y%m%d-%H%M%S')}-{src}{msg}-{tmpfilename}"
                    shutil.copyfile(att, filename)
                    logging.debug(f"saved attachment to {filename}")
                except Exception as ex:
                    logging.error(f"error copying attachment {att}: {ex}")
                    ex.add_note(f"while copying attachment {att} to {filename}")
                    exception = ex
        except Exception as ex:
            logging.error(f"error: {ex}")
            exception = ex
        finally:
            if not exception:
                # green check mark
                signal.sendGroupMessageReaction("\u2705", False, source, timestamp, group_id)
                if "logging" in config and "success_number" in config["logging"]:
                    signal.sendMessage(
                        f"successfully archived a message from {group_name} with {len(attachments)} file(s)",
                        [], ["+" + config["logging"]["success_number"]])
            else:
                # red cross mark
                signal.sendGroupMessageReaction("\u274C", False, source, timestamp, group_id)
                if "logging" in config and "error_number" in config["logging"]:
                    signal.sendMessage(
                        f"could not archive a message from {group_name} with {len(attachments)} file(s): {exception}",
                        [], ["+" + config["logging"]["error_number"]])


target_dir = config["local"]["target_dir"]
if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
    raise Exception(f"configured target path {target_dir} is not a directory")
signal.onMessageReceived = check_and_possibly_archive_media
loop.run()
