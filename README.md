# Git-Tent

Git-Tent is an application that allows you to host your own git server on your own machine. 

## Requirement 

Any unix machine (Linux, OSX, FreeBSD) with Python installed.

## Installation

    # Install required package (Python YAML module)
    # Choose one:
    sudo apt-get install python-yaml  # Ubuntu, Debian
    sudo yum install PyYAML           # CentOS, Fedora
    sudo pip install pyyaml           # Using Python PIP

    # add user named "git"
    sudo adduser git

    # Switch to the new user
    sudo su - git
    
    # Download and unpack package
    wget https://github.com/rayed/git-tent/archive/master.zip
    unzip master.zip
    mv git-tent-master git-tent
    cd git-tent
    ./git-tent.py sample_config > git-tent-config.yaml

The application will over write the "authorized\_keys" file, DON'T USE in with your normal account.

The applcaition default settings are:
 
    settings:
      user: git
      home: /home/git
      authorized_keys: /home/git/.ssh/authorized_keys
      shell_file: /home/git/git-tent/git-tent.py
      log_file: /home/git/git-tent/git-tent.log
      repos_dir: /home/git/git-tent/repos/

Copy and edit the previous section to your config as needed.


## Configuration

git-tent is configured using a single YAML file "git-tent-config.yaml", the file have the following structure:

    ---

    repos:

    - name: project1
        users:
        - rayed
        - mohammed

    - name: project2
        users: [rayed, khaled]

    users:

    - name: rayed
        keys:
        - "ssh-rsa AAAA....    rayed@host1"
        - "ssh-rsa AAAA....    rayed@host2"

    - name: mohammed
        keys:
        - "ssh-rsa AAAA....    mohammed@host1"
        - "ssh-rsa AAAA....    mohammed@host2"

    - name: khaled
        keys:
        - "ssh-rsa AAAA....    khaled@host1"
        - "ssh-rsa AAAA....    khaled@host2"


Edit the name of the reposirtoes you want to create, and add your PUBLIC keys (and other team members keys too).

After editing the file you need to run:

  ./git-tent.py setup
  
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

