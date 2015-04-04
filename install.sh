#!/usr/bin/env bash

git update-index --assume-unchanged config.json

sudo apt-get install python-pip
sudo apt-get install python-dev libmysqlclient-dev
sudo apt-get install mysql-server

pip install -U pip
pip install PyMySQL
pip install MySQL-python

git clone https://github.com/a2design-company/hipster
cd hipster
python setup.py install

python set_up_db.py config.json
