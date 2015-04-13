#!/usr/bin/env bash
# from inside the uck console
#
# to enable auto-completion type:
# . /etc/bash_completion
#
apt-get update
apt-get purge -y abiword*  # none
apt-get purge -y gnumeric*  # none
apt-get purge -y firefox*  # midori
apt-get purge -y parole  # mplayer2
apt-get purge -y gmusicbrowser  # quodlibet
apt-get purge -y mousepad  # medit
apt-get purge -y gnome-mines   # because ...
apt-get purge -y gnome-sudoku  # because ...

apt-get autoremove -y

# editors
apt-get install -y ne medit editra

# ftp client
apt-get install -y foff  # ftp client
apt-get install -y midori  # browser

# media
apt-get install -y quodlibet mplayer2

# python dev libraries
apt-get install -y build-essential python-dev python-pip
apt-get install -y libssl-dev libxml2-dev libxslt1-dev libssl-dev libffi-dev libpcre3-dev

# dev tools
apt-get install -y ipython bpython
# regex tester
apt-get install -y kiki
# vcs
apt-get install -y git-core git-cola

# for gamers
apt-get install -y python-pygame
apt-get install -y renpy ardentryst
apt-get install -y pcsxr mupen64plus desmume


pip install virtualenvwrapper==4.3.2
pip install numpy==1.8.2
pip install PyOpenGL-accelerate==3.1

dpkg-divert --local --add /etc/init.d/systemd-logind
ln -s /bin/true /etc/init.d/systemd-logind

apt-get upgrade -y

# in case of error:
# see https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1325142
