#!/bin/bash

# Root directory to search for .zarr files and directories
root_dir="/datasets/work/oa-coconet/work/OceanParcels-GBR/outputs/Coral/"

# Define the array of folders
folders=(
    "2015-10-29"
    "2015-11-28"
    "2015-12-27"
    "2016-10-18"
    "2016-11-17"
    "2016-12-16"
    "2017-10-08"
    "2017-11-06"
    "2017-12-06"
    "2018-10-27"
)

# Print the folders that will be processed
echo "Folders to be processed:"
printf '%s\n' "${folders[@]}"

# Loop through each folder
for folder in "${folders[@]}"; do
  full_path="$root_dir/$folder"
  echo "Processing folder: $full_path"
  
  # Find and remove .zarr directories and their contents
  find "$full_path" -type d -name "*.zarr" -exec rm -rf {} +
  
  # Find and remove .zarr files
  find "$full_path" -type f -name "*.zarr" -delete
  
  echo "Finished processing $full_path"
done

echo "All .zarr files and directories have been removed."

echo "All .zarr files and directories have been removed."
