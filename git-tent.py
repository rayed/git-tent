#!/usr/bin/env python


GIT_TENT_HOME= "/home/git/git-tent/"
AUTHORIZED_KEYS="/home/git/.ssh/authorized_keys"

SHELL=GIT_TENT_HOME+"/git-tent.py"
CONFIG_FILE=GIT_TENT_HOME+"/config.yaml"
REPOS_DIR=GIT_TENT_HOME+"/repos"
LOG_FILE=GIT_TENT_HOME+"/git-tent.log"


import os
import re
import sys
import yaml
import logging
import subprocess
from pprint import pprint

logger = logging.getLogger(__name__)
if os.isatty(sys.stdout.fileno()):
    handler = logging.StreamHandler()
else:
    handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def read_config():
    f = open(CONFIG_FILE)
    config = yaml.load(f)
    f.close()
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
    f = open(AUTHORIZED_KEYS, "w")
    for user in config['users']:
        logger.info("Adding [%s] keys " % (user['name']))
        for key in user['keys']:
            f.write('command="%s shell %s" %s\n' % (SHELL, user['name'], key))
    f.close()
    os.chmod(AUTHORIZED_KEYS, 0644)
    # Build missing repos
    for repo in config['repos']:
        repo_name = repo['name'] + ".git"
        repo_dir = os.path.join(REPOS_DIR, repo_name)
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
    regex = r"(git-upload-archive|git-upload-pack|git-receive-pack) '([\w-]+)\.git'"
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
    repo_dir = os.path.join(REPOS_DIR, repo_name)
    if not os.path.isdir(repo_dir):
        raise ShellException("Repo doesn't exist")
    #  run
    os.execl('/usr/bin/'+ command, command, repo_dir)


def main():
    config = read_config()
    if len(sys.argv) == 3 and sys.argv[1] == 'shell': 
        user = sys.argv[2]
        try:
            shell(config, user)
        except ShellException, e:
            report_error(e)
    elif len(sys.argv) == 2 and sys.argv[1] == 'setup':
        logger.info("Setup")
        setup(config)
    elif len(sys.argv) == 2 and sys.argv[1] == 'sample_config':
        logger.setLevel(logging.ERROR)
        sample_config()
    else:
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


