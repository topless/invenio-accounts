#!/bin/sh

# quit on errors:
set -o errexit

# quit on unbound symbols:
set -o nounset

DIR=`dirname "$0"`

cd $DIR
export FLASK_APP=app.py

mkdir $DIR/instance

# Build assets
flask collect -v
flask webpack buildall

# Create the database
flask db init
flask db create
