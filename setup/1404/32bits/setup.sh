#!/usr/bin/env bash
# from inside the uck console
#
# to enable auto-completion type:
# . /etc/bash_completion
# 
apt-get update
apt-get purge -y abiword* \  # none
gnumeric* \  # none
firefox* \  # midori
parole \  # mplayer2
gmusicbrowser \  # quodlibet
mousepad  \ # medit
gnome-mines  \  # because ...
gnome-sudoku  \ # because ...

# editors
apt-get install -y ne medit editra

# ftp client
apt-get install -y foff \  # ftp client
midori  # browser

# media
apt-get install -y quodlibet mplayer2

# for gamers
apt-get install -y python-pygame

# python dev libraries
apt-get install -y build-essential python-dev python-pip
apt-get install -y libssl-dev libxml2-dev libxslt1-dev libssl-dev libffi-dev libpcre3-dev

# dev tools
apt-get install -y ipython bpython \
kiki \  # regex tester
git-core  \  # vcs
git-cola  \  # git manager

pip install virtualenvwrapper==4.3.2
pip install numpy==1.8.2
pip install PyOpenGL-accelerate==3.1

apt-get autoremove
apt-get upgrade

# in case of error:
# see https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1325142