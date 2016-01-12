# Git-Tent

Git-Tent is an application that allows you to host your own git server on your own machine. 

## Requirement 

Any unix machine (Linux, OSX, FreeBSD) with Python installed.

## Installation

	# Install required package (Python YAML module)
	sudo pip install pyyaml
    # ... on CentOS you can install from YUM
    sudo yum install PyYAML

	# add user named "git"
	sudo adduser git

	# create directory for "git-tent"
	sudo -u git mkdir ~git/git-tent

	# copy "git-tent.py" and change owner and permision
	sudo cp git-tent.py ~git/git-tent
	sudo chown git:git ~git/git-tent/git-tent.py
	sudo chmod +x ~git/git-tent/git-tent.py

	# Create sample config
	sudo -u git ~git/git-tent/git-tent.py sample_config > ~git/git-tent/config.yaml
	
If 	the home directory for "git" user is different from "/home/git" open "git-tent.py" and edit "GIT_TENT_HOME" and "AUTHORIZED_KEYS" variables.

## Configuration

git-tent is configured using a single YAML file "config.yaml", the file have the following structure:

	---

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


Edit the name of the reposirtoes you want to create, and add your PUBLIC keys (and other team members keys too).

After editing the file you need to run:

	sudo -u git ~git/git-tent/git-tent.py setup
	
This will create two reposirtory "project1" and "project2", which can be accessed from any other machine.


# Accessing the Repo

Create a new repository on the command line:

		echo "# test" >> README.md
		git init
		git add README.md
		git commit -m "first commit"
		git remote add origin git@your_server:project1.git
		git push -u origin master

OR push an existing repository from the command line:

		git remote add origin git@your_server:project1.git
		git push -u origin master


# TODO 

1. Add two levels of access, read-only, and read-write.
2. Add groups


# Hints

You can access your public keys in github from the following URL (replace user with your account): <https://github.com/user.keys>
