#
# Performs a REST call to controller (possibly localhost) of latest farm status.
#


import datetime
import http
import json
import os
import requests
import socket
import sqlite3
import traceback

from flask import g

from common.config import globals
from api.commands import plotman_cli
from api import app
from api import utils

def update():
    with app.app_context():
        try:
            hostname = utils.get_hostname()
            gc = globals.load()
            plotting_status = "disabled"
            if gc['plotting_enabled']:
                if plotman_cli.get_plotman_pid():
                    plotting_status = "running"
                else:
                    plotting_status = "stopped"
            payload = {
                "hostname": hostname,
                "mode": os.environ['mode'],
                "plotting": plotting_status,
                "url": utils.get_remote_url(),
                "config": json.dumps(gc),
            }
            utils.send_post('/workers', payload, debug=False)
        except:
            app.logger.info("Failed to load and send worker status.")
            app.logger.info(traceback.format_exc())