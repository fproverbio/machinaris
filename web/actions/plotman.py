#
# CLI interactions with the plotman script.
#

import datetime
import os
import psutil
import re
import signal
import shutil
import time
import traceback
import yaml

from flask import Flask, jsonify, abort, request, flash
from subprocess import Popen, TimeoutExpired, PIPE
from common.models import plottings as pl
from web import app, db, utils
from web.models.plotman import PlottingSummary

PLOTMAN_SCRIPT = '/chia-blockchain/venv/bin/plotman'

# Don't query plotman unless at least this long since last time.
RELOAD_MINIMUM_SECS = 30

def load_plotting_summary():
    plottings = db.session.query(pl.Plotting).all()
    return PlottingSummary(plottings)

def start_plotman():
    global last_plotting_summary
    app.logger.info("Starting Plotman run....")
    try:
        logfile = "/root/.chia/plotman/logs/plotman.log"
        log_fd = os.open(logfile, os.O_RDWR | os.O_CREAT)
        log_fo = os.fdopen(log_fd, "a+")
        proc = Popen("{0} {1} </dev/tty".format(PLOTMAN_SCRIPT, 'plot'),
                     shell=True, universal_newlines=True, stdout=log_fo, stderr=log_fo)
    except:
        app.logger.info(traceback.format_exc())
        flash('Failed to start Plotman plotting run!', 'danger')
        flash('Please see: {0}'.format(logfile), 'warning')
    else:
        last_plotting_summary = None  # Force a refresh on next load
        flash('Plotman started successfully.', 'success')
        # Wait for Plotman to start a plot running for display in table
        time.sleep(5)

def action_plots(form):
    global last_plotting_summary
    app.logger.info("Actioning plots....")
    action = form.get('action')
    plot_ids = form.getlist('plot_id')
    app.logger.info("About to {0} plots: {1}".format(action, plot_ids))
    for plot_id in plot_ids:
        try:
            prefix = ""
            if action == "kill":
                prefix = "printf 'y\n' |"
            logfile = "/root/.chia/plotman/logs/plotman.log"
            log_fd = os.open(logfile, os.O_RDWR | os.O_CREAT)
            log_fo = os.fdopen(log_fd, "a+")
            proc = Popen("{0} {1} {2} {3}".format(prefix, PLOTMAN_SCRIPT, action, plot_id),
                         shell=True, universal_newlines=True, stdout=log_fo, stderr=log_fo)
        except:
            app.logger.info(traceback.format_exc())
            flash('Failed to {0} selected plot {1}.'.format(
                action, plot_id), 'danger')
            flash('Please see: {0}'.format(logfile), 'warning')
            return
    last_plotting_summary = None  # Force a refresh on next load
    flash('Plotman was able to {0} the selected plots successfully.'.format(
        action), 'success')
    time.sleep(5)  # Wait for Plotman to complete its actions

def get_plotman_pid():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'plotman' and 'plot' in proc.info['cmdline']:
            return proc.info['pid']
    return None

def stop_plotman():
    global last_plotting_summary
    app.logger.info("Stopping Plotman run....")
    try:
        os.kill(get_plotman_pid(), signal.SIGTERM)
    except:
        app.logger.info(traceback.format_exc())
        flash('Failed to stop Plotman plotting run!', 'danger')
        flash('Please see /root/.chia/plotman/logs/plotman.log', 'warning')
    else:
        last_plotting_summary = None  # Force a refresh on next load
        flash('Plotman stopped successfully.  No new plots will be started, but existing ones will continue on.', 'success')

def load_config(plotter):
    return utils.send_get(plotter, "/configs/{0}/plotting".format(plotter.hostname), debug=False).content

def save_config(plotter, config):
    try: # Validate the YAML first
        yaml.safe_load(config)
    except Exception as ex:
        app.logger.info(traceback.format_exc())
        flash('Updated plotman.yaml failed validation! Fix and save or refresh page.', 'danger')
        flash(str(ex), 'warning')
    try:
        utils.send_put(plotter, "/configs/{0}/plotting".format(plotter.hostname), config, debug=True)
    except Exception as ex:
        flash('Failed to save config to plotter.  Please check log files.', 'danger')
        flash(str(ex), 'warning')
    else:
        flash('Nice! Plotman\'s plotman.yaml validated and saved successfully.', 'success')

def find_plotting_job_log(plot_id):
    dir_path = '/root/.chia/plotman/logs'
    directory = os.fsencode(dir_path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".log") and not filename.startswith('plotman.'): 
            with open(os.path.join(str(dir_path), filename)) as logfile:
                head = [next(logfile) for x in range(10)] # Check first 10 lines
                for line in head:
                    if plot_id in line:
                        return os.path.join(str(dir_path), filename)
            continue
        else:
            continue
    return None

def analyze(plot_file):
    groups = re.match("plot-k(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\w+).plot", plot_file)
    if not groups:
        return "Invalid plot file name provided: {0}".format(plot_file)
    plot_log_file = find_plotting_job_log(groups[7])
    if plot_log_file:
        proc = Popen("{0} {1} {2} < /dev/tty".format(
            PLOTMAN_SCRIPT,'analyze', plot_log_file), stdout=PIPE, stderr=PIPE, shell=True)
        try:
            outs, errs = proc.communicate(timeout=90)
        except TimeoutExpired:
            proc.kill()
            proc.communicate()
            abort(500, description="The timeout is expired!")
        if errs:
            app.logger.error(errs.decode('utf-8'))
            return "Failed to analyze plot log.  See machinaris/logs/webui.log for details."
        return outs.decode('utf-8')
    return "Sorry, not plotting job log found.  Perhaps plot was made elsewhere?"