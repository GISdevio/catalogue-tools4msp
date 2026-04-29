#!/bin/bash

set -ex

VERSION="2.11.0"

uv add "setuptools<46" wheel Cython

uv add -r "https://raw.githubusercontent.com/ckan/ckanext-spatial/master/requirements.txt"
uv add -r "https://raw.githubusercontent.com/ckan/ckan/refs/tags/ckan-$VERSION/requirements.txt"
