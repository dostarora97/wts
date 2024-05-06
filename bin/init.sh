#!/bin/bash

echo "Initializing..."

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"
else
  echo "Homebrew is already installed."
fi

# Install Git using Homebrew if not already installed
if ! command -v git &> /dev/null; then
  echo "Installing Git..."
  brew install git
else
  echo "Git is already installed."
fi

echo "Cloning repo..."
git clone https://github.com/dostarora97/wts.git > /dev/null 2>&1

cd wts || exit

echo "Setting up permissions..."
chmod +x ./bin/build.sh
chmod +x ./bin/create-app.sh
chmod +x ./bin/clean.sh

source ./bin/build.sh

echo "Steps 1 to 4 completed. Continue from Step 5 in README.md"

open ./wts
