#install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# install python using brew
brew install python

# Install git using homebrew
brew install git

# Make virtual environment
python3 -m venv wts-venv
source wts-venv/bin/activate

# Install necessary modules
python3 -m pip install flask pandas pyinstaller

# Build app executable
pyinstaller --onefile app.py

# Make sure port is closed
sudo lsof -ti:8000 | xargs sudo kill -9
