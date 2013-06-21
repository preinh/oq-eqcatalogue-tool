#!/bin/bash
# sudo apt-get install git
# git clone https://github.com/gem/oq-eqcatalogue-tool.git
# bash install-ubuntu.sh precise|quantal|raring
sudo apt-get install python-pip python-scipy python-shapely
sudo apt-get install python-mock python-coverage python-nose
sudo apt-get install python-pysqlite2 python-sqlalchemy
sudo apt-get install python-twill matplotlib
sudo pip install geoalchemy

sudo echo "\ndeb     http://qgis.org/debian-nightly $1 main\ndeb-src http://qgis.org/debian-nightly $1 main\n" > /etc/apt/sources.list
sudo gpg --keyserver keyserver.ubuntu.com --recv 997D3880
sudo gpg --export --armor 997D3880 | sudo apt-key add -
sudo apt-get install qgis
mkdir $HOME/.qgis2
mkdir $HOME/.qgis2/python
mkdir $HOME/.qgis2/python/plugins
ln -s $HOME/oq-eqcatalogue-tool/openquake/qgis/gemcatalogue $HOME/.qgis2/python/plugins/gemcatalogue
export PYTHONPATH=$HOME/oq-eqcatalogue-tool
./run_tests
