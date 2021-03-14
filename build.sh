#!/usr/bin/env bash

if [ -z "${VIRTUAL_ENV}" ]; then
  echo "Make sure you run this script from within the"
  echo "Python Virtual environment of this project"
  exit 1
fi

if [ "$1" == "clean" ]; then
  echo "Cleaning..."
  if [ -d "./dist" ]; then
    rm -rf "./dist" "./build" 2>/dev/null
  fi
  ./images.sh
fi
echo "Versioning..."
python ./version.py

echo "Building..."

echo "Building the app"
python -OO -m PyInstaller --osx-bundle-identifier nl.ivonet.aax2m4b --noconsole -y aax2m4b.spec

./tag.sh
