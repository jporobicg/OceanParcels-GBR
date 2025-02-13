#!/bin/bash

PATH_TO_FILES="/datasets/work/oa-coconet/work/OceanParcels-GBR/outputs/Coral"

# Define the array of folders
dates=(
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

wind_percentage=3
missing_files=0

# Create a log file
log_file="missing_files_log.txt"
echo "Missing Files Report" > "$log_file"
date >> "$log_file"
echo "-------------------" >> "$log_file"

# Loop through all dates
for release_start_day in "${dates[@]}"; do
    echo "Checking files for date: $release_start_day"
    
    # Loop through all polygon IDs (0-3805)
    for polygon_id in $(seq 0 3805); do
        expected_file="${PATH_TO_FILES}/GBR1_H2p0_Coral_Release_${release_start_day}_Polygon_${polygon_id}_Wind_${wind_percentage}_percent_displacement_field.nc"
        
        if [ ! -d "$expected_file" ]; then
            echo "Missing: ${expected_file}" >> "$log_file"
            ((missing_files++))
        fi
    done
done

echo "-------------------" >> "$log_file"
echo "Total missing files: $missing_files" >> "$log_file"
echo "Check complete. Found $missing_files missing files."
echo "Details have been saved to $log_file"

