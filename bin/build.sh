#!/bin/bash

#install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# install python using brew
brew install python

# Make virtual environment
python3 -m venv wts-venv
source wts-venv/bin/activate

# Install necessary modules
python3 -m pip install flask pandas pyinstaller

# Get app.py
curl -fsSL https://raw.githubusercontent.com/dostarora97/wts/main/app.py > ./app.py

# Build app executable
pyinstaller --onefile app.py

# Make sure port is closed
sudo lsof -ti:8000 | xargs sudo kill -9

echo "Executable created in some-path(todo)"
