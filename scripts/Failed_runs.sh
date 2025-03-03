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
    "2018-10-27"  # Was missing
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
    "2021-11-21"  # Was missing
    "2021-12-21"  # Was missing
)

wind_percentage=3
missing_files=0
small_files=0
output_dir="../checks"
# Create log files
log_file="${output_dir}/missing_files_log.txt"
echo "File Check Report" > "$log_file"
date >> "$log_file"
echo "-------------------" >> "$log_file"
echo "Checking for missing or undersized files (< 1MB)" >> "$log_file"
echo "-------------------" >> "$log_file"

# Loop through all dates
for release_start_day in "${dates[@]}"; do
    echo "Checking files for date: $release_start_day"
    rerun_file="${output_dir}/Failed_run_${release_start_day}.txt"
    > "$rerun_file"  # Create or clear the file
    
    # Loop through all polygon IDs (0-3805)
    for polygon_id in $(seq 0 3805); do
        expected_file="${PATH_TO_FILES}/${release_start_day}/GBR1_H2p0_Coral_Release_${release_start_day}_Polygon_${polygon_id}_Wind_${wind_percentage}_percent_displacement_field.nc"
        
        if [ ! -f "$expected_file" ]; then
            echo "Missing: ${expected_file}" >> "$log_file"
            echo -e "${polygon_id}\tMissing" >> "$rerun_file"
            ((missing_files++))
        else
            # Get file size in bytes
            size=$(stat -f%z "$expected_file" 2>/dev/null || stat -c%s "$expected_file" 2>/dev/null)
            # 1MB = 1048576 bytes
            if [ "$size" -lt 1048576 ]; then
                echo "Undersized ($(($size/1024))KB): ${expected_file}" >> "$log_file"
                echo -e "${polygon_id}\tUndersized" >> "$rerun_file"
                ((small_files++))
            fi
        fi
    done
done

echo "-------------------" >> "$log_file"
echo "Total missing files: $missing_files" >> "$log_file"
echo "Total undersized files: $small_files" >> "$log_file"
echo "Total problematic files: $(($missing_files + $small_files))" >> "$log_file"
echo "Check complete. Found $missing_files missing files and $small_files undersized files."
echo "Details have been saved to $log_file"

