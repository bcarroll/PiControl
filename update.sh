#!/bin/bash
# This script will pull the latest PiControl changes from Github and restart PiControl
./PiControl.sh stop
git pull
./PiControl.sh start
