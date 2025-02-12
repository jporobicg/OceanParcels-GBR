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
    "2018-11-25"
    "2018-12-25"
"2019-10-16"
"2019-11-15"
"2019-12-14"
"2020-10-04"
"2020-11-03"
"2020-12-02"
"2021-01-01"
"2021-10-23"
    
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


