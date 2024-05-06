deactivate
rm -rf wts-venv
brew uninstall platypus --force
#!/bin/bash

# Save the path to the `dist` folder
dist_folder="./dist"

# Check if the `dist` folder exists
if [ ! -d "$dist_folder" ]; then
  echo "The 'dist' folder does not exist."
  exit 1
fi

# Delete all files and folders in the current directory except `dist`
for file in *; do
  if [ "$file" != "dist" ]; then
    rm -rf "$file"
  fi
done

# Move the contents of `dist` into the current directory
mv "$dist_folder"/* .

# Remove the now empty `dist` folder
rm -rf "$dist_folder"

echo "Operation completed successfully."
