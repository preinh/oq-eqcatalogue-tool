#!/bin/bash
set -x
# sudo apt-get install git
# git clone https://github.com/gem/oq-eqcatalogue-tool.git
# bash install-ubuntu.sh precise|quantal|raring
sudo apt-get install -y python-pip python-scipy python-shapely
sudo apt-get install -y python-mock python-coverage python-nose
sudo apt-get install -y python-pysqlite2 python-sqlalchemy
sudo apt-get install -y python-twill python-matplotlib
sudo pip install geoalchemy
# directories created before the installation to avoid permission
# issues: the buggy installer create a .qgis2 directory as root
mkdir $HOME/.qgis2
mkdir $HOME/.qgis2/python
mkdir $HOME/.qgis2/python/plugins
ln -s $HOME/oq-eqcatalogue-tool/openquake/qgis/gemcatalogue $HOME/.qgis2/python/plugins/gemcatalogue
sudo sed -i "$ a\deb     http://qgis.org/debian-nightly `lsb_release -cs` main\ndeb-src http://qgis.org/debian-nightly `lsb_release -cs` main\n" /etc/apt/sources.list
sudo gpg --keyserver keyserver.ubuntu.com --recv 997D3880
sudo gpg --export --armor 997D3880 | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y qgis

export PYTHONPATH=$HOME/oq-eqcatalogue-tool
./run_tests
