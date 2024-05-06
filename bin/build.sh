#!/bin/bash

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew is already installed."
fi

# Install Python using Homebrew if not already installed
if ! command -v python3 &> /dev/null; then
  echo "Installing Python..."
  brew install python
else
  echo "Python is already installed."
fi

# Install Git using Homebrew if not already installed
if ! command -v git &> /dev/null; then
  echo "Installing Git..."
  brew install git
else
  echo "Git is already installed."
fi

# Make virtual environment if not already created
if [ ! -d "wts-venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv wts-venv
else
  echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
# Activate virtual environment
source wts-venv/bin/activate

echo "Installing necessary dependencies..."
# Install necessary modules
pip install -r ./requirements.txt -qq

# Get CPU brand string and replace spaces with dashes
cpu_brand=$(sysctl -n machdep.cpu.brand_string | tr ' ' '-')

# Define the executable name based on the CPU brand
executable_name="wts-executable-${cpu_brand}"

echo "Building executable..."
# Build app executable with the generated name
pyinstaller --onefile --name "$executable_name" app.py > pyinstaller.log 2>&1

# Make sure port is closed
if sudo lsof -ti:8000 &> /dev/null; then
  echo "Closing port 8000..."
  sudo lsof -ti:8000 | xargs sudo kill -9
else
  echo "Port 8000 is already closed."
fi

echo "Executable created in path ./dist/${executable_name}"
