#!/usr/bin/env python

"""
Git Tent
Easily manage your Git server with support of multiple users with different
access permissions

Rayed Alrashed 13 Jan 2016
"""

import os
import re
import sys
import yaml
import logging
import subprocess
from pprint import pprint

# Chdir to script own directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# setup logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

def setup_logging(config, console=True):
    logger.setLevel(logging.DEBUG)
    # if called interactively log to console
    if console and os.isatty(sys.stdout.fileno()):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    # set log handler for logfile
    if "log_file" in config:
        h = logging.FileHandler(config["log_file"])
        h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        h.setLevel(logging.DEBUG)
        logger.addHandler(h)

def read_config():
    if os.path.exists("git-tent-config.yaml"):
        config_file = "git-tent-config.yaml"
    elif os.path.exists("/etc/git-tent-config.yaml"):
        config_file = "/etc/git-tent-config.yaml"
    else:
        logger.error("No config file found!")
        sys.exit(1)
    try:
        with open(config_file) as f:
            config = yaml.load(f)
    except yaml.YAMLError, exc:
        logger.error("Couldn't parse config file:\n%s" % (exc))
        sys.exit(1)
    except:
        logger.exception("Couldn't parse config file")
        sys.exit(1)
    if config == None:
        config = {}
    config["settings"] = config.get("settings", {})
    _s = config["settings"]
    _s["user"] = _s.get("user", "git")
    _s["home"] = _s.get("home", "/home/" + _s["user"])
    _s["authorized_keys"] = _s.get("authorized_keys", _s["home"] + "/.ssh/authorized_keys")
    _s["shell_file"] = _s.get("shell_file", _s["home"] + "/git-tent/git-tent.py")
    _s["repos_dir"] = _s.get("repos_dir", _s["home"] + "/git-tent/repos/")
    _s["log_file"] = _s.get("log_file", _s["home"] + "/git-tent/git-tent.log")
    if _s["repos_dir"][-1] != "/":
        _s["repos_dir"] += "/"
    return config

def sample_config():
    print """---

repos:

- name: project1
  users:
  - rayed
  - mohammed

- name: project2
  users:
  - rayed
  - khaled

users:

- name: rayed
  keys:
  - "ssh-rsa AAAA....  rayed@host1"
  - "ssh-rsa AAAA....  rayed@host2"

- name: mohammed
  keys:
  - "ssh-rsa AAAA....  mohammed@host1"
  - "ssh-rsa AAAA....  mohammed@host2"

- name: khaled
  keys:
  - "ssh-rsa AAAA....  khaled@host1"
  - "ssh-rsa AAAA....  khaled@host2"

"""

def setup(config):
    # Build authorized_keys
    f = open(config["settings"]["authorized_keys"], "w")
    for user in config['users']:
        logger.info("Adding [%s] keys " % (user['name']))
        for key in user['keys']:
            f.write('command="%s shell %s" %s\n' %
                    (config["settings"]["shell_file"], user['name'], key))
    f.close()
    os.chmod(config["settings"]["authorized_keys"], 0644)
    # Build missing repos
    for repo in config['repos']:
        repo_name = repo['name'] + ".git"
        repo_dir = os.path.join(config["settings"]["repos_dir"], repo_name)
        if not os.path.isdir(repo_dir):
            subprocess.call(['git', 'init', '--bare', repo_dir])


class ShellException(Exception):
    def __init__(self, message=''):
        super(ShellException, self).__init__(message)

def report_error(message):
    logger.error(message)
    sys.stderr.write('ERROR: %s \n' % (message))
    sys.exit(1)


def shell(config, user):
    logger.info("Git shell with user [%s]" % (user))
    # command and repo are pased through SSH_ORIGINAL_COMMAND
    command = os.getenv('SSH_ORIGINAL_COMMAND', '')
    logger.debug('SSH_ORIGINAL_COMMAND:'+command)
    regex = r"(git-upload-archive|git-upload-pack|git-receive-pack) '([\/\w-]+)\.git'"
    m = re.match(regex, command)
    if not m:
        raise ShellException('Sorry account for Git only')
    else:
        command = m.group(1)
        repo_name = m.group(2)
    logger.debug("Git command: [%s] on repo [%s]" % (command, repo_name))
    # validate : check user and repo name are valid
    repo = None
    for row in config['repos']:
        if row['name'] == repo_name:
            repo = row
            break
    if not repo:
        raise ShellException("Repo doesn't exist")
    if user not in repo['users']:
        raise ShellException("Not authorized to access this repo")
    repo_name = repo_name + ".git"
    repo_dir = os.path.join(config["settings"]["repos_dir"], repo_name)
    if not os.path.isdir(repo_dir):
        raise ShellException("Repo doesn't exist")
    #  run
    os.execl('/usr/bin/'+ command, command, repo_dir)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == 'shell': 
        config = read_config()
        setup_logging(config, False)
        user = sys.argv[2]
        try:
            shell(config, user)
        except ShellException, e:
            report_error(e)
    elif len(sys.argv) == 2 and sys.argv[1] == 'setup':
        config = read_config()
        setup_logging(config)
        logger.info("Setup")
        setup(config)
    elif len(sys.argv) == 2 and sys.argv[1] == 'sample_config':
        setup_logging({}, False)
        logger.setLevel(logging.ERROR)
        sample_config()
    else:
        setup_logging({}, True)
        logger.error("Usage: %s (setup|sample_config)" % (sys.argv[0]))
        sys.exit(1)


if __name__=="__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        logger.exception('Exception happend')
        report_error('Unhandled exception')


